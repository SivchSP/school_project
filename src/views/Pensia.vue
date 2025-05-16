<template>
    <div class="records-page-button-container">
    <button class="records-page-button" @click="goToRecordsPage">Назад</button>
    </div>
    <p>АМАХАСЛА - валюта, которую можно получить путём: 
            тапания; 
            заработать, выполнив задание
             или же своровать.</p>
    
</template>
<script setup>
import { useRouter } from 'vue-router';
import { RouterLink } from 'vue-router'

const router = useRouter();

const goToRecordsPage = () => {
  router.push('/records'); // Предполагается, что у вас есть маршрут '/records'
};
</script>
<style scoped>
P {
  text-align: center;
  top: 20px;
  color: #e0e0e0;
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