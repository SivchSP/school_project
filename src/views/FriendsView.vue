
<template>
  <div class="friends-container">
    <div class="friends-card">
      <!-- Header section -->
      <div class="header-section">
        <h1 class="page-title">Referral Program</h1>
        <p class="page-subtitle">Invite friends and earn bonuses</p>
      </div>

      <!-- Referral link -->
      <div class="referral-section">
        <div class="referral-card">
          <div class="referral-info">
            <div class="reward-badge">
              <span class="reward-icon">🎁</span>
              <span class="reward-text">+500</span>
            </div>
            <p class="referral-description">For each invited friend</p>
          </div>
          
          <button 
            class="referral-btn" 
            @click="copy" 
            :disabled="!telegramUsername"
            :class="{ 'copied': referalText === 'Copied!' }"
          >
            <span class="btn-text">{{ referalText }}</span>
            <span class="btn-icon" v-if="referalText !== 'Copied!'">📋</span>
            <span class="btn-icon" v-else>✅</span>
          </button>
        </div>
      </div>

      <!-- Friends list -->
      <div class="friends-section">
        <div class="section-header">
          <h2 class="section-title">Your Friends</h2>
          <div class="friends-count" v-if="!loading">{{ friends.length }}</div>
        </div>

        <!-- Loading state -->
        <div class="loading-state" v-if="loading">
          <div class="spinner"></div>
          <p>Loading friends...</p>
        </div>

        <!-- Empty state -->
        <div class="empty-state" v-else-if="friends.length === 0">
          <div class="empty-icon">👥</div>
          <h3>No friends yet</h3>
          <p>Invite friends using the referral link above</p>
        </div>

        <!-- Friends list -->
        <div class="friends-list" v-else>
          <div 
            class="friend-item" 
            v-for="friend in friends" 
            :key="friend.id"
          >
            <div class="friend-info">
              <div class="friend-avatar">
                {{ getInitials(friend.name) }}
              </div>
              <div class="friend-details">
                <span class="friend-name">{{ friend.name }}</span>
                <span class="friend-status">Active</span>
              </div>
            </div>
            <div class="friend-reward">
              <span class="reward-amount">+500</span>
              <span class="reward-currency">Drops</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useScoreStore } from '@/stores/score'
import { ref, computed, onMounted, watch } from 'vue'
import supabase from '../../services/supabase'
import { debounce } from 'lodash'

const scoreStore = useScoreStore()

const referalText = ref('Copy referral link')
const telegramUsername = ref('')
const currentFriends = ref(null)
const loading = ref(false)
const error = ref(null)
const isInitialized = ref(false)

const debouncedLoadAccount = debounce(loadAccountData, 500)

onMounted(async () => {
  if (isInitialized.value) return
  loading.value = true
  try {
    await debouncedLoadAccount()
    isInitialized.value = true
  } catch (err) {
    error.value = err.message
    console.error('Initialization error:', err)
  } finally {
    loading.value = false
  }
})

watch(() => scoreStore.currentAccount, (newAccount) => {
  if (!newAccount || !isInitialized.value) return
  loading.value = true
  debouncedLoadAccount().finally(() => {
    loading.value = false
  })
}, { deep: true })

async function loadAccountData() {
  if (!scoreStore.currentAccount?.name) {
    currentFriends.value = []
    return
  }

  try {
    const { data: userData, error: supabaseError } = await supabase
      .from('users')
      .select('telegram, friends')
      .eq('name', scoreStore.currentAccount.name)
      .single()

    if (supabaseError) throw supabaseError

    telegramUsername.value = userData?.telegram || ''
    
    currentFriends.value = userData?.friends 
      ? Object.entries(userData.friends)
          .filter(([id, name]) => id && name)
          .map(([id, name]) => ({ id, name }))
      : []
      
  } catch (err) {
    console.error('Data loading error:', {
      error: err,
      account: scoreStore.currentAccount
    })
    currentFriends.value = []
    throw err
  }
}

function copy() {
  try {
    if (!telegramUsername.value) {
      return
    }
    navigator.clipboard.writeText(
      `https://t.me/DROPS_OFC_bot?start=${telegramUsername.value}`
    )
    referalText.value = 'Copied!'
    
    setTimeout(() => {
      referalText.value = 'Copy referral link'
    }, 3000)
  } catch (err) {
    console.error('Copy error:', err)
  }
}

function getInitials(name) {
  return name.split(' ').map(n => n[0]).join('').toUpperCase()
}

const friends = computed(() => {
  if (currentFriends.value === null) return []
  if (!Array.isArray(currentFriends.value)) {
    console.warn('Invalid friends format:', currentFriends.value)
    return []
  }
  return currentFriends.value
})
</script>

<style scoped>
.friends-container {
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
  min-height: 100vh;
}

.friends-card {
  background-color: #222222;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(255, 196, 0, 0.15);
  border: 2px solid #ffc400;
  max-width: 100%;
  margin: 0 auto;
}

/* Header Section */
.header-section {
  text-align: center;
  margin-bottom: 32px;
}

.page-title {
  color: #ffc400;
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 8px 0;
  text-shadow: 0 2px 4px rgba(255, 196, 0, 0.3);
}

.page-subtitle {
  color: #b0b0b0;
  font-size: 16px;
  margin: 0;
}

/* Referral Section */
.referral-section {
  margin-bottom: 32px;
}

.referral-card {
  background: linear-gradient(135deg, #2e2e2e 0%, #2b2b2b 100%);
  border-radius: 35px;
  padding: 24px;
  border: 3px solid #ffc400;
  box-shadow: 0 4px 16px rgba(255, 196, 0, 0.2);
}

.referral-info {
  text-align: center;
  margin-bottom: 20px;
}

.reward-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 196, 0, 0.1);
  padding: 8px 16px;
  border-radius: 20px;
  border: 1px solid #ffc400;
  margin-bottom: 12px;
}

.reward-icon {
  font-size: 18px;
}

.reward-text {
  color: #ffc400;
  font-weight: 600;
  font-size: 14px;
}

.referral-description {
  color: #808080;
  font-size: 14px;
  margin: 0;
}

.referral-btn {
  width: 100%;
  padding: 16px;
  background: linear-gradient(135deg, #ffc400 0%, #ffb300 100%);
  border: none;
  border-radius: 25px;
  color: #000;
  font-weight: 600;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  box-shadow: 0 4px 12px rgba(255, 196, 0, 0.3);
}

.referral-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 196, 0, 0.4);
}

.referral-btn:active {
  transform: translateY(0);
}

.referral-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.referral-btn.copied {
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
  color: white;
}

.btn-text {
  font-weight: 600;
}

.btn-icon {
  font-size: 18px;
}

/* Friends Section */
.friends-section {
  background: #2d2d2d;
  border-radius: 35px;
  padding: 24px;
  border: 3px solid #404040;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-title {
  color: #ffc400;
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}

.friends-count {
  background: #ffc400;
  color: #000;
  font-weight: 700;
  padding: 6px 12px;
  border-radius: 12px;
  font-size: 14px;
}

/* Loading State */
.loading-state {
  text-align: center;
  padding: 40px 20px;
  color: #808080;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #404040;
  border-top: 3px solid #ffc400;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #808080;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-state h3 {
  color: #b0b0b0;
  margin: 0 0 8px 0;
  font-size: 18px;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
}

/* Friends List */
.friends-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.friend-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #353535;
  border-radius: 12px;
  border: 2px solid #404040;
  transition: all 0.2s ease;
}

.friend-item:hover {
  border-color: #ffc400;
  transform: translateY(-1px);
}

.friend-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.friend-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ffc400 0%, #ffb300 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #000;
  font-weight: 700;
  font-size: 14px;
}

.friend-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.friend-name {
  color: #ffffff;
  font-weight: 600;
  font-size: 14px;
}

.friend-status {
  color: #4CAF50;
  font-size: 12px;
  font-weight: 500;
}

.friend-reward {
  display: flex;
  align-items: center;
  gap: 4px;
  background: rgba(255, 196, 0, 0.1);
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid #ffc400;
}

.reward-amount {
  color: #ffc400;
  font-weight: 700;
  font-size: 14px;
}

.reward-currency {
  color: #ffd000;
  font-size: 12px;
  font-weight: 500;
}

/* Responsive */
@media (max-width: 480px) {
  .friends-container {
    padding: 16px;
  }
  
  .friends-card {
    padding: 20px;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .referral-card {
    padding: 20px;
  }
}
</style>
