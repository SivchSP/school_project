import express from 'express';
import cors from 'cors';
import TonWeb from 'tonweb';
import { Buffer } from 'buffer';

const app = express();
const port = 3000;

// Настройки CORS
app.use(cors({
  origin: 'http://localhost:5173',
  methods: ['POST', 'OPTIONS'],
  allowedHeaders: ['Content-Type']
}));

app.use(express.json());

// Обработка OPTIONS запросов
app.options('/withdraw', cors());

// Эндпоинт для вывода
app.post('/withdraw', async (req, res) => {
  try {
    const { recipientAddress, amount } = req.body;
    
    const provider = new TonWeb.HttpProvider('https://testnet.toncenter.com/api/v2/jsonRPC');
    const tonweb = new TonWeb(provider);

    const privateKey = new Uint8Array(Buffer.from('d41d0c2fef6ea013b56e9a09e20782b711a98015bfc06254541e52799c686ad1', 'hex'));
    const keyPair = TonWeb.utils.nacl.sign.keyPair.fromSeed(privateKey);

    const WalletClass = tonweb.wallet.all['v3R2'];
    const wallet = new WalletClass(provider, { publicKey: keyPair.publicKey, wc: 0 });

    const body = new TonWeb.boc.Cell();
    body.bits.writeAddress(new TonWeb.utils.Address(recipientAddress));
    body.bits.writeCoins(TonWeb.utils.toNano(amount));

    await wallet.methods.transfer({
      secretKey: keyPair.secretKey,
      toAddress: recipientAddress,
      amount: TonWeb.utils.toNano(amount),
      seqno: await wallet.methods.seqno().call(),
      payload: body,
      sendMode: 3,
    }).send();

    res.json({ success: true, message: 'Транзакция успешно отправлена' });
  } catch (error) {
    console.error('Ошибка:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

app.listen(port, () => {
  console.log(`Сервер запущен на порту ${port}`);
});