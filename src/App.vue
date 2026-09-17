<script setup>
import { RouterView, useRoute, useRouter } from 'vue-router'
import TheMenu from './components/TheMenu.vue'
import { onMounted, ref, watch, nextTick, computed } from 'vue'
import { useAppStore } from './stores/app'
import { useTelegram } from '../services/telegram'
import { TonConnectUI } from '@tonconnect/ui'
import { Buffer } from 'buffer';
import { getOrCreateUserByTelegramId } from '../api/app';
import { useScoreStore } from '@/stores/score';
import { checkAccess } from './utils/environmentCheck';

window.Buffer = Buffer;

// Проверка доступа
const accessCheck = checkAccess();
const accessDenied = ref(!accessCheck.isAllowed);
const isProductionDomain = ref(window.location.hostname === 'drops-gifts.vercel.app');

console.log('Access Check Result:', accessCheck);

// Принудительно показываем экран блокировки на production домене, если не Telegram
if (isProductionDomain.value && !accessCheck.isTelegram) {
  console.log('Production domain detected - forcing access denied');
  accessDenied.value = true;
}

// Функция для перезагрузки с dev параметром (для разработчиков)
const enableDevMode = () => {
  const url = new URL(window.location.href);
  url.searchParams.set('dev', 'true');
  window.location.href = url.toString();
};

const loaded = ref(false)
const app = useAppStore()
const scoreStore = useScoreStore()
const { tg, user } = useTelegram()
const route = useRoute()
const router = useRouter()
const isProfilePage = ref(false)
const isMyOffersPage = ref(false)
const tonConnectUI = ref(null)
const accountLoaded = ref(false)

// Флаг для отображения начального спиннера во время загрузки данных
const showInitialSpinner = ref(true)

// Стадии анимации
const animationStage = ref(0)
const dropsPosition = ref(-15)
const dropsSize = ref(300)
const blackDustOpacity = ref(0)
const blackDustScale = ref(1)
const textOpacity = ref(0)
const textYPosition = ref(100)
const horizonGlow = ref(0)
const dropsOpacity = ref(1)
const gradientOpacity = ref(0)
const gradientSize = ref(0)

// Статичное расположение подарков
const gifts = ref([
  { id: 1, x: 10, y: 8, rotation: 20, scale: 0.6, opacity: 0.8, zIndex: 1 },
  { id: 2, x: 25, y: 10, rotation: -15, scale: 0.55, opacity: 0.75, zIndex: 1 },
  { id: 3, x: 40, y: 7, rotation: 25, scale: 0.65, opacity: 0.85, zIndex: 1 },
  { id: 4, x: 55, y: 9, rotation: -20, scale: 0.6, opacity: 0.8, zIndex: 1 },
  { id: 5, x: 70, y: 12, rotation: 15, scale: 0.55, opacity: 0.75, zIndex: 1 },
  { id: 6, x: 85, y: 8, rotation: -25, scale: 0.6, opacity: 0.8, zIndex: 1 },
  { id: 7, x: 15, y: 15, rotation: 30, scale: 0.5, opacity: 0.7, zIndex: 1 },
  { id: 8, x: 90, y: 14, rotation: -30, scale: 0.5, opacity: 0.7, zIndex: 1 },
  { id: 9, x: 20, y: 25, rotation: -10, scale: 0.6, opacity: 0.8, zIndex: 1 },
  { id: 10, x: 35, y: 28, rotation: 18, scale: 0.55, opacity: 0.75, zIndex: 1 },
  { id: 11, x: 50, y: 30, rotation: -22, scale: 0.65, opacity: 0.85, zIndex: 1 },
  { id: 12, x: 65, y: 25, rotation: 12, scale: 0.6, opacity: 0.8, zIndex: 1 },
  { id: 13, x: 80, y: 28, rotation: -18, scale: 0.55, opacity: 0.75, zIndex: 1 },
  { id: 14, x: 10, y: 32, rotation: 25, scale: 0.5, opacity: 0.7, zIndex: 1 },
  { id: 15, x: 45, y: 22, rotation: -15, scale: 0.6, opacity: 0.8, zIndex: 1 },
  { id: 16, x: 75, y: 20, rotation: 20, scale: 0.55, opacity: 0.75, zIndex: 1 },
  { id: 17, x: 15, y: 45, rotation: -8, scale: 0.6, opacity: 0.85, zIndex: 1 },
  { id: 18, x: 30, y: 50, rotation: 15, scale: 0.55, opacity: 0.75, zIndex: 1 },
  { id: 19, x: 45, y: 48, rotation: -20, scale: 0.65, opacity: 0.9, zIndex: 1 },
  { id: 20, x: 60, y: 45, rotation: 10, scale: 0.6, opacity: 0.8, zIndex: 1 },
  { id: 21, x: 75, y: 50, rotation: -25, scale: 0.55, opacity: 0.75, zIndex: 1 },
  { id: 22, x: 90, y: 46, rotation: 18, scale: 0.6, opacity: 0.85, zIndex: 1 },
  { id: 23, x: 25, y: 42, rotation: -12, scale: 0.5, opacity: 0.7, zIndex: 1 },
  { id: 24, x: 85, y: 42, rotation: 22, scale: 0.5, opacity: 0.7, zIndex: 1 },
  { id: 25, x: 20, y: 65, rotation: 15, scale: 0.6, opacity: 0.8, zIndex: 1 },
  { id: 26, x: 35, y: 68, rotation: -18, scale: 0.55, opacity: 0.75, zIndex: 1 },
  { id: 27, x: 50, y: 70, rotation: 22, scale: 0.65, opacity: 0.9, zIndex: 1 },
  { id: 28, x: 65, y: 65, rotation: -15, scale: 0.6, opacity: 0.8, zIndex: 1 },
  { id: 29, x: 80, y: 68, rotation: 20, scale: 0.55, opacity: 0.75, zIndex: 1 },
  { id: 30, x: 10, y: 70, rotation: -25, scale: 0.5, opacity: 0.7, zIndex: 1 },
  { id: 31, x: 45, y: 62, rotation: 12, scale: 0.6, opacity: 0.85, zIndex: 1 },
  { id: 32, x: 75, y: 60, rotation: -10, scale: 0.55, opacity: 0.75, zIndex: 1 },
  { id: 33, x: 15, y: 85, rotation: -20, scale: 0.6, opacity: 0.8, zIndex: 1 },
  { id: 34, x: 30, y: 88, rotation: 25, scale: 0.55, opacity: 0.75, zIndex: 1 },
  { id: 35, x: 45, y: 90, rotation: -18, scale: 0.65, opacity: 0.85, zIndex: 1 },
  { id: 36, x: 60, y: 85, rotation: 15, scale: 0.6, opacity: 0.8, zIndex: 1 },
  { id: 37, x: 75, y: 88, rotation: -22, scale: 0.55, opacity: 0.75, zIndex: 1 },
  { id: 38, x: 90, y: 84, rotation: 20, scale: 0.6, opacity: 0.85, zIndex: 1 },
  { id: 39, x: 25, y: 92, rotation: -30, scale: 0.5, opacity: 0.7, zIndex: 1 },
  { id: 40, x: 85, y: 92, rotation: 30, scale: 0.5, opacity: 0.7, zIndex: 1 }
])

const giftFlyOpacity = ref(0)

const urlParams = new URLSearchParams(window.location.search)
// ERUDA - консоль на 5 нажатий
const script = document.createElement('script');
script.src = 'https://cdn.jsdelivr.net/npm/eruda';
script.onload = () => eruda.init();
document.head.appendChild(script);
const checkRoute = () => {
  isProfilePage.value = route.path === '/profile'
  isMyOffersPage.value = route.path === '/myoffers'
}

// Функция для обработки startParam и преобразования его в маршрут
const processStartParam = () => {
  const initData = window.Telegram?.WebApp?.initDataUnsafe;
  const startParam = initData?.start_param || initData?.startParam;
  
  console.log('Пользователь:', initData?.user?.id);
  console.log('Тип чата:', initData?.chat_type);
  console.log('Параметр запуска:', startParam);
  
  if (startParam && startParam.startsWith('shop_')) {
    const shopId = startParam.substring(5);
    
    if (shopId) {
      const shopRoute = `/shop/${shopId}`;
      console.log(`Преобразование startParam в маршрут: ${startParam} -> ${shopRoute}`);
      
      if (route.path !== shopRoute) {
        console.log(`Перенаправление на маршрут: ${shopRoute}`);
        router.push(shopRoute);
      }
    }
  }
}

// Функция для автоматической регистрации пользователя
const autoRegisterUser = async () => {
  try {
    console.log('Начинаем автоматическую регистрацию пользователя...');
    
    const telegramId = user?.id;
    
    if (!telegramId) {
      console.warn('Telegram ID не найден, используем тестовый ID');
      const testId = 4252;
      const userData = await getOrCreateUserByTelegramId(testId);
      await handleUserRegistration(userData);
      return;
    }
    
    console.log('Telegram ID пользователя:', telegramId);
    
    const userData = await getOrCreateUserByTelegramId(telegramId);
    await handleUserRegistration(userData);
    
  } catch (error) {
    console.error('Ошибка при автоматической регистрации:', error);
  }
};

// Функция для обработки данных пользователя после регистрации
const handleUserRegistration = async (userData) => {
  try {
    console.log('Данные пользователя получены:', userData);
    
    scoreStore.setCurrentAccount({
      name: userData.name,
      score: userData.score || 0,
      ton_balance: userData.ton_balance || 0,
      telegram: userData.telegram,
      avatar_link: userData.avatar_link
    });
    
    localStorage.setItem('currentAccount', JSON.stringify({
      name: userData.name,
      telegram: userData.telegram,
      avatar_link: userData.avatar_link
    }));
    
    localStorage.setItem('isLoggedIn', 'true');
    
    console.log('Пользователь успешно зарегистрирован/авторизован');
    
  } catch (error) {
    console.error('Ошибка при обработке данных пользователя:', error);
  }
};

// Функция для запуска анимации загрузки
const startLoadingAnimation = () => {
  showInitialSpinner.value = false
  
  requestAnimationFrame(() => {
    setTimeout(() => {
      const startTime = performance.now()
      const duration = 4000
      
      const animateRise = (currentTime) => {
        const elapsed = currentTime - startTime
        const progress = Math.min(elapsed / duration, 1)
        
        const easeOutQuart = 1 - Math.pow(1 - progress, 4)
        const smoothProgress = easeOutQuart
        
        dropsPosition.value = -15 + (40 * smoothProgress)
        horizonGlow.value = 0.8 * smoothProgress
        giftFlyOpacity.value = smoothProgress
        
        if (progress < 1) {
          requestAnimationFrame(animateRise)
        } else {
          setTimeout(() => {
            const darkStartTime = performance.now()
            const darkDuration = 2500
            
            const animateDark = (currentTime) => {
              const darkElapsed = currentTime - darkStartTime
              const darkProgress = Math.min(darkElapsed / darkDuration, 1)
              
              const smoothDarkProgress = 1 - Math.pow(1 - darkProgress, 3)
              
              gradientOpacity.value = smoothDarkProgress
              
              if (darkProgress < 1) {
                requestAnimationFrame(animateDark)
              } else {
                setTimeout(() => {
                  const textStartTime = performance.now()
                  const textDuration = 2000
                  
                  const animateText = (currentTime) => {
                    const textElapsed = currentTime - textStartTime
                    const textProgress = Math.min(textElapsed / textDuration, 1)
                    
                    const smoothTextProgress = 1 - Math.pow(1 - textProgress, 3)
                    
                    textOpacity.value = smoothTextProgress
                    textYPosition.value = 100 - (100 * smoothTextProgress)
                    
                    if (textProgress < 1) {
                      requestAnimationFrame(animateText)
                    } else {
                      setTimeout(() => {
                        accountLoaded.value = true
                      }, 1000)
                    }
                  }
                  
                  requestAnimationFrame(animateText)
                }, 300)
              }
            }
            
            requestAnimationFrame(animateDark)
          }, 100)
        }
      }
      
      requestAnimationFrame(animateRise)
    }, 100)
  })
}

// Функция для инициализации всех данных приложения
const initializeAllData = async () => {
  try {
    console.log('Starting data initialization...')
    
    const cachedData = scoreStore.getCachedData()
    
    if (cachedData) {
      console.log('⚡ Используем кэшированные данные при запуске')
      scoreStore.setCurrentAccount(cachedData)
      loaded.value = true
      showInitialSpinner.value = false
      
      startLoadingAnimation()
      
      setTimeout(() => {
        continueInitialization()
      }, 100)
      
      return
    }
    
    await continueInitialization()
    
  } catch (error) {
    console.error('Error during data initialization:', error)
    loaded.value = true
    showInitialSpinner.value = false
    accountLoaded.value = true
  }
}

// Вынесенная логика инициализации
const continueInitialization = async () => {
  await autoRegisterUser();
  console.log('User auto-registration completed')
  
  processStartParam();
  console.log('StartParam processing completed')
  
  await app.init(urlParams.get('ref'))
  console.log('App initialization completed')
  
  if (accessCheck.isTelegram) {
    tg.ready()
    tg.expand()
    console.log('Telegram Web App initialized')
  }
  
  await initializeTonConnect()
  console.log('TonConnect initialized')
  
  checkRoute()
  
  const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true'
  const currentAccount = localStorage.getItem('currentAccount')
  const initData = window.Telegram?.WebApp?.initDataUnsafe
  const startParam = initData?.start_param || initData?.startParam
  
  if (isLoggedIn && currentAccount && (!startParam || !startParam.startsWith('shop_'))) {
    if (route.path === '/' || route.path === '/register') {
      console.log('Пользователь зарегистрирован, перенаправляем на профиль')
      router.push('/profile')
    }
  }
  
  console.log('Routing completed')
  
  loaded.value = true
  
  if (!accountLoaded.value) {
    console.log('Starting loading animation...')
    startLoadingAnimation()
  }
}

const walletAddress = computed(() => {
  const addr = tonConnectUI.value?.account?.address;
  console.log('Current wallet address in App.vue:', addr);
  return addr;
})

const isWalletConnected = computed(() => {
  return !!walletAddress.value
})

const initializeTonConnect = async () => {
  try {
    await nextTick()
    
    const element = document.getElementById('ton-connect')
    if (!element) {
      console.warn('TonConnect element not found, retrying...')
      setTimeout(initializeTonConnect, 300)
      return
    }
    
    if (!window.tonConnectUI) {
      window.tonConnectUI = new TonConnectUI({
        manifestUrl: 'https://raw.githubusercontent.com/SivchSP/Manifest/main/tonconnect-manifest.json',
        buttonRootId: 'ton-connect',
        uiPreferences: {
          theme: 'DARK',
          borderRadius: 'm'
        }
      })

      window.tonConnectUI.onStatusChange((wallet) => {
        if (wallet?.connectItems?.error) {
          console.error('Wallet connection error:', wallet.connectItems.error)
        }
      })
    }
    
    tonConnectUI.value = window.tonConnectUI
    updateButtonVisibility()
    
    return new Promise((resolve) => {
      const checkWalletStatus = () => {
        if (tonConnectUI.value) {
          console.log('TonConnect fully initialized')
          resolve()
        } else {
          setTimeout(checkWalletStatus, 100)
        }
      }
      checkWalletStatus()
    })
  } catch (error) {
    console.error('TonConnect initialization error:', error)
    throw error
  }
}

const updateButtonVisibility = () => {
  const element = document.getElementById('ton-connect')
  if (element) {
    element.style.display = isProfilePage.value ? 'block' : 'none'
    if (window.tonConnectUI) {
      window.tonConnectUI.uiOptions = {
        ...window.tonConnectUI.uiOptions,
        buttonRootId: isProfilePage.value ? 'ton-connect' : null
      }
    }
  }
}

const copyLink = async () => {
  try {
    const botLink = 'https://t.me/DROPS_OFC_bot/market?startapp'; // Замените на ссылку вашего бота
    await navigator.clipboard.writeText(botLink);
    alert('Bot link copied to clipboard! Please open it in Telegram.');
  } catch (error) {
    console.error('Failed to copy link:', error);
  }
};

onMounted(async () => {
  console.log('App mounted, checking access...');
  
  // Если доступ запрещен, не инициализируем приложение
  if (accessDenied.value) {
    console.log('Access denied, stopping initialization');
    return;
  }
  
  console.log('Starting data loading...')
  
  await initializeAllData()
  
  setTimeout(() => {
    if (!accountLoaded.value) {
      console.warn('Loading timeout, forcing completion')
      showInitialSpinner.value = false
      accountLoaded.value = true
    }
  }, 20000)
})

watch(walletAddress, (newVal) => {
  console.log('Wallet address changed:', newVal);
}, { immediate: true })

watch(() => route.path, () => {
  checkRoute()
  updateButtonVisibility()
}, { immediate: true })

const showMenu = computed(() => {
  return !isMyOffersPage.value
})
</script>

<template>
  
  <!-- Access Denied Screen -->
  <div v-if="accessDenied" class="access-denied-screen">
    <div class="access-denied-container">
      <div class="access-denied-icon">🚫</div>
      <h1 class="access-denied-title">Access Denied</h1>
      <p class="access-denied-message">
        This application can only be opened in Telegram Web App.
      </p>
      <p class="access-denied-submessage">
        Please open this app through Telegram on your mobile device.
      </p>
      <div class="access-denied-decoration">
        <span class="decoration-item">📱</span>
        <span class="decoration-item">→</span>
        <span class="decoration-item">🎁</span>
      </div>
      <button 
        @click="copyLink" 
        class="access-denied-button"
      >
        Launch Drops
      </button>
      
      <!-- Скрытая опция для разработчиков (только если есть параметр dev) -->
      <div v-if="isProductionDomain && $route.query.dev === 'debug'" class="dev-option">
        <button @click="enableDevMode" class="dev-button">
          Enable Dev Mode
        </button>
      </div>
    </div>
  </div>

  <!-- Initial Loading Spinner -->
  <div v-else-if="showInitialSpinner" class="initial-loading-screen">
    <div class="spinner-container">
      <div class="spinner"></div>
    </div>
  </div>

  <!-- Loading Animation -->
  <div v-else-if="loaded && !accountLoaded && !showInitialSpinner" class="loading-screen">
    <div class="animation-container">
      <div 
        class="horizon-glow"
        :style="{ opacity: horizonGlow }"
      ></div>
      
      <div 
        v-for="gift in gifts"
        :key="`gift-${gift.id}`"
        class="gift-fly"
        :style="{
          left: `${gift.x}%`,
          top: `${gift.y}%`,
          transform: `translate(-50%, -50%) rotate(${gift.rotation}deg) scale(${gift.scale})`,
          opacity: giftFlyOpacity * gift.opacity,
        }"
      >
        <img 
          src="@/assets/gift_fly.png" 
          alt="Flying Gift"
          loading="eager"
          decoding="async"
        />
      </div>
      
      <div 
        class="drops-image" 
        :style="{
          bottom: `${dropsPosition}%`,
          opacity: dropsOpacity
        }"
      >
        <img 
          src="@/assets/Drops_moon2.png" 
          alt="Drops"
          loading="eager"
          decoding="async"
          fetchpriority="high"
        />
      </div>
      
      <div class="ground"></div>
    </div>

    <div 
      class="darken-overlay"
      :style="{
        opacity: gradientOpacity
      }"
    ></div>

    <div 
      class="drops-text-overlay"
      :style="{
        opacity: textOpacity,
        transform: `translateY(${textYPosition}px)`
      }"
    >
      <div class="drops-text-container">
        DROPS
      </div>
    </div>
  </div>

  <!-- Main App Content -->
  <main v-else class="game" v-if="loaded && accountLoaded && !showInitialSpinner">
    <div id="ton-connect" class="ton-connect-container" :class="{ 'hidden': !isProfilePage }"></div>
    <div class="page">
      <RouterView 
          :ton-connect-u-i="tonConnectUI"
          :wallet-address="walletAddress"
      />
    </div>
    <TheMenu v-if="showMenu" />
  </main>
  
</template>

<style scoped>
input, 
textarea, 
button, 
select, 
div, 
a {
  -webkit-tap-highlight-color: rgba(0,0,0,0) !important;
  -webkit-tap-highlight-color: transparent !important;
}
button,
a,
[role="button"],
.clickable {
  -webkit-tap-highlight-color: transparent !important;
  -tap-highlight-color: transparent !important;
  -webkit-touch-callout: none !important;
  user-select: none !important;
}

.initial-loading-screen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100vh;
  background: #000;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10000;
}

.spinner-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  padding: 30px;
  background: rgba(0, 0, 0, 0.7);
  border-radius: 15px;
  box-shadow: 0 0 30px rgba(255, 187, 0, 0.1);
}

.spinner {
  width: 80px;
  height: 80px;
  border: 6px solid rgba(255, 187, 0, 0.2);
  border-radius: 50%;
  border-top-color: #ffbb00;
  border-right-color: #ffcc33;
  border-bottom-color: #ffaa00;
  animation: spin 1.2s cubic-bezier(0.68, -0.55, 0.27, 1.55) infinite;
  will-change: transform;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  50% {
    transform: rotate(180deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* Loading Animation Styles */
.loading-screen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100vh;
  background: #000;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  overflow: auto;
  content-visibility: auto;
  contain: content;
}

.animation-container {
  position: relative;
  width: 100%;
  max-width: 500px;
  height: 500px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  z-index: 10;
  will-change: transform;
  transform: translateZ(0);
}

.darken-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #000;
  z-index: 20;
  opacity: 0;
  transition: opacity 0.1s linear;
  pointer-events: none;
  will-change: opacity;
  transform: translateZ(0);
}

.horizon-glow {
  position: absolute;
  bottom: 0;
  left: -20%;
  width: 140%;
  height: 300px;
  background: radial-gradient(
    ellipse at center bottom,
    rgba(255, 187, 0, 0.4) 0%,
    rgba(255, 187, 0, 0.25) 20%,
    rgba(255, 187, 0, 0.15) 40%,
    rgba(255, 187, 0, 0.05) 60%,
    transparent 80%
  );
  z-index: 11;
  opacity: 0;
  transition: opacity 0.1s linear;
  pointer-events: none;
  will-change: opacity;
  transform: translateZ(0);
}

.gift-fly {
  position: absolute;
  transform-origin: center;
  z-index: 12;
  pointer-events: none;
  will-change: transform, opacity;
  transform: translateZ(0);
  backface-visibility: hidden;
}

.gift-fly img {
  width: 90px;
  height: 90px;
  object-fit: contain;
  filter: drop-shadow(0 0 20px rgba(255, 187, 0, 0.322));
  image-rendering: -webkit-optimize-contrast;
  image-rendering: crisp-edges;
}

.drops-image {
  position: absolute;
  left: 50%;
  bottom: -15%;
  width: 300px;
  height: 300px;
  z-index: 13;
  transform: translateX(-50%);
  opacity: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
  will-change: bottom, opacity;
  transform: translateX(-50%) translateZ(0);
  backface-visibility: hidden;
}

.drops-image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: 
    drop-shadow(0 0 30px #ffbb00)
    drop-shadow(0 0 60px rgba(255, 187, 0, 0.8));
  image-rendering: -webkit-optimize-contrast;
  image-rendering: crisp-edges;
  transform: translateZ(0);
  backface-visibility: hidden;
}

.ground {
  position: absolute;
  bottom: -170px;
  left: 50%;
  transform: translateX(-50%);
  width: 200%;
  height: 250px;
  background: #000;
  border-radius: 50% 50% 0 0;
  box-shadow: 0 -25px 60px rgba(0, 0, 0, 0.95);
  z-index: 14;
  pointer-events: none;
  transform: translateX(-50%) translateZ(0);
}

.drops-text-overlay {
  position: fixed;
  top: 50%;
  left: 0;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 30;
  opacity: 0;
  pointer-events: none;
  will-change: transform, opacity;
  transform: translateY(100px) translateZ(0);
  backface-visibility: hidden;
}

.drops-text-container {
  font-size: 180px;
  font-weight: 900;
  color: #ffbb00;
  text-align: center;
  text-shadow: 
    0 0 15px #ffbb00,
    0 0 30px #ffbb00,
    0 0 45px #ffbb00,
    0 0 60px rgba(255, 187, 0, 0.7),
    0 0 75px rgba(255, 187, 0, 0.5);
  letter-spacing: 20px;
  font-family: 'Arial Black', 'Helvetica Bold', 'Helvetica', 'Roboto Bold', 'Segoe UI Black', sans-serif;
  text-transform: uppercase;
  max-width: 90vw;
  padding: 0 20px;
  line-height: 1;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  animation: textPulseSoft 2s infinite alternate;
}

@supports (-webkit-touch-callout: none) {
  .drops-text-container {
    font-weight: 900;
    text-shadow: 
      0 0 15px #ffbb00,
      0 0 30px #ffbb00,
      0 0 45px #ffbb00,
      0 0 60px #ffbb00,
      0 2px 0 #000,
      2px 0 0 #000,
      -2px 0 0 #000,
      0 -2px 0 #000;
    transform: scale(1.01) translateZ(0);
  }
}

@media (max-width: 768px) {
  .drops-text-container {
    font-size: 100px;
    letter-spacing: 12px;
  }
  
  @supports (-webkit-touch-callout: none) {
    .drops-text-container {
      font-size: 100px;
    }
  }
}

@media (max-width: 480px) {
  .drops-text-container {
    font-size: 70px;
    letter-spacing: 10px;
    max-width: 95vw;
  }
  
  @supports (-webkit-touch-callout: none) {
    .drops-text-container {
      font-size: 70px;
    }
  }
}

@keyframes textPulseSoft {
  from {
    text-shadow: 
      0 0 10px #ffbb00,
      0 0 20px #ffbb00,
      0 0 30px rgba(255, 187, 0, 0.7),
      0 0 40px rgba(255, 187, 0, 0.5);
  }
  to {
    text-shadow: 
      0 0 15px #ffbb00,
      0 0 30px #ffbb00,
      0 0 45px rgba(255, 187, 0, 0.7),
      0 0 60px rgba(255, 187, 0, 0.5);
  }
}

.ton-connect-container {
  position: absolute;
  top: 28px;
  right: 25px;
  z-index: 1000;
  width: 180px;
  height: 40px;
  background: transparent;
}

.ton-connect-container.hidden {
  display: none !important;
}

:deep(.tc-wallet-button) {
  width: 100% !important;
  height: 100% !important;
  max-width: 180px;
}

.game {
  position: relative;
  width: 100%;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.page {
  flex: 1;
  padding-bottom: 70px;
}

/* Access Denied Screen Styles */
.access-denied-screen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100vh;
  background: linear-gradient(135deg, #1a1a1a 0%, #000000 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 20000;
  padding: 20px;
}

.access-denied-container {
  max-width: 400px;
  width: 100%;
  text-align: center;
  padding: 40px 30px;
  background: rgba(20, 20, 20, 0.9);
  border-radius: 24px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 187, 0, 0.2);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
  animation: fadeInUp 0.6s ease;
}

.access-denied-icon {
  font-size: 80px;
  margin-bottom: 20px;
  animation: shake 0.5s ease-in-out;
}

.access-denied-title {
  font-size: 32px;
  font-weight: 900;
  color: #ffbb00;
  margin-bottom: 16px;
  text-shadow: 0 0 20px rgba(255, 187, 0, 0.5);
  letter-spacing: 2px;
}

.access-denied-message {
  font-size: 18px;
  color: #ffffff;
  margin-bottom: 12px;
  line-height: 1.5;
  opacity: 0.9;
}

.access-denied-submessage {
  font-size: 16px;
  color: #cccccc;
  margin-bottom: 30px;
  line-height: 1.5;
  opacity: 0.7;
}

.access-denied-decoration {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;
  font-size: 30px;
}

.decoration-item {
  animation: bounce 2s infinite;
}

.decoration-item:nth-child(2) {
  animation-delay: 0.2s;
}

.decoration-item:nth-child(3) {
  animation-delay: 0.4s;
}

.access-denied-button {
  background: linear-gradient(135deg, #ffbb00 0%, #ffaa00 100%);
  color: #000000;
  border: none;
  padding: 16px 32px;
  font-size: 18px;
  font-weight: bold;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 10px 20px rgba(255, 187, 0, 0.3);
  width: 100%;
  max-width: 280px;
  margin: 0 auto;
}

.access-denied-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 15px 30px rgba(255, 187, 0, 0.4);
}

.access-denied-button:active {
  transform: translateY(0);
  box-shadow: 0 5px 15px rgba(255, 187, 0, 0.3);
}

.dev-option {
  margin-top: 20px;
}

.dev-button {
  background: transparent;
  color: #666;
  border: 1px solid #333;
  padding: 8px 16px;
  font-size: 12px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.dev-button:hover {
  color: #ffbb00;
  border-color: #ffbb00;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
  20%, 40%, 60%, 80% { transform: translateX(5px); }
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

@media (max-width: 480px) {
  .access-denied-container {
    padding: 30px 20px;
  }
  
  .access-denied-icon {
    font-size: 60px;
  }
  
  .access-denied-title {
    font-size: 28px;
  }
  
  .access-denied-message {
    font-size: 16px;
  }
  
  .access-denied-submessage {
    font-size: 14px;
  }
  
  .access-denied-button {
    padding: 14px 28px;
    font-size: 16px;
  }
}
</style>