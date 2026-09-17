// /api/withdraw.js
import { sendWithdrawTransaction, initWithdrawSystem } from './tonWithdraw.js';

// Инициализируем систему при старте
let isSystemInitialized = false;

async function ensureSystemInitialized() {
  if (!isSystemInitialized) {
    await initWithdrawSystem();
    isSystemInitialized = true;
  }
}

export default async function handler(req, res) {
  // Разрешаем CORS для разработки
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }
  
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    // Инициализируем систему если нужно
    await ensureSystemInitialized();
    
    const { userId, userName, address, amount } = req.body;
    
    // Валидация
    if (!userId || !userName || !address || !amount) {
      return res.status(400).json({ 
        error: 'Missing required fields: userId, userName, address, amount' 
      });
    }
    
    if (isNaN(amount) || amount <= 0) {
      return res.status(400).json({ error: 'Invalid amount' });
    }
    
    console.log(`📤 Withdraw request: ${amount} TON for ${userName} (${address})`);
    
    // Вызываем серверную функцию
    const result = await sendWithdrawTransaction(userId, userName, address, amount);
    
    console.log(`✅ Withdraw result:`, result);
    
    return res.status(200).json(result);
    
  } catch (error) {
    console.error('Withdraw API error:', error);
    return res.status(500).json({ 
      success: false, 
      error: error.message || 'Internal server error' 
    });
  }
}