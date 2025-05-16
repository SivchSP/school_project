<template>
  <img src="../assets/record.png" alt="coin" />
  
  <div class="records-page">
    <div v-if="records.length > 0" class="records-list">
      <h1>Абсолютный рекордсмен</h1>
      <div class="record-item">
        <h3>Имя:</h3>       <h3>АМАХАСЛА:</h3> 
      </div>
      <div v-for="record in records" :key="record.ID" class="record-item">
        <span class="record-name">{{ record.babkaname }}</span>
        <span class="record-clicks">{{ record.clicks }}</span>
      </div>
      <button
          @click="completeTask"
          class="list-btn"
        > <h4>💰Своровать амахаслу у Галины💰</h4>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import supabase from '../../services/supabase';
import { useScoreStore } from '@/stores/score';
import { completeTaskGetMoney } from '../../api/app';

const scoreStore = useScoreStore();
const records = ref([]);
const ID = 1;

const loadRecords = async () => {
  try {
    const { data, error } = await supabase
      .from('record')
      .select('*')
      .eq('id', ID)

    if (error) {
      throw error;
    }

    records.value = data;
  } catch (error) {
    console.error('Ошибка при загрузке данных:', error);
  }
};

const completeTask = async () => {
  try {
    if (!scoreStore.currentAccount) {
      return;
    }

    // Выполняем задание и получаем деньги
    const reward = 25000; // Размер вознаграждения
    await completeTaskGetMoney(reward, scoreStore.currentAccount.name);
    
    // Обновляем счет в хранилище
    
  } catch (error) {
    console.error('Ошибка при выполнении задания:', error);
  }
};

onMounted(() => {
  loadRecords();
});
</script>

<style scoped>
.records-page {
  padding: 20px;
  font-family: Arial, sans-serif;
}
h3 {
  margin-bottom: 5px;
  text-shadow: 
    -1px -1px 0 #000,
    1px -1px 0 #000,
    -1px 1px 0 #000,
    1px 1px 0 #000;
  color: white;
}
h1 {
  text-align: center;
  margin-bottom: 5px;
  color: #e0e0e0;
}
p {
  text-align: center;
  margin-bottom: 5px;
  gap:100px;
  top: 20px;
  color: #e0e0e0;
}
.list-btn {
  text-align: center;
  margin-top: 20px;
  padding: 10px;
  background-color: #ffd700;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 0 20px rgba(255, 196, 0, 0.5);

}
.list-btn:hover {
  background-color: #ffc800;
  transform: translateY(-2px);
}
.records-list {
  display: flex;
  flex-direction: column;
  gap:10px;
}
.record-item {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  border: 10px;
  border-radius: 20px;
  background-color: #5a5a5a;
  left: 20px;
  top: 20px;
}
.record-name {
  font-weight: bold;
  text-shadow: 
    -0.7px -0.7px 0 #000,
    0.7px -0.7px 0 #000,
    -0.7px 0.7px 0 #000,
    0.7px 0.7px 0 #000;
  color: #ffd000;
}
.record-clicks {
  text-shadow: 
    -0.7px -0.7px 0 #000,
    0.7px -0.7px 0 #000,
    -0.7px 0.7px 0 #000,
    0.7px 0.7px 0 #000;
  color: #ffffff;
}
</style>