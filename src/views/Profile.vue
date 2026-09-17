<template>
  <div class="app dark-theme" style="overflow-x: hidden;">
    
    <!-- Header (original styles) -->
    <header class="header">
      <div class="logo"></div>
      <div class="balance-container-wrapper">
  <div class="balance-container" @click="toggleBalancePopup">
    <span class="balance">{{ formattedBalance }}</span>
    <img class="balance-icon" :src="TON" alt="TON" />
  </div>
  
  <transition name="withdraw-animation">
    <div v-if="showWithdrawNotification" class="withdraw-notification">
      <span class="withdraw-amount">{{ formattedWithdrawAmount }}</span>
    </div>
  </transition>
</div>
      <div id="ton-connect"></div>
      <div class="header-actions" style="padding-right: 10px">
        <!-- <button class="logout-btn" @click="logout">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1-2-2h4"></path>
            <polyline points="16 17 21 12 16 7"></polyline>
            <line x1="21" y1="12" x2="9" y2="12"></line>
          </svg>
        </button> -->
      </div>
    </header>

    <!-- Main content -->
    <main class="content">
      <!-- Profile -->
      <section class="profile">
        <div class="profile-card">
          <img :src="avatarUrl" alt="Profile" class="avatar" />
          <h2 class="username">@{{ displayName }}</h2>

          <!-- Quick top-up -->
          <div class="quick-topup">
            <button 
              @click="handleTopUp(1)" 
              :disabled="!isWalletConnected"
              :class="{ 'disabled-btn': !isWalletConnected }"
            >+1 TON</button>
            <button 
              @click="handleTopUp(5)" 
              :disabled="!isWalletConnected"
              :class="{ 'disabled-btn': !isWalletConnected }"
            >+5 TON</button>
            <button 
              @click="handleTopUp(10)" 
              :disabled="!isWalletConnected"
              :class="{ 'disabled-btn': !isWalletConnected }"
            >+10 TON</button>
          </div>
        </div>

        <!-- NFT Collection -->
        <button class="nft-btn" @click="navigateToNFT">My Gifts</button>
        <button class="offers-btn" @click="navigateToOffers">My Offers</button>

        <!-- NEW SECTIONS: Tasks and Friends -->
        <div class="sections-container">
          <div class="bonus-text">Complete tasks, invite friends, and get more bonuses!</div>
          <!-- Tasks section with slider -->
          <div class="gradient-card tasks-card">
            <div class="slider-track" @touchstart="startDrag($event, 'tasks')" @touchmove="drag($event, 'tasks')" @touchend="endDrag('tasks')"
                 @mousedown="startDrag($event, 'tasks')" @mousemove="drag($event, 'tasks')" @mouseup="endDrag('tasks')" @mouseleave="endDrag('tasks')">
              <div class="card-content">
                <h3 class="card-title" :style="{ transform: `translateX(${tasksDragOffset}px)` }">Tasks</h3>
                <span class="card-arrow">Complete</span>
              </div>
            </div>
          </div>

          <!-- Friends section -->
          <div class="gradient-card">
            <div class="slider-track" @touchstart="startDrag($event, 'friends')" @touchmove="drag($event, 'friends')" @touchend="endDrag('friends')"
                 @mousedown="startDrag($event, 'friends')" @mousemove="drag($event, 'friends')" @mouseup="endDrag('friends')" @mouseleave="endDrag('friends')">
              <div class="card-content">
                <h3 class="card-title-friends" :style="{ transform: `translateX(${friendsDragOffset}px)` }">Friends</h3>
                <span class="card-arrow-friends">Invite</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>

    <!-- Balance management popup -->
    <div v-if="showBalancePopup" class="balance-popup-overlay" @click.self="showBalancePopup = false">
      <div class="balance-popup">
        <div class="balance-popup-header">
          <h3>Balance: {{ formattedBalance }} TON</h3>
          <button class="close-btn" @click="showBalancePopup = false">&times;</button>
        </div>
        <div class="balance-popup-body">
          <button 
            class="balance-action-btn top-up" 
            @click="handleBalanceAction('topup')"
            :disabled="!isWalletConnected"
            :class="{ 'disabled-action-btn': !isWalletConnected }"
          >
            {{ isWalletConnected ? 'Top up balance' : 'Connect wallet' }}
          </button>
          <button 
            class="balance-action-btn withdraw" 
            @click="handleBalanceAction('withdraw')"
            :disabled="!isWalletConnected || Math.floor(Number(currentAccount.ton_balance) * 1000) / 1000 <= 0"
            :class="{ 'disabled-action-btn': !isWalletConnected }"
          >
            {{ isWalletConnected ? 'Withdraw funds' : 'Connect wallet' }}
          </button>
          <!-- Operations history button -->
          <button 
            class="balance-action-btn history" 
            @click="showOperationsHistory"
          >
            Operations History
          </button>
          <div v-if="!isWalletConnected" class="wallet-notice">
            <small>Connect wallet to top up and withdraw funds</small>
          </div>
        </div>
      </div>
    </div>

    <!-- Balance top-up modal -->
    <div v-if="showTopUpModal" class="modal-overlay" @click.self="showTopUpModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>Balance Top-up</h3>
          <button class="close-btn" @click="showTopUpModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <div class="input-group">
            <label>Amount (TON)</label>
            <input 
              type="number" 
              v-model="topUpAmount"
              class="amount-input"
              min="0.1"
              step="0.001"
              placeholder="Enter amount"
              :disabled="!isWalletConnected"
            >
          </div>
          <div class="quick-amounts">
            <button 
              @click="topUpAmount = 1" 
              :disabled="!isWalletConnected"
              :class="{ 'disabled-btn': !isWalletConnected }"
            >1 TON</button>
            <button 
              @click="topUpAmount = 5" 
              :disabled="!isWalletConnected"
              :class="{ 'disabled-btn': !isWalletConnected }"
            >5 TON</button>
            <button 
              @click="topUpAmount = 10" 
              :disabled="!isWalletConnected"
              :class="{ 'disabled-btn': !isWalletConnected }"
            >10 TON</button>
          </div>
          <div v-if="!isWalletConnected" class="wallet-required-notice">
            ❌ Wallet connection required for top-up
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showTopUpModal = false">Cancel</button>
          <button 
            class="btn-primary" 
            @click="confirmTopUp" 
            :disabled="!isWalletConnected"
            :class="{ 'disabled-primary-btn': !isWalletConnected }"
          >
            {{ isWalletConnected ? 'Top Up' : 'Connect wallet' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Withdraw funds modal -->
    <div v-if="showWithdrawModal" class="modal-overlay" @click.self="showWithdrawModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>Withdraw Funds</h3>
          <button class="close-btn" @click="showWithdrawModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <div class="input-group">
            <label>Amount (TON)</label>
            <input 
              type="number" 
              v-model="withdrawAmount" 
              @input="validateAmountInput($event.target.value, 'withdraw')"
              class="amount-input" 
              min="0.1" 
              :max="Math.floor(Number(currentAccount.ton_balance) * 1000) / 1000"
              step="0.001"
              :placeholder="`Available: ${formattedBalance} TON`"
              :disabled="!isWalletConnected"
            >
          </div>
          <div class="quick-amounts">
            <button 
              @click="withdrawAmount = 1" 
              :disabled="!isWalletConnected"
              :class="{ 'disabled-btn': !isWalletConnected }"
            >1 TON</button>
            <button 
              @click="withdrawAmount = 5" 
              :disabled="!isWalletConnected"
              :class="{ 'disabled-btn': !isWalletConnected }"
            >5 TON</button>
            <button 
              @click="withdrawAmount = 10" 
              :disabled="!isWalletConnected"
              :class="{ 'disabled-btn': !isWalletConnected }"
            >10 TON</button>
            <button 
              @click="withdrawAmount = Math.floor(Number(currentAccount.ton_balance) * 1000) / 1000" 
              :disabled="!isWalletConnected"
              :class="{ 'disabled-btn': !isWalletConnected }"
            >All</button>
          </div>
          <div class="total-info">
            Withdraw {{ formattedWithdrawAmountInModal }} TON
          </div>
          <div v-if="!isWalletConnected" class="wallet-required-notice">
            ❌ Wallet connection required for withdrawal
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showWithdrawModal = false">Cancel</button>
          <button 
            class="btn-primary" 
            @click="confirmWithdraw" 
            :disabled="!isWithdrawValid || !isWalletConnected"
            :class="{ 'disabled-primary-btn': !isWalletConnected }"
          >
            {{ isWalletConnected ? 'Withdraw' : 'Connect wallet' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Operations history modal -->
<!-- Operations history modal -->
<div v-if="showOperationsHistoryModal" class="modal-overlay" @click.self="showOperationsHistoryModal = false">
  <div class="modal operations-history-modal">
    <div class="modal-header">
      <h3>Operations History</h3>
      <button class="close-btn" @click="showOperationsHistoryModal = false">&times;</button>
    </div>
    <div class="modal-body">
      <div 
        class="operations-list" 
        ref="operationsListRef"
        @scroll="handleOperationsScroll"
      >
        <div 
          v-for="operation in displayedOperations" 
          :key="operation.id || operation.timestamp"
          class="operation-item"
          :class="getOperationClass(operation.type)"
        >
          <div class="operation-info">
            <div class="operation-type-wrapper">
              <span class="operation-type">
                {{ getOperationTypeText(operation.type) }}
              </span>
            </div>
            
            <!-- Для Transfer Sent показываем получателя -->
            <div v-if="operation.type === 'transfer_sent' && operation.recipient_username" 
                class="recipient-info"
                @click="(e) => toggleUsername(operation.id, e)">
              <span class="recipient-label">To:</span>
              <span class="recipient-username" :class="{ 'expanded': expandedUsernames.has(operation.id) }">
                @{{ getDisplayUsername(operation, 'recipient') }}
              </span> 
              <span v-if="operation.recipient_username && operation.recipient_username.length > 10" class="expand-hint">
                {{ expandedUsernames.has(operation.id) ? '▼' : '▶' }}
              </span>
            </div>
            
            <!-- Для Transfer Received показываем отправителя -->
            <div v-else-if="operation.type === 'transfer_received' && operation.sender_username" 
                class="recipient-info"
                @click="(e) => toggleUsername(operation.id, e)">
              <span class="recipient-label">From:</span>
              <span class="recipient-username" :class="{ 'expanded': expandedUsernames.has(operation.id) }">
                @{{ getDisplayUsername(operation, 'sender') }}
              </span> 
              <span v-if="operation.sender_username && operation.sender_username.length > 10" class="expand-hint">
                {{ expandedUsernames.has(operation.id) ? '▼' : '▶' }}
              </span>
            </div>

            <!-- Информация о комиссии (только для offer_sale) -->
            <div v-if="operation.commission && operation.type === 'offer_sale'" 
                 class="commission-info">
              <span class="commission-label">Commission:</span>
              <span class="commission-amount">{{ operation.commission }} TON</span>
            </div>
            
            <!-- Wallet address - show ONLY for wallet-related operations -->
            <div v-if="shouldShowWalletAddress(operation.type) && operation.walletAddress" class="wallet-address">
              {{ formatWalletAddress(operation.walletAddress) }}
            </div>
            
            <span class="operation-date">
              {{ formatDate(operation.timestamp) }}
            </span>
          </div>
          
          <!-- Правая часть - сумма и изображение -->
          <div class="operation-right">
            <!-- Для Transfer и Offer Purchase показываем пустой блок (сумма не нужна) -->
            <div v-if="operation.type === 'transfer_sent' || operation.type === 'transfer_received' || operation.type === 'offer_purchase'" 
                class="operation-amount amount-transfer">
              <!-- Пусто -->
            </div>
            
            <!-- Для остальных операций показываем сумму -->
            <div v-else-if="operation.type !== 'wallet_connect'" 
                class="operation-amount" 
                :class="getAmountClass(operation.type)">
              {{ getAmountText(operation.type, operation.amount, operation) }}
            </div>
            
            <!-- Специальный случай для wallet_connect -->
            <div v-else class="operation-amount amount-neutral">
              <img 
                src="@/assets/party-popper.png" 
                alt="🎉" 
                class="party-popper-icon-amount"
              />
            </div>
            
           <!-- Изображение NFT для операций с NFT -->
            <img 
              v-if="['listing', 'purchase', 'Sale', 'Cancel Sale', 'sale', 'cancel_sale', 'offer', 'promote', 
                    'transfer_sent', 'transfer_received', 'offer_sale', 'offer_purchase', 
                    'gift_received', 'sale_for_gift', 'gift_purchase', 'gift_sent'].includes(operation.type) && operation.link"
              :src="getNftImageUrl(operation.link)"
              :alt="operation.nftName || 'Gift'"
              class="nft-thumbnail"
              @error="handleImageError"
              @load="handleImageLoad"
              loading="lazy"
            />
          </div>
        </div>
        
        <!-- Load more indicator -->
        <div v-if="isLoadingMoreOperations" class="loading-more">
          <div class="loading-spinner"></div>
          <span>Loading more operations...</span>
        </div>
        
        <!-- End of list indicator -->
        <div v-if="hasLoadedAllOperations && displayedOperations.length > 0" class="end-of-list">
          <span>No more operations</span>
        </div>
      </div>
      <div v-if="displayedOperations.length === 0 && !isLoadingMoreOperations" class="empty-history">
        <p>No operations history</p>
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn-secondary" @click="showOperationsHistoryModal = false">Close</button>
    </div>
  </div>
</div>
<BalancePopup 
  v-if="showBalanceModal"
  :tonConnectUI="tonConnectUI"
  @close="closeBalanceModal"
  @showHistory="showOperationsHistoryFromPopup"
/>
  </div>
</template>
<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import amahaslaImage from '@/assets/amahasla.png'
import frogIcon from '@/assets/frog1.png'
import partyPopperIcon from '@/assets/party-popper.png'
import { useScoreStore } from '@/stores/score'
import supabase from '../../services/supabase'
import { useRouter, useRoute } from 'vue-router'
import TON from '@/assets/ton-logo-black.png'

// Замените существующий импорт sendWithdrawTransaction на:
// Замените существующий импорт на:
import { 
  sendWithdrawTransaction, 
  getHighloadWalletBalance, 
  getQueueStatus,
  initWithdrawSystem
} from '/services/tonWithdraw.js'
import { subscribeToChannel, unsubscribeFromChannel } from '/subscriptions'
import axios from 'axios'
import { debounce } from 'lodash'
import { useShopStore } from '@/stores/app'
import { useTelegram } from '../../services/telegram'
import BalancePopup from '@/components/BalancePopup.vue'

// Добавьте состояние для показа модалки
const showBalanceModal = ref(false)

// Измените функцию toggleBalancePopup
const toggleBalancePopup = () => {
  showBalanceModal.value = true
}
const showOperationsHistoryFromPopup = async () => {
  showBalanceModal.value = false
  await loadOperationsHistory(true)
  showOperationsHistoryModal.value = true
  
  currentPage.value = 1
  hasLoadedAllOperations.value = false
  displayedOperations.value = []
  
  await loadMoreOperations()
}
// Добавьте функцию закрытия модалки
const closeBalanceModal = () => {
  showBalanceModal.value = false
}
const { 
  username: telegramUsername, 
  avatarUrl: telegramAvatar, 
  firstName,
  languageCode // Добавляем language_code
} = useTelegram()
const route = useRoute()

// Функция для сохранения данных в БД
const saveTelegramData = async () => {
  try {
    if (!currentAccount.value?.name) return

    const updates = {}
    
    if (telegramUsername) updates.username = telegramUsername
    if (firstName) updates.first_name = firstName
    if (languageCode) updates.language_code = languageCode // Добавляем language_code
    if (telegramAvatar) {
      updates.avatar_link = { 
        url: telegramAvatar,
        name: telegramUsername || firstName || 'User'
      }
    }
    
    if (Object.keys(updates).length === 0) return

    await supabase
      .from('users')
      .update(updates)
      .eq('name', currentAccount.value.name)

    console.log('✅ Данные Telegram сохранены:', updates)
    
  } catch (error) {
    console.error('Ошибка сохранения:', error)
  }
}




// Обновляем avatarUrl для приоритета из БД
const avatarUrl = computed(() => {
  if (currentAccount.value?.avatar_link?.url) {
    return currentAccount.value.avatar_link.url
  }
  return telegramAvatar || '/default-avatar.png'
})

// Обновляем displayName для приоритета из БД
const displayName = computed(() => {
  if (currentAccount.value?.username) {
    return currentAccount.value.username
  }
  if (currentAccount.value?.first_name) {
    return currentAccount.value.first_name
  }
  return telegramUsername || firstName || 'User'
})

// Функция для сохранения Telegram данных в колонку massiv
const saveTelegramDataToMassiv = async () => {
  try {
    // Проверяем, есть ли данные пользователя
    if (!currentAccount.value?.name) {
      console.log('Нет данных текущего аккаунта')
      return
    }

    console.log('💾 Сохраняем Telegram данные в massiv:', telegramData)

    // Обновляем запись пользователя - добавляем данные в колонку massiv
    const { error } = await supabase
      .from('users')
      .update({ 
        massiv: telegramData, // Сохраняем как JSON
        updated_at: new Date().toISOString()
      })
      .eq('name', currentAccount.value.name)

    if (error) throw error

    console.log('✅ Telegram данные успешно сохранены в колонку massiv')
    
    // Обновляем локальные данные
    if (currentAccount.value) {
      currentAccount.value.massiv = telegramData
    }
    
  } catch (error) {
    console.error('❌ Ошибка сохранения Telegram данных:', error)
  }
}

// Или можно вызвать отдельно при монтировании
onMounted(async () => {
  console.log('🚀 Profile.vue mounted')
  
  // Загружаем профиль
  await loadUserProfile()
  
  // Сохраняем Telegram данные
  await saveTelegramDataToMassiv()
  
  // ... остальной код
})

const shopStore = useShopStore()
const { user } = useTelegram()

const navigateToNFT = () => {
  shopStore.setActiveTab('my-nfts')
  router.push('/shop')
}

const navigateToOffers = () => {
  router.push('/myoffers')
}


// Константы
const isTransactionInProgress = ref(false)
const RECIPIENT_ADDRESS = "EQBzpf5KMPu3aOnEkgSD2Sx1zdYG644uLebdUteJIRi3o18D"
const props = defineProps({
  tonConnectUI: Object
})

// Состояния
const withdrawAmount = ref(0)
const isLoading = ref(false)
const showWithdrawNotification = ref(false)
const lastWithdrawAmount = ref(0)
const showOperationsHistoryModal = ref(false)
const operationsHistory = ref([])
const lastWalletConnectionTime = ref(null)
const lastWalletDisconnectionTime = ref(null)

// Переменные для пагинации истории операций
const displayedOperations = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const isLoadingMoreOperations = ref(false)
const hasLoadedAllOperations = ref(false)
const operationsListRef = ref(null)

// Переменные для перетаскивания
const isDragging = ref(false)
const dragType = ref(null)
const startX = ref(0)
const currentX = ref(0)
const tasksDragOffset = ref(0)
const friendsDragOffset = ref(0)
const DRAG_THRESHOLD = 100
// Добавьте после других переменных ref
const isHighloadWalletInitialized = ref(false)
const highloadWalletAddress = ref('')
const highloadWalletBalance = ref(0)
const router = useRouter()
const scoreStore = useScoreStore()

// Инициализируем currentAccount из стора или localStorage для показа во время загрузки
const getInitialAccount = () => {
  // Сначала пробуем из стора (самые свежие данные)
  if (scoreStore.currentAccount?.name) {
    console.log('📦 Начальная инициализация из стора:', scoreStore.currentAccount.name)
    return {
      name: scoreStore.currentAccount.name,
      score: scoreStore.currentAccount.score || 0,
      ton_balance: scoreStore.currentAccount.ton_balance || 0,
      avatar_link: scoreStore.currentAccount.avatar_link
    }
  }
  
  // Затем из localStorage (на случай перезагрузки страницы)
  const savedAccount = localStorage.getItem('currentAccount')
  if (savedAccount) {
    try {
      const account = JSON.parse(savedAccount)
      console.log('📦 Начальная инициализация из localStorage:', account.name)
      // Баланс берем из стора если есть, иначе 0
      const savedBalance = localStorage.getItem(`lastBalance_${account.name}`)
      return {
        name: account.name || '',
        score: 0,
        ton_balance: savedBalance ? parseFloat(savedBalance) : 0,
        avatar_link: account.avatar_link || null
      }
    } catch (e) {
      console.error('Ошибка парсинга savedAccount:', e)
    }
  }
  
  // Если ничего нет - пустой объект (такого не должно быть, т.к. пользователь уже залогинен)
  return {
    name: '',
    score: 0,
    ton_balance: 0,
    avatar_link: null
  }
}

const currentAccount = ref(getInitialAccount())
const balance = ref(currentAccount.value.ton_balance || 0)

// Флаг для отслеживания первой загрузки из БД
const isFirstLoadComplete = ref(false)

const showTopUpModal = ref(false)
const showBalancePopup = ref(false)
const showWithdrawModal = ref(false)
const topUpAmount = ref(1)
const withdrawAnimationDuration = 3000
const isWithdrawAnimating = ref(false)

// Вычисляемые свойства
// Profile.vue - вставь этот код

// Вместо computed используем ref
const isWalletConnected = ref(false);


// В setupTonConnectListeners
const setupTonConnectListeners = () => {
  if (props.tonConnectUI) {
    // Сразу обновляем статус
    updateWalletStatus();
    
    if (props.tonConnectUI.account?.address) {
      lastKnownWalletAddress.value = props.tonConnectUI.account.address
    }
    
    props.tonConnectUI.onStatusChange((walletInfo) => {
      updateWalletStatus();
      handleWalletStatusChange(walletInfo);
    });
  }
};
// Функция обновления статуса
const updateWalletStatus = () => {
  const newStatus = props.tonConnectUI?.connected || false;
  if (isWalletConnected.value !== newStatus) {
    isWalletConnected.value = newStatus;
    console.log(`🔄 Статус кошелька: ${newStatus ? 'подключен' : 'отключен'}`);
  }
};



const formattedWithdrawAmount = computed(() => {
  if (lastWithdrawAmount.value <= 0) return '0'
  return `-${lastWithdrawAmount.value.toFixed(2)}`
})

const isWithdrawValid = computed(() => {
  if (!isWalletConnected.value) return false
  
  const amount = parseFloat(withdrawAmount.value)
  // ЗАМЕНИТЕ ЭТУ СТРОКУ:
  return amount >= 0.1 && amount <= (Math.floor(Number(currentAccount.value.ton_balance) * 1000) / 1000)
})




// ТОЛЬКО ЭТО ДОБАВИТЬ:
const formattedBalance = computed(() => {
  const balance = Number(currentAccount.value.ton_balance) || 0
  return Math.floor(balance * 1000) / 1000
})
// Функции для перетаскивания
const startDrag = (event, type) => {
  isDragging.value = true
  dragType.value = type
  const clientX = event.touches ? event.touches[0].clientX : event.clientX
  startX.value = clientX
  event.preventDefault()
}

const drag = (event, type) => {
  if (!isDragging.value || dragType.value !== type) return
  
  const clientX = event.touches ? event.touches[0].clientX : event.clientX
  currentX.value = clientX
  const offset = Math.max(0, currentX.value - startX.value)
  
  if (type === 'tasks') {
    tasksDragOffset.value = offset
  } else if (type === 'friends') {
    friendsDragOffset.value = offset
  }
}

const endDrag = (type) => {
  if (!isDragging.value || dragType.value !== type) return
  
  const offset = type === 'tasks' ? tasksDragOffset.value : friendsDragOffset.value
  
  if (offset >= DRAG_THRESHOLD) {
    if (type === 'tasks') {
      navigateToTasks()
    } else if (type === 'friends') {
      navigateToFriends()
    }
  }
  
  isDragging.value = false
  dragType.value = null
  
  if (type === 'tasks') {
    animateReset(tasksDragOffset)
  } else if (type === 'friends') {
    animateReset(friendsDragOffset)
  }
}

const animateReset = (offsetRef) => {
  const start = offsetRef.value
  const startTime = performance.now()
  const duration = 300
  
  const animate = (currentTime) => {
    const elapsed = currentTime - startTime
    const progress = Math.min(elapsed / duration, 1)
    offsetRef.value = start * (1 - progress)
    
    if (progress < 1) {
      requestAnimationFrame(animate)
    }
  }
  
  requestAnimationFrame(animate)
}

const lastKnownWalletAddress = ref(null)

// Функция для обработки скролла
const handleOperationsScroll = () => {
  if (!operationsListRef.value || isLoadingMoreOperations.value || hasLoadedAllOperations.value) return
  
  const list = operationsListRef.value
  const scrollTop = list.scrollTop
  const scrollHeight = list.scrollHeight
  const clientHeight = list.clientHeight
  
  if (scrollTop + clientHeight >= scrollHeight * 0.8) {
    loadMoreOperations()
  }
}

// Функция для проверки и открытия попапа при загрузке
const checkAndOpenBalancePopup = () => {
  if (route.query.openBalance === 'true') {
    // Небольшая задержка для полной загрузки компонента
    setTimeout(() => {
      showBalanceModal.value = true
      
      // Очищаем query параметр, чтобы при обновлении страницы попап не открывался снова
      router.replace({ path: '/profile', query: {} })
    }, 300)
  }
}
// Найдите функцию loadOperationsHistory (примерно строка 370-400) и замените:
const loadOperationsHistory = async (forceRefresh = false) => {
  try {
    if (!currentAccount.value.name) {
      console.warn('⚠️ Не удалось загрузить историю: имя пользователя не найдено')
      return
    }

    console.log('🔄 Загрузка истории операций для:', currentAccount.value.name)
    
    const { data: userData, error } = await supabase
      .from('users')
      .select('operation_history')
      .eq('name', currentAccount.value.name)
      .single()

    if (error) {
      console.error('❌ Ошибка загрузки истории операций:', error)
      return
    }

    let history = userData?.operation_history || []
    
    // ✅ ИСПРАВЛЕНО: Форматируем суммы в истории, НО пропускаем referal
    history = history.map(op => {
      // Если это referal - не трогаем amount, оставляем как есть
      if (op.type === 'referal') {
        return op;
      }
      // Для всех остальных - форматируем до сотых
      return {
        ...op,
        amount: op.amount ? Number(parseFloat(op.amount).toFixed(2)) : op.amount
      };
    });
    
    console.log('📥 Получено операций из БД:', history.length)
    
    history.sort((a, b) => {
      const dateA = new Date(a.timestamp).getTime()
      const dateB = new Date(b.timestamp).getTime()
      return dateB - dateA
    })
    
    operationsHistory.value = history
    
  } catch (error) {
    console.error('❌ Ошибка загрузки истории операций:', error)
  }
}
// Функция для загрузки дополнительных операций
const loadMoreOperations = async () => {
  if (isLoadingMoreOperations.value || hasLoadedAllOperations.value) return
  
  isLoadingMoreOperations.value = true
  
  try {
    const startIndex = (currentPage.value - 1) * pageSize.value
    const endIndex = startIndex + pageSize.value
    
    const newOperations = operationsHistory.value.slice(startIndex, endIndex)
    
    if (newOperations.length === 0) {
      hasLoadedAllOperations.value = true
      return
    }
    
    displayedOperations.value = [...displayedOperations.value, ...newOperations]
    currentPage.value++
    
    if (endIndex >= operationsHistory.value.length) {
      hasLoadedAllOperations.value = true
    }
    
  } catch (error) {
    console.error('❌ Ошибка загрузки дополнительных операций:', error)
  } finally {
    isLoadingMoreOperations.value = false
  }
}

// Функция для записи операции в историю
let isAddingOperation = false
const addOperationToHistory = async (type, amount = null, transactionHash = null) => {
  if (isAddingOperation) {
    console.log('⏭️ Уже добавляется другая операция, пропускаем')
    return
  }
  
  isAddingOperation = true
  
  try {
    console.log('📝 Начало записи операции:', type)
    
    if (!currentAccount.value.name) {
      throw new Error('Имя пользователя не установлено')
    }
    
    const walletAddress = type === 'wallet_disconnect' 
      ? lastKnownWalletAddress.value 
      : (props.tonConnectUI?.account?.address || lastKnownWalletAddress.value)
    
    const { data: existingUser, error: fetchError } = await supabase
      .from('users')
      .select('name, operation_history')
      .eq('name', currentAccount.value.name)
      .single()
    
    if (fetchError) throw fetchError
    if (!existingUser) throw new Error('Пользователь не найден')
    
    let currentHistory = existingUser.operation_history || []
    
    let nextId = 1
    if (currentHistory.length > 0) {
      const maxId = Math.max(...currentHistory.map(op => {
        const id = parseInt(op.id)
        return isNaN(id) ? 0 : id
      }))
      nextId = maxId + 1
    }
    
    // ✅ Добавляем transactionHash в операцию

    // В функции addOperationToHistory, создание operation
    // В Profile.vue, в функции addOperationToHistory
    const operation = {
      id: nextId,
      type: type,
      amount: amount ? Number(parseFloat(amount).toFixed(2)) : null,
      timestamp: new Date().toISOString(),
      transactionHash: transactionHash,
      walletAddress: walletAddress,
      is_recorded: "false"  // 👈 ДОБАВИТЬ ЭТУ СТРОКУ
    }

    // Добавляем is_recorded для topup и withdraw
    if (type === 'topup' || type === 'withdraw') {
      operation.is_recorded = "false"
    }

    console.log(`📝 Операция с хэшем: ${transactionHash || 'не указан'}`)
    
    currentHistory.unshift(operation)
    
    const { error: updateError } = await supabase
      .from('users')
      .update({ 
        operation_history: currentHistory,
        updated_at: new Date().toISOString()
      })
      .eq('name', currentAccount.value.name)
    
    if (updateError) throw updateError
    
    console.log('✅ Операция записана успешно!')
    
    operationsHistory.value = currentHistory.sort((a, b) => {
      const dateA = new Date(a.timestamp).getTime()
      const dateB = new Date(b.timestamp).getTime()
      return dateB - dateA
    })
    
  } catch (error) {
    console.error('💥 Ошибка при записи операции:', error)
    throw error
  } finally {
    setTimeout(() => {
      isAddingOperation = false
    }, 1000)
  }
}
// Функция для форматирования суммы с округлением до сотых
const formatAmount = (amount) => {
  if (amount === null || amount === undefined) return '';
  const num = parseFloat(amount);
  return isNaN(num) ? '' : num.toFixed(2);
};
const showOperationsHistory = async () => {
  showBalancePopup.value = false
  await loadOperationsHistory(true)
  showOperationsHistoryModal.value = true
  
  currentPage.value = 1
  hasLoadedAllOperations.value = false
  displayedOperations.value = []
  
  await loadMoreOperations()
}

const formatDate = (dateString) => {
  const date = new Date(dateString);
  
  // Получаем language_code из currentAccount
  const languageCode = currentAccount.value?.language_code || 'ru';
  
  // Определяем часовой пояс на основе language_code
  const timeZone = getTimeZoneFromLanguage(languageCode);
  
  return date.toLocaleString('ru-RU', {
    timeZone: timeZone,
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
};

// Функция для определения часового пояса по language_code
const getTimeZoneFromLanguage = (languageCode) => {
  const timeZoneMap = {
    // СНГ страны (обычно UTC+3)
    'ru': 'Europe/Moscow',
    'uk': 'Europe/Kiev',
    'be': 'Europe/Minsk',
    'kz': 'Asia/Almaty',
    'uz': 'Asia/Tashkent',
    
    // Европа
    'en': 'Europe/London',
    'de': 'Europe/Berlin',
    'fr': 'Europe/Paris',
    'it': 'Europe/Rome',
    'es': 'Europe/Madrid',
    
    // Азия
    'zh': 'Asia/Shanghai',
    'ja': 'Asia/Tokyo',
    'ko': 'Asia/Seoul',
    'tr': 'Europe/Istanbul',
    
    // Америка
    'pt': 'America/Sao_Paulo',
    'en-us': 'America/New_York',
    'es-mx': 'America/Mexico_City',
    
    // По умолчанию - Москва
    'default': 'Europe/Moscow'
  };
  
  return timeZoneMap[languageCode] || timeZoneMap['default'];
};


const shouldShowWalletAddress = (type) => {
  const walletRelatedTypes = ['wallet_connect', 'wallet_disconnect', 'topup', 'withdraw']
  return walletRelatedTypes.includes(type)
}
// Функция для обновления username в базе данных
const updateUsernameInDB = async (username) => {
  if (!username || !currentAccount.value?.name) return;
  
  try {
    await supabase
      .from('users')
      .update({ username: username })
      .eq('name', currentAccount.value.name);
  } catch (error) {
    console.error('Ошибка обновления username:', error);
  }
};
const formatWalletAddress = (address) => {
  if (!address) return ''
  return `${address.slice(0, 6)}...${address.slice(-4)}`
}

// В функции getOperationClass (примерно строка 700-720) - добавьте referal
const getOperationClass = (type) => {
  switch (type) {
    case 'topup': return 'operation-topup'
    case 'withdraw': return 'operation-withdraw'
    case 'wallet_connect': return 'operation-wallet-connect'
    case 'wallet_disconnect': return 'operation-wallet-disconnect'
    case 'offer': return 'operation-offer'
    case 'purchase': return 'operation-purchase'
    case 'promote': return 'operation-promote'
    case 'sale': return 'operation-sale'
    case 'refund': return 'operation-refund'
    case 'cancel_sale': return 'operation-cancel-sale'
    case 'price_edit_package': return 'operation-price-edit'
    case 'listing': return 'operation-listing'
    case 'Cancel Sale': return 'operation-cancel-sale'
    case 'Sale': return 'operation-sale'
    case 'transfer_sent': return 'operation-transfer'
    case 'transfer_received': return 'operation-transfer'
    case 'offer_sale': return 'operation-offer-sale'
    case 'offer_purchase': return 'operation-offer-purchase'
    case 'gift_received': 
    case 'gift_purchase': 
    case 'gift_sent': return 'operation-gift'
    case 'sale_for_gift': return 'operation-sale'
    case 'bonus': return 'operation-bonus'
    case 'referal': return 'operation-referal' // 👈 ДОБАВЛЯЕМ REFERAL
    default: 
      console.log('⚠️ Неизвестный тип операции:', type);
      return ''
  }
}

// В функции getOperationTypeText (примерно строка 750-770) - добавьте referal
const getOperationTypeText = (type) => {
  switch (type) {
    case 'topup': return 'Top-up'
    case 'withdraw': return 'Withdrawal'
    case 'wallet_connect': return 'Wallet connected'
    case 'wallet_disconnect': return 'Wallet disconnected'
    case 'offer': return 'Offer'
    case 'purchase': return 'Purchase'
    case 'promote': return 'Promotion'
    case 'sale': return 'Sale'
    case 'refund': return 'Refund'
    case 'cancel_sale': return 'Cancel Sale'
    case 'price_edit_package': return 'Price Edit Package'
    case 'listing': return 'Listing'
    case 'Cancel Sale': return 'Cancel Sale'
    case 'Sale': return 'Sale'
    case 'transfer_sent': return 'Transfer Sent'
    case 'transfer_received': return 'Transfer Received'
    case 'offer_sale': return 'Offer Sale'
    case 'offer_purchase': return 'Offer Purchase'
    case 'gift_received': return '🎁 Gift Received'
    case 'sale_for_gift': return 'Sale'
    case 'gift_purchase': return 'Gift Purchase'
    case 'gift_sent': return 'Gift Sent'
    case 'bonus': return 'Bonus'
    case 'referal': return 'Referral Bonus' // 👈 ДОБАВЛЯЕМ REFERAL
    default: return type
  }
}

// В функции getAmountClass (примерно строка 780-800) - добавьте referal
const getAmountClass = (type) => {
  switch (type) {
    case 'topup': 
    case 'sale': 
    case 'refund':
    case 'Sale':
    case 'offer_sale':
    case 'sale_for_gift':
    case 'bonus':
    case 'referal': // 👈 ДОБАВЛЯЕМ REFERAL К ПОЛОЖИТЕЛЬНЫМ
      return 'amount-positive'
    case 'withdraw': 
    case 'offer': 
    case 'purchase': 
    case 'promote':
    case 'price_edit_package':
    case 'Cancel Sale':
    case 'offer_purchase':
    case 'gift_purchase':
      return 'amount-negative'
    case 'listing':
      return 'amount-listing'
    case 'transfer_sent':
    case 'transfer_received':
    case 'gift_received':
    case 'gift_sent':
      return 'amount-transfer'
    case 'wallet_connect': 
    case 'wallet_disconnect':
    case 'cancel_sale':
      return 'amount-neutral'
    default: return ''
  }
}

// В функции getAmountText (примерно строка 810-830) - добавьте referal
// Обновите функцию getAmountText:
const getAmountText = (type, amount, operation) => {
  // Для referal - просто отображаем то, что в базе
  if (type === 'referal') {
    return `+${amount} TON`;
  }
  
  // Для остальных типов операций
  let formattedAmount = formatAmount(amount);
  
  switch (type) {
    case 'topup': 
    case 'sale': 
    case 'refund':
    case 'Sale':
    case 'offer_sale':
    case 'sale_for_gift':
    case 'bonus':
      return `+${formattedAmount} TON`
    case 'withdraw': 
    case 'offer': 
    case 'purchase': 
    case 'promote':
    case 'price_edit_package':
    case 'Cancel Sale':
    case 'offer_purchase':
    case 'gift_purchase':
      return `-${formattedAmount} TON`
    case 'listing':
      return `${formattedAmount} TON`
    case 'transfer_sent':
    case 'transfer_received':
    case 'gift_received':
    case 'gift_sent':
    case 'cancel_sale':
      return ''
    default: 
      return formattedAmount ? `${formattedAmount} TON` : ''
  }
}

const handleTopUp = (amount) => {
  if (!isWalletConnected.value) {
    alert('Пожалуйста, подключите кошелек для пополнения баланса')
    return
  }
  topUpAmount.value = amount
  showTopUpModal.value = true
}

const handleBalanceAction = (action) => {
  if (!isWalletConnected.value) {
    alert('Пожалуйста, подключите кошелек')
    showBalancePopup.value = false
    return
  }
  
  if (action === 'topup') {
    showTopUpModal.value = true
  } else if (action === 'withdraw') {
    showWithdrawModal.value = true
  }
  showBalancePopup.value = false
}

const validateWithdrawAmount = () => {
  if (withdrawAmount.value > currentAccount.value.ton_balance) {
    withdrawAmount.value = currentAccount.value.ton_balance
  }
  if (withdrawAmount.value < 0.1) {
    withdrawAmount.value = 0.1
  }
}

const showWithdrawAnimation = () => {
  if (isWithdrawAnimating.value) return
  
  isWithdrawAnimating.value = true
  showWithdrawNotification.value = true
  
  setTimeout(() => {
    showWithdrawNotification.value = false
    setTimeout(() => {
      isWithdrawAnimating.value = false
    }, 500)
  }, withdrawAnimationDuration)
}
const handleImageError = (event) => {
  // Если изображение не загрузилось, показываем заглушку
  event.target.src = partyPopperIcon; // Укажите путь к вашей заглушке
  event.target.classList.add('image-error');
};
// Генерация хэша из boc
const generateHashFromBoc = (boc, amount) => {
  try {
    const data = `${boc.substring(0, 100)}-${amount}-${Date.now()}`
    let hash = 0
    for (let i = 0; i < data.length; i++) {
      hash = ((hash << 5) - hash) + data.charCodeAt(i)
      hash = hash & hash
    }
    let hexHash = Math.abs(hash).toString(16)
    while (hexHash.length < 64) {
      hexHash = '0' + hexHash
    }
    return hexHash
  } catch (error) {
    return null
  }
}

// Генерация fallback хэша
const generateFallbackHash = (address, amount) => {
  const timestamp = Date.now()
  const data = `${address || 'unknown'}-${amount}-${timestamp}`
  let hash = 0
  for (let i = 0; i < data.length; i++) {
    hash = ((hash << 5) - hash) + data.charCodeAt(i)
    hash |= 0
  }
  let fallbackHash = (hash >>> 0).toString(16)
  while (fallbackHash.length < 64) {
    fallbackHash = Math.floor(Math.random() * 16).toString(16) + fallbackHash
  }
  return fallbackHash
}
// Добавьте после функции loadUserProfile или в любом удобном месте
const checkAndInitHighloadWallet = async () => {
  try {
    console.log('🏦 Инициализация Highload Wallet V3 R1...')
    const config = await initHighloadWallet()
    highloadWalletAddress.value = config.walletAddress
    isHighloadWalletInitialized.value = true
    
    const balance = await getHighloadWalletBalance()
    highloadWalletBalance.value = balance
    
    if (balance < 1) {
      console.warn(`⚠️ Highload Wallet баланс низкий: ${balance} TON`)
      console.log(`📝 Отправьте TON на адрес: ${highloadWalletAddress.value}`)
    } else {
      console.log(`✅ Highload Wallet готов, баланс: ${balance} TON`)
    }
    
    return true
  } catch (error) {
    console.error('❌ Ошибка инициализации Highload Wallet:', error)
    // Не показываем ошибку пользователю, просто логируем
    return false
  }
}
// В Profile.vue, замените существующую функцию confirmWithdraw на эту:

// Profile.vue - confirmWithdraw

const confirmWithdraw = async () => {
  if (!isWithdrawValid.value || isTransactionInProgress.value || !isWalletConnected.value) return

  try {
    isTransactionInProgress.value = true
    isLoading.value = true
    const amount = parseFloat(withdrawAmount.value)
    
    // Получаем адрес пользователя
    const userAddress = props.tonConnectUI.account?.address
    if (!userAddress) throw new Error('Не удалось получить адрес кошелька')
    
    // Получаем ID и имя пользователя
    const userId = currentAccount.value.id || currentAccount.value.name
    const userName = currentAccount.value.name || 'unknown'
    
    console.log(`💰 Запрос на вывод: ${amount} TON для ${userName} на адрес ${userAddress}`)
    console.log(`📝 Параметры: userId=${userId}, userName=${userName}, address=${userAddress}, amount=${amount}`)
    
    // Проверяем баланс в БД
    const { data: userData, error: fetchError } = await supabase
      .from('users')
      .select('ton_balance')
      .eq('name', currentAccount.value.name)
      .single()

    if (fetchError) throw fetchError
    if (!userData) throw new Error('Пользователь не найден')

    const currentBalance = parseFloat(userData.ton_balance)
    if (currentBalance < amount) {
      throw new Error('Недостаточно средств на балансе')
    }

    // ✅ ИСПРАВЛЕНО: 4 аргумента: userId, userName, address, amount
    const result = await sendWithdrawTransaction(
      userId,      // 1. ID пользователя
      userName,    // 2. Имя пользователя
      userAddress, // 3. Адрес кошелька
      amount       // 4. Сумма (ЧИСЛО)
    )
    
    if (result.success) {
      // Обновляем баланс в БД
      const newBalance = (currentBalance - amount).toFixed(2)
      const { error: updateError } = await supabase
        .from('users')
        .update({ ton_balance: newBalance })
        .eq('name', currentAccount.value.name)

      if (updateError) throw updateError

      // Обновляем локальное состояние
      currentAccount.value.ton_balance = parseFloat(newBalance)
      balance.value = parseFloat(newBalance)
      
      if (scoreStore.currentAccount) {
        scoreStore.currentAccount.ton_balance = parseFloat(newBalance)
      }
      
      // Сохраняем баланс в localStorage
      localStorage.setItem(`lastBalance_${currentAccount.value.name}`, newBalance)
      
      // Показываем анимацию
      lastWithdrawAmount.value = amount
      showWithdrawAnimation()
      showWithdrawModal.value = false
      
      // Записываем в историю с хэшем
      await addOperationToHistory('withdraw', amount, result.txHash)
      await loadOperationsHistory(true)
      
      alert(`✅ ${amount} TON успешно выведены на ваш кошелек!`)
    } else {
      throw new Error(result.error || 'Ошибка при выводе средств')
    }
  } catch (error) {
    console.error('Ошибка при выводе средств:', error)
    alert(error.message || 'Произошла ошибка при выводе средств')
  } finally {
    isTransactionInProgress.value = false
    isLoading.value = false
  }
}
const updateTonBalance = async (amount) => {
  try {
    const { data: userData, error } = await supabase
      .from('users')
      .select('ton_balance')
      .eq('name', currentAccount.value.name)
      .single()

    if (error) throw error

    const newBalance = (parseFloat(userData.ton_balance) || 0) + parseFloat(amount)
    
    const { error: updateError } = await supabase
      .from('users')
      .update({ ton_balance: newBalance })
      .eq('name', currentAccount.value.name)

    if (updateError) throw updateError

    currentAccount.value.ton_balance = newBalance
    balance.value = newBalance.toFixed(2)
    
    if (scoreStore.currentAccount) {
      scoreStore.currentAccount.ton_balance = newBalance
    }
    
    // Сохраняем баланс в localStorage
    localStorage.setItem(`lastBalance_${currentAccount.value.name}`, Number(newBalance).toFixed(2))

  } catch (error) {
    console.error('Error updating TON balance:', error)
    throw error
  }
}

// Функция для получения хэша из boc
const getHashFromBoc = (boc) => {
  try {
    // Создаем строку для хэширования из boc
    // Используем первые 100 символов boc + timestamp для уникальности
    const data = `${boc.substring(0, 100)}-${Date.now()}`
    
    let hash = 0
    for (let i = 0; i < data.length; i++) {
      hash = ((hash << 5) - hash) + data.charCodeAt(i)
      hash = hash & hash
    }
    
    let hexHash = Math.abs(hash).toString(16)
    while (hexHash.length < 64) {
      hexHash = '0' + hexHash
    }
    
    return hexHash
  } catch (error) {
    console.error('Ошибка генерации хэша из boc:', error)
    return null
  }
}

// Функция пополнения баланса
// Функция для ожидания и получения реального хэша транзакции через API
const waitForTransactionHash = async (walletAddress, expectedAmount, maxAttempts = 30) => {
  console.log("⏳ Ожидаем подтверждения транзакции...");
  
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    try {
      // Пробуем через toncenter.com API
      const response = await fetch(
        `https://toncenter.com/api/v2/getTransactions?address=${walletAddress}&limit=5`
      );
      
      if (response.ok) {
        const data = await response.json();
        
        if (data.ok && data.result && data.result.length > 0) {
          const expectedAmountNano = Math.floor(expectedAmount * 1000000000);
          
          // Ищем транзакцию с нашей суммой за последние 60 секунд
          for (const tx of data.result) {
            const txAmount = parseFloat(tx.amount) || 0;
            const txTime = new Date(tx.utime * 1000).getTime();
            const now = Date.now();
            
            // Проверяем сумму и время (последние 60 секунд)
            if (txAmount === expectedAmountNano && (now - txTime) < 60000) {
              const txHash = tx.transaction_id.hash;
              if (txHash && txHash.length === 64) {
                console.log(`📝 Получен реальный хэш: ${txHash}`);
                return txHash;
              }
            }
          }
          
          // Если не нашли по сумме, берем последнюю транзакцию за последние 30 секунд
          const lastTx = data.result[0];
          const txTime = new Date(lastTx.utime * 1000).getTime();
          const now = Date.now();
          
          if (now - txTime < 30000 && lastTx.transaction_id && lastTx.transaction_id.hash) {
            const txHash = lastTx.transaction_id.hash;
            console.log(`📝 Получен хэш последней транзакции: ${txHash}`);
            return txHash;
          }
        }
      }
    } catch (apiError) {
      console.warn('Ошибка при запросе к toncenter API:', apiError.message);
    }
    
    // Пробуем через tonscan.org API
    try {
      const response = await fetch(
        `https://tonscan.org/api/accounts/${walletAddress}/transactions?limit=1`
      );
      
      if (response.ok) {
        const data = await response.json();
        if (data && data.transactions && data.transactions.length > 0) {
          const tx = data.transactions[0];
          const txTime = new Date(tx.timestamp).getTime();
          const now = Date.now();
          
          // Проверяем, что транзакция свежая (последние 30 секунд)
          if (now - txTime < 30000 && tx.hash && tx.hash.length === 64) {
            console.log(`📝 Получен хэш из tonscan: ${tx.hash}`);
            return tx.hash;
          }
        }
      }
    } catch (apiError) {
      console.warn('Ошибка при запросе к tonscan:', apiError.message);
    }
    
    if (attempt % 5 === 0) {
      console.log(`⏳ Ожидание хэша... ${attempt + 1}/${maxAttempts} секунд`);
    }
  }
  
  console.warn(`⚠️ Не удалось получить реальный хэш транзакции за ${maxAttempts} секунд`);
  return null;
}

// Функция пополнения баланса
const topUpBalance = async (amount) => {
  if (!isWalletConnected.value) {
    alert('Сначала подключите кошелек')
    return
  }

  isLoading.value = true
  let txHash = null
  
  try {
    const transaction = {
      validUntil: Math.floor(Date.now() / 1000) + 300,
      messages: [
        {
          address: RECIPIENT_ADDRESS,
          amount: String(Math.floor(amount * 1000000000)),
        }
      ]
    }

    console.log('📤 Отправляем транзакцию пополнения...')
    console.log(`💰 Сумма: ${amount} TON`)
    
    const result = await props.tonConnectUI.sendTransaction(transaction)
    
    console.log('✅ Транзакция отправлена')
    
    // Получаем адрес отправителя
    const senderAddress = props.tonConnectUI.account?.address
    
    if (senderAddress) {
      // Получаем реальный хэш
      txHash = await waitForTransactionHash(senderAddress, amount, 30)
    }
    
    // Если не удалось получить реальный хэш, пробуем из результата
    if (!txHash) {
      if (result.hash) {
        txHash = result.hash
      } else if (result.transaction?.hash) {
        txHash = result.transaction.hash
      } else if (result.txId) {
        txHash = result.txId
      } else if (result.boc) {
        // Генерируем из boc
        txHash = generateHashFromBoc(result.boc, amount)
      }
    }
    
    // Fallback
    if (!txHash) {
      txHash = generateFallbackHash(senderAddress, amount)
      console.warn(`⚠️ Используем fallback хэш: ${txHash}`)
    } else {
      console.log(`✅ Получен хэш транзакции: ${txHash}`)
    }
    
    console.log(`🔗 Ссылка: https://tonscan.org/tx/${txHash}`)
    
    // Обновляем баланс
    await updateTonBalance(amount)
    await fetchBalance(true)
    
    showTopUpModal.value = false
    
    console.log('💸 ПОПОЛНЕНИЕ:')
    console.log(`💰 Сумма: ${amount} TON`)
    console.log(`🔗 Хэш: ${txHash}`)
    
    // ✅ Записываем в историю с хэшем
    await addOperationToHistory('topup', amount, txHash)
    await loadOperationsHistory(true)
    
    alert(`✅ Баланс успешно пополнен на ${amount} TON!\nTransaction ID: ${txHash}`)
    
  } catch (error) {
    console.error('❌ Ошибка транзакции:', error)
    if (!error.message.includes('Rejected by user')) {
      alert(`❌ Ошибка: ${error.message}`)
    } else {
      alert('Транзакция отменена')
    }
  } finally {
    isLoading.value = false
  }
}
onMounted(async () => {
  console.log('🚀 Profile.vue mounted')
  
  
  // Слушаем события транзакций от TonConnectUI
  if (props.tonConnectUI) {
    props.tonConnectUI.onStatusChange((walletInfo) => {
      console.log('Статус кошелька изменился:', walletInfo)
      
      // Если есть последняя транзакция, получаем ее хэш
      if (props.tonConnectUI.lastTransactionId) {
        console.log('Последний хэш транзакции:', props.tonConnectUI.lastTransactionId)
      }
    })
  }
})
// Функция для форматирования username (обрезание если длинный)
const formatUsername = (username, maxLength = 10) => {
  if (!username) return '';
  if (username.length <= maxLength) return username;
  return `${username.substring(0, maxLength)}...`;
};

// Состояние для отслеживания раскрытых username
const expandedUsernames = ref(new Set());

// Функция для переключения раскрытия username
const toggleUsername = (operationId, event) => {
  event.stopPropagation();
  if (expandedUsernames.value.has(operationId)) {
    expandedUsernames.value.delete(operationId);
  } else {
    expandedUsernames.value.add(operationId);
  }
  expandedUsernames.value = new Set(expandedUsernames.value);
};

// Функция для получения отображаемого username (с поддержкой sender/recipient)
const getDisplayUsername = (operation, type = 'recipient') => {
  const username = type === 'sender' ? operation.sender_username : operation.recipient_username;
  if (!username) return '';
  if (expandedUsernames.value.has(operation.id)) {
    return username;
  }
  return formatUsername(username);
};

const fetchBalance = async (forceRefresh = false) => {
  try {
    const { data: userData, error } = await supabase
      .from('users')
      .select('ton_balance')
      .eq('name', currentAccount.value.name)
      .single()

    if (!error && userData) {
      balance.value = userData.ton_balance
      currentAccount.value.ton_balance = userData.ton_balance
      
      if (scoreStore.currentAccount) {
        scoreStore.currentAccount.ton_balance = userData.ton_balance
      }
      
      // Сохраняем баланс в localStorage
      localStorage.setItem(`lastBalance_${currentAccount.value.name}`, Number(userData.ton_balance).toFixed(2))
    }
  } catch (error) {
    console.error('Database balance error:', error)
  }
}

const confirmTopUp = () => {
  if (!isWalletConnected.value) {
    alert('Пожалуйста, подключите кошелек')
    return
  }
  
  topUpAmount.value = Math.round(topUpAmount.value * 100) / 100
  
  const amount = parseFloat(topUpAmount.value)
  if (isNaN(amount)) {
    alert('Пожалуйста, введите корректную сумму')
    return
  }
  if (amount < 0.01) {
    alert('Минимальная сумма пополнения 0.01 TON')
    return
  }
  if (amount > 10) {
    alert('Максимальная сумма пополнения 10 TON')
    return
  }
  topUpBalance(amount)
}

const validateAmountInput = (amount, field) => {
  let value = amount.replace(/[^\d.]/g, '')
  
  const parts = value.split('.')
  if (parts.length > 2) {
    value = parts[0] + '.' + parts.slice(1).join('')
  }
  
  if (parts.length === 2 && parts[1].length > 2) {
    value = parts[0] + '.' + parts[1].substring(0, 2)
  }
  
  if (field === 'topUp') {
    topUpAmount.value = value
  } else {
    withdrawAmount.value = value
  }
}

// ОСНОВНАЯ ФУНКЦИЯ ЗАГРУЗКИ ПРОФИЛЯ - ВСЕГДА ГРУЗИТ ИЗ БД
const loadUserProfile = async () => {
  try {
    console.log('🔄 ЗАГРУЗКА ПРОФИЛЯ ИЗ БД...')
    
    const savedAccount = localStorage.getItem('currentAccount')
    const savedLoginState = localStorage.getItem('isLoggedIn')
    
    if (!savedAccount || savedLoginState !== 'true') {
      console.log('📭 Нет сохраненного аккаунта')
      router.push('/register')
      return
    }

    const account = JSON.parse(savedAccount)
    console.log('👤 Загружаем профиль для:', account.name)
    
    const { data: userData, error } = await supabase
      .from('users')
      .select('*')
      .eq('name', account.name)
      .maybeSingle()

    if (error) throw error
    if (!userData) {
      console.error('❌ Пользователь не найден в базе данных')
      await logout()
      return
    }

    // Обновляем стор с добавлением всех полей
    scoreStore.setCurrentAccount({
      name: userData.name,
      score: userData.score || 0,
      ton_balance: userData.ton_balance || 0,
      avatar_link: userData.avatar_link,
      username: userData.username,
      language_code: userData.language_code || 'ru' // Добавляем language_code
    })
    
    // Обновляем локальное состояние с добавлением всех полей
    currentAccount.value = {
      name: userData.name,
      score: userData.score || 0,
      ton_balance: userData.ton_balance || 0,
      avatar_link: userData.avatar_link,
      username: userData.username,
      first_name: userData.first_name,
      massiv: userData.massiv,
      language_code: userData.language_code || 'ru' // Добавляем language_code
    }
    
    balance.value = userData.ton_balance || 0
    
    // Сохраняем баланс в localStorage для быстрого показа при следующем открытии
    localStorage.setItem(`lastBalance_${userData.name}`, userData.ton_balance || 0)
    
    console.log('✅ Профиль загружен из БД:', userData.name, 'баланс:', userData.ton_balance)
    console.log('📝 Language code из БД:', userData.language_code) // Лог для отладки
    
    await saveTelegramData()

    // Загружаем историю операций
    await loadOperationsHistory()
    
    isFirstLoadComplete.value = true
    
  } catch (error) {
    console.error('❌ Ошибка загрузки профиля:', error)
    if (error.message.includes('JWT')) {
      await logout()
    }
  }
}



const logout = async () => {
  try {
    await props.tonConnectUI?.disconnect()
  } catch (error) {
    console.error('Ошибка отключения кошелька:', error)
  }
  
  localStorage.removeItem('currentAccount')
  localStorage.removeItem('isLoggedIn')
  if (currentAccount.value.name) {
    localStorage.removeItem(`lastBalance_${currentAccount.value.name}`)
  }
  scoreStore.setCurrentAccount(null)
  router.push('/register')
}

const navigateToTasks = () => {
  router.push('/tasks')
}

const navigateToFriends = () => {
  router.push('/friends')
}

// Переменные для записи подключений
const isRecordingConnection = ref(false)
const isRecordingDisconnection = ref(false)
// Функция для преобразования ссылки Telegram в ссылку на изображение Fragment
const getNftImageUrl = (link) => {
  if (!link) return null;
  
  // Извлекаем идентификатор NFT из ссылки
  // Пример: https://t.me/nft/KhabibsPapakha-10730
  const match = link.match(/\/nft\/(.+)$/);
  if (match && match[1]) {
    const nftId = match[1];
    return `https://nft.fragment.com/gift/${nftId}.webp`;
  }
  
  return null;
};

const recordWalletConnection = async () => {
  if (isRecordingConnection.value) {
    return
  }
  
  if (!currentAccount.value.name) {
    return
  }
  
  if (!isWalletConnected.value) {
    return
  }
  
  isRecordingConnection.value = true
  
  try {
    console.log('📝 Записываем подключение кошелька')
    await addOperationToHistory('wallet_connect')
    await loadOperationsHistory(true)
  } catch (error) {
    console.error('❌ Ошибка при записи подключения кошелька:', error)
  } finally {
    setTimeout(() => {
      isRecordingConnection.value = false
    }, 2000)
  }
}

const recordWalletDisconnection = async () => {
  if (!currentAccount.value.name) {
    return
  }
  
  if (!lastKnownWalletAddress.value) {
    return
  }
  
  try {
    console.log('📝 Записываем отключение кошелька')
    await addOperationToHistory('wallet_disconnect')
  } catch (error) {
    console.error('❌ Ошибка записи отключения:', error)
  }
}

let isProcessingWalletChange = false
let lastWalletChangeTime = 0
// В шаблоне, где проверяется наличие изображения:
const operationsWithImage = ['listing', 'purchase', 'Sale', 'Cancel Sale', 'sale', 'cancel_sale', 'offer', 'promote', 'transfer_sent'];
const handleWalletStatusChange = async (walletInfo) => {
  const now = Date.now()
  
  if (now - lastWalletChangeTime < 2000) {
    return
  }
  
  if (isProcessingWalletChange) {
    return
  }
  
  isProcessingWalletChange = true
  lastWalletChangeTime = now
  
  try {
    const isNowConnected = !!walletInfo?.account
    const walletAddress = walletInfo?.account?.address
    
    await new Promise(resolve => setTimeout(resolve, 300))
    
    if (isNowConnected && walletAddress) {
      lastKnownWalletAddress.value = walletAddress
      await fetchBalance(true)
      
      if (currentAccount.value.name) {
        await recordWalletConnection()
      }
    } 
    else if (!isNowConnected && lastKnownWalletAddress.value && currentAccount.value.name) {
      await recordWalletDisconnection()
    }
  } catch (error) {
    console.error('❌ Ошибка обработки изменения статуса:', error)
  } finally {
    isProcessingWalletChange = false
  }
}

// Watch для отслеживания
watch(
  () => props.tonConnectUI?.connected,
  () => updateWalletStatus(),
  { immediate: true }
);

watch(
  () => props.tonConnectUI,
  () => updateWalletStatus(),
  { immediate: true, deep: true }
);

// В onMounted добавь:
onMounted(async () => {
  console.log('🚀 Profile.vue mounted')
  
  // Принудительная проверка
  setTimeout(() => updateWalletStatus(), 50);
  
  // ... остальной код
});
watch(() => props.tonConnectUI?.account?.balance, debounce(() => {
  fetchBalance(true)
}, 1000))

watch(() => props.tonConnectUI?.account, async (newAccount, oldAccount) => {
  if (newAccount) {
    lastKnownWalletAddress.value = newAccount.address
    fetchBalance(true)
    
    if (newAccount && !oldAccount && currentAccount.value.name && isFirstLoadComplete.value) {
      setTimeout(async () => {
        await recordWalletConnection()
      }, 500)
    }
  } else if (oldAccount && !newAccount && currentAccount.value.name && isFirstLoadComplete.value) {
    setTimeout(async () => {
      await recordWalletDisconnection()
    }, 500)
  }
}, { immediate: true, deep: true })

// Profile.vue - оставь только этот onMounted, остальные удали
onMounted(async () => {
  console.log('🚀 Profile.vue mounted - НАЧАЛО ЗАГРУЗКИ')
  
  // Инициализируем систему вывода
  await initWithdrawSystem()
  
  // Подписываемся на изменения
  subscribeToChannel('market_changes', () => {
    loadUserProfile()
  })
  
  // Загружаем профиль из БД
  await loadUserProfile()
  
  // Настраиваем слушатели кошелька
  setupTonConnectListeners()
  
  // Периодическое обновление баланса
  const interval = setInterval(() => {
    if (currentAccount.value.name) {
      fetchBalance(true)
    }
  }, 30000)
  
  // 👇 ДОБАВЬТЕ ЭТУ СТРОЧКУ
  checkAndOpenBalancePopup()
  
  onUnmounted(() => {
    clearInterval(interval)
    cleanupTonConnectListeners()
    unsubscribeFromChannel('market_changes')
  })
})
onMounted(async () => {
  console.log('🚀 Profile.vue mounted - НАЧАЛО ЗАГРУЗКИ')
  
  // Инициализируем систему вывода
  await initWithdrawSystem()
  
  // Подписываемся на изменения
  subscribeToChannel('market_changes', () => {
    loadUserProfile()
  })
  
  // Загружаем профиль из БД
  await loadUserProfile()
  
  // Настраиваем слушатели кошелька
  setupTonConnectListeners()
  
  // Периодическое обновление баланса
  const interval = setInterval(() => {
    if (currentAccount.value.name) {
      fetchBalance(true)
    }
  }, 30000)
  
  onUnmounted(() => {
    clearInterval(interval)
    cleanupTonConnectListeners()
    unsubscribeFromChannel('market_changes')
  })
})

const cleanupTonConnectListeners = () => {
  if (props.tonConnectUI) {
    props.tonConnectUI.onStatusChange(() => {})
  }
}

const formattedWithdrawAmountInModal = computed(() => {
  const amount = parseFloat(withdrawAmount.value)
  return isNaN(amount) ? '0.00' : amount.toFixed(2)
})
</script>

<style scoped>
/* Добавляем новые стили для отключенных кнопок */
.disabled-btn {
  opacity: 0.5 !important;
  cursor: not-allowed !important;
  pointer-events: none !important;
}

.disabled-action-btn {
  opacity: 0.5 !important;
  cursor: not-allowed !important;
  pointer-events: none !important;
  background-color: #555 !important;
  color: #888 !important;
}

.disabled-primary-btn {
  opacity: 0.5 !important;
  cursor: not-allowed !important;
  background-color: #666 !important;
  color: #999 !important;
}

.wallet-notice {
  margin-top: 10px;
  padding: 8px;
  background-color: rgba(255, 187, 0, 0.1);
  border-radius: 6px;
  text-align: center;
  font-size: 12px;
  color: #ffbb00;
}

.wallet-required-notice {
  margin-top: 10px;
  padding: 8px;
  background-color: rgba(255, 68, 68, 0.1);
  border-radius: 6px;
  text-align: center;
  font-size: 12px;
  color: #ff4444;
}

/* Стили для истории операций */
.operations-history-modal {
  max-width: 450px;
}

.operations-list {
  max-height: 400px;
  overflow-y: auto;
  margin: 10px 0;
}

.operation-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  margin-bottom: 8px;
  border-radius: 8px;
  background-color: var(--surface-light);
  border-left: 4px solid;
  transition: all 0.2s;
}

.operation-topup {
  border-left-color: #00E676;
}

.operation-withdraw {
  border-left-color: #FF4444;
}

.operation-wallet-connect {
  border-left-color: #CCCCCC;
}

.operation-wallet-disconnect {
  border-left-color: #999999;
}

.operation-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.operation-type-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.operation-type {
  font-weight: 600;
  font-size: 14px;
  color: var(--text);
}

.operation-date {
  font-size: 12px;
  color: var(--text-secondary);
}

.operation-amount {
  font-weight: 700;
  font-size: 16px;
  margin-left: 10px;
  white-space: nowrap;
  display: flex;
  align-items: center;
  justify-content: center;
}

.amount-positive {
  color: #00E676;
}

.amount-negative {
  color: #FF4444;
}

.amount-neutral {
  color: transparent;
}

.empty-history {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-secondary);
  font-style: italic;
}

/* Иконка party popper */
.party-popper-icon {
  width: 16px;
  height: 16px;
  object-fit: contain;
  vertical-align: middle;
}

.party-popper-icon-amount {
  width: 24px;
  height: 24px;
  object-fit: contain;
}

/* Кнопка истории в баланс-попапе */
.balance-action-btn.history {
  background-color: #6c757d;
  color: white;
  border: none;
}

.balance-action-btn.history:hover {
  background-color: #5a6268;
}

/* Остальные стили остаются без изменений */
.nft-links-section {
  background-color: var(--surface);
  border-radius: 12px;
  padding: 15px;
  margin-top: 15px;
  border: 2px solid var(--accent);
}

.nft-links-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.nft-link-item {
  background-color: var(--surface-light);
  border-radius: 6px;
  padding: 10px;
  text-align: center;
}

.nft-link {
  color: var(--accent);
  text-decoration: none;
  font-weight: 600;
  display: block;
  padding: 8px;
  transition: all 0.2s;
}

.nft-link:hover {
  color: #E6B000;
  text-decoration: underline;
}

.balance-container-wrapper {

  gap: 8px;
}

.withdraw-notification {
  position: absolute;
  top: calc(100% + 5px);
  left: 50%;
  transform: translateX(-50%);
  color: #ff4444;
  font-weight: bold;
  font-size: 18px;
  text-shadow: 0 0 2px rgba(0, 0, 0, 0.5);
  white-space: nowrap;
  pointer-events: none;
  z-index: 10;
}

.withdraw-animation-enter-active,
.withdraw-animation-leave-active {
  transition: all 0.5s ease;
}

.withdraw-animation-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(-25px);
}

.withdraw-animation-enter-to {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}

.withdraw-animation-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-15px);
}

.amount-input {
  text-align: center;
}

.quick-amounts {
  display: flex;
  gap: 8px;
  margin: 12px 0;
  flex-wrap: wrap;
}

.quick-amounts button {
  padding: 6px 10px;
  background-color: var(--surface-light);
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--text);
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.quick-amounts button:hover {
  background-color: var(--accent);
  color: #000;
}

.total-info {
  font-weight: bold;
  margin: 8px 0;
  color: var(--accent);
}

.wallet-info {
  font-size: 12px;
  color: var(--text-secondary);
  word-break: break-all;
  background: var(--surface-light);
  padding: 8px;
  border-radius: 6px;
  margin-top: 10px;
}

.app {
  overflow-x: hidden;
  min-width: 100%;
  margin: 0 auto;
  background-color: var(--bg);
  min-height: 100vh;
  font-family: 'Inter', sans-serif;
  color: var(--text);
  width: 100%;
  max-width: 100%;
  position: relative;
  box-sizing: border-box;
}

.dark-theme {
  --bg: #1d1d1d;
  --surface: #1E1E1E;
  --surface-light: #2A2A2A;
  --text: #FFFFFF;
  --text-secondary: #B0B0B0;
  --accent: #FFbb00;
  --border: #333333;
  --success: #00E676;
}

/* Шапка */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: var(--surface);
  border-bottom: 1px solid var(--border);
}

.header-actions {
  display: flex;
  gap: 10px;
}

.logo {
  font-weight: 700;
  font-size: 18px;
  color: var(--accent);
}

.balance-container {
  display: flex;
  align-items: center;
  height: 39px;
  background-color: var(--accent);
  border-radius: 20px;
  padding: 0 8px;
  gap: 6px;
  padding-left: 16px;
  padding-right: 1px;
  min-width: fit-content;
  cursor: pointer;
  margin-top: -3px;
  transition: transform 0.2s;
  margin-left: -20px;
}

.balance-container:hover {
  transform: scale(1.05);
}

.balance {
  font-weight: 600;
  color: #1E1E1E;
  font-size: 18px;
  line-height: 24px;
}

.balance-icon {
  width: 16px;
  height: 16px;
}

.logout-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 4px;
}

/* Основной контент */
.content {
  padding: 15px;
}

/* Профиль */
.profile-card {
  background-color: var(--accent);
  border-radius: 12px;
  padding: 20px 15px;
  text-align: center;
  margin-bottom: 15px;
  color: #FFae00;
}

.avatar {
  width: 80px;
  height: 80px;
  border-radius: 10px;
  object-fit: cover;
  margin-bottom: 12px;
}

.username {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 10px;
  color: #000;
}

.score {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 6px;
  font-size: 18px;
  font-weight: 600;
  color: #ff9900;
}

.frog-icon {
  width: 20px;
  height: 20px;
}

.quick-topup {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  justify-content: center;
}

.quick-topup button {
  padding: 6px 12px;
  background-color: #2A2A2A;
  color: white;
  border: 1px solid #333;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 12px;
}

.quick-topup button:hover:not(.disabled-btn) {
  background-color: #333;
  border-color: #444;
}

/* NFT Секция */
.nft-section {
  background-color: var(--surface);
  border-radius: 12px;
  padding: 15px;
  border: 2px solid var(--accent);
}

.nft-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--text);
}

.nft-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-bottom: 15px;
}

.nft-item {
  aspect-ratio: 1;
}

.nft-badge {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  font-weight: 600;
  background-color: var(--surface-light);
  color: var(--text-secondary);
  font-size: 14px;
}

.nft-badge.active {
  background-color: var(--accent);
  color: #000;
}

.nft-btn {
  width: 100%;
  padding: 12px;
  background-color: var(--accent);
  color: #000;
  border: none;
  border-radius: 6px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 10px;
}

.nft-btn:hover {
  background-color: #ffbb00;
}

/* Модальное окно */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  background-color: var(--surface);
  border-radius: 10px;
  width: 90%;
  max-width: 350px;
  padding: 15px;
  border: 1px solid var(--border);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.modal-header h3 {
  margin: 0;
  color: var(--accent);
  font-size: 18px;
}

.close-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 22px;
  cursor: pointer;
  padding: 0;
}

.input-group {
  margin-bottom: 12px;
}

.input-group label {
  display: block;
  margin-bottom: 6px;
  color: var(--text-secondary);
  font-size: 14px;
}

.amount-input {
  width: 100%;
  padding: 10px;
  background-color: var(--surface-light);
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--text);
  font-size: 14px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.btn-secondary {
  padding: 8px 16px;
  background: none;
  border: 1px solid var(--border);
  border-radius: 5px;
  color: var(--text);
  cursor: pointer;
  font-size: 14px;
}

.btn-primary {
  padding: 8px 16px;
  background-color: var(--accent);
  border: none;
  border-radius: 5px;
  color: #000;
  font-weight: bold;
  cursor: pointer;
  font-size: 14px;
}

.btn-primary:disabled,
.btn-primary.disabled-primary-btn {
  opacity: 0.5;
  cursor: not-allowed;
}

.fee-info, .total-info {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 8px 0;
  text-align: center;
}

.total-info {
  font-weight: bold;
  color: var(--accent);
}

/* Попап баланса */
.balance-popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.balance-popup {
  background-color: var(--surface);
  border-radius: 10px;
  width: 90%;
  max-width: 300px;
  padding: 15px;
  border: 1px solid var(--border);
}

.balance-popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.balance-popup-header h3 {
  margin: 0;
  font-size: 16px;
  color: var(--accent);
}

.balance-popup-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.balance-action-btn {
  padding: 12px;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
  text-align: center;
}

.balance-action-btn.top-up {
  background-color: #0088cc;
  color: white;
}

.balance-action-btn.top-up:hover:not(.disabled-action-btn) {
  background-color: #006699;
}

.balance-action-btn.withdraw {
  background-color: var(--surface-light);
  color: var(--text);
  border: 1px solid var(--border);
}

.balance-action-btn.withdraw:hover:not(.disabled-action-btn) {
  background-color: #333;
}

/* Кошелек */
.ton-connect-wrapper {
  display: flex;
  margin: 15px 0;
  right: 50px;
}

#ton-connect {
  width: 200px;
  height: 42px;
}

html, body {
  overflow-x: hidden;
  width: 100%;
  margin: 0;
  padding: 0;
}

.profile-card {
  background-color: #ffbb00;
  border-radius: 30px;
  padding: 20px 15px;
  text-align: center;
  margin-bottom: 15px;
  color: #000;
  box-shadow: 0 4px 12px rgba(255, 187, 0, 0.3);
}

.avatar {
  width: 80px;
  height: 80px;
  border-radius: 10px;
  object-fit: cover;
  margin-bottom: 12px;
}

.username {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 10px;
  color: #000;
}

.score {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 6px;
  font-size: 18px;
  font-weight: 600;
  color: #ffffff;
}

.frog-icon {
  width: 20px;
  height: 20px;
}

.quick-topup {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  justify-content: center;
}

.quick-topup button {
  padding: 6px 12px;
  background-color: #2a2a2a;
  color: #ffbb00;
  border: 1px solid #333;
  border-radius: 30px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 12px;
  font-weight: bold;
}

.quick-topup button:hover:not(.disabled-btn) {
  background-color: #2a2a2a;
  border-color: #444;
}

/* КНОПКА NFT */
.nft-btn {
  width: 100%;
  padding: 12px;
  background-color: #ffbb00;
  color: #1d1d1d;
  border: none;
  border-radius: 30px;
  font-weight: 900;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 20px;
  margin-bottom: 10px;
  box-shadow: 0 4px 8px rgba(255, 187, 0, 0.2);
}

.nft-btn:hover {
  background-color: #ffc400;
  transform: translateY(-2px);
}

/* НОВЫЕ КАРТОЧКИ С ГРАДИЕНТОМ */
.sections-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 25px;
  background-color: #3535355e;
  padding: 10px;
  border-radius: 30px;
  border: 2px solid #2c2c2c;
  width: 100%;
}

.gradient-card {
  background: linear-gradient(90deg, #0e0e0e 0%, #1d1d1db0 20%, #ffbb0088 100%);
  border-radius: 25px;
  padding: 18px 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.card-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title-friends {
  font-size: 18px;
  font-weight: 700;
  margin: 0;
  background: #ffbb00;
  border: none;
  border-radius: 10px;
  color: #000000;
  cursor: pointer;
  font-size: 1.1rem;
  padding: 17px 14px 15px 14px;
  transition: all 0.2s ease;
  font-weight: 700;
  min-width: 100px !important; 
  text-align: center;
}

.card-arrow-friends {
  background: rgba(255, 196, 0, 0.26);
  border: none;
  text-align: center;
  border-radius: 20px;
  color: #ffc400;
  cursor: pointer;
  font-size: 0.9rem;
  padding: 15px 24px;
  transition: all 0.2s ease;
  font-weight: 500;
  font-size: 20px;
  font-weight: 600;
  min-width: 127px !important; 
}

.card-title {
  font-size: 50px;
  margin: 0;
  background: #ffbb00;
  border: none;
  border-radius: 10px;
  color: #000000;
  cursor: pointer;
  padding: 17px 28px 16px 28px;
  transition: all 0.2s ease;
  font-weight: 600;
}

.card-arrow {
  background: rgba(255, 196, 0, 0.26);
  border: none;
  border-radius: 20px;
  color: #ffc400;
  cursor: pointer;
  font-size: 0.9rem;
  padding: 15px 18px;
  transition: all 0.2s ease;
  font-weight: 500;
  font-size: 24px;
  font-weight: 600;
}

/* АНИМАЦИЯ ВЫВОДА */
.withdraw-notification {
  position: absolute;
  top: calc(100% + 5px);
  left: 50%;
  transform: translateX(-50%);
  color: #ff4444;
  font-weight: bold;
  font-size: 18px;
  text-shadow: 0 0 2px rgba(0, 0, 0, 0.5);
  white-space: nowrap;
  pointer-events: none;
}

.withdraw-animation-enter-active,
.withdraw-animation-leave-active {
  transition: all 0.5s ease;
}

.withdraw-animation-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(-25px);
}

.withdraw-animation-enter-to {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}

.withdraw-animation-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-15px);
}

/* АДАПТИВНОСТЬ */
@media (max-width: 768px) {
  .content {
    padding: 10px;
  }
  
  .sections-container {
    gap: 12px;
  }
  
  .gradient-card {
    padding: 15px 18px;
  }
  
  .card-title {
    font-size: 16px;
  }
  
  .card-arrow {
    font-size: 20px;
  }
}

.card-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}

.card-title, .card-title-friends {
  transition: transform 0.2s ease;
  margin: 0;
  will-change: transform;
}

.slider-track {
  position: relative;
  width: 100%;
  height: 55px;
  overflow: hidden;
  cursor: grab;
  user-select: none;
  -webkit-user-select: none;
  -webkit-touch-callout: none;
  background: rgba(255, 187, 0, 0.05);
  border-radius: 10px 20px 20px 10px;
}

.bonus-text{
  color: #707070;
  font-size: 20px;
  font-weight: 600;
  padding: 10px 10px 3px 10px;
}

.balance-container-wrapper {
  gap: 8px;
}

.offers-btn {
  width: 100%;
  padding: 12px;
  color: #707070;
  border: none;
  border-radius: 30px;
  font-weight: 900;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 20px;
  margin-bottom: 10px;
  border: 2px solid #2c2c2c;
  background-color: #3535355e;
}


.wallet-address {
  font-size: 12px;
  color: #888;
  font-family: monospace;
  margin: 2px 0;
}
/* Стили для операции отключения кошелька */
.operation-wallet-disconnect .operation-type {
  color: #ff4444 !important; /* Красный цвет для текста */
}

/* Убираем иконку party popper для отключения */
.operation-wallet-disconnect .party-popper-icon {
  display: none !important;
}

.operation-wallet-disconnect .party-popper-icon-amount {
  display: none !important;
}

/* Стили для операции подключения кошелька */
.operation-wallet-connect .operation-type {
  color: #00E676 !important; /* Зеленый цвет для подключения */
}

/* Общие стили для операции */
.operation-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  margin-bottom: 8px;
  border-radius: 8px;
  background-color: var(--surface-light);
  border-left: 4px solid;
  transition: all 0.2s;
}

.operation-wallet-connect {
  border-left-color: #00E676; /* Зеленая граница для подключения */
}

.operation-wallet-disconnect {
  border-left-color: #ff4444; /* Красная граница для отключения */
}

/* Остальные стили остаются такими же */
.operation-topup {
  border-left-color: #00E676;
}

.operation-withdraw {
  border-left-color: #FF4444;
}

.operation-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.operation-type-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.operation-type {
  font-weight: 600;
  font-size: 14px;
  color: var(--text);
}

/* Специально для подключения/отключения делаем шрифт жирнее */
.operation-wallet-connect .operation-type,
.operation-wallet-disconnect .operation-type {
  font-weight: 700;
  font-size: 15px;
}

.wallet-address {
  font-size: 12px;
  color: #888;
  font-family: monospace;
  margin: 2px 0;
}

.operation-date {
  font-size: 12px;
  color: var(--text-secondary);
}

.operation-amount {
  font-weight: 700;
  font-size: 16px;
  margin-left: 10px;
  white-space: nowrap;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Для подключения кошелька - прозрачный текст, но иконка видна */
.operation-wallet-connect .operation-amount {
  color: transparent;
}

/* Для отключения кошелька - красный цвет и скрываем сумму */
.operation-wallet-disconnect .operation-amount {
  color: transparent;
}

.amount-positive {
  color: #00E676;
}

.amount-negative {
  color: #FF4444;
}

/* Иконки */
.party-popper-icon {
  width: 16px;
  height: 16px;
  object-fit: contain;
}

.party-popper-icon-amount {
  width: 24px;
  height: 24px;
  object-fit: contain;
}

/* Убираем иконку для отключения */
.operation-wallet-disconnect .party-popper-icon,
.operation-wallet-disconnect .party-popper-icon-amount {
  display: none;
}
.operation-offer {
  border-left-color: #FF4444;
}

.operation-purchase {
  border-left-color: #FF4444;
}

.operation-promote {
  border-left-color: #FF4444;
}

.operation-sale {
  border-left-color: #00E676;
}
/* Стили для истории операций */
.operations-history-modal {
  max-width: 450px;
}

.operations-list {
  max-height: 400px;
  overflow-y: auto;
  margin: 10px 0;
}

.operation-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  margin-bottom: 8px;
  border-radius: 8px;
  background-color: var(--surface-light);
  border-left: 4px solid;
  transition: all 0.2s;
}

.operation-topup {
  border-left-color: #00E676;
}

.operation-withdraw {
  border-left-color: #FF4444;
}

.operation-offer {
  border-left-color: #FF4444;
}

.operation-purchase {
  border-left-color: #FF4444;
}

.operation-promote {
  border-left-color: #FF4444;
}

.operation-sale {
  border-left-color: #00E676;
}

.operation-wallet-connect {
  border-left-color: #00E676;
}

.operation-wallet-disconnect {
  border-left-color: #FF4444;
}

.operation-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.operation-type-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.operation-type {
  font-weight: 600;
  font-size: 14px;
  color: var(--text);
}

.operation-date {
  font-size: 12px;
  color: var(--text-secondary);
}

.operation-amount {
  font-weight: 700;
  font-size: 16px;
  margin-left: 10px;
  white-space: nowrap;
  display: flex;
  align-items: center;
  justify-content: center;
}

.amount-positive {
  color: #00E676;
}

.amount-negative {
  color: #FF4444;
}

.amount-neutral {
  color: transparent;
}

.empty-history {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-secondary);
  font-style: italic;
}

/* Иконка party popper */
.party-popper-icon {
  width: 16px;
  height: 16px;
  object-fit: contain;
  vertical-align: middle;
}

.party-popper-icon-amount {
  width: 24px;
  height: 24px;
  object-fit: contain;
}
/* В секции стилей для operation-item добавьте: */
.operation-refund {
  border-left-color: #00E676; /* Зелёный цвет как у topup и sale */
}
/* В секцию стилей добавьте CSS для скелетонов */
.operation-skeleton {
  display: flex;
  flex-direction: column;
  padding: 15px;
  margin-bottom: 10px;
  background-color: var(--surface-light);
  border-radius: 8px;
  border-left: 4px solid var(--surface-light);
  position: relative;
  overflow: hidden;
  min-height: 70px;
}

.skeleton-line {
  background: linear-gradient(90deg, 
    var(--surface-light) 25%, 
    #3a3a3a 50%, 
    var(--surface-light) 75%);
  background-size: 200% 100%;
  border-radius: 4px;
  animation: skeleton-loading 1.5s infinite;
}

.skeleton-line.title {
  height: 16px;
  width: 60%;
  margin-bottom: 8px;
}

.skeleton-line.date {
  height: 12px;
  width: 40%;
  margin-bottom: 10px;
}

.skeleton-line.amount {
  height: 18px;
  width: 30%;
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
}

@keyframes skeleton-loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* Модифицируйте существующие стили */
.operations-list {
  max-height: 400px;
  overflow-y: auto;
  margin: 10px 0;
  min-height: 150px; /* Минимальная высота для плавного перехода */
}

.empty-history {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-secondary);
  font-style: italic;
  min-height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
}
/* Добавьте после operation-refund или в любое место в стилях */
.operation-cancel-sale {
  border-left-color: #CCCCCC; /* Серый цвет как у wallet_connect */
}
/* Добавьте после operation-offer или в любое место в стилях */
.operation-price-edit {
  border-left-color: #FF4444; /* Красный цвет как у withdraw/offer */
}
/* Стили для операций с NFT */
.operation-listing {
  border-left-color: #FF4444; /* Красный для листинга */
}

.operation-sale,
.operation-sale.amount-positive {
  border-left-color: #00E676; /* Зеленый для продажи */
}

.operation-cancel-sale {
  border-left-color: #CCCCCC; /* Серый для отмены */
}

/* Контейнер для правой части операции */
.operation-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* Миниатюра NFT */
.nft-thumbnail {
  width: 50px;
  height: 50px;
  border-radius: 8px;
  object-fit: cover;
  transition: transform 0.2s;
}

.nft-thumbnail:hover {
  transform: scale(1.1);
}

.nft-thumbnail.image-error {
  opacity: 0.5;
  background-color: var(--surface-light);
}

/* Название NFT */
.nft-name {
  font-size: 12px;
  color: var(--accent);
  font-weight: 500;
  margin-left: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 150px;
}

/* Адаптивность для мобильных */
@media (max-width: 480px) {
  .nft-thumbnail {
    width: 32px;
    height: 32px;
  }
  
  .nft-name {
    max-width: 100px;
    font-size: 10px;
  }
  
  .operation-right {
    gap: 8px;
  }
}
/* Стили для операций с NFT */
.operation-listing {
  border-left-color: #CCCCCC; /* Серый для листинга */
}

.operation-sale,
.operation-sale.amount-positive {
  border-left-color: #00E676; /* Зеленый для продажи */
}

.operation-cancel-sale {
  border-left-color: #FF4444; /* Красный для отмены продажи */
}

/* Класс для суммы Listing - серый цвет без знака */
.amount-neutral-listing {
  color: #CCCCCC !important;
  font-weight: 600;
}

/* Контейнер для правой части операции */
.operation-right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0; /* Запрещаем сжатие */
}

/* Миниатюра NFT */
.nft-thumbnail {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  object-fit: cover;
  transition: transform 0.2s;
  flex-shrink: 0; /* Запрещаем сжатие */
}

.nft-thumbnail:hover {
  transform: scale(1.1);
}

.nft-thumbnail.image-error {
  opacity: 0.5;
  background-color: var(--surface-light);
}

/* Название NFT */
.nft-name {
  font-size: 12px;
  color: var(--accent);
  font-weight: 500;
  margin-left: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 150px;
}

/* Убедимся что сумма не сжимается */
.operation-amount {
  white-space: nowrap;
  flex-shrink: 0;
}

/* Адаптивность для мобильных */
@media (max-width: 480px) {
  .nft-thumbnail {
    width: 32px;
    height: 32px;
  }
  
  .nft-name {
    max-width: 100px;
    font-size: 10px;
  }
  
  .operation-right {
    gap: 8px;
  }
  
  .operation-amount {
    font-size: 14px; /* Чуть меньше на мобильных */
  }
}

/* Для очень маленьких экранов */
@media (max-width: 360px) {
  .operation-item {
    flex-wrap: wrap;
  }
  
  .operation-right {
    margin-top: 8px;
    width: 100%;
    justify-content: flex-end;
  }
}
.operation-amount {
  font-weight: 700;
  font-size: 16px;
  margin-left: 10px;
  white-space: nowrap;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.amount-positive {
  color: #00E676;
}

.amount-negative {
  color: #FF4444;
}

.amount-neutral {
  color: transparent;
}

/* Новый класс для Listing */
.amount-neutral-listing {
  color: #CCCCCC !important;
}
/* Специальный класс для суммы Listing - серый цвет без знака */
.amount-listing {
  color: #CCCCCC !important;
  font-weight: 600;
}

/* Зеленая граница для Listing (положительная операция по оформлению) */
.operation-listing {
  border-left-color: #00E676; /* Зеленый для листинга */
}
/* Стили для операций */
.operation-listing {
  border-left-color: #CCCCCC;
}

.operation-sale {
  border-left-color: #00E676;
}

.operation-purchase {
  border-left-color: #FF4444; /* Красный для Purchase */
}

.operation-offer {
  border-left-color: #FF4444;
}

.operation-promote {
  border-left-color: #FF4444;
}

.operation-cancel-sale {
  border-left-color: #FF4444;
}

/* Классы для сумм */
.amount-positive {
  color: #00E676;
}

.amount-negative {
  color: #FF4444;
}

.amount-neutral {
  color: transparent;
}

.amount-listing {
  color: #CCCCCC !important;
  font-weight: 600;
}

/* Контейнер для правой части операции - мобильная адаптация */
.operation-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
  margin-left: 8px;
}

/* Миниатюра NFT - адаптивный размер */
.nft-thumbnail {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  object-fit: cover;
  transition: transform 0.2s;
  flex-shrink: 0;
  background-color: var(--surface-light);
}

/* Название NFT - адаптивное */
.nft-name {
  font-size: 12px;
  color: var(--accent);
  font-weight: 500;
  margin-left: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 120px; /* Уменьшаем для мобильных */
}

/* Сумма операции - адаптивная */
.operation-amount {
  white-space: nowrap;
  flex-shrink: 0;
  font-size: 14px; /* Базовый размер для мобильных */
  font-weight: 600;
  min-width: 70px; /* Минимальная ширина для суммы */
  text-align: right;
}

/* Дата операции - адаптивная */
.operation-date {
  font-size: 11px;
  color: var(--text-secondary);
  white-space: nowrap;
}

/* Адрес кошелька - адаптивный */
.wallet-address {
  font-size: 10px;
  color: #888;
  font-family: monospace;
  margin: 2px 0;
}

/* Мобильная адаптация для разных размеров экрана */

/* Для планшетов и маленьких десктопов */
@media (max-width: 768px) {
  .nft-thumbnail {
    width: 36px;
    height: 36px;
  }
  
  .nft-name {
    max-width: 100px;
    font-size: 11px;
  }
  
  .operation-amount {
    font-size: 13px;
    min-width: 65px;
  }
}

/* Для мобильных телефонов */
@media (max-width: 480px) {
  .operation-item {
    padding: 10px 12px;
    flex-wrap: wrap; /* Позволяем перенос на маленьких экранах */
  }
  
  .operation-info {
    min-width: 0; /* Позволяем сжиматься */
    flex: 1 1 auto;
  }
  
  .nft-thumbnail {
    width: 32px;
    height: 32px;
    border-width: 1.5px;
  }
  
  .nft-name {
    max-width: 80px;
    font-size: 10px;
  }
  
  .operation-amount {
    font-size: 12px;
    min-width: 60px;
  }
  
  .operation-right {
    gap: 6px;
    margin-left: 6px;
  }
  
  .operation-type {
    font-size: 13px;
  }
  
  .operation-date {
    font-size: 10px;
  }
}

/* Для очень маленьких экранов (до 360px) */
@media (max-width: 360px) {
  .operation-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .operation-info {
    width: 100%;
  }
  
  .operation-right {
    width: 100%;
    justify-content: flex-end;
    margin-left: 0;
  }
  
  .nft-name {
    max-width: 150px; /* Больше места при вертикальном расположении */
  }
  
  .nft-thumbnail {
    width: 28px;
    height: 28px;
  }
}

/* Для экранов с высоким разрешением */
@media (min-width: 1200px) {
  .nft-thumbnail {
    width: 44px;
    height: 44px;
  }
  
  .nft-name {
    max-width: 180px;
    font-size: 13px;
  }
  
  .operation-amount {
    font-size: 15px;
    min-width: 80px;
  }
}

/* Анимация при загрузке изображения */
.nft-thumbnail.loading {
  opacity: 0.5;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% {
    opacity: 0.5;
  }
  50% {
    opacity: 0.8;
  }
  100% {
    opacity: 0.5;
  }
}

/* Стили для изображения с ошибкой */
.nft-thumbnail.error {
  opacity: 0.3;
  filter: grayscale(100%);
}

/* Улучшенная читаемость на мобильных */
.operation-type-wrapper {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
}

/* Затемнение фона для лучшей читаемости */
.operation-item {
  background-color: rgba(42, 42, 42, 0.9);
  backdrop-filter: blur(2px);
}
/* Базовые стили для operation-item */
.operation-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 18px; /* Увеличенные отступы */
  margin-bottom: 12px; /* Больше отступ между элементами */
  border-radius: 12px; /* Более скругленные углы */
  background-color: var(--surface-light);
  border-left: 6px solid; /* Более толстая граница */
  transition: all 0.2s;
  min-height: 80px; /* Минимальная высота */
}

/* Левая часть с информацией */
.operation-info {
  display: flex;
  flex-direction: column;
  gap: 6px; /* Увеличенный отступ */
  flex: 1;
}

.operation-type-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.operation-type {
  font-weight: 700; /* Более жирный */
  font-size: 16px; /* Увеличенный размер */
  color: var(--text);
}

/* Название NFT */
.nft-name {
  font-size: 14px; /* Увеличенный размер */
  color: var(--accent);
  font-weight: 600;
  margin-left: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 150px;
  background: rgba(255, 187, 0, 0.1); /* Легкий фон */
  padding: 2px 8px;
  border-radius: 12px;
}

/* Адрес кошелька */
.wallet-address {
  font-size: 12px; /* Увеличенный размер */
  color: #888;
  font-family: monospace;
  margin: 2px 0;
  background: rgba(0, 0, 0, 0.2);
  padding: 2px 6px;
  border-radius: 4px;
  display: inline-block;
  width: fit-content;
}

/* Дата операции */
.operation-date {
  font-size: 13px; /* Увеличенный размер */
  color: var(--text-secondary);
  font-weight: 500;
  background: rgba(255, 255, 255, 0.05);
  padding: 2px 8px;
  border-radius: 12px;
  display: inline-block;
  width: fit-content;
}

/* Правая часть - сумма и изображение */
.operation-right {
  display: flex;
  align-items: center;
  gap: 15px; /* Увеличенный отступ */
  flex-shrink: 0;
  margin-left: 12px;
  padding: 8px 12px;
  border-radius: 40px; /* Скругленный фон */
}

/* Сумма операции */
.operation-amount {
  white-space: nowrap;
  flex-shrink: 0;
  font-size: 16px; /* Увеличенный размер */
  font-weight: 700; /* Более жирный */
  min-width: 85px; /* Увеличенная минимальная ширина */
  text-align: right;
  letter-spacing: 0.3px; /* Немного разреженный текст */
}

/* Миниатюра NFT */
.nft-thumbnail {
  width: 48px; /* Увеличенный размер */
  height: 48px;
  border-radius: 12px; /* Более скругленные углы */
  object-fit: cover;
  transition: transform 0.2s, box-shadow 0.2s;
  flex-shrink: 0;
  background-color: var(--surface-light);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3); /* Тень для объема */
}

.nft-thumbnail:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 12px rgba(255, 187, 0, 0.3);
}

/* Мобильная адаптация */
@media (max-width: 768px) {
  .operation-item {
    padding: 18px 16px; /* Увеличенные отступы для мобильных */
    margin-bottom: 14px;
    min-height: 90px; /* Больше высота */
  }
  
  .operation-type {
    font-size: 17px; /* Крупнее на мобильных */
  }
  
  .nft-name {
    font-size: 15px;
    max-width: 130px;
    padding: 3px 10px;
  }
  
  .operation-date {
    font-size: 14px;
    padding: 3px 10px;
  }
  
  .wallet-address {
    font-size: 13px;
    padding: 3px 8px;
  }
  
  .operation-right {
    gap: 12px;
    padding: 8px 14px;
  }
  
  .operation-amount {
    font-size: 17px;
    min-width: 90px;
    font-weight: 800;
  }
  
  .nft-thumbnail {
    width: 52px; /* Еще крупнее на мобильных */
    height: 52px;
    border-width: 2.5px;
  }
}

/* Для небольших мобильных телефонов */
@media (max-width: 480px) {
  .operation-item {
    padding: 16px 14px;
    flex-direction: row; /* Оставляем в строку */
    align-items: center;
    min-height: 85px;
  }
  
  .operation-info {
    flex: 2; /* Даем больше места для информации */
  }
  
  .operation-type {
    font-size: 16px;
  }
  
  .nft-name {
    font-size: 14px;
    max-width: 110px;
    padding: 2px 8px;
  }
  
  .operation-date {
    font-size: 13px;
    padding: 2px 8px;
    background: rgba(255, 255, 255, 0.08);
  }
  
  .wallet-address {
    font-size: 12px;
    padding: 2px 6px;
  }
  
  .operation-right {
    flex: 1; /* Фиксированная ширина для правой части */
    gap: 10px;
    padding: 6px 10px;
    justify-content: flex-end;
    min-width: 140px; /* Минимальная ширина */
  }
  
  .operation-amount {
    font-size: 16px;
    min-width: 80px;
    font-weight: 700;
  }
  
  .nft-thumbnail {
    width: 48px;
    height: 48px;
  }
}

/* Для очень маленьких экранов */
@media (max-width: 380px) {
  .operation-item {
    padding: 14px 12px;
    min-height: 80px;
  }
  
  .operation-type {
    font-size: 15px;
  }
  
  .nft-name {
    font-size: 13px;
    max-width: 90px;
    padding: 2px 6px;
  }
  
  .operation-date {
    font-size: 12px;
    padding: 2px 6px;
  }
  
  .operation-right {
    gap: 8px;
    padding: 5px 8px;
    min-width: 130px;
  }
  
  .operation-amount {
    font-size: 15px;
    min-width: 75px;
  }
  
  .nft-thumbnail {
    width: 42px;
    height: 42px;
    border-width: 2px;
  }
}

/* Для планшетов */
@media (min-width: 768px) and (max-width: 1024px) {
  .operation-item {
    padding: 18px 20px;
  }
  
  .nft-thumbnail {
    width: 50px;
    height: 50px;
  }
  
  .operation-amount {
    font-size: 18px;
    min-width: 95px;
  }
}

/* Цвета границ для разных типов операций */
.operation-listing {
  border-left-color: #CCCCCC;
}

.operation-sale {
  border-left-color: #00E676;
}

.operation-purchase {
  border-left-color: #FF4444;
}

.operation-offer {
  border-left-color: #FF4444;
}

.operation-promote {
  border-left-color: #FF4444;
}

.operation-cancel-sale {
  border-left-color: #FF4444;
}

.operation-topup {
  border-left-color: #00E676;
}

.operation-withdraw {
  border-left-color: #FF4444;
}

.operation-wallet-connect {
  border-left-color: #00E676;
}

.operation-wallet-disconnect {
  border-left-color: #FF4444;
}

/* Цвета сумм */
.amount-positive {
  color: #00E676;
  text-shadow: 0 0 5px rgba(0, 230, 118, 0.1); /* Легкое свечение */
}

.amount-negative {
  color: #FF4444;
  text-shadow: 0 0 5px rgba(255, 68, 68, 0.1);
}

.amount-neutral {
  color: transparent;
}

.amount-listing {
  color: #CCCCCC !important;
  font-weight: 700;
  text-shadow: 0 0 5px rgba(255, 255, 255, 0.1);
}

/* Иконка party popper */
.party-popper-icon-amount {
  width: 32px;
  height: 32px;
  object-fit: contain;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}

/* Стили для пустой истории */
.empty-history {
  text-align: center;
  padding: 50px 20px;
  color: var(--text-secondary);
  font-style: italic;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  background: var(--surface-light);
  border-radius: 12px;
  margin: 10px 0;
}

/* Стили для загрузки */
.loading-more {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 20px;
  color: var(--text-secondary);
  font-size: 14px;
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 3px solid var(--surface-light);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Конец списка */
.end-of-list {
  text-align: center;
  padding: 20px;
  color: var(--text-secondary);
  font-size: 14px;
  position: relative;
}

.end-of-list::before,
.end-of-list::after {
  content: '';
  position: absolute;
  top: 50%;
  width: 30%;
  height: 1px;
  background: var(--border);
}

.end-of-list::before {
  left: 0;
}

.end-of-list::after {
  right: 0;
}
/* Зеленые операции (положительные) */
.operation-topup {
  border-left-color: #00E676;
}

.operation-sale {
  border-left-color: #00E676;
}

.operation-refund {
  border-left-color: #00E676; /* Зеленый для Refund */
}

/* Красные операции (отрицательные) */
.operation-withdraw {
  border-left-color: #FF4444;
}

.operation-offer {
  border-left-color: #FF4444;
}

.operation-purchase {
  border-left-color: #FF4444;
}

.operation-promote {
  border-left-color: #FF4444;
}

.operation-cancel-sale {
  border-left-color: #FF4444;
}

.operation-price-edit {
  border-left-color: #FF4444;
}

/* Нейтральные операции */
.operation-listing {
  border-left-color: #CCCCCC;
}

.operation-wallet-connect {
  border-left-color: #00E676;
}

.operation-wallet-disconnect {
  border-left-color: #FF4444;
}
/* Стили для операций с NFT */
.operation-listing {
  border-left-color: #00E676; /* Красный для листинга */
}
/* Стили для Transfer операции */
.operation-transfer {
  border-left-color: #FFBB00 !important; /* Желтый цвет */
}

/* Сумма для Transfer */
.amount-transfer {
  color: #FFBB00 !important;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  text-shadow: 0 0 5px rgba(255, 187, 0, 0.3);
  display: flex;
  align-items: center;
  gap: 4px;
}

.amount-transfer:hover {
  transform: scale(1.05);
  text-shadow: 0 0 8px rgba(255, 187, 0, 0.5);
}

/* Информация о получателе */
.recipient-info {
  display: flex;
  align-items: center;
  gap: 4px;
  margin: 4px 0;
  padding: 4px 8px;
  background: rgba(255, 187, 0, 0.1);
  border-radius: 16px;
  width: fit-content;
  cursor: pointer;
  transition: all 0.2s;
}

.recipient-info:hover {
  background: rgba(255, 187, 0, 0.2);
  border-color: rgba(255, 187, 0, 0.4);
}

.recipient-label {
  font-size: 12px;
  color: #FFBB00;
  font-weight: 500;
  opacity: 0.8;
}

.recipient-username {
  font-size: 14px;
  color: #FFBB00;
  font-weight: 600;
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.recipient-username.expanded {
  white-space: normal;
  word-break: break-all;
}

.expand-hint {
  font-size: 12px;
  color: #FFBB00;
  opacity: 0.7;
  margin-left: 2px;
}

/* Мобильная адаптация для Transfer */
@media (max-width: 480px) {
  .recipient-info {
    padding: 3px 6px;
  }
  
  .recipient-label {
    font-size: 11px;
  }
  
  .recipient-username {
    font-size: 13px;
    max-width: 120px;
  }
  
  .amount-transfer {
    font-size: 15px;
  }
  
  .expand-hint {
    font-size: 10px;
  }
}

@media (max-width: 360px) {
  .recipient-username {
    max-width: 90px;
  }
  
  .amount-transfer {
    font-size: 14px;
  }
}
/* Стили для offer операций */
.operation-offer-sale {
  border-left-color: #00E676; /* Зеленый для продажи */
}

.operation-offer-purchase {
  border-left-color: #FF4444; /* Красный для покупки */
}

/* Информация об участниках */
.participant-info {
  display: flex;
  align-items: center;
  gap: 4px;
  margin: 4px 0;
  padding: 2px 8px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  width: fit-content;
}

.participant-label {
  font-size: 11px;
  color: var(--text-secondary);
  font-weight: 500;
}

.participant-username {
  font-size: 12px;
  color: var(--accent);
  font-weight: 600;
}

/* Информация о комиссии */
.commission-info {
  display: flex;
  align-items: center;
  gap: 4px;
  margin: 2px 0 4px 0;
  padding: 2px 8px;
  background: rgba(255, 187, 0, 0.1);
  border-radius: 12px;
  width: fit-content;
  font-size: 11px;
}

.commission-label {
  color: #FFBB00;
  opacity: 0.8;
}

.commission-amount {
  color: #FFBB00;
  font-weight: 600;
}

/* Мобильная адаптация */
@media (max-width: 480px) {
  .participant-info {
    padding: 2px 6px;
  }
  
  .participant-label {
    font-size: 10px;
  }
  
  .participant-username {
    font-size: 11px;
  }
  
  .commission-info {
    font-size: 10px;
    padding: 2px 6px;
  }
}
.operation-offer-sale {
  border-left-color: #00E676; /* Зеленый для продажи */
}

.operation-offer-purchase {
  border-left-color: #FF4444; /* Красный для покупки */
}
/* Полосатый левый бордер в стиле барбершоп для gift_received */
.operation-gift-received {
  border-left: none !important; /* Убираем обычный бордер */
  position: relative;
  overflow: hidden;
}

.operation-gift-received::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 6px; /* Ширина полосатой области */
  background: repeating-linear-gradient(
    45deg, /* Угол наклона 45 градусов */
    #FF4444, /* Красный */
    #FF4444 8px, /* Ширина красной полосы */
    #FFBB00 8px, /* Желтый */
    #FFBB00 16px /* Ширина желтой полосы */
  );
  pointer-events: none; /* Чтобы полоса не мешала кликам */
  z-index: 1;
}

/* Адаптация для мобильных устройств */
@media (max-width: 768px) {
  .operation-gift-received::before {
    width: 6px; /* Та же ширина */
    background: repeating-linear-gradient(
      45deg,
      #FF4444,
      #FF4444 8px,
      #FFBB00 8px,
      #FFBB00 16px
    );
  }
}

/* Для очень маленьких экранов можно сделать полосы чуть уже */
@media (max-width: 480px) {
  .operation-gift-received::before {
    background: repeating-linear-gradient(
      45deg,
      #FF4444,
      #FF4444 6px,
      #FFBB00 6px,
      #FFBB00 12px
    );
  }
}
/* ТОЛЬКО ЛЕВЫЙ ПОЛОСАТЫЙ BORDER, БОЛЬШЕ НИЧЕГО */
.operation-gift {
  border-left: 6px solid transparent !important;
  border-image: repeating-linear-gradient(
    135deg,
    #FF4444,
    #FF4444 6px,
    #FFBB00 6px,
    #FFBB00 12px
  );
  border-image-slice: 1;
}

/* Адаптация для мобильных */
@media (max-width: 480px) {
  .operation-gift {
    border-left-width: 4px;
  }
}
/* ПОЛОСАТЫЙ ЛЕВЫЙ БОРДЕР ДЛЯ ВСЕХ GIFT-ОПЕРАЦИЙ */
.operation-gift {
  border-left: none !important; /* Убираем стандартный бордер */
  position: relative;
  overflow: hidden;
}

/* Полосатый левый бордер через псевдоэлемент */
.operation-gift::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 6px; /* Ширина полосатой области */
  background: repeating-linear-gradient(
    45deg, /* Угол наклона 45 градусов */
    #FF4444, /* Красный */
    #FF4444 8px, /* Ширина красной полосы */
    #FFBB00 8px, /* Желтый */
    #FFBB00 16px /* Ширина желтой полосы */
  );
  pointer-events: none; /* Чтобы полоса не мешала кликам */
  z-index: 1;
}

/* Адаптация для мобильных устройств */
@media (max-width: 768px) {
  .operation-gift::before {
    width: 6px;
    background: repeating-linear-gradient(
      45deg,
      #FF4444,
      #FF4444 8px,
      #FFBB00 8px,
      #FFBB00 16px
    );
  }
}

/* Для очень маленьких экранов */
@media (max-width: 480px) {
  .operation-gift::before {
    width: 6px;
    background: repeating-linear-gradient(
      45deg,
      #FF4444,
      #FF4444 6px,
      #FFBB00 6px,
      #FFBB00 12px
    );
  }
}
/* Общие стили для overlay (затемнение) */
.balance-popup-overlay,
.modal-overlay {
  backdrop-filter: blur(8px);
  background-color: rgba(0, 0, 0, 0.7);
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* ===== BALANCE POPUP ===== */
.balance-popup {
  background: linear-gradient(145deg, #1e1e1e 0%, #2d2d2d 100%);
  border-radius: 32px;
  padding: 24px;
  max-width: 340px;
  width: 90%;
  border: 1px solid rgba(255, 187, 0, 0.2);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 187, 0, 0.1) inset;
  animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.balance-popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.balance-popup-header h3 {
  font-size: 20px;
  font-weight: 700;
  color: #ffffff;
  margin: 0;
  letter-spacing: -0.3px;
}

.balance-popup-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.balance-action-btn {
  padding: 16px 20px;
  border: none;
  border-radius: 20px;
  font-weight: 600;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  text-align: center;
  position: relative;
  overflow: hidden;
}

.balance-action-btn::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 5px;
  height: 5px;
  background: rgba(255, 255, 255, 0.5);
  opacity: 0;
  border-radius: 100%;
  transform: scale(1, 1) translate(-50%);
  transform-origin: 50% 50%;
}

.balance-action-btn:active::after {
  animation: ripple 0.6s ease-out;
}

@keyframes ripple {
  0% {
    transform: scale(0, 0);
    opacity: 0.5;
  }
  100% {
    transform: scale(20, 20);
    opacity: 0;
  }
}

.balance-action-btn.top-up {
  background: linear-gradient(135deg, #ffbb00 0%, #ffd966 100%);
  color: #1a1a1a;
  box-shadow: 0 8px 20px -8px rgba(255, 187, 0, 0.5);
}

.balance-action-btn.top-up:hover:not(.disabled-action-btn) {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px -8px rgba(255, 187, 0, 0.7);
}

.balance-action-btn.withdraw {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #ffffff;
}

.balance-action-btn.withdraw:hover:not(.disabled-action-btn) {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 187, 0, 0.3);
}

.balance-action-btn.history {
  background: rgba(255, 255, 255, 0.03);
  border: 1px dashed rgba(255, 255, 255, 0.2);
  color: #ffffff;
}

.balance-action-btn.history:hover:not(.disabled-action-btn) {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 187, 0, 0.4);
  color: #ffffff;
}

.disabled-action-btn {
  opacity: 0.4;
  cursor: not-allowed;
  filter: grayscale(0.5);
  pointer-events: none;
}

.wallet-notice {
  margin-top: 16px;
  padding: 12px;
  background: rgba(255, 187, 0, 0.1);
  border-radius: 16px;
  text-align: center;
  font-size: 13px;
  color: #ffffff;
  border: 1px solid rgba(255, 187, 0, 0.2);
  backdrop-filter: blur(4px);
}

/* ===== OPERATIONS HISTORY MODAL ===== */
.operations-history-modal.modal {
  background: linear-gradient(145deg, #1a1a1a 0%, #252525 100%);
  border-radius: 40px;
  padding: 24px 20px;
  max-width: 500px;
  width: 95%;
  border: 1px solid rgba(255, 255, 255, 0.05);
  box-shadow: 0 30px 60px -15px rgba(0, 0, 0, 0.8), 0 0 0 1px rgba(255, 187, 0, 0.1) inset;
  animation: scaleIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.operations-history-modal .modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 0 8px 12px 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.operations-history-modal .modal-header h3 {
  font-size: 24px;
  font-weight: 700;
  color: #ffffff;
  margin: 0;
  letter-spacing: -0.5px;
}

.operations-history-modal .close-btn {
  width: 40px;
  height: 40px;
  border-radius: 30px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #ffffff;
  font-size: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  padding: 0;
  line-height: 1;
}

.operations-history-modal .close-btn:hover {
  background: rgba(255, 187, 0, 0.15);
  border-color: rgba(255, 187, 0, 0.3);
  transform: rotate(90deg);
  color: #ffbb00;
}

.operations-history-modal .modal-body {
  max-height: 60vh;
  overflow-y: auto;
  padding: 4px 8px 0 8px;
  margin-bottom: 16px;
  scrollbar-width: thin;
  scrollbar-color: transparent transparent;
}

.operations-history-modal .modal-body::-webkit-scrollbar {
  width: 6px;
}

.operations-history-modal .modal-body::-webkit-scrollbar-track {
  background: transparent;
  border-radius: 20px;
}

.operations-history-modal .modal-body::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.operations-history-modal .modal-body::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

.operations-history-modal .modal-footer {
  display: flex;
  justify-content: flex-end;
  padding: 12px 8px 4px 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.operations-history-modal .btn-secondary {
  padding: 14px 32px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 40px;
  color: #ffffff;
  font-weight: 600;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s;
  letter-spacing: 0.3px;
  backdrop-filter: blur(4px);
}

.operations-history-modal .btn-secondary:hover {
  background: rgba(255, 187, 0, 0.15);
  border-color: rgba(255, 187, 0, 0.4);
  transform: scale(1.02);
  color: #ffffff;
}

/* Стили для пустой истории */
.empty-history {
  text-align: center;
  padding: 60px 20px;
  color: rgba(255, 255, 255, 0.4);
  font-style: italic;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 28px;
  margin: 10px 0;
  border: 1px dashed rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(4px);
}

/* Загрузка и конец списка */
.loading-more {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 24px;
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 3px solid rgba(255, 187, 0, 0.2);
  border-top-color: #ffbb00;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.end-of-list {
  text-align: center;
  padding: 24px;
  color: rgba(255, 255, 255, 0.3);
  font-size: 14px;
  position: relative;
}

.end-of-list::before,
.end-of-list::after {
  content: '';
  position: absolute;
  top: 50%;
  width: 30%;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 187, 0, 0.3), transparent);
}

.end-of-list::before { left: 0; }
.end-of-list::after { right: 0; }

/* Анимации */
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Адаптация для мобильных */
@media (max-width: 480px) {
  .balance-popup {
    padding: 20px;
    border-radius: 28px;
  }

  .balance-popup-header h3 {
    font-size: 18px;
  }

  .balance-action-btn {
    padding: 14px 16px;
    font-size: 15px;
    border-radius: 18px;
  }

  .operations-history-modal.modal {
    padding: 20px 16px;
    border-radius: 32px;
  }

  .operations-history-modal .modal-header h3 {
    font-size: 22px;
  }

  .operations-history-modal .btn-secondary {
    padding: 12px 28px;
    font-size: 15px;
  }

  .empty-history {
    padding: 40px 16px;
    font-size: 15px;
  }
}
/* Стили для модалок (общие для top-up и withdraw) */
.modal:not(.operations-history-modal) {
  background: linear-gradient(145deg, #1a1a1a 0%, #252525 100%);
  border-radius: 40px;
  padding: 24px 20px;
  max-width: 400px;
  width: 90%;
  border: 1px solid rgba(255, 255, 255, 0.05);
  box-shadow: 0 30px 60px -15px rgba(0, 0, 0, 0.8), 0 0 0 1px rgba(255, 187, 0, 0.1) inset;
  animation: scaleIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

/* Заголовок модалки */
.modal:not(.operations-history-modal) .modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 0 4px 16px 4px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.modal:not(.operations-history-modal) .modal-header h3 {
  font-size: 24px;
  font-weight: 700;
  color: #ffffff;
  margin: 0;
  letter-spacing: -0.5px;
}

/* Кнопка закрытия */
.modal:not(.operations-history-modal) .close-btn {
  width: 40px;
  height: 40px;
  border-radius: 30px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #ffffff;
  font-size: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  padding: 0;
  line-height: 1;
}

.modal:not(.operations-history-modal) .close-btn:hover {
  background: rgba(255, 187, 0, 0.15);
  border-color: rgba(255, 187, 0, 0.3);
  transform: rotate(90deg);
  color: #ffbb00;
}

/* Тело модалки */
.modal:not(.operations-history-modal) .modal-body {
  padding: 0 4px;
  margin-bottom: 24px;
}

/* Группа инпутов */
.modal:not(.operations-history-modal) .input-group {
  margin-bottom: 20px;
}

.modal:not(.operations-history-modal) .input-group label {
  display: block;
  margin-bottom: 10px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 15px;
  font-weight: 500;
  letter-spacing: 0.3px;
}

/* Поле ввода */
.modal:not(.operations-history-modal) .amount-input {
  width: 100%;
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  color: #ffffff;
  font-size: 18px;
  font-weight: 500;
  transition: all 0.2s;
  box-sizing: border-box;
}

.modal:not(.operations-history-modal) .amount-input:focus {
  outline: none;
  border-color: rgba(255, 187, 0, 0.5);
  background: rgba(255, 255, 255, 0.08);
  box-shadow: 0 0 0 3px rgba(255, 187, 0, 0.1);
}

.modal:not(.operations-history-modal) .amount-input::placeholder {
  color: rgba(255, 255, 255, 0.3);
}

.modal:not(.operations-history-modal) .amount-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Быстрые суммы */
.modal:not(.operations-history-modal) .quick-amounts {
  display: flex;
  gap: 10px;
  margin: 20px 0;
  flex-wrap: wrap;
}

.modal:not(.operations-history-modal) .quick-amounts button {
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 30px;
  color: #ffffff;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  flex: 1 1 auto;
  min-width: 70px;
}

.modal:not(.operations-history-modal) .quick-amounts button:hover:not(:disabled) {
  background: rgba(255, 187, 0, 0.15);
  border-color: rgba(255, 187, 0, 0.4);
  transform: translateY(-2px);
}

.modal:not(.operations-history-modal) .quick-amounts button:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

/* Информация о сумме */
.modal:not(.operations-history-modal) .total-info {
  font-size: 18px;
  font-weight: 700;
  color: #ffffff;
  margin: 16px 0;
  padding: 16px;
  background: rgba(255, 187, 0, 0.1);
  border-radius: 24px;
  text-align: center;
  border: 1px solid rgba(255, 187, 0, 0.2);
  backdrop-filter: blur(4px);
}

/* Предупреждение о подключении кошелька */
.modal:not(.operations-history-modal) .wallet-required-notice {
  margin-top: 16px;
  padding: 14px;
  background: rgba(255, 68, 68, 0.1);
  border-radius: 20px;
  text-align: center;
  font-size: 14px;
  color: #ffffff;
  border: 1px solid rgba(255, 68, 68, 0.3);
  backdrop-filter: blur(4px);
}

/* Футер модалки */
.modal:not(.operations-history-modal) .modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 4px 4px 4px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

/* Кнопки в футере */
.modal:not(.operations-history-modal) .btn-secondary {
  padding: 14px 28px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 40px;
  color: #ffffff;
  font-weight: 600;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s;
  letter-spacing: 0.3px;
  backdrop-filter: blur(4px);
  flex: 1;
}

.modal:not(.operations-history-modal) .btn-secondary:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
  transform: scale(1.02);
}

.modal:not(.operations-history-modal) .btn-primary {
  padding: 14px 28px;
  background: linear-gradient(135deg, #ffbb00 0%, #ffd966 100%);
  border: none;
  border-radius: 40px;
  color: #1a1a1a;
  font-weight: 700;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s;
  letter-spacing: 0.3px;
  box-shadow: 0 8px 20px -8px rgba(255, 187, 0, 0.5);
  flex: 1;
}

.modal:not(.operations-history-modal) .btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px -8px rgba(255, 187, 0, 0.7);
}

.modal:not(.operations-history-modal) .btn-primary:disabled,
.modal:not(.operations-history-modal) .btn-primary.disabled-primary-btn {
  opacity: 0.4;
  cursor: not-allowed;
  filter: grayscale(0.5);
  transform: none;
  box-shadow: none;
}

/* Специфичные стили для withdraw модалки */
.modal:not(.operations-history-modal) .withdraw .total-info {
  background: rgba(255, 68, 68, 0.1);
  border-color: rgba(255, 68, 68, 0.2);
}

/* Адаптация для мобильных */
@media (max-width: 480px) {
  .modal:not(.operations-history-modal) {
    padding: 20px 16px;
    border-radius: 32px;
  }

  .modal:not(.operations-history-modal) .modal-header h3 {
    font-size: 22px;
  }

  .modal:not(.operations-history-modal) .amount-input {
    padding: 14px 18px;
    font-size: 16px;
    border-radius: 20px;
  }

  .modal:not(.operations-history-modal) .quick-amounts button {
    padding: 10px 16px;
    font-size: 14px;
  }

  .modal:not(.operations-history-modal) .total-info {
    font-size: 16px;
    padding: 14px;
  }

  .modal:not(.operations-history-modal) .btn-secondary,
  .modal:not(.operations-history-modal) .btn-primary {
    padding: 12px 24px;
    font-size: 15px;
  }
}

@media (max-width: 360px) {
  .modal:not(.operations-history-modal) .quick-amounts {
    gap: 6px;
  }

  .modal:not(.operations-history-modal) .quick-amounts button {
    padding: 8px 12px;
    font-size: 13px;
    min-width: 60px;
  }
}

/* Анимация для модалок */
@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
/* Стили для операции Bonus */
.operation-bonus {
  border-left-color: #00E676; /* Зеленый как у topup/sale */
}

.operation-bonus .operation-type {
  color: #00E676;
  font-weight: 700;
}
.balance-container-wrapper {
  position: relative;
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.withdraw-notification {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  color: #ff4444;
  font-weight: bold;
  font-size: 18px;
  text-shadow: 0 0 2px rgba(0, 0, 0, 0.5);
  white-space: nowrap;
  pointer-events: none;
  z-index: 10;
  margin-top: 5px;
}
.balance-container-wrapper {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.withdraw-notification {
  position: absolute;
  left: 100%;
  top: 50%;
  transform: translateY(-50%);
  color: #ff4444;
  font-weight: bold;
  font-size: 18px;
  text-shadow: 0 0 2px rgba(0, 0, 0, 0.5);
  white-space: nowrap;
  pointer-events: none;
  z-index: 10;
  margin-left: 10px;
}

/* Анимация выезда справа */
.withdraw-animation-enter-active,
.withdraw-animation-leave-active {
  transition: all 0.3s ease;
}

.withdraw-animation-enter-from {
  opacity: 0;
  transform: translateY(-50%) translateX(-10px);
}

.withdraw-animation-enter-to {
  opacity: 1;
  transform: translateY(-50%) translateX(0);
}

.withdraw-animation-leave-to {
  opacity: 0;
  transform: translateY(-50%) translateX(-10px);
}
/* Стили для операции Referal */
.operation-referal {
  border-left-color: #00E676; /* Зеленый как у topup */
}

.operation-referal .operation-type {
  color: #00E676;
  font-weight: 700;
}

/* Для суммы referal - ярко-зеленый */
.operation-referal .amount-positive {
  color: #00E676;
  text-shadow: 0 0 5px rgba(0, 230, 118, 0.2);
} 
/* ... остальные стили без изменений ... */
</style>