<template>
  <button class="back-button" @click="goBack">← Назад</button>

  <div class="product-page">
    <h1 class="title">NFT1</h1>
    <img :src="frog1" alt="NFT Лягушка" class="image">
    <div class="product-details">
      <p class="price">15000</p>
      <img :src="frog" alt="Валюта" class="price-image">
    </div>
    <button class="buy-now" @click="showConfirmation">Купить сейчас</button>

    <div v-if="showModal" class="modal-overlay">
      <div class="modal-content">
        <p>Вы точно хотите купить?</p>
        <div class="modal-buttons">
          <button @click="confirmPurchase" class="modal-button yes">Да</button>
          <button @click="hideConfirmation" class="modal-button no">Нет</button>
        </div>
      </div>
    </div>
    
    <div v-if="purchaseMessage" class="purchase-message" :class="{ 'success': purchaseSuccess, 'error': !purchaseSuccess }">
      {{ purchaseMessage }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import frog1 from '@/assets/nft1.png';
import frog from '@/assets/frog1.png';

import { useScoreStore } from '@/stores/score';
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://jgkfvqiophgvswqvatbx.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impna2Z2cWlvcGhndnN3cXZhdGJ4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk4ODI5NTMsImV4cCI6MjA1NTQ1ODk1M30.GTN1V9NJwnmwy8GmXOOz3SxepV7n4yVKkhLYZTYuFEQ';
const supabase = createClient(supabaseUrl, supabaseKey);

const router = useRouter();
const scoreStore = useScoreStore();
const showModal = ref(false);
const purchaseMessage = ref('');
const purchaseSuccess = ref(false);

const goBack = () => {
  router.go(-1);
};

const showConfirmation = () => {
  if (!scoreStore.currentAccount) {
    purchaseMessage.value = 'Для покупки необходимо войти в аккаунт!';
    purchaseSuccess.value = false;
    return;
  }
  
  if (scoreStore.score < 15000) {
    purchaseMessage.value = 'Недостаточно средств для покупки!';
    purchaseSuccess.value = false;
    return;
  }
  
  showModal.value = true;
};

const hideConfirmation = () => {
  showModal.value = false;
};

const confirmPurchase = async () => {
  hideConfirmation();
  
  if (!scoreStore.currentAccount) {
    purchaseMessage.value = 'Для покупки необходимо войти в аккаунт!';
    purchaseSuccess.value = false;
    return;
  }

  try {
    // 1. Получаем текущие данные пользователя
    const { data: userData, error: fetchError } = await supabase
      .from('users')
      .select('nft1, score')
      .eq('name', scoreStore.currentAccount.name)
      .single();

    if (fetchError) throw fetchError;
    if (!userData) throw new Error('Аккаунт не найден');

    // 2. Проверяем достаточно ли средств
    if (userData.score < 15000) {
      purchaseMessage.value = 'Недостаточно средств для покупки!';
      purchaseSuccess.value = false;
      return;
    }

    // 3. Рассчитываем новые значения
    const newNftCount = (userData.nft1 || 0) + 1;
    const newScore = userData.score - 15000;

    // 4. Обновляем данные в базе
    const { error: updateError } = await supabase
      .from('users')
      .update({ 
        nft1: newNftCount,
        score: newScore
      })
      .eq('name', scoreStore.currentAccount.name);

    if (updateError) throw updateError;

    // 5. Обновляем локальное состояние
    scoreStore.setScore(newScore);
    
    purchaseMessage.value = 'Покупка успешно совершена!';
    purchaseSuccess.value = true;
  } catch (error) {
    console.error('Ошибка при покупке:', error);
    purchaseMessage.value = 'Произошла ошибка при покупке. Попробуйте позже.';
    purchaseSuccess.value = false;
  }
};
</script>

<style scoped>
/* Стили остаются без изменений */
.back-button {
  position: absolute;
  top: 10px;
  left: 10px;
  font-size: 16px;
  cursor: pointer;
  padding: 5px;
  background-color: #ffd000;
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  font-weight: bold;
  cursor: pointer;
  margin-top: 10px;
}

.product-page {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  background-color: #ffffff;
  border: 10px;
  gap: 20px;
  margin-top: 10px;
  border-radius: 15px;
  width: 300px;
  position: relative;
}

.title {
  text-align: center;
  margin-bottom: 20px;
  color: #ffd000;
}

.product-details {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  margin: 10px 0;
}

.price-image {
  width: 20px;
  height: 20px;
}

.image {
  width: 180px;
  height: 150px;
  margin: 10px 0;
}

.buy-now {
  background-color: #ffd000;
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  font-weight: bold;
  cursor: pointer;
  margin-top: 10px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 20px;
  border-radius: 10px;
  text-align: center;
  width: 250px;
}

.modal-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 20px;
}

.modal-button {
  padding: 8px 20px;
  border: none;
  border-radius: 5px;
  font-weight: bold;
  cursor: pointer;
}

.modal-button.yes {
  background-color: #4CAF50;
  color: white;
}

.modal-button.no {
  background-color: #f44336;
  color: white;
}

.purchase-message {
  margin-top: 20px;
  padding: 10px;
  border-radius: 5px;
  text-align: center;
  font-weight: bold;
}

.purchase-message.success {
  background-color: #d4edda;
  color: #155724;
}

.purchase-message.error {
  background-color: #f8d7da;
  color: #721c24;
}
</style>