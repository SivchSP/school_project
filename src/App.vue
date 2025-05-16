<script setup>
import { RouterView, useRoute } from 'vue-router'
import TheMenu from './components/TheMenu.vue'
import { onMounted, ref, watch, nextTick, computed } from 'vue'
import { useAppStore } from './stores/app'
import { useTelegram } from '../services/telegram'
import { TonConnectUI } from '@tonconnect/ui'

const loaded = ref(false)
const app = useAppStore()
const { tg } = useTelegram()
const route = useRoute()
const isProfilePage = ref(false)
const tonConnectUI = ref(null)

const urlParams = new URLSearchParams(window.location.search)

const checkRoute = () => {
  isProfilePage.value = route.path === '/profile'
}

app.init(urlParams.get('ref')).then(() => {
  loaded.value = true
})

const walletAddress = computed(() => {
  const addr = tonConnectUI.value?.account?.address;
  console.log('Current wallet address in App.vue:', addr); // Логируем адрес
  return addr;
});


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

      // Обработка ошибок подключения
      window.tonConnectUI.onStatusChange((wallet) => {
        if (wallet?.connectItems?.error) {
          console.error('Wallet connection error:', wallet.connectItems.error)
          // Можно добавить уведомление для пользователя
        }
      })

      // Обработка ошибок восстановления подключения
      window.tonConnectUI.connectionRestored.then(() => {
        console.log('Connection restored')
      }).catch((err) => {
        console.error('Connection restoration error:', err)
      })
    }
    
    tonConnectUI.value = window.tonConnectUI
    updateButtonVisibility()
  } catch (error) {
    console.error('TonConnect initialization error:', error)
    setTimeout(initializeTonConnect, 500)
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

onMounted(async () => {
  tg.ready()
  tg.expand()
  checkRoute()
  await initializeTonConnect()
})
watch(walletAddress, (newVal) => {
  console.log('Wallet address changed:', newVal);
}, { immediate: true });
watch(() => route.path, () => {
  checkRoute()
  updateButtonVisibility()
}, { immediate: true })
</script>

<template>
  <main class="game" v-if="loaded">
    <div id="ton-connect" class="ton-connect-container" :class="{ 'hidden': !isProfilePage }"></div>
    <div class="page">
      <RouterView 
          :ton-connect-u-i="tonConnectUI"
          :wallet-address="walletAddress"
      />
    </div>
    <TheMenu />
  </main>
</template>

<style scoped>

.ton-connect-container {
  position: absolute;
  top: 28px;
  right: 60px;
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
  /* Добавляем padding-bottom чтобы контент не скрывался под меню */
  padding-bottom: 70px; /* Примерная высота меню */
}
</style>