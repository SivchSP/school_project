<template>
  <div class="records-page">
    <div class="records-page-button-container">
    <button class="records-page-button" @click="goToMenu">Назад</button>
    </div>
    <h1>Таблица лидеров</h1>

    <div v-if="records.length > 0" class="records-list">
      <div class="record-item">
       <h3>Имя:</h3>       <h3>АМАХАСЛА:</h3>  <h3></h3>

      </div>

      <div v-for="record in records" :key="record.ID" class="record-item">
        <span class="record-name">{{ record.babkaname }}</span>
        <span class="record-clicks">{{ record.clicks }}</span>
        <a
            @click.prevent="goToGetMoney"
            target="_blank"
            class="list-btn"
          > 
          </a>
      </div>
      <a
            @click.prevent="goToPensia"
            target="_blank"
            class="list-btn"
          > <h4>Подробности</h4>
          </a>
    </div>
    
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import supabase from '../../services/supabase';
import { useRouter } from 'vue-router';
import router from '@/router';
const records = ref([]);
const goToMenu = () => {
  router.push('/'); // Предполагается, что у вас есть маршрут '/records'
};
const goToPensia = () => {
  router.push('/pensia'); // Предполагается, что у вас есть маршрут '/records'
};
const goToGetMoney = () => {
  router.push('/getmoney'); // Предполагается, что у вас есть маршрут '/records'
};
const loadRecords = async () => {
  try {
    const { data, error } = await supabase
      .from('record')
      .select('*')
      .order('clicks', { ascending: false });

    if (error) {
      throw error;
    }

    console.log('Данные из таблицы record:', data); // Отладочное сообщение
    records.value = data;
  } catch (error) {
    console.error('Ошибка при загрузке данных:', error);
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
  background-color: #414141;
  box-shadow: 0 0 10px rgba(255, 196, 0, 0.7);
  border: solid 1px rgba(255, 196, 0, 0.4);
  border-radius: 10px;


}
h3 {
  margin-bottom: 5px;

  text-shadow: 
    -1px -1px 0 #000, /* Верхний левый контур */
    1px -1px 0 #000,  /* Верхний правый контур */
    -1px 1px 0 #000,  /* Нижний левый контур */
    1px 1px 0 #000;   /* Нижний правый контур */
  color: white;        /* Цвет текста */
}
h1 {
  text-align: center;
  margin-bottom: 5px;
  color: #e0e0e0;

}

a {
  text-align: center;
  margin-bottom: 0;
  gap:20px;
  color: #000000;

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
    -0.7px -0.7px 0 #000, /* Верхний левый контур */
    0.7px -0.7px 0 #000,  /* Верхний правый контур */
    -0.7px 0.7px 0 #000,  /* Нижний левый контур */
    0.7px 0.7px 0 #000;   /* Нижний правый контур */
  color: #ffd000;
  

}

.record-clicks {
  text-shadow: 
    -0.7px -0.7px 0 #000, /* Верхний левый контур */
    0.7px -0.7px 0 #000,  /* Верхний правый контур */
    -0.7px 0.7px 0 #000,  /* Нижний левый контур */
    0.7px 0.7px 0 #000;   /* Нижний правый контур */
  color: #ffffff;

}
.records-page-button {
  width: 100px; /* Ширина кнопки равна ширине контейнера */
  padding: 10px;
  background-color: #3f4b4ea1;
  color: white;
  border: none;
  border-radius: 10px; /* Убираем скругление углов */
  cursor: pointer;
  text-align: center; /* Текст по центру */
}
.records-page-button-container {
  position: fixed;
  top: 0px;
  left: 0px;
}
</style>