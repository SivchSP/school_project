// services/telegram.js
export function useTelegram() {
  // Проверяем, существует ли Telegram WebApp
  const tg = window.Telegram?.WebApp || null
  
  // Если WebApp нет, возвращаем заглушку
  if (!tg) {
    return {
      tg: null,
      user: null,
      username: null,
      avatarUrl: null,
      firstName: null,
      lastName: null,
      languageCode: null,
      telegramId: null
    }
  }
  
  const user = tg.initDataUnsafe?.user || null
  
  return {
    tg,
    user,
    username: user?.username || null,
    avatarUrl: user?.photo_url || null,
    firstName: user?.first_name || null,
    lastName: user?.last_name || null,
    languageCode: user?.language_code || null,
    telegramId: user?.id || null
  }
}