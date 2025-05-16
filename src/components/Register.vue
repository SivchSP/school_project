<template>
  <div class="PERCHIK">
    <div class="app dark-theme">
    <main class="content">

    <div v-if="!isLoggedIn" class="profile-page">
      <section class="auth">
        <h1 class="auth-title">Вход</h1>
        <input v-model="username" placeholder="Имя пользователя" class="input" />
        <input v-model="password" type="password" placeholder="Пароль" class="input" />
        <button class="login-btn" @click="login">Войти</button>
      </section>
    </div>
  </main>
</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { createClient } from '@supabase/supabase-js'
import { useScoreStore } from '@/stores/score'

const supabaseUrl = 'https://jgkfvqiophgvswqvatbx.supabase.co'
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impna2Z2cWlvcGhndnN3cXZhdGJ4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk4ODI5NTMsImV4cCI6MjA1NTQ1ODk1M30.GTN1V9NJwnmwy8GmXOOz3SxepV7n4yVKkhLYZTYuFEQ'
const supabase = createClient(supabaseUrl, supabaseKey)
const scoreStore = useScoreStore()
const router = useRouter()

const isLoggedIn = ref(false)
const username = ref('')
const password = ref('')
const currentAccount = ref({
  name: '',
  score: 0,
  nft1: null,
  telegram: ''
})
const login = async () => {
  try {
    if (!username.value.trim() || !password.value.trim()) {
      return
    }

    const { data: userData, error } = await supabase
      .from('users')
      .select('*')
      .eq('name', username.value.trim())
      .eq('password', password.value.trim())
      .single()

    if (error) throw error
    if (!userData) {
      return
    }

    scoreStore.setCurrentAccount({
      name: userData.name,
      score: userData.score || 0
    })

    currentAccount.value = {
      name: userData.name || 'Без имени',
      score: userData.score || 0,
      nft1: userData.nft1,
      telegram: userData.telegram || ''
    }

    isLoggedIn.value = true
    localStorage.setItem('currentAccount', JSON.stringify(currentAccount.value))
    localStorage.setItem('isLoggedIn', 'true')
    
    router.push('/profile')
    
  } catch (error) {
    console.error('Ошибка при входе:', error)
  }
}

onMounted(() => {
  const savedLoginState = localStorage.getItem('isLoggedIn')
  if (savedLoginState === 'true') {
    isLoggedIn.value = true
    // Если пользователь уже авторизован, перенаправляем на профиль
    router.push('/profile')
  }
})
</script>

<style scoped>
#ton-connect {
  display: block !important; /* Принудительно отображать */
  visibility: visible !important;
  opacity: 1 !important;
}
.ton-connect-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
}

.wallet-info {
  margin-top: 20px;
  padding: 15px;
  background-color: #ffc400;
  border-radius: 8px;
  color: #000;
  max-width: 200px;
}

.disconnect-btn {
  margin-top: 10px;
  padding: 8px 16px;
  background-color: #ff4444;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.disconnect-btn:hover {
  background-color: #cc0000;
}
.wallet-btn {
  width: 40px;
  height: 40px;
  background-color: var(--surface-light);
  border: none;
  border-radius: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.wallet-btn:hover {
  background-color: #333;
}

.wallet-btn svg {
  width: 20px;
  height: 20px;
  stroke: var(--accent);
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

.app {
  min-width: 100%;
  margin: 0 auto;
  background-color: var(--bg);
  min-height: 100vh;
  font-family: 'Inter', sans-serif;
  color: var(--text);
}

/* Шапка */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background-color: var(--surface);
  border-bottom: 1px solid var(--border);
}

.header-actions {
  display: flex;
  gap: 12px;
}

.logo {
  font-weight: 700;
  font-size: 20px;
  color: var(--accent);
}

.wallet-btn {
  width: 40px;
  height: 40px;
  background-color: var(--surface-light);
  border: none;
  border-radius: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.wallet-btn:hover {
  background-color: #333;
}

.wallet-icon {
  width: 24px;
  height: 24px;
}

.logout-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
}

/* Основной контент */
.content {
  padding: 20px;
}

/* Профиль */
.profile-card {
  background-color: var(--accent);
  border-radius: 16px;
  padding: 30px 20px;
  text-align: center;
  margin-bottom: 20px;
}

.avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid var(--surface);
  margin-bottom: 15px;
}

.username {
  font-size: 22px;
  font-weight: 600;
  margin-bottom: 15px;
  color: #000;
}

.score {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  font-size: 20px;
  font-weight: 600;
  color: #000;
}

.frog-icon {
  width: 24px;
  height: 24px;
}

/* NFT Секция */
.nft-section {
  background-color: var(--surface);
  border-radius: 16px;
  padding: 20px;
  border: 2px solid #FFC400;
}

.nft-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 15px;
  color: var(--text);
}

.nft-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 20px;
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
  border-radius: 8px;
  font-weight: 600;
  background-color: var(--surface-light);
  color: var(--text-secondary);
}

.nft-badge.active {
  background-color: var(--accent);
  color: #000;
}

.nft-btn, .login-btn {
  width: 100%;
  padding: 14px;
  background-color: var(--accent);
  color: #000;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.nft-btn:hover, .login-btn:hover {
  background-color: #E6B000;
}

/* Форма входа */
.auth {
  background-color: var(--surface);
  border-radius: 16px;
  padding: 30px 20px;
  border: 1px solid var(--border);
}

.auth-title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 25px;
  text-align: center;
  color: var(--text);
}

.input {
  width: 100%;
  padding: 14px;
  margin-bottom: 15px;
  background-color: var(--surface-light);
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 16px;
  color: var(--text);
}

.input::placeholder {
  color: var(--text-secondary);
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
  width: 90%;
  max-width: 400px;
  background-color: var(--surface);
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid var(--border);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid var(--border);
}

.modal-header h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  color: var(--text);
}

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-secondary);
}

.modal-body {
  padding: 20px;
}

.modal-text {
  color: var(--text-secondary);
  margin-bottom: 15px;
}

.address-box {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: var(--surface-light);
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.address-box code {
  font-family: monospace;
  word-break: break-all;
  font-size: 14px;
  color: var(--text);
}

.copy-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-secondary);
  margin-left: 10px;
}

.progress-bar {
  height: 6px;
  background-color: var(--surface-light);
  border-radius: 3px;
  margin-bottom: 20px;
  overflow: hidden;
}

.progress {
  height: 100%;
  background-color: var(--accent);
  border-radius: 3px;
  transition: width 0.3s;
}

.modal-hint {
  font-size: 13px;
  color: var(--text-secondary);
  text-align: center;
  margin-bottom: 0;
}

.modal-footer {
  display: flex;
  justify-content: space-between;
  padding: 15px 20px;
  border-top: 1px solid var(--border);
}

.btn-primary {
  padding: 10px 20px;
  background-color: var(--accent);
  color: #000;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}

.btn-secondary {
  padding: 10px 20px;
  background-color: var(--surface-light);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
}
.profile-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  position: relative;
  bottom: 10px;
}

.login-button {
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
  width: 100%;
  margin-top: 10px;
  background-color: #4CAF50;
  color: white;
}

.login-button:hover {
  background-color: #45a049;
  transform: translateY(-2px);
}

.login-container {
  padding: 40px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  max-width: 400px;
  width: 100%;
}

.login-input {
  width: 100%;
  padding: 12px;
  margin-bottom: 15px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 16px;
}
</style>