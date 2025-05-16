<template>
  <section class="ads-container">
  <div class="ad-card">
  <div class="task-container">
    <div class="list-item">
    <h4>Подпишись на телеграм AMAHASLA</h4>
    </div>
    <button
      @click="handleTask"
      class="task-button"
      :class="{ completed: isCompleted }"
      :disabled="isCompleted || !currentAccount"
    >
      {{ isCompleted ? 'Задание выполнено' : '10.000' }}
    </button>
    <p v-if="message" class="message" :class="{ error: isError }">
      {{ message }}
    </p>
  </div>
</div>
</section>

</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useScoreStore } from '@/stores/score';
import { completeFirstTask } from '../../api/app';
import supabase from '../../services/supabase';
const scoreStore = useScoreStore();
const currentAccount = ref(null);
const isCompleted = ref(false);
const message = ref('');
const isError = ref(false);

// Telegram ссылка для задания
const TASK_TELEGRAM_LINK = 'https://t.me/amahaslacoin';

// Проверяем статус задания при загрузке
onMounted(async () => {
  if (scoreStore.currentAccount) {
    currentAccount.value = scoreStore.currentAccount;
    await checkTaskStatus();
  }
});

// Проверяем статус задания
async function checkTaskStatus() {
  try {
    const { data } = await supabase
      .from('users')
      .select('tasks')
      .eq('name', currentAccount.value.name)
      .single();

    isCompleted.value = data?.tasks?.["1"] === true;
  } catch (error) {
    console.error('Ошибка проверки задания:', error);
  }
}

// Обработчик выполнения задания
async function handleTask() {
  if (!currentAccount.value) {
    showMessage('Сначала войдите в аккаунт!', true);
    return;
  }

  try {
    // 1. Открываем Telegram ссылку
    window.open(TASK_TELEGRAM_LINK, '_blank');
    
    // 2. Выполняем задание и получаем награду
    const result = await completeFirstTask(currentAccount.value.name);
    
    if (result.alreadyCompleted) {
      showMessage('Вы уже выполнили это задание!');
      isCompleted.value = true;
      return;
    }

    // 3. Обновляем локальное состояние
    scoreStore.setScore(result.newScore);
    isCompleted.value = true;
    showMessage('Вы получили 10.000 амахаслы!');
    
  } catch (error) {
    console.error('Ошибка выполнения задания:', error);
    showMessage(error.message || 'Ошибка выполнения задания', true);
  }
}

// Показываем сообщение
function showMessage(msg, error = false) {
  message.value = msg;
  isError.value = error;
  setTimeout(() => message.value = '', 3000);
}
</script>

<style scoped>
.task-container {
  text-align: center;
  padding: 20px;
  max-width: 300px;
  margin: 0 auto;
}

.task-button {
  background-color: white;
  color: black;
  border: 2px solid #4CAF50;
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
  border-radius: 5px;
  font-weight: bold;
  transition: all 0.3s;

}

.task-button:hover:not(:disabled) {
  background-color: #f0f0f0;
}

.task-button:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.task-button.completed {
  background-color: #009205;
  color: white;
}

.message {
  margin-top: 10px;
  color: #009205;
}

.message.error {
  color: #f44336;
}


.ad-card { background: #424242; 
  border: 2px solid #ffc4001f;
  border-radius: 10px; 
  padding: 19px;
  text-align: center; 
  display: flex;
  flex-direction: column; }
.ads-container { 
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); 
  gap: 20px; }
.list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 19px;
  margin: 8px 0;
  background-color: #ffc400;
  border-radius: 8px;
  color: rgb(0, 0, 0);
  font-weight: bold;
  font-size: large;
  box-shadow: 0 -5px 15px rgba(255, 196, 0, 0.534);

}
</style>