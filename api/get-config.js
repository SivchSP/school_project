// /api/get-config.js
export default function handler(req, res) {
  // Устанавливаем CORS заголовки
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }
  
  // ✅ БЕЗОПАСНО: возвращаем ТОЛЬКО публичные данные, НЕ секреты
  // Но для теста покажем, какие переменные существуют (но не их значения)
  
  const config = {
    hasMnemonic: !!process.env.CONTRACT_MNEMONIC,
    hasSubwalletId: !!process.env.CONTRACT_SUBWALLET_ID,
    hasTimeout: !!process.env.CONTRACT_TIMEOUT,
    hasEndpoint: !!process.env.CONTRACT_ENDPOINT,
    hasApiKey: !!process.env.API_KEY_TG,
    hasCodeHex: !!process.env.CODE_HEX,
    hasTelegramToken: !!process.env.TELEGRAM_TOKEN,
    // Для теста вернем небольшую публичную информацию
    subwalletId: process.env.CONTRACT_SUBWALLET_ID || 'not set',
    timeout: process.env.CONTRACT_TIMEOUT || 'not set',
    endpoint: process.env.CONTRACT_ENDPOINT ? 'set' : 'not set',
    message: 'Variables are available on server'
  };
  
  console.log('📡 API /api/get-config called');
  console.log('Environment check:', config);
  
  res.status(200).json(config);
}