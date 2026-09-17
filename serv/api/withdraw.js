import express from 'express';
import bodyParser from 'body-parser';
import cors from 'cors';
import { getHttpEndpoint } from "@orbs-network/ton-access";
import { mnemonicToWalletKey } from "@ton/crypto";
import { TonClient, WalletContractV4, internal, Address } from "@ton/ton";
import { toNano } from "@ton/core";

const app = express();

// Middleware
app.use(bodyParser.json());
app.use(cors({
  origin: [
    'https://sivch-app-2.vercel.app',
    'http://localhost:5173' // для разработки
  ],
  credentials: true
}));

// Конфигурация
const MNEMONIC = "none";

function isValidTonAddress(address) {
  try {
    Address.parse(address);
    return true;
  } catch (e) {
    return false;
  }
}

async function sendTransaction(toAddress, amount) {
  try {
    if (!isValidTonAddress(toAddress)) {
      throw new Error('Неверный формат адреса получателя');
    }

    const key = await mnemonicToWalletKey(MNEMONIC.split(" "));
    const wallet = WalletContractV4.create({ publicKey: key.publicKey, workchain: 0 });

    const endpoint = await getHttpEndpoint({ network: "mainnet" });
    const client = new TonClient({ endpoint });

    const isDeployed = await client.isContractDeployed(wallet.address);
    if (!isDeployed) {
      throw new Error(`Кошелек не развернут. Сначала отправьте на него TON: ${wallet.address.toString()}`);
    }

    const walletContract = client.open(wallet);
    const seqno = await walletContract.getSeqno();

    const message = internal({
      to: toAddress,
      value: toNano(amount.toString()),
      body: "Amahasla withdraw",
      bounce: false,
    });

    await walletContract.sendTransfer({
      secretKey: key.secretKey,
      seqno: seqno,
      messages: [message],
      sendMode: 3,
    });

    console.log("🔄 Транзакция отправлена");
    return `tx-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
  } catch (error) {
    console.error('⛔ Ошибка транзакции:', error.message);
    throw error;
  }
}

// Обработчик вывода средств
app.post('/api/withdraw', async (req, res) => {
  try {
    const { amount, recipient } = req.body;
    
    if (!amount || !recipient) {
      return res.status(400).json({ 
        success: false,
        message: 'Не указана сумма или адрес получателя' 
      });
    }
    
    const numericAmount = parseFloat(amount);
    if (isNaN(numericAmount)) {
      return res.status(400).json({ 
        success: false,
        message: 'Некорректная сумма вывода' 
      });
    }

    if (numericAmount <= 0) {
      return res.status(400).json({ 
        success: false,
        message: 'Сумма должна быть больше 0' 
      });
    }

    if (!isValidTonAddress(recipient)) {
      return res.status(400).json({ 
        success: false,
        message: 'Неверный формат адреса получателя' 
      });
    }

    const txHash = await sendTransaction(recipient, numericAmount);
    
    res.json({ 
      success: true, 
      message: `Транзакция на ${numericAmount} TON отправлена`,
      txHash: txHash
    });
  } catch (error) {
    console.error('Server withdraw error:', error);
    
    let errorMessage = error.message;
    let statusCode = 500;
    
    if (error.message.includes('Неверный формат адреса')) {
      statusCode = 400;
    } else if (error.message.includes('Кошелек не развернут')) {
      statusCode = 400;
      errorMessage = 'Кошелек отправителя не активирован. Пожалуйста, пополните его баланс.';
    } else if (error.message.includes('out-of-gas')) {
      errorMessage = 'Недостаточно газа для выполнения транзакции';
    }
    
    res.status(statusCode).json({ 
      success: false,
      message: errorMessage 
    });
  }
});

// Экспортируем для Vercel
export default app;