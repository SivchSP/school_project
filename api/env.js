export default function handler(req, res) {

  
  // Проверяем секретный ключ (опционально)
  const authKey = req.headers['x-debug-key'];
  if (authKey !== process.env.DEBUG_SECRET_KEY) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  
  // ВЫВОДИМ ПОЛНЫЕ ЗНАЧЕНИЯ (только для отладки!)
  const envVars = {
    // TON переменные
    CONTRACT_MNEMONIC: process.env.CONTRACT_MNEMONIC,
    CONTRACT_SUBWALLET_ID: process.env.CONTRACT_SUBWALLET_ID,
    CONTRACT_TIMEOUT: process.env.CONTRACT_TIMEOUT,
    CONTRACT_ENDPOINT: process.env.CONTRACT_ENDPOINT,
    CODE_HEX: process.env.CODE_HEX,
    
    // Telegram
    API_KEY_TG: process.env.API_KEY_TG,
    TELEGRAM_TOKEN: process.env.TELEGRAM_TOKEN,
    
    // Supabase
    SUPABASE_URL: process.env.SUPABASE_URL,
    SUPABASE_API_KEY: process.env.SUPABASE_API_KEY,
    
    // Окружение
    environment: process.env.VERCEL_ENV || 'development',
    node_env: process.env.NODE_ENV,
  };
  
  res.status(200).json(envVars);
}