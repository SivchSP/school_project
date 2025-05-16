<template>
  <div class="page-container">
    <!-- Навигация между страницами -->
    <div class="navigation">
      <button class="nav-button" @click="setActiveTab('market')" :class="{ active: activeTab === 'market' }">
        Рынок
      </button>
      <button class="nav-button" @click="setActiveTab('my-nfts')" :class="{ active: activeTab === 'my-nfts' }">
        Мои NFT
      </button>
    </div>

    <!-- Баланс и фильтр -->
    <div class="balance-filter-container">
      <div v-if="tonConnectUI?.connected" class="ton-balance balance-container">
        <span>Баланс: {{ tonBalance }} TON</span>
      </div>
      
      <div v-if="activeTab === 'market'" class="filter-container">
        <button class="filter-button" @click="toggleFilterDropdown">
          NFTs <span class="filter-icon">{{ showFilterDropdown ? '▲' : '▼' }}</span>
        </button>
        <div v-if="showFilterDropdown" class="filter-dropdown">
    <div class="search-box">
      <input 
        v-model="searchQuery" 
        type="text" 
        placeholder="Search..." 
        class="search-input"
      >
    </div>
    
    <div class="filter-section">
      <div class="filter-category">
        <!-- <div class="category-header">
          Easter Egg <span class="new-badge">NEW!</span>
        </div> -->
        <div 
          v-for="nft in filteredEasterEggNfts" 
          :key="nft" 
          class="filter-item"
          @click="toggleNftFilter(nft)"
          :class="{ selected: selectedNftTypes.includes(nft) }"
        >
          <img :src="getNftImage(nft)" :alt="nft" class="nft-icon">
          <span class="nft-name">{{ getNftDisplayName(nft) }}</span>
          <span class="checkmark" v-if="selectedNftTypes.includes(nft)">✓</span>
        </div>
      </div>
      
      <div class="filter-category">
        <div class="category-header">
          Featured
        </div>
        <div 
          v-for="nft in filteredFeaturedNfts" 
          :key="nft" 
          class="filter-item"
          @click="toggleNftFilter(nft)"
          :class="{ selected: selectedNftTypes.includes(nft) }"
        >
          <img :src="getNftImage(nft)" :alt="nft" class="nft-icon">
          <span class="nft-name">{{ getNftDisplayName(nft) }}</span>
          <span class="checkmark" v-if="selectedNftTypes.includes(nft)">✓</span>
        </div>
      </div>
    </div>
  </div>
      </div>
    </div>

    <div v-if="notification.show" class="notification" :class="notification.type">
      {{ notification.message }}
    </div>

    <!-- Страница "Мои NFT" -->
    <div v-if="activeTab === 'my-nfts'" class="nft-page">
      <div class="header-section">
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
            <p class="nft-price" :class="{ 'ton': isTONNFT(nftName) }">
                Текущая цена: {{ getNftSellPrice(nftName).price }}
            <img :src="getNftSellPrice(nftName).currencyImage" :alt="getNftSellPrice(nftName).currency" class="currency-icon">
            </p>
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
                :class="{ 'ton': isTONNFT(nftName) }"
                @click="initiateSell(nftName)"
                :disabled="count <= 0"
              >
                Продать
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
    <div v-else class="market-page">
      <div class="market-container">
        <div class="market-grid">
          <div 
            v-for="item in filteredMarketItems" 
            :key="item.id" 
            class="market-item" 
            :class="{ 'ton': item.currency === 'TON' }"
          >
            <div class="item-image-container" @click="showItemDetails(item)">
              <img :src="getNftImage(item.nft_type)" :alt="item.nft_type" class="nft-image">
            </div>
            <h6 class="hustler">{{ getNftDisplayName(item.nft_type) }}</h6>  
            <div class="item-actions">
              <button 
                class="buy-button" 
                @click.stop="initiateBuy(item)"
                :disabled="item.seller === currentAccountName"
              >
                {{ item.price_per_unit }} {{ item.currency }}
              </button>
              <button 
                v-if="item.seller === currentAccountName"
                class="cancel-sale-button"
                @click.stop="initiateCancelSale(item)"
              >
                Снять с продажи
              </button>
            </div>
          </div>
        </div>
        
        <div v-if="filteredMarketItems.length === 0" class="empty-message">
          На рынке пока нет предложений 
        </div>
      </div>
    </div>

    <!-- Модальное окно деталей товара -->
    <div v-if="itemDetailsModal.show" class="item-details-modal-overlay" @click="handleModalClose">
      <div 
        class="item-details-modal-content"
        :style="{ transform: `translateY(${itemDetailsModal.offset}px)` }"
        @click.stop
        @mousedown="startDrag"
        @touchstart.passive="startDrag"
      >
        <div class="modal-drag-handle" @mousedown="startDrag"></div>
        <div class="item-details-container">
          <img :src="getNftImage(itemDetailsModal.item.nft_type)" :alt="itemDetailsModal.item.nft_type" class="modal-nft-image">
          <div class="item-details-info">
            <h3>{{ getNftDisplayName(itemDetailsModal.item.nft_type) }}</h3>
            <div class="detail-row">
              <span>Количество:</span>
              <span>{{ itemDetailsModal.item.amount }}</span>
            </div>
            <div class="detail-row">
              <span>Цена за штуку:</span>
              <span>{{ itemDetailsModal.item.price_per_unit }} {{ itemDetailsModal.item.currency }}</span>
            </div>
            <div class="detail-row">
              <span>Продавец:</span>
              <span>{{ itemDetailsModal.item.seller }}</span>
            </div>
          </div>
        </div>
        <div class="modal-actions">
          <button 
            class="buy-button" 
            @click="initiateBuy(itemDetailsModal.item)"
            :disabled="itemDetailsModal.item.seller === currentAccountName"
          >
            Купить
          </button>
          <button 
            v-if="itemDetailsModal.item.seller === currentAccountName"
            class="cancel-sale-button"
            @click="initiateCancelSale(itemDetailsModal.item)"
          >
            Снять с продажи
          </button>
        </div>
      </div>
    </div>
    
    <!-- Модальное окно снятия с продажи -->
    <div v-if="cancelSaleModal.show" class="modal-overlay">
      <div class="modal-content">
        <h3>Снятие с продажи {{ getNftDisplayName(cancelSaleModal.nftType) }}</h3>
        
        <div class="confirmation-details">
          <h4>Подтверждение снятия с продажи</h4>
          <div class="detail-row">
            <span>Тип NFT:</span>
            <span>{{ getNftDisplayName(cancelSaleModal.nftType) }}</span>
          </div>
          <div class="detail-row">
            <span>Количество:</span>
            <span>{{ cancelSaleModal.amount }}</span>
          </div>
        </div>
        
        <div class="modal-buttons">
          <button @click="cancelSaleModal.show = false" class="cancel-button">Отмена</button>
          <button @click="executeCancelSale" class="confirm-button">Подтвердить</button>
        </div>
      </div>
    </div>

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
            <label>Цена за единицу ({{ isTONNFT(sellModal.nftType) ? 'TON' : 'AMHSL' }}):</label>
            <input 
              type="number" 
              v-model="sellModal.price" 
              min="1"
              :placeholder="`Введите цену в ${isTONNFT(sellModal.nftType) ? 'TON' : 'AMHSL'}`"
              class="input"
            >
          </div>
          
          <div class="form-group">
            <div class="price-row total">
              <span>Общая сумма:</span>
              <span class="price-value">{{ getTotalSellPrice() }} {{ isTONNFT(sellModal.nftType) ? 'TON' : 'AMHSL' }}</span>
            </div>
            <div v-if="!isTONNFT(sellModal.nftType)" class="price-row-commission">
              <span>Комиссия системы (5%):</span>
              <span class="price-value-comm"> -{{ getCommission() }} AMHSL</span>
            </div>
            <div v-if="!isTONNFT(sellModal.nftType)" class="price-row total">
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
              <span class="got-a-drop">{{ sellModal.price }} {{ isTONNFT(sellModal.nftType) ? 'TON' : 'AMHSL' }}</span>
            </div>
            
            <div v-if="!isTONNFT(sellModal.nftType)">
              <span>Комиссия системы: </span>
              <span class="got-a-drop-comm">-{{ getCommission() }} AMHSL</span>
            </div>
            <div class="detail-row-sale total">
              <span>К получению:</span>
              <span>{{ isTONNFT(sellModal.nftType) ? getTotalSellPrice() : getFinalAmount() }} {{ isTONNFT(sellModal.nftType) ? 'TON' : 'AMHSL' }}</span>
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
            <span class="detail-value">{{ buyModal.pricePerUnit }} {{ buyModal.currency }}</span>
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
            <span class="detail-value total-price">{{ buyModal.buyAmount * buyModal.pricePerUnit }} {{ buyModal.currency }}</span>
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
                    <span class="item-price">{{ sale.price_per_unit }} {{ sale.currency || 'AMHSL' }} за шт</span>
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
                  <span>{{ transfer.sender === currentAccountName.value ? 'Отправка' : 'Получение' }}</span>
                </div>
                <div class="item-details">
                  <div class="item-info">
                    <span class="item-name">{{ getNftDisplayName(transfer.nft_type) }}</span>
                    <span class="item-amount">{{ transfer.amount }} шт</span>
                    <span class="item-recipient">
                      {{ transfer.sender === currentAccountName.value ? '→ ' + transfer.recipient : '← ' + transfer.sender }}
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
                      {{ deal.price_per_unit }} {{ deal.currency || 'AMHSL' }} за шт
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
import { ref, computed, onMounted, watch, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { createClient } from '@supabase/supabase-js';
import default_nft_image from '@/assets/nft1.png';
import cowboy_nft_image from '@/assets/nft2.png';
import stalker_nft_image from '@/assets/nft5.png';
import lame_nft_image from '@/assets/nft4.png';
import boss_nft_image from '@/assets/nft3.png';
import nft10 from '@/assets/nft6.png';
import nft7 from '@/assets/nft7.png';
import nft8 from '@/assets/nft8.png';
import nft9 from '@/assets/nft9.png';
import nft6 from '@/assets/nft10.png';
import Ton_def from '@/assets/TON_def.png';
import AMHSL from '@/assets/frog1.png';

const supabaseUrl = 'https://jgkfvqiophgvswqvatbx.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impna2Z2cWlvcGhndnN3cXZhdGJ4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk4ODI5NTMsImV4cCI6MjA1NTQ1ODk1M30.GTN1V9NJwnmwy8GmXOOz3SxepV7n4yVKkhLYZTYuFEQ';
const supabase = createClient(supabaseUrl, supabaseKey);

export default {
  props: {
    tonConnectUI: Object
  },
  
  setup(props) {
    const router = useRouter();
    const tonBalance = ref(0);
    const isDraggingModal = ref(false);
    const dragStartY = ref(0);
    const dragCurrentY = ref(0);

    // Состояние компонента
    const activeTab = ref('market');
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

    // Фильтрация
    const showFilterDropdown = ref(false);
    const searchQuery = ref('');
    const selectedNftTypes = ref([]);
    const easterEggNfts = ['nft1', 'nft2', 'nft3', 'nft4', 'nft5'];
    const featuredNfts = ['nft6', 'nft7', 'nft8', 'nft9', 'nft10'];

    const filteredEasterEggNfts = computed(() => {
      return easterEggNfts.filter(nft => 
        getNftDisplayName(nft).toLowerCase().includes(searchQuery.value.toLowerCase()))
    });

    const filteredFeaturedNfts = computed(() => {
      return featuredNfts.filter(nft => 
        getNftDisplayName(nft).toLowerCase().includes(searchQuery.value.toLowerCase()))
    });

    const filteredMarketItems = computed(() => {
      if (selectedNftTypes.value.length === 0) return marketItems.value;
      return marketItems.value.filter(item => selectedNftTypes.value.includes(item.nft_type));
    });

    // Модальные окна и уведомления
    const cancelSaleModal = ref({
      show: false,
      id: '',
      nftType: '',
      amount: 0
    });

    const notification = ref({
      show: false,
      message: '',
      type: 'success'
    });

    const recipientCheck = ref({
      loading: false,
      exists: false
    });

    const transferModal = ref({
      show: false,
      nftType: '',
      recipientName: '',
      amount: '',
      confirmStep: false
    });

    const sellModal = ref({
      show: false,
      nftType: '',
      amount: '',
      price: '',
      confirmStep: false
    });

    const buyModal = ref({
      show: false,
      id: '',
      nftType: '',
      seller: '',
      amount: 0,
      pricePerUnit: 0,
      totalPrice: 0,
      buyAmount: 1,
      currency: 'AMHSL'
    });

    const itemDetailsModal = ref({
      show: false,
      item: null,
      offset: 0,
      startY: 0,
      isDragging: false
    });

    // Константы
    const nftPricesInTON = {
      'nft10': 0.3,
      'nft7': 0.1,
      'nft8': 0.15,
      'nft9': 0.25,
      'nft6': 0.05,
    };

    const nftPrices = {
      'nft1': 15000,
      'nft2': 20000,
      'nft3': 30000,
      'nft4': 40000,
      'nft5': 50000,
    };

    const nftDisplayNames = {
      'nft1': 'HUSTLER',
      'nft2': 'COWBOY HUSTLER',
      'nft3': 'BOSS HUSTLER',
      'nft4': 'STEEP HUSTLER',
      'nft5': 'STALKER HUSTLER',
      'nft6': 'MACHO HUSTLER',
      'nft7': 'ROCK & ROLL HUSTLER',
      'nft8': 'GUY HUSTLER',
      'nft9': '90-s HUSTLER',
      'nft10': 'NINJA HUSTLER'
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

    // Методы фильтрации
    const toggleFilterDropdown = () => {
  showFilterDropdown.value = !showFilterDropdown.value;
  nextTick(() => {
    const dropdown = document.querySelector('.filter-dropdown');
    if (dropdown) {
      if (showFilterDropdown.value) {
        dropdown.classList.add('open');
      } else {
        dropdown.classList.remove('open');
      }
    }
  });
};

    const toggleNftFilter = (nftType) => {
      if (selectedNftTypes.value.includes(nftType)) {
        selectedNftTypes.value = selectedNftTypes.value.filter(type => type !== nftType);
      } else {
        selectedNftTypes.value = [...selectedNftTypes.value, nftType];
      }
    };

    // Функция загрузки рыночных предметов
    const loadMarketItems = async () => {
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
    };

    // Остальные методы компонента
    const getNftDisplayName = (nftKey) => {
      return nftDisplayNames[nftKey] || nftKey;
    };

    const getNftImage = (nftKey) => {
      return nftImages[nftKey] || default_nft_image;
    };

    const isTONNFT = (nftType) => {
      return ['nft6', 'nft7', 'nft8', 'nft9', 'nft10'].includes(nftType);
    };

    const getNftSellPrice = (nftType) => {
      if (isTONNFT(nftType)) {
        return {
          price: nftPricesInTON[nftType],
          currency: 'TON',
          currencyImage: Ton_def
        };
      }
      return {
        price: nftPrices[nftType] || 0,
        currency: 'AMHSL',
        currencyImage: AMHSL
      };
    };

    const getTotalSellPrice = () => {
      const amount = Number(sellModal.value.amount) || 0;
      const price = Number(sellModal.value.price) || 0;
      return amount * price;
    };

    const getCommission = () => {
      return Math.round(getTotalSellPrice() * 0.05);
    };

    const getFinalAmount = () => {
      return getTotalSellPrice() - getCommission();
    };

    const validateTransferAmount = () => {
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
    };

    const validateSellAmount = () => {
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
    };

    const checkRecipientExists = async () => {
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
    };

    const formatDate = (dateString) => {
      const options = { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' };
      return new Date(dateString).toLocaleDateString('ru-RU', options);
    };

    const formatDateTime = (dateString) => {
      const options = { 
        day: 'numeric', 
        month: 'long', 
        year: 'numeric', 
        hour: '2-digit', 
        minute: '2-digit' 
      };
      return new Date(dateString).toLocaleDateString('ru-RU', options);
    };

    const showNotification = (message, type = 'success') => {
      notification.value = { show: true, message, type };
      setTimeout(() => {
        notification.value.show = false;
      }, 3000);
    };

    const loadHistory = async () => {
      loadingHistory.value = true;
      
      try {
        const { data: userData, error } = await supabase
          .from('users')
          .select('transfers_history, sales_history, market_history')
          .eq('name', currentAccountName.value)
          .single();

        if (error) throw error;

        if (userData) {
          transfersHistory.value = (userData.transfers_history || [])
            .sort((a, b) => new Date(b.date) - new Date(a.date));
          
          salesHistory.value = (userData.sales_history || [])
            .sort((a, b) => new Date(b.date) - new Date(a.date));
          
          marketHistory.value = (userData.market_history || [])
            .sort((a, b) => new Date(b.date) - new Date(a.date));
        }
        
      } catch (error) {
        console.error('Ошибка загрузки истории:', error);
        showNotification('Ошибка загрузки истории операций', 'error');
      } finally {
        loadingHistory.value = false;
      }
    };

    const initiateCancelSale = (item) => {
      cancelSaleModal.value = {
        show: true,
        id: item.id,
        nftType: item.nft_type,
        amount: item.amount
      };
    };

    const executeCancelSale = async () => {
      try {
        const { id, nftType, amount } = cancelSaleModal.value;
        
        const { data: userData, error: fetchError } = await supabase
          .from('users')
          .select('*')
          .eq('name', currentAccountName.value)
          .single();
        
        if (fetchError) throw fetchError;

        const { error: deleteError } = await supabase
          .from('market')
          .delete()
          .eq('id', id);
        
        if (deleteError) throw deleteError;

        const updates = {
          [nftType]: (userData[nftType] || 0) + amount
        };

        const { error: updateError } = await supabase
          .from('users')
          .update(updates)
          .eq('name', currentAccountName.value);
        
        if (updateError) throw updateError;
        
        const cancelRecord = {
          nft_type: nftType,
          amount: amount,
          price_per_unit: 0,
          seller: currentAccountName.value,
          date: new Date().toISOString(),
          type: 'cancel'
        };

        const { error: historyError } = await supabase
          .from('users')
          .update({
            market_history: [cancelRecord, ...marketHistory.value]
          })
          .eq('name', currentAccountName.value);

        if (historyError) throw historyError;
        
        nfts.value[nftType] = (nfts.value[nftType] || 0) + amount;
        marketHistory.value = [cancelRecord, ...marketHistory.value];
        
        await loadMarketItems();
        
        showNotification(`NFT успешно сняты с продажи!`, 'success');
        cancelSaleModal.value.show = false;
        
      } catch (error) {
        console.error('Ошибка снятия с продажи:', error);
        showNotification('Ошибка при снятии NFT с продажи: ' + error.message, 'error');
      }
    };

    const initiateTransfer = (nftType) => {
      transferModal.value = {
        show: true,
        nftType,
        recipientName: '',
        amount: '',
        confirmStep: false
      };
      recipientCheck.value = { loading: false, exists: false };
    };

    const showConfirmation = () => {
      if (!transferModal.value.recipientName || !recipientCheck.value.exists) {
        showNotification('Пожалуйста, укажите действительного получателя', 'error');
        return;
      }
      
      if (!transferModal.value.amount || transferModal.value.amount < 1) {
        showNotification('Пожалуйста, укажите корректное количество', 'error');
        return;
      }
      
      transferModal.value.confirmStep = true;
    };

    const executeTransfer = async () => {
      try {
        const { nftType, recipientName, amount } = transferModal.value;
        const numAmount = Number(amount);
        
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

        if (sender[nftType] < numAmount) {
          throw new Error('Недостаточно NFT для передачи');
        }

        const transferRecord = {
          nft_type: nftType,
          amount: numAmount,
          sender: currentAccountName.value,
          recipient: recipientName,
          date: new Date().toISOString()
        };

        const senderUpdates = {
          [nftType]: sender[nftType] - numAmount,
          transfers_history: [transferRecord, ...(sender.transfers_history || [])]
        };

        const recipientUpdates = {
          [nftType]: (recipient[nftType] || 0) + numAmount,
          transfers_history: [transferRecord, ...(recipient.transfers_history || [])]
        };

        const { error: updateError } = await supabase
          .from('users')
          .upsert([
            { id: sender.id, ...senderUpdates },
            { id: recipient.id, ...recipientUpdates }
          ]);

        if (updateError) throw updateError;

        nfts.value[nftType] -= numAmount;
        if (nfts.value[nftType] <= 0) {
          delete nfts.value[nftType];
        }

        transfersHistory.value = [transferRecord, ...transfersHistory.value];
        showNotification('NFT успешно переданы!');
        transferModal.value.show = false;

      } catch (error) {
        console.error('Transfer failed:', error);
        showNotification(`Ошибка передачи: ${error.message}`, 'error');
      }
    };

    const initiateSell = (nftType) => {
      sellModal.value = {
        show: true,
        nftType,
        amount: '',
        price: isTONNFT(nftType) ? nftPricesInTON[nftType] : nftPrices[nftType] || 0,
        confirmStep: false
      };
    };

    const showSellConfirmation = () => {
      const amount = Number(sellModal.value.amount);
      if (!amount || amount < 1 || amount > nfts.value[sellModal.value.nftType]) {
        showNotification('Пожалуйста, укажите корректное количество (от 1 до ' + nfts.value[sellModal.value.nftType] + ')', 'error');
        return;
      }

      const price = Number(sellModal.value.price);
      if (isNaN(price)) {
        showNotification('Цена должна быть числом', 'error');
        return;
      }

      if (isTONNFT(sellModal.value.nftType)) {
        if (price < 0.05) {
          showNotification('Минимальная цена для этого NFT - 0.05 TON', 'error');
          return;
        }
      } else {
        if (price < 1) {
          showNotification('Минимальная цена для этого NFT - 1 AMHSL', 'error');
          return;
        }
      }

      sellModal.value.confirmStep = true;
    };
    
    const executeSell = async () => {
      try {
        const nftType = sellModal.value.nftType;
        const amount = sellModal.value.amount;
        const price = sellModal.value.price;

        const numAmount = Number(amount);
        if (isNaN(numAmount)) {
          throw new Error('Некорректное количество');
        }

        const numPrice = Number(price);
        if (isNaN(numPrice)) {
          throw new Error('Некорректная цена');
        }

        const isTonNft = isTONNFT(nftType);
        const currency = isTonNft ? 'TON' : 'AMHSL';

        if (isTonNft && numPrice < 0.05) {
          throw new Error('Минимальная цена для TON NFT - 0.1 TON');
        } else if (!isTonNft && numPrice < 100) {
          throw new Error('Минимальная цена для AMHSL NFT - 100 AMHSL');
        }

        const { data: userData, error: fetchError } = await supabase
          .from('users')
          .select('*')
          .eq('name', currentAccountName.value)
          .single();
        
        if (fetchError) throw fetchError;
        if (!userData) throw new Error('Пользователь не найден');
        if (userData[nftType] < numAmount) {
          throw new Error(`Недостаточно NFT для продажи (доступно: ${userData[nftType]})`);
        }

        const { data: marketItem, error: marketError } = await supabase
          .from('market')
          .insert([{
            nft_type: nftType,
            seller: currentAccountName.value,
            amount: numAmount,
            price_per_unit: numPrice,
            total_price: numAmount * numPrice,
            currency: currency,
            created_at: new Date().toISOString()
          }])
          .select()
          .single();

        if (marketError) throw marketError;

        const saleRecord = {
          nft_type: nftType,
          amount: numAmount,
          price_per_unit: numPrice,
          currency: currency,
          date: new Date().toISOString()
        };

        const updates = {
          [nftType]: userData[nftType] - numAmount,
          sales_history: [saleRecord, ...(userData.sales_history || [])]
        };

        const { error: updateError } = await supabase
          .from('users')
          .update(updates)
          .eq('name', currentAccountName.value);
        
        if (updateError) throw updateError;

        nfts.value[nftType] -= numAmount;
        if (nfts.value[nftType] <= 0) {
          delete nfts.value[nftType];
        }
        
        salesHistory.value = [saleRecord, ...salesHistory.value];
        
        await loadMarketItems();
        
        showNotification(`${numAmount} ${getNftDisplayName(nftType)} успешно выставлены на рынок за ${numPrice} ${currency} каждый!`, 'success');
        sellModal.value.show = false;
        
      } catch (error) {
        console.error('Ошибка продажи:', error);
        showNotification('Ошибка при выставлении NFT на рынок: ' + (error.message || 'неизвестная ошибка'), 'error');
      }
    };

    const initiateBuy = (item) => {
      buyModal.value = {
        show: true,
        id: item.id,
        nftType: item.nft_type,
        seller: item.seller,
        amount: item.amount,
        pricePerUnit: item.price_per_unit,
        totalPrice: item.total_price,
        buyAmount: 1,
        currency: item.currency || 'AMHSL'
      };
    };

    const executeBuy = async () => {
      try {
        const { id, nftType, seller, buyAmount, pricePerUnit, currency } = buyModal.value;
        const numAmount = Number(buyAmount);
        const totalPrice = numAmount * pricePerUnit;
        const isTONPurchase = currency === 'TON';

        if (isTONPurchase && !props.tonConnectUI?.connected) {
          showNotification('Сначала подключите кошелек TON', 'error');
          return;
        }

        const { data: buyerData, error: buyerError } = await supabase
          .from('users')
          .select('*')
          .eq('name', currentAccountName.value)
          .single();

        if (buyerError) throw new Error('Ошибка получения данных покупателя');

        if (isTONPurchase) {
          const currentBalance = Number(buyerData.ton_balance || 0);
          if (currentBalance < totalPrice) {
            showNotification(`Недостаточно TON. Ваш баланс: ${currentBalance} TON`, 'error');
            return;
          }
        } else {
          if ((buyerData.score || 0) < totalPrice) {
            showNotification('Недостаточно AMHSL для покупки', 'error');
            return;
          }
        }

        const { data: marketItem, error: marketError } = await supabase
          .from('market')
          .select('*')
          .eq('id', id)
          .single();

        if (marketError || !marketItem) throw new Error('Объявление не найдено');

        const { error: deleteError } = await supabase
          .from('market')
          .delete()
          .eq('id', id);

        if (deleteError) throw new Error('Ошибка удаления объявления');

        const buyerUpdates = {
          [nftType]: (buyerData[nftType] || 0) + numAmount,
          market_history: [...(buyerData.market_history || []), {
            nft_type: nftType,
            amount: numAmount,
            price_per_unit: pricePerUnit,
            seller: seller,
            date: new Date().toISOString(),
            type: 'buy',
            currency: currency
          }]
        };

        if (isTONPurchase) {
          buyerUpdates.ton_balance = Number(buyerData.ton_balance || 0) - totalPrice;
        } else {
          buyerUpdates.score = Number(buyerData.score || 0) - totalPrice;
        }

        const { data: sellerData, error: sellerError } = await supabase
          .from('users')
          .select('*')
          .eq('name', seller)
          .single();

        if (sellerError) throw new Error('Ошибка получения данных продавца');

        const sellerUpdates = {
          market_history: [...(sellerData.market_history || []), {
            nft_type: nftType,
            amount: numAmount,
            price_per_unit: pricePerUnit,
            buyer: currentAccountName.value,
            date: new Date().toISOString(),
            type: 'sell',
            currency: currency
          }]
        };

        if (isTONPurchase) {
          sellerUpdates.ton_balance = Number(sellerData.ton_balance || 0) + totalPrice;
        } else {
          sellerUpdates.score = Number(sellerData.score || 0) + totalPrice;
        }

        const { error: updateError } = await supabase
          .from('users')
          .upsert([
            { id: buyerData.id, ...buyerUpdates },
            { id: sellerData.id, ...sellerUpdates }
          ]);

        if (updateError) throw new Error('Ошибка обновления балансов');

        tonBalance.value = isTONPurchase ? buyerUpdates.ton_balance : tonBalance.value;
        userScore.value = isTONPurchase ? userScore.value : buyerUpdates.score;
        nfts.value[nftType] = (nfts.value[nftType] || 0) + numAmount;
        marketItems.value = marketItems.value.filter(item => item.id !== id);

        showNotification(`Успешная покупка! Получено ${numAmount} ${getNftDisplayName(nftType)}`, 'success');
        buyModal.value.show = false;

      } catch (error) {
        console.error('Ошибка покупки:', error);
        showNotification(`Ошибка: ${error.message}`, 'error');
      }
    };

    const setActiveTab = (tab) => {
      activeTab.value = tab;
      if (tab === 'market') {
        loadMarketItems();
      }
    };

    const showItemDetails = (item) => {
      itemDetailsModal.value = {
        show: true,
        item,
        startY: 0,
        currentY: 0,
        isDragging: false
      };
      
      nextTick(() => {
        const modal = document.querySelector('.item-details-modal-content');
        if (modal) modal.style.transform = '';
      });
    };

    const startDrag = (e) => {
      isDraggingModal.value = true;
      dragStartY.value = e.clientY ?? e.touches[0].clientY;
      
      document.addEventListener('mousemove', handleDrag);
      document.addEventListener('mouseup', stopDrag);
      document.addEventListener('touchmove', handleDrag, { passive: false });
      document.addEventListener('touchend', stopDrag);
    };

    const handleDrag = (e) => {
      if (!isDraggingModal.value) return;
      e.preventDefault();
      
      const clientY = e.clientY ?? e.touches[0].clientY;
      dragCurrentY.value = clientY - dragStartY.value;
      
      itemDetailsModal.value.offset = Math.max(0, dragCurrentY.value);
    };

    const stopDrag = () => {
      isDraggingModal.value = false;
      
      if (dragCurrentY.value > 100) {
        itemDetailsModal.value.show = false;
      }
      
      document.removeEventListener('mousemove', handleDrag);
      document.removeEventListener('mouseup', stopDrag);
      document.removeEventListener('touchmove', handleDrag);
      document.removeEventListener('touchend', stopDrag);
      
      itemDetailsModal.value.offset = 0;
    };

    const handleModalClose = (e) => {
      if (e.target.classList.contains('item-details-modal-overlay')) {
        itemDetailsModal.value.show = false;
      }
    };

    const fetchTonBalance = async () => {
      try {
        if (!currentAccountName.value) return;
        
        const { data, error } = await supabase
          .from('users')
          .select('ton_balance')
          .eq('name', currentAccountName.value)
          .single();
          
        if (error) throw error;
        
        tonBalance.value = String(data?.ton_balance || '0');
      } catch (error) {
        console.error('Ошибка получения баланса TON:', error);
        tonBalance.value = '0';
      }
    };

    const updateTonBalance = async (newBalance) => {
      try {
        if (!currentAccountName.value) return;
        
        const { error } = await supabase
          .from('users')
          .update({ ton_balance: newBalance })
          .eq('name', currentAccountName.value);
          
        if (!error) {
          tonBalance.value = newBalance;
        }
      } catch (error) {
        console.error('Ошибка обновления баланса TON:', error);
      }
    };

    const loadUserData = async () => {
      loading.value = true;
      
      try {
        const { data, error } = await supabase
          .from('users')
          .select('nft1, nft2, nft3, nft4, nft5, nft6, nft7, nft8, nft9, nft10, score, ton_balance, transfers_history, sales_history, market_history')
          .eq('name', currentAccountName.value)
          .single();
        
        if (error) throw error;

        if (data) {
          nfts.value = Object.fromEntries(
            Object.entries(data).filter(([key, value]) => key.startsWith('nft') && value > 0)
          );
          userScore.value = data.score || 0;
          tonBalance.value = String(data.ton_balance || '0');
          
          transfersHistory.value = (data.transfers_history || [])
            .sort((a, b) => new Date(b.date) - new Date(a.date));
          
          salesHistory.value = (data.sales_history || [])
            .sort((a, b) => new Date(b.date) - new Date(a.date));
          
          marketHistory.value = (data.market_history || [])
            .sort((a, b) => new Date(b.date) - new Date(a.date));
        }
        
      } catch (error) {
        console.error('Ошибка загрузки:', error);
        showNotification('Ошибка загрузки данных', 'error');
      } finally {
        loading.value = false;
      }
    };

    const goBack = () => {
      router.go(-1);
    };

    // Инициализация компонента
    onMounted(async () => {
      const savedAccount = localStorage.getItem('currentAccount');
      if (savedAccount) {
        currentAccountName.value = JSON.parse(savedAccount).name;
      }
      
      if (currentAccountName.value) {
        await loadUserData();
        await loadMarketItems();
        
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

      watch(() => props.tonConnectUI?.connected, (connected) => {
        if (connected) {
          fetchTonBalance();
        } else {
          tonBalance.value = '0';
        }
      }, { immediate: true });
    });

    return {
      tonBalance,
      activeTab,
      nfts,
      loading,
      marketLoading,
      currentAccountName,
      showHistory,
      historyTab,
      filteredSales: computed(() => salesHistory.value),
      filteredTransfers: computed(() => transfersHistory.value),
      marketHistory,
      marketItems,
      filteredMarketItems,
      notification,
      transferModal,
      sellModal,
      buyModal,
      cancelSaleModal,
      recipientCheck,
      itemDetailsModal,
      showFilterDropdown,
      searchQuery,
      selectedNftTypes,
      filteredEasterEggNfts,
      filteredFeaturedNfts,
      setActiveTab,
      getNftDisplayName,
      getNftImage,
      isTONNFT,
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
      initiateCancelSale,
      executeCancelSale,
      initiateTransfer,
      showConfirmation,
      executeTransfer,
      initiateSell,
      showSellConfirmation,
      executeSell,
      initiateBuy,
      executeBuy,
      loadMarketItems,
      goBack,
      showItemDetails,
      startDrag,
      stopDrag,
      handleModalClose,
      handleDrag,
      toggleFilterDropdown,
      toggleNftFilter
    };
  }
};
</script>
<style scoped>

.nft-icon{
  max-width:200px ;
  max-height: 200px;
}
/* Обновленные стили для контейнера баланса и фильтра */
.balance-filter-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  gap: 10px;
}

/* Стили для кнопки баланса (голубой) */
.ton-balance {
  background-color: #0088cc; /* Голубой цвет */
  color: white;
  border: none;
  border-radius: 8px;
  padding: 10px 15px;
  font-weight: bold;
  flex: 1;
  text-align: center;
  min-height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Стили для кнопки фильтра (жёлтый) */
.filter-button {
  width: 100%;
  padding: 10px 15px;
  background-color: #ffc400; /* Жёлтый цвет */
  color: black;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  min-height: 40px;
}

.filter-container {
  position: relative;
  flex: 1;
  z-index: 100;
}

.filter-dropdown {
  position: absolute;
  top: calc(100% + 10px);
  left: 0;
  right: 0;
  background-color: #2c2c2c;
  border: 1px solid #444;
  border-radius: 8px;
  z-index: 100;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  max-height: 0;
  overflow: hidden;
  transition: all 0.3s ease-out;
  transform-origin: top;
  opacity: 0;
  transform: translateY(-20px);
  padding: 0;
}

.filter-dropdown.open {
  max-height: 400px;
  padding: 10px;
  opacity: 1;
  transform: translateY(0);
  overflow-y: auto;
}

/* Анимация содержимого внутри открытого дропдауна */
.filter-dropdown.open .filter-section {
  animation: fadeIn 0.2s ease-out 0.1s forwards;
  opacity: 0;
}

@keyframes fadeIn {
  to {
    opacity: 1;
  }
}

/* Остальные стили остаются такими же */
.filter-button {
  width: 100%;
  padding: 10px 15px;
  background-color: #ffc400;
  color: black;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  min-height: 40px;
}

.filter-icon {
  transition: transform 0.3s;
}

.filter-button.active .filter-icon {
  transform: rotate(180deg);
}


.search-box {
  padding: 10px;
  border-bottom: 1px solid #3d3d3d;
}

.search-input {
  width: 100%;
  padding: 8px 12px;
  background-color: #3a3a3a;
  border: 1px solid #555;
  border-radius: 6px;
  color: white;
}

.search-input::placeholder {
  color: #888;
}

.filter-section {
  padding: 5px 0;
}

.filter-category {
  margin-bottom: 10px;
}

.category-header {
  padding: 8px 15px;
  font-weight: bold;
  color: #ffc400;
  background-color: #363636;
  display: flex;
  align-items: center;
}

.new-badge {
  margin-left: 8px;
  font-size: 0.8em;
  background-color: #ff4757;
  color: white;
  padding: 2px 6px;
  border-radius: 10px;
}

.filter-item {
  padding: 10px 15px;
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: background-color 0.2s;
}

.filter-item:hover {
  background-color: #3a3a3a;
}

.filter-item.selected {
  background-color: rgba(255, 196, 0, 0.1);
}

.nft-icon {
  width: 24px;
  height: 24px;
  margin-right: 10px;
  border-radius: 4px;
}

.nft-name {
  flex-grow: 1;
  color: #e0e0e0;
}

.checkmark {
  color: #ffc400;
  font-weight: bold;
}
.filter-nft-image{
  max-width: 100px;
  max-height: 100px
}
/* Добавьте эти стили */
.balance-filter-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  gap: 10px;
}

.filter-container {
  position: relative;
}


.filter-icon {
  font-size: 0.8rem;
  transition: transform 0.2s;
}

.filter-button:hover .filter-icon {
  transform: translateY(2px);
}

.filter-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  background-color: #2c2c2c;
  border: 1px solid #444;
  border-radius: 6px;
  padding: 5px 0;
  z-index: 10;
  box-shadow: 0 2px 10px rgba(0,0,0,0.2);
  min-width: 120px;
}

.filter-option {
  padding: 8px 12px;
  cursor: pointer;
  color: #ddd;
  font-size: 0.9rem;
}

.filter-option:hover {
  background-color: #3a3a3a;
}

.filter-option.active {
  color: #ffc400;
  font-weight: bold;
}
/* Стиль для кнопки продажи TON NFT */
.sell-button.ton {
  background-color: #0088cc; /* Голубой цвет для TON */
  color: white;
}

/* Стиль для кнопки продажи AMHSL NFT */
.sell-button:not(.ton) {
  background-color: #ffbb00; /* Желтый цвет для AMHSL */
  color: black;
}



.currency-icon {
  max-width: 25px;
  max-height: 25px;
  vertical-align: middle;
  margin-left: -1px;
  margin-top: -2px; /* Поднимаем иконку на 2px */
  display: inline-block;
}

/* Эффекты при наведении */
.transfer-button:hover:not(:disabled),
.sell-button:hover:not(:disabled) {
  opacity: 0.9;
  transform: translateY(-1px) scale(1.05);
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}

/* Эффекты при нажатии */
.transfer-button:active:not(:disabled),
.sell-button:active:not(:disabled) {
  transform: translateY(1px) scale(0.98);
}

.transfer-button:disabled, 
.sell-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: scale(1);
}

/* Обновление класса для TON NFT */
.ton-nft .sell-button {
  background-color: #0088cc;
  color: white;
}

.ton-nft .nft-price {
  color: #0088cc;
}


.market-item.ton .item-actions .buy-button {
  background-color: #0088cc;
  color: white;
}

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

.ton.nft-price{
  color: #008cff;
  font-weight: bold;
}

.nft-price{
  color: #ffbb00;
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
  padding: 8px 12px;
  background-color: #149918; /* Зеленый цвет */
  color: rgb(255, 255, 255);
  font-weight: 600;
  border: none;
  border-radius: 5px;
  font-size: 0.9rem;
  cursor: pointer;
  flex: 1;
  transition: all 0.2s;
  transform: scale(1);
}

.sell-button {
  padding: 8px 12px;
  background-color: #ffc400; /* Желтый цвет по умолчанию (для AMHSL) */
  color: #000;
  font-weight: 600;
  border: none;
  border-radius: 5px;
  font-size: 0.9rem;
  cursor: pointer;
  flex: 1;
  transition: all 0.2s;
  transform: scale(1);
}

.transfer-button:hover:not(:disabled),
.sell-button:hover:not(:disabled) {
  opacity: 0.9;
  transform: translateY(-1px) scale(1.05);
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}

/* Эффекты при нажатии */
.transfer-button:active:not(:disabled),
.sell-button:active:not(:disabled) {
  transform: translateY(1px) scale(0.98);
}

.transfer-button:disabled, 
.sell-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: scale(1);
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

