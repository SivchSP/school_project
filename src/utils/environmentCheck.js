// utils/environmentCheck.js

/**
 * Улучшенная проверка, запущено ли приложение в Telegram Web App
 * @returns {boolean} - true если в Telegram, false если нет
 */
export const isTelegramWebApp = () => {
  try {
    // Проверяем наличие Telegram WebApp различными способами
    const hasTelegramWebApp = !!(
      window.Telegram?.WebApp ||
      window?.Telegram?.WebApp?.initData ||
      window?.TelegramWebviewProxy ||
      (window?.Telegram?.WebApp?.platform) || // Проверяем наличие platform
      (window?.Telegram?.WebApp?.version)     // Проверяем версию
    );
    
    // Дополнительная проверка: если есть initData, значит точно Telegram
    const hasInitData = !!window?.Telegram?.WebApp?.initData;
    
    // Проверяем, что это не просто объект Telegram (может быть в DevTools)
    const isRealTelegram = hasInitData || 
                          (hasTelegramWebApp && 
                           window?.Telegram?.WebApp?.platform !== 'unknown');
    
    console.log('Telegram check:', {
      hasTelegramWebApp,
      hasInitData,
      isRealTelegram,
      platform: window?.Telegram?.WebApp?.platform,
      version: window?.Telegram?.WebApp?.version
    });
    
    return isRealTelegram;
  } catch (error) {
    console.error('Error checking Telegram environment:', error);
    return false;
  }
};

/**
 * Проверяет, запущено ли приложение в режиме разработки (localhost или vercel preview)
 * @returns {boolean} - true если dev режим, false если нет
 */
export const isDevelopmentEnvironment = () => {
  try {
    const hostname = window.location.hostname;
    const isLocalhost = hostname === 'localhost' || 
                       hostname === '127.0.0.1' ||
                       hostname.includes('192.168.') ||
                       hostname.includes('10.0.');
    
    // Разрешаем Vercel preview deployments для тестирования
    const isVercelPreview = hostname.includes('vercel.app');
    
    // Разрешаем если есть параметр dev=true в URL
    const urlParams = new URLSearchParams(window.location.search);
    const isDevParam = urlParams.get('dev') === 'true';
    
    return isLocalhost || (isVercelPreview && isDevParam);
  } catch (error) {
    console.error('Error checking development environment:', error);
    return false;
  }
};

/**
 * Проверяет, разрешен ли доступ к приложению
 * @returns {Object} - результат проверки
 */
export const checkAccess = () => {
  const isTelegram = isTelegramWebApp();
  const isDev = isDevelopmentEnvironment();
  
  // Дополнительная проверка для production домена
  const isProductionDomain = window.location.hostname === 'drops-gifts.vercel.app';
  const forceTelegramOnly = isProductionDomain && !isDev;
  
  const isAllowed = isTelegram || (isDev && !forceTelegramOnly);
  
  console.log('Access check:', {
    isTelegram,
    isDev,
    isProductionDomain,
    forceTelegramOnly,
    isAllowed,
    hostname: window.location.hostname
  });
  
  return {
    isAllowed,
    isTelegram,
    isDev,
    reason: isTelegram 
      ? 'telegram' 
      : isDev 
        ? 'development' 
        : 'blocked',
    showBlockScreen: !isAllowed
  };
};