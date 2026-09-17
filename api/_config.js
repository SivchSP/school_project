// api/_config.js - Конфигурационный файл для API
// Все переменные окружения собираются здесь и экспортируются

// TON Конфигурация
export const tonConfig = {
    mnemonic: process.env.CONTRACT_MNEMONIC,
    subwalletId: parseInt(process.env.CONTRACT_SUBWALLET_ID),
    timeout: parseInt(process.env.CONTRACT_TIMEOUT),
    endpoint: process.env.CONTRACT_ENDPOINT,
    apiKey: process.env.API_KEY_TG,
    codeHex: process.env.CODE_HEX,
};

// Telegram Конфигурация
export const telegramConfig = {
    botToken: process.env.TELEGRAM_TOKEN || process.env.API_KEY_TG,
};

// Supabase Конфигурация
export const supabaseConfig = {
    url: process.env.SUPABASE_URL,
    apiKey: process.env.SUPABASE_API_KEY,
};

// Проверка наличия всех переменных
export const isConfigured = {
    ton: !!tonConfig.mnemonic && !!tonConfig.codeHex,
    telegram: !!telegramConfig.botToken,
    supabase: !!supabaseConfig.url && !!supabaseConfig.apiKey,
};

// Для отладки (только в development)
if (process.env.NODE_ENV === 'development') {
    console.log('📦 Config loaded:', {
        ton: isConfigured.ton,
        telegram: isConfigured.telegram,
        supabase: isConfigured.supabase,
        mnemonicExists: !!tonConfig.mnemonic,
        codeHexExists: !!tonConfig.codeHex,
        timeoutExists: !!tonConfig.timeout,
    });
}

export default {
    ton: tonConfig,
    telegram: telegramConfig,
    supabase: supabaseConfig,
    isConfigured,
};