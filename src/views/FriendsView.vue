<template>
  <div class="text-content">
   <div class="friends-page">
    <h1></h1>

    <h1></h1>
    <div class="center">
      <button class="referal" @click="copy">{{ referalText }}</button>
      <h1></h1>
    </div>
    <p class="info">Пригласи друга и получи +5000 Амахаслы!</p>
    <h1></h1>

    <h1>ТВОИ ДРУЗЬЯ</h1>

    <h3 v-if="!loading && friends.length === 0"></h3>
    <h3 v-if="loading">Загрузка...</h3>

    <ul class="list">
      <li class="list-item" v-for="friend in friends" :key="friend.id">
        {{ friend.name }}
        <span class="list-btn done">5000</span>
      </li>
    </ul>
  </div>
</div>

</template>

<script setup>

import { useScoreStore } from '@/stores/score'
import { ref, computed, onMounted, watch } from 'vue'
import supabase from '../../services/supabase'
import { debounce } from 'lodash' // Добавляем debounce

const scoreStore = useScoreStore()

const referalText = ref('Твой реферал')
const telegramUsername = ref('')
const currentFriends = ref(null) // Изменено на null для чёткого отслеживания состояния
const loading = ref(false) // Начальное значение false
const error = ref(null)

// Добавляем флаг для отслеживания инициализации
const isInitialized = ref(false)

// Дебаунс для предотвращения множественных вызовов
const debouncedLoadAccount = debounce(loadAccountData, 500)

// Инициализация
onMounted(async () => {
  if (isInitialized.value) return
  loading.value = true
  try {
    await debouncedLoadAccount()
    isInitialized.value = true
  } catch (err) {
    error.value = err.message
    console.error('Ошибка инициализации:', err)
  } finally {
    loading.value = false
  }
})

// Оптимизированный обработчик изменений
watch(() => scoreStore.currentAccount, (newAccount) => {
  if (!newAccount || !isInitialized.value) return
  loading.value = true
  debouncedLoadAccount().finally(() => {
    loading.value = false
  })
}, { deep: true })

// Оптимизированная загрузка данных
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
    
    // Более безопасное преобразование friends
    currentFriends.value = userData?.friends 
      ? Object.entries(userData.friends)
          .filter(([id, name]) => id && name)
          .map(([id, name]) => ({ id, name }))
      : []
      
  } catch (err) {
    console.error('Ошибка загрузки данных:', {
      error: err,
      account: scoreStore.currentAccount
    })
    currentFriends.value = []
    throw err
  }
}

// Копирование реферальной ссылки (без изменений)
function copy() {
  try {
    if (!telegramUsername.value) {
      return
    }
    
    navigator.clipboard.writeText(
      `https://t.me/iamhustler_bot?start=${telegramUsername.value}`
    )
    referalText.value = 'Скопировано!'
    
    setTimeout(() => {
      referalText.value = 'Твой реферал'
    }, 3000)
  } catch (err) {
    console.error('Ошибка копирования:', err)
  }
}
// Более безопасный computed для friends
const friends = computed(() => {
  if (currentFriends.value === null) return [] // Данные ещё не загружены
  if (!Array.isArray(currentFriends.value)) {
    console.warn('Некорректный формат friends:', currentFriends.value)
    return []
  }
  return currentFriends.value
})
</script>

<style scoped>
.text-content {
  padding: 20px;
  font-family: Arial, sans-serif;
  text-align: center;
}
.friends-page{
  margin-bottom: 25px;
  background-color: #353535;
  padding: 10px;
  border-radius: 10px;
  box-shadow: 0 0 20px rgba(255, 196, 0, 0.5);
  border: 1px solid #ffc400;
  width: 99%;


}
.center {
  display: flex;
  justify-content: center;
  margin: 20px 0;
  
}

.referal {
  padding: 10px 20px;
  background-color: #ffc400;
  border: none;
  border-radius: 10px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
  width: 95%;
  overflow-y: auto;
}

.referal:hover {
  background-color: #ffc800;
  transform: translateY(-2px);
}
.info{
  color: #808080;
  font-style: normal;
}
.list {
  list-style: none;
  padding: 0;
  max-width: 95%;
  margin: 0 auto;
  overflow-y: auto;
}

.list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  margin: 5px 0;
  background-color: #ffc400;
  border-radius: 5px;
  color: rgb(0, 0, 0);

}

.reward-badge {
  padding: 3px 8px;
  background-color: #4CAF50;
  color: white;
  border-radius: 10px;
  font-size: 0.8em;
}
</style>