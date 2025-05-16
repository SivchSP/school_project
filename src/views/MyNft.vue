<template>
  <div class="page-container">
    <!-- Навигация между страницами -->
    <div class="navigation">
      <button class="nav-button" @click="setActiveTab('my-nfts')" :class="{ active: activeTab === 'my-nfts' }">
        Мои NFT
      </button>
    
    </div>


    <div v-if="notification.show" class="notification" :class="notification.type">
      {{ notification.message }}
    </div>

    <!-- Страница "Мои NFT" -->
    <div v-if="activeTab === 'my-nfts'" class="nft-page">
      <div class="header-section">Мои NFT
        <button class="history-button" @click="showHistory = true">
          <h3>История операций</h3>
        </button>
      </div>
      
      <div v-if="loading" class="loading">Загрузка...</div>
      
      <div v-else class="nft-list">
        <div v-for="(count, nftName) in nfts" :key="nftName" class="nft-item">
          <div class="nft-info">
            <h3>{{ getNftDisplayName(nftName) }}</h3>
            <img :src="getNftImage(nftName)" :alt="nftName" class="nft-image">

            <p>Количество: {{ count }}</p>
            <p class="nft-price">Текущая цена: {{ getNftSellPrice(nftName) }} AMHSL</p>
            <div class="button-group">
              <button 
                class="transfer-button" 
                @click="initiateTransfer(nftName)"
                :disabled="count <= 0"
              >
                Передать
              </button>
              <button 
                class="sell-button" 
                @click="initiateSell(nftName)"
                :disabled="count <= 0"
              >
                Выставить на рынок
              </button>
            </div>
          </div>
        </div>
        
        <div v-if="Object.keys(nfts).length === 0" class="empty-message">
          У вас пока нет NFT. Посетите магазин, чтобы сделать покупки или войдите в аккаунт!
        </div>
      </div>
    </div>


    <!-- Страница "Рынок" -->
    
    <!-- Модальное окно передачи NFT -->
    <div v-if="transferModal.show" class="modal-overlay">
      <div class="modal-content">
        <h3>Передача {{ getNftDisplayName(transferModal.nftType) }}</h3>
        
        <div v-if="!transferModal.confirmStep">
          <div class="form-group-input">
            <label>Имя получателя:</label>
            <input 
              type="text" 
              v-model="transferModal.recipientName" 
              placeholder="Введите имя пользователя"
              @input="checkRecipientExists"
              class="input"
            >
            <p v-if="recipientCheck.loading" class="check-message loading">Проверка...</p>
            <p v-else-if="recipientCheck.exists" class="check-message success">Пользователь найден</p>
            <p v-else-if="transferModal.recipientName && !recipientCheck.exists" class="check-message error">Пользователь не найден</p>
          </div>
          
          <div class="form-group-input">
            <label>Количество (до {{ nfts[transferModal.nftType] }}):</label>
            <input 
              type="number" 
              v-model="transferModal.amount" 
              :max="nfts[transferModal.nftType]"
              min="1"
              placeholder="Введите количество"
              @input="validateTransferAmount"
              class="input"
            >
          </div>
          
          <div class="modal-buttons">
            <button @click="transferModal.show = false" class="cancel-button">Отмена</button>
            <button 
              @click="showConfirmation" 
              class="confirm-button"
              :disabled="!recipientCheck.exists || !transferModal.amount"
            >
              Далее
            </button>
          </div>
        </div>
        
        <div v-else>
          <div class="confirmation-details">
            <h4 class="confirmation-details-h4">Детали передачи:</h4>
            <p><strong>Получатель:</strong> {{ transferModal.recipientName }}</p>
            <p><strong>NFT:</strong> {{ getNftDisplayName(transferModal.nftType) }}</p>
            <p><strong>Количество:</strong> {{ transferModal.amount }}</p>
          </div>
          
          <div class="modal-buttons">
            <button @click="transferModal.confirmStep = false" class="cancel-button">Назад</button>
            <button @click="executeTransfer" class="confirm-button">Подтвердить передачу</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно продажи NFT -->
    <div v-if="sellModal.show" class="modal-overlay">
      <div class="modal-content">
        <h3>Выставление на рынок {{ getNftDisplayName(sellModal.nftType) }}</h3>
        
        <div v-if="!sellModal.confirmStep">
          <div class="form-group-input">
            <label>Количество (до {{ nfts[sellModal.nftType] }}):</label>
            <input 
              type="number" 
              v-model="sellModal.amount" 
              :max="nfts[sellModal.nftType]"
              min="1"
              placeholder="Введите количество"
              @input="validateSellAmount"
              class="input"
            >
          </div>
          
          <div class="form-group-input">
            <label>Цена за единицу (AMHSL):</label>
            <input 
              type="number" 
              v-model="sellModal.price" 
              min="1"
              placeholder="Введите цену"
              class="input"
            >
          </div>
          
          <div class="form-group">
            <div class="price-row total">
              <span>Общая сумма:</span>
              <span class="price-value">{{ getTotalSellPrice() }} AMHSL</span>
            </div>
            <div class="price-row-commission">
              <span>Комиссия системы (5%):   </span>
              <span class="price-value-comm"> -{{ getCommission() }} AMHSL</span>
            </div>
            <div class="price-row total">
              <span>Вы получите:</span>
              <span class="price-value">{{ getFinalAmount() }} AMHSL</span>
            </div>
          </div>
          
          <div class="modal-buttons">
            <button @click="sellModal.show = false" class="cancel-button">Отмена</button>
            <button 
              @click="showSellConfirmation" 
              class="confirm-button"
              :disabled="!sellModal.amount || !sellModal.price"
            >
              Далее
            </button>
          </div>
        </div>
        
        <div v-else>
          <div class="confirmation-details-sale">
            <h4>Подтверждение продажи</h4>
          
            <div class="detail-row-sale">
              <span>Количество: </span>
              <span class="got-a-drop">{{ sellModal.amount }}</span>
            </div>
            <div class="detail-row-sale">
              <span>Цена за единицу: </span>
              <span class="got-a-drop">{{ sellModal.price }} AMHSL</span>
            </div>
            
            <div>
              <span>Комиссия системы: </span>
              <span class="got-a-drop-comm">-{{ getCommission() }} AMHSL</span>
            </div>
            <div class="detail-row-sale total">
              <span>К получению:</span>
              <span>{{ getFinalAmount() }} AMHSL</span>
            </div>
          </div>
          
          <div class="modal-buttons">
            <button @click="sellModal.confirmStep = false" class="cancel-button">Назад</button>
            <button @click="executeSell" class="confirm-button">Подтвердить продажу</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно покупки NFT -->
    <div v-if="buyModal.show" class="modal-overlay">
      <div class="modal-content">
        <h3>Покупка {{ getNftDisplayName(buyModal.nftType) }}</h3>
        
        <div class="confirmation-details">
  <div class="detail-item">
    <span class="detail-label">Продавец</span>
    <span class="detail-value">{{ buyModal.seller }}</span>
  </div>
  <div class="detail-item">
    <span class="detail-label">Количество</span>
    <span class="detail-value">{{ buyModal.amount }} шт.</span>
  </div>
  <div class="detail-item">
    <span class="detail-label">Цена за единицу</span>
    <span class="detail-value">{{ buyModal.pricePerUnit }} AMHSL</span>
  </div>

    <label class="detail-label">Количество для покупки</label>
    <input
      type="number"
      v-model="buyModal.buyAmount"
      :max="buyModal.amount"
      min="1"
      placeholder="Введите количество"
      class="modern-input"
    >

  <div class="detail-item total">
    <span class="detail-label">К оплате</span>
    <span class="detail-value total-price">{{ buyModal.buyAmount * buyModal.pricePerUnit }} AMHSL</span>
  </div>
</div>
        
        <div class="modal-buttons">
          <button @click="buyModal.show = false" class="cancel-button">Отмена</button>
          <button 
            @click="executeBuy" 
            class="confirm-button"
            :disabled="!buyModal.buyAmount || buyModal.buyAmount > buyModal.amount"
          >
            Подтвердить покупку
          </button>
        </div>
      </div>
    </div>
    <!-- История операций -->
    <div v-if="showHistory" class="history-modal">
      <div class="history-content">
        <div class="history-header">
          <h3>История операций</h3>
          <button class="close-history" @click="showHistory = false">×</button>
        </div>
        
        <div class="history-tabs">
          <button 
            class="tab-button" 
            :class="{ active: historyTab === 'sales' }"
            @click="historyTab = 'sales'"
          >
            Продажи
          </button>
          <button 
            class="tab-button" 
            :class="{ active: historyTab === 'transfers' }"
            @click="historyTab = 'transfers'"
          >
            Передачи
          </button>
          <button 
            class="tab-button" 
            :class="{ active: historyTab === 'market' }"
            @click="historyTab = 'market'"
          >
            Рыночные сделки
          </button>
        </div>
        
        <div v-if="loadingHistory" class="loading-history">
          Загрузка истории...
        </div>
        
        <div v-else>
          <div v-if="historyTab === 'sales'">
            <div v-if="filteredSales.length === 0" class="empty-history">
              У вас еще не было продаж
            </div>
            
            <div v-else class="history-list">
              <div v-for="(sale, index) in filteredSales" :key="'sale-'+index" class="history-item">
                <div class="item-type sale">
                  <span>Продажа</span>
                </div>
                <div class="item-details">
                  <div class="item-info">
                    <span class="item-name">{{ getNftDisplayName(sale.nft_type) }}</span>
                    <span class="item-amount">{{ sale.amount }} шт </span>
                    <span class="item-price">{{ sale.price_per_unit }} AMHSL за шт</span>
                  </div>
                  <div class="item-total">
                    <span class="item-date">{{ formatDate(sale.date) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div v-if="historyTab === 'transfers'">
            <div v-if="filteredTransfers.length === 0" class="empty-history">
              У вас еще не было передач
            </div>
            
            <div v-else class="history-list">
              <div v-for="(transfer, index) in filteredTransfers" :key="'transfer-'+index" class="history-item">
                <div class="item-type transfer">
                  <span>{{ transfer.sender === currentAccountName ? 'Отправка' : 'Получение' }}</span>
                </div>
                <div class="item-details">
                  <div class="item-info">
                    <span class="item-name">{{ getNftDisplayName(transfer.nft_type) }}</span>
                    <span class="item-amount">{{ transfer.amount }} шт</span>
                    <span class="item-recipient">
                      {{ transfer.sender === currentAccountName ? '→ ' + transfer.recipient : '← ' + transfer.sender }}
                    </span>
                  </div>
                  <div class="item-date-full">
                    {{ formatDateTime(transfer.date) }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="historyTab === 'market'">
  <div v-if="marketHistory.length === 0" class="empty-history">
    У вас еще не было рыночных сделок
  </div>
  
  <div v-else class="history-list">
    <div v-for="(deal, index) in marketHistory" :key="'deal-'+index" class="history-item">
      <div class="item-type" :class="deal.type">
        <span>{{ 
          deal.type === 'buy' ? 'Покупка' : 
          deal.type === 'sell' ? 'Продажа' : 
          'Снятие с продажи' 
        }}</span>
      </div>
      <div class="item-details">
        <div class="item-info">
          <span class="item-name">{{ getNftDisplayName(deal.nft_type) }}</span>
          <span class="item-amount">{{ deal.amount }} шт</span>
          <span v-if="deal.type !== 'cancel'" class="item-price">
            {{ deal.price_per_unit }} AMHSL за шт
          </span>
          <span v-if="deal.type === 'buy'" class="item-counterparty">
          </span>
          <span v-if="deal.type === 'sell'" class="item-counterparty">
          </span>
        </div>
        <div class="item-total" v-if="deal.type !== 'cancel'">
          <span class="item-date">{{ formatDate(deal.date) }}</span>
        </div>
        <div class="item-date-full" v-else>
          {{ formatDateTime(deal.date) }}
        </div>
      </div>
    </div>
  </div>
</div>
</div>
</div>
    </div>
  </div>
</template>
<script>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { createClient } from '@supabase/supabase-js';
import default_nft_image from '@/assets/nft1.png';
import cowboy_nft_image from '@/assets/nft2.png';
import stalker_nft_image from '@/assets/nft5.png';
import lame_nft_image from '@/assets/nft4.png';
import boss_nft_image from '@/assets/nft3.png';
import nft6 from '@/assets/nft6.png';
import nft7 from '@/assets/nft7.png';
import nft8 from '@/assets/nft8.png';
import nft9 from '@/assets/nft9.png';
import nft10 from '@/assets/nft10.png';

const supabaseUrl = 'https://jgkfvqiophgvswqvatbx.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impna2Z2cWlvcGhndnN3cXZhdGJ4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk4ODI5NTMsImV4cCI6MjA1NTQ1ODk1M30.GTN1V9NJwnmwy8GmXOOz3SxepV7n4yVKkhLYZTYuFEQ';
const supabase = createClient(supabaseUrl, supabaseKey);

export default {
  setup() {
    const router = useRouter();

    // Состояние компонента
    const activeTab = ref('my-nfts');
    const nfts = ref({});
    const loading = ref(true);
    const marketLoading = ref(false);
    const currentAccountName = ref('');
    const userScore = ref(0);
    const showHistory = ref(false);
    const historyTab = ref('sales');
    const salesHistory = ref([]);
    const transfersHistory = ref([]);
    const marketHistory = ref([]);
    const loadingHistory = ref(false);
    const marketItems = ref([]);

    // Уведомления
    const notification = ref({
      show: false,
      message: '',
      type: 'success'
    });

    // Проверка получателя
    const recipientCheck = ref({
      loading: false,
      exists: false
    });

    // Модальное окно передачи
    const transferModal = ref({
      show: false,
      nftType: '',
      recipientName: '',
      amount: '',
      confirmStep: false
    });

    // Модальное окно продажи
    const sellModal = ref({
      show: false,
      nftType: '',
      amount: '',
      price: '',
      confirmStep: false
    });

    // Модальное окно покупки
    const buyModal = ref({
      show: false,
      id: '',
      nftType: '',
      seller: '',
      amount: 0,
      pricePerUnit: 0,
      totalPrice: 0,
      buyAmount: 1
    });

    // Цены NFT по умолчанию
    const nftPrices = {
      'nft1': 15000,
      'nft2': 20000,
      'nft3': 30000,
      'nft4': 40000,
      'nft5': 50000,
      'nft6': 60000,
      'nft7': 65000,
      'nft8': 70000,
      'nft9': 75000,
      'nft10': 90000
    };

    // Отображение NFT
    const nftDisplayNames = {
      'nft1': 'HUSTLER',
      'nft2': 'COWBOY HUSTLER',
      'nft3': 'BOSS HUSTLER',
      'nft4': 'STEEP HUSTLER',
      'nft5': 'STALKER HUSTLER',
      'nft6': 'NINJA HUSTLER',
      'nft7': 'ROCK & ROLL HUSTLER',
      'nft8': 'GUY HUSTLER',
      'nft9': '90-s HUSTLER',
      'nft10': 'MACHO HUSTLER'
    };

    const nftImages = {
      'nft1': default_nft_image,
      'nft2': cowboy_nft_image,
      'nft3': boss_nft_image,
      'nft4': lame_nft_image,
      'nft5': stalker_nft_image,
      'nft6': nft6,
      'nft7': nft7,
      'nft8': nft8,
      'nft9': nft9,
      'nft10': nft10
    };

    // Вычисляемые свойства
    const filteredSales = computed(() => {
      return salesHistory.value;
    });

    const filteredTransfers = computed(() => {
      return transfersHistory.value;
    });

    // Основные функции
    function setActiveTab(tab) {
      activeTab.value = tab;
      if (tab === 'market') {
        loadMarketItems();
      }
    }

    function getNftDisplayName(nftKey) {
      return nftDisplayNames[nftKey] || nftKey;
    }

    function getNftImage(nftKey) {
      return nftImages[nftKey] || default_nft_image;
    }

    function getNftSellPrice(nftType) {
      return nftPrices[nftType] || 0;
    }

    function getTotalSellPrice() {
      const amount = Number(sellModal.value.amount) || 0;
      const price = Number(sellModal.value.price) || 0;
      return amount * price;
    }

    function getCommission() {
      return Math.round(getTotalSellPrice() * 0.05);
    }

    function getFinalAmount() {
      return getTotalSellPrice() - getCommission();
    }

    // Валидация
    function validateTransferAmount() {
      const maxAmount = nfts.value[transferModal.value.nftType];
      const value = transferModal.value.amount;
      
      if (value === '') {
        return;
      }
      
      const numValue = Number(value);
      if (isNaN(numValue)) {
        transferModal.value.amount = '';
        return;
      }
      
      if (numValue > maxAmount) {
        transferModal.value.amount = maxAmount;
      } else if (numValue < 1) {
        transferModal.value.amount = 1;
      }
    }

    function validateSellAmount() {
      const maxAmount = nfts.value[sellModal.value.nftType];
      const value = sellModal.value.amount;
      
      if (value === '') {
        return;
      }
      
      const numValue = Number(value);
      if (isNaN(numValue)) {
        sellModal.value.amount = '';
        return;
      }
      
      if (numValue > maxAmount) {
        sellModal.value.amount = maxAmount;
      } else if (numValue < 1) {
        sellModal.value.amount = 1;
      }
    }

    // Проверка получателя
    async function checkRecipientExists() {
      if (!transferModal.value.recipientName) {
        recipientCheck.value = { loading: false, exists: false };
        return;
      }
      
      recipientCheck.value.loading = true;
      
      try {
        const { data, error } = await supabase
          .from('users')
          .select('name')
          .eq('name', transferModal.value.recipientName)
          .single();
        
        recipientCheck.value = {
          loading: false,
          exists: !!data && !error
        };
      } catch (error) {
        recipientCheck.value = {
          loading: false,
          exists: false
        };
      }
    }

    // Форматирование дат
    function formatDate(dateString) {
      const options = { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' };
      return new Date(dateString).toLocaleDateString('ru-RU', options);
    }

    function formatDateTime(dateString) {
      const options = { 
        day: 'numeric', 
        month: 'long', 
        year: 'numeric', 
        hour: '2-digit', 
        minute: '2-digit' 
      };
      return new Date(dateString).toLocaleDateString('ru-RU', options);
    }

    // Уведомления
    function showNotification(message, type = 'success') {
      notification.value = { show: true, message, type };
      setTimeout(() => {
        notification.value.show = false;
      }, 3000);
    }

    // Загрузка истории операций
    async function loadHistory() {
      loadingHistory.value = true;
      
      try {
        const { data: userData, error } = await supabase
          .from('users')
          .select('transfers_history, sales_history, market_history')
          .eq('name', currentAccountName.value)
          .single();

        if (error) throw error;

        if (userData) {
          transfersHistory.value = userData.transfers_history || [];
          salesHistory.value = userData.sales_history || [];
          marketHistory.value = userData.market_history || [];
        }
        
      } catch (error) {
        console.error('Ошибка загрузки истории:', error);
        showNotification('Ошибка загрузки истории операций', 'error');
      } finally {
        loadingHistory.value = false;
      }
    }

    // Загрузка рыночных предложений
    async function loadMarketItems() {
      marketLoading.value = true;
      
      try {
        const { data, error } = await supabase
          .from('market')
          .select('*')
          .order('created_at', { ascending: false });

        if (error) throw error;

        marketItems.value = data || [];
        
      } catch (error) {
        console.error('Ошибка загрузки рынка:', error);
        showNotification('Ошибка загрузки рыночных предложений', 'error');
      } finally {
        marketLoading.value = false;
      }
    }

    // Инициализация передачи
    function initiateTransfer(nftType) {
      transferModal.value = {
        show: true,
        nftType,
        recipientName: '',
        amount: '',
        confirmStep: false
      };
      recipientCheck.value = { loading: false, exists: false };
    }

    // Подтверждение передачи
    function showConfirmation() {
      if (!transferModal.value.recipientName || !recipientCheck.value.exists) {
        showNotification('Пожалуйста, укажите действительного получателя', 'error');
        return;
      }
      
      if (!transferModal.value.amount || transferModal.value.amount < 1) {
        showNotification('Пожалуйста, укажите корректное количество', 'error');
        return;
      }
      
      transferModal.value.confirmStep = true;
    }

    // Выполнение передачи
    async function executeTransfer() {
      try {
        const { nftType, recipientName, amount } = transferModal.value;
        const numAmount = Number(amount);
        
        // 1. Получаем данные обоих пользователей
        const { data: users, error: fetchError } = await supabase
          .from('users')
          .select('*')
          .or(`name.eq.${currentAccountName.value},name.eq.${recipientName}`);

        if (fetchError || !users || users.length !== 2) {
          throw new Error('Ошибка получения данных пользователей');
        }

        const sender = users.find(user => user.name === currentAccountName.value);
        const recipient = users.find(user => user.name === recipientName);

        if (!sender || !recipient) {
          throw new Error('Один из пользователей не найден');
        }

        // 2. Проверяем баланс отправителя
        if (sender[nftType] < numAmount) {
          throw new Error('Недостаточно NFT для передачи');
        }

        // 3. Создаем запись о передаче
        const transferRecord = {
          nft_type: nftType,
          amount: numAmount,
          sender: currentAccountName.value,
          recipient: recipientName,
          date: new Date().toISOString()
        };

        // 4. Подготавливаем обновления
        const senderUpdates = {
          [nftType]: sender[nftType] - numAmount,
          transfers_history: [...(sender.transfers_history || []), transferRecord]
        };

        const recipientUpdates = {
          [nftType]: (recipient[nftType] || 0) + numAmount,
          transfers_history: [...(recipient.transfers_history || []), transferRecord]
        };

        // 5. Выполняем обновления
        const { error: updateError } = await supabase
          .from('users')
          .upsert([
            { id: sender.id, ...senderUpdates },
            { id: recipient.id, ...recipientUpdates }
          ]);

        if (updateError) throw updateError;

        // 6. Обновляем локальное состояние
        nfts.value[nftType] -= numAmount;
        if (nfts.value[nftType] <= 0) {
          delete nfts.value[nftType];
        }

        transfersHistory.value = senderUpdates.transfers_history;
        showNotification('NFT успешно переданы!');
        transferModal.value.show = false;

      } catch (error) {
        console.error('Transfer failed:', error);
        showNotification(`Ошибка передачи: ${error.message}`, 'error');
      }
    }

    // Инициализация продажи
    function initiateSell(nftType) {
      sellModal.value = {
        show: true,
        nftType,
        amount: '',
        price: nftPrices[nftType] || 0,
        confirmStep: false
      };
    }

    // Подтверждение продажи
    function showSellConfirmation() {
      if (!sellModal.value.amount || sellModal.value.amount < 1) {
        showNotification('Пожалуйста, укажите корректное количество', 'error');
        return;
      }
      
      if (!sellModal.value.price || sellModal.value.price < 1) {
        showNotification('Пожалуйста, укажите корректную цену', 'error');
        return;
      }
      
      sellModal.value.confirmStep = true;
    }

    // Выполнение продажи (выставление на рынок)
    async function executeSell() {
      try {
        const { nftType, amount, price } = sellModal.value;
        const numAmount = Number(amount);
        const numPrice = Number(price);
        
        // 1. Получаем текущие данные пользователя
        const { data: userData, error: fetchError } = await supabase
          .from('users')
          .select('*')
          .eq('name', currentAccountName.value)
          .single();
        
        if (fetchError) throw fetchError;
        if (!userData || userData[nftType] < numAmount) {
          throw new Error('Недостаточно NFT для продажи');
        }
        
        // 2. Создаем запись о продаже на рынке
        const { data: marketItem, error: marketError } = await supabase
          .from('market')
          .insert([{
            nft_type: nftType,
            seller: currentAccountName.value,
            amount: numAmount,
            price_per_unit: numPrice,
            total_price: numAmount * numPrice
          }])
          .select()
          .single();

        if (marketError) throw marketError;

        // 3. Обновляем баланс пользователя
        const updates = {
          [nftType]: userData[nftType] - numAmount
        };

        const { error: updateError } = await supabase
          .from('users')
          .update(updates)
          .eq('name', currentAccountName.value);
        
        if (updateError) throw updateError;
        
        // 4. Обновляем локальное состояние
        nfts.value[nftType] -= numAmount;
        if (nfts.value[nftType] <= 0) {
          delete nfts.value[nftType];
        }
        
        // 5. Обновляем список рыночных предложений
        await loadMarketItems();
        
        showNotification(`NFT успешно выставлены на рынок!`, 'success');
        sellModal.value.show = false;
        
      } catch (error) {
        console.error('Ошибка продажи:', error);
        showNotification('Ошибка при выставлении NFT на рынок: ' + error.message, 'error');
      }
    }

    // Инициализация покупки
    function initiateBuy(item) {
      buyModal.value = {
        show: true,
        id: item.id,
        nftType: item.nft_type,
        seller: item.seller,
        amount: item.amount,
        pricePerUnit: item.price_per_unit,
        totalPrice: item.total_price,
        buyAmount: 1
      };
    }

    // Выполнение покупки
    async function executeBuy() {
      try {
        const { id, nftType, seller, buyAmount, pricePerUnit } = buyModal.value;
        const numAmount = Number(buyAmount);
        const totalPrice = numAmount * pricePerUnit;
        
        // 1. Получаем данные покупателя и продавца
        const { data: users, error: fetchError } = await supabase
          .from('users')
          .select('*')
          .or(`name.eq.${currentAccountName.value},name.eq.${seller}`);

        if (fetchError || !users || users.length !== 2) {
          throw new Error('Ошибка получения данных пользователей');
        }

        const buyer = users.find(user => user.name === currentAccountName.value);
        const sellerData = users.find(user => user.name === seller);

        if (!buyer || !sellerData) {
          throw new Error('Один из пользователей не найден');
        }

        // 2. Проверяем баланс покупателя
        if ((buyer.score || 0) < totalPrice) {
          throw new Error('Недостаточно средств для покупки');
        }

        // 3. Проверяем наличие предложения на рынке
        const { data: marketItem, error: marketError } = await supabase
          .from('market')
          .select('*')
          .eq('id', id)
          .single();

        if (marketError || !marketItem) {
          throw new Error('Предложение на рынке не найдено');
        }

        if (marketItem.amount < numAmount) {
          throw new Error('Недостаточное количество NFT в предложении');
        }

        // 4. Создаем запись о сделке
        const dealRecord = {
          nft_type: nftType,
          amount: numAmount,
          price_per_unit: pricePerUnit,
          seller: seller,
          buyer: currentAccountName.value,
          date: new Date().toISOString(),
          type: 'buy'
        };

        // 5. Подготавливаем обновления
        // Для покупателя
        const buyerUpdates = {
          [nftType]: (buyer[nftType] || 0) + numAmount,
          score: (buyer.score || 0) - totalPrice,
          market_history: [...(buyer.market_history || []), dealRecord]
        };

        // Для продавца
        const sellerUpdates = {
          score: (sellerData.score || 0) + totalPrice,
          market_history: [...(sellerData.market_history || []), {
            ...dealRecord,
            type: 'sell'
          }]
        };

        // 6. Обновление рыночного предложения
        let marketUpdates = null;
        if (marketItem.amount === numAmount) {
          // Если покупаем все - удаляем предложение
          const { error: deleteError } = await supabase
            .from('market')
            .delete()
            .eq('id', id);
          
          if (deleteError) throw deleteError;
        } else {
          // Если покупаем часть - уменьшаем количество
          const { error: updateError } = await supabase
            .from('market')
            .update({ 
              amount: marketItem.amount - numAmount,
              total_price: (marketItem.amount - numAmount) * marketItem.price_per_unit
            })
            .eq('id', id);
          
          if (updateError) throw updateError;
        }

        // 7. Выполняем обновления пользователей
        const { error: updateError } = await supabase
          .from('users')
          .upsert([
            { id: buyer.id, ...buyerUpdates },
            { id: sellerData.id, ...sellerUpdates }
          ]);

        if (updateError) throw updateError;

        // 8. Обновляем локальное состояние
        nfts.value[nftType] = (nfts.value[nftType] || 0) + numAmount;
        userScore.value = buyerUpdates.score;

        // 9. Обновляем историю и список рыночных предложений
        marketHistory.value = buyerUpdates.market_history;
        await loadMarketItems();
        await loadUserData(); // Перезагружаем данные пользователя

        showNotification(`Вы успешно купили ${numAmount} ${getNftDisplayName(nftType)} за ${totalPrice} AMHSL!`, 'success');
        buyModal.value.show = false;

      } catch (error) {
        console.error('Ошибка покупки:', error);
        showNotification('Ошибка при покупке NFT: ' + error.message, 'error');
      }
    }

    // Навигация
    function goBack() {
      router.go(-1);
    }

    // Загрузка данных пользователя
    async function loadUserData() {
      loading.value = true;
      
      try {
        const { data, error } = await supabase
          .from('users')
          .select('nft1, nft2, nft3, nft4, nft5,nft6, nft7, nft8, nft9, nft10, score, transfers_history, sales_history, market_history')
          .eq('name', currentAccountName.value)
          .single();
        
        if (error) throw error;

        if (data) {
          nfts.value = Object.fromEntries(
            Object.entries(data).filter(([key, value]) => key.startsWith('nft') && value > 0)
          );
          userScore.value = data.score || 0;
          transfersHistory.value = data.transfers_history || [];
          salesHistory.value = data.sales_history || [];
          marketHistory.value = data.market_history || [];
        }
        
      } catch (error) {
        console.error('Ошибка загрузки:', error);
        showNotification('Ошибка загрузки данных', 'error');
      } finally {
        loading.value = false;
      }
    }

    // Инициализация компонента
    onMounted(async () => {
      const savedAccount = localStorage.getItem('currentAccount');
      if (savedAccount) {
        currentAccountName.value = JSON.parse(savedAccount).name;
      }
      
      if (currentAccountName.value) {
        await loadUserData();
        await loadMarketItems();
        
        // Подписка на изменения рынка в реальном времени
        const marketSubscription = supabase
          .channel('market_changes')
          .on(
            'postgres_changes',
            {
              event: '*',
              schema: 'public',
              table: 'market'
            },
            () => {
              loadMarketItems();
            }
          )
          .subscribe();
      } else {
        loading.value = false;
      }
    });

    return {
      activeTab,
      nfts,
      loading,
      marketLoading,
      currentAccountName,
      showHistory,
      historyTab,
      filteredSales,
      filteredTransfers,
      marketHistory,
      marketItems,
      notification,
      transferModal,
      sellModal,
      buyModal,
      recipientCheck,
      setActiveTab,
      getNftDisplayName,
      getNftImage,
      getNftSellPrice,
      getTotalSellPrice,
      getCommission,
      getFinalAmount,
      validateTransferAmount,
      validateSellAmount,
      checkRecipientExists,
      formatDate,
      formatDateTime,
      showNotification,
      loadHistory,
      initiateTransfer,
      showConfirmation,
      executeTransfer,
      initiateSell,
      showSellConfirmation,
      executeSell,
      initiateBuy,
      executeBuy,
      goBack
    };
  }
};
</script>
<style scoped>
@keyframes slideLeftFadeIn {
  from {
    opacity: 0;
    transform: translateX(0px);
  }
  to {
    opacity: 1;
    transform: translateX(50);
  }
}
@keyframes slideRightFadeIn {
  from {
    opacity: 0;
    transform: translateX(50px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
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
.item-details-modal-content {
  touch-action: none; /* Важно для предотвращения скролла страницы за модалкой */
}

@media (max-width: 768px) {
  .item-details-modal-content {
    padding-bottom: env(safe-area-inset-bottom); /* Учет "безопасной зоны" на iOS */
  }
  
  .modal-drag-handle {
    height: 8px;
    width: 60px;
  }
}
.item-details-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  animation: slideUpFadeIn 0.3s ease-out forwards;
  opacity: 0; /* Начальное состояние (прозрачность 0) */
}

.item-details-modal-content {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: #2c2c2c;
  border-radius: 20px 20px 0 0;
  padding: 20px;
  padding-bottom: 80px;
  border: 1px solid #1b1b1b;
  box-shadow: 0 -2px 10px rgba(51, 51, 51, 0.13);
  touch-action: none;
}

.modal-drag-handle {
  width: 50px;
  height: 6px;
  background-color: #8d8d8d;
  border-radius: 3px;
  margin: 0 auto 15px;
  cursor: grab;
}

.item-details-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
  overflow-y: auto;
  max-height: calc(80vh - 150px); /* Учитываем padding и кнопки */
  color: #dddddd;
  padding-top: 20px; /* Оставляем место для ручки */
  width: 100%;
}

.modal-nft-image {
  max-width: 100%;
  max-height: 25vh;
  object-fit: contain;
  border-radius: 20px;
  margin: 0 auto;
  display: block;
}

.item-details-info {
  width: 100%;
  text-align: center;
  padding: 0 10px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #3d3d3d;
}

.modal-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 20px;
  position: sticky;
  bottom: 0;
  background-color: #2c2c2c;
  padding-top: 10px;
}

.buy-button, .cancel-sale-button {
  padding: 14px;
  border-radius: 10px;
  font-weight: bold;
  cursor: pointer;
  border: none;
  width: 100%;
  font-size: 16px;
  transition: opacity 0.2s;
}

.buy-button {
  background-color: #4CAF50;
  color: white;
}

.buy-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
  opacity: 0.7;
}

.cancel-sale-button {
  background-color: #f44336;
  color: white;
}

/* Анимация закрытия при свайпе */
@keyframes slide-down {
  to {
    transform: translateY(100%);
  }
}

/* Для закрытия при достижении 50% */
.item-details-modal-content.closing {
  animation: slide-down 0.2s forwards;
}

/* Стили для карточек товаров на рынке */
.market-item {
  position: relative;
  border-radius: 10px;
  overflow: hidden;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
}

.item-image-container {
  cursor: pointer;
  position: relative;
}

.item-image-container::after {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.03);
  transition: background 0.2s;
}

.item-image-container:hover::after {
  background: rgba(0, 0, 0, 0.1);
}

.nft-image {
  width: 100%;
  height: 200px;
  object-fit: contain;
  display: block;
}

.item-actions {
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* Адаптивные стили */
@media (min-width: 768px) {
  .item-details-modal-content {
    max-width: 500px;
    border-radius: 20px;
    align-items: center;
  }
  
  .item-details-container {
    flex-direction: row;
    align-items: flex-start;
  }
  
  .modal-nft-image {
    width: 150px;
    height: 150px;
  }
  
  .item-details-info {
    text-align: left;
    flex: 1;
  }
}
.page-container {
  position: relative;
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
  padding: 20px 15px 80px;
  background-color: #1d1d1d;
  font-family: 'Arial', sans-serif;
  border-radius: 15px;
  box-shadow: 0 0 20px rgba(255, 196, 0, 0.068);

}

/* Навигация */
.navigation {
  display: flex;
  justify-content: space-around;
  margin-bottom: 25px;
  background-color: #2c2c2c;
  padding: 10px;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.nav-button {
  padding: 12px 20px;
  background-color: transparent;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  color: #ffffff;
  cursor: pointer;
  transition: all 0.3s ease;
}

.nav-button.active {
  background-color: #ffd700;
  color: #000;
  font-weight: 600;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  box-shadow: 0 0 20px rgba(255, 196, 0, 0.5);
}

.nav-button:hover:not(.active) {
  background-color: #ffd700;
}

/* Общие элементы */
.back-button {
  position: fixed;
  top: 15px;
  left: 15px;
  padding: 8px 15px;
  background-color: #ffd700;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  z-index: 100;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.title {
  color: #ffd700;
  margin: 0 0 15px 0;
  font-size: 1.5rem;
  text-align: center;
}

.loading {
  text-align: center;
  padding: 30px 0;
  color: #666;
  font-size: 1.1rem;
}

.empty-message {
  text-align: center;
  padding: 30px 0;
  color: #888;
  font-size: 1rem;
}

/* Уведомления */
.notification {
  position: fixed;
  bottom: 70px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 24px;
  border-radius: 8px;
  color: white;
  font-size: 0.95rem;
  z-index: 1000;
  animation: fadeIn 0.3s, fadeOut 0.3s 2.7s;
  max-width: 90%;
  text-align: center;
}

.notification.success {
  background-color: #4CAF50;
  bottom: 70px;

}

.notification.error {
  background-color: #F44336;
  bottom: 70px;

}

/* Страница "Мои NFT" */
.nft-page {
  background-color: #363636;
  padding: 20px;
  border-radius: 15px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  animation: slideLeftFadeIn 0.15s ease-out forwards;
  opacity: 0; /* Начальное состояние (прозрачность 0) */
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  color: #ffbb00;
  font-size: 23px;
  font-weight: 800;
}

.history-button {
  padding: 8px 15px;
  background-color: #ffd700;
  border: none;
  border-radius: 5px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.history-button:hover {
  background-color: #e0e0e0;
}

.nft-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.nft-item {
  display: flex;
  background-color: #2e2e2e;
  border-radius: 10px;
  padding: 15px;
  box-shadow: 0 1px 3px rgba(0,0,0,1);
  transition: transform 0.2s;
  border: 1px solid #ffc4001f;

}

.nft-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 3px 8px rgba(0,0,0,0.1);
}

.nft-info {
  text-align: center;

  flex: 1;
}

.nft-info h3 {
  margin: 0 0 8px 0;
  color: #ffc400;
  font-size: 1.2rem;
}

.nft-info p {
  margin: 5px 0;
  color: #c2c2c2;
  font-size: 0.95rem;
}

.nft-price {
  color: #4CAF50;
  font-weight: bold;
}

.button-group {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.transfer-button, 
.sell-button {
  padding: 8px 12px;
  border: none;
  border-radius: 5px;
  font-size: 0.9rem;
  cursor: pointer;
  flex: 1;
  transition: all 0.2s;
}

.transfer-button {
  background-color: #ffd700;
  color: #000;
}

.sell-button {
  background-color: #4CAF50;
  color: white;
}

.transfer-button:hover:not(:disabled),
.sell-button:hover:not(:disabled) {
  opacity: 0.9;
  transform: translateY(-1px);
}

.transfer-button:disabled, 
.sell-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.nft-image {
  width: 80px;
  height: 80px;
  border-radius: 10px;
  object-fit: cover;
  margin-left: 15px;
  border: 2px solid #eee;
}

/* Обновленные стили для страницы "Рынок" */
.market-page {
  background-color: #363636;
  padding: 20px;
  border-radius: 15px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  animation: slideLeftFadeIn 0.15s ease-out forwards;
  opacity: 0; /* Начальное состояние (прозрачность 0) */
}

.market-container {
  max-width: 100%;
}

.market-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  width: 100%;
}

.market-item {
  display: flex;
  flex-direction: column;
  background-color: #2e2e2e;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.5);
  transition: all 0.2s;
  height: 95%;



}

.market-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 3px 8px rgba(0,0,0,0.1);
}

.item-image {
  width: 90%;
  margin-bottom: 10px;
  display: flex;
  justify-content: center;
}

.item-image img {
  width: 100%;
  max-width: 120px;
  height: auto;
  border-radius: 8px;
  object-fit: cover;
  border: 2px solid #eee;
}

.item-details {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.item-details h3 {
  margin: 0 0 8px 0;
  color: #ffc400;
  font-size: 1.1rem;
  text-align: center;
}

.item-info {
  flex: 1;
}

.item-info p {
  margin: 4px 0;
  color: #c2c2c2;
  font-size: 0.9rem;
}

.item-price {
  color: #4CAF50;
  font-weight: bold;
}

.item-total {
  font-weight: bold;
  color: #333;
}

.item-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 12px;
}

.buy-button {
  padding: 8px 12px;
  background-color: #ffd900;
  color: rgb(14, 14, 14);
  border: none;
  border-radius: 5px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 0 20px rgba(36, 36, 36, 0.5);
  width: 100%;
}

.buy-button:hover:not(:disabled) {
  background-color: #ffd900b4;
  transform: translateY(-1px);
}

.buy-button:disabled {
  background-color: #ffd900b4;
  cursor: not-allowed;
}

.cancel-sale-button {
  padding: 8px 12px;
  background-color: #f44336;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.2s;
  width: 100%;
}

.cancel-sale-button:hover {
  background-color: #d32f2f;
  transform: translateY(-1px);
}

.item-type.cancel {
  background-color: #ff9800;
}
.hustler{
color: #707070;
text-align: left;
font-size: 14px ;
font-weight: bold;
}
/* Модальные окна */
.input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  transition: border 0.2s;
  background-color: #2c2c2c;
  color: #ffff;
}

.input:focus {
  outline: none;
  border-color: #ffbb00;
}
.detail-row-sale {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #494949;
}
.got-a-drop{
  color: #d4d4d4;
  font-weight: 600;

}
.got-a-drop-comm{
  color: #ff2525;
  font-weight: 600;
  font-style: italic;
}
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background-color: rgb(34, 34, 34);
  padding: 20px;
  border-radius: 19px;
  width: 100%;
  max-width: 400px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 0 20px rgba(255, 196, 0, 0.5);
  border: 2px solid #ffc400;


}
.modal-content h3 {
  margin: 0 0 20px 0;
  color: #ffbb00;
  font-size: 1.3rem;
  text-align: center;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
  
}
.form-group-input{
  margin-bottom: 15px;
  color: #bebebe;
  font-family: 'Inter', sans-serif;
  font-weight: 600;

}
.form-group {
  margin-bottom: 15px;
  font-family: 'Inter', sans-serif;
  background-color: #3a3a3a;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;

}

.form-group label {
  margin-bottom: 8px;
  font-size: 0.95rem;
  color: #c9c9c9;
  font-weight: 500;
}

.form-group-input input {

  width: 100%;
  padding: 10px 12px;
  border: 1px solid #313131;
  border-radius: 6px;
  font-size: 1rem;
  box-sizing: border-box;
  transition: border-color 0.2s;
}

.form-group input:focus {
  border-color: #ffc400;
  outline: none;
}

.check-message {
  font-size: 0.85rem;
  margin: 5px 0 0;
  padding: 3px 5px;
  border-radius: 3px;
}

.check-message.loading {
  color: #2196F3;
}

.check-message.success {
  color: #4CAF50;
  background-color: rgb(34, 34, 34);
}

.check-message.error {
  color: #f44336;
  background-color: rgb(34, 34, 34);
}

.price-details {
  background-color: #333333;
  padding: 15px;
  border-radius: 8px;
  margin: 20px 0;
}

.price-row-commission{
color: rgb(255, 255, 255);
}
.price-value-comm{
color: rgb(255, 0, 0);
font-weight: 600;
font-style: italic;
}

.price-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-size: 0.95rem;
}

.price-value {
  font-weight: bold;
}



.total {
  font-weight: bold;
  color: #4CAF50;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px dashed #ddd;
}

.confirmation-details {
  background-color: #dddddd;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}
.confirmation-details {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  font-family: 'Inter', sans-serif;
  color: #c0c0c0;
  padding: 1.5rem;
  border-radius: 12px;
  background: #1b1b1b;
  box-shadow: 0 2px 10px rgba(82, 82, 82, 0.1);
}
.confirmation-details-sale {
  background-color: #dddddd;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}
.confirmation-details-sale {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  font-family: 'Inter', sans-serif;
  color: #999999;
  padding: 1.5rem;
  border-radius: 12px;
  background: #1b1b1b;
  box-shadow: 0 2px 10px rgba(82, 82, 82, 0.1);
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid #3a3a3a;
}

.detail-item:last-child {
  border-bottom: none;
}

.detail-label {
  font-weight: 500;
  color: #888888;
}

.detail-value {
  font-weight: 600;
  color: #cccccc;
}

.input-row {
  flex-direction: column;
  align-items: flex-start;
  gap: 0.5rem;
}

.modern-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  transition: border 0.2s;
  background-color: #2c2c2c;
  color: #ffff;
}

.modern-input:focus {
  outline: none;
  border-color: #ffbb00;
}

.total {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #5e5e5e;
}

.total-price {
  font-size: 1.1rem;
  color: #ffbb00;
  font-weight: 700;
}
.confirmation-details h4 {
  margin: 0 0 15px 0;
  text-align: center;
  color: #ececec;
  font-size: 1.1rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 0.95rem;
}

.detail-row span:first-child {
  color: #666;
}

.detail-row.total {
  font-weight: bold;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px dashed #000000;
}

.modal-buttons {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  margin-top: 20px;
}

.cancel-button, 
.confirm-button {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-button {
  background-color: #363636;
  color: #b4b4b4;
}

.cancel-button:hover {
  background-color: #313131;
}

.confirm-button {
  background-color: #4CAF50;
  color: white;
  font-weight: bold;
}

.confirm-button:hover:not(:disabled) {
  background-color: #388E3C;
}

.confirm-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  background-color: #a5d6a7;
}

/* История операций */
.history-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 20px;
  
}
.history-content {
  background-color: rgb(34, 34, 34);
  padding: 20px;
  border-radius: 12px;
  width: 100%;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
  position: relative;
  box-shadow: 0 0 20px rgba(255, 196, 0, 0.5);
  border: 2px solid #ffc400;
  animation: slideUpFadeIn 0.3s ease-out forwards;
  opacity: 0; /* Начальное состояние (прозрачность 0) */
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.history-header h3 {
  margin: 0;
  color: #ffd000;
  font-size: 1.3rem;
  
}

.close-history {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #666;
  padding: 5px;
  transition: color 0.2s;
}

.close-history:hover {
  color: #333;
}

.history-tabs {
  display: flex;
  border-bottom: 1px solid #000000;
  margin-bottom: 15px;
}

.tab-button {
  flex: 1;
  padding: 10px;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  font-size: 0.95rem;
  color: #ffffff;
  transition: all 0.2s;
}

.tab-button.active {
  color: #ffd700;
  border-bottom-color: #ffd700;
  font-weight: bold;
}

.tab-button:hover:not(.active) {
  color: #333;
}

.loading-history {
  text-align: center;
  padding: 30px 0;
  color: #666;
  font-size: 1rem;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  
}

.history-item {
  display: flex;
  background-color: #525252;
  border-radius: 8px;
  padding: 12px;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(0,0,0,0.5);

}

.history-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.item-type {
  width: 80px;
  padding: 5px;
  border-radius: 4px;
  text-align: center;
  font-size: 0.8rem;
  font-weight: bold;
  margin-right: 12px;
  align-self: center;
}

.item-type.sale {
  background-color: #4CAF50;
  color: rgb(0, 0, 0);
}

.item-type.transfer {
  background-color: #4CAF50;
  color: rgb(0, 0, 0);
}

.item-type.buy {
  background-color: #ffbb00;
  color: rgb(2, 2, 2);
}

.item-details {
  flex: 1;
}

.item-info {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 5px;
}

.item-name {
  font-weight: bold;
  color: #ffc400;
}

.item-amount {
  color: #dddddd;
}

.item-price {
  color: #4CAF50;
  font-weight: bold;
}

.item-recipient, 
.item-counterparty {
  color: #4CAF50;
}

.item-total {
  text-align: right;
  font-weight: bold;
  color: #333;
}

.item-date {
  display: block;
  font-size: 0.8rem;
  color: #bdbdbd;
  margin-top: 3px;
}

.item-date-full {
  text-align: right;
  font-size: 0.8rem;
  color: #888;
  
}
/* Анимации */
@keyframes fadeIn {
  from { 
    opacity: 0;
    bottom: 0;
  }
  to { 
    opacity: 1;
    bottom: 20px;
  }
}

@keyframes fadeOut {
  from { 
    opacity: 1;
    bottom: 20px;
  }
  to { 
    opacity: 0;
    bottom: 0;
  }
}


/* Адаптивность */
@media (max-width: 300px) {
  .market-grid {
    grid-template-columns: 1fr;
  }
  
  .market-item {
    flex-direction: row;
  }
  
  .item-image {
    flex: 0 0 80px;
    margin-right: 15px;
    margin-bottom: 0;
  }
  
  .item-image img {
    max-width: 80px;
  }
}

@media (max-width: 480px) {
  .page-container {
    padding: 15px 10px 70px;
  }
  
  .navigation {
    margin-bottom: 15px;
  }
  
  .nav-button {
    padding: 10px 15px;
    font-size: 0.9rem;
  }
  
  .nft-page, 
  .market-page {
    padding: 15px;
  }
  
  .nft-item, 
  .market-item {
    flex-direction: column;
  }
  
  .nft-image, 
  .item-image img {
    width: 100%;
    height: auto;
    margin: 10px 0 0 0;
  }
  
  .button-group {
    flex-direction: column;
  }
  
  .modal-content {
    padding: 15px;
  }
  
  .market-item {
    flex-direction: column;
  }
  
  .item-image {
    flex: 0 0 auto;
    margin-right: 0;
    margin-bottom: 12px;
  }
}

/* Анимации */
@keyframes fadeIn {
  from { 
    opacity: 0;
    bottom: 0;
  }
  to { 
    opacity: 1;
    bottom: 20px;
  }
}

@keyframes fadeOut {
  from { 
    opacity: 1;
    bottom: 20px;
  }
  to { 
    opacity: 0;
    bottom: 0;
  }
}
</style>