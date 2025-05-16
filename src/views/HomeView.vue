<template>
  <div class="back-ground">
  <div class="page-wrapper">
    <!-- Прогресс-бар -->
    <div class="top-progress-bar">
      <h4 class="progress-level">
        <span class="pidr">{{ userTitle }} 
          <button class="info-button" @click.stop="showModal = true">></button>
        </span>
        <span >Level {{ store.level.level + 1 }}</span>
      </h4>
      <div class="progress-container">
        <div class="progress-value" :style="{ width: progress + '%' }"></div>
      </div>
    </div>
    <div class="game-container">
      <div class="header">
        <img src="../assets/coin.png" alt="coin" />
        <h2 class="score">{{ store.score }}</h2>
      </div>
      <div class="circle-container" ref="container">
        <img 
          ref="clickableImg" 
          class="clickable-image" 
          :src="imgSrc" 
          @click="handleClick"
        />
        <transition name="plus-one">
          <div v-if="showPlusOne" class="plus-one-animation" :style="animationStyle">+{{ clickValue }}</div>
        </transition>
      </div>
      <div class="boost-container" @click="goToClicksPage">
        <img class="boost-icon" :src="raketa" alt="Boost" />
        <span class="boost-text">Energy</span>
      </div>
      <div class="clicks-container" @click="goToBoostPage">
        <img class="clicks-icon" :src="lighting" alt="Clicks" />
        <span class="clicks-text">Boost</span>
      </div>
      <ProgressBar ref="progressBar" />
    </div>

    <!-- Модальное окно -->
    <transition name="modal">
      <div v-if="showModal" class="modal-overlay" @click="showModal = false">
        <div class="modal-content" @click.stop>
          <div class="modal-score">
            <span>До нового уровня: {{ store.level.value - store.currentScore}}  </span>
          </div>
          <button class="modal-close" @click="showModal = false">×</button>
        </div>
      </div>
    </transition>

    <!-- Boost Page Modal -->
    <transition name="modal">
      <div v-if="showBoostPage" class="modal-overlay" @click="showBoostPage = false">
        <div class="boost-page" @click.stop>
          <h2>Boost Packages</h2>
          <div class="boost-packages">
            <div 
              v-for="(pack, index) in boostPackages" 
              :key="index" 
              class="boost-package"
              @click="purchaseBoost(pack)"
              :class="{ 
                'disabled': store.score < pack.price || purchasedBoosts[pack.field],
                'purchased': purchasedBoosts[pack.field]
              }"
            >
              <h3>+{{ pack.value }} per click</h3>
              <p v-if="!purchasedBoosts[pack.field]">Price: {{ pack.price }}</p>
              <p v-else>Purchased</p>
            </div>
          </div>
          <button class="modal-close" @click="showBoostPage = false">×</button>
        </div>
      </div>
    </transition>
  
    <!-- Energy Page Modal -->
    <transition name="modal">
      <div v-if="showEnergyPage" class="modal-overlay" @click="showEnergyPage = false">
        <div class="energy-page" @click.stop>
          <h2>Bitcoin Trading</h2>
          <div class="trading-container">
            <div class="chart-container">
              <div v-if="loading" class="loading-chart">Loading chart...</div>
              <div v-else id="btc-chart" ref="btcChart"></div>
            </div>
            
            <div class="price-info">
              <div class="current-price">
                <span>Current Price: ${{ formatNumber(currentPrice) }}</span>
                <span :class="{'price-up': priceChange >= 0, 'price-down': priceChange < 0}">
                  ({{ priceChange >= 0 ? '+' : '' }}{{ priceChange.toFixed(2) }}%)
                </span>
              </div>
              <div class="position-info" v-if="activePosition">
                <p>Position: {{ activePosition.type }} @ ${{ formatNumber(activePosition.entryPrice) }}</p>
                <p>P/L: <span :class="{'profit': currentPL >= 0, 'loss': currentPL < 0}">
                  ${{ formatNumber(Math.abs(currentPL)) }} ({{ positionROI >= 0 ? '+' : '' }}{{ positionROI.toFixed(2) }}%)
                </span></p>
              </div>
            </div>
            
            <div class="trade-buttons">
              <button 
                class="trade-button long" 
                @click="openPosition('long')"
                :disabled="!!activePosition"
              >
                LONG
              </button>
              <button 
                class="trade-button short" 
                @click="openPosition('short')"
                :disabled="!!activePosition"
              >
                SHORT
              </button>
              <button 
                class="trade-button close" 
                @click="closePosition"
                :disabled="!activePosition"
              >
                CLOSE
              </button>
            </div>
          </div>
          <button class="modal-close" @click="showEnergyPage = false">×</button>
        </div>
      </div>
    </transition>
  </div>
</div>
</template>

<script setup>
import { onMounted, ref, computed, watch, onBeforeUnmount } from 'vue';
import { createChart, CrosshairMode } from 'lightweight-charts';
import ProgressBar from '@/components/DelayForClick.vue';
import { useScoreStore } from '@/stores/score';
import frog1 from '@/assets/frog1.png';
import raketa from '@/assets/raketa.png';
import lighting from '@/assets/lighting.png';
import { getUserByName } from '../../api/app';
import supabase from '../../services/supabase';

const showEnergyPage = ref(false);
const loading = ref(true);
const currentPrice = ref(0);
const priceChange = ref(0);
const activePosition = ref(null);
const currentPL = ref(0);
const positionROI = ref(0);
const priceUpdateInterval = ref(null);
const chart = ref(null);
const btcChart = ref(null);

const goToClicksPage = () => {
  showEnergyPage.value = true;
  initChart();
  startPriceUpdates();
};

const formatNumber = (num) => {
  return num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

const initChart = async () => {
  if (!btcChart.value) return;
  
  try {
    // Создаем график
    chart.value = createChart(btcChart.value, {
      width: btcChart.value.clientWidth,
      height: 300,
      layout: {
        backgroundColor: '#1a1a1a',
        textColor: '#d9d9d9',
      },
      grid: {
        vertLines: {
          color: '#2B2B43',
        },
        horzLines: {
          color: '#2B2B43',
        },
      },
      crosshair: {
        mode: CrosshairMode.Normal,
      },
      rightPriceScale: {
        borderColor: '#2B2B43',
      },
      timeScale: {
        borderColor: '#2B2B43',
      },
    });

    // Добавляем свечной график
    const candleSeries = chart.value.addCandlestickSeries({
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderVisible: false,
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
    });

    // Получаем исторические данные (заглушка)
    const historicalData = await fetchHistoricalData();
    candleSeries.setData(historicalData);
    
    // Добавляем линию текущей цены
    const lineSeries = chart.value.addLineSeries({
      color: 'rgba(255, 196, 0, 0.5)',
      lineWidth: 2,
    });
    
    lineSeries.setData([{ time: historicalData[historicalData.length-1].time, value: historicalData[historicalData.length-1].close }]);
    
    loading.value = false;
  } catch (error) {
    console.error('Error initializing chart:', error);
    loading.value = false;
  }
};

const fetchHistoricalData = async () => {
  // В реальном приложении здесь должен быть запрос к API
  // Это заглушка с фейковыми данными
  const now = Math.floor(Date.now() / 1000);
  const data = [];
  
  for (let i = 30; i >= 0; i--) {
    const time = now - i * 86400;
    const open = 50000 + Math.random() * 5000;
    const high = open + Math.random() * 1000;
    const low = open - Math.random() * 1000;
    const close = low + Math.random() * (high - low);
    
    data.push({
      time,
      open,
      high,
      low,
      close,
    });
  }
  
  return data;
};

const startPriceUpdates = () => {
  // Останавливаем предыдущий интервал, если он есть
  if (priceUpdateInterval.value) {
    clearInterval(priceUpdateInterval.value);
  }
  
  // В реальном приложении здесь должен быть WebSocket или API запрос
  // Это имитация обновления цены
  currentPrice.value = 55000 + Math.random() * 5000;
  priceUpdateInterval.value = setInterval(() => {
    const change = (Math.random() - 0.5) * 1000;
    const newPrice = currentPrice.value + change;
    priceChange.value = ((newPrice - currentPrice.value) / currentPrice.value) * 100;
    currentPrice.value = newPrice;
    
    // Обновляем P/L если есть открытая позиция
    if (activePosition.value) {
      updatePositionPL();
    }
  }, 3000);
};

const openPosition = (type) => {
  activePosition.value = {
    type,
    entryPrice: currentPrice.value,
    entryTime: new Date().toISOString(),
  };
  updatePositionPL();
};

const closePosition = async () => {
  if (!activePosition.value) return;
  
  // Рассчитываем прибыль/убыток
  const profit = currentPL.value;
  
  // Если прибыль >= $25, обновляем available_clicks
  if (profit >= 25) {
    try {
      const { data, error } = await supabase
        .from('users')
        .update({ available_clicks: 5000 })
        .eq('name', store.currentAccount.name);
        
      if (error) throw error;
      
      console.log('Successfully updated available_clicks to 5000');
    } catch (error) {
      console.error('Error updating available_clicks:', error);
    }
  }
  
  // Закрываем позицию
  activePosition.value = null;
  currentPL.value = 0;
  positionROI.value = 0;
};

const updatePositionPL = () => {
  if (!activePosition.value) return;
  
  if (activePosition.value.type === 'long') {
    currentPL.value = currentPrice.value - activePosition.value.entryPrice;
  } else {
    currentPL.value = activePosition.value.entryPrice - currentPrice.value;
  }
  
  positionROI.value = (currentPL.value / activePosition.value.entryPrice) * 100;
};

onBeforeUnmount(() => {
  if (priceUpdateInterval.value) {
    clearInterval(priceUpdateInterval.value);
  }
  
  if (chart.value) {
    chart.value.remove();
    chart.value = null;
  }
});

const store = useScoreStore();  
const progressBar = ref(null);
const clickableImg = ref(null);
const container = ref(null);
const imgSrc = frog1;
const progress = computed(() => (100 * store.currentScore) / store.level.value);
const showModal = ref(false);
const showBoostPage = ref(false);
const clickValue = ref(1 + store.boost);

// Объект для отслеживания купленных пакетов
const purchasedBoosts = ref({
  boost_1: false,
  boost_2: false,
  boost_3: false,
  boost_4: false,
  boost_5: false
});

const userTitle = ref("Bum");
const titles = [
  { threshold: 0, name: "Bum Hustler" },
  { threshold: 25, name: "Penniless Hustler" },
  { threshold: 100, name: "Beggar Hustler" },
  { threshold: 500, name: "Poor Hustler" },
  { threshold: 2000, name: "Struggling Hustler" },
  { threshold: 10000, name: "Average Hustler" },
  { threshold: 50000, name: "Comfortable Hustler" },
  { threshold: 200000, name: "Wealthy Hustler" },
  { threshold: 1000000, name: "Rich Hustler" },
  { threshold: 5000000, name: "Millionaire Hustler" },
  { threshold: 20000000, name: "Multi-Millionaire Hustler" },
  { threshold: 100000000, name: "Billionaire Hustler" },
  { threshold: 500000000, name: "Tycoon Hustler" },
  { threshold: 2000000000, name: "Magnate Hustler" },
  { threshold: Infinity, name: "Ultra Magnate Hustler" }
];

const boostPackages = [
  { price: 5000, value: 1, field: 'boost_1' },
  { price: 10000, value: 2, field: 'boost_2' },
  { price: 20000, value: 3, field: 'boost_3' },
  { price: 50000, value: 4, field: 'boost_4' },
  { price: 100000, value: 5, field: 'boost_5' }
  
];

const updateTitle = () => {
  const currentScore = store.currentScore;
  let newTitle = "Bum";
  for (let i = titles.length - 1; i >= 0; i--) {
    if (currentScore >= titles[i].threshold) {
      newTitle = titles[i].name;
      break;
    }
  }
  userTitle.value = newTitle;
};

watch(() => store.currentScore, updateTitle, { immediate: true });
watch(() => store.boost, (newBoost) => {
  clickValue.value = 1 + newBoost;
});

const showPlusOne = ref(false);
const animationStyle = ref({
  left: '0px',
  top: '0px'
});

const handleClick = (event) => {
  if (!progressBar.value.useClick()) return;
  
  store.add(clickValue.value);
  event.preventDefault();
  
  animateTilt(event);
  showPlusOneAtPosition(event);
};

const animateTilt = (event) => {
  const rect = clickableImg.value.getBoundingClientRect();
  const offsetX = event.clientX - rect.left - rect.width / 2;
  const offsetY = event.clientY - rect.top - rect.height / 2;
  const tiltX = (offsetY / rect.height) * 40;
  const tiltY = (offsetX / rect.width) * -40;

  clickableImg.value.style.transform = `rotateX(${tiltX}deg) rotateY(${tiltY}deg)`;
  
  setTimeout(() => {
    clickableImg.value.style.transform = 'rotateX(0deg) rotateY(0deg)';
  }, 300);
};

const showPlusOneAtPosition = (event) => {
  const containerRect = container.value.getBoundingClientRect();
  const clickX = event.clientX - containerRect.left;
  const clickY = event.clientY - containerRect.top;

  animationStyle.value = {
    left: `${clickX}px`,
    top: `${clickY - 20}px`
  };
  
  showPlusOne.value = true;
  setTimeout(() => showPlusOne.value = false, 800);
};

const goToBoostPage = () => {
  showBoostPage.value = true;
};

const purchaseBoost = async (pack) => {
  // Проверяем, что пакет еще не куплен
  if (purchasedBoosts.value[pack.field]) {
    console.log('Этот пакет уже куплен');
    return;
  }

  // Проверяем, что у пользователя достаточно средств
  if (store.score < pack.price) {
    console.log('Недостаточно средств');
    return;
  }

  // Сохраняем исходные значения для возможного отката
  const originalScore = store.score;
  const originalBoost = store.boost;
  const originalClickValue = clickValue.value;

  try {
    // Обновляем локальное состояние
    store.score -= pack.price;
    store.boost += pack.value;
    clickValue.value = 1 + store.boost;
    purchasedBoosts.value[pack.field] = true;

    // Обновляем данные в базе
    const { data, error } = await supabase
      .from('users')
      .update({
        score: store.score,
        boost: store.boost,
        [pack.field]: true
      })
      .eq('name', store.currentAccount.name);

    if (error) {
      throw error;
    }

    console.log('Пакет успешно куплен');

  } catch (error) {
    // Откатываем изменения при ошибке
    store.score = originalScore;
    store.boost = originalBoost;
    clickValue.value = originalClickValue;
    purchasedBoosts.value[pack.field] = false;
    
    console.error('Ошибка при покупке пакета:', error.message);
    // Здесь можно добавить уведомление для пользователя
    alert('Произошла ошибка при покупке пакета. Пожалуйста, попробуйте позже.');
  }
};

onMounted(async () => {
  if (store.currentAccount?.name) {
    const userData = await getUserByName(store.currentAccount.name);
    store.setCurrentAccount(userData);
    clickValue.value = 1 + (userData.boost || 0);
    
    // Загружаем информацию о купленных пакетах
    if (userData) {
      // Инициализируем все поля как false
      const initialBoosts = {
        boost_1: false,
        boost_2: false,
        boost_3: false,
        boost_4: false,
        boost_5: false
        
      };

      // Обновляем значения из базы данных
      for (const key in initialBoosts) {
        if (userData[key] !== undefined) {
          purchasedBoosts.value[key] = userData[key];
        }
      }
    }
  }
});


</script>
<style scoped>
.pidr{
  color: #ffc400;
}
.energy-page {
  position: relative;
  background-color: #3b3b3b;
  border-radius: 10px;
  padding: 20px;
  max-width: 800px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  color: rgb(255, 187, 0);
  box-shadow: 0 0 10px rgba(255, 196, 0, 0.5);
  border: 2px solid #ffc400;
  animation: slideUpFadeIn 0.3s ease-out forwards;
  opacity: 0;
}
.score{
  font-family: 'Inter', sans-serif;
  font-weight: 600;
}
.trading-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.chart-container {
  height: 300px;
  background-color: #1a1a1a;
  border-radius: 8px;
  position: relative;
}

#btc-chart {
  width: 100%;
  height: 100%;
}

.loading-chart {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #ffc400;
}

.price-info {
  display: flex;
  justify-content: space-between;
  background-color: #2a2a2a;
  padding: 10px 15px;
  border-radius: 8px;
}

.current-price {
  font-size: 18px;
  font-weight: bold;
}

.price-up {
  color: #26a69a;
}

.price-down {
  color: #ef5350;
}

.position-info {
  text-align: right;
  font-size: 14px;
}

.profit {
  color: #26a69a;
}

.loss {
  color: #ef5350;
}

.trade-buttons {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.trade-button {
  padding: 12px 25px;
  border: none;
  border-radius: 6px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 16px;
}

.trade-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.trade-button.long {
  background-color: #26a69a;
  color: white;
}

.trade-button.long:not(:disabled):hover {
  background-color: #1d887e;
}

.trade-button.short {
  background-color: #ef5350;
  color: white;
}

.trade-button.short:not(:disabled):hover {
  background-color: #d84340;
}

.trade-button.close {
  background-color: #ffc400;
  color: #333;
}

.trade-button.close:not(:disabled):hover {
  background-color: #e6b000;
}

@media (max-width: 600px) {
  .trade-buttons {
    flex-direction: column;
  }
  
  .price-info {
    flex-direction: column;
    gap: 8px;
  }
  
  .position-info {
    text-align: left;
  }
}
.boost-package.purchased {
  background-color: #4CAF50; /* Зелёный цвет для купленных */
  cursor: not-allowed;
}

.boost-package.disabled:not(.purchased) {
  background-color: #f44336; /* Красный цвет для недоступных */
  cursor: not-allowed;
}
.account-selector {
  margin-left: 20px;
}

.account-selector select {
  padding: 5px;
  border-radius: 5px;
  border: 1px solid #ccc;
  background-color: #fff;
  color: #333;
}
.clicks-container {
  position: absolute;
  left: 20px;
  bottom: 60px;
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: transform 0.2s;
}
.clicks-icon {
  width: 23px;
  height: 23px;
  margin-right: 1px;
}
.clicks-text {
  font-size: 18px;
  font-weight: bold;
  color: #ffc400;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
  font-style: italic;
  font-family: 'Inter', sans-serif;
  font-weight: 600;

}
.boost-container {
  position: absolute;
  right: 20px;
  bottom: 55px;
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: transform 0.2s;
}

.boost-container:hover {
  transform: scale(1.1);
}

.boost-icon {
  width: 24px;
  height: 32px;
  margin-right: 1px;
}

.boost-text {
  font-size: 18px;
  font-weight: bold;
  color: #9f7aca;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
  font-style: italic;
  font-family: 'Inter', sans-serif;
  font-weight: 600;

}

.boost-page {
  position: relative;
  background-color: #3b3b3b;
  border-radius: 10px;
  padding: 20px;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  color: rgb(255, 187, 0);
  box-shadow: 0 0 10px rgba(255, 196, 0, 0.5);
  border: 2px solid #ffc400;
  
  /* Анимация появления */
  animation: slideUpFadeIn 0.3s ease-out forwards;
  opacity: 0; /* Начальное состояние (прозрачность 0) */
}
@keyframes slideUpFadeIn {
  from {
    opacity: 0;
    transform: translateY(50px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.boost-packages {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  margin-top: 20px;
}

.boost-package {
  background-color: #303030;
  border-radius: 8px;
  padding: 15px;
  cursor: pointer;
  transition: transform 0.2s, background-color 0.2s;
}

.boost-package:hover {
  transform: scale(1.05);
}

.boost-package.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.boost-package h3 {
  color: #ffcc00;
  margin-bottom: 5px;
}

.boost-package p {
  color: #ddd;
}

.modal-close {
  position: absolute;
  top: 10px;
  right: 10px;
  background: none;
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
}

.plus-one-animation {
  position: absolute;
  color: #ffcc00;
  font-size: 24px;
  font-weight: bold;
  pointer-events: none;
  z-index: 10;
  animation: float-up 0.8s ease-out forwards;
}

@keyframes float-up {
  0% {
    opacity: 1;
    transform: translateY(0);
  }
  100% {
    opacity: 0;
    transform: translateY(-50px);
  }
}
.top-progress-bar {
  width: 80%;
  margin: 0 auto;
  padding-bottom: 10px;
  position: relative;
  top: 17vh;
}

.progress-container {
  height: 11px;
  background-color: #333;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.progress-value {
  height: 100%;
  background-color: #ffc400;
  border-radius: 10px;
  transition: width 0.3s ease;
}

.progress-level {
  display: flex;
  justify-content: space-between;
  margin: 5px 0;
  color: white;
  font-size: 14px;
  font-family: 'Inter', sans-serif;
  font-weight: 550;
}

.info-button {
  background: none;
  border: none;
  color: white;
  font-size: 16px;
  cursor: pointer;
  margin-left: 8px;  /* Увеличил отступ */
  padding: 6px 10px; /* Увеличил внутренние отступы */
  min-width: 24px;   /* Минимальная ширина */
  min-height: 24px;  /* Минимальная высота */
  display: inline-flex;
  align-items: center;
  justify-content: center;
  position: relative;
  border-radius: 4px; /* Скругление углов */
  transition: all 0.2s ease;
  color: #ffc400;

  
}

.info-button:hover {
  color: #ffc400;
  background-color: rgba(255, 196, 0, 0.1); /* Легкий фон при наведении */
  
}

/* Убедимся, что родительские элементы не обрезают кнопку */
.progress-level {
  display: flex;
  justify-content: space-between;
  margin: 5px 0;
  color: white;
  font-size: 14px;
  align-items: center;
  padding: 2px 0; /* Добавим немного отступа сверху/снизу */
}

.back-ground {
 background-color: #1f1f1f;
 border-radius: 0px;
 width: 500px;
 height: 1000px;

}
.page-wrapper {
  position: fixed;
  left: -2px;
  right: 0;
  height: 70vh;
  bottom: 20px ;
  width: calc(100% + 4px);
  background-color: rgb(41, 41, 41);
  border-radius: 30px 30px 0 0;
  overflow: hidden;
  z-index: 10;
  box-shadow: 0 -5px 15px rgba(255, 196, 0, 0.534);
  border: 2px solid #ffc400;

}

.game-container {
  width: 100%;
  height: calc(100%);
  margin-top: -50px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.header {
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.circle-container {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding-bottom: 20px;
  position: relative;
  -webkit-tap-highlight-color: transparent;
  outline: none;
}

.clickable-image {
  width: 300px;
  height: 300px;
  object-fit: contain;
  cursor: pointer;
  transition: transform 0.3s ease;
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
}

.plus-one-animation {
  position: absolute;
  font-size: 24px;
  font-weight: bold;
  color: rgb(255, 166, 0);
  -webkit-text-stroke: 0.3px black;
  user-select: none;
  pointer-events: none;
  animation: floatUp 1s ease-out;
}

/* Стили для модального окна */
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
  z-index: 100;
}

.modal-content {
  background-color: rgb(41, 41, 41);
  padding: 30px;
  border-radius: 15px;
  width: 80%;
  max-width: 300px;
  position: relative;
  box-shadow: 0 0 20px rgba(255, 196, 0, 0.5);
  border: 1px solid #ffc400;
  animation: slideUpFadeIn 0.3s ease-out forwards;
  opacity: 0; /* Начальное состояние (прозрачность 0) */
}

.modal-score {
  color: white;
  font-size: 18px;
  text-align: center;
  margin-bottom: 20px;
}

.modal-close {
  position: absolute;
  top: 10px;
  right: 10px;
  background: none;
  border: none;
  color: white;
  font-size: 20px;
  cursor: pointer;
}

.modal-close:hover {
  color: #ffc400;
}

/* Анимации */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

@keyframes floatUp {
  0% {
    transform: translate(-50%, -50%);
    opacity: 1;
  }
  100% {
    transform: translate(-50%, -150%);
    opacity: 0;
  }
}

@media (max-width: 768px) {
  .page-wrapper {
    height: 80vh;
  }
  
  .clickable-image {
    width: 35vh;
    height: 35vh;
  }
}
</style>