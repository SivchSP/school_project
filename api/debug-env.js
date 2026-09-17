// /api/debug-env.js
export default function handler(req, res) {
  // ⚠️ ТОЛЬКО ДЛЯ ТЕСТА! УДАЛИТЬ ПОСЛЕ ОТЛАДКИ!
  
  // Добавляем заголовки для CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }
  
  // Получаем все переменные окружения (ПОЛНОСТЬЮ, без обрезки)
  const envVars = {
    // TON Contract variables
    CONTRACT_MNEMONIC: process.env.CONTRACT_MNEMONIC || 'NOT SET',
    CONTRACT_SUBWALLET_ID: process.env.CONTRACT_SUBWALLET_ID || 'NOT SET',
    CONTRACT_TIMEOUT: process.env.CONTRACT_TIMEOUT || 'NOT SET',
    CONTRACT_ENDPOINT: process.env.CONTRACT_ENDPOINT || 'NOT SET',
    
    // API Keys
    API_KEY_TG: process.env.API_KEY_TG || 'NOT SET',
    TELEGRAM_TOKEN: process.env.TELEGRAM_TOKEN || 'NOT SET',
    
    // Contract code
    CODE_HEX: process.env.CODE_HEX || 'NOT SET',
    
    // Supabase
    SUPABASE_URL: process.env.SUPABASE_URL || 'NOT SET',
    SUPABASE_API_KEY: process.env.SUPABASE_API_KEY || 'NOT SET',
    SERVICE_ROLE: process.env.SERVICE_ROLE || 'NOT SET',
    
    // System info
    NODE_ENV: process.env.NODE_ENV || 'NOT SET',
    VERCEL_ENV: process.env.VERCEL_ENV || 'NOT SET',
    VERCEL_URL: process.env.VERCEL_URL || 'NOT SET',
  };
  
  // Логируем на сервере (ПОЛНОСТЬЮ, без обрезки)
  console.log('='.repeat(80));
  console.log('🔍 DEBUG: Environment Variables (FULL VALUES)');
  console.log('='.repeat(80));
  Object.entries(envVars).forEach(([key, value]) => {
    if (value && value !== 'NOT SET') {
      // Выводим ПОЛНОСТЬЮ, не обрезая
      console.log(`✅ ${key}:`);
      console.log(`${value}`);
      console.log(`📊 Длина: ${value.length} символов`);
      console.log('─'.repeat(40));
    } else {
      console.log(`❌ ${key}: ${value}`);
    }
  });
  console.log('='.repeat(80));
  
  // Возвращаем клиенту ПОЛНОСТЬЮ (без обрезки)
  res.status(200).json({
    success: true,
    timestamp: new Date().toISOString(),
    environment: envVars,  // Полные значения
    message: 'Environment variables retrieved successfully (full values)'
  });
}