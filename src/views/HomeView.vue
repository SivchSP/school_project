<template>
  <div class="back-ground">
    <div class="page-wrapper">
      <div class="progress-bar-container">
        <div class="progress-bar">
          <div class="progress-valueperchik" :style="{ width: progress1 + '%' }"></div>
        </div>
        <div class="progress-info">
          <h4 class="progress-level">
            <span>Clicks</span>
            <span>{{ availableClicks }} / {{ maxClicks }}</span>
          </h4>
        </div>
      </div>
      <div class="game-container">
        <div class="header-wrapper">
          <div class="header">
            <img class="gift_icon" src="../assets/gift_icon.png" alt="coin" />
            <h2 class="score" ref="scoreElement">{{ formatScore(store.score) }}</h2>
          </div>
        </div>
          
        <div class="circle-container" ref="container">
          <img 
            ref="clickableImg" 
            class="clickable-image" 
            :src="imgSrc" 
            @click="handleClick"
          />
          <transition name="plus-one">
            <div v-if="showPlusOne" class="plus-one-animation" :style="animationStyle">
              <span class="plus-text">+{{ clickValue }}</span>
              <img class="gift-fly" src="@/assets/gift_fly.png" alt="Gift" />
            </div>
          </transition>
        </div>
        
        <div class="boost-container" @click="showFinanceSimulator = true">
          <img class="boost-icon" src="@/assets/coin.png" alt="Finance" />
          <span class="boost-text">Finance</span>
        </div>
        
        <div class="clicks-container" @click="goToBoostPage">
          <img class="clicks-icon" src="@/assets/raketa.png" alt="Clicks" />
          <span class="clicks-text">Boost</span>
        </div>
        
        <ProgressBar ref="progressBar" />
      </div>
      
      <!-- Boost Page Modal -->
      <transition name="modal">
        <div v-if="showBoostPage" class="modal-overlay" @click="showBoostPage = false">
          <div class="boost-page-modern" @click.stop>
            <!-- Заголовок с иконкой -->
            <div class="boost-header">
              <div class="boost-title-section">
                <img class="boost-header-icon" src="@/assets/raketa.png" alt="Boost" />
                <div>
                  <h2>Boost Packages</h2>
                  <p class="boost-subtitle">Enhance your clicking power</p>
                </div>
              </div>
              <div class="boost-balance">
                <span class="balance-label">Your Balance</span>
                <span class="balance-amount">{{ formatScore(store.score) }}</span>
              </div>
            </div>

            <!-- Прогресс бустов -->
            <div class="boost-progress">
              <div class="progress-info">
                <span class="progress-label">Current Boost Level</span>
              </div>
              <div class="progress-bar-modern">
                <div class="progress-fill" :style="{ width: boostProgress + '%' }"></div>
              </div>
            </div>

            <!-- Сетка бустов -->
            <div class="boost-grid">
              <div 
                v-for="(pack, index) in boostPackages" 
                :key="index" 
                class="boost-card"
                :class="{ 
                  'disabled': store.score < pack.price || purchasedBoosts[pack.field],
                  'purchased': purchasedBoosts[pack.field],
                  'next-upgrade': !purchasedBoosts[pack.field] && isNextUpgrade(index)
                }"
                @click="purchaseBoost(pack)"
              >
                <!-- Бейдж статуса -->
                <div class="boost-badge" v-if="purchasedBoosts[pack.field]">
                  <span>✓ Owned</span>
                </div>
                
                <div class="boost-card-content">
                  <!-- Иконка и значение -->
                  <div class="boost-icon-section">
                    <div class="boost-value-circle">
                      <span class="boost-value">+{{ pack.value }}</span>
                      <img class="boost-mini-icon" src="@/assets/raketa.png" alt="Boost" />
                    </div>
                  </div>

                  <!-- Информация о бусте -->
                  <div class="boost-info">
                    <h3 class="boost-name">Level {{ index + 1 }} Boost</h3>
                    <p class="boost-description">+{{ pack.value }} click power</p>
                    
                    <!-- Цена или статус -->
                    <div class="boost-price-section" v-if="!purchasedBoosts[pack.field]">
                      <span class="boost-price">{{ formatScore(pack.price) }}</span>
                      <img class="coin-icon" src="@/assets/coin.png" alt="Coins" />
                    </div>
                    <div class="boost-owned" v-else>
                      <span>Activated</span>
                    </div>
                  </div>

                  <!-- Эффект следующего апгрейда -->
                  <div class="next-upgrade-indicator" v-if="!purchasedBoosts[pack.field] && isNextUpgrade(index)">
                    <span>Next Upgrade</span>
                  </div>
                </div>

                <!-- Состояние недоступности -->
                <div class="unavailable-overlay" v-if="store.score < pack.price && !purchasedBoosts[pack.field]">
                  <span>Need {{ formatScore(pack.price - store.score) }} more</span>
                </div>
              </div>
            </div>

            <!-- Статистика бустов -->
            <div class="boost-stats">
              <div class="stat-item">
                <span class="stat-label">Total Boost</span>
                <span class="stat-value">+{{ store.boost }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">Click Value</span>
                <span class="stat-value">{{ formatScore(clickValue) }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">Packages Owned</span>
                <span class="stat-value">{{ ownedBoostsCount }}/{{ boostPackages.length }}</span>
              </div>
            </div>

            <button class="modal-close-modern" @click="showBoostPage = false">
              <span>×</span>
            </button>
          </div>
        </div>
      </transition>
      
      <!-- Finance Simulator Modal -->
      <transition name="modal">
        <div v-if="showFinanceSimulator" class="modal-overlay" @click="showFinanceSimulator = false">
          <div class="finance-simulator-wrapper">
            <!-- Серая накладка, которая прикреплена к скроллящему контенту -->
            <div class="simulator-block-overlay-sticky">
              <!-- Блокирующая накладка, которая всегда покрывает видимую область -->
            </div>
            
            <div class="finance-simulator" @click.stop>
              <div class="simulator-header">
                <h2>Finance Market</h2>
                <p class="subtitle">Buy promo codes and income cards</p>
              </div>
              
              <div class="tabs">
                <button 
                  v-for="tab in tabs" 
                  :key="tab.id"
                  :class="{ active: activeTab === tab.id }"
                  @click.prevent=""
                  :disabled="true"
                >
                  <img :src="tab.icon" :alt="tab.name" class="tab-icon" />
                  {{ tab.name }}
                </button>
              </div>
              
              <!-- Promo Codes Tab -->
              <div v-if="activeTab === 'promo'" class="stock-tab">
                <div class="debug-info" v-if="promoItems.length === 0">
                  <p>Debug: No promo items to display</p>
                  <p>Total stock items: {{ stockItems.length }}</p>
                  <p>Promo items computed: {{ promoItems.length }}</p>
                </div>
                
                <div class="stock-items">
                  <div 
                    v-for="item in promoItems" 
                    :key="item.id"
                    class="stock-item blocked"
                    :class="{ 
                      'disabled': store.score < item.price || item.remaining_activations <= 0 || isItemPurchased(item.id),
                      'purchased': isItemPurchased(item.id)
                    }"
                    @click.prevent=""
                  >
                    <div class="item-header">
                      <h3>{{ item.name }}</h3>
                      <span class="item-price">{{ item.price }} coins</span>
                    </div>
                    <p class="item-description">{{ item.description }}</p>
                    <div class="item-details">
                      <div class="detail">
                        <span class="label">Value:</span>
                        <span class="value">{{ formatSaleValue(item.sale_value) }}</span>
                      </div>
                      <div class="detail">
                        <span class="label">Activations left:</span>
                        <span class="value">{{ item.remaining_activations }}/{{ item.total_activations }}</span>
                      </div>
                      <div class="detail">
                        <span class="label">Valid until:</span>
                        <span class="value">{{ formatDate(item.valid_until) }}</span>
                      </div>
                    </div>
                    <div class="item-status">
                      <span v-if="isItemPurchased(item.id)" class="purchased-badge">Purchased</span>
                      <span v-else-if="item.remaining_activations <= 0" class="sold-out-badge">Sold Out</span>
                      <span v-else-if="store.score < item.price" class="insufficient-funds">Not enough coins</span>
                      <span v-else class="available-badge">Available</span>
                    </div>
                  </div>
                </div>
                
                <div v-if="promoItems.length === 0" class="no-items">
                  <p>No promo codes available at the moment</p>
                </div>
              </div>

              <!-- Income Cards Tab -->
              <div v-if="activeTab === 'income'" class="stock-tab">
                <div class="debug-info" v-if="incomeItems.length === 0">
                  <p>Debug: No income items to display</p>
                  <p>Total stock items: {{ stockItems.length }}</p>
                  <p>Income items computed: {{ incomeItems.length }}</p>
                </div>
                
                <div class="stock-items">
                  <div 
                    v-for="item in incomeItems" 
                    :key="item.id"
                    class="stock-item blocked"
                    :class="{ 
                      'disabled': store.score < item.price || item.remaining_activations <= 0 || isItemPurchased(item.id),
                      'purchased': isItemPurchased(item.id)
                    }"
                    @click.prevent=""
                  >
                    <div class="item-header">
                      <h3>{{ item.name }}</h3>
                      <span class="item-price">{{ item.price }} coins</span>
                    </div>
                    <p class="item-description">{{ item.description }}</p>
                    <div class="item-details">
                      <div class="detail">
                        <span class="label">Income:</span>
                        <span class="value">+{{ getIncomeValue(item.sale_value) }}/sec</span>
                      </div>
                      <div class="detail">
                        <span class="label">Activations left:</span>
                        <span class="value">{{ item.remaining_activations }}/{{ item.total_activations }}</span>
                      </div>
                      <div class="detail">
                        <span class="label">Valid until:</span>
                        <span class="value">{{ formatDate(item.valid_until) }}</span>
                      </div>
                    </div>
                    <div class="item-status">
                      <span v-if="isItemPurchased(item.id)" class="purchased-badge">Purchased</span>
                      <span v-else-if="item.remaining_activations <= 0" class="sold-out-badge">Sold Out</span>
                      <span v-else-if="store.score < item.price" class="insufficient-funds">Not enough coins</span>
                      <span v-else class="available-badge">Available</span>
                    </div>
                  </div>
                </div>
                
                <div v-if="incomeItems.length === 0" class="no-items">
                  <p>No income cards available at the moment</p>
                </div>
              </div>
              
              <button class="modal-close" @click="showFinanceSimulator = false">×</button>
            </div>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue';
import { Chart, registerables } from 'chart.js';
import ProgressBar from '@/components/DelayForClick.vue';
import { useScoreStore } from '@/stores/score';
import frog1 from '@/assets/drops_coin.png';
import bonus_ticket from '@/assets/bonus_ticket.png';
import promocode from '@/assets/Promocode.png';
import lighting from '@/assets/7level.png';
import supabase from '../../services/supabase';
import { subscribeToChannel, unsubscribeFromChannel } from '/subscriptions';

// Инициализация Chart.js
Chart.register(...registerables);

const store = useScoreStore();
const progressBar = ref(null);
const clickableImg = ref(null);
const container = ref(null);
const imgSrc = frog1;
const progress = computed(() => (100 * store.currentScore) / store.level.value);
const showModal = ref(false);
const showBoostPage = ref(false);
const clickValue = computed(() => store.clickValue);

// Финансовый симулятор - акции
const showFinanceSimulator = ref(false);
const activeTab = ref('promo');
const stockItems = ref([]);
const userData = ref(null);

// Обновите массив tabs в секции script
const tabs = [
  { id: 'promo', name: 'Promo Codes', icon: promocode },
  { id: 'income', name: 'Income Cards', icon: bonus_ticket }
];

const loadUserData = async () => {
  if (!store.currentAccount?.name) return;

  try {
    const { data, error } = await supabase
      .from('users')
      .select('*')
      .eq('name', store.currentAccount.name)
      .single();
      
    if (data) {
      // ДОБАВЛЕНО: Расчет и применение пассивного дохода (как progress-bar)
      const offlineIncome = store.calculateOfflinePassiveIncome(data);
      if (offlineIncome > 0) {
        const newScore = data.score + offlineIncome;
        
        // Обновляем счет в базе
        const { error: updateError } = await supabase
          .from('users')
          .update({ 
            score: newScore,
            last_passive_income_update: new Date().toISOString()
          })
          .eq('name', store.currentAccount.name);
          
        if (!updateError) {
          data.score = newScore;
          store.score = newScore;
          console.log(`✅ Applied offline passive income: +${offlineIncome} coins`);
        }
      }

      userData.value = data;

      // Восстанавливаем клики с учётом прошедшего времени (как progress-bar)
      const lastUpdate = new Date(data.last_click_update || new Date());
      const now = new Date();
      const secondsPassed = Math.floor((now - lastUpdate) / 1000);

      const newClicks = Math.min(
        maxClicks,
        (data.available_clicks || maxClicks) + secondsPassed
      );

      availableClicks.value = newClicks;

      // Обновляем время последнего обновления
      await supabase
        .from('users')
        .update({ 
          available_clicks: newClicks,
          last_click_update: now.toISOString() 
        })
        .eq('name', store.currentAccount.name);
    } else if (error) {
      console.error('Ошибка загрузки данных:', error);
    }
  } catch (error) {
    console.error('Error loading user data:', error);
  }
};

// Временное исправление - нормализация item_type
const normalizeStockItems = (items) => {
  return items.map(item => {
    let normalizedType = item.item_type;
    
    // Приводим к нижнему регистру и убираем пробелы
    if (item.item_type) {
      const cleanType = item.item_type.toString().toLowerCase().trim();
      
      if (cleanType.includes('promo') || cleanType === 'promo') {
        normalizedType = 'promo';
      } else if (cleanType.includes('income') || cleanType.includes('card') || cleanType === 'income_card') {
        normalizedType = 'income_card';
      }
    }
    
    return {
      ...item,
      item_type: normalizedType
    };
  });
};

// Улучшенная версия с обработкой краевых случаев
const formatScore = (score) => {
  if (score === null || score === undefined || score === '') return '0';
  
  const num = Number(score);
  if (isNaN(num)) return '0';
  if (num === 0) return '0';

  const absNum = Math.abs(num);
  const sign = num < 0 ? '-' : '';

  if (absNum >= 1000000000) {
    const value = absNum / 1000000000;
    // Для целых чисел убираем .0
    if (value % 1 === 0) {
      return sign + value.toFixed(0) + 'b';
    }
    return sign + value.toFixed(1).replace(/\.0$/, '') + 'b';
  } else if (absNum >= 1000000) {
    const value = absNum / 1000000;
    if (value % 1 === 0) {
      return sign + value.toFixed(0) + 'm';
    }
    return sign + value.toFixed(1).replace(/\.0$/, '') + 'm';
  } else if (absNum >= 1000) {
    const value = absNum / 1000;
    if (value % 1 === 0) {
      return sign + value.toFixed(0) + 'k';
    }
    return sign + value.toFixed(1).replace(/\.0$/, '') + 'k';
  } else {
    // Для чисел меньше 1000 показываем как есть, но убираем десятичные если они .0
    if (num % 1 === 0) {
      return sign + num.toFixed(0);
    }
    return sign + num.toFixed(1).replace(/\.0$/, '');
  }
};

// Обновите функцию загрузки
const loadStockItems = async () => {
  try {
    console.log('🔄 Loading stock items from Supabase...');
    
    const { data, error } = await supabase
      .from('stock_items')
      .select('*')
      .order('created_at', { ascending: false });

    if (error) {
      console.error('❌ Error loading stock items:', error);
      throw error;
    }
    
    console.log('✅ Raw stock items:', data);
    
    // Нормализуем данные
    const normalizedData = normalizeStockItems(data || []);
    console.log('✅ Normalized stock items:', normalizedData);
    
    stockItems.value = normalizedData;
    
  } catch (error) {
    console.error('❌ Error loading stock items:', error);
  }
};

// Вычисляемые свойства с нормализацией
const promoItems = computed(() => {
  const now = new Date();
  const filtered = stockItems.value.filter(item => {
    const cleanType = item.item_type?.toString().toLowerCase().trim();
    const isValidType = cleanType === 'promo';
    const validUntil = new Date(item.valid_until);
    const isValidDate = validUntil > now;
    const isValid = isValidType && isValidDate;
    
    console.log(`📊 Promo check: ${item.name}`, {
      original_type: item.item_type,
      clean_type: cleanType,
      isValidType,
      validUntil: item.valid_until,
      isValidDate,
      isValid
    });
    
    return isValid;
  });
  
  console.log('🎯 Final PROMO items:', filtered);
  return filtered;
});

const incomeItems = computed(() => {
  const now = new Date();
  const filtered = stockItems.value.filter(item => {
    const cleanType = item.item_type?.toString().toLowerCase().trim();
    const isValidType = cleanType === 'income_card';
    const validUntil = new Date(item.valid_until);
    const isValidDate = validUntil > now;
    const isValid = isValidType && isValidDate;
    
    console.log(`📊 Income check: ${item.name}`, {
      original_type: item.item_type,
      clean_type: cleanType,
      isValidType,
      validUntil: item.valid_until,
      isValidDate,
      isValid
    });
    
    return isValid;
  });
  
  console.log('🎯 Final INCOME items:', filtered);
  return filtered;
});

// Добавьте также отладку в наблюдатель
watch(showFinanceSimulator, (newVal) => {
  console.log('Finance simulator opened:', newVal); // Отладка
  if (newVal) {
    loadStockItems();
  }
});

// Проверка покупки элемента
const isItemPurchased = (itemId) => {
  if (!userData.value || !userData.value.purchased_items) return false;
  return userData.value.purchased_items[itemId] === true;
};

// Покупка элемента - ЗАБЛОКИРОВАНА
const purchaseItem = async (item) => {
  // Функция заблокирована - ничего не делаем
  console.log('Finance покупки заблокированы');
  return;
};

// Применение эффекта элемента
const applyItemEffect = async (item) => {
  try {
    if (item.item_type === 'promo') {
      const saleValue = parseSaleValue(item.sale_value);
      if (saleValue.type === 'sale') {
        store.applyDiscount(saleValue.value);
        console.log(`✅ Applied ${saleValue.value}% discount`);
      }
    } else if (item.item_type === 'income_card') {
      const incomeValue = parseSaleValue(item.sale_value);
      if (incomeValue.type === 'income') {
        store.addPassiveIncome(incomeValue.value);
        console.log(`✅ Added passive income: ${incomeValue.value}/sec`);
      }
    }
  } catch (error) {
    console.error('❌ Error applying item effect:', error);
  }
};

// Вспомогательные функции для акций
const formatSaleValue = (saleValue) => {
  const parsed = parseSaleValue(saleValue);
  if (parsed.type === 'sale') {
    return `${parsed.value}% discount`;
  } else if (parsed.type === 'income') {
    return `+${parsed.value}/sec`;
  }
  return saleValue;
};

const getIncomeValue = (saleValue) => {
  const parsed = parseSaleValue(saleValue);
  return parsed.type === 'income' ? parsed.value : 0;
};

const parseSaleValue = (saleValue) => {
  const parts = saleValue.split(' ');
  if (parts.length === 2) {
    return {
      type: parts[0],
      value: parseInt(parts[1])
    };
  }
  return { type: 'unknown', value: 0 };
};

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};

// Система кликов
const maxClicks = 100;
const availableClicks = ref(maxClicks);
const progress1 = computed(() => (availableClicks.value / maxClicks) * 100);

// Функции для работы с кликами
const saveClicks = async () => {
  if (!store.currentAccount?.name) return;

  const { error } = await supabase
    .from('users')
    .update({ 
      available_clicks: availableClicks.value,
      last_click_update: new Date().toISOString() 
    })
    .eq('name', store.currentAccount.name);

  if (error) {
    console.error('Ошибка сохранения:', error);
  }
};

const useClick = () => {
  const clickCost = store.boost + 1;
  
  if (availableClicks.value >= clickCost) {
    availableClicks.value -= clickCost;
    saveClicks();
    return true;
  }
  return false;
};

// Анимации клика
const showPlusOne = ref(false);
const animationStyle = ref({ left: '0px', top: '0px' });

const handleClick = (event) => {
  if (!useClick()) return;
  
  store.add(clickValue.value);
  event.preventDefault();
  
  animateTilt(event);
  showPlusOneAtPosition(event);
};

const animateTilt = (event) => {
  // Эффект вдавливания (scale)
  clickableImg.value.style.transform = `scale(0.99)`;
  clickableImg.value.style.transition = 'transform 0.1s ease';
  
  setTimeout(() => {
    clickableImg.value.style.transform = 'scale(1)';
  }, 100);
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

// Boost система - ИСПРАВЛЕННАЯ ФУНКЦИЯ
const goToBoostPage = () => {
  showBoostPage.value = true;
  console.log('Opening boost page'); // Для отладки
};

const boostPackages = [
  { price: 500, value: 1, field: 'boost_1' },
  { price: 1000, value: 2, field: 'boost_2' },
  { price: 2000, value: 3, field: 'boost_3' },
  { price: 5000, value: 4, field: 'boost_4' },
  { price: 10000, value: 5, field: 'boost_5' }
];

const purchaseBoost = async (pack) => {
  const success = await store.purchaseBoost(pack);
  if (success) {
    console.log('Boost purchased successfully');
  }
};

// Вычисляемые свойства для бустов
const boostProgress = computed(() => {
  const ownedCount = ownedBoostsCount.value;
  return (ownedCount / boostPackages.length) * 100;
});

const ownedBoostsCount = computed(() => {
  return Object.values(purchasedBoosts.value).filter(owned => owned).length;
});

const isNextUpgrade = (index) => {
  if (index === 0) return !purchasedBoosts.value[boostPackages[0].field];
  
  const previousOwned = purchasedBoosts.value[boostPackages[index - 1].field];
  const currentOwned = purchasedBoosts.value[boostPackages[index].field];
  
  return previousOwned && !currentOwned;
};

const purchasedBoosts = computed(() => store.purchasedBoosts);

// Система титулов
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

const updateTitle = () => {
  const currentScore = store.currentScore;
  for (let i = titles.length - 1; i >= 0; i--) {
    if (currentScore >= titles[i].threshold) {
      userTitle.value = titles[i].name;
      break;
    }
  }
};
// Добавьте в script секцию после существующих переменных
const scoreElement = ref(null);

// Функция для анимации счета
const animateScore = () => {
  if (scoreElement.value) {
    scoreElement.value.classList.add('pulse');
    setTimeout(() => {
      if (scoreElement.value) {
        scoreElement.value.classList.remove('pulse');
      }
    }, 300);
  }
};

// Обновите watch для store.score
watch(() => store.score, (newVal, oldVal) => {
  if (newVal !== oldVal) {
    animateScore();
  }
});
// После загрузки stockItems добавьте детальную проверку
watch(stockItems, (newItems) => {
  console.log('🔍 DETAILED ITEM ANALYSIS:');
  newItems.forEach((item, index) => {
    console.log(`Item ${index + 1}:`, {
      name: item.name,
      item_type: item.item_type,
      'item_type === "promo"': item.item_type === 'promo',
      'item_type === "income_card"': item.item_type === 'income_card',
      'typeof item_type': typeof item.item_type,
      'trimmed item_type': item.item_type?.trim(),
      'valid_until': item.valid_until,
      'isValidDate': new Date(item.valid_until) > new Date()
    });
  });
}, { immediate: true, deep: true });

// Наблюдатели
watch(() => store.currentScore, updateTitle, { immediate: true });

watch(() => store.currentAccount, async (newAccount) => {
  if (newAccount) {
    await loadUserData();
  }
}, { immediate: true });

watch(showFinanceSimulator, (newVal) => {
  if (newVal) {
    loadStockItems();
  }
});

// Жизненный цикл
onUnmounted(() => {
  unsubscribeFromChannel('market_changes');
});

onMounted(async () => {
  // Подписка на канал
  subscribeToChannel('market_changes', () => {
    loadStockItems();
  });

  // Загрузка данных
  await loadUserData();
  await loadStockItems();

  // Обновляем клики каждую секунду
  const clickInterval = setInterval(() => {
    if (availableClicks.value < maxClicks) {
      availableClicks.value += 1;
      saveClicks();
    }
  }, 1000);

  // Очистка интервала при размонтировании
  onUnmounted(() => {
    clearInterval(clickInterval);
  });
});
</script>
<style scoped>
.finance-simulator {
  position: relative;
  background-color: #2a2a2a;
  border-radius: 15px;
  padding: 20px;
  max-width: 800px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  color: white;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
  border: 2px solid #FFC400;
}

.simulator-header {
  text-align: center;
  margin-bottom: 20px;
}

.simulator-header h2 {
  color: #FFC400;
  margin-bottom: 5px;
}

.subtitle {
  color: #aaa;
  font-size: 14px;
}

.tabs {
  display: flex;
  border-bottom: 1px solid #444;
  margin-bottom: 20px;
}

.tabs button {
  padding: 10px 20px;
  background: none;
  border: none;
  color: #aaa;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
}

.tabs button.active {
  color: #FFC400;
  font-weight: bold;
}

.tabs button.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background: #FFC400;
}

.tab-icon {
  width: 40px;
  height: 40px;
}

/* Стили для вкладки обучения */
.learn-tab {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.lesson {
  background: #333;
  border-radius: 10px;
  padding: 15px;
  border-left: 4px solid #FFC400;
}

.lesson h3 {
  color: #FFC400;
  margin-top: 0;
}

.lesson-example {
  margin: 15px 0;
  background: #222;
  padding: 10px;
  border-radius: 5px;
}

.lesson-example img {
  max-width: 100%;
  border-radius: 5px;
}

.complete-btn {
  background: #FFC400;
  color: #222;
  border: none;
  padding: 8px 15px;
  border-radius: 5px;
  font-weight: bold;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
  margin-top: 10px;
}

.complete-btn:hover {
  background: #e6b000;
}

/* Стили для симулятора */
.portfolio-summary {
  display: flex;
  justify-content: space-between;
  background: #333;
  padding: 15px;
  border-radius: 10px;
  margin-bottom: 20px;
}

.portfolio-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.portfolio-item img {
  width: 24px;
  height: 24px;
}

.profit {
  color: #4CAF50;
}

.loss {
  color: #F44336;
}

.market-container {
  display: flex;
  gap: 20px;
}

.asset-selector {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.asset-card {
  background: #333;
  padding: 15px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.2s;
}

.asset-card:hover {
  background: #3a3a3a;
}

.asset-card.active {
  border-left: 4px solid #FFC400;
  background: #3a3a3a;
}

.asset-card img {
  width: 30px;
  height: 30px;
}

.price-up {
  color: #4CAF50;
}

.price-down {
  color: #F44336;
}

.asset-details {
  flex: 2;
  display: flex;
  flex-direction: column;
}

.asset-chart {
  height: 300px;
  background: #222;
  border-radius: 8px;
  padding: 10px;
  margin-bottom: 15px;
}

.asset-actions {
  background: #333;
  padding: 15px;
  border-radius: 8px;
}

.action-input {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.action-input input {
  flex: 1;
  background: #222;
  border: 1px solid #444;
  color: white;
  padding: 10px;
  border-radius: 5px;
  font-size: 16px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 10px 15px;
  border: none;
  border-radius: 5px;
  font-weight: bold;
  cursor: pointer;
}

.action-btn img {
  width: 16px;
  height: 16px;
}

.action-btn.buy {
  background: #4CAF50;
  color: white;
}

.action-btn.sell {
  background: #F44336;
  color: white;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Стили для достижений */
.achievements-tab {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.achievement {
  display: flex;
  gap: 15px;
  background: #333;
  padding: 15px;
  border-radius: 10px;
}

.achievement-icon img {
  width: 40px;
  height: 40px;
}

.achievement-details {
  flex: 1;
}

.achievement-details h4 {
  margin: 0 0 5px 0;
  color: #FFC400;
}

.progress-bar {
  height: 6px;
  background: #222;
  border-radius: 3px;
  margin: 8px 0;
  overflow: hidden;
}

.progress {
  height: 100%;
  background: #555;
  transition: width 0.3s;
}

.progress.completed {
  background: #FFC400;
}

.reward {
  font-size: 12px;
  color: #FFC400;
}

@media (max-width: 768px) {
  .market-container {
    flex-direction: column;
  }
  
  .portfolio-summary {
    flex-direction: column;
    gap: 10px;
  }
}
/* Стили для трейдинговой страницы */
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

.balance-info {
  background: #2a2a2a;
  padding: 10px;
  border-radius: 8px;
  margin-top: 10px;
}

.balance-info p {
  margin: 5px 0;
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
.gift_icon{
  width: 40px;
  height: 40px;
  margin-right: -7px;
  margin-top: -7px;
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
  background-color: #8c47b9; /* Зелёный цвет для купленных */
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
  bottom: 90px;
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: transform 0.2s;
}
.clicks-icon {
  width: 24px;
  height: 30px;
  margin-right: 3px;
}
.clicks-text {
  font-size: 18px;
  font-weight: bold;
  color: #9f7aca;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
  font-style: italic;
  font-family: 'Inter', sans-serif;
  font-weight: 600;

}
.boost-container {
  position: absolute;
  right: 20px;
  bottom: 90px;
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
  height: 24px;
  margin-right: 3px;
}

.boost-text {
  font-size: 18px;
  font-weight: bold;
  color: #ffc400;
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
  color: #ffc400;
  box-shadow: 0 0 10px rgba(255, 196, 0, 0.5);
  border: 2px solid #803bcf;
  
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
  bottom: 0px ;
  width: calc(100% + 4px);
  background-color: rgb(41, 41, 41);
  border-radius: 30px 30px 0 0;
  overflow: hidden;
  z-index: 10;
  box-shadow: 0 -5px 15px -5px rgba(255, 196, 0, 0.534);
  border-top: 2px solid #ffc400;

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
  background-color: #ffbb00;
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
.tabs {
  display: flex;
  margin-bottom: 15px;
  border-bottom: 1px solid #444;
}

.tabs button {
  padding: 8px 15px;
  background: none;
  border: none;
  color: #ccc;
  cursor: pointer;
  font-size: 16px;
  position: relative;
}

.tabs button.active {
  color: #ffc400;
  font-weight: bold;
}

.tabs button.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background: #ffc400;
}

.nft-container {
  margin-top: 15px;
}

.nft-collections {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 15px;
}

.nft-card {
  background: #2a2a2a;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  border: 1px solid #444;
}

.nft-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(255, 196, 0, 0.2);
}

.nft-card.owned {
  border-color: #4CAF50;
}

.nft-image {
  width: 100%;
  height: 120px;
  object-fit: cover;
}

.nft-info {
  padding: 10px;
}

.nft-info h3 {
  margin: 0 0 5px 0;
  font-size: 14px;
  color: #ffc400;
}

.nft-info p {
  margin: 3px 0;
  font-size: 12px;
}

.owned-badge {
  color: #4CAF50;
  font-weight: bold;
}

.price-change {
  font-weight: bold;
}

.price-up {
  color: #26a69a;
}

.price-down {
  color: #ef5350;
}

.balance-info {
  background: #2a2a2a;
  padding: 10px;
  border-radius: 8px;
  margin-top: 10px;
}

.balance-info p {
  margin: 5px 0;
}

.boost-status {
  margin-top: 20px;
  padding: 15px;
  background: #2a2a2a;
  border-radius: 8px;
  border-left: 4px solid #ffc400;
}

.boost-item {
  margin: 5px 0;
  padding: 5px;
  background: rgba(255, 196, 0, 0.1);
  border-radius: 4px;
}
.progress-bar-container {
  width: 80%;
  margin: 0 auto;
  padding-bottom: 10px;
  position: relative;
  top: 17vh;
  text-align: center;
  background-color: transparent;
  border-radius: 0px;
}

.progress-bar {
  width: 100%;
  height: 11px;
  background-color: #333;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.progress-valueperchik {
  height: 100%;
  background-color: #ffc400;
  border-radius: 10px;
  transition: width 0.3s ease;
}

.progress-info {
  margin-top: 8px;
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
.plus-one-animation {
  font-weight: 900;
  position: absolute;
  color: #ffcc00;
  font-size: 24px;
  pointer-events: none;
  z-index: 10;
  animation: float-down 0.8s ease-out forwards;
  display: flex;
  align-items: center;
  gap: 3px;
  font-style: normal;
}

.plus-text {
  -webkit-text-stroke: 0.3px black;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.gift-fly {
  width: 50px;
  height: 50px;
  object-fit: contain;
  filter: drop-shadow(1px 1px 2px rgba(0, 0, 0, 0.5));
  margin-left: -12px;
}

@keyframes float-down {
  0% {
    opacity: 1;
    transform: translateY(0);
  }
  100% {
    opacity: 0;
    transform: translateY(50px); /* Изменили на положительное значение для движения вниз */
  }
}

/* Альтернативный вариант с более плавным движением вниз */
.header-wrapper {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.header {
  background-color: #ffc400; /* Жёлтый цвет */
  padding: 12px 24px;
  border-radius: 45px; /* Закруглённые края */
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); /* Небольшая тень для объёма */
  min-width: 150px;
  justify-content: center;
}

.gift_icon {
  width: 40px;
  height: 40px;
  margin-right: -7px;
  margin-top: -7px;
}

.score {
  font-family: 'Inter', sans-serif;
  font-weight: 600;
  color: #2a2a2a; /* Тёмный цвет текста для контраста на жёлтом фоне */
  margin: 0;
  font-size: 36px;
}
/* Стили для элементов акций */
.stock-tab {
  padding: 10px 0;
}

.stock-items {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 15px;
  max-height: 60vh;
  overflow-y: auto;
  padding: 10px 5px;
}

.stock-item {
  background: #333;
  border-radius: 10px;
  padding: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
  position: relative;
}

.stock-item:hover:not(.disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(255, 196, 0, 0.3);
  border-color: #FFC400;
}

.stock-item.disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.stock-item.purchased {
  border-color: #4CAF50;
  background: rgba(76, 175, 80, 0.1);
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.item-header h3 {
  color: #FFC400;
  margin: 0;
  font-size: 18px;
  flex: 1;
}

.item-price {
  background: #FFC400;
  color: #2a2a2a;
  padding: 4px 8px;
  border-radius: 6px;
  font-weight: bold;
  font-size: 14px;
  margin-left: 10px;
}

.item-description {
  color: #ccc;
  font-size: 14px;
  margin-bottom: 15px;
  line-height: 1.4;
}

.item-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 15px;
}

.detail {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.label {
  color: #aaa;
  font-size: 12px;
}

.value {
  color: #fff;
  font-weight: bold;
  font-size: 13px;
}

.item-status {
  text-align: center;
  padding: 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: bold;
}

.purchased-badge {
  color: #4CAF50;
  background: rgba(76, 175, 80, 0.2);
  padding: 4px 8px;
  border-radius: 4px;
}

.sold-out-badge {
  color: #F44336;
  background: rgba(244, 67, 54, 0.2);
  padding: 4px 8px;
  border-radius: 4px;
}

.insufficient-funds {
  color: #FF9800;
  background: rgba(255, 152, 0, 0.2);
  padding: 4px 8px;
  border-radius: 4px;
}

.available-badge {
  color: #4CAF50;
  background: rgba(76, 175, 80, 0.2);
  padding: 4px 8px;
  border-radius: 4px;
}

.no-items {
  text-align: center;
  padding: 40px 20px;
  color: #aaa;
  font-style: italic;
}

/* Адаптивность */
@media (max-width: 768px) {
  .stock-items {
    grid-template-columns: 1fr;
  }
  
  .finance-simulator {
    width: 95%;
    padding: 15px;
  }
}

/* Остальные стили остаются без изменений */
.finance-simulator {
  position: relative;
  background-color: #2a2a2a;
  border-radius: 15px;
  padding: 20px;
  max-width: 800px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  color: white;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
  border: 2px solid #FFC400;
}

.simulator-header {
  text-align: center;
  margin-bottom: 20px;
}

.simulator-header h2 {
  color: #FFC400;
  margin-bottom: 5px;
}

.subtitle {
  color: #aaa;
  font-size: 14px;
}

.tabs {
  display: flex;
  border-bottom: 1px solid #444;
  margin-bottom: 20px;
}

.tabs button {
  padding: 10px 20px;
  background: none;
  border: none;
  color: #aaa;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
}

.tabs button.active {
  color: #FFC400;
  font-weight: bold;
}

.tabs button.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background: #FFC400;
}

.tab-icon {
  width: 20px;
  height: 20px;
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
/* Обновленные стили для Finance Simulator */
.finance-simulator {
  position: relative;
  background: linear-gradient(135deg, #2a2a2a 0%, #1f1f1f 100%);
  border-radius: 20px;
  padding: 25px;
  max-width: 900px;
  width: 95%;
  max-height: 90vh;
  overflow-y: auto;
  color: white;
  box-shadow: 
    0 10px 30px rgba(0, 0, 0, 0.6),
    0 0 0 1px rgba(255, 196, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 196, 0, 0.3);
  backdrop-filter: blur(10px);
}

.simulator-header {
  text-align: center;
  margin-bottom: 25px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(255, 196, 0, 0.2);
  position: relative;
}

.simulator-header::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 25%;
  right: 25%;
  height: 2px;
  background: linear-gradient(90deg, transparent, #FFC400, transparent);
}

.simulator-header h2 {
  color: #FFC400;
  margin-bottom: 8px;
  font-size: 28px;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  letter-spacing: 0.5px;
}

.subtitle {
  color: #ccc;
  font-size: 15px;
  font-weight: 400;
  opacity: 0.9;
}

/* Обновленные вкладки */
.tabs {
  display: flex;
  background: rgba(40, 40, 40, 0.8);
  border-radius: 12px;
  padding: 6px;
  margin-bottom: 25px;
  border: 1px solid rgba(255, 196, 0, 0.2);
  backdrop-filter: blur(5px);
}

.tabs button {
  flex: 1;
  padding: 12px 20px;
  background: transparent;
  border: none;
  color: #aaa;
  cursor: pointer;
  font-size: 15px;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  position: relative;
  border-radius: 8px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.tabs button:hover {
  color: #FFC400;
  background: rgba(255, 196, 0, 0.1);
  transform: translateY(-1px);
}

.tabs button.active {
  color: #FFC400;
  background: rgba(255, 196, 0, 0.15);
  box-shadow: 0 2px 8px rgba(255, 196, 0, 0.2);
  font-weight: 600;
}

.tabs button.active::before {
  content: '';
  position: absolute;
  top: -6px;
  left: 50%;
  transform: translateX(-50%);
  width: 6px;
  height: 6px;
  background: #FFC400;
  border-radius: 50%;
  box-shadow: 0 0 10px #FFC400;
}

.tab-icon {
  width: 20px;
  height: 20px;
  filter: drop-shadow(0 2px 3px rgba(0, 0, 0, 0.3));
}

/* Обновленные карточки товаров */
.stock-tab {
  padding: 5px 0;
}

.stock-items {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  max-height: 60vh;
  overflow-y: auto;
  padding: 15px 5px;
}

.stock-item {
  background: linear-gradient(145deg, #333 0%, #2a2a2a 100%);
  border-radius: 16px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
  overflow: hidden;
}

.stock-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 196, 0, 0.4), transparent);
}

.stock-item:hover:not(.disabled) {
  transform: translateY(-5px);
  box-shadow: 
    0 10px 25px rgba(255, 196, 0, 0.25),
    0 0 0 1px rgba(255, 196, 0, 0.3);
  border-color: rgba(255, 196, 0, 0.5);
}

.stock-item.disabled {
  cursor: not-allowed;
  opacity: 0.5;
  filter: grayscale(0.8);
}

.stock-item.purchased {
  border-color: #4CAF50;
  background: linear-gradient(145deg, rgba(76, 175, 80, 0.15) 0%, #333 100%);
  position: relative;
}

.stock-item.purchased::after {
  content: '✓';
  position: absolute;
  top: 15px;
  right: 15px;
  width: 24px;
  height: 24px;
  background: #4CAF50;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: bold;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
  position: relative;
}

.item-header h3 {
  color: #FFC400;
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  flex: 1;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.item-price {
  background: linear-gradient(135deg, #FFC400 0%, #e6b000 100%);
  color: #2a2a2a;
  padding: 6px 12px;
  border-radius: 8px;
  font-weight: 700;
  font-size: 15px;
  margin-left: 12px;
  box-shadow: 0 2px 8px rgba(255, 196, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.item-description {
  color: #ddd;
  font-size: 14px;
  margin-bottom: 18px;
  line-height: 1.5;
  opacity: 0.9;
}

.item-details {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 18px;
  background: rgba(0, 0, 0, 0.2);
  padding: 12px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.detail {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
}

.label {
  color: #bbb;
  font-size: 13px;
  font-weight: 500;
}

.value {
  color: #fff;
  font-weight: 600;
  font-size: 14px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.item-status {
  text-align: center;
  padding: 10px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-top: 5px;
}

.purchased-badge {
  color: #4CAF50;
  background: rgba(76, 175, 80, 0.15);
  padding: 6px 12px;
  border-radius: 6px;
  border: 1px solid rgba(76, 175, 80, 0.3);
}

.sold-out-badge {
  color: #F44336;
  background: rgba(244, 67, 54, 0.15);
  padding: 6px 12px;
  border-radius: 6px;
  border: 1px solid rgba(244, 67, 54, 0.3);
}

.insufficient-funds {
  color: #FF9800;
  background: rgba(255, 152, 0, 0.15);
  padding: 6px 12px;
  border-radius: 6px;
  border: 1px solid rgba(255, 152, 0, 0.3);
}

.available-badge {
  color: #4CAF50;
  background: rgba(76, 175, 80, 0.15);
  padding: 6px 12px;
  border-radius: 6px;
  border: 1px solid rgba(76, 175, 80, 0.3);
}

.no-items {
  text-align: center;
  padding: 50px 20px;
  color: #aaa;
  font-style: italic;
  font-size: 16px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 12px;
  border: 2px dashed rgba(255, 255, 255, 0.1);
}

/* Кастомный скроллбар */
.stock-items::-webkit-scrollbar {
  width: 6px;
}

.stock-items::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

.stock-items::-webkit-scrollbar-thumb {
  background: rgba(255, 196, 0, 0.4);
  border-radius: 3px;
}

.stock-items::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 196, 0, 0.6);
}

/* Анимации */
@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.stock-item {
  animation: slideInUp 0.5s ease-out;
}

.stock-item:nth-child(odd) {
  animation-delay: 0.1s;
}

.stock-item:nth-child(even) {
  animation-delay: 0.2s;
}

/* Адаптивность */
@media (max-width: 768px) {
  .finance-simulator {
    width: 98%;
    padding: 20px 15px;
    margin: 10px;
    border-radius: 16px;
  }
  
  .stock-items {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .tabs {
    flex-direction: column;
    gap: 5px;
  }
  
  .tabs button {
    padding: 15px;
  }
  
  .simulator-header h2 {
    font-size: 24px;
  }
}

/* Эффект блеска при наведении */
.stock-item:not(.disabled):hover::after {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(
    45deg,
    transparent,
    rgba(255, 255, 255, 0.1),
    transparent
  );
  transform: rotate(45deg);
  animation: shine 1.5s ease-in-out;
}

@keyframes shine {
  0% {
    transform: rotate(45deg) translateX(-100%);
  }
  100% {
    transform: rotate(45deg) translateX(100%);
  }
}
/* Обновленные стили для вкладок - расположение по краям */
.tabs {
  display: flex;
  background: rgba(40, 40, 40, 0.8);
  border-radius: 12px;
  padding: 6px;
  margin-bottom: 25px;
  border: 1px solid rgba(255, 196, 0, 0.2);
  backdrop-filter: blur(5px);
  justify-content: space-between;
  gap: 10px;
}

.tabs button {
  flex: 1;
  max-width: 48%;
  padding: 14px 20px;
  background: transparent;
  border: none;
  color: #aaa;
  cursor: pointer;
  font-size: 15px;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  position: relative;
  border-radius: 8px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  min-height: 50px;
}

/* Первая кнопка слева */
.tabs button:first-child {
  margin-right: auto;
}

/* Последняя кнопка справа */
.tabs button:last-child {
  margin-left: auto;
}

.tabs button:hover {
  color: #FFC400;
  background: rgba(255, 196, 0, 0.1);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.tabs button.active {
  color: #FFC400;
  background: rgba(255, 196, 0, 0.15);
  box-shadow: 
    0 4px 15px rgba(255, 196, 0, 0.25),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  font-weight: 600;
  border: 1px solid rgba(255, 196, 0, 0.3);
}

.tabs button.active::before {
  content: '';
  position: absolute;
  top: -6px;
  left: 50%;
  transform: translateX(-50%);
  width: 6px;
  height: 6px;
  background: #FFC400;
  border-radius: 50%;
  box-shadow: 0 0 12px #FFC400;
}

.tabs button.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 10%;
  right: 10%;
  height: 2px;
  background: #FFC400;
  border-radius: 1px;
}

/* Альтернативный вариант с разделителем */
.tabs.with-divider {
  position: relative;
}

.tabs.with-divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 1px;
  height: 30px;
  background: linear-gradient(to bottom, transparent, rgba(255, 196, 0, 0.3), transparent);
}

.tab-icon {
  width: 40px;
  height: 40px;
  filter: drop-shadow(0 2px 3px rgba(0, 0, 0, 0.3));
  transition: transform 0.3s ease;
}

.tabs button.active .tab-icon {
  transform: scale(1.1);
  filter: drop-shadow(0 2px 4px rgba(255, 196, 0, 0.4));
}

/* Адаптивность для мобильных */
@media (max-width: 768px) {
  .tabs {
    flex-direction: row;
    gap: 8px;
  }
  
  .tabs button {
    max-width: 48%;
    padding: 12px 15px;
    min-height: 44px;
    font-size: 14px;
  }
  
  .tab-icon {
    width: 40px;
    height: 40px;
  }
}

/* Дополнительный вариант с разными цветами акцентов для вкладок */
.tabs button:first-child.active {
  background: linear-gradient(135deg, rgba(255, 196, 0, 0.15) 0%, rgba(255, 196, 0, 0.05) 100%);
}

.tabs button:last-child.active {
  background: linear-gradient(135deg, rgba(255, 196, 0, 0.15) 0%, rgba(255, 196, 0, 0.05) 100%);
}

/* Анимация переключения вкладок */
.tabs button {
  position: relative;
  overflow: hidden;
}

.tabs button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transition: left 0.5s ease;
}

.tabs button:hover::before {
  left: 100%;
}
/* Минималистичный современный дизайн Finance с вкладками по краям */
.finance-simulator {
  position: relative;
  background: #1a1a1a;
  border-radius: 24px;
  padding: 30px;
  max-width: 900px;
  width: 95%;
  max-height: 90vh;
  overflow-y: auto;
  color: white;
  box-shadow: 
    0 20px 40px rgba(0, 0, 0, 0.8),
    0 0 0 2px #FFC400;
  border: 3px solid #FFC400;
  font-family: 'Inter', sans-serif;
}

.simulator-header {
  text-align: center;
  margin-bottom: 30px;
  padding-bottom: 25px;
  border-bottom: 3px solid #FFC400;
}

.simulator-header h2 {
  color: #FFC400;
  margin-bottom: 12px;
  font-size: 32px;
  font-weight: 800;
  letter-spacing: -0.5px;
  text-transform: uppercase;
}

.subtitle {
  color: #ccc;
  font-size: 16px;
  font-weight: 500;
  opacity: 0.9;
}

/* Вкладки по краям - как было ранее */
.tabs {
  display: flex;
  background: #2a2a2a;
  border-radius: 16px;
  padding: 8px;
  margin-bottom: 30px;
  border: 2px solid #FFC400;
  justify-content: space-between;
  gap: 10px;
}




/* Стили для иконок bonus_ticket и promocode */
.tab-icon {
  width: 40px;
  height: 40px;
  object-fit: contain;
  filter: brightness(0) invert(1);
  transition: all 0.3s ease;
}



/* Минималистичные карточки товаров */
.stock-tab {
  padding: 0;
}

.stock-items {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 24px;
  max-height: 65vh;
  overflow-y: auto;
  padding: 10px 5px;
}

.stock-item {
  background: #2a2a2a;
  border-radius: 20px;
  padding: 25px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 3px solid transparent;
  position: relative;
  overflow: hidden;
}

.stock-item:hover:not(.disabled) {
  transform: translateY(-5px);
  border-color: #FFC400;
  box-shadow: 0 15px 35px rgba(255, 196, 0, 0.2);
}

.stock-item.disabled {
  cursor: not-allowed;
  opacity: 0.4;
  filter: grayscale(1);
}

.stock-item.purchased {
  border-color: #4CAF50;
  background: #2a2a2a;
}

.stock-item.purchased::after {
  content: '✓';
  position: absolute;
  top: 20px;
  right: 20px;
  width: 18px;
  height: 18px;
  background: #4CAF50;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: bold;
  border: 2px solid white;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #FFC400;
}

.item-header h3 {
  color: #FFC400;
  margin: 0;
  font-size: 24px;
  font-weight: 800;
  flex: 1;
  letter-spacing: -0.5px;
}

.item-price {
  background: #FFC400;
  color: #000;
  padding: 10px 16px;
  border-radius: 12px;
  font-weight: 800;
  font-size: 18px;
  margin-left: 15px;
  border: 2px solid #000;
}

.item-description {
  color: #ddd;
  font-size: 16px;
  margin-bottom: 22px;
  line-height: 1.5;
  font-weight: 500;
}

.item-details {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-bottom: 22px;
  background: #333;
  padding: 18px;
  border-radius: 14px;
  border: 2px solid #444;
}

.detail {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.label {
  color: #bbb;
  font-size: 15px;
  font-weight: 600;
}

.value {
  color: #fff;
  font-weight: 700;
  font-size: 16px;
}

.item-status {
  text-align: center;
  padding: 14px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 1px;
  border: 2px solid;
}

.purchased-badge {
  color: #4CAF50;
  background: rgba(76, 175, 80, 0.1);
  border-color: #4CAF50;
}

.sold-out-badge {
  color: #F44336;
  background: rgba(244, 67, 54, 0.1);
  border-color: #F44336;
}

.insufficient-funds {
  color: #FF9800;
  background: rgba(255, 152, 0, 0.1);
  border-color: #FF9800;
}

.available-badge {
  color: #4CAF50;
  background: rgba(76, 175, 80, 0.1);
  border-color: #4CAF50;
}

.no-items {
  text-align: center;
  padding: 60px 30px;
  color: #aaa;
  font-style: italic;
  font-size: 18px;
  font-weight: 600;
  background: #2a2a2a;
  border-radius: 20px;
  border: 3px dashed #444;
}

/* Кастомный скроллбар - утолщенный */
.stock-items::-webkit-scrollbar {
  width: 12px;
}

.stock-items::-webkit-scrollbar-track {
  background: #2a2a2a;
  border-radius: 6px;
  border: 2px solid #444;
}

.stock-items::-webkit-scrollbar-thumb {
  background: #FFC400;
  border-radius: 6px;
  border: 2px solid #2a2a2a;
}

.stock-items::-webkit-scrollbar-thumb:hover {
  background: #e6b000;
}


/* Анимации */
@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(40px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.stock-item {
  animation: slideInUp 0.4s ease-out;
}

/* Адаптивность */
@media (max-width: 768px) {
  .finance-simulator {
    width: 98%;
    padding: 25px 20px;
    margin: 10px;
    border-radius: 20px;
    border-width: 2px;
  }
  
  .stock-items {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .tabs button {
    padding: 16px 20px;
    min-height: 55px;
    font-size: 16px;
    gap: 10px;
  }
  
  .simulator-header h2 {
    font-size: 28px;
  }
  
  .item-header h3 {
    font-size: 22px;
  }
  
  .tab-icon {
    width: 24px;
    height: 24px;
  }
}

@media (max-width: 480px) {
  .finance-simulator {
    padding: 20px 15px;
    border-radius: 16px;
  }
  
  .tabs {
    flex-direction: row;
    gap: 8px;
  }
  
  .tabs button {
    min-height: 50px;
    padding: 14px 16px;
    font-size: 14px;
    gap: 8px;
  }
  
  .stock-item {
    padding: 20px;
  }
  
  .item-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .item-price {
    margin-left: 0;
    align-self: flex-start;
  }
  
  .tab-icon {
    width: 40px;
    height: 40px;
  }
}

/* Эффект подсветки для активных элементов */
.stock-item:not(.disabled):hover .item-header {
  border-color: #FFC400;
}

/* Минималистичные разделители */
.item-details .detail:not(:last-child) {
  border-bottom: 2px solid #444;
  padding-bottom: 12px;
}

/* Улучшенная типографика */
.simulator-header h2,
.item-header h3,
.tabs button {
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}

/* Контрастные тени */
.stock-item,
.tabs,
.finance-simulator {
  box-shadow: 
    0 10px 30px rgba(0, 0, 0, 0.9),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
}
/* Современный дизайн Boost Page */
.boost-page-modern {
  position: relative;
  background: linear-gradient(135deg, #2a2a2a 0%, #1f1f1f 100%);
  border-radius: 24px;
  padding: 30px;
  max-width: 800px;
  width: 95%;
  max-height: 90vh;
  overflow-y: auto;
  color: white;
  box-shadow: 
    0 20px 40px rgba(0, 0, 0, 0.8),
    0 0 0 2px #9f7aca;
  border: 3px solid #9f7aca;
  font-family: 'Inter', sans-serif;
  animation: slideUpFadeIn 0.3s ease-out forwards;
  opacity: 0;
}

.boost-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30px;
  padding-bottom: 25px;
  border-bottom: 2px solid rgba(159, 122, 202, 0.3);
}

.boost-title-section {
  display: flex;
  align-items: center;
  gap: 15px;
}

.boost-header-icon {
  width: 50px;
  height: 60px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}

.boost-title-section h2 {
  color: #9f7aca;
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.boost-subtitle {
  color: #ccc;
  font-size: 14px;
  margin: 5px 0 0 0;
  opacity: 0.8;
}

.boost-balance {
  text-align: right;
  background: rgba(159, 122, 202, 0.1);
  padding: 12px 18px;
  border-radius: 12px;
  border: 1px solid rgba(159, 122, 202, 0.3);
}

.balance-label {
  display: block;
  color: #ccc;
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.balance-amount {
  display: block;
  color: #9f7aca;
  font-size: 20px;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

/* Прогресс бар */
.boost-progress {
  background: rgba(40, 40, 40, 0.8);
  padding: 20px;
  border-radius: 16px;
  margin-bottom: 25px;
  border: 1px solid rgba(159, 122, 202, 0.2);
}



.progress-label {
  color: #ccc;
  font-size: 14px;
  font-weight: 600;
}


.progress-bar-modern {
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #9f7aca, #803bcf);
  border-radius: 4px;
  transition: width 0.5s ease;
  position: relative;
}

.progress-fill::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

/* Сетка бустов */
.boost-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 25px;
}

.boost-card {
  background: linear-gradient(145deg, #333 0%, #2a2a2a 100%);
  border-radius: 20px;
  padding: 25px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 2px solid transparent;
  position: relative;
  overflow: hidden;
}

.boost-card:hover:not(.disabled):not(.purchased) {
  transform: translateY(-5px);
  border-color: #9f7aca;
  box-shadow: 0 15px 35px rgba(159, 122, 202, 0.3);
}

.boost-card.purchased {
  border-color: #9f7aca;
  background: linear-gradient(145deg, rgba(159, 122, 202, 0.15) 0%, #2a2a2a 100%);
}

.boost-card.next-upgrade {
  border-color: #ffc400;
  box-shadow: 0 0 20px rgba(255, 196, 0, 0.4);
}

.boost-card.disabled:not(.purchased) {
  cursor: not-allowed;
  opacity: 0.5;
  filter: grayscale(0.8);
}

.boost-badge {
  position: absolute;
  top: 15px;
  right: 15px;
  background: #9f7aca;
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  z-index: 2;
}

.boost-card-content {
  position: relative;
  z-index: 1;
}

.boost-icon-section {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.boost-value-circle {
  position: relative;
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #9f7aca, #803bcf);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 3px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 20px rgba(159, 122, 202, 0.4);
}

.boost-value {
  color: white;
  font-size: 20px;
  font-weight: 800;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.boost-mini-icon {
  position: absolute;
  bottom: -5px;
  right: -3px;
  width: 20px;
  height: 24px;
  filter: brightness(0) invert(1) drop-shadow(0 1px 2px rgba(0, 0, 0, 0.3));
}

.boost-info {
  text-align: center;
}

.boost-name {
  color: #9f7aca;
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 700;
}

.boost-description {
  color: #ccc;
  margin: 0 0 15px 0;
  font-size: 14px;
  opacity: 0.9;
}

.boost-price-section {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: rgba(255, 196, 0, 0.1);
  padding: 10px 15px;
  border-radius: 10px;
  border: 1px solid rgba(255, 196, 0, 0.3);
}

.boost-price {
  color: #ffc400;
  font-size: 18px;
  font-weight: 700;
}

.coin-icon {
  width: 20px;
  height: 20px;
}

.boost-owned {
  background: rgba(159, 122, 202, 0.2);
  padding: 10px 15px;
  border-radius: 10px;
  color: #9f7aca;
  font-weight: 600;
}

.next-upgrade-indicator {
  position: absolute;
  bottom: -1px;
  left: -1px;
  right: -1px;
  background: linear-gradient(90deg, #ffc400, #e6b000);
  color: #2a2a2a;
  padding: 8px;
  text-align: center;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-radius: 0 0 18px 18px;
}

.unavailable-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 18px;
}

.unavailable-overlay span {
  color: #ff6b6b;
  font-weight: 600;
  text-align: center;
  padding: 0 15px;
}

/* Статистика */
.boost-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  background: rgba(40, 40, 40, 0.8);
  padding: 20px;
  border-radius: 16px;
  border: 1px solid rgba(159, 122, 202, 0.2);
}

.stat-item {
  text-align: center;
  padding: 15px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.stat-label {
  display: block;
  color: #ccc;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}

.stat-value {
  display: block;
  color: #9f7aca;
  font-size: 20px;
  font-weight: 700;
}

/* Кнопка закрытия */
.modal-close-modern {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 20px;
  height: 20px;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  color: white;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}



/* Адаптивность */
@media (max-width: 768px) {
  .boost-page-modern {
    width: 98%;
    padding: 25px 20px;
    margin: 10px;
  }
  
  .boost-header {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .boost-title-section {
    justify-content: center;
  }
  
  .boost-balance {
    align-self: center;
  }
  
  .boost-grid {
    grid-template-columns: 1fr;
  }
  
  .boost-stats {
    grid-template-columns: 1fr;
    gap: 10px;
  }
  
  .stat-item {
    padding: 12px;
  }
}

/* Кастомный скроллбар */
.boost-page-modern::-webkit-scrollbar {
  width: 8px;
}

.boost-page-modern::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
}

.boost-page-modern::-webkit-scrollbar-thumb {
  background: #9f7aca;
  border-radius: 4px;
}

.boost-page-modern::-webkit-scrollbar-thumb:hover {
  background: #803bcf;
}

/* Анимации */
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

.boost-card {
  animation: slideInUp 0.4s ease-out;
}

.boost-card:nth-child(odd) {
  animation-delay: 0.1s;
}

.boost-card:nth-child(even) {
  animation-delay: 0.2s;
}
@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
/* Стили для серой накладки */
.simulator-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(50, 50, 50, 0.7);
  backdrop-filter: blur(2px);
  z-index: 100;
  pointer-events: all; /* Блокирует все события мыши */
  border-radius: 24px;
}

/* Разрешаем скролл даже при наложении */
.stock-items {
  z-index: 1;
  position: relative;
}

/* Блокируем кнопки вкладок когда overlay активен */
.tabs button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Блокируем клики на элементах когда overlay активен */
.stock-item.disabled-overlay {
  cursor: not-allowed;
  opacity: 0.7;
}

/* Убедимся, что кнопка закрытия поверх overlay */
.modal-close {
  position: absolute;
  top: 10px;
  right: 10px;
  background: none;
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  z-index: 101; /* Выше чем overlay */
}

.finance-simulator {
  position: relative; /* Важно для позиционирования overlay */
  background: #1a1a1a;
  border-radius: 24px;
  padding: 30px;
  max-width: 900px;
  width: 95%;
  max-height: 90vh;
  overflow-y: auto;
  color: white;
  box-shadow: 
    0 20px 40px rgba(0, 0, 0, 0.8),
    0 0 0 2px #FFC400;
  border: 3px solid #FFC400;
  font-family: 'Inter', sans-serif;
}

/* Альтернативный вариант с полупрозрачным overlay */
.simulator-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(30, 30, 30, 0.85);
  z-index: 100;
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Можно добавить сообщение на overlay */
.simulator-overlay::after {
  content: 'Processing...';
  color: #FFC400;
  font-size: 18px;
  font-weight: bold;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}

/* Блокировка только определенных элементов */
.stock-item {
  position: relative;
}

.stock-item.blocked::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(50, 50, 50, 0.6);
  border-radius: 16px;
  z-index: 10;
  cursor: not-allowed;
}

/* Сохраняем скроллбар видимым */
.finance-simulator::-webkit-scrollbar {
  z-index: 102;
}
/* Серая накладка на весь экран */
.fullscreen-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(40, 40, 40, 0.95);
  backdrop-filter: blur(3px);
  z-index: 99;
  pointer-events: all;
  /* При клике в любом месте overlay закрывает модалку */
  cursor: pointer;
}

/* Модальное окно Finance Simulator */
.finance-simulator {
  position: relative;
  background: #1a1a1a;
  border-radius: 24px;
  padding: 30px;
  max-width: 900px;
  width: 95%;
  max-height: 90vh;
  overflow-y: auto;
  color: white;
  box-shadow: 
    0 20px 40px rgba(0, 0, 0, 0.8),
    0 0 0 2px #FFC400;
  border: 3px solid #FFC400;
  font-family: 'Inter', sans-serif;
  z-index: 100; /* Выше чем overlay */
  
  /* Позиционирование по центру */
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

/* Затемнение фона модального окна */
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

/* Кнопка закрытия всегда доступна */
.modal-close {
  position: absolute;
  top: 10px;
  right: 10px;
  background: none;
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  z-index: 101; /* Самый верхний слой */
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.5);
  transition: all 0.3s ease;
}

.modal-close:hover {
  background: rgba(255, 196, 0, 0.3);
  color: #FFC400;
  transform: scale(1.1);
}

/* Стили для содержимого */
.stock-items {
  position: relative;
  z-index: 1;
}

/* Все элементы внутри модалки остаются кликабельными */
.stock-item,
.tabs button {
  position: relative;
  z-index: 1;
}

/* Анимация появления */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .finance-simulator,
.modal-leave-active .finance-simulator {
  transition: all 0.3s ease;
}

.modal-enter-from .finance-simulator,
.modal-leave-to .finance-simulator {
  opacity: 0;
  transform: translate(-50%, -50%) scale(0.9);
}

/* Альтернативный вариант - более темная накладка */
.fullscreen-overlay.darker {
  background: rgba(20, 20, 20, 0.98);
  backdrop-filter: blur(5px);
}

/* Вариант с сообщением */
.fullscreen-overlay.with-message::before {
  content: 'Finance Simulator';
  position: absolute;
  top: 20px;
  left: 0;
  right: 0;
  text-align: center;
  color: #FFC400;
  font-size: 24px;
  font-weight: bold;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}

/* Для мобильных устройств */
@media (max-width: 768px) {
  .finance-simulator {
    width: 98%;
    padding: 25px 20px;
    margin: 10px;
    max-height: 85vh;
  }
  
  .fullscreen-overlay {
    background: rgba(30, 30, 30, 0.97);
  }
}

/* Вариант с градиентом для overlay */
.fullscreen-overlay.gradient {
  background: linear-gradient(
    135deg, 
    rgba(30, 30, 30, 0.95) 0%, 
    rgba(40, 40, 40, 0.95) 100%
  );
}

/* Стили для скроллбара внутри модалки */
.finance-simulator::-webkit-scrollbar {
  width: 12px;
}

.finance-simulator::-webkit-scrollbar-track {
  background: #2a2a2a;
  border-radius: 6px;
  border: 2px solid #444;
}

.finance-simulator::-webkit-scrollbar-thumb {
  background: #FFC400;
  border-radius: 6px;
  border: 2px solid #2a2a2a;
}

.finance-simulator::-webkit-scrollbar-thumb:hover {
  background: #e6b000;
}
/* Серая накладка на весь экран */
.fullscreen-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(40, 40, 40, 0.95);
  backdrop-filter: blur(3px);
  z-index: 99;
  pointer-events: all;
  /* При клике в любом месте overlay закрывает модалку */
  cursor: pointer;
}

/* Модальное окно Finance Simulator */
.finance-simulator {
  position: relative;
  background: #1a1a1a;
  border-radius: 24px;
  padding: 30px;
  max-width: 900px;
  width: 95%;
  max-height: 90vh;
  overflow-y: auto;
  color: white;
  box-shadow: 
    0 20px 40px rgba(0, 0, 0, 0.8),
    0 0 0 2px #FFC400;
  border: 3px solid #FFC400;
  font-family: 'Inter', sans-serif;
  z-index: 100; /* Выше чем overlay */
  
  /* Позиционирование по центру */
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

/* Затемнение фона модального окна */
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

/* Кнопка закрытия всегда доступна */
.modal-close {
  position: absolute;
  top: 10px;
  right: 10px;
  background: none;
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  z-index: 101; /* Самый верхний слой */
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.5);
  transition: all 0.3s ease;
}

.modal-close:hover {
  background: rgba(255, 196, 0, 0.3);
  color: #FFC400;
  transform: scale(1.1);
}

/* Стили для содержимого */
.stock-items {
  position: relative;
  z-index: 1;
}

/* Все элементы внутри модалки остаются кликабельными */
.stock-item,
.tabs button {
  position: relative;
  z-index: 1;
}

/* Анимация появления */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .finance-simulator,
.modal-leave-active .finance-simulator {
  transition: all 0.3s ease;
}

.modal-enter-from .finance-simulator,
.modal-leave-to .finance-simulator {
  opacity: 0;
  transform: translate(-50%, -50%) scale(0.9);
}

/* Альтернативный вариант - более темная накладка */
.fullscreen-overlay.darker {
  background: rgba(20, 20, 20, 0.98);
  backdrop-filter: blur(5px);
}

/* Вариант с сообщением */
.fullscreen-overlay.with-message::before {
  content: 'Finance Simulator';
  position: absolute;
  top: 20px;
  left: 0;
  right: 0;
  text-align: center;
  color: #FFC400;
  font-size: 24px;
  font-weight: bold;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}

/* Для мобильных устройств */
@media (max-width: 768px) {
  .finance-simulator {
    width: 98%;
    padding: 25px 20px;
    margin: 10px;
    max-height: 85vh;
  }
  
  .fullscreen-overlay {
    background: rgba(30, 30, 30, 0.97);
  }
}

/* Вариант с градиентом для overlay */
.fullscreen-overlay.gradient {
  background: linear-gradient(
    135deg, 
    rgba(30, 30, 30, 0.95) 0%, 
    rgba(40, 40, 40, 0.95) 100%
  );
}

/* Стили для скроллбара внутри модалки */
.finance-simulator::-webkit-scrollbar {
  width: 12px;
}

.finance-simulator::-webkit-scrollbar-track {
  background: #2a2a2a;
  border-radius: 6px;
  border: 2px solid #444;
}

.finance-simulator::-webkit-scrollbar-thumb {
  background: #FFC400;
  border-radius: 6px;
  border: 2px solid #2a2a2a;
}

.finance-simulator::-webkit-scrollbar-thumb:hover {
  background: #e6b000;
}
/* Обертка для finance simulator */
.finance-simulator-wrapper {
  position: relative;
  max-width: 900px;
  width: 95%;
  max-height: 90vh;
}

/* Фиксированная накладка, которая всегда покрывает видимую область */
.simulator-block-overlay-sticky {
  position: sticky;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(80, 80, 80, 0.7); /* Более прозрачная */
  backdrop-filter: blur(1px);
  z-index: 101;
  pointer-events: none; /* Позволяет скроллить */
  border-radius: 24px;
  
  /* Фиксируем размер чтобы покрывал всю видимую область */
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

/* Контент finance simulator */
.finance-simulator {
  position: relative;
  background: #1a1a1a;
  border-radius: 24px;
  padding: 30px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  color: white;
  box-shadow: 
    0 20px 40px rgba(0, 0, 0, 0.8),
    0 0 0 2px #FFC400;
  border: 3px solid #FFC400;
  font-family: 'Inter', sans-serif;
  z-index: 100;
  
  /* Позиционирование по центру */
  position: relative;
  top: 0;
  left: 0;
  transform: none;
}

/* Кнопка закрытия поверх накладки */
.modal-close {
  position: absolute;
  top: 10px;
  right: 10px;
  background: none;
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  z-index: 102; /* Выше overlay */
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.5);
  transition: all 0.3s ease;
}

.modal-close:hover {
  background: rgba(255, 196, 0, 0.3);
  color: #FFC400;
  transform: scale(1.1);
}

/* Заблокированные элементы */
.stock-item.blocked {
  cursor: not-allowed;
  pointer-events: none;
  opacity: 0.8;
}

.tabs button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Затемнение фона модального окна */
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
/* Современный дизайн для header-wrapper */
.header-wrapper {
  display: flex;
  justify-content: center;
  padding: 25px 0 15px 0;
  position: relative;
}

.header {
  background: linear-gradient(135deg, #FFC400 0%, #FFB300 100%);
  padding: 16px 32px;
  border-radius: 60px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 
    0 8px 20px rgba(255, 196, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.5);
  min-width: 180px;
  justify-content: center;
  backdrop-filter: blur(5px);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

/* Эффект блеска при наведении */
.header::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
  transition: left 0.6s ease;
}

.header:hover::before {
  left: 100%;
}

/* Анимация при наведении */
.header:hover {
  transform: translateY(-2px);
  box-shadow: 
    0 12px 28px rgba(255, 196, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);
}

/* Стиль для иконки подарка */
.gift_icon {
  width: 48px;
  height: 48px;
  margin-right: -5px;
  margin-top: -5px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
  animation: subtleFloat 3s ease-in-out infinite;
}

@keyframes subtleFloat {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-3px);
  }
}

/* Стиль для счета */
.score {
  font-family: 'Inter', 'Segoe UI', sans-serif;
  font-weight: 800;
  color: #000000;
  margin: 0;
  font-size: 42px;
  letter-spacing: -1px;
  background: linear-gradient(135deg, #1f1f1f 0%, #2a2a2a 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  position: relative;
  display: inline-block;
}

/* Добавляем декоративный элемент */
.header::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 10%;
  right: 10%;
  height: 3px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.8), transparent);
  border-radius: 3px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.header:hover::after {
  opacity: 1;
}

/* Адаптивность для мобильных */
@media (max-width: 768px) {
  .header {
    padding: 12px 24px;
    min-width: 150px;
  }
  
  .gift_icon {
    width: 40px;
    height: 40px;
  }
  
  .score {
    font-size: 32px;
  }
}


.score.pulse {
  animation: scorePulse 0.3s ease-out;
}
</style>