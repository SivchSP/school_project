



<template>
  <!-- Ваш шаблон остаётся без изменений -->
  <div class="progressperchik">
    <h4 class="progress-level">
      <span>{{ store.currentScore }} / {{ store.level.value }}</span>
      <span>{{ store.level.level + 1 }}</span>
    </h4>
    <div class="progress-container">
      <div class="progress-value" :style="{ width: progress + '%' }"></div>
    </div>
  </div>
  <div class="progress-bar-container" :style="containerStyle">
    <div class="progress-bar">
      <div class="progress-valueperchik" :style="{ width: progress1 + '%' }"></div>
    </div>
    <div class="progress-info">
      <h4 class="progress-level">
        <span>Клики</span>
        <span>{{ availableClicks }} / {{ maxClicks }}</span>
      </h4>
    </div>
  </div>

  <div class="records-page-button-container" :style="buttonContainerStyle">
    <button class="records-page-button" @click="goToRecordsPage">
      <h2 class="record">Рекорды</h2>
    </button>
  </div>
</template>

<script setup>
import { useScoreStore } from '@/stores/score';
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import supabase from '../../services/supabase';
import { useRouter } from 'vue-router';

const router = useRouter();
const store = useScoreStore();

const currentUserName = computed(() => store.currentAccount?.name);
const progress1 = computed(() => (availableClicks.value / maxClicks) * 100);
const progress = computed(() => (100 * store.currentScore) / store.level.value);

const top_size = ref('520px');
const screenWidth = ref(window.screen.width);
const width_size = ref('369px');
const leftButton = ref(0);
const maxClicks = 100;
const availableClicks = ref(maxClicks);
const userBoost = ref(0);
const userData = ref(null);

let interval;

// Загружаем данные пользователя и восстанавливаем клики
const loadUserData = async () => {
  if (!currentUserName.value) return;

  const { data, error } = await supabase
    .from('users')
    .select('*')
    .eq('name', currentUserName.value)
    .single();
    
  if (data) {
    userData.value = data;
    userBoost.value = data.boost || 0;

    // Восстанавливаем клики с учётом прошедшего времени
    const lastUpdate = new Date(data.last_click_update || new Date());
    const now = new Date();
    const secondsPassed = Math.floor((now - lastUpdate) / 1000);

    // Добавляем клики за прошедшее время (но не больше maxClicks)
    const newClicks = Math.min(
      maxClicks,
      (data.available_clicks || maxClicks) + secondsPassed
    );

    availableClicks.value = newClicks;
    store.setCurrentAccount(data);

    // Обновляем время последнего обновления
    await supabase
      .from('users')
      .update({ 
        available_clicks: newClicks,
        last_click_update: now.toISOString() 
      })
      .eq('name', currentUserName.value);
  } else if (error) {
    console.error('Ошибка загрузки данных:', error);
  }
};

// Сохраняем клики и время обновления
const saveClicks = async () => {
  if (!currentUserName.value) return;

  const { error } = await supabase
    .from('users')
    .update({ 
      available_clicks: availableClicks.value,
      last_click_update: new Date().toISOString() 
    })
    .eq('name', currentUserName.value);

  if (error) {
    console.error('Ошибка сохранения:', error);
  }
};

const useClick = () => {
  const clickCost = userBoost.value + 1;
  
  if (availableClicks.value >= clickCost) {
    availableClicks.value -= clickCost;
    saveClicks();
    return true;
  }
  return false;
};

onMounted(async () => {
  await loadUserData();

  // Обновляем клики каждую секунду
  interval = setInterval(() => {
    if (availableClicks.value < maxClicks) {
      availableClicks.value += 1;
      saveClicks();
    }
  }, 1000);

  // Адаптация под разные экраны
  const calculatedWidthSize = Math.ceil((screenWidth.value - 6));
  width_size.value = `${calculatedWidthSize}px`;
  leftButton.value = `${calculatedWidthSize + 6}px`;
  
  if (screenWidth.value > 500) {
    width_size.value = '424px';
    leftButton.value = '218px';
  }
});

onUnmounted(() => {
  clearInterval(interval);
  saveClicks(); // Сохраняем клики перед закрытием
});

watch(currentUserName, (newVal) => {
  if (newVal) {
    loadUserData();
  }
});

const containerStyle = computed(() => ({
  position: 'fixed',
  top: '40px',
  left: '3px',
  width: width_size.value,
}));

const buttonContainerStyle = computed(() => ({
  position: 'fixed',
  top: '0px',
  left: '3px',
  width: width_size.value,
}));

const goToRecordsPage = () => {
  router.push('/records');
};

defineExpose({
  availableClicks,
  useClick,
  userData,
});
</script>

<style scoped>
.progressperchik{
 background-color: #1f1f1f;
 border-radius: 0px;
 
}
.progress-bar-container {
  text-align: center;
}

.progress-bar {
  width: 100%;
  height: 10px; /* Высота прогресс-бара */
  background-color: #3d3d3d;
  border-radius: 10px;
  overflow: hidden;
}

.progress-valueperchik {
  height: 100%;
  background-color: #e7b81f;
  transition: width 0.3s ease;
}

.progress-info {
  margin-top: 8px;
  font-size: 15px;
  color: #e0e0e0;
  font-family: 'Inter', sans-serif;
  font-weight: 600;
}

.text {
  margin-top: 8px;
  font-size: 15px;
  color: #e0e0e0;
}

.records-page-button-container {
  position: fixed;
  top: 0px;
}
.record {
  color: #d4d4d4;
}

.records-page-button {
  width: 100%; /* Ширина кнопки равна ширине контейнера */
  padding: 7px;
  background-color: #3f4b4ea1;
  color: white;
  border: none;
  border-radius: 10px; /* Убираем скругление углов */
  cursor: pointer;
  text-align: center; /* Текст по центру */
}
</style>