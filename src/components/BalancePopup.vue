<!-- src/components/BalancePopup.vue -->
<template>
  <div class="balance-modal-overlay" @click.self="handleClose">
    <div class="balance-popup">
      <div class="balance-popup-header">
        <button class="back-btn" @click="handleClose">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M15 18l-6-6 6-6"/>
          </svg>
        </button>
        <h3>Balance: {{ formattedBalance }} TON</h3>
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
            <button @click="topUpAmount = 1">1 TON</button>
            <button @click="topUpAmount = 5">5 TON</button>
            <button @click="topUpAmount = 10">10 TON</button>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showTopUpModal = false">Cancel</button>
          <button class="btn-primary" @click="confirmTopUp">Top Up</button>
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
              class="amount-input" 
              min="0.1" 
              :max="Math.floor(Number(currentAccount.ton_balance) * 1000) / 1000"
              step="0.001"
              :placeholder="`Available: ${formattedBalance} TON`"
              :disabled="!isWalletConnected"
            >
          </div>
          <div class="quick-amounts">
            <button @click="withdrawAmount = 1">1 TON</button>
            <button @click="withdrawAmount = 5">5 TON</button>
            <button @click="withdrawAmount = 10">10 TON</button>
            <button @click="withdrawAmount = Math.floor(Number(currentAccount.ton_balance) * 1000) / 1000">All</button>
          </div>
          <div class="total-info">
            Withdraw {{ formattedWithdrawAmountInModal }} TON
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showWithdrawModal = false">Cancel</button>
          <button class="btn-primary" @click="confirmWithdraw">Withdraw</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useScoreStore } from '@/stores/score'
import supabase from '../../services/supabase'
import { sendWithdrawTransaction, initWithdrawSystem } from '/services/tonWithdraw.js'

const props = defineProps({
  tonConnectUI: Object
})

const emit = defineEmits(['close', 'showHistory'])

const showOperationsHistory = () => {
  emit('close')
  emit('showHistory')
}
const router = useRouter()
const scoreStore = useScoreStore()

// Состояния
const currentAccount = ref(scoreStore.currentAccount || {})
const showTopUpModal = ref(false)
const showWithdrawModal = ref(false)
const topUpAmount = ref(1)
const withdrawAmount = ref(0)
const isLoading = ref(false)
const isTransactionInProgress = ref(false)

const RECIPIENT_ADDRESS = "EQBzpf5KMPu3aOnEkgSD2Sx1zdYG644uLebdUteJIRi3o18D"

// Вычисляемые свойства
const isWalletConnected = computed(() => props.tonConnectUI?.connected || false)

const formattedBalance = computed(() => {
  const balance = Number(currentAccount.value.ton_balance) || 0
  return Math.floor(balance * 1000) / 1000
})

const formattedWithdrawAmountInModal = computed(() => {
  const amount = parseFloat(withdrawAmount.value)
  return isNaN(amount) ? '0.00' : amount.toFixed(2)
})

const isWithdrawValid = computed(() => {
  const amount = parseFloat(withdrawAmount.value)
  return amount >= 0.1 && amount <= (Math.floor(Number(currentAccount.value.ton_balance) * 1000) / 1000)
})

// Методы
const handleClose = () => {
  emit('close')
}

const handleBalanceAction = (action) => {
  if (!isWalletConnected.value) {
    alert('Пожалуйста, подключите кошелек')
    return
  }
  
  if (action === 'topup') {
    showTopUpModal.value = true
  } else if (action === 'withdraw') {
    showWithdrawModal.value = true
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
    
    if (scoreStore.currentAccount) {
      scoreStore.currentAccount.ton_balance = newBalance
    }
    
    localStorage.setItem(`lastBalance_${currentAccount.value.name}`, Number(newBalance).toFixed(2))

  } catch (error) {
    console.error('Error updating TON balance:', error)
    throw error
  }
}

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
      txHash = await waitForTransactionHash(senderAddress, amount, 30)
    }
    
    if (!txHash) {
      if (result.hash) {
        txHash = result.hash
      } else if (result.transaction?.hash) {
        txHash = result.transaction.hash
      } else if (result.txId) {
        txHash = result.txId
      }
    }
    
    if (!txHash) {
      txHash = generateFallbackHash(senderAddress, amount)
      console.warn(`⚠️ Используем fallback хэш: ${txHash}`)
    } else {
      console.log(`✅ Получен хэш транзакции: ${txHash}`)
    }
    
    console.log(`🔗 Ссылка: https://tonscan.org/tx/${txHash}`)
    
    // Обновляем баланс
    await updateTonBalance(amount)
    
    showTopUpModal.value = false
    
    // ✅✅✅ ВАЖНО: ВЫЗЫВАЕМ ЗАПИСЬ В ИСТОРИЮ ✅✅✅
    await addOperationToHistory('topup', amount, txHash)
    
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

// В BalancePopup.vue, добавьте эту функцию (скопируйте из Profile.vue с небольшими изменениями):

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
    
    const walletAddress = props.tonConnectUI?.account?.address || null
    
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
    
    const operation = {
      id: nextId,
      type: type,
      amount: amount ? Number(parseFloat(amount).toFixed(2)) : null,
      timestamp: new Date().toISOString(),
      transactionHash: transactionHash,
      walletAddress: walletAddress,
      is_recorded: "false"
    }

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
    
  } catch (error) {
    console.error('💥 Ошибка при записи операции:', error)
    throw error
  } finally {
    setTimeout(() => {
      isAddingOperation = false
    }, 1000)
  }
}

const confirmTopUp = () => {
  if (!isWalletConnected.value) {
    alert('Пожалуйста, подключите кошелек')
    return
  }
  
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

// Функция для ожидания хэша транзакции
const waitForTransactionHash = async (walletAddress, expectedAmount, maxAttempts = 30) => {
  console.log("⏳ Ожидаем подтверждения транзакции...");
  
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    try {
      const response = await fetch(
        `https://toncenter.com/api/v2/getTransactions?address=${walletAddress}&limit=5`
      );
      
      if (response.ok) {
        const data = await response.json();
        
        if (data.ok && data.result && data.result.length > 0) {
          const expectedAmountNano = Math.floor(expectedAmount * 1000000000);
          
          for (const tx of data.result) {
            const txAmount = parseFloat(tx.amount) || 0;
            const txTime = new Date(tx.utime * 1000).getTime();
            const now = Date.now();
            
            if (txAmount === expectedAmountNano && (now - txTime) < 60000) {
              const txHash = tx.transaction_id.hash;
              if (txHash && txHash.length === 64) {
                console.log(`📝 Получен реальный хэш: ${txHash}`);
                return txHash;
              }
            }
          }
          
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
    
    if (attempt % 5 === 0) {
      console.log(`⏳ Ожидание хэша... ${attempt + 1}/${maxAttempts} секунд`);
    }
  }
  
  console.warn(`⚠️ Не удалось получить реальный хэш транзакции за ${maxAttempts} секунд`);
  return null;
}
const confirmWithdraw = async () => {
  if (!isWithdrawValid.value || isTransactionInProgress.value || !isWalletConnected.value) return

  try {
    isTransactionInProgress.value = true
    isLoading.value = true
    const amount = parseFloat(withdrawAmount.value)
    
    const userAddress = props.tonConnectUI.account?.address
    if (!userAddress) throw new Error('Не удалось получить адрес кошелька')
    
    const userId = currentAccount.value.id || currentAccount.value.name
    const userName = currentAccount.value.name || 'unknown'
    
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

    const result = await sendWithdrawTransaction(
      userId, userName, userAddress, amount
    )
    
    if (result.success) {
      const newBalance = (currentBalance - amount).toFixed(2)
      const { error: updateError } = await supabase
        .from('users')
        .update({ ton_balance: newBalance })
        .eq('name', currentAccount.value.name)

      if (updateError) throw updateError

      currentAccount.value.ton_balance = parseFloat(newBalance)
      
      if (scoreStore.currentAccount) {
        scoreStore.currentAccount.ton_balance = parseFloat(newBalance)
      }
      
      localStorage.setItem(`lastBalance_${currentAccount.value.name}`, newBalance)
      
      showWithdrawModal.value = false
 
      
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



// Следим за изменением баланса в сторе
watch(
  () => scoreStore.currentAccount?.ton_balance,
  (newBalance) => {
    if (newBalance !== undefined && currentAccount.value) {
      currentAccount.value.ton_balance = newBalance
    }
  },
  { immediate: true }
)

// Загрузка профиля
const loadUserProfile = async () => {
  try {
    const savedAccount = localStorage.getItem('currentAccount')
    if (!savedAccount) {
      handleClose()
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
      handleClose()
      return
    }

    currentAccount.value = userData
    
  } catch (error) {
    console.error('❌ Ошибка загрузки профиля:', error)
  }
}

// Обработчик нажатия Escape
const handleEscape = (e) => {
  if (e.key === 'Escape') {
    handleClose()
  }
}

onMounted(async () => {
  await loadUserProfile()
  await initWithdrawSystem()
  document.addEventListener('keydown', handleEscape)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleEscape)
})
</script>

<style scoped>
.balance-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(8px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

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
  flex: 1;
  text-align: center;
}

.back-btn {
  width: 40px;
  height: 40px;
  border-radius: 30px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.back-btn:hover {
  background: rgba(255, 187, 0, 0.15);
  border-color: rgba(255, 187, 0, 0.3);
  color: #ffbb00;
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
  transition: all 0.2s;
  text-align: center;
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

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1100;
}

.modal {
  background: linear-gradient(145deg, #1a1a1a 0%, #252525 100%);
  border-radius: 40px;
  padding: 24px 20px;
  max-width: 400px;
  width: 90%;
  border: 1px solid rgba(255, 255, 255, 0.05);
  box-shadow: 0 30px 60px -15px rgba(0, 0, 0, 0.8);
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

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.modal-header h3 {
  font-size: 24px;
  font-weight: 700;
  color: #ffffff;
  margin: 0;
}

.close-btn {
  width: 40px;
  height: 40px;
  border-radius: 30px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #ffffff;
  font-size: 24px;
  cursor: pointer;
  transition: all 0.2s;
}

.close-btn:hover {
  background: rgba(255, 187, 0, 0.15);
  border-color: rgba(255, 187, 0, 0.3);
  transform: rotate(90deg);
  color: #ffbb00;
}

.input-group {
  margin-bottom: 20px;
}

.input-group label {
  display: block;
  margin-bottom: 10px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 15px;
  font-weight: 500;
}

.amount-input {
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

.amount-input:focus {
  outline: none;
  border-color: rgba(255, 187, 0, 0.5);
  background: rgba(255, 255, 255, 0.08);
}

.quick-amounts {
  display: flex;
  gap: 10px;
  margin: 20px 0;
  flex-wrap: wrap;
}

.quick-amounts button {
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 30px;
  color: #ffffff;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  flex: 1;
  min-width: 70px;
}

.quick-amounts button:hover {
  background: rgba(255, 187, 0, 0.15);
  border-color: rgba(255, 187, 0, 0.4);
  transform: translateY(-2px);
}

.total-info {
  font-size: 18px;
  font-weight: 700;
  color: #ffffff;
  margin: 16px 0;
  padding: 16px;
  background: rgba(255, 187, 0, 0.1);
  border-radius: 24px;
  text-align: center;
  border: 1px solid rgba(255, 187, 0, 0.2);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.btn-secondary {
  padding: 14px 28px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 40px;
  color: #ffffff;
  font-weight: 600;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s;
  flex: 1;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
  transform: scale(1.02);
}

.btn-primary {
  padding: 14px 28px;
  background: linear-gradient(135deg, #ffbb00 0%, #ffd966 100%);
  border: none;
  border-radius: 40px;
  color: #1a1a1a;
  font-weight: 700;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s;
  flex: 1;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px -8px rgba(255, 187, 0, 0.7);
}
</style>