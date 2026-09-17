/**
 * Import function triggers from their respective submodules:
 *
 * const {onCall} = require("firebase-functions/v2/https");
 * const {onDocumentWritten} = require("firebase-functions/v2/firestore");
 *
 * See a full list of supported triggers at https://firebase.google.com/docs/functions
 */

const {onRequest} = require("firebase-functions/v2/https");
const logger = require("firebase-functions/logger");
const functions = require('firebase-functions');
const TonWeb = require('tonweb');
const cors = require('cors')({origin: true});

// Инициализация TonWeb
const provider = new TonWeb.HttpProvider('https://testnet.toncenter.com/api/v2/jsonRPC');
const tonweb = new TonWeb(provider);

exports.withdraw = functions.https.onRequest(async (req, res) => {
  // Включение CORS
  cors(req, res, async () => {
    if (req.method === 'OPTIONS') {
      return res.status(204).send();
    }

    if (req.method !== 'POST') {
      return res.status(405).send('Method Not Allowed');
    }

    try {
      const { recipientAddress, amount } = req.body;
      
      // Ваш приватный ключ (храните его безопасно!)
      const privateKey = new Uint8Array(Buffer.from('none', 'hex'));
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
});
// Create and deploy your first functions
// https://firebase.google.com/docs/functions/get-started

// exports.helloWorld = onRequest((request, response) => {
//   logger.info("Hello logs!", {structuredData: true});
//   response.send("Hello from Firebase!");
// });
