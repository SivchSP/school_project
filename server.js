import express from 'express';
import bodyParser from 'body-parser';
import cors from 'cors';
import { getHttpEndpoint } from "@orbs-network/ton-access";
import { mnemonicToWalletKey } from "@ton/crypto";
import { TonClient, WalletContractV4, internal, Address } from "@ton/ton";
import { toNano } from "@ton/core";

const app = express();
app.use(bodyParser.json());
app.use(cors());

// Конфигурация
const MNEMONIC = "none";
const PORT = 3000;

// Функция для проверки валидности адреса TON
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
    // Проверка адреса получателя
    if (!isValidTonAddress(toAddress)) {
      throw new Error('Неверный формат адреса получателя');
    }

    // 1. Инициализация кошелька
    const key = await mnemonicToWalletKey(MNEMONIC.split(" "));
    const wallet = WalletContractV4.create({ publicKey: key.publicKey, workchain: 0 });

    // 2. Подключение к сети
    const endpoint = await getHttpEndpoint({ network: "mainnet" });
    const client = new TonClient({ endpoint });

    // 3. Проверка развертывания кошелька
    const isDeployed = await client.isContractDeployed(wallet.address);
    if (!isDeployed) {
      throw new Error(`Кошелек не развернут. Сначала отправьте на него TON: ${wallet.address.toString()}`);
    }

    // 4. Открытие контракта и получение seqno
    const walletContract = client.open(wallet);
    const seqno = await walletContract.getSeqno();

    // 5. Подготовка сообщения
    const message = internal({
      to: toAddress,
      value: toNano(amount.toString()),
      body: "Amahasla withdraw",
      bounce: false,
    });

    // 6. Отправка транзакции
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
    
    // Валидация входных данных
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

    // Проверка адреса получателя
    if (!isValidTonAddress(recipient)) {
      return res.status(400).json({ 
        success: false,
        message: 'Неверный формат адреса получателя' 
      });
    }

    // Отправка транзакции
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
    
    // Определяем тип ошибки для более информативного ответа
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

app.listen(PORT, () => {
  console.log(`Сервер вывода запущен на порту ${PORT}`);
});