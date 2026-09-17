import express from 'express';
import cors from 'cors';
import TonWeb from 'tonweb';
import { Buffer } from 'buffer';

const app = express();
const port = 3000;

// Middleware для обработки JSON-тела запроса
app.use(express.json());

// Правильная настройка CORS
app.use(cors({
  origin: ['http://localhost:5173', 'https://localhost:5173'], // Разрешаем и HTTP, и HTTPS
  methods: ['GET', 'POST', 'OPTIONS'],
  allowedHeaders: ['Content-Type'],
  credentials: true
}));

// Обработка предварительных запросов OPTIONS
app.options('*', cors());

// Ваш эндпоинт для вывода
app.post('/api/withdraw', async (req, res) => {
  try {
    const { recipientAddress, amount } = req.body;
    
    const provider = new TonWeb.HttpProvider('https://toncenter.com/api/v2/jsonRPC', {
      apiKey: 'none' // Рекомендуется добавить API ключ
    });
    const tonweb = new TonWeb(provider);

    const privateKey = new Uint8Array(Buffer.from('none', 'hex'));
    const keyPair = TonWeb.utils.nacl.sign.keyPair.fromSeed(privateKey);

    const WalletClass = tonweb.wallet.all['v3R2'];
    const wallet = new WalletClass(provider, { publicKey: keyPair.publicKey, wc: 0 });

    // Получаем seqno и проверяем, активирован ли кошелек
    const seqno = await wallet.methods.seqno().call();
    if (seqno === null || seqno === undefined) {
      throw new Error('Кошелек не активирован. Пополните его минимум на 0.02 TON для активации.');
    }

    const body = new TonWeb.boc.Cell();
    body.bits.writeAddress(new TonWeb.utils.Address(recipientAddress));
    body.bits.writeCoins(TonWeb.utils.toNano(amount));

    const result = await wallet.methods.transfer({
      secretKey: keyPair.secretKey,
      toAddress: recipientAddress,
      amount: TonWeb.utils.toNano(amount),
      seqno: seqno,
      payload: body,
      sendMode: 3,
    }).send();

    if (!result) {
      throw new Error('Не удалось отправить транзакцию');
    }

    res.json({ 
      success: true, 
      message: 'Транзакция успешно отправлена',
      transactionHash: result 
    });
  } catch (error) {
    console.error('Ошибка вывода:', error);
    res.status(500).json({ 
      success: false, 
      error: error.message,
      details: 'Убедитесь, что кошелек активирован и имеет достаточный баланс' 
    });
  }
});

app.listen(port, () => {
  console.log(`Сервер запущен на порту ${port}`);
});