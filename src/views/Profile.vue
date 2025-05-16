<template>
  <div class="app dark-theme" style="overflow-x: hidden;">
    <!-- Шапка -->
    <header class="header">
      <div class="logo"></div>
      <div class="balance-container" v-if="tonConnectUI?.connected" @click="toggleBalancePopup">
        <span class="balance">{{ currentAccount.ton_balance }}</span>
        <img class="balance-icon" :src="TON" alt="TON" />
      </div>
    
      <div id="ton-connect"></div>
      <div class="header-actions" style="padding-right: 10px">
        <button class="logout-btn" @click="logout">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
            <polyline points="16 17 21 12 16 7"></polyline>
            <line x1="21" y1="12" x2="9" y2="12"></line>
          </svg>
        </button>
      </div>
    </header>

    <!-- Основной контент -->
    <main class="content">
      <!-- Профиль -->
      <section class="profile">
        <div class="profile-card">
          <img :src="amahaslaImage" alt="Profile" class="avatar" />
          <h2 class="username">{{ currentAccount.name }}</h2>
          <div class="score">
            <span>{{ scoreStore.score }}</span>
            <img :src="frogIcon" alt="Score" class="frog-icon" />
          </div>
          
          <!-- Быстрое пополнение -->
          <div class="quick-topup">
            <button @click="showTopUpModal = true">+1 TON</button>
            <button @click="showTopUpModal = true">+5 TON</button>
            <button @click="showTopUpModal = true">+10 TON</button>
          </div>
        </div>

        <!-- NFT Коллекция -->
        <div class="nft-section">
          <h3 class="nft-title">NFT коллекция</h3>
          <div class="nft-grid">
            <div v-for="(hasNft, index) in nftList" :key="index" class="nft-item">
              <div :class="['nft-badge', hasNft ? 'active' : 'inactive']">
                {{ hasNft ? index + 1 : '—' }}
              </div>
            </div>
          </div>
          <button class="nft-btn" @click="navigateToNFT">Мои NFT</button>
        </div>
      </section>
    </main>

    <!-- Модальное окно пополнения баланса -->
    <div v-if="showTopUpModal" class="modal-overlay" @click.self="showTopUpModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>Пополнение баланса</h3>
          <button class="close-btn" @click="showTopUpModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <div class="input-group">
            <label>Сумма (TON)</label>
            <input 
              type="number" 
              v-model="topUpAmount" 
              class="amount-input" 
              min="0.1" 
              max="10" 
              step="0.1"
              placeholder="Введите сумму от 0.1 до 10 TON"
            >
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showTopUpModal = false">Отмена</button>
          <button class="btn-primary" @click="confirmTopUp">Пополнить</button>
        </div>
      </div>
    </div>

    <!-- Попап управления балансом -->
    <div v-if="showBalancePopup" class="balance-popup-overlay" @click.self="showBalancePopup = false">
      <div class="balance-popup">
        <div class="balance-popup-header">
          <h3>Ваш баланс: {{ currentAccount.ton_balance }} TON</h3>
          <button class="close-btn" @click="showBalancePopup = false">&times;</button>
        </div>
        <div class="balance-popup-body">
          <button class="balance-action-btn top-up" @click="showTopUpModal = true; showBalancePopup = false">
            Пополнить баланс
          </button>
          <button class="balance-action-btn withdraw" @click="showWithdrawModal = true; showBalancePopup = false">
            Вывести средства
          </button>
        </div>
      </div>
    </div>

    <!-- Модальное окно вывода средств -->
<!-- Модальное окно вывода средств -->
<div v-if="showWithdrawModal" class="modal-overlay" @click.self="showWithdrawModal = false">
    <div class="modal">
      <div class="modal-header">
        <h3>Вывод средств</h3>
        <button class="close-btn" @click="showWithdrawModal = false">&times;</button>
      </div>
      <div class="modal-body">
        <div class="input-group">
          <label>Сумма (TON)</label>
          <input 
            type="number" 
            v-model="withdrawAmount" 
            class="amount-input" 
            min="0.1" 
            :max="currentAccount.ton_balance"
            step="0.1"
            :placeholder="`Доступно: ${currentAccount.ton_balance} TON`"
            @input="validateWithdrawAmount"
          >
        </div>
        <div class="quick-amounts">
          <button @click="withdrawAmount = 1">1 TON</button>
          <button @click="withdrawAmount = 5">5 TON</button>
          <button @click="withdrawAmount = 10">10 TON</button>
          <button @click="withdrawAmount = currentAccount.ton_balance">Всё</button>
        </div>
        <div class="fee-info">
          Комиссия сети: ~0.1 TON (списывается дополнительно)
        </div>
        <div class="total-info">
          Итого получите: {{ (withdrawAmount - 0.1).toFixed(2) }} TON
        </div>
        <div class="wallet-info">
          Средства поступят на: {{ shortAddress(tonConnectUI.account?.address) }}
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn-secondary" @click="showWithdrawModal = false">Отмена</button>
        <button 
          class="btn-primary" 
          @click="confirmWithdraw" 
          :disabled="!isWithdrawValid"
        >
          Вывести
        </button>
      </div>
    </div>
  </div>
    </div>

</template>

<script setup>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import amahaslaImage from '@/assets/amahasla.png'
import frogIcon from '@/assets/frog1.png'
import { useScoreStore } from '@/stores/score'
import supabase from '../../services/supabase'
import { useRouter } from 'vue-router'
import TON from '@/assets/TON.jpg'
import axios from 'axios'; // <-- Добавьте эту строку!

const ADMIN_WALLET = "UQCm6we41JB5_a-bz581Yarp2WUc7btjWozHr-j9UaRgO_Sf"; 
const RECIPIENT_ADDRESS = "kQABGvyK4O3Y4JQkzjgHVQPU_-c-FC1uZqW_KiZC3Bx0KnHK";
const props = defineProps({
  tonConnectUI: Object
})

const router = useRouter()
const scoreStore = useScoreStore()
const currentAccount = ref({
  name: '',
  score: 0,
  nft1: null,
  nft2: null,
  nft3: null,
  nft4: null,
  nft5: null,
  nft6: null,
  nft7: null,
  nft8: null,
  nft9: null,
  nft10: null,
  telegram: ''
})

const showTopUpModal = ref(false)
const showBalancePopup = ref(false)
const showWithdrawModal = ref(false)
const topUpAmount = ref(1)
const withdrawAmount = ref(0)
const balance = ref(0)
const isLoading = ref(false)

const nftList = computed(() => {
  return [
    currentAccount.value.nft1,
    currentAccount.value.nft2,
    currentAccount.value.nft3,
    currentAccount.value.nft4,
    currentAccount.value.nft5,
    currentAccount.value.nft6,
    currentAccount.value.nft7,
    currentAccount.value.nft8,
    currentAccount.value.nft9,
    currentAccount.value.nft10
  ].map(nft => nft !== null && nft !== undefined)
})

const toggleBalancePopup = () => {
  showBalancePopup.value = !showBalancePopup.value
}
// В секции script setup
const shortAddress = (address) => {
  if (!address) return 'не указан';
  return `${address.slice(0, 6)}...${address.slice(-4)}`;
};

const validateWithdrawAmount = () => {
  if (withdrawAmount.value > currentAccount.value.ton_balance) {
    withdrawAmount.value = currentAccount.value.ton_balance;
  }
  if (withdrawAmount.value < 0.1) {
    withdrawAmount.value = 0.1;
  }
};

const isWithdrawValid = computed(() => {
  return withdrawAmount.value >= 0.1 && 
         withdrawAmount.value <= currentAccount.value.ton_balance &&
         props.tonConnectUI?.connected;
});

const confirmWithdraw = async () => {
  if (!isWithdrawValid.value) return;
  
  try {
    isLoading.value = true;
    
    // Отправляем запрос на сервер для выполнения транзакции
    const response = await axios.post('http://localhost:3000/withdraw', {
      recipientAddress: props.tonConnectUI.account?.address,
      amount: (withdrawAmount.value - 0.1).toFixed(2)
    });

    // Обновляем баланс в базе данных
    await supabase
      .from('users')
      .update({ ton_balance: currentAccount.value.ton_balance - withdrawAmount.value })
      .eq('id', currentAccount.value.id);

    currentAccount.value.ton_balance -= withdrawAmount.value;
    showWithdrawModal.value = false;
    alert(`✅ ${withdrawAmount.value} TON успешно выведены!`);
    
  } catch (error) {
    console.error('Withdraw failed:', error);
    alert(`❌ Ошибка: ${error.response?.data?.error || 'Сервер недоступен'}`);
  } finally {
    isLoading.value = false;
  }
};

const updateTonBalance = async (amount) => {
  try {
    // Получаем текущий баланс
    const { data: userData, error } = await supabase
      .from('users')
      .select('ton_balance')
      .eq('name', currentAccount.value.name)
      .single()

    if (error) throw error

    // Вычисляем новый баланс
    const newBalance = (parseFloat(userData.ton_balance) || 0) + parseFloat(amount)
    
    // Обновляем в базе
    const { error: updateError } = await supabase
      .from('users')
      .update({ ton_balance: newBalance })
      .eq('name', currentAccount.value.name)

    if (updateError) throw updateError

    // Обновляем локальное состояние
    currentAccount.value.ton_balance = newBalance
    balance.value = newBalance.toFixed(2)

  } catch (error) {
    console.error('Error updating TON balance:', error)
    throw error
  }
}

const topUpBalance = async (amount) => {
  if (!props.tonConnectUI?.connected) {
    alert('Сначала подключите кошелек')
    return
  }

  isLoading.value = true
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

    const result = await props.tonConnectUI.sendTransaction(transaction)
    
    if (result?.boc) {
      // Обновляем баланс TON в базе данных
      await updateTonBalance(amount)
      
      // Дополнительная проверка реального баланса
      await fetchBalance()
      
      showTopUpModal.value = false
      alert(`Баланс успешно пополнен на ${amount} TON!`)
    }
  } catch (error) {
    console.error('Transaction error:', error)
    if (!error.message.includes('Rejected by user')) {
      alert(`Ошибка: ${error.message}`)
    }
  } finally {
    isLoading.value = false
  }
}

// Функция вывода средств
// В секции script setup добавьте:
const withdrawTon = async (amount) => {
  if (!props.tonConnectUI?.connected) {
    alert('Сначала подключите кошелек');
    return;
  }

  isLoading.value = true;

  try {
    // Проверяем, достаточно ли TON у пользователя (в его игровом балансе)
    if (amount > currentAccount.value.ton_balance) {
      throw new Error("Недостаточно средств на игровом балансе");
    }

    // 1. Создаем транзакцию для вывода с вашего кошелька на кошелек пользователя
    const transaction = {
      validUntil: Math.floor(Date.now() / 1000) + 300, // 5 минут на подтверждение
      messages: [
        {
          address: props.tonConnectUI.account.address, // Кошелек пользователя (куда отправляем)
          amount: String(Math.floor(amount * 1000000000)), // Конвертируем в наноTON (1 TON = 10^9 наноTON)
        }
      ],
      // Опционально: можно указать, что транзакция должна быть отправлена с вашего кошелька
      // (но это требует настройки TonConnect для мультикошельковости)
    };

    // 2. Отправляем транзакцию через TonConnect
    // (здесь TonConnect подписывает транзакцию, но деньги списываются с вашего кошелька)
    const result = await props.tonConnectUI.sendTransaction(transaction);

    if (result?.boc) {
      // 3. Если транзакция успешна, списываем сумму с баланса пользователя в вашей БД
      await supabase
        .from('users')
        .update({ ton_balance: currentAccount.value.ton_balance - amount })
        .eq('id', currentAccount.value.id);

      // 4. Обновляем локальный баланс
      currentAccount.value.ton_balance -= amount;

      alert(`✅ Успешно! ${amount} TON отправлены на ваш кошелек.`);
      showWithdrawModal.value = false;
    }
  } catch (error) {
    console.error('Ошибка вывода:', error);
    if (!error.message.includes('Rejected by user')) {
      alert(`❌ Ошибка: ${error.message}`);
    }
  } finally {
    isLoading.value = false;
  }
};




const fetchBalance = async () => {
  // Баланс TON из кошелька
  if (props.tonConnectUI?.connected) {
    try {
      const account = props.tonConnectUI.account || 
                    props.tonConnectUI.walletConnectionSource?.account
      
      if (account?.balance) {
        const walletBalance = (Number(account.balance) / 1000000000).toFixed(2)
        // Можно использовать для проверки, но основной баланс берем из БД
      }
    } catch (error) {
      console.error('Wallet balance error:', error)
    }
  }

  // Баланс TON из базы данных (основной источник)
  try {
    const { data: userData, error } = await supabase
      .from('users')
      .select('ton_balance')
      .eq('name', currentAccount.value.name)
      .single()

    if (!error && userData) {
      balance.value = userData.ton_balance
      currentAccount.value.ton_balance = userData.ton_balance
    }
  } catch (error) {
    console.error('Database balance error:', error)
  }
}

const confirmTopUp = () => {
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


const loadUserData = async () => {
  try {
    const savedAccount = localStorage.getItem('currentAccount')
    const savedLoginState = localStorage.getItem('isLoggedIn')
    
    if (!savedAccount || savedLoginState !== 'true') {
      console.error('Пользователь не авторизован')
      return
    }

    const account = JSON.parse(savedAccount)
    const { data: userData, error } = await supabase
      .from('users')
      .select('*')
      .eq('name', account.name)
      .single()

    if (error) throw error
    if (!userData) {
      await logout()
      return
    }

    // Обновляем все данные, включая ton_balance
    scoreStore.setCurrentAccount({
      name: userData.name,
      score: userData.score || 0,
      ton_balance: userData.ton_balance || 0
    })
    
    currentAccount.value = {
      ...userData,
      score: userData.score || 0,
      ton_balance: userData.ton_balance || 0
    }
    
    balance.value = userData.ton_balance || 0

  } catch (error) {
    console.error('Ошибка загрузки данных пользователя:', error)
  }
}

const logout = async () => {
  if (props.tonConnectUI?.connected) {
    await props.tonConnectUI.disconnect()
  }
  scoreStore.clearAccount()
  localStorage.removeItem('currentAccount')
  localStorage.removeItem('isLoggedIn')
  router.push('/register')
}

const navigateToNFT = () => {
  router.push('/mynft')
}

// Инициализация
onMounted(() => {
  loadUserData()
  fetchBalance()

  // Подписка на изменения
  const userSubscription = supabase
    .channel('user_changes')
    .on('postgres_changes', {
      event: '*',
      schema: 'public',
      table: 'users',
      filter: `name=eq.${currentAccount.value.name}`
    }, (payload) => {
      if (payload.new) {
        scoreStore.setCurrentAccount({
          name: payload.new.name,
          score: payload.new.score || 0
        })
        currentAccount.value = {
          ...payload.new,
          score: payload.new.score || 0
        }
      }
    })
    .subscribe()

  // Подписка на изменения кошелька
  const unsubscribe = props.tonConnectUI?.onStatusChange((wallet) => {
    if (wallet) {
      fetchBalance()
      const interval = setInterval(fetchBalance, 10000)
      onUnmounted(() => clearInterval(interval))
    } else {
      balance.value = '0'
    }
  })

  onUnmounted(() => {
    supabase.removeChannel(userSubscription)
    unsubscribe?.()
  })
})

watch(() => props.tonConnectUI?.connected, async (connected) => {
  if (connected) {
    await fetchBalance()
    const interval = setInterval(fetchBalance, 30000) // Проверка каждые 30 сек
    onUnmounted(() => clearInterval(interval))
  } else {
    balance.value = '0'
  }
}, { immediate: true })

watch(withdrawAmount, (newVal) => {
  if (newVal > currentAccount.value.ton_balance) {
    withdrawAmount.value = currentAccount.value.ton_balance
  }
})
</script>

<style scoped>
/* Общие стили */
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
  --bg: #121212;
  --surface: #1E1E1E;
  --surface-light: #2A2A2A;
  --text: #FFFFFF;
  --text-secondary: #B0B0B0;
  --accent: #FFC400;
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
  height: 30px;
  background-color: var(--accent);
  border-radius: 8px;
  padding: 0 8px;
  gap: 4px;
  min-width: fit-content;
  cursor: pointer;
  transition: transform 0.2s;
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
  width: 22px;
  height: 20px;
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
}

.avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--surface);
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
  color: #000;
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

.quick-topup button:hover {
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
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
}

.nft-btn:hover {
  background-color: #E6B000;
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
.wallet-info {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 10px;
  word-break: break-all;
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

.btn-primary:disabled {
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

.balance-action-btn.top-up:hover {
  background-color: #006699;
}

.balance-action-btn.withdraw {
  background-color: var(--surface-light);
  color: var(--text);
  border: 1px solid var(--border);
}

.balance-action-btn.withdraw:hover {
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

/* Добавьте эти стили в конец секции <style scoped> */
html, body {
  overflow-x: hidden;
  width: 100%;
  margin: 0;
  padding: 0;
}
</style>