<template>
  <div class="activity-page">
      <div class="back-button-container">

<button class="modern-back-button" @click="handleBack">
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
    <path d="M15 18L9 12L15 6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
  </svg>
</button>
    </div>

    <!-- Система фильтров -->
    <div class="filter-system" v-click-outside="() => closeFilterMenu()">
      <div class="filter-categories-container" ref="categoriesContainer">
        <div class="filter-categories-scroll">
          <button 
            v-for="category in filterCategories"
            :key="category.id"
            class="filter-category-btn"
            :class="{ active: activeFilterCategory === category.id }"
            @click="setActiveFilter($event, category.id)"
            ref="filterButtons"
          >
            {{ category.name }}
          </button>
        </div>

        <!-- Symbol Filter Dropdown -->
        <transition name="filter-dropdown">
          <div 
            class="filter-dropdown-menu filter-dropdown-menu-nft"
            v-if="activeFilterCategory === 'symbol'"
            @touchstart.passive="handleTouchStart"
            @mousedown="handleMouseDown"
          >
            <div 
              class="modal-drag-handle"
              @touchstart="startDrag"
              @mousedown="startDrag"
            ></div>
          
            <div class="filter-header">
              <div class="search-box">
                <input 
                  v-model="searchQuery" 
                  type="text" 
                  placeholder="Search Symbols..." 
                  class="search-input"
                >
              </div>
              <button class="clear-filter-btn" @click="clearFilterCategory('symbol')" 
                      :disabled="selectedFilters.symbol.length === 0">
                Clear
              </button>
            </div>
            
            <div v-if="symbolsLoading" class="loading-symbols">
              Loading symbols...
            </div>
            
            <div class="filter-options-container" v-else>
              <!-- Сначала показываем выбранные символы -->
              <div 
                v-for="symbol in getSelectedSymbolOptions()"
                :key="'selected-' + symbol.value + '-' + forceUpdate"
                class="filter-option selected"
                @click.stop="toggleFilterOption('symbol', symbol.name)"
              >
                <div class="symbol-html-container">
                  <iframe 
                    v-if="symbol.htmlContent"
                    :srcdoc="symbol.htmlContent"
                    class="symbol-html-iframe"
                    sandbox="allow-scripts allow-same-origin"
                    @load="onSymbolIframeLoad(symbol.name)"
                    @error="onSymbolIframeError(symbol.name)"
                  ></iframe>
                  <div v-else class="symbol-placeholder">
                    🎨
                    <div class="loading-text">Loading...</div>
                  </div>
                </div>
                <div class="option-content">
                  <span class="option-text">{{ symbol.name }}</span>
                  <span class="option-count" v-if="symbol.count">({{ symbol.count }})</span>
                  <span v-if="symbol.floorPrice" class="floor-price">
                    {{ symbol.floorPrice.toFixed(1) }} 
                    <img :src="tonlogofloor" alt="TON" class="ton-floor-icon">
                  </span>
                  <span v-else class="floor-price no-floor"></span>
                  <span class="option-rarity" :class="symbol.rarityClass">
                    {{ symbol.rarityText }}
                  </span>
                </div>
              </div>
              
              <!-- Аналогично для невыбранных символов -->
              <div 
                v-for="symbol in getUnselectedSymbolOptions()"
                :key="'unselected-' + symbol.value + '-' + forceUpdate"
                class="filter-option"
                :class="{ selected: isOptionSelected('symbol', symbol.name) }"
                @click.stop="toggleFilterOption('symbol', symbol.name)"
              >
                <div class="symbol-html-container">
                  <iframe 
                    v-if="symbol.htmlContent"
                    :srcdoc="symbol.htmlContent"
                    class="symbol-html-iframe"
                    sandbox="allow-scripts allow-same-origin"
                    @load="onSymbolIframeLoad(symbol.name)"
                    @error="onSymbolIframeError(symbol.name)"
                  ></iframe>
                  <div v-else class="symbol-placeholder">
                    🎨
                    <div class="loading-text">Loading...</div>
                  </div>
                </div>
                <div class="option-content">
                  <span class="option-text">{{ symbol.name }}</span>
                  <span class="option-count" v-if="symbol.count">({{ symbol.count }})</span>
                  <span v-if="symbol.floorPrice" class="floor-price">
                    {{ symbol.floorPrice.toFixed(1) }} 
                    <img :src="tonlogofloor" alt="TON" class="ton-floor-icon">
                  </span>
                  <span v-else class="floor-price no-floor"></span>
                  <span class="option-rarity" :class="symbol.rarityClass">
                    {{ symbol.rarityText }}
                  </span>
                </div>
                <span 
                  v-if="isOptionSelected('symbol', symbol.name)"
                  class="checkmark"
                ></span>
              </div>
              
              <div v-if="getFilteredSymbols().length === 0" class="no-symbols-message">
                Symbols not found
              </div>
            </div>
          </div>
        </transition>

<!-- NFT Filter Dropdown -->
<transition name="filter-dropdown">
  <div 
    class="filter-dropdown-menu filter-dropdown-menu-nft"
    v-if="activeFilterCategory === 'nft'"
    @touchstart.passive="handleTouchStart"
    @mousedown="handleMouseDown"
  >
    <div 
      class="modal-drag-handle"
      @touchstart="startDrag"
      @mousedown="startDrag"
    ></div>
  
    <div class="filter-header">
      <div class="search-box">
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="Search NFTs..." 
          class="search-input"
        >
      </div>
      <button class="clear-filter-btn" @click="clearFilterCategory('nft')" 
              :disabled="selectedFilters.nft.length === 0">
        Clear
      </button>
    </div>
    
    <div class="filter-options-container">
      <!-- Выбранные опции -->
      <div 
        v-for="option in getSelectedNftOptions()"
        :key="'selected-' + option.originalType"
        class="filter-option selected"
        @click.stop="toggleFilterOption('nft', option.originalType)"
      >
        <img 
          :src="option.imageUrl" 
          :alt="option.name" 
          class="option-image"
          @error="(event) => handleNftImageError(event, option.name)"
        >
        <div class="option-content">
          <span class="option-text">{{ option.name }}</span>
          <span v-if="option.floorPrice" class="floor-price">
            {{ option.floorPrice.toFixed(1) }} 
            <img :src="tonlogofloor" alt="TON" class="ton-floor-icon">
          </span>
          <span v-else class="floor-price no-floor"></span>
        </div>
      </div>
      
      <!-- Невыбранные опции -->
      <div 
        v-for="option in getUnselectedNftOptions()"
        :key="'unselected-' + option.originalType"
        class="filter-option"
        :class="{ selected: isOptionSelected('nft', option.originalType) }"
        @click.stop="toggleFilterOption('nft', option.originalType)"
      >
        <img 
          :src="option.imageUrl" 
          :alt="option.name" 
          class="option-image"
          @error="(event) => handleNftImageError(event, option.name)"
        >
        <div class="option-content">
          <span class="option-text">{{ option.name }}</span>
          <span v-if="option.floorPrice" class="floor-price">
            {{ option.floorPrice.toFixed(1) }} 
            <img :src="tonlogofloor" alt="TON" class="ton-floor-icon">
          </span>
          <span v-else class="floor-price no-floor"></span>
        </div>
        <span 
          v-if="isOptionSelected('nft', option.originalType)"
          class="checkmark"
        ></span>
      </div>
      
      <div v-if="getSortedNftOptions().length === 0" class="no-nft-message">
        NFTs not found
      </div>
    </div>
  </div>
</transition>

        <!-- Model Filter Dropdown -->
        <transition name="filter-dropdown">
          <div 
            class="filter-dropdown-menu filter-dropdown-menu-model"
            v-if="activeFilterCategory === 'model'"
            @touchstart.passive="handleTouchStart"
            @mousedown="handleMouseDown"
          >
            <div 
              class="modal-drag-handle"
              @touchstart="startDrag"
              @mousedown="startDrag"
            ></div>
          
            <div class="filter-header">
              <div class="search-box">
                <input 
                  v-model="modelSearchQuery" 
                  type="text" 
                  placeholder="Search Models..." 
                  class="search-input"
                >
              </div>
              <button class="clear-filter-btn" @click="clearFilterCategory('model')" 
                      :disabled="selectedFilters.model.length === 0">
                Clear
              </button>
            </div>

            <!-- Кнопки переключения режимов -->
            <div class="display-mode-buttons">
              <button 
                class="mode-button"
                :class="{ active: displayMode === 'list' }"
                @click="setDisplayMode('list')"
              >
                <i class="icon-list"></i> List
              </button>
              <button 
                class="mode-button"
                :class="{ active: displayMode === 'grouped' }"
                @click="setDisplayMode('grouped')"
              >
                <i class="icon-group"></i> Groups
              </button>
            </div>

            <template v-if="selectedFilters.nft.length > 0">
              <div class="filter-options-container">
                <!-- Режим списка -->
                <template v-if="displayMode === 'list'">
                  <div class="models">
                    <div v-if="modelsLoading" class="loading-models">
                      Loading models...
                    </div>
                    <template v-else>
                      <!-- Сначала показываем выбранные модели -->
                      <div 
                        v-for="modelData in getSelectedModelOptions()"
                        :key="'selected-' + modelData.name"
                        class="filter-option selected"
                        @click.stop="toggleFilterOption('model', modelData.name)"
                      >
                          <img 
                            :src="getOptionImageUrl(modelData.parentNft, modelData.name)" 
                            :alt="modelData.name" 
                            class="option-image"
                            @error="handleImageError"
                          >
                        <div class="option-content">
                          <span class="option-text">{{ modelData.name }}</span>
                          <span v-if="modelData.floorPrice" class="floor-price">
                            {{ modelData.floorPrice.toFixed(1) }} 
                            <img :src="tonlogofloor" alt="TON" class="ton-floor-icon">
                          </span>
                          <span v-else class="floor-price no-floor"></span>
                          <span class="option-rarity">{{ modelData.rarityText }}</span>
                        </div>
                        <span class="checkmark"></span>
                      </div>
                      
                      <!-- Затем невыбранные модели -->
                      <div 
                        v-for="modelData in getUnselectedModelOptions()"
                        :key="'unselected-' + modelData.name"
                        class="filter-option"
                        :class="{ selected: isOptionSelected('model', modelData.name) }"
                        @click.stop="toggleFilterOption('model', modelData.name)"
                      >
                        <img 
                          :src="getOptionImageUrl(modelData.parentNft, modelData.name)" 
                          :alt="modelData.name" 
                          class="option-image"
                          @error="handleImageError"
                        >
                        <div class="option-content">
                          <span class="option-text">{{ modelData.name }}</span>
                          <span v-if="modelData.floorPrice" class="floor-price">
                            {{ modelData.floorPrice.toFixed(1) }} 
                            <img :src="tonlogofloor" alt="TON" class="ton-floor-icon">
                          </span>
                          <span v-else class="floor-price no-floor"></span>
                          <span class="option-rarity">{{ modelData.rarityText }}</span>
                        </div>
                        <span 
                          v-if="isOptionSelected('model', modelData.name)"
                          class="checkmark"
                        ></span>
                      </div>
                      
                      <div v-if="getAllModelDataSortedByRarity().length === 0" class="no-models-message">
                        No models available
                      </div>
                    </template>
                  </div>
                </template>

                <!-- Режим групп -->
                <template v-else>
                  <div class="models">
                    <div 
                      v-for="nftType in selectedFilters.nft"
                      :key="nftType"
                      class="nft-group"
                    >
                      <div 
                        class="nft-group-header"
                        @click="toggleNftGroup(nftType)"
                      >
                        <span class="group-nft-name">{{ getNftDisplayNameForGroup(nftType) }}</span>
                        <span class="group-toggle-icon">
                          {{ expandedNftGroups[nftType] ? '−' : '+' }}
                        </span>
                      </div>
                      
                      <transition name="expand">
                        <div 
                          v-if="expandedNftGroups[nftType]"
                          class="nft-group-models"
                        >
                          <!-- Сначала выбранные модели в группе -->
                          <div 
                            v-for="model in getSelectedModelsInGroup(nftType)"
                            :key="'selected-' + model.name"
                            class="filter-option model-option selected"
                            @click.stop="toggleFilterOption('model', model.name)"
                          >
                            <img 
                              :src="getOptionImageUrl(modelData.parentNft, modelData.name)" 
                              :alt="modelData.name" 
                              class="option-image"
                              @error="handleImageError"
                            >
                            <div class="option-content">
                              <span class="option-text">{{ model.name }}</span>
                              <span v-if="model.floorPrice" class="floor-price">
                                {{ model.floorPrice.toFixed(1) }} 
                                <img :src="tonlogofloor" alt="TON" class="ton-floor-icon">
                              </span>
                              <span v-else class="floor-price no-floor"></span>
                              <span class="option-rarity">{{ model.rarityText }}</span>
                            </div>
                            <span class="checkmark"></span>
                          </div>
                          
                          <!-- Затем невыбранные модели в группе -->
                          <div 
                            v-for="model in getUnselectedModelsInGroup(nftType)"
                            :key="'unselected-' + model.name"
                            class="filter-option model-option"
                            :class="{ selected: isOptionSelected('model', model.name) }"
                            @click.stop="toggleFilterOption('model', model.name)"
                          >
                            <img 
                              :src="getOptionImageUrl(modelData.parentNft, modelData.name)" 
                              :alt="modelData.name" 
                              class="option-image"
                              @error="handleImageError"
                            >
                            <div class="option-content">
                              <span class="option-text">{{ model.name }}</span>
                              <span v-if="model.floorPrice" class="floor-price">
                                {{ model.floorPrice.toFixed(1) }} 
                                <img :src="tonlogofloor" alt="TON" class="ton-floor-icon">
                              </span>
                              <span v-else class="floor-price no-floor"></span>
                              <span class="option-rarity">{{ model.rarityText }}</span>
                            </div>
                            <span 
                              v-if="isOptionSelected('model', model.name)"
                              class="checkmark"
                            ></span>
                          </div>
                          
                          <!-- Сообщение если в группе нет моделей -->
                          <div 
                            v-if="getGroupedModelOptions()[nftType] && getGroupedModelOptions()[nftType].length === 0" 
                            class="no-models-in-group"
                          >
                            No models found in this group
                          </div>
                        </div>
                      </transition>
                    </div>
                    
                    <!-- Сообщение если нет групп -->
                    <div 
                      v-if="selectedFilters.nft.length === 0" 
                      class="no-groups-message"
                    >
                      Please select at least one NFT first
                    </div>
                  </div>
                </template>
              </div>
            </template>
            <div v-else class="no-nft-selected">
              Please select at least one NFT first
            </div>
          </div>
        </transition>

        <!-- Price Filter Dropdown -->
        <transition name="filter-dropdown">
          <div 
            class="filter-dropdown-menu-indiv filter-dropdown-menu-id"
            v-if="activeFilterCategory === 'price'"
          >
            <div class="search-box">
              <input 
                v-model="idFilterValue" 
                type="number" 
                placeholder="Enter Gift ID..." 
                class="search-input"
                @keyup.enter="applyIdFilter"
              >
            </div>
            
            <div class="id-filter-status" v-if="selectedIdFilter !== null">
              <span>Active filter: ID {{ selectedIdFilter }}</span>
            </div>
            
            <button class="apply-id-filter-btn" @click="applyIdFilter" :disabled="!idFilterValue">
              Apply Filter
            </button>
            <button class="clear-id-filter-btn" @click="clearIdFilter" v-if="selectedIdFilter !== null">
              Clear Filter
            </button>
          </div>
        </transition>

        <!-- Backdrop Filter Dropdown -->
        <transition name="filter-dropdown">
          <div 
            class="filter-dropdown-menu filter-dropdown-menu-backdrop"
            v-if="activeFilterCategory === 'backdrop'"
            @touchstart.passive="handleTouchStart"
            @mousedown="handleMouseDown"
          >
            <div 
              class="modal-drag-handle"
              @touchstart="startDrag"
              @mousedown="startDrag"
            ></div>
          
            <div class="filter-header">
              <div class="search-box">
                <input 
                  v-model="backdropSearchQuery" 
                  type="text" 
                  placeholder="Search backdrops..." 
                  class="search-input"
                >
              </div>
              <button class="clear-filter-btn" @click="clearFilterCategory('backdrop')" 
                      :disabled="selectedFilters.backdrop.length === 0">
                Clear
              </button>
            </div>
            
            <div class="filter-options-container">
              <div 
                v-for="color in getSelectedBackdropOptions()"
                :key="'selected-' + color.id"
                class="filter-option backdrop-option selected"
                @click.stop="toggleFilterOption('backdrop', color.id)"
              >
                <div class="backdrop-icon-container">
                  <div 
                    class="backdrop-svg-wrapper"
                    v-html="color.svgContent"
                  ></div>
                </div>
                
                <div class="option-content">
                  <span class="option-text">{{ color.name }}</span>
                  <span class="option-count" v-if="color.count">({{ color.count }})</span>
                  <span v-if="color.floorPrice" class="floor-price">
                    {{ color.floorPrice }} 
                    <img :src="tonlogofloor" alt="TON" class="ton-floor-icon">
                  </span>
                  <span v-else class="floor-price no-floor"></span>
                  <span class="option-rarity">{{ color.rarityText }}</span>
                </div>
              </div>
              
              <div 
                v-for="color in getUnselectedBackdropOptions()"
                :key="'unselected-' + color.id"
                class="filter-option backdrop-option"
                :class="{ selected: isOptionSelected('backdrop', color.id) }"
                @click.stop="toggleFilterOption('backdrop', color.id)"
              >
                <div class="backdrop-icon-container">
                  <div 
                    class="backdrop-svg-wrapper"
                    v-html="color.svgContent"
                  ></div>
                </div>
                
                <div class="option-content">
                  <span class="option-text">{{ color.name }}</span>
                  <span class="option-count" v-if="color.count">({{ color.count }})</span>
                  <span v-if="color.floorPrice" class="floor-price">
                    {{ color.floorPrice }} 
                    <img :src="tonlogofloor" alt="TON" class="ton-floor-icon">
                  </span>
                  <span v-else class="floor-price no-floor"></span>
                  <span class="option-rarity">{{ color.rarityText }}</span>
                </div>
                
                <span 
                  v-if="isOptionSelected('backdrop', color.id)"
                  class="checkmark"
                ></span>
              </div>
            </div>
          </div>
        </transition>
      </div>
    </div>

<div v-if="htmlModal.show" class="fullscreen-view">
<button class="back-button" @click="handleBackButton">
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
    <path d="M15 18L9 12L15 6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
  </svg>
</button>
  
<div class="fullscreen-content">
<!-- В template секции, добавьте @click на iframe -->
<div class="html-container">
  <iframe 
    sandbox="allow-scripts allow-same-origin"
    :srcdoc="htmlModal.htmlContent"
    class="html-content-iframe"
    ref="htmlIframe"
  ></iframe>
</div>

  <!-- Добавьте этот блок с кнопками ПЕРЕД info-container -->
   
<div class="action-buttons-row">
  <!-- Кнопка корзины - неактивна если объявления нет в market -->
  <button 
    class="action-button-row"
    @click="toggleCartFromFullscreen"
    :disabled="!isItemOnMarket(htmlModal.item)"
    :title="!isItemOnMarket(htmlModal.item) ? 'Item not available on market' : (htmlModal.item && isInCart(htmlModal.item.id) ? 'Remove from cart' : 'Add to cart')"
    :class="{ 
      'in-cart': htmlModal.item && isInCart(htmlModal.item.id),
      'disabled': !isItemOnMarket(htmlModal.item)
    }"
  >
    <img 
      :src="htmlModal.item && isInCart(htmlModal.item.id) ? rubish_bucket : bucket_white_img" 
      :alt="htmlModal.item && isInCart(htmlModal.item.id) ? 'Remove from cart' : 'Add to cart'" 
      class="action-button-icon"
    >
  </button>

  <!-- Кнопка Telegram - всегда активна если есть ссылка -->
  <button 
    v-if="htmlModal.telegramLink" 
    class="action-button-row"
    @click="openTelegramLink(htmlModal.telegramLink)"
    title="Open in Telegram"
  >
    <img :src="telega" alt="Telegram" class="action-button-icon">
  </button>

  <!-- Кнопка поделиться - неактивна если объявления нет в market -->
  <button 
    class="action-button-row" 
    title="Share to Telegram"
    @click="shareToTelegram"
    :disabled="!isItemOnMarket(htmlModal.item)"
    :class="{ 'disabled': !isItemOnMarket(htmlModal.item) }"
  >
    <img :src="share" alt="Share to Telegram" class="action-button-icon">
  </button>

  <!-- Кнопка подарка - неактивна если объявления нет в market -->
  <button 
    class="action-button-row" 
    title="Send as Gift"
    @click="openGiftModal(htmlModal.item)"
    :disabled="!isItemOnMarket(htmlModal.item)"
    :class="{ 'disabled': !isItemOnMarket(htmlModal.item) }"
  >
    <img :src="giftbox" alt="Send as Gift" class="action-button-icon">
  </button>
</div>

  <!-- В fullscreen-view, секция info-container -->
<div class="info-container">
  <div class="item-info">
    <div class="info-grid">
      <!-- Показываем всегда если есть item -->
      <div v-if="htmlModal.item">
        <h3 class="info-item-name">
          <span class="info-label-name">{{ getNftDisplayName(htmlModal.item.nft_type, htmlModal.item.nft_object) || 'NFT' }}</span>
          <span class="info-value-id" v-if="extractNftId(htmlModal.item.nft_object)">
            #{{ extractNftId(htmlModal.item.nft_object) }}
          </span>
        </h3>
      </div>
      
      <!-- Показываем модель даже если "Не указано" -->
      <div class="info-item" v-if="htmlModal.model">
        <span class="info-label">Model:</span>
        <div class="info-value-container">
          <span class="info-value">{{ htmlModal.model }}</span>
          <span class="info-value-procent" v-if="htmlModal.modelPercentage && htmlModal.modelPercentage !== ''">
            {{ htmlModal.modelPercentage }}
          </span>
        </div>
      </div>

      <!-- Показываем символ даже если "Не указано" -->
      <div class="info-item" v-if="htmlModal.symbol">
        <span class="info-label">Symbol:</span>
        <div class="info-value-container">
          <span class="info-value">{{ htmlModal.symbol }}</span>
          <span class="info-value-procent" v-if="htmlModal.symbolPercentage && htmlModal.symbolPercentage !== ''">
            {{ htmlModal.symbolPercentage }}
          </span>
        </div>
      </div>

      <!-- Показываем фон даже если "Не указано" -->
      <div class="info-item" v-if="htmlModal.backdrop">
        <span class="info-label">Backdrop:</span>
        <div class="info-value-container">
          <span class="info-value">{{ htmlModal.backdrop }}</span>
          <span class="info-value-procent" v-if="htmlModal.backdropPercentage && htmlModal.backdropPercentage !== ''">
            {{ htmlModal.backdropPercentage }}
          </span>
        </div>
      </div>
    </div>
  </div>
</div>

<div class="action-buttons">
  <!-- Для полученных pending офферов -->
  <template v-if="htmlModal.item && 
                htmlModal.item.status === 'pending' && 
                htmlModal.item.seller_name === currentAccountName && 
                htmlModal.item.buyer_name !== currentAccountName">
  <div class="offer-action-button-container">
    <button 
      class="offer-action-button full-width"
      @click="openOfferBotLink"
    >
      <span class="button-text">Open Offer in Telegram Bot</span>
    </button>
  </div>
</template>

  <!-- КНОПКА ПЕРЕХОДА К ОБЪЯВЛЕНИЮ НА МАРКЕТЕ (под кнопками офферов) -->
  <div v-if="isCurrentItemOnMarket" class="market-action-button-container">
    <button 
      class="market-action-button full-width"
      @click="goToMarketItem(htmlModal.item)"
    >
      <span class="button-text">View Listing on Market</span>
    </button>
  </div>
</div>
  </div>
  <div class="fullscreen-modals">
    
    <!-- Make Offer Modal -->
<!-- Модальное окно создания предложения -->
<div v-if="offerModal.show" class="modal-dropdown-overlay fullscreen-modal" @click="offerModal.show = false">
  <div class="modal-dropdown fullscreen-modal-dropdown" @click.stop>
    <div class="modal-drag-handle"></div>
    
    <div class="modal-dropdown-header">
      <h3 class="modal-dropdown-title">Make an Offer</h3>
    </div>
    
    <div class="modal-dropdown-content">
      <!-- NFT Preview -->
      <div class="cart-item-preview">
        <div v-if="offerModal.item?.html_content" class="cart-item-html-wrapper">
          <iframe 
            sandbox="allow-scripts allow-same-origin"
            :srcdoc="addSquareStyles(offerModal.item.html_content)"
            class="cart-item-html-content"
            @load="forceSquareStyles"
          ></iframe>
        </div>
        <img v-else :src="getNftImage(offerModal.item?.nft_type)" :alt="offerModal.item?.nft_type" class="cart-item-image">
        
        <div class="cart-item-info">
          <div class="cart-item-name-container">
            <span class="cart-item-name">{{ extractNameFromNftObject(offerModal.item).name }}</span>
            <span v-if="extractNameFromNftObject(offerModal.item).number" class="cart-item-number">
              #{{ extractNameFromNftObject(offerModal.item).number }}
            </span>
          </div>
          <div class="cart-item-price-section">
            <span class="cart-item-price">Current: {{ offerModal.currentPrice }} TON</span>
            <img :src="tonlogoyellow" alt="TON" class="currency-icon-small">
          </div>
        </div>
      </div>

      <!-- Offer Input -->
      <div class="form-group-input">
        <label>Your Offer (TON):</label>
        <input 
          type="number" 
          v-model="offerModal.offerPrice" 
          min="0.1"
          step="0.1"
          placeholder="Enter your offer price"
          class="input"
          :class="{ 'error': offerModal.priceError }"
          @input="offerModal.priceError = ''"
        >
        <p v-if="offerModal.priceError" class="error-message">{{ offerModal.priceError }}</p>
      </div>

      <!-- Balance Info -->
      <div class="balance-info">
        <p>Your balance: {{ tonBalance }} TON</p>
        <p v-if="offerModal.offerPrice" class="remaining-balance">
          Remaining after offer: {{ (parseFloat(tonBalance) - parseFloat(offerModal.offerPrice || 0)).toFixed(2) }} TON
        </p>
      </div>
    </div>
    
    <div class="modal-dropdown-actions">
      <button @click="offerModal.show = false" class="cancel-button">Cancel</button>
      <button 
        @click="showOfferConfirmation" 
        class="confirm-button"
        :disabled="!offerModal.offerPrice || offerModal.offerPrice <= 0 || offerModal.loading"
      >
        <span v-if="offerModal.loading">Processing...</span>
        <span v-else>Send Offer</span>
      </button>
    </div>
  </div>
</div>


      <!-- Модальное окно покупки -->
      <!-- Модальное окно покупки -->
<div v-if="buyModal.show" class="modal-dropdown-overlay fullscreen-modal" @click="buyModal.show = false">
  <div class="modal-dropdown fullscreen-modal-dropdown" @click.stop>
    <div class="modal-drag-handle"></div>
    
    <div class="modal-dropdown-header">
      <h3 class="modal-dropdown-title">Покупка NFT</h3>
    </div>
    
    <div class="modal-dropdown-content">
      <!-- NFT Preview как в корзине -->
      <!-- В buyModal -->
<div class="cart-item-preview">
  <div v-if="buyModal.item?.html_content" class="cart-item-html-wrapper">
    <iframe 
      sandbox="allow-scripts allow-same-origin"
      :srcdoc="addSquareStyles(buyModal.item.html_content)"
      class="cart-item-html-content"
      @load="forceSquareStyles"
    ></iframe>
  </div>
  <img v-else :src="getNftImage(buyModal.nftType)" :alt="buyModal.nftType" class="cart-item-image">
  
  <div class="cart-item-info">
    <div class="cart-item-name-container">
      <span class="cart-item-name">{{ extractNameFromNftObject(buyModal.item).name }}</span>
      <span v-if="extractNameFromNftObject(buyModal.item).number" class="cart-item-number">
        #{{ extractNameFromNftObject(buyModal.item).number }}
      </span>
    </div>
    <div class="cart-item-price-section">
      <span class="cart-item-price">{{ buyModal.pricePerUnit }}</span>
      <img v-if="buyModal.currency === 'TON'" :src="tonlogoyellow" alt="TON" class="currency-icon-small">
    </div>
  </div>
</div>

      
      
    </div>
    
    <div class="modal-dropdown-actions">
      <button @click="buyModal.show = false" class="cancel-button">Отмена</button>
      <button 
  @click="executeBuy()" 
  class="confirm-button"
  :disabled="!buyModal.buyAmount || buyModal.buyAmount > buyModal.amount || buyModal.loading"
>
  <span v-if="buyModal.loading">Processing...</span>
  <span v-else>{{ buyModal.buyAmount * buyModal.pricePerUnit }} {{ buyModal.currency }}</span>
</button>
    </div>
  </div>
</div>

      <!-- Модальное окно снятия с продажи -->
      <div v-if="cancelSaleModal.show" class="modal-dropdown-overlay fullscreen-modal" @click="cancelSaleModal.show = false">
  <div class="modal-dropdown fullscreen-modal-dropdown" @click.stop>
    <div class="modal-drag-handle"></div>
    
    <div class="modal-dropdown-header">
      <h3 class="modal-dropdown-title">Confirm cancel sale</h3>
    </div>
    
    <div class="modal-dropdown-content">
      <!-- NFT Preview как в корзине -->

      <div class="cart-item-preview">
  <div v-if="cancelSaleModal.item?.html_content" class="cart-item-html-wrapper">
    <iframe 
      sandbox="allow-scripts allow-same-origin"
      :srcdoc="addSquareStyles(cancelSaleModal.item.html_content)"
      class="cart-item-html-content"
      @load="forceSquareStyles"
    ></iframe>
  </div>
  <img v-else :src="getNftImage(cancelSaleModal.nftType)" :alt="cancelSaleModal.nftType" class="cart-item-image">
  
  <div class="cart-item-info">
    <div class="cart-item-name-container">
      <span class="cart-item-name">{{ extractNameFromNftObject(cancelSaleModal.item).name }}</span>
      <span v-if="extractNameFromNftObject(cancelSaleModal.item).number" class="cart-item-number">
        #{{ extractNameFromNftObject(cancelSaleModal.item).number }}
      </span>
    </div>
    <div class="cart-item-price-section">
      <span class="cart-item-price">{{ cancelSaleModal.item?.price_per_unit }}</span>
      <img v-if="cancelSaleModal.item?.currency === 'TON'" :src="tonlogoyellow" alt="TON" class="currency-icon-small">
    </div>
  </div>
</div>
    </div>
    
    <div class="modal-dropdown-actions">
      <button @click="cancelSaleModal.show = false" class="cancel-button">Cancel</button>
<button 
  @click="executeCancelSale" 
  class="confirm-button"
  :disabled="cancelSaleModal.loading"
>
  <span v-if="cancelSaleModal.loading">Обработка...</span>
  <span v-else>Confirm</span>
</button>    </div>
  </div>
</div>

<!-- Gift Modal -->
<div v-if="giftModal.show" class="modal-dropdown-overlay fullscreen-modal" @click="giftModal.show = false">
  <div class="modal-dropdown fullscreen-modal-dropdown" @click.stop>
    <div class="modal-drag-handle"></div>
    
    <div class="modal-dropdown-header">
      <h3 class="modal-dropdown-title">Send as Gift</h3>
    </div>
    
    <div class="modal-dropdown-content">
      <!-- NFT Preview -->
      <div class="cart-item-preview">
        <div v-if="giftModal.item?.html_content" class="cart-item-html-wrapper">
          <iframe 
            sandbox="allow-scripts allow-same-origin"
            :srcdoc="addSquareStyles(giftModal.item.html_content)"
            class="cart-item-html-content"
            @load="forceSquareStyles"
          ></iframe>
        </div>
        <img v-else :src="getNftImage(giftModal.item?.nft_type)" :alt="giftModal.item?.nft_type" class="cart-item-image">
        
        <div class="cart-item-info">
          <div class="cart-item-name-container">
            <span class="cart-item-name">{{ extractNameFromNftObject(giftModal.item).name }}</span>
            <span v-if="extractNameFromNftObject(giftModal.item).number" class="cart-item-number">
              #{{ extractNameFromNftObject(giftModal.item).number }}
            </span>
          </div>
          <!-- Показываем цену только для чужих объявлений -->
          <div v-if="!giftModal.isOwnItem" class="cart-item-price-section">
            <span class="cart-item-price">{{ giftModal.item?.price_per_unit }}</span>
            <img v-if="giftModal.item?.currency === 'TON'" :src="tonlogoyellow" alt="TON" class="currency-icon-small">
          </div>
        </div>
      </div>

      <!-- Recipient Input -->
      <div class="form-group-input">
        <label>Recipient Username:</label>
        <input 
          type="text" 
          v-model="giftModal.recipientName" 
          placeholder="Enter username"
          class="input"
          :disabled="giftModal.loading"
        >
      </div>

      <!-- Price Info (только для чужих объявлений) -->
      <div v-if="!giftModal.isOwnItem" class="price-details">
        <div class="detail-row">
          <span>Gift Price:</span>
          <span>{{ giftModal.item?.price_per_unit }} TON</span>
        </div>
        <div class="detail-row total">
          <span>Your Balance:</span>
          <span>{{ tonBalance }} TON</span>
        </div>
      </div>
    </div>
    
    <div class="modal-dropdown-actions">
      <button 
        @click="giftModal.show = false" 
        class="cancel-button"
        :disabled="giftModal.loading"
      >
        Cancel
      </button>
      <button 
        @click="sendGift" 
        class="confirm-button"
        :class="{ 'free-button': giftModal.isOwnItem }"
        :disabled="!giftModal.recipientName || giftModal.loading"
      >
        <span v-if="giftModal.loading">Sending...</span>
        <span v-else-if="giftModal.isOwnItem">Send Gift (FREE)</span>
        <span v-else>Send Gift ({{ giftModal.item?.price_per_unit }} TON)</span>
      </button>
    </div>
  </div>
</div>
      <!-- Модальное окно редактирования цены -->
<div v-if="editPriceModal.show" class="modal-dropdown-overlay fullscreen-modal" @click="editPriceModal.show = false">
  <div class="modal-dropdown fullscreen-modal-dropdown" @click.stop>
    <div class="modal-drag-handle"></div>
    
    <div class="modal-dropdown-header">
      <h3 class="modal-dropdown-title">Edit price</h3>
    </div>
    
    <div class="modal-dropdown-content">
      <!-- NFT Preview как в корзине -->
      <div class="cart-item-preview">
        <div v-if="editPriceModal.item?.html_content" class="cart-item-html-wrapper">
          <iframe 
            sandbox="allow-scripts allow-same-origin"
            :srcdoc="addSquareStyles(editPriceModal.item.html_content)"
            class="cart-item-html-content"
            @load="forceSquareStyles"
          ></iframe>
        </div>
        <img v-else :src="getNftImage(editPriceModal.nftType)" :alt="editPriceModal.nftType" class="cart-item-image">
        
        <div class="cart-item-info">
          <div class="cart-item-name-container">
            <span class="cart-item-name">{{ extractNameFromNftObject(editPriceModal.item).name }}</span>
            <span v-if="extractNameFromNftObject(editPriceModal.item).number" class="cart-item-number">
              #{{ extractNameFromNftObject(editPriceModal.item).number }}
            </span>
          </div>
          <div class="cart-item-price-section">
            <span class="cart-item-price">{{ editPriceModal.currentPrice }}</span>
            <img :src="tonlogoyellow" alt="TON" class="currency-icon-small">
          </div>
        </div>
      </div>
      
      <div class="form-group-input">
        <input 
          type="number" 
          v-model="editPriceModal.newPrice" 
          min="0.1"
          step="0.1"
          placeholder="Input new price"
          class="input"
          @input="checkPriceChange"
        >
      </div>
      
      <div class="price-details">
        <div class="detail-row">
          <span>Текущая цена:</span>
          <span>{{ editPriceModal.currentPrice }} TON</span>
        </div>
        <div class="detail-row">
          <span>New price:</span>
          <span>{{ editPriceModal.newPrice || '0' }} TON</span>
        </div>
      </div>
    </div>
    
    <div class="modal-dropdown-actions">
      <button @click="editPriceModal.show = false" class="cancel-button">Отмена</button>
      <button 
        @click="executePriceEdit" 
        class="confirm-button"
        :class="{ 'disabled': !isPriceChanged }"
        :disabled="!editPriceModal.newPrice || editPriceModal.newPrice <= 0 || !isPriceChanged || editPriceModal.loading"
      >
        <span v-if="editPriceModal.loading">Обновление...</span>
        <span v-else>Обновить цену</span>
      </button>
    </div>
  </div>
</div>


      <!-- Модальное окно продажи -->
      <!-- Модальное окно продажи (замените существующее) -->
    </div>
</div>
            <div class="activity-container">
      <!-- Заголовок с переключателем My Activity -->


      <div class="activity-filters">
        <div class="filter-buttons">
          <button 
            v-for="type in offerTypes" 
            :key="type.value"
            class="filter-button"
            :class="{ active: selectedOfferType === type.value }"
            @click="setOfferType(type.value)"
          >
          <img 
              v-if="type.value === 'accepted'" 
              :src="galochka" 
              alt="Accepted" 
              class="filter-button-icon"
            >
            <!-- <img 
              v-else-if="type.value === 'rejected'" 
              :src="KPECTUK" 
              alt="Rejected" 
              class="filter-button-icon"
            > -->
            <img 
                v-else-if="type.value === 'pending'" 
                :src="selectedOfferType === 'pending' ? TIME_active : TIME" 
                alt="Pending" 
                class="filter-button-icon-pending"
            >
            
            
            <span v-else>{{ type.label }}</span>
          </button>
<div class="my-activity-toggle">
  <label class="toggle-label-activity">
    <input 
      type="checkbox" 
      class="toggle-input-activity" 
      v-model="showOnlyMyActivity"
      @change="toggleMyActivity"
    >
    <div class="toggle-switch-activity">
      <div class="toggle-slider-activity"></div>
    </div>
    <span class="toggle-text-activity">
      {{ showOnlyMyActivity ? 'Received Offers' : 'Sent Offers' }}
    </span>
  </label>
</div>
        </div>
      </div>

       <div class="activity-list" @scroll="handleScroll" ref="scrollContainer">
      <div v-if="displayedOffers.length === 0 && offersLoading" class="empty-activity">
        <div class="empty-activity-content">
          <div class="spinner"></div>
          <span>Loading offers...</span>
        </div>
      </div>

      <div v-else-if="displayedOffers.length === 0" class="empty-activity">
        <div class="empty-activity-content">
          <div class="empty-activity-icon">💸</div>
          <h3>No offers found</h3>
          <p>No offers match your current filters.</p>
        </div>
      </div>
    <div v-else class="activity-items">
      <div 
          v-for="offer in displayedOffers" 
          :key="offer.id"
          class="activity-item"
          :class="[offer.status, { 'my-offer': offer.buyer_name === currentAccountName }]"
        >
        <!-- NFT Preview -->
        <div class="activity-nft-preview" @click="openOfferFullscreen(offer)">
          <div class="cart-item-html-wrapper">
            <iframe 
              sandbox="allow-scripts allow-same-origin"
              :srcdoc="getOfferNftHtml(offer)"
              class="cart-item-html-content"
            ></iframe>
          </div>
        </div>
        <!-- Offer Details -->
        <div class="activity-details">
          <div class="activity-main-row">
            <div class="activity-info-left">
              <div class="activity-header-info">
                <div class="nft-title-container">
                  <h4 class="activity-nft-name">
                    {{ getOfferNftName(offer) }}
                  </h4>
                  <span class="nft-id-activity">
                    #{{ extractOfferNftId(offer) }}
                  </span>
                </div>

              </div>
              
              <div class="activity-meta">
                <div class="activity-type-container">
                  <span class="activity-type" :class="offer.status">
                    {{ getOfferStatusLabel(offer.status) }}
                  </span>
                  <span class="activity-date">{{ formatOfferDate(offer.created_at) }}</span>
                </div>


              </div>
            </div>
                <!-- Цена всегда справа -->
                <div class="activity-price-section" v-if="offer.offer_price">
                  <!-- Иконка типа оффера в правом верхнем углу -->
                  <div class="activity-type-icon" @click="setOfferType(offer.status)">
                    <img 
                      v-if="offer.status === 'pending'" 
                      :src="TIME_yellow" 
                      alt="Pending" 
                      class="activity-type-image-pending"
                      :class="{ active: selectedOfferType === 'pending' }"
                    >
                    <!-- <img 
                      v-else-if="offer.status === 'rejected'" 
                      :src="KPECTUK_red" 
                      alt="rejected" 
                      class="activity-type-image"
                      :class="{ active: selectedOfferType === 'accepted' }"
                    > -->
                    <img 
                      v-else-if="offer.status === 'accepted'" 
                      :src="galochka_green" 
                      alt="Accepted" 
                      class="activity-type-image"
                      :class="{ active: selectedOfferType === 'accepted' }"
                    >
                    
                  </div>

                  <div class="activity-price">
                    <span class="price-amount">{{ formatPrice(offer.offer_price) }}</span>
                    <img v-if="offer.currency === 'TON'" :src="tonlogoyellow" alt="TON" class="currency-icon-small">
                    <span v-else class="currency-text">{{ offer.currency || 'TON' }}</span>
                  </div>
                  
                  <div class="activity-total" v-if="offer.amount > 1">
                    For {{ offer.amount }} items
                  </div>
                  
                  <div class="original-price" v-if="offer.original_price">
                    Original: {{ formatPrice(offer.original_price) }} {{ offer.currency || 'TON' }}
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
import { ref, computed, onMounted, watch, nextTick, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import default_nft_image from '@/assets/invinsible.png';
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
import supabase from '../../services/supabase';
import telegramIcon from '@/assets/telegram_shop.png'; 
import vClickOutside from '@/directives/clickOutside.js';
import filter_img from '@/assets/filter.png';
import sell_img from '@/assets/sell.png';
import bucket_img from '@/assets/bucket.png';
import bucket_icon from '@/assets/bucket_icon.png';
import rubish_bucket_icon from '@/assets/rubish_bucket_icon.png';
import tonlogo from '@/assets/tonlogo.png';
import tonlogoblack from '@/assets/ton-logo-black.png';
import cennik from '@/assets/cennik.png';
import withdraw_icon from '@/assets/withdraw.png';
import tonlogogray from '@/assets/ton-logo-gray.png';
import tonlogoyellow  from '@/assets/ton-logo-yellow.png';
import tonlogofloor from '@/assets/ton-logo-floor.png'
import { useShopStore } from '@/stores/app'
import BANK from '@/assets/BANK.mp4'
import Giveaway from '@/assets/GiveAway.mp4'
import bucket_white_img from '@/assets/bucket_white.png';
import giftbox from '@/assets/giftbox_white.png';
import telega from '@/assets/telega.png';
import share from '@/assets/share.png';
import rubish_bucket from '@/assets/rubish_bucket.png';
import success from '@/assets/Success (1).gif';
import SuccessAnimation from '@/assets/Success.json';
import FailAnimation from '@/assets/BouncyFail.json';
import lottie from 'lottie-web';
import listIcon from '@/assets/to-do-list.png';
import editIcon from '@/assets/edit_price.png';
import purschaseIcon from '@/assets/business.png';
import listIcon_blue from '@/assets/to-do-list_blue.png';
import editIcon_blue from '@/assets/price_edit_blue.png';
import purschaseIcon_green from '@/assets/business_green.png';
import galochka from '@/assets/galochka.png';
import galochka_green from '@/assets/galochka_green.png';
import KPECTUK_red from '@/assets/KPECTUK_red.png';
import KPECTUK from '@/assets/KPECTUK.png';
import TIME from '@/assets/TIME.png';
import TIME_yellow from '@/assets/TIME_yellow.png';
import TIME_active from '@/assets/TIME_active.png';
import { onDeactivated } from 'vue';
import { subscribeToChannel, unsubscribeFromChannel } from '/subscriptions';



import { useRoute } from 'vue-router'


export default {
  directives: {
    clickOutside: vClickOutside
  },
  props: {
    tonConnectUI: Object
  },
  
  setup(props) {

    const gradients = {
  'Black': {
    stops: [
      { color: '#363738', offset: '0%' },
      { color: '#0e0f0f', offset: '100%' }
    ]
  },
  'Aquamarine': {
    stops: [
      { color: '#60b195', offset: '0%' },
      { color: '#46abb4', offset: '100%' }
    ]
  },
  'Azure_Blue': {
    stops: [
      { color: '#5db1cb', offset: '0%' },
      { color: '#448bab', offset: '100%' }
    ]
  },
  'Battleship_Grey': {
    stops: [
      { color: '#8c8c85', offset: '0%' },
      { color: '#6c6c66', offset: '100%' }
    ]
  },
  'Burgundy': {
    stops: [
      { color: '#a35e66', offset: '0%' },
      { color: '#6d414a', offset: '100%' }
    ]
  },
  'Burnt_Sienna': {
    stops: [
      { color: '#d66f3c', offset: '0%' },
      { color: '#b54b2d', offset: '100%' }
    ]
  },
  'Camo_Green': {
    stops: [
      { color: '#75944d', offset: '0%' },
      { color: '#547341', offset: '100%' }
    ]
  },
  'Cappuccino': {
    stops: [
      { color: '#b1907e', offset: '0%' },
      { color: '#7c6356', offset: '100%' }
    ]
  },
  'Caramel': {
    stops: [
      { color: '#d09932', offset: '0%' },
      { color: '#b77431', offset: '100%' }
    ]
  },
  'Carmine': {
    stops: [
      { color: '#e0574a', offset: '0%' },
      { color: '#a8383b', offset: '100%' }
    ]
  },
  'Carrot_Juice': {
    stops: [
      { color: '#db9867', offset: '0%' },
      { color: '#c76f4f', offset: '100%' }
    ]
  },
  'Celtic_Blue': {
    stops: [
      { color: '#45b8ed', offset: '0%' },
      { color: '#3886d9', offset: '100%' }
    ]
  },
  'Chestnut': {
    stops: [
      { color: '#be6f54', offset: '0%' },
      { color: '#994838', offset: '100%' }
    ]
  },
  'Chocolate': {
    stops: [
      { color: '#a46e58', offset: '0%' },
      { color: '#74443b', offset: '100%' }
    ]
  },
  'Cobalt_Blue': {
    stops: [
      { color: '#6088cf', offset: '0%' },
      { color: '#5162b8', offset: '100%' }
    ]
  },
  'Copper': {
    stops: [
      { color: '#d08656', offset: '0%' },
      { color: '#9d6531', offset: '100%' }
    ]
  },
  'Coral_Red': {
    stops: [
      { color: '#da896b', offset: '0%' },
      { color: '#c4654f', offset: '100%' }
    ]
  },
  'Cyberpunk': {
    stops: [
      { color: '#858ff3', offset: '0%' },
      { color: '#865fd3', offset: '100%' }
    ]
  },
  'Dark_Green': {
    stops: [
      { color: '#516341', offset: '0%' },
      { color: '#2b452f', offset: '100%' }
    ]
  },
  'Dark_Lilac': {
    stops: [
      { color: '#b17da5', offset: '0%' },
      { color: '#8c577a', offset: '100%' }
    ]
  },
  'Deep_Cyan': {
    stops: [
      { color: '#31b5aa', offset: '0%' },
      { color: '#189599', offset: '100%' }
    ]
  },
  'Desert_Sand': {
    stops: [
      { color: '#b39f82', offset: '0%' },
      { color: '#7e735b', offset: '100%' }
    ]
  },
  'Electric_Indigo': {
    stops: [
      { color: '#a980f3', offset: '0%' },
      { color: '#5b62d8', offset: '100%' }
    ]
  },
  'Electric_Purple': {
    stops: [
      { color: '#ca70c6', offset: '0%' },
      { color: '#9662d4', offset: '100%' }
    ]
  },
  'Emerald': {
    stops: [
      { color: '#78c585', offset: '0%' },
      { color: '#42a171', offset: '100%' }
    ]
  },
  'Fandango': {
    stops: [
      { color: '#e28ab6', offset: '0%' },
      { color: '#a4588b', offset: '100%' }
    ]
  },
  'Feldgrau': {
    stops: [
      { color: '#899288', offset: '0%' },
      { color: '#5e6b63', offset: '100%' }
    ]
  },
  'Fire_Engine': {
    stops: [
      { color: '#f05f4f', offset: '0%' },
      { color: '#c43949', offset: '100%' }
    ]
  },
  'French_Blue': {
    stops: [
      { color: '#5c9bc4', offset: '0%' },
      { color: '#37739a', offset: '100%' }
    ]
  },
  'French_Violet': {
    stops: [
      { color: '#c260e6', offset: '0%' },
      { color: '#914ed9', offset: '100%' }
    ]
  },
  'Grape': {
    stops: [
      { color: '#9d74c1', offset: '0%' },
      { color: '#794da0', offset: '100%' }
    ]
  },
  'Gunmetal': {
    stops: [
      { color: '#4c5d63', offset: '0%' },
      { color: '#2f3b42', offset: '100%' }
    ]
  },
  'Gunship_Green': {
    stops: [
      { color: '#558a65', offset: '0%' },
      { color: '#3d6657', offset: '100%' }
    ]
  },
  'Hunter_Green': {
    stops: [
      { color: '#8fae78', offset: '0%' },
      { color: '#4b825b', offset: '100%' }
    ]
  },
  'Indigo_Dye': {
    stops: [
      { color: '#537991', offset: '0%' },
      { color: '#416479', offset: '100%' }
    ]
  },
  'Ivory_White': {
    stops: [
      { color: '#bab6b1', offset: '0%' },
      { color: '#a19d97', offset: '100%' }
    ]
  },
  'Jade_Green': {
    stops: [
      { color: '#55c49c', offset: '0%' },
      { color: '#3b9977', offset: '100%' }
    ]
  },
  'Khaki_Green': {
    stops: [
      { color: '#adb070', offset: '0%' },
      { color: '#6b7d54', offset: '100%' }
    ]
  },
  'Lavender': {
    stops: [
      { color: '#b789e4', offset: '0%' },
      { color: '#8a5abc', offset: '100%' }
    ]
  },
  'Lemongrass': {
    stops: [
      { color: '#aeb85a', offset: '0%' },
      { color: '#559345', offset: '100%' }
    ]
  },
  'Light_Olive': {
    stops: [
      { color: '#c2af64', offset: '0%' },
      { color: '#887e45', offset: '100%' }
    ]
  },
  'Malachite': {
    stops: [
      { color: '#95b457', offset: '0%' },
      { color: '#3d9755', offset: '100%' }
    ]
  },
  'Marine_Blue': {
    stops: [
      { color: '#4e689c', offset: '0%' },
      { color: '#3b4b7a', offset: '100%' }
    ]
  },
  'Mexican_Pink': {
    stops: [
      { color: '#e36692', offset: '0%' },
      { color: '#c9497c', offset: '100%' }
    ]
  },
  'Midnight_Blue': {
    stops: [
      { color: '#5c6985', offset: '0%' },
      { color: '#354057', offset: '100%' }
    ]
  },
  'Mint_Green': {
    stops: [
      { color: '#7ecb82', offset: '0%' },
      { color: '#459e5a', offset: '100%' }
    ]
  },
  'Moonstone': {
    stops: [
      { color: '#7eb1b4', offset: '0%' },
      { color: '#588390', offset: '100%' }
    ]
  },
  'Mustard': {
    stops: [
      { color: '#d4980d', offset: '0%' },
      { color: '#c47712', offset: '100%' }
    ]
  },
  'Mystic_Pearl': {
    stops: [
      { color: '#d08b6d', offset: '0%' },
      { color: '#b05770', offset: '100%' }
    ]
  },
  'Navy_Blue': {
    stops: [
      { color: '#6c9edd', offset: '0%' },
      { color: '#5c6ec9', offset: '100%' }
    ]
  },
  'Neon_Blue': {
    stops: [
      { color: '#7596f9', offset: '0%' },
      { color: '#6862e4', offset: '100%' }
    ]
  },
  'Old_Gold': {
    stops: [
      { color: '#b58d38', offset: '0%' },
      { color: '#946925', offset: '100%' }
    ]
  },
  'Onyx_Black': {
    stops: [
      { color: '#4d5254', offset: '0%' },
      { color: '#313638', offset: '100%' }
    ]
  },
  'Orange': {
    stops: [
      { color: '#d19a3a', offset: '0%' },
      { color: '#c06f47', offset: '100%' }
    ]
  },
  'Pacific_Cyan': {
    stops: [
      { color: '#5abea6', offset: '0%' },
      { color: '#3d95ba', offset: '100%' }
    ]
  },
  'Pacific_Green': {
    stops: [
      { color: '#6fc793', offset: '0%' },
      { color: '#3b9c84', offset: '极速赛车开奖结果记录' }
    ]
  },
  'Persimmon': {
    stops: [
      { color: '#e7a75a', offset: '0%' },
      { color: '#c5675f', offset: '100%' }
    ]
  },
  'Pine_Green': {
    stops: [
      { color: '#6ba97c', offset: '0%' },
      { color: '#3e7970', offset: '100%' }
    ]
  },
  'Pistachio': {
    stops: [
      { color: '#97b07c', offset: '0%' },
      { color: '#5c814c', offset: '100%' }
    ]
  },
  'Platinum': {
    stops: [
      { color: '#b2aea7', offset: '0%' },
      { color: '#88847e', offset: '100%' }
    ]
  },
  'Pure_Gold': {
    stops: [
      { color: '#ccab41', offset: '0%' },
      { color: '#987b32', offset: '100%' }
    ]
  },
  'Purple': {
    stops: [
      { color: '#ae6cae', offset: '0%' },
      { color: '#844784', offset: '100%' }
    ]
  },
  'Ranger_Green': {
    stops: [
      { color: '#5f7849', offset: '0%' },
      { color: '#3c4f3b', offset: '100%' }
    ]
  },
  'Raspberry': {
    stops: [
      { color: '#e07b85', offset: '0%' },
      { color: '#b65980', offset: '100%' }
    ]
  },
  'Rifle_Green': {
    stops: [
      { color: '#64695c', offset: '0%' },
      { color: '#4b5241', offset: '100%' }
    ]
  },
  'Roman_Silver': {
    stops: [
      { color: '#a3a8b5', offset: '0%' },
      { color: '#7c808a', offset: '100%' }
    ]
  },
  'Rosewood': {
    stops: [
      { color: '#b77a77', offset: '0%' },
      { color: '#814c52', offset: '100%' }
    ]
  },
  'Sapphire': {
    stops: [
      { color: '#58a3c8', offset: '0%' },
      { color: '#5379c2', offset: '100%' }
    ]
  },
  'Satin_Gold': {
    stops: [
      { color: '#bf9b47', offset: '0%' },
      { color: '#8d7739', offset: '100%' }
    ]
  },
  'Seal_Brown': {
    stops: [
      { color: '#664d45', offset: '0%' },
      { color: '#47362e', offset: '100%' }
    ]
  },
  'Shamrock_Green': {
    stops: [
      { color: '#8ab163', offset: '0%' },
      { color: '#559345', offset: '100%' }
    ]
  },
  'Silver_Blue': {
    stops: [
      { color: '#80a4b8', offset: '0%' },
      { color: '#607c91', offset: '100%' }
    ]
  },
  'Sky_Blue': {
    stops: [
      { color: '#58b4c8', offset: '0%' },
      { color: '#538bc2', offset: '100%' }
    ]
  },
  'Steel_Grey': {
    stops: [
      { color: '#97a2ac', offset: '0%' },
      { color: '#63727c', offset: '100%' }
    ]
  },
  'Strawberry': {
    stops: [
      { color: '#dd8e6f', offset: '0%' },
      { color: '#b75a60', offset: '100%' }
    ]
  },
  'Tactical_Pine': {
    stops: [
      { color: '#44826b', offset: '0%' },
      { color: '#2f6369', offset: '100%' }
    ]
  },
  'Tomato': {
    stops: [
      { color: '#e6793e', offset: '0%' },
      { color: '#d44e3f', offset: '100%' }
    ]
  },
  'Turquoise': {
    stops: [
      { color: '#5ec0b8', offset: '0%' },
      { color: '#3d928e', offset: '100%' }
    ]
  }
};
const myMarketItems = computed(() => {
  return marketItems.value.filter(item => {
    // Дополнительная проверка владения
    const isOwner = item.seller === currentAccountName.value;
    
    // Для надежности можно добавить проверку в реальном времени
    if (isOwner) {
      // Проверяем, что товар действительно существует в базе
      // Это можно сделать асинхронно, но для computed property используем кэш
      return true;
    }
    
    return false;
  });
});
    const backdropColors = ref([
  { id: 'Black', name: 'Black' },
  { id: 'Aquamarine', name: 'Aquamarine' },
  { id: 'Azure Blue', name: 'Azure Blue' },
  { id: 'Battleship Grey', name: 'Battleship Grey' },
  { id: 'Burgundy', name: 'Burgundy' },
  { id: 'Burnt Sienna', name: 'Burnt Sienna' },
  { id: 'Camo Green', name: 'Camo Green' },
  { id: 'Cappuccino', name: 'Cappuccino' },
  { id: 'Caramel', name: 'Caramel' },
  { id: 'Carmine', name: 'Carmine' },
  { id: 'Carrot Juice', name: 'Carrot Juice' },
  { id: 'Celtic Blue', name: 'Celtic Blue' },
  { id: 'Chestnut', name: 'Chestnut' },
  { id: 'Chocolate', name: 'Chocolate' },
  { id: 'Cobalt Blue', name: 'Cobalt Blue' },
  { id: 'Copper', name: 'Copper' },
  { id: 'Coral Red', name: 'Coral Red' },
  { id: 'Cyberpunk', name: 'Cyberpunk' },
  { id: 'Dark Green', name: 'Dark Green' },
  { id: 'Dark Lilac', name: 'Dark Lilac' },
  { id: 'Deep Cyan', name: 'Deep Cyan' },
  { id: 'Desert Sand', name: 'Desert Sand' },
  { id: 'Electric Indigo', name: 'Electric Indigo' },
  { id: 'Electric Purple', name: 'Electric Purple' },
  { id: 'Emerald', name: 'Emerald' },
  { id: 'Fandango', name: 'Fandango' },
  { id: 'Feldgrau', name: 'Feldgrau' },
  { id: 'Fire Engine', name: 'Fire Engine' },
  { id: 'French Blue', name: 'French Blue' },
  { id: 'French Violet', name: 'French Violet' },
  { id: 'Grape', name: 'Grape' },
  { id: 'Gunmetal', name: 'Gunmetal' },
  { id: 'Gunship Green', name: 'Gunship Green' },
  { id: 'Hunter Green', name: 'Hunter Green' },
  { id: 'Indigo Dye', name: 'Indigo Dye' },
  { id: 'Ivory White', name: 'Ivory White' },
  { id: 'Jade Green', name: 'Jade Green' },
  { id: 'Khaki Green', name: 'Khaki Green' },
  { id: 'Lavender', name: 'Lavender' },
  { id: 'Lemongrass', name: 'Lemongrass' },
  { id: 'Light Olive', name: 'Light Olive' },
  { id: 'Malachite', name: 'Malachite' },
  { id: 'Marine Blue', name: 'Marine Blue' },
  { id: 'Mexican Pink', name: 'Mexican Pink' },
  { id: 'Midnight Blue', name: 'Midnight Blue' },
  { id: 'Mint Green', name: 'Mint Green' },
  { id: 'Moonstone', name: 'Moonstone' },
  { id: 'Mustard', name: 'Mustard' },
  { id: 'Mystic Pearl', name: 'Mystic Pearl' },
  { id: 'Navy Blue', name: 'Navy Blue' },
  { id: 'Neon Blue', name: 'Neon Blue' },
  { id: 'Old Gold', name: 'Old Gold' },
  { id: 'Onyx Black', name: 'Onyx Black' },
  { id: 'Orange', name: 'Orange' },
  { id: 'Pacific Cyan', name: 'Pacific Cyan' },
  { id: 'Pacific Green', name: 'Pacific Green' },
  { id: 'Persimmon', name: 'Persimmon' },
  { id: 'Pine Green', name: 'Pine Green' },
  { id: 'Pistachio', name: 'Pistachio' },
  { id: 'Platinum', name: 'Platinum' },
  { id: 'Pure Gold', name: 'Pure Gold' },
  { id: 'Purple', name: 'Purple' },
  { id: 'Ranger Green', name: 'Ranger Green' },
  { id: 'Raspberry', name: 'Raspberry' },
  { id: 'Rifle Green', name: 'Rifle Green' },
  { id: 'Roman Silver', name: 'Roman Silver' },
  { id: 'Rosewood', name: 'Rosewood' },
  { id: 'Sapphire', name: 'Sapphire' },
  { id: 'Satin Gold', name: 'Satin Gold' },
  { id: 'Seal Brown', name: 'Seal Brown' },
  { id: 'Shamrock Green', name: 'Shamrock Green' },
  { id: 'Silver Blue', name: 'Silver Blue' },
  { id: 'Sky Blue', name: 'Sky Blue' },
  { id: 'Steel Grey', name: 'Steel Grey' },
  { id: 'Strawberry', name: 'Strawberry' },
  { id: 'Tactical Pine', name: 'Tactical Pine' },
  { id: 'Tomato', name: 'Tomato' },
  { id: 'Turquoise', name: 'Turquoise' }
]);
// В секции setup() добавьте эти функции:
const getOptionImageUrl = (nftType, modelName, useLegacy = false) => {
  if (useLegacy) {
    return getLegacyModelImageUrl(nftType, modelName);
  }
  return getModelImageUrl(nftType, modelName);
};

const getLegacyModelImageUrl = (nftType, modelName) => {
  let cleanNftType = nftType.toLowerCase();
  if (cleanNftType.startsWith('html_nft_')) {
    cleanNftType = cleanNftType.replace('html_nft_', '');
  }
  if (cleanNftType.startsWith('htmlnft')) {
    cleanNftType = cleanNftType.replace('htmlnft', '');
  }
  
  const folderName = groupDisplayNames[cleanNftType] || cleanNftType;
  const nftPath = folderName.toLowerCase().replace(/\s+/g, '%20');
  
  const modelPath = modelName.replace(/\s+/g, '%20').replace(/\?/g, '%3F');
  
  return `https://gifts.coffin.meme/${nftPath}/${modelPath}.png`;
};
const playLottieFailAnimation = () => {
  console.log('🎨 playLottieFailAnimation вызвана, show:', operationFail.value.show);
  
  if (operationFail.value.show && operationFail.value.animationData) {
    console.log('✅ Условия для fail анимации выполнены');
    
    nextTick(() => {
      if (lottieFailAnimation) {
        lottieFailAnimation.destroy();
      }
      
      const container = document.querySelector('.lottie-fail-container');
      if (container) {
        try {
          lottieFailAnimation = lottie.loadAnimation({
            container: container,
            renderer: 'svg',
            loop: false,
            autoplay: true,
            animationData: operationFail.value.animationData,
            rendererSettings: {
              preserveAspectRatio: 'xMidYMid meet'
            }
          });
          
          // Обработчик завершения fail анимации
          lottieFailAnimation.addEventListener('complete', () => {
            console.log('🏁 Fail анимация завершена');
            // Анимация завершилась - ждем 1 секунду на последнем кадре
            setTimeout(() => {
              operationFail.value.show = false;
            }, 1000);
          });
        } catch (error) {
          console.error('Error loading Lottie fail animation:', error);
          // Fallback: закрываем через 2 секунды даже если анимация не загрузилась
          setTimeout(() => {
            operationFail.value.show = false;
          }, 2000);
        }
      }
    });
  } else {
    console.log('❌ Условия для fail анимации не выполнены:', {
      show: operationFail.value.show,
      hasAnimationData: !!operationFail.value.animationData
    });
  }
};

const showFailAnimation = (title = 'Operation Failed', type = 'purchase_failed') => {
  operationFail.value = {
    show: true,
    animationData: FailAnimation,
    type: type,
    title: title
  };
  
  // Запускаем анимацию
  playLottieFailAnimation();
};
const lottieFailContainer = ref(null);




// Обновленная функция для fullscreen-view
const generateNftHtmlForFullscreen = (nftData) => {
  try {
    const nftId = extractNftIdFromData(nftData);
    const nftNameMatch = nftData.url?.match(/\/nft\/([^-]+)/);
    const nftName = nftNameMatch ? nftNameMatch[1] : 'unknown';
    
    return `
<!DOCTYPE html>
<html>
<head>
  <title>NFT Display - ${nftName}-${nftId}</title>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/bodymovin/5.12.2/lottie.min.js"><\/script>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
      border-radius:30px;

    }
    
    body, html {
      margin: 0;
      padding: 0;
      width: 100%;
      height: 100%;
      background: transparent;
      overflow: hidden;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      
    }
    
    #main-container {
      display: inline-block;
      position: relative;
      background: transparent;
      /* Размер будет определяться содержимым */
    }
    
    #animation-container {
      display: inline-block;
      position: relative;
      line-height: 0; /* Убирает лишние отступы */
    }
    
    #image-container {
      display: none;
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
    }
    
    .nft-image {
      width: 100%;
      height: 100%;
      object-fit: contain;
      display: block;
    }
    
    .lottie-animation {
      display: block;
      width: 100%;
      height: 100%;
    }
  </style>
</head>
<body>
  <div id="main-container">
    <div id="animation-container">
      <div class="lottie-animation"></div>
    </div>
    <div id="image-container">
      <img class="nft-image" alt="${nftName}">
    </div>
  </div>
  <script>
    let currentAnimation = null;
    let currentImage = null;
    let animationLoaded = false;
    let containerSize = { width: 0, height: 0 };

    function updateContainerSize() {
      const mainContainer = document.getElementById('main-container');
      const animationContainer = document.getElementById('animation-container');
      
      if (animationContainer.offsetWidth > 0 && animationContainer.offsetHeight > 0) {
        containerSize.width = animationContainer.offsetWidth;
        containerSize.height = animationContainer.offsetHeight;
        
        mainContainer.style.width = containerSize.width + 'px';
        mainContainer.style.height = containerSize.height + 'px';
        
        console.log('Container size updated:', containerSize);
      }
    }

    function loadAnimationWhenVisible() {
      if (currentAnimation) {
        currentAnimation.destroy();
        currentAnimation = null;
      }
      
      if (currentImage && currentImage.parentNode) {
        currentImage.parentNode.removeChild(currentImage);
        currentImage = null;
      }
      
      document.getElementById('animation-container').style.display = 'block';
      document.getElementById('image-container').style.display = 'none';
      
      const animationContainer = document.querySelector('.lottie-animation');
      animationContainer.innerHTML = '';

      currentAnimation = lottie.loadAnimation({
        container: animationContainer,
        renderer: "svg",
        loop: false,
        autoplay: true,
        path: "https://nft.fragment.com/gift/${nftName}-${nftId}.lottie.json"
      });

      // Обновляем размер контейнера когда анимация загружена
      currentAnimation.addEventListener('DOMLoaded', function() {
        setTimeout(updateContainerSize, 100);
      });

      currentAnimation.addEventListener('config_ready', function() {
        setTimeout(updateContainerSize, 100);
      });

      currentImage = new Image();
      currentImage.src = "https://nft.fragment.com/gift/${nftName}-${nftId}.webp";
      currentImage.className = 'nft-image';
      currentImage.alt = '${nftName}';
      
      currentImage.onload = function() {
        // Обновляем размер когда изображение загружено
        updateContainerSize();
      };
      
      document.getElementById('image-container').innerHTML = '';
      document.getElementById('image-container').appendChild(currentImage);

      currentAnimation.addEventListener('complete', function() {
        if (currentImage.complete && currentImage.naturalWidth !== 0) {
          document.getElementById('animation-container').style.display = 'none';
          document.getElementById('image-container').style.display = 'block';
          updateContainerSize();
        } else {
          currentImage.onload = function() {
            document.getElementById('animation-container').style.display = 'none';
            document.getElementById('image-container').style.display = 'block';
            updateContainerSize();
          };
          currentImage.onerror = function() {
            console.error('Failed to load image, keeping animation');
            document.getElementById('animation-container').style.display = 'block';
            document.getElementById('image-container').style.display = 'none';
          };
        }
      });

      currentAnimation.addEventListener('error', function() {
        console.error('Failed to load animation, trying image');
        document.getElementById('animation-container').style.display = 'none';
        document.getElementById('image-container').style.display = 'block';
        updateContainerSize();
      });

      animationLoaded = true;
      
      if (window.parent) {
        window.parent.postMessage({
          type: 'animationRestarted',
          nftId: '${nftName}-${nftId}'
        }, '*');
      }
    }

    function replayAnimation() {
      console.log('Replaying animation...');
      loadAnimationWhenVisible();
    }

    // Обработчик клика - перезапускаем анимацию
    document.addEventListener('click', function() {
      replayAnimation();
    });

    window.addEventListener('message', function(event) {
      if (event.data.type === 'replayAnimation') {
        replayAnimation();
      }
    });

    // Периодически обновляем размер (на случай если анимация меняет размер)
    const resizeInterval = setInterval(updateContainerSize, 500);

    // Загружаем анимацию сразу для полноэкранного режима
    loadAnimationWhenVisible();

    // Очистка интервала при размонтировании
    window.addEventListener('beforeunload', function() {
      clearInterval(resizeInterval);
    });

    window.replayAnimation = replayAnimation;
  <\/script>
</body>
</html>
    `;
  } catch (error) {
    console.error('Error generating NFT HTML for fullscreen:', error);
    return `
      <div style="width: 100%; height: 100%; background: #f0f0f0; display: flex; align-items: center; justify-content: center; cursor: pointer;">
        <div style="text-align: center;">
          <h3>Error loading NFT</h3>
          <p>Click to retry</p>
        </div>
      </div>
    `;
  }
};

// Обновленная функция для market-item - только изображение
const generateNftHtmlForListActivity = (nftData) => {
  try {
    const nftId = extractNftIdFromData(nftData);
    
    const nftNameMatch = nftData.url?.match(/\/nft\/([^-]+)/);
    const nftName = nftNameMatch ? nftNameMatch[1] : 'unknown';
    
    const imageUrl = `https://nft.fragment.com/gift/${nftName}-${nftId}.webp`;
    
    return `
<!DOCTYPE html>
<html>
<head>
  <title>NFT Display - ${nftName}-${nftId}</title>
  <style>
    body, html {
      margin: 0;
      padding: 0;
      width: 100%;
      height: 100%;
      background: transparent;
      overflow: hidden;
      cursor: pointer;
    }
    #image-container {
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      background: transparent;
    }
    .nft-image {
      max-width: 100%;
      max-height: 100%;
      object-fit: contain;
    }
  </style>
</head>
<body>
  <div id="image-container">
    <img src="${imageUrl}" alt="${nftName}" class="nft-image" 
         onerror="this.onerror=null; this.src='${default_nft_image}';">
  </div>
  <script>
    // Обработчик клика - открываем полноэкранный просмотр
    document.addEventListener('click', function() {
      if (window.parent) {
        window.parent.postMessage({
          type: 'openFullscreenView',
          nftId: '${nftId}',
          nftName: '${nftName}'
        }, '*');
      }
    });

    // Загрузка изображения при появлении в viewport
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = document.querySelector('.nft-image');
          if (img && !img.loaded) {
            img.loaded = true;
          }
          observer.disconnect();
        }
      });
    }, { threshold: 0.1 });

    observer.observe(document.getElementById('image-container'));
  <\/script>
</body>
</html>
    `;
  } catch (error) {
    console.error('Error generating NFT HTML for list:', error);
    return `
      <div style="width: 100%; height: 100%; background: #f0f0f0; display: flex; align-items: center; justify-content: center; cursor: pointer;">
        <img src="${default_nft_image}" alt="Default NFT" style="max-width: 80%; max-height: 80%;">
      </div>
    `;
  }
};

// Обновленная функция для fullscreen-view - только изображение
const generateNftHtmlForFullscreenActivity = (nftData) => {
  try {
    const nftId = extractNftIdFromData(nftData);
    const nftNameMatch = nftData.url?.match(/\/nft\/([^-]+)/);
    const nftName = nftNameMatch ? nftNameMatch[1] : 'unknown';
    
    const imageUrl = `https://nft.fragment.com/gift/${nftName}-${nftId}.webp`;
    
    return `
<!DOCTYPE html>
<html>
<head>
  <title>NFT Display - ${nftName}-${nftId}</title>
  <style>
    body, html {
      margin: 0;
      padding: 0;
      width: 100%;
      height: 100%;
      background: transparent;
      overflow: hidden;
      cursor: pointer;
    }
    #image-container {
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      background: transparent;
    }
    .nft-image {
      max-width: 100%;
      max-height: 100%;
      object-fit: contain;
    }
  </style>
</head>
<body>
  <div id="image-container">
    <img src="${imageUrl}" alt="${nftName}" class="nft-image" 
         onerror="this.onerror=null; this.src='${default_nft_image}';">
  </div>
  <script>
    function reloadImage() {
      const img = document.querySelector('.nft-image');
      if (img) {
        // Добавляем timestamp для принудительной перезагрузки
        const newSrc = img.src.split('?')[0] + '?t=' + Date.now();
        img.src = newSrc;
      }
    }

    // Обработчик клика - перезагружаем изображение
    document.addEventListener('click', function() {
      reloadImage();
    });

    window.addEventListener('message', function(event) {
      if (event.data.type === 'replayAnimation') {
        reloadImage();
      }
    });

    // Уведомляем родителя о загрузке
    if (window.parent) {
      window.parent.postMessage({
        type: 'animationRestarted',
        nftId: '${nftName}-${nftId}'
      }, '*');
    }

    window.reloadImage = reloadImage;
  <\/script>
</body>
</html>
    `;
  } catch (error) {
    console.error('Error generating NFT HTML for fullscreen:', error);
    return `
      <div style="width: 100%; height: 100%; background: #f0f0f0; display: flex; align-items: center; justify-content: center; cursor: pointer;">
        <img src="${default_nft_image}" alt="Default NFT" style="max-width: 80%; max-height: 80%;">
      </div>
    `;
  }
};


// В mounted
onMounted(() => {
  window.addEventListener('message', (event) => {
    if (event.data.type === 'openFullscreenView') {
      // Находим соответствующий item по ID или другим данным
      const item = findItemById(event.data.nftId, event.data.nftName);
      if (item) {
        openFullscreenView(item);
      }
    }
  });
});


// Функция для поиска item по данным
// Улучшенная функция для поиска item
const findItemById = (nftId, nftName) => {
  console.log('Searching for item with ID:', nftId, 'and name:', nftName);
  
  // Сначала ищем по полному имени (nftName-id)
  if (nftName && nftId) {
    const fullName = `${nftName}-${nftId}`;
    
    // Ищем в marketItems
    let item = marketItems.value.find(item => {
      const itemUrl = item.url || (item.nft_object && item.nft_object.url);
      return itemUrl && itemUrl.includes(fullName);
    });
    
    if (item) return item;
    
    // Ищем в unlisted NFT
    item = myUnlistedNfts.value.find(nft => {
      const nftUrl = nft.url;
      return nftUrl && nftUrl.includes(fullName);
    });
    
    if (item) return item;
  }
  
  // Fallback: ищем только по ID
  let item = marketItems.value.find(item => {
    const itemId = extractNftIdFromData(item.nft_object || item);
    return itemId === nftId;
  });
  
  if (!item) {
    item = myUnlistedNfts.value.find(nft => {
      const itemId = extractNftIdFromData(nft);
      return itemId === nftId;
    });
  }
  
  return item;
};
onMounted(async () => {
  const route = useRoute(); // ← ПЕРЕМЕСТИТЬ сюда
  
  if (route.params.itemId) {
    const item = findItemByItemId(route.params.itemId);
    if (item) {
      openFullscreenView(item);
    }
  }
});
// Добавьте эту функцию для поиска по item_id
const findItemByItemId = (itemId) => {
  console.log('🔍 Поиск item по item_id:', itemId);
  console.log('📊 Всего marketItems:', marketItems.value.length);
  
  // Поиск в marketItems
  let item = marketItems.value.find(item => {
    const found = item.item_id === itemId;
    if (found) {
      console.log('✅ Найден в marketItems:', item);
    }
    return found;
  });
  
  // Поиск в myMarketItems (listed NFT)
  if (!item) {
    item = myMarketItems.value.find(item => item.item_id === itemId);
    if (item) {
      console.log('✅ Найден в myMarketItems:', item);
    }
  }
  
  // Поиск в unlisted NFT (преобразованных в market формат)
  if (!item && myUnlistedNfts.value.length > 0) {
    const unlistedItem = myUnlistedNfts.value.find(nft => {
      // Генерируем временный item_id для unlisted NFT
      const tempItemId = `unlisted-${extractNftIdFromUnlisted(nft)}`;
      return tempItemId === itemId;
    });
    
    if (unlistedItem) {
      console.log('✅ Найден в unlisted NFT:', unlistedItem);
      // Создаем временный item в формате market
      item = {
        id: `unlisted-${extractNftIdFromUnlisted(unlistedItem)}`,
        item_id: itemId,
        nft_type: `html_nft_${extractNftNameFromUrl(unlistedItem.url)}`,
        nft_object: unlistedItem,
        seller: currentAccountName.value,
        is_unlisted: true
      };
    }
  }
  
  if (!item) {
    console.log('❌ Item не найден ни в одном источнике');
    // Логируем первые несколько items для отладки
    if (marketItems.value.length > 0) {
      console.log('📝 Первые 5 marketItems:', marketItems.value.slice(0, 5).map(i => ({ 
        id: i.id, 
        item_id: i.item_id,
        nft_type: i.nft_type 
      })));
    }
  }
  
  return item;
};

const handleBackButton = () => {
  // Закрываем полноэкранный просмотр
  htmlModal.value.show = false;
  
  // Сбрасываем все модальные окна
  resetAllModals();

};
const handleRouteItemId = async (itemId) => {
  console.log('🔄 handleRouteItemId вызван с:', itemId);
  
  // Проверяем, не обрабатываем ли мы уже этот itemId
  if (window.currentlyProcessingItemId === itemId) {
    console.log('⏳ Этот itemId уже обрабатывается, пропускаем');
    return;
  }
  
  window.currentlyProcessingItemId = itemId;
  
  try {
    // Ждем загрузки данных если нужно
    if (marketItems.value.length === 0) {
      console.log('📥 Ожидаем загрузки marketItems...');
      await new Promise((resolve) => {
        const checkData = () => {
          if (marketItems.value.length > 0) {
            resolve();
          } else {
            setTimeout(checkData, 100);
          }
        };
        checkData();
      });
    }
    
    await nextTick(); // Ждем обновления Vue
    
    const item = findItemByItemId(itemId);
    if (item) {
      console.log('✅ Item найден, открываем fullscreen:', item.item_id);
      
      // Дополнительная задержка для гарантии
      await nextTick();
      
      openFullscreenView(item);
    } else {
      console.error('❌ Item не найден после ожидания:', itemId);
      
      // Пробуем еще раз через короткое время
      setTimeout(() => {
        const retryItem = findItemByItemId(itemId);
        if (retryItem) {
          console.log('✅ Item найден при повторной попытке');
          openFullscreenView(retryItem);
        }
      }, 300);
    }
  } catch (error) {
    console.error('❌ Ошибка в handleRouteItemId:', error);
  } finally {
    // Сбрасываем флаг обработки
    setTimeout(() => {
      window.currentlyProcessingItemId = null;
    }, 100);
  }
};
// Обновите mounted для обработки маршрутов:
onMounted(() => {
  // Обработка открытия по item_id из URL
  const route = useRoute();
  if (route.params.itemId) {
    const item = findItemByItemId(route.params.itemId);
    if (item) {
      openFullscreenView(item);
    }
  }
});

// Исправленная функция openFullscreenView - добавьте async
const openFullscreenView = async (item) => {
  try {
    if (!item) {
      console.error('Item is undefined');
      return;
    }
    
    console.log('🎯 Открываем fullscreen view для:', item.item_id);
    console.log('📋 Данные item:', {
      id: item.id,
      item_id: item.item_id,
      nft_type: item.nft_type,
      url: item.url,
      nft_object: item.nft_object
    });
    
    // Если у item есть item_id, обновляем URL (с обработкой ошибок)
    if (item.item_id) {
      try {
        // Проверяем, не находимся ли мы уже на этом маршруте
        const currentRoute = router.currentRoute.value;
        if (currentRoute.params.itemId !== item.item_id) {
          router.push(`/shop/${item.item_id}`);
        }
      } catch (routerError) {
        console.warn('Ошибка маршрутизатора, продолжаем без изменения URL:', routerError);
      }
    }

    // Используем безопасный вызов extractFullNftName
    let fullNftName = null;
    let telegramLink = null;
    
    try {
      const url = item.url || (item.nft_object && item.nft_object.url);
      fullNftName = extractFullNftName(url);
      telegramLink = fullNftName ? `https://t.me/nft/${fullNftName}` : null;
    } catch (urlError) {
      console.warn('Ошибка извлечения URL:', urlError);
    }
    
    console.log('📊 Telegram link:', telegramLink);

    // Функция для извлечения значения и процента
    const extractValueAndPercentage = (value) => {
      if (!value) return { name: 'Не указано', percentage: '' };
      
      try {
        const parts = value.split(' ');
        if (parts.length > 1 && parts[parts.length - 1].includes('%')) {
          const percentage = parts.pop();
          return { name: parts.join(' '), percentage };
        }
        return { name: value, percentage: '' };
      } catch (e) {
        return { name: value, percentage: '' };
      }
    };

    let modelData = { name: 'Не указано', percentage: '' };
    let symbolData = { name: 'Не указано', percentage: '' };
    let backdropData = { name: 'Не указано', percentage: '' };
    
    try {
      if (item.nft_object) {
        const nftObj = typeof item.nft_object === 'string' 
          ? JSON.parse(item.nft_object) 
          : item.nft_object;
        
        modelData = extractValueAndPercentage(nftObj.model);
        symbolData = extractValueAndPercentage(nftObj.symbol);
        backdropData = extractValueAndPercentage(nftObj.backdrop);
      }
    } catch (parseError) {
      console.error('Ошибка парсинга nft_object:', parseError);
    }

    console.log('📋 Extracted data:', { modelData, symbolData, backdropData });

    // Генерируем HTML контент с обработкой ошибок
    let htmlContent = '';
    try {
      htmlContent = generateNftHtmlForFullscreen(item.nft_object || item);
    } catch (htmlError) {
      console.error('Ошибка генерации HTML:', htmlError);
      htmlContent = `
        <div style="width: 100%; height: 100%; background: #f0f0f0; display: flex; align-items: center; justify-content: center;">
          <div style="text-align: center;">
            <h3>Error loading NFT</h3>
            <p>Unable to display content</p>
          </div>
        </div>
      `;
    }

    // Определяем тип действия для unlisted NFT
    let actionType = 'sell'; // по умолчанию
    if (item.is_unlisted) {
      // Для unlisted NFT определяем доступные действия
      if (item.nft_object && item.nft_object.url) {
        actionType = 'send'; // или 'withdraw' в зависимости от логики
      }
    }
    
// На эту простую проверку:
const isOnMarket = true; // ВРЕМЕННО ВСЕГДА TRUE
console.log('🏪 Item on market: TRUE (forced)');

    htmlModal.value = {
      show: true,
      htmlContent: htmlContent,
      title: getNftDisplayName(item.nft_type, item.nft_object) || 'NFT',
      model: modelData.name,
      modelPercentage: modelData.percentage,
      symbol: symbolData.name,
      symbolPercentage: symbolData.percentage,
      backdrop: backdropData.name,
      backdropPercentage: backdropData.percentage,
      telegramLink,
      item: item,
      isUnlisted: item.is_unlisted || false,
      actionType: actionType,
      isOnMarket: isOnMarket // ← ДОБАВЛЕНО: флаг наличия на маркете
    };

    console.log('✅ Fullscreen view успешно открыт');

  } catch (err) {
    console.error('❌ Критическая ошибка при открытии полноэкранного просмотра:', err);
    
    // Fallback с минимальными данными
    htmlModal.value = {
      show: true,
      htmlContent: `
        <div style="width: 100%; height: 100%; background: #f0f0f0; display: flex; align-items: center; justify-content: center;">
          <div style="text-align: center;">
            <h3>Error loading NFT</h3>
            <p>Click to retry</p>
          </div>
        </div>
      `,
      title: 'NFT',
      model: 'Ошибка загрузки',
      modelPercentage: '',
      symbol: 'Ошибка загрузки',
      symbolPercentage: '',
      backdrop: 'Ошибка загрузки',
      backdropPercentage: '',
      telegramLink: null,
      item: item,
      isUnlisted: item.is_unlisted || false,
      isOnMarket: false // ← ДОБАВЛЕНО: в случае ошибки считаем что не на маркете
    };
  }
};

onMounted(async () => {
  const savedAccount = localStorage.getItem('currentAccount');
  if (savedAccount) {
    currentAccountName.value = JSON.parse(savedAccount).name;
  }
  
  if (currentAccountName.value) {
    await loadUserData();
    await loadMarketItems();
    await loadCartFromDatabase();
    
    // Создаем подписки только если они еще не созданы
    if (!marketSubscription.value) {
      marketSubscription.value = supabase
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
    }

    if (!userSubscription.value) {
      userSubscription.value = supabase
        .channel('user_cart_changes')
        .on(
          'postgres_changes',
          {
            event: 'UPDATE',
            schema: 'public',
            table: 'users',
            filter: `name=eq.${currentAccountName.value}`
          },
          (payload) => {
            if (payload.new.bucket && Array.isArray(payload.new.bucket)) {
              const newCartIds = payload.new.bucket;
              const currentCartIds = cartItems.value.map(item => item.id);
              
              if (JSON.stringify(newCartIds.sort()) !== JSON.stringify(currentCartIds.sort())) {
                loadCartFromDatabase();
              }
            }
          }
        )
        .subscribe();
    }
  }

  // Обработка маршрута ДОЛЖНА БЫТЬ ПОСЛЕ загрузки данных
  const route = useRoute();
  console.log('🔄 Текущий маршрут:', route.path, 'itemId:', route.params.itemId);
  
  if (route.params.itemId) {
    await handleRouteItemId(route.params.itemId);
  }

  // Обработчик сообщений от iframe
  window.addEventListener('message', handleIframeMessage);
  
  // Обработчик кнопки "Назад"
  window.addEventListener('popstate', handlePopState);

  watch(() => props.tonConnectUI?.connected, (connected) => {
    if (connected) {
      fetchTonBalance();
    } else {
      tonBalance.value = '0';
    }
  }, { immediate: true });
});


onMounted(() => {
  window.addEventListener('message', (event) => {
    if (event.data.type === 'animationRestarted') {
    }
  });
});
    const modelsLoading = ref(false);
    const nftImageCache = ref({});
    const modelImageCache = ref({});
    const displayMode = ref('list'); // 'list' или 'grouped'
    const setDisplayMode = (mode) => {
      displayMode.value = mode;

    };
const backdropSearchQuery = ref('');
const modelSearchQuery = ref('');
const searchQuery = ref('');
    const isInCart = (itemId) => {
      return cartItems.value.some(item => item.id === itemId);
    };

    const cartItems = ref([]);
    const cartMenu = ref({
      show: false
    });
    const selectedOption = document.querySelector('.filter-option.selected');
    // Извлекаем URL изображения из атрибута src
    const defaultImage = ref(''); // Инициализируем пустой строкой
    // Выводим результат
    console.log(defaultImage); // https://gifts.coffin.meme/easter%20egg/Choco%20Bunny.png
    const selectedImageCache = ref({}); // { "DeskCalendar": "https://gifts.coffin.meme/desk%20calendar/Plum%20Peach.png" }
    const tonBalance = ref(0);
    const isDraggingModal = ref(false);
    const dragStartY = ref(0);
    const dragCurrentY = ref(0);
    const categoriesContainer = ref(null);
    const nftModels = ref([]);
    const expandedModelNfts = ref({});
    const nftModelsCache = ref({});

onMounted(() => {
  // Получаем состояние из маршрута
  if (router.currentRoute.value.state?.activeTab) {
    activeTab.value = router.currentRoute.value.state.activeTab
  }
})
const addToCart = async (item, event) => {
  try {
    if (!cartItems.value.some(cartItem => cartItem.id === item.id)) {
      cartItems.value.push({...item});
      
      await saveCartToDatabase();
      showNotification('Item added to cart', 'success');
      
      if (event) {
        const button = event.currentTarget;
        button.classList.add('added');
        setTimeout(() => {
          button.classList.remove('added');
        }, 600);
      }
    }
  } catch (error) {
    console.error('Error adding to cart:', error);
    showNotification('Error adding to cart', 'error');
  }
};

const removeFromCart = async (itemId, event) => {
  try {
    cartItems.value = cartItems.value.filter(item => item.id !== itemId);
    await saveCartToDatabase();
    localStorage.setItem('userCart', JSON.stringify(cartItems.value));
    
    if (event) {
      const button = event.currentTarget;
      button.classList.add('removed');
      setTimeout(() => {
        button.classList.remove('removed');
      }, 600);
    }
    
    showNotification('Item removed from cart', 'success');
  } catch (error) {
    console.error('Error removing from cart:', error);
    showNotification('Error removing from cart', 'error');
  }
};
// Функция для сохранения корзины в базу данных
const saveCartToDatabase = async () => {
  try {
    if (!currentAccountName.value) return;
    
    // Получаем только ID товаров из корзины
    const cartItemIds = cartItems.value.map(item => item.id);
    
    const { error } = await supabase
      .from('users')
      .update({ 
        bucket: cartItemIds,
        updated_at: new Date().toISOString()
      })
      .eq('name', currentAccountName.value);
    
    if (error) throw error;
    
    console.log('Cart saved to database');
  } catch (error) {
    console.error('Error saving cart to database:', error);
    throw error;
  }
};

// Функция для загрузки корзины из базы данных
const loadCartFromDatabase = async () => {
  try {
    if (!currentAccountName.value) return;
    
    const { data, error } = await supabase
      .from('users')
      .select('bucket')
      .eq('name', currentAccountName.value)
      .single();
    
    if (error && error.code !== 'PGRST116') throw error; // PGRST116 - no rows found
    
    if (data && data.bucket && Array.isArray(data.bucket)) {
      // Загружаем полную информацию о товарах по их ID
      const { data: marketData, error: marketError } = await supabase
        .from('market')
        .select('*')
        .in('id', data.bucket);
      
      if (marketError) throw marketError;
      
      cartItems.value = marketData || [];
      localStorage.setItem('userCart', JSON.stringify(cartItems.value));
    }
  } catch (error) {
    console.error('Error loading cart from database:', error);
    // Fallback to localStorage
    const savedCart = localStorage.getItem('userCart');
    if (savedCart) {
      cartItems.value = JSON.parse(savedCart);
    }
  }
};
// Добавьте эти функции перед функцией openFullscreenView

const extractFullNftName = (url) => {
  if (!url) return null;
  const match = url.match(/\/nft\/([^-]+-\d+)/);
  return match ? match[1] : null;
};




const handleIframeMessage = (event) => {
  if (event.data.type === 'openFullscreenView') {
    console.log('📨 Сообщение от iframe:', event.data);
    resetAllModals();

    let targetItem = null;
    
    // Ищем item по item_id если есть
    if (event.data.itemId) {
      targetItem = findItemByItemId(event.data.itemId);
    }
    
    // Если не нашли, ищем по nft данным
    if (!targetItem && event.data.nftId && event.data.nftName) {
      targetItem = findItemById(event.data.nftId, event.data.nftName);
    }
    
    if (targetItem && targetItem.item_id) {
      console.log('🚀 Навигация к item:', targetItem.item_id);
      
      // Используем replace чтобы избежать дублирования в истории
      const currentRoute = useRoute();
      if (currentRoute.params.itemId !== targetItem.item_id) {
        router.replace(`/shop/${targetItem.item_id}`);
      } else {
        // Если уже на этом route, принудительно вызываем обработку
        console.log('🔄 Уже на правильном route, принудительно открываем');
        openFullscreenView(targetItem);
      }
    } else {
      console.error('❌ Item не найден для навигации');
    }
  }
};

// Функция для очистки корзины в базе данных
const clearCartFromDatabase = async () => {
  try {
    if (!currentAccountName.value) return;
    
    const { error } = await supabase
      .from('users')
      .update({ 
        bucket: [],
        updated_at: new Date().toISOString()
      })
      .eq('name', currentAccountName.value);
    
    if (error) throw error;
    
    console.log('Cart cleared from database');
  } catch (error) {
    console.error('Error clearing cart from database:', error);
  }
};

// Обновляем функцию removeFromCart


// Обновляем функцию clearCart
const clearCart = async () => {
  cartItems.value = [];
  localStorage.removeItem('userCart');
  
  // Очищаем корзину в базе данных
  await clearCartFromDatabase();
  
  showNotification('Cart cleared', 'success');
};

// Обновляем функцию buyAllFromCart
const buyAllFromCart = async () => {
  try {
    // Проверяем, что все товары еще доступны
    const itemIds = cartItems.value.map(item => item.id);
    const { data: availableItems, error: checkError } = await supabase
      .from('market')
      .select('*')
      .in('id', itemIds);

    if (checkError) {
      throw checkError;
    }

    // Создаем мап для быстрой проверки доступности
    const availableItemsMap = {};
    availableItems.forEach(item => {
      availableItemsMap[item.id] = item;
    });

    // Проверяем, все ли товары еще доступны
    const unavailableItems = cartItems.value.filter(item => !availableItemsMap[item.id]);
    if (unavailableItems.length > 0) {
      showNotification('Some items in your cart are no longer available', 'error');
      // Удаляем недоступные товары из корзины
      unavailableItems.forEach(item => removeFromCart(item.id));
      return;
    }

    // Рассчитываем общую стоимость
    const totalCost = cartItems.value.reduce((total, item) => {
      return total + (item.price_per_unit * (item.amount || 1));
    }, 0);

    // Проверяем баланс пользователя
    const { data: userData, error: fetchError } = await supabase
      .from('users')
      .select('ton_balance, nft_links')
      .eq('name', currentAccountName.value)
      .single();

    if (fetchError) {
      throw fetchError;
    }

    const currentBalance = parseFloat(userData.ton_balance) || 0;
    const currentLinks = userData.nft_links || [];

    if (currentBalance < totalCost) {
      showNotification(`Insufficient TON balance. Need ${totalCost} TON, have ${currentBalance} TON`, 'error');
      return;
    }

    const updatedLinks = [...currentLinks];
    const purchasePromises = [];
    const purchasedItemIds = [];

    // Выполняем покупки последовательно для надежности
    for (const item of cartItems.value) {
      const purchasePromise = async () => {
        // Проверяем еще раз доступность товара
        const { data: currentItem, error: itemError } = await supabase
          .from('market')
          .select('*')
          .eq('id', item.id)
          .single();

        if (itemError || !currentItem) {
          throw new Error(`Item ${item.id} is no longer available`);
        }

        // Рассчитываем сумму для продавца (98%)
        const sellerAmount = item.price_per_unit * (item.amount || 1) * 0.98;
        
        // Комиссия платформы (2%)
        const platformFee = item.price_per_unit * (item.amount || 1) * 0.02;

        const nftData = {
          url: item.nft_object?.url || item.url || '',
          name: getNftDisplayName(item.nft_type, item.nft_object),
          model: item.nft_object?.model || '',
          symbol: item.nft_object?.symbol || '',
          backdrop: item.nft_object?.backdrop || '',
          acquired_at: new Date().toISOString()
        };

        updatedLinks.push(nftData);

        // Пополняем баланс продавца
        const { data: sellerData } = await supabase
          .from('users')
          .select('ton_balance')
          .eq('name', item.seller)
          .single();

        if (sellerData) {
          const sellerCurrentBalance = parseFloat(sellerData.ton_balance) || 0;
          const newSellerBalance = sellerCurrentBalance + sellerAmount;

          await supabase
            .from('users')
            .update({ ton_balance: newSellerBalance })
            .eq('name', item.seller);
        }

        // Немедленно удаляем с рынка
        const { error: deleteError } = await supabase
          .from('market')
          .delete()
          .eq('id', item.id);

        if (deleteError) {
          throw deleteError;
        }

        // Запоминаем ID купленных товаров
        purchasedItemIds.push(item.id);

        // Записываем активность
        await recordPurchaseActivity(item, currentAccountName.value, item.amount || 1);
      };

      purchasePromises.push(purchasePromise());
    }

    // Ждем завершения всех покупок
    await Promise.all(purchasePromises);

    // Обновляем баланс покупателя (списываем полную сумму)
    const newBuyerBalance = currentBalance - totalCost;
    await supabase
      .from('users')
      .update({ 
        ton_balance: newBuyerBalance,
        nft_links: updatedLinks
      })
      .eq('name', currentAccountName.value);

    // Синхронизация локального состояния
    marketItems.value = marketItems.value.filter(item => !purchasedItemIds.includes(item.id));
    myMarketItems.value = myMarketItems.value.filter(item => !purchasedItemIds.includes(item.id));

    await clearCart();
    showNotification('All items purchased successfully!', 'success');
    
    // Обновляем локальный баланс
    tonBalance.value = newBuyerBalance.toString();
    
    // Закрываем fullscreen view если открыт
    if (htmlModal.value.show) {
      htmlModal.value.show = false;
    }
    
    // Обновляем список товаров
    await loadMarketItems();
    
    // Переходим на /shop
    router.push('/shop');
    
  } catch (error) {
    console.error('Error purchasing items from cart:', error);
    showNotification(`Error purchasing items: ${error.message}`, 'error');
  }
};

// Функции для работы с корзиной
    const toggleCartMenu = () => {
      cartMenu.value.show = !cartMenu.value.show;
      sortMenu.value.show = false;
      priceRangeMenu.value.show = false;
    };


    const calculateCartTotal = () => {
      return cartItems.value.reduce((total, item) => {
        // Конвертируем все в TON для упрощения
        if (item.currency === 'TON') {
          return total + (item.price_per_unit * item.amount);
        } else {
          // Здесь можно добавить конвертацию AMHSL в TON если нужно
          return total + (item.price_per_unit * item.amount);
        }
      }, 0).toFixed(2);
    };
const getTotalNFTsInCart = () => {
  return cartItems.value.reduce((total, item) => total + (item.amount || 1), 0);
};

onMounted(async () => {
  const savedAccount = localStorage.getItem('currentAccount');
  if (savedAccount) {
    currentAccountName.value = JSON.parse(savedAccount).name;
  }
  
  if (currentAccountName.value) {
    await loadUserData();
    await loadMarketItems();
    await loadCartFromDatabase(); // Загружаем корзину из базы данных
    
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

    // Подписка на изменения корзины пользователя
    const userSubscription = supabase
      .channel('user_cart_changes')
      .on(
        'postgres_changes',
        {
          event: 'UPDATE',
          schema: 'public',
          table: 'users',
          filter: `name=eq.${currentAccountName.value}`
        },
        (payload) => {
          // Обновляем корзину если она изменилась из другого источника
          if (payload.new.bucket && Array.isArray(payload.new.bucket)) {
            const newCartIds = payload.new.bucket;
            const currentCartIds = cartItems.value.map(item => item.id);
            
            // Проверяем, есть ли различия
            if (JSON.stringify(newCartIds.sort()) !== JSON.stringify(currentCartIds.sort())) {
              loadCartFromDatabase();
            }
          }
        }
      )
      .subscribe();

    // Убираем подписки при размонтировании компонента
    onUnmounted(() => {
      supabase.removeChannel(marketSubscription);
      supabase.removeChannel(userSubscription);
    });
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
  const openHtmlModal = async (item) => {
  try {
    const nftId = extractNftIdFromHtml(item.html_content);
    const telegramLink = nftId ? `https://t.me/nft/${nftId}` : null;
    
    // Парсим nft_object для получения model, symbol, backdrop
    let model = 'Не указано';
    let symbol = 'Не указано';
    let backdrop = 'Не указано';
    
    try {
      if (item.nft_object) {
        const nftObj = typeof item.nft_object === 'string' 
          ? JSON.parse(item.nft_object) 
          : item.nft_object;
        
        model = nftObj.model || model;
        symbol = nftObj.symbol || symbol;
        backdrop = nftObj.backdrop || backdrop;
      }
    } catch (parseError) {
      console.error('Ошибка парсинга nft_object:', parseError);
    }

    htmlModal.value = {
      show: true,
  htmlContent: item.html_content,
  title: getNftDisplayName(item.nft_type, item.nft_object),
      model,
      backdrop,
      symbol,
      telegramLink,
      item: item
    };

  } catch (err) {
    console.error('Ошибка при открытии модального окна:', err);
    htmlModal.value = {
      show: true,
      htmlContent: item.html_content,
      title: getNftDisplayName(item.nft_type),
      model: 'Ошибка загрузки',
      backdrop: 'Ошибка загрузки',
      symbol: 'Ошибка загрузки',
      telegramLink: null,
      item: item
    };
  }
};

  // Инициализация категорий фильтров
  filterCategories.value = [
    { id: 'nft', name: 'NFT' },
    { id: 'model', name: 'Model' },
    { id: 'symbol', name: 'Symbol' },
    { id: 'backdrop', name: 'Backdrop' },
    { id: 'price', name: selectedIdFilter.value ? `ID: ${selectedIdFilter.value}` : 'ID' }
  ];

  // Загрузка символов
  loadSymbolOptions();
  
  // Дебаг данных
  debugPatternsData();

  // Добавляем обработчик скролла для контейнера категорий
  const container = document.querySelector('.filter-categories-container');
  if (container) {
    let isDown = false;
    let startX;
    let scrollLeft;

    container.addEventListener('mousedown', (e) => {
      isDown = true;
      startX = e.pageX - container.offsetLeft;
      scrollLeft = container.scrollLeft;
    });

    container.addEventListener('mouseleave', () => {
      isDown = false;
    });

    container.addEventListener('mouseup', () => {
      isDown = false;
    });

    container.addEventListener('mousemove', (e) => {
      if (!isDown) return;
      e.preventDefault();
      const x = e.pageX - container.offsetLeft;
      const walk = (x - startX) * 2;
      container.scrollLeft = scrollLeft - walk;
    });
  }

  // iOS специфичные стили
  const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
  if (isIOS) {
    const style = document.createElement('style');
    style.textContent = `
      .filter-categories-container {
        -webkit-overflow-scrolling: touch !important;
      }
    `;
    document.head.appendChild(style);
  }
});

    // Загрузка корзины из localStorage при монтировании
    onMounted(() => {
      const savedCart = localStorage.getItem('userCart');
      if (savedCart) {
        cartItems.value = JSON.parse(savedCart);
      }
    });





const cancelSaleModal = ref({
  show: false,
  item: null,
  nftType: '',
  loading: false // ← ДОБАВЬТЕ ЭТО
});

const editPriceModal = ref({
  show: false,
  item: null,
  nftType: '',
  currentPrice: 0,
  newPrice: '',
  loading: false // ← ДОБАВЬТЕ ЭТО
});

// В ref секции добавьте:
const loadingActivity = ref(false);
const activityItems = ref([]);
const selectedActivityType = ref('all');
const showOnlyMyActivity = ref(false); // ← Новый переключатель

// Функция загрузки ВСЕХ операций
const loadActivityHistory = async () => {
  try {
    loadingActivity.value = true;
    
    console.log('📊 Загрузка ВСЕЙ истории активности');

    // Загружаем ВСЕ записи из таблицы activity_history
    const { data, error } = await supabase
      .from('activity_history')
      .select('*')
      .order('created_at', { ascending: false })

    if (error) {
      console.error('❌ Ошибка загрузки активности:', error);
      activityItems.value = [];
    } else {
      console.log(`✅ Загружено ${data?.length || 0} записей активности (все операции)`);
      activityItems.value = data || [];
      
      if (data && data.length > 0) {
      } else {
        console.log('📭 История активности пуста');
      }
    }
    
  } catch (error) {
    console.error('❌ Общая ошибка загрузки истории активности:', error);
    activityItems.value = [];
  } finally {
    loadingActivity.value = false;
  }
};



const recordPurchaseActivity = async (item, buyerName, amount = 1) => {
  if (!buyerName) {
    console.error('Missing buyer name for purchase activity');
    return null;
  }

  return await addActivityRecord({
    user_name: buyerName,
    item_id: item.item_id || item.id,
    nft_type: item.nft_type,
    nft_object: item.nft_object,
    html_content: item.html_content,
    operation_type: 'purchase',
    price_per_unit: item.price_per_unit,
    currency: item.currency || 'TON',
    amount: amount,
    total_price: item.price_per_unit * amount,
    counterparty: item.seller
  });
};

const recordDelistingActivity = async (item) => {
  if (!item.seller) {
    console.error('Missing seller for delisting activity');
    return null;
  }

  return await addActivityRecord({
    user_name: item.seller,
    item_id: item.item_id,
    nft_type: item.nft_type,
    nft_object: item.nft_object,
    html_content: item.html_content,
    operation_type: 'delisting',
    price_per_unit: item.price_per_unit,
    currency: item.currency || 'TON',
    amount: item.amount || 1,
    total_price: item.total_price || item.price_per_unit
  });
};

const recordPriceEditActivity = async (item, oldPrice, newPrice) => {
  // Проверяем обязательные поля
  if (!currentAccountName.value || !item) {
    console.error('Missing required fields for activity record');
    return null;
  }

  return await addActivityRecord({
    user_name: currentAccountName.value, // Текущий пользователь
    item_id: item.item_id || item.id,
    nft_type: item.nft_type,
    nft_object: item.nft_object,
    html_content: item.html_content,
    operation_type: 'price_edit',
    price_per_unit: newPrice,
    old_price: oldPrice,
    currency: item.currency || 'TON',
    amount: item.amount || 1,
    total_price: newPrice * (item.amount || 1)
  });
};


const addActivityRecord = async (activityData) => {
  try {
    if (!activityData.user_name) {
      console.error('Missing user_name for activity record');
      return null;
    }

    if (!activityData.operation_type) {
      console.error('Missing operation_type for activity record');
      return null;
    }

    // УБИРАЕМ поле id - база данных сама его сгенерирует
    const record = {
      user_name: activityData.user_name,
      operation_type: activityData.operation_type,
      item_id: activityData.item_id || null,
      nft_type: activityData.nft_type || null,
      nft_object: activityData.nft_object || null,
      html_content: activityData.html_content || null,
      price_per_unit: activityData.price_per_unit || null, // ← ИСПРАВЛЕНО: activityData.price_per_unit
      old_price: activityData.old_price || null,
      currency: activityData.currency || 'TON',
      amount: activityData.amount || 1,
      total_price: activityData.total_price || null,
      counterparty: activityData.counterparty || null,
      created_at: new Date().toISOString()
    };

    const { data, error } = await supabase
      .from('activity_history')
      .insert([record])
      .select();

    if (error) {
      console.error('❌ Ошибка добавления записи активности:', error);
      return null;
    }

    console.log('✅ Запись активности добавлена:', data[0]);
    
    if (activeTab.value === 'activity') {
      loadActivityHistory();
    }
    
    return data[0];
    
  } catch (error) {
    console.error('❌ Ошибка добавления записи активности:', error);
    return null;
  }
};
const toggleMyActivity = (event) => {
  const newValue = event.target.checked;
  console.log(`🔍 Переключение My Activity: ${showOnlyMyActivity.value} -> ${newValue}`);
  
  showOnlyMyActivity.value = newValue;
  
  console.log(`🔍 My Activity: ${showOnlyMyActivity.value ? 'ON (полученные офферы)' : 'OFF (отправленные офферы)'}`);
  
  // Перезагружаем офферы с новым фильтром
  loadOffers(false);
};

// Остальные функции
const setActivityType = (type) => {
  selectedActivityType.value = type;
};


// Офферы, созданные текущим пользователем
const myCreatedOffers = computed(() => {
  return activityItems.value.filter(offer => 
    offer.buyer_name === currentAccountName.value
  );
});

// Офферы, полученные текущим пользователем
const myReceivedOffers = computed(() => {
  return activityItems.value.filter(offer => {
    if (offer.operation_type === 'purchase') {
      return offer.user_name === currentAccountName.value;
    }
    return offer.counterparty === currentAccountName.value;
  });
});

// Альтернативный вариант с годом для старых записей
const formatActivityDateWithYear = (dateString) => {
  try {
    const date = new Date(dateString);
    const now = new Date();
    const currentYear = now.getFullYear();
    const recordYear = date.getFullYear();
    
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const day = date.getDate().toString().padStart(2, '0');
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    
    // Если запись не из текущего года, добавляем год
    if (recordYear !== currentYear) {
      return `${month}.${day}.${recordYear.toString().slice(-2)} ${hours}:${minutes}`;
    }
    
    return `${month}.${day} ${hours}:${minutes}`;
  } catch (error) {
    return '--.-- --:--';
  }
};

// Альтернативный вариант - всегда показывать полное время
const formatActivityDateFull = (dateString) => {
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      year: 'numeric'
    }) + ' • ' + date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    });
  } catch (error) {
    return 'Unknown time';
  }
};




// Обновленная функция executeCancelSale с защитой от повторных нажатий
const executeCancelSale = async () => {
  try {
    // Защита от повторных нажатий
    if (cancelSaleModal.value.loading) {
      console.log('⏳ Снятие с продажи уже обрабатывается...');
      return;
    }
    
    // Блокируем кнопку
    cancelSaleModal.value.loading = true;
    
    const { item } = cancelSaleModal.value;

    if (!item) {
      showNotification('Invalid item data', 'error');
      cancelSaleModal.value.loading = false;
      return;
    }

    console.log('🔄 Начинаем снятие с продажи NFT...', item.id);

    // Извлекаем имя из nft_object
    let nftName = 'Unknown NFT';
    if (item.nft_object) {
      try {
        const nftObj = typeof item.nft_object === 'string' 
          ? JSON.parse(item.nft_object) 
          : item.nft_object;
        nftName = nftObj.name || nftName;
      } catch (e) {
        console.error('Error parsing nft_object for name:', e);
      }
    }

    // Подготавливаем данные для добавления в nft_links
    const nftData = {
      url: item.nft_object?.url || item.url || '',
      name: nftName, // Добавляем имя из nft_object
      model: item.nft_object?.model || '',
      symbol: item.nft_object?.symbol || '',
      backdrop: item.nft_object?.backdrop || '',
      acquired_at: new Date().toISOString() // Обновляем дату приобретения
    };

    // Получаем текущие nft_links пользователя
    const { data: userData, error: fetchError } = await supabase
      .from('users')
      .select('nft_links')
      .eq('name', currentAccountName.value)
      .single();

    if (fetchError) throw fetchError;

    const currentLinks = userData.nft_links || [];
    
    // Добавляем NFT обратно в nft_links
    const updatedLinks = [...currentLinks, nftData];

    // Обновляем nft_links пользователя
    const { error: updateError } = await supabase
      .from('users')
      .update({ nft_links: updatedLinks })
      .eq('name', currentAccountName.value);

    if (updateError) throw updateError;

    // Удаляем item с рынка
    const { error: deleteError } = await supabase
      .from('market')
      .delete()
      .eq('id', item.id);

    if (deleteError) throw deleteError;

    console.log('✅ NFT успешно снято с продажи');
    
    showNotification('NFT успешно снято с продажи!', 'success');
    
    // Закрываем модальные окна
    cancelSaleModal.value.show = false;
    
    // Показываем успешное снятие с продажи с анимацией
    showSuccessAnimation('delisting');
    
    // Закрываем fullscreen view если он открыт
    if (htmlModal.value.show) {
      htmlModal.value.show = false;
    }
    
    // Переходим на /shop
    router.push('/shop');

    // Обновляем данные
    await loadMarketItems();
    await loadUnlistedNfts();

  } catch (error) {
    console.error('Ошибка снятия с продажи:', error);
    showNotification('Ошибка снятия с продажи', 'error');
  } finally {
    // Всегда разблокируем кнопку
    cancelSaleModal.value.loading = false;
  }
};

// Обновленная функция executePriceEdit с защитой от повторных нажатий
const executePriceEdit = async () => {
  try {
    // Защита от повторных нажатий
    if (editPriceModal.value.loading) {
      console.log('⏳ Изменение цены уже обрабатывается...');
      return;
    }
    
    // Блокируем кнопку
    editPriceModal.value.loading = true;
    
    const { item, newPrice, currentPrice } = editPriceModal.value;
    
    // Проверяем, что новая цена отличается от текущей
    if (parseFloat(newPrice) === parseFloat(currentPrice)) {
      showNotification('New price must be different from current price', 'error');
      editPriceModal.value.loading = false;
      return;
    }
    
    if (!newPrice || newPrice <= 0) {
      showNotification('Please enter a valid price', 'error');
      editPriceModal.value.loading = false;
      return;
    }

    console.log('🔄 Обновление цены для NFT...', item.id);

    // Сохраняем старую цену для записи в историю
    const oldPrice = currentPrice;

    // Обновляем цену в базе данных
    const { error } = await supabase
      .from('market')
      .update({ 
        price_per_unit: parseFloat(newPrice),
        total_price: parseFloat(newPrice) * item.amount,
        created_at: new Date().toISOString()
      })
      .eq('id', item.id);

    if (error) throw error;

    // Обновляем локальные данные
    const itemIndex = marketItems.value.findIndex(marketItem => marketItem.id === item.id);
    if (itemIndex !== -1) {
      marketItems.value[itemIndex].price_per_unit = parseFloat(newPrice);
      marketItems.value[itemIndex].total_price = parseFloat(newPrice) * item.amount;
    }

    // Записываем в историю с корректными данными
    await recordPriceEditActivity(item, oldPrice, newPrice);

    console.log('✅ Цена успешно обновлена');
    
    showNotification('Price updated successfully!', 'success');
    editPriceModal.value.show = false;
    
    // Показываем успешное изменение цены с анимацией
    showSuccessAnimation('price_edit');
    
  } catch (error) {
    console.error('Error updating price:', error);
    showNotification('Error updating price', 'error');
  } finally {
    // Всегда разблокируем кнопку
    editPriceModal.value.loading = false;
  }
};






// В секции методов добавьте метод для сброса всех модальных окон
const resetAllModals = () => {
  // Сбрасываем все модальные окна
  buyModal.value.show = false;
  cancelSaleModal.value.show = false;
  editPriceModal.value.show = false;
  sellModal.value.show = false;
  transferModal.value.show = false;
  giftModal.value.show = false; // ← ДОБАВЬТЕ ЭТУ СТРОКУ
  
  // Сбрасываем любые другие модальные окна, которые могут быть открыты
  if (itemDetailsModal.value) {
    itemDetailsModal.value.show = false;
  }
};

// Обновите функцию closeHtmlModal
const closeHtmlModal = () => {
  // Сбрасываем все модальные окна перед закрытием
  resetAllModals();
  
  // Закрываем полноэкранный просмотр
  htmlModal.value.show = false;
  
  // Возвращаемся к основному маршруту магазина
  const currentRoute = useRoute();
  if (currentRoute.params.itemId) {
    router.push('/shop');
  }
};

// Также можно добавить сброс при нажатии кнопки "Назад"
const handlePopState = () => {
  if (htmlModal.value.show) {
    resetAllModals();
    closeHtmlModal();
  }
};



// Функция для удаления конкретного NFT из фильтра
const removeNftFromFilter = (nftType) => {
  console.log(`🗑️ Удаление NFT из фильтра: ${nftType}`);
  
  // Удаляем NFT из фильтра
  const nftIndex = selectedFilters.value.nft.indexOf(nftType);
  if (nftIndex !== -1) {
    selectedFilters.value.nft.splice(nftIndex, 1);
  }
  
  // Получаем все модели для этого NFT и удаляем их из фильтра
  const modelsToRemove = [];
  if (nftModelsCache.value[nftType]) {
    nftModelsCache.value[nftType].forEach(modelString => {
      const modelName = modelString.split(' — ')[0].trim();
      modelsToRemove.push(modelName);
    });
  }
  
  // Удаляем эти модели из выбранных фильтров
  if (modelsToRemove.length > 0) {
    selectedFilters.value.model = selectedFilters.value.model.filter(
      model => !modelsToRemove.includes(model)
    );
    console.log(`✅ Удалены модели для NFT ${nftType}:`, modelsToRemove);
  }
  
  // Форсируем обновление реактивности
  selectedFilters.value = { ...selectedFilters.value };
  
  console.log(`🎯 После удаления - NFT:`, selectedFilters.value.nft);
  console.log(`🎯 После удаления - модели:`, selectedFilters.value.model);
};

const giftModal = ref({
  show: false,
  item: null,
  recipientName: '',
  loading: false
});
const clearFilterCategory = (category) => {
  console.log(`🧹 Очистка фильтра категории: ${category}`);
  
  switch (category) {
    case 'nft':
      // При очистке NFT также очищаем зависимые фильтры
      selectedFilters.value.nft = [];
      selectedFilters.value.model = [];
      selectedFilters.value.symbol = [];
      selectedFilters.value.backdrop = [];
      console.log('✅ Очищены все фильтры (nft, model, symbol, backdrop)');
      break;
      
    case 'model':
      selectedFilters.value.model = [];
      console.log('✅ Очищены модели');
      break;
      
    case 'symbol':
      selectedFilters.value.symbol = [];
      console.log('✅ Очищены символы');
      break;
      
    case 'backdrop':
      selectedFilters.value.backdrop = [];
      console.log('✅ Очищены фоны');
      break;
      
    case 'price':
      clearIdFilter();
      console.log('✅ Очищен ID фильтр');
      break;
  }
  
  // Форсируем обновление реактивности
  selectedFilters.value = { ...selectedFilters.value };
  
  // Показываем уведомление
  showNotification(`Фильтр ${getCategoryDisplayName(category)} очищен`, 'success');
};

// Вспомогательная функция для отображения названий категорий
const getCategoryDisplayName = (category) => {
  const names = {
    'nft': 'NFT',
    'model': 'Model', 
    'symbol': 'Symbol',
    'backdrop': 'Backdrop',
    'price': 'ID'
  };
  return names[category] || category;
};
const extractBackdropFromNft = (item) => {
  try {
    
    let backdrop = null;
    
    // Для activity items используем прямое поле backdrop
    if (item.backdrop) {
      backdrop = item.backdrop;
    }
    // Для market items используем существующую логику
    else {
      const sources = [
        { name: 'nft_metadata', value: item.nft_metadata?.backdrop },
        { name: 'backdrop field', value: item.backdrop },
        { name: 'nft_object', value: getBackdropFromNftObject(item.nft_object) },
        { name: 'html_content', value: getBackdropFromHtml(item.html_content) }
      ];
      
      for (const source of sources) {
        if (source.value) {
          backdrop = source.value;
          break;
        }
      }
    }
    
    if (backdrop) {
      // ИСПРАВЛЕНО: убираем ТОЛЬКО проценты, сохраняем ВСЕ слова
      const cleanBackdrop = backdrop
        .replace(/\d+\.?\d*%/, '') // удаляем проценты
        .replace(/^\s+|\s+$/g, '') // обрезаем пробелы
        .replace(/\s+/g, ' '); // заменяем множественные пробелы на один
      
      return cleanBackdrop;
    }
    
    console.log('❌ Backdrop не найден ни в одном источнике');
    return null;
    
  } catch (error) {
    console.error('❌ Ошибка извлечения backdrop:', error);
    return null;
  }
};


async function getModelOptions() {
  try {
    console.log('Получение опций моделей...', selectedFilters.value.nft);
    
    if (!selectedFilters.value.nft || selectedFilters.value.nft.length === 0) {
      console.log('Нет выбранных NFT для загрузки моделей');
      return [];
    }

    // Загружаем модели для всех выбранных NFT
    const modelPromises = selectedFilters.value.nft.map(nft => loadNftModels(nft));
    const modelsResults = await Promise.all(modelPromises);
    
    // Объединяем все модели в один массив
    const allModels = modelsResults.flat();
    
    console.log(`Всего загружено моделей: ${allModels.length}`);
    
    return allModels.map(model => {
      const [name, rarityText] = model.split(' — ');
      const rarity = parseFloat(rarityText?.match(/\d+\.?\d*/)?.[0] || 0);
      
      return {
        name,
        rarity,
        imageUrl: getModelImageUrl(selectedFilters.value.nft[0], model),
        parentNft: selectedFilters.value.nft[0]
      };
    }).sort((a, b) => a.name.localeCompare(b.name));
    
  } catch (error) {
    console.error('Ошибка получения моделей:', error);
    return [];
  }
}
// Вспомогательные функции

// Отладка для getBackdropFromNftObject
const getBackdropFromNftObject = (nftObject) => {
  if (!nftObject) {
    console.log('   ❌ nftObject пустой');
    return null;
  }
  
  try {
    const nftObj = typeof nftObject === 'string' ? JSON.parse(nftObject) : nftObject;
    const backdrop = nftObj.backdrop || null;
    return backdrop;
  } catch (e) {
    console.log('   ❌ Ошибка парсинга nft_object:', e);
    return null;
  }
};

// Отладка для getBackdropFromHtml
const getBackdropFromHtml = (htmlContent) => {
  if (!htmlContent) {
    return null;
  }
  
  const patterns = [
    /backdrop["']?:\s*["']([^"']+)["']/i,
    /backdrop["']?:\s*[']([^']+)[']/i,
    /backdrop["']?:\s*([^\s>'"]+)/i,
    /backdrop\s*:\s*([^<,]+)/i,
    /backdrop["']?\s*:\s*["']([^"']+)["']/i
  ];
  
  for (const pattern of patterns) {
    const match = htmlContent.match(pattern);
    if (match && match[1]) {
      const result = match[1].trim();
      console.log(`   ✅ Backdrop найден в HTML (паттерн ${patterns.indexOf(pattern)}): "${result}"`);
      return result;
    }
  }
  
  return null;
};
const getAllModelOptions = () => {
  try {
    console.log('Получение всех опций моделей...');
    
    const allModels = [];
    
    // Проходим по всем выбранным NFT и собираем их модели
    selectedFilters.value.nft.forEach(nftType => {
      if (nftModelsCache.value[nftType]) {
        nftModelsCache.value[nftType].forEach(model => {
          const [name, rarityText] = model.split(' — ');
          const rarity = parseFloat(rarityText?.match(/\d+\.?\d*/)?.[0] || 0);
          
          allModels.push({
            name,
            rarity,
            imageUrl: getModelImageUrl(nftType, model),
            parentNft: nftType
          });
        });
      }
    });
    
    // Сортируем по имени для удобства
    allModels.sort((a, b) => a.name.localeCompare(b.name));
    
    console.log(`Всего моделей для отображения: ${allModels.length}`);
    return allModels;
    
  } catch (error) {
    console.error('Ошибка получения всех моделей:', error);
    return [];
  }
};

    // Добавляем новые переменные
    const expandedNfts = ref({}); // Состояние развернутости для каждого NFT
    const selectedNftModels = ref({}); // Модели для каждого NFT
    const modelCache = ref({}); // Кэш моделей
    const setActiveFilter = async (event, categoryId) => {
  try {
    console.log('🔄 Активирована категория:', categoryId);
    console.log('📊 Текущая активная категория:', activeFilterCategory.value);
    
    const button = event.currentTarget;
    
    // Обновляем активную категорию
    if (activeFilterCategory.value === categoryId) {
      activeFilterCategory.value = null;
      console.log('❌ Закрываем категорию:', categoryId);
    } else {
      activeFilterCategory.value = categoryId;
      console.log('✅ Открываем категорию:', categoryId);
      
      // Для symbol загружаем данные если нужно
      if (categoryId === 'symbol') {
        console.log('🔄 Загружаем символы...');
        await loadSymbolOptions();
        console.log('📊 Загружено символов:', symbolOptions.value.length);
      }
    }
    
    // Обновляем категории фильтров
    updateFilterCategories();
    
    nextTick(() => {
      console.log('🎯 Категория установлена:', activeFilterCategory.value);
    });
    
  } catch (error) {
    console.error('❌ Error in setActiveFilter:', error);
  }
};








// Функция для обновления списка категорий фильтров
const updateFilterCategories = () => {
  filterCategories.value = [
    { id: 'nft', name: 'NFT' },
    { id: 'model', name: 'Model' },
    { id: 'symbol', name: 'Symbol' },
    { id: 'backdrop', name: 'Backdrop' },
    { 
      id: 'price', 
      name: selectedIdFilter.value ? `ID: ${selectedIdFilter.value}` : 'ID' 
    }
  ];
};
const justSelectedNft = ref(null);

watch(() => nftModelsCache.value, (newCache) => {
  // Автоматически раскрываем первую группу при загрузке моделей
  if (Object.keys(newCache).length > 0 && Object.keys(expandedNftGroups.value).length === 0) {
    const firstNftType = selectedFilters.value.nft[0];
    if (firstNftType) {
      expandedNftGroups.value[firstNftType] = true;
    }
  }
}, { deep: true });
const expandedNftGroups = ref({});

const toggleNftGroup = async (nftType) => {
  if (!expandedNftGroups.value[nftType] && !nftModelsCache.value[nftType]) {
    await loadNftModels(nftType);
  }
  
  expandedNftGroups.value = {
    ...expandedNftGroups.value,
    [nftType]: !expandedNftGroups.value[nftType]
  };
};
const getModelsForNftSortedByRarity = (nftType) => {
  try {
    console.group(`🔍 Получение моделей для NFT: ${nftType}`);
    
    if (!nftModelsCache.value[nftType]) {
      console.log('❌ Нет моделей в кэше');
      console.groupEnd();
      return [];
    }
    
    console.log('📋 Модели в кэше:', nftModelsCache.value[nftType]);
    
    const searchQuery = modelSearchQuery.value.toLowerCase().trim();
    const modelsData = [];
    
    nftModelsCache.value[nftType].forEach((modelString, index) => {
      console.log(`📝 Обработка модели ${index + 1}:`, modelString);
      
      const parts = modelString.split(' — ');
      if (parts.length === 2) {
        const name = parts[0].trim();
        const rarityText = parts[1].trim();
        const rarity = parseFloat(rarityText.replace('%', ''));
        
        console.log('🔤 Название модели:', name);
        console.log('📊 Редкость:', rarityText, rarity);
        
        // Фильтрация по поисковому запросу
        const matchesSearch = searchQuery === '' || 
                            name.toLowerCase().includes(searchQuery) ||
                            rarityText.toLowerCase().includes(searchQuery);
        
        console.log('🔍 Соответствует поиску:', matchesSearch);
        
        if (name && !isNaN(rarity) && matchesSearch) {
          // Генерируем URL изображения
          const imageUrl = getModelImageUrl(nftType, name);
          
          modelsData.push({
            name,
            rarity,
            rarityText,
            parentNft: nftType,
            imageUrl: imageUrl,
            isSelected: isOptionSelected('model', name),
            displayName: getNftDisplayNameForGroup(nftType),
            floorPrice: getFloorPrice('model', name)
          });
          
          console.log('✅ Модель добавлена:', name);
        }
      } else {
        console.log('⚠️ Неправильный формат модели:', modelString);
      }
    });
    
    // СОРТИРОВКА: сначала выбранные, затем по редкости
    modelsData.sort((a, b) => {
      if (a.isSelected && !b.isSelected) return -1;
      if (!a.isSelected && b.isSelected) return 1;
      return a.rarity - b.rarity;
    });
    
    console.log(`📊 Итоговое количество моделей: ${modelsData.length}`);
    console.log('📋 Данные моделей:', modelsData);
    console.groupEnd();
    
    return modelsData;
    
  } catch (error) {
    console.error(`❌ Ошибка получения моделей для ${nftType}:`, error);
    console.groupEnd();
    return [];
  }
};

// Computed свойства для выбранных и невыбранных моделей
const selectedModelOptions = computed(() => {
  const allOptions = getAllModelDataSortedByRarity();
  return allOptions.filter(option => 
    isOptionSelected('model', option.name)
  );
});

const unselectedModelOptions = computed(() => {
  const allOptions = getAllModelDataSortedByRarity();
  return allOptions.filter(option => 
    !isOptionSelected('model', option.name)
  );
});

const getModelsForNft = async (nftType) => {
  if (!nftModelsCache.value[nftType]) {
    await loadNftModels(nftType);
  }

  const models = nftModelsCache.value[nftType] || [];
  return models.map(model => {
    const [name, rarityText] = model.split(' — ');
    const rarity = parseFloat(rarityText?.match(/\d+\.?\d*/)?.[0] || 0);
    
    return {
      name,
      rarity,
      imageUrl: getModelImageUrl(nftType, model),
      parentNft: nftType
    };
  }).sort((a, b) => a.rarity - b.rarity);
};


const extractModelRarity = (item) => {
  if (!item.nft_object) return 0;
  try {
    const model = JSON.parse(item.nft_object).model;
    const match = model.match(/(\d+\.?\d*)%/);
    return match ? parseFloat(match[1]) : 0;
  } catch {
    return 0;
  }
};

const openCartItemModal = (item) => {
  openHtmlModal(item); // Используем существующую функцию открытия модалки
};
// .------------------------------------------------------------------------------

// Добавьте эту функцию для отладки
// Добавьте эту функцию для отладки
const debugPatternsData = async () => {
  const { data } = await supabase
    .from('patterns')
    .select('links, names')
    .limit(5);
  
  console.log('Структура данных patterns:');
  data.forEach((item, index) => {
    console.log(`Запись ${index + 1}:`);
    console.log('  links:', item.links);
    console.log('  names:', item.names);
    console.log('  types:', {
      links: Array.isArray(item.links) ? 'array' : typeof item.links,
      names: Array.isArray(item.names) ? 'array' : typeof item.names
    });
  });
};

// Вызовите эту функцию в onMounted
onMounted(() => {
  debugPatternsData();
  loadSymbolOptions();
});

const isPriceChanged = computed(() => {
  const { newPrice, currentPrice } = editPriceModal.value;
  if (!newPrice || !currentPrice) return false;
  return parseFloat(newPrice) !== parseFloat(currentPrice);
});
const checkPriceChange = () => {
  // Функция автоматически обновляет computed свойство isPriceChanged
  // через реактивность Vue
};
// Функция для загрузки символов из базы данных
const symbolOptions = ref([]);
const symbolsLoading = ref(false);
// Функция для обработки нажатия кнопки назад
const handleBack = () => {
      router.go(-1); // Возврат на предыдущую страницу
      // Или можно использовать router.push('/shop') для возврата в магазин
};

// Функция для загрузки символов из базы данных
const loadSymbolOptions = async () => {
  try {
    symbolsLoading.value = true;
    console.log('Загрузка символов из базы данных...');
    
    const { data, error } = await supabase
      .from('patterns')
      .select('links, names')
      .limit(250);

    if (error) {
      console.error('Ошибка загрузки символов:', error);
      return;
    }

    console.log('Полученные данные patterns:', data);
    
    const symbolData = [];

    data.forEach(item => {
      // Обрабатываем новый формат данных (объекты вместо массивов)
      if (item.links && item.names && typeof item.links === 'object' && typeof item.names === 'object') {
        // Для формата {url: '...'} и {en: '...'}
        const link = item.links.url;
        const name = item.names.en;
        
        if (link && name) {
          symbolData.push({
            name: name,
            imageUrl: link,
            value: name.toLowerCase()
          });
        }
      }
      // Сохраняем старую обработку для обратной совместимости
      else {
        try {
          const links = typeof item.links === 'string' ? JSON.parse(item.links) : item.links;
          const names = typeof item.names === 'string' ? JSON.parse(item.names) : item.names;
          
          if (Array.isArray(links) && Array.isArray(names)) {
            links.forEach((link, index) => {
              if (typeof link === 'string' && link) {
                const name = names[index] || extractSymbolNameFromUrl(link);
                
                symbolData.push({
                  name: name,
                  imageUrl: link,
                  value: name.toLowerCase()
                });
              }
            });
          }
        } catch (parseError) {
          console.error('Ошибка парсинга JSON:', parseError);
        }
      }
    });

    // Убираем дубликаты по значению
    const uniqueSymbols = symbolData.filter((symbol, index, self) =>
      index === self.findIndex(s => s.value === symbol.value)
    );

    uniqueSymbols.sort((a, b) => a.name.localeCompare(b.name));
    symbolOptions.value = uniqueSymbols;
    
    console.log(`Загружено ${uniqueSymbols.length} символов:`, uniqueSymbols);
    
  } catch (error) {
    console.error('Ошибка загрузки символов:', error);
  } finally {
    symbolsLoading.value = false;
  }
};


// Вспомогательная функция для извлечения названия из URL
const extractSymbolNameFromUrl = (url) => {
  try {
    // Извлекаем имя файла из URL
    const filename = url.split('/').pop();
    const nameWithoutExt = filename.split('.')[0];
    
    // Преобразуем в читаемое название
    return nameWithoutExt
      .split(/[-_]/)
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ');
  } catch (error) {
    console.error('Ошибка извлечения названия из URL:', url, error);
    return 'Unknown Symbol';
  }
};

// Вызываем функцию загрузки при монтировании компонента или когда нужно
onMounted(() => {
  loadSymbolOptions();
});
const loadSymbolOptionsAlternative = async () => {
  try {
    const { data, error } = await supabase
      .from('patterns')
      .select('links, names')
      .limit(100);

    if (error) throw error;

    const symbolData = [];
    const uniqueSymbols = new Set();

    data.forEach(item => {
      // Пробуем разные форматы данных
      const processData = (links, names) => {
        if (Array.isArray(links) && Array.isArray(names)) {
          links.forEach((link, index) => {
            const name = names[index];
            if (link && name && !uniqueSymbols.has(name)) {
              uniqueSymbols.add(name);
              symbolData.push({
                name: name,
                imageUrl: link,
                value: name.toLowerCase()
              });
            }
          });
        }
      };

      // Пробуем разные форматы
      try {
        // Формат 1: JSON строки
        const linksJson = typeof item.links === 'string' ? JSON.parse(item.links) : item.links;
        const namesJson = typeof item.names === 'string' ? JSON.parse(item.names) : item.names;
        processData(linksJson, namesJson);
      } catch (e) {
        // Формат 2: Прямые массивы
        processData(item.links, item.names);
      }
    });

    symbolOptions.value = symbolData;
    
  } catch (error) {
    console.error('Ошибка загрузки символов:', error);
  } finally {
    symbolsLoading.value = false;
  }
};


// Функция для фильтрации символов по поисковому запросу

const testMultiWordSymbols = async () => {
  try {
    console.log('=== ТЕСТИРОВАНИЕ МНОГОСЛОВНЫХ СИМВОЛОВ ===');
    
    // Тестовые данные с многословными символами
    const testCases = [
      { nft_object: '{"symbol": "Red Apple 0.5%"}', expected: "Red Apple" },
      { nft_object: '{"symbol": "Blue Moon 1.2%"}', expected: "Blue Moon" },
      { nft_object: '{"symbol": "Golden Star 0.8%"}', expected: "Golden Star" },
      { nft_object: '{"symbol": "Silver Coin"}', expected: "Silver Coin" },
      { nft_object: '{"symbol": "Tree"}', expected: "Tree" }
    ];
    
    testCases.forEach((testCase, index) => {
      const mockItem = { id: `test-${index}`, nft_object: testCase.nft_object };
      const extracted = extractSymbolFromNft(mockItem);
      const normalized = normalizeSymbolName(extracted || '');
      
      console.log('---');
      console.log('Тест кейс:', testCase.nft_object);
      console.log('Ожидаемый результат:', testCase.expected);
      console.log('Извлеченный результат:', extracted);
      console.log('Нормализованный результат:', normalized);
      console.log('Совпадение:', normalized === normalizeSymbolName(testCase.expected));
    });
    
    console.log('=== ТЕСТ МНОГОСЛОВНЫХ СИМВОЛОВ ЗАВЕРШЕН ===');
    
  } catch (error) {
    console.error('Ошибка тестирования:', error);
  }
};

// Вызовите для тестирования
// testMultiWordSymbols();
const extractSymbolFromNftAdvanced = (item) => {
  try {
    let rawSymbol = null;
    
    // Поиск символа в различных источниках
    if (item.nft_metadata?.symbol) {
      rawSymbol = item.nft_metadata.symbol;
    } else if (item.symbol) {
      rawSymbol = item.symbol;
    } else if (item.nft_object) {
      try {
        const nftObj = typeof item.nft_object === 'string' 
          ? JSON.parse(item.nft_object) 
          : item.nft_object;
        rawSymbol = nftObj.symbol;
      } catch (e) {
        console.log('Ошибка парсинга nft_object:', e);
      }
    } else if (item.html_content) {
      const patterns = [
        /symbol["']?:\s*["']([^"']+)["']/i,
        /symbol["']?:\s*[']([^']+)[']/i
      ];
      
      for (const pattern of patterns) {
        const match = item.html_content.match(pattern);
        if (match && match[1]) {
          rawSymbol = match[1];
          break;
        }
      }
    }
    
    if (!rawSymbol) return null;
    
    // Извлекаем название символа (убираем проценты и лишнее)
    const cleanedSymbol = rawSymbol
      .replace(/\d+\.?\d*%/, '') // удаляем проценты
      .replace(/^\s+|\s+$/g, '') // обрезаем пробелы
      .replace(/\s+/g, ' '); // заменяем множественные пробелы на один
    
    return cleanedSymbol || null;
    
  } catch (error) {
    console.error('Ошибка извлечения символа:', error);
    return null;
  }
};
const handleTransferFromFullscreen = (nftData) => {
  // Закрываем полноэкранное меню
  htmlModal.value.show = false;
  
  // Открываем модальное окно передачи
  transferModal.value = {
    show: true,
    nftType: `html_nft_${extractNftIdFromUnlisted(nftData).replace('#', '')}`,
    recipientName: '',
    amount: 1,
    confirmStep: false,
    nftData: nftData
  };
};


// Добавьте эту функцию в секцию script
const generateItemId = () => {
  const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
  const generateSegment = () => {
    let segment = '';
    for (let i = 0; i < 8; i++) {
      segment += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return segment;
  };
  
  return `${generateSegment()}-${generateSegment()}-${generateSegment()}-${generateSegment()}`;
};





const handleWithdrawFromFullscreen = async (nftData) => {
  try {
    // Закрываем полноэкранное меню
    htmlModal.value.show = false;
    
    // Логика для withdraw (вывода NFT)
    const { data: userData, error: fetchError } = await supabase
      .from('users')
      .select('nft_links')
      .eq('name', currentAccountName.value)
      .single();

    if (fetchError) throw fetchError;

    const currentLinks = userData.nft_links || [];
    
    // Находим индекс NFT для удаления
    const nftIndex = currentLinks.findIndex(link => {
      const linkUrl = typeof link === 'object' ? link.url : link;
      return linkUrl === nftData.url;
    });

    if (nftIndex === -1) {
      throw new Error('NFT не найдено в вашем профиле');
    }

    // Удаляем NFT из списка
    const updatedLinks = [...currentLinks];
    updatedLinks.splice(nftIndex, 1);

    // Обновляем базу данных
    const { error: updateError } = await supabase
      .from('users')
      .update({ nft_links: updatedLinks })
      .eq('name', currentAccountName.value);

    if (updateError) throw updateError;

    // Обновляем локальные данные
    myUnlistedNfts.value = myUnlistedNfts.value.filter(item => 
      item.url !== nftData.url
    );

    showNotification('NFT успешно выведено!', 'success');
    
  } catch (error) {
    console.error('Ошибка вывода NFT:', error);
    showNotification(`Ошибка вывода: ${error.message}`, 'error');
  }
};


// Функция getNftOptions теперь просто возвращает отфильтрованные опции
const getNftOptions = () => {
  return getFilteredNftOptions();
};

// Функция getFilterOptions остается без изменений
const getFilterOptions = (category) => {
  try {
    if (category === 'nft') {
      return getFilteredNftOptions();
    }
    
    if (category === 'model') {
      if (!selectedFilters.value.nft || selectedFilters.value.nft.length === 0) {
        return [];
      }
      return getFilteredModels();
    }
    
    if (category === 'backdrop') {
      return getFilteredBackdrops();
    }
    
    return [];
    
  } catch (error) {
    console.error('Error in getFilterOptions:', error);
    return [];
  }
};

const generateMarketStyleImageUrl = async (nftType, displayName) => {
  try {
    console.log(`🔄 Генерация URL для: ${nftType} (${displayName})`);
    
    // Получаем случайную модель для этого NFT
    const randomModel = await getRandomModelForNft(nftType);
    
    if (randomModel) {
      // Преобразуем displayName в формат пути URL
      const nftPath = displayName.replace(/\s+/g, '%20').toLowerCase();
      const imageUrl = `https://gifts.coffin.meme/${nftPath}/${randomModel}.png`;
      
      // Сохраняем в кэш для будущего использования
      nftImageUrls.value[nftType] = imageUrl;
      
      console.log(`✅ Сгенерирован URL: ${imageUrl}`);
      return imageUrl;
    } else {
      console.warn(`❌ Не удалось получить модель для ${nftType}`);
    }
  } catch (error) {
    console.error(`🔥 Ошибка генерации URL для ${nftType}:`, error);
  }
  
  // Fallback на изображение по умолчанию
  console.warn(`⚠️ Для ${nftType} используется изображение по умолчанию`);
  return default_nft_image;
};


const isOptionSelected = (category, option) => {
  if (category === 'price') {
    return selectedIdFilter.value !== null;
  }
  
  if (!selectedFilters.value[category]) {
    return false;
  }
  
  let optionToCheck = option;
  
  // Нормализуем опцию для сравнения
  if (category === 'nft') {
    optionToCheck = normalizeNftName(option);
  } else if (category === 'symbol') {
    optionToCheck = normalizeSymbolName(option);
  } else if (category === 'backdrop') {
    optionToCheck = typeof option === 'object' ? option.id : option;
  } else if (category === 'model') {
    optionToCheck = option.toLowerCase().trim();
      }
  
  const result = selectedFilters.value[category].some(selected => {
    let normalizedSelected = selected;
    
    // Нормализуем выбранное значение для сравнения
    if (category === 'nft') {
      normalizedSelected = normalizeNftName(selected);
    } else if (category === 'symbol') {
      normalizedSelected = normalizeSymbolName(selected);
    } else if (category === 'model') {
      normalizedSelected = selected.toLowerCase().trim();
      console.log(`   Сравнение моделей: "${optionToCheck}" === "${normalizedSelected}"`);
    }
    
    return normalizedSelected === optionToCheck;
  });
  
  if (category === 'model') {
  }
  return result;
};


// Обновите функцию handleOptionClick для правильной работы
const handleOptionClick = (option, category) => {
  if (category === 'nft') {
    // Используем normalizedName для фильтрации
    const normalizedName = normalizeNftName(option.name);
    toggleFilterOption('nft', normalizedName);
    selectedImageCache.value[option.originalType] = option.imageUrl;
    
    // Добавляем класс для анимации
    const optionElement = document.querySelector(`[key="${category}-${option.originalType}"]`);
    if (optionElement) {
      optionElement.classList.add('just-selected');
      setTimeout(() => {
        optionElement.classList.remove('just-selected');
      }, 300);
    }
  } else if (option.parentNft) {
    toggleFilterOption('model', option.name);
    selectedImageCache.value[option.parentNft] = option.imageUrl;
  } else {
    toggleFilterOption(category, option.name);
  }
};

const loadNftModels = async (nftName) => {
  try {
    if (!nftName) {
      console.warn('❌ NFT name is empty');
      return [];
    }
    
    // Проверяем кэш
    if (nftModelsCache.value[nftName]) {
      return nftModelsCache.value[nftName];
    }

    // Нормализуем имя для базы данных
    let cleanNftName = nftName.toLowerCase();
    
    // Убираем префиксы
    if (cleanNftName.startsWith('html_nft_')) {
      cleanNftName = cleanNftName.replace('html_nft_', '');
    }
    if (cleanNftName.startsWith('htmlnft')) {
      cleanNftName = cleanNftName.replace('htmlnft', '');
    }

    // Получаем отображаемое имя для колонки в базе
    const dbColumnName = groupDisplayNames[cleanNftName] || 
                        cleanNftName.replace(/([a-z])([A-Z])/g, '$1 $2')
                                   .replace(/^./, str => str.toUpperCase())
                                   .trim();

    if (!dbColumnName) {
      console.warn(`❌ No database column name for: ${cleanNftName}`);
      return [];
    }

    // Экранируем имя колонки для SQL
    const quotedColumnName = `"${dbColumnName}"`;
    
    console.log(`🔍 Loading models for: ${nftName} -> ${dbColumnName}`);

    const { data, error } = await supabase
      .from('nft')
      .select(quotedColumnName)
      .not(quotedColumnName, 'is', null)
      .limit(1);

    if (error) {
      console.error(`❌ Database error for ${nftName}:`, error);
      return [];
    }

    if (!data || data.length === 0) {
      console.warn(`❌ No data found for ${nftName}`);
      return [];
    }

    const modelsArray = data[0][dbColumnName];
    
    if (!Array.isArray(modelsArray)) {
      console.warn(`❌ Models data is not array for ${nftName}:`, modelsArray);
      return [];
    }

    // Сохраняем в кэш
    nftModelsCache.value[nftName] = modelsArray;
    console.log(`✅ Loaded ${modelsArray.length} models for ${nftName}`);
    
    return modelsArray;

  } catch (error) {
    console.error(`❌ Error loading models for ${nftName}:`, error);
    return [];
  }
};






// Новая функция для удаления моделей конкретного NFT
const removeModelsForNft = (nftType) => {
  if (!selectedFilters.value.model || selectedFilters.value.model.length === 0) {
    return;
  }
  
  // Получаем все модели для этого NFT
  const modelsToRemove = [];
  if (nftModelsCache.value[nftType]) {
    nftModelsCache.value[nftType].forEach(modelString => {
      const modelName = modelString.split(' — ')[0].trim();
      modelsToRemove.push(modelName);
    });
  }
  
  // Удаляем эти модели из выбранных фильтров
  if (modelsToRemove.length > 0) {
    selectedFilters.value.model = selectedFilters.value.model.filter(
      model => !modelsToRemove.includes(model)
    );
    console.log(`Удалены модели для NFT ${nftType}:`, modelsToRemove);
  }
};

const reloadModels = async () => {
  modelsLoading.value = true;
  nftModelsCache.value = {}; // Очищаем кэш
  
  try {
    const loadPromises = selectedFilters.value.nft.map(async (nftType) => {
      console.log(`Перезагружаем модели для ${nftType}`);
      return await loadNftModels(nftType);
    });
    
    await Promise.all(loadPromises);
    console.log('Все модели перезагружены');
  } catch (error) {
    console.error('Ошибка перезагрузки моделей:', error);
  } finally {
    modelsLoading.value = false;
  }
};

const extractSymbolFromNft = (item) => {
  try {
    
    let rawSymbol = null;
    
    // Для activity items используем прямое поле symbol
    if (item.symbol) {
      rawSymbol = item.symbol;
    }
    // Для market items используем существующую логику
    else if (item.nft_metadata?.symbol) {
      rawSymbol = item.nft_metadata.symbol;
      console.log('📋 Символ из nft_metadata:', rawSymbol);
    } else if (item.symbol) {
      rawSymbol = item.symbol;
      console.log('📋 Символ из поля symbol:', rawSymbol);
    } else if (item.nft_object) {
      try {
        const nftObj = typeof item.nft_object === 'string' 
          ? JSON.parse(item.nft_object) 
          : item.nft_object;
        
        if (nftObj.symbol) {
          rawSymbol = nftObj.symbol;
        }
      } catch (e) {
        console.log('❌ Ошибка парсинга nft_object:', e);
      }
    } else if (item.html_content) {
      const patterns = [
        /symbol["']?:\s*["']([^"']+)["']/i,
        /symbol["']?:\s*[']([^']+)[']/i,
        /Символ[:\s]+([^\n\r<]+)/i
      ];
      
      for (const pattern of patterns) {
        const match = item.html_content.match(pattern);
        if (match && match[1]) {
          rawSymbol = match[1];
          console.log('📋 Символ из HTML:', rawSymbol);
          break;
        }
      }
    }
    
    if (!rawSymbol) {
      console.log('❌ Символ не найден');
      return null;
    }
    
    // Извлекаем название символа (убираем проценты и лишнее)
    const cleanedSymbol = rawSymbol
      .replace(/\d+\.?\d*%/, '') // удаляем проценты
      .replace(/^\s+|\s+$/g, '') // обрезаем пробелы
      .replace(/\s+/g, ' '); // заменяем множественные пробелы на один
    
    return cleanedSymbol;
    
  } catch (error) {
    console.error('❌ Ошибка извлечения символа:', error);
    return null;
  }
};
// Функция для извлечения символов из activity_history
const extractSymbolsFromActivityHistory = async () => {
  try {
    console.log('🔍 Извлечение символов из activity_history...');
    
    const { data, error } = await supabase
      .from('activity_history')
      .select('nft_object')
      .not('nft_object', 'is', null);

    if (error) {
      console.error('❌ Ошибка загрузки activity_history:', error);
      return [];
    }

    console.log(`📊 Загружено ${data?.length || 0} записей из activity_history`);

    const symbols = new Set();
    const symbolData = [];

    data.forEach(item => {
      try {
        const nftObject = typeof item.nft_object === 'string' 
          ? JSON.parse(item.nft_object) 
          : item.nft_object;

        if (nftObject && nftObject.symbol) {
          const symbol = nftObject.symbol;
          
          // Добавляем в Set для уникальности
          if (!symbols.has(symbol)) {
            symbols.add(symbol);
            
            // Извлекаем название и процент
            const symbolName = symbol.replace(/\d+\.?\d*%/, '').trim();
            const percentageMatch = symbol.match(/(\d+\.?\d*)%/);
            const percentage = percentageMatch ? parseFloat(percentageMatch[1]) : 0;
            
            symbolData.push({
              name: symbolName,
              fullName: symbol,
              percentage: percentage,
              rarityText: percentage > 0 ? `${percentage}%` : 'N/A',
              rarityClass: getRarityClass(percentage)
            });
          }
        }
      } catch (parseError) {
        console.error('❌ Ошибка парсинга nft_object:', parseError);
      }
    });

    // Сортируем по названию
    symbolData.sort((a, b) => a.name.localeCompare(b.name));
    
    console.log(`✅ Извлечено ${symbolData.length} уникальных символов из activity_history`);
    console.log('📋 Символы:', symbolData);
    
    return symbolData;

  } catch (error) {
    console.error('❌ Общая ошибка извлечения символов:', error);
    return [];
  }
};



// Функция для получения символов с фильтрацией по поисковому запросу
const getFilteredSymbolsFromActivityHistory = (searchQuery = '') => {
  return extractSymbolsFromActivityHistory().then(symbols => {
    if (!searchQuery) return symbols;
    
    const query = searchQuery.toLowerCase();
    return symbols.filter(symbol => 
      symbol.name.toLowerCase().includes(query) ||
      symbol.fullName.toLowerCase().includes(query)
    );
  });
};

// Альтернативная версия - загрузка с пагинацией
const extractSymbolsFromActivityHistoryPaginated = async (limit = 1000) => {
  try {
    let allSymbols = new Set();
    let offset = 0;
    let hasMore = true;

    while (hasMore) {
      const { data, error } = await supabase
        .from('activity_history')
        .select('nft_object')
        .not('nft_object', 'is', null)
        .range(offset, offset + limit - 1);

      if (error) throw error;

      if (!data || data.length === 0) {
        hasMore = false;
        break;
      }

      data.forEach(item => {
        try {
          const nftObject = typeof item.nft_object === 'string' 
            ? JSON.parse(item.nft_object) 
            : item.nft_object;

          if (nftObject && nftObject.symbol) {
            allSymbols.add(nftObject.symbol);
          }
        } catch (parseError) {
          console.error('Ошибка парсинга nft_object:', parseError);
        }
      });

      offset += limit;
      
      // Прерываем если получили меньше данных чем лимит
      if (data.length < limit) {
        hasMore = false;
      }
    }

    // Преобразуем Set в массив объектов
    const symbolData = Array.from(allSymbols).map(symbol => {
      const symbolName = symbol.replace(/\d+\.?\d*%/, '').trim();
      const percentageMatch = symbol.match(/(\d+\.?\d*)%/);
      const percentage = percentageMatch ? parseFloat(percentageMatch[1]) : 0;
      
      return {
        name: symbolName,
        fullName: symbol,
        percentage: percentage,
        rarityText: percentage > 0 ? `${percentage}%` : 'N/A',
        rarityClass: getRarityClass(percentage)
      };
    });

    symbolData.sort((a, b) => a.name.localeCompare(b.name));
    
    console.log(`✅ Извлечено ${symbolData.length} уникальных символов (пагинация)`);
    return symbolData;

  } catch (error) {
    console.error('❌ Ошибка пагинированного извлечения:', error);
    return [];
  }
};

// Использование:
// 1. Получить все символы
// extractSymbolsFromActivityHistory().then(symbols => {
//   console.log('Все символы:', symbols);
// });

// 2. Получить с фильтрацией
// getFilteredSymbolsFromActivityHistory('strawberry').then(filtered => {
//   console.log('Отфильтрованные символы:', filtered);
// });

// 3. Для больших объемов данных
// extractSymbolsFromActivityHistoryPaginated(500).then(symbols => {
//   console.log('Символы (пагинация):', symbols);
// });
const myNftsViewMode = ref('unlisted'); // 'listed' или 'unlisted'
    const myUnlistedNfts = ref([]);
    
    // Функция для загрузки unlisted NFT из nft_links
const loadUnlistedNfts = async () => {
  try {
    if (!currentAccountName.value) return;
    
    const { data, error } = await supabase
      .from('users')
      .select('nft_links')
      .eq('name', currentAccountName.value)
      .single();
      
    if (error) throw error;
    
    const nftLinks = data?.nft_links || [];
    
    // УДАЛЯЕМ ДУБЛИКАТЫ NFT по URL или ID
    const uniqueNfts = [];
    const seenUrls = new Set();
    
    nftLinks.forEach(nft => {
      const nftUrl = typeof nft === 'object' ? nft.url : nft;
      
      if (!seenUrls.has(nftUrl)) {
        seenUrls.add(nftUrl);
        
        // Если nft - объект, используем его, иначе создаем базовый объект
        const nftData = typeof nft === 'object' ? nft : { url: nft };
        uniqueNfts.push(nftData);
      } else {
        console.warn('🚫 Найден дубликат NFT:', nftUrl);
      }
    });
    
    myUnlistedNfts.value = uniqueNfts;
    
    console.log(`✅ Загружено ${uniqueNfts.length} уникальных NFT (было ${nftLinks.length})`);
    
  } catch (error) {
    console.error('❌ Ошибка загрузки unlisted NFT:', error);
    myUnlistedNfts.value = [];
  }
};
    
    
    

    // Функция для инициации продажи unlisted NFT
    // Инициализация продажи для unlisted NFT




// Функция для очистки дубликатов в базе данных (можно вызывать при необходимости)
const cleanupDuplicates = async () => {
  try {
    console.log('🧹 Запуск очистки дубликатов...');
    
    // Очистка дубликатов в market
    const { data: marketData } = await supabase
      .from('market')
      .select('*');
    
    if (marketData) {
      const uniqueMarketItems = [];
      const seenMarketItems = new Set();
      const duplicatesToDelete = [];
      
      marketData.forEach(item => {
        const itemKey = item.item_id || `${item.nft_type}_${item.seller}_${item.price_per_unit}`;
        
        if (!seenMarketItems.has(itemKey)) {
          seenMarketItems.add(itemKey);
          uniqueMarketItems.push(item);
        } else {
          duplicatesToDelete.push(item.id);
        }
      });
      
      // Удаляем дубликаты
      if (duplicatesToDelete.length > 0) {
        const { error } = await supabase
          .from('market')
          .delete()
          .in('id', duplicatesToDelete);
          
        if (error) throw error;
        console.log(`🗑️ Удалено ${duplicatesToDelete.length} дубликатов объявлений`);
      }
    }
    
    // Очистка дубликатов в пользовательских NFT
    const { data: usersData } = await supabase
      .from('users')
      .select('name, nft_links');
    
    if (usersData) {
      for (const user of usersData) {
        if (user.nft_links && user.nft_links.length > 0) {
          const uniqueNfts = [];
          const seenNftUrls = new Set();
          
          user.nft_links.forEach(nft => {
            const nftUrl = typeof nft === 'object' ? nft.url : nft;
            
            if (!seenNftUrls.has(nftUrl)) {
              seenNftUrls.add(nftUrl);
              uniqueNfts.push(nft);
            }
          });
          
          // Обновляем если нашли дубликаты
          if (uniqueNfts.length !== user.nft_links.length) {
            const { error } = await supabase
              .from('users')
              .update({ nft_links: uniqueNfts })
              .eq('name', user.name);
              
            if (error) throw error;
            console.log(`🔄 Очищены дубликаты NFT для пользователя ${user.name}`);
          }
        }
      }
    }
    
    console.log('✅ Очистка дубликатов завершена');
    showNotification('Дубликаты очищены', 'success');
    
  } catch (error) {
    console.error('❌ Ошибка очистки дубликатов:', error);
    showNotification('Ошибка очистки дубликатов', 'error');
  }
};





// .------------------------------------------------------------------------------
// Функция для извлечения модели из unlisted NFT
const extractModelFromUnlistedNft = (nftData) => {
  try {
    if (nftData.model) return nftData.model;
    
    // Парсим URL для извлечения информации
    const urlMatch = nftData.url?.match(/\/nft\/([^-]+)/);
    if (urlMatch && urlMatch[1]) {
      return urlMatch[1].replace(/([A-Z])/g, ' $1').trim();
    }
    
    return null;
  } catch (error) {
    console.error('Error extracting model from unlisted NFT:', error);
    return null;
  }
};

// Функция для извлечения символа из unlisted NFT
const extractSymbolFromUnlistedNft = (nftData) => {
  try {
    if (nftData.symbol) return nftData.symbol;
    return null;
  } catch (error) {
    console.error('Error extracting symbol from unlisted NFT:', error);
    return null;
  }
};

// Функция для извлечения backdrop из unlisted NFT
const extractBackdropFromUnlistedNft = (nftData) => {
  try {
    if (nftData.backdrop) return nftData.backdrop;
    return null;
  } catch (error) {
    console.error('Error extracting backdrop from unlisted NFT:', error);
    return null;
  }
};

// Функция для получения всех моделей с сортировкой
const getAllModelDataSortedByRarity = () => {
  try {
    if (modelsLoading.value) {
      return [];
    }
    
    const allModelData = [];
    const searchQuery = modelSearchQuery.value.toLowerCase().trim();
    
    selectedFilters.value.nft.forEach(nftType => {
      if (nftModelsCache.value[nftType]) {
        nftModelsCache.value[nftType].forEach(modelString => {
          const parts = modelString.split(' — ');
          
          if (parts.length === 2) {
            const name = parts[0].trim();
            const rarityText = parts[1].trim();
            const rarity = parseFloat(rarityText.replace('%', ''));
            
            const matchesSearch = searchQuery === '' || 
                                name.toLowerCase().includes(searchQuery) ||
                                rarityText.toLowerCase().includes(searchQuery);
            
            if (name && !isNaN(rarity) && matchesSearch) {
              const imageUrl = getModelImageUrl(nftType, name);
              
              allModelData.push({
                name,
                rarity,
                rarityText,
                parentNft: nftType,
                imageUrl: imageUrl,
                isSelected: isOptionSelected('model', name),
                displayName: getNftDisplayNameForGroup(nftType),
                floorPrice: getFloorPrice('model', name)
              });
            }
          }
        });
      }
    });
    
    allModelData.sort((a, b) => {
      if (a.isSelected && !b.isSelected) return -1;
      if (!a.isSelected && b.isSelected) return 1;
      return a.rarity - b.rarity;
    });
    
    return allModelData;
    
  } catch (error) {
    return [];
  }
}; 

const getSelectedModelOptions = () => {
  const allOptions = getAllModelDataSortedByRarity();
  return allOptions.filter(option => 
    isOptionSelected('model', option.name)
  );
};

const getUnselectedModelOptions = () => {
  const allOptions = getAllModelDataSortedByRarity();
  return allOptions.filter(option => 
    !isOptionSelected('model', option.name)
  );
};
const handleTransfer = (nftData) => {
  // Если мы в fullscreen view, закрываем его
  if (htmlModal.value && htmlModal.value.show) {
    htmlModal.value.show = false;
  }
  
  transferModal.value = {
    show: true,
    nftType: `html_nft_${extractNftIdFromUnlisted(nftData).replace('#', '')}`,
    recipientName: '',
    amount: 1,
    confirmStep: false,
    nftData: nftData
  };
};
const handleWithdraw = async (nftData) => {
  try {
    const { data: userData, error: fetchError } = await supabase
      .from('users')
      .select('nft_links')
      .eq('name', currentAccountName.value)
      .single();

    if (fetchError) throw fetchError;

    const currentLinks = userData.nft_links || [];
    const nftIndex = currentLinks.findIndex(link => {
      const linkUrl = typeof link === 'object' ? link.url : link;
      return linkUrl === nftData.url;
    });

    if (nftIndex === -1) {
      throw new Error('NFT не найдено в вашем профиле');
    }

    const updatedLinks = [...currentLinks];
    updatedLinks.splice(nftIndex, 1);

    const { error: updateError } = await supabase
      .from('users')
      .update({ nft_links: updatedLinks })
      .eq('name', currentAccountName.value);

    if (updateError) throw updateError;

    myUnlistedNfts.value = myUnlistedNfts.value.filter(item => 
      item.url !== nftData.url
    );

    showNotification('NFT успешно выведено!', 'success');
    
  } catch (error) {
    console.error('Ошибка вывода NFT:', error);
    showNotification(`Ошибка вывода: ${error.message}`, 'error');
  }
};



const extractModelFromNft = (item) => {
  try {
    let model = null;
    
    // Для activity items используем прямое поле model
    if (item.model) {
      model = item.model;
    }
    // Для market items используем существующую логику
    else if (item.nft_metadata?.model) {
      model = item.nft_metadata.model;
    } else if (item.model) {
      model = item.model;
    } else if (item.nft_object) {
      try {
        const nftObj = typeof item.nft_object === 'string' 
          ? JSON.parse(item.nft_object) 
          : item.nft_object;
        model = nftObj.model;
      } catch (e) {
        console.log('Ошибка парсинга nft_object для модели:', e);
      }
    } else if (item.html_content) {
      const patterns = [
        /model["']?:\s*["']([^"']+)["']/i,
        /model["']?:\s*[']([^']+)[']/i,
        /Модель[:\s]+([^\n\r<]+)/i
      ];
      
      for (const pattern of patterns) {
        const match = item.html_content.match(pattern);
        if (match && match[1]) {
          model = match[1];
          break;
        }
      }
    }
    
    if (model) {
      // Убираем проценты но сохраняем полное название
      const cleanModel = model.replace(/\d+\.?\d*%/, '').trim();
      return cleanModel;
    }
    
    return null;
    
  } catch (error) {
    console.error('Ошибка извлечения модели:', error);
    return null;
  }
};
const floorPriceCache = ref({});

const getCachedFloorPrice = (category, optionName) => {
  const cacheKey = `${category}_${normalizeModelName(optionName)}`;
  
  // Если есть в кэше и кэш не старше 5 минут, используем его
  if (floorPriceCache.value[cacheKey] && 
      Date.now() - floorPriceCache.value[cacheKey].timestamp < 5 * 60 * 1000) {
    return floorPriceCache.value[cacheKey].price;
  }
  
  // Иначе вычисляем заново и сохраняем в кэш
  const price = getFloorPrice(category, optionName);
  floorPriceCache.value[cacheKey] = {
    price: price,
    timestamp: Date.now()
  };
  
  return price;
};





const toggleModelNftExpansion = (nftType) => {
  expandedModelNfts.value = {
    ...expandedModelNfts.value,
    [nftType]: !expandedModelNfts.value[nftType]
  };

  if (expandedModelNfts.value[nftType] && !nftModelsCache.value[nftType]) {
    loadNftModels(nftType).then(models => {
      nftModelsCache.value[nftType] = models;
    });
  }
};






// В функции getFilteredModels убедимся, что она не влияет на доступность NFT
const getFilteredModels = () => {
  const query = modelSearchQuery.value ? modelSearchQuery.value.toLowerCase() : '';
  
  // Получаем модели только для выбранных NFT (если есть выбор)
  const availableModels = availableModelOptions.value;
  
  const allModels = getAllModelDataSortedByRarity();
  
  return allModels.filter(model => 
    availableModels.includes(model.name.toLowerCase()) &&
    (model.name.toLowerCase().includes(query) ||
     model.rarityText.toLowerCase().includes(query))
  );
};

// Функция для сброса зависимых фильтров при изменении основного
const resetDependentFilters = (changedCategory) => {
  const dependencyOrder = ['nft', 'model', 'symbol', 'backdrop'];
  const changedIndex = dependencyOrder.indexOf(changedCategory);
  
  if (changedIndex === -1) return;
  
  // Сбрасываем только фильтры, которые логически зависят от измененного
  // Например, при изменении NFT сбрасываем model, symbol, backdrop
  // Но при изменении symbol или backdrop ничего не сбрасываем
  for (let i = changedIndex + 1; i < dependencyOrder.length; i++) {
    const categoryToReset = dependencyOrder[i];
    selectedFilters.value[categoryToReset] = [];
  }
  
  console.log(`Сброшены фильтры после ${changedCategory}`);
};

// Обновляем функцию toggleFilterOption для сброса зависимых фильтров
// Функция для очистки зависимых фильтров при изменении NFT
// Функция для очистки зависимых фильтров при изменении основного
const clearDependentFilters = (changedCategory) => {
  console.log(`🔄 Очистка зависимых фильтров после изменения ${changedCategory}`);
  
  const dependencyOrder = ['nft', 'model', 'symbol', 'backdrop'];
  const changedIndex = dependencyOrder.indexOf(changedCategory);
  
  if (changedIndex === -1) return;
  
  // Сбрасываем только фильтры, которые логически зависят от измененного
  for (let i = changedIndex + 1; i < dependencyOrder.length; i++) {
    const categoryToReset = dependencyOrder[i];
    selectedFilters.value[categoryToReset] = [];
    console.log(`✅ Очищен фильтр: ${categoryToReset}`);
  }
  
  // Форсируем обновление реактивности
  selectedFilters.value = { ...selectedFilters.value };
};

// Обновим toggleFilterOption
const toggleFilterOption = async (category, option, event) => {
  if (event) {
    event.stopPropagation();
  }
  
  if (!selectedFilters.value[category]) {
    selectedFilters.value[category] = [];
  }
  
  let optionToUse = option;
  
  // Нормализация для разных категорий
  if (category === 'nft') {
    optionToUse = normalizeNftName(option);
  } else if (category === 'symbol') {
    optionToUse = normalizeSymbolName(option);
  } else if (category === 'model') {
    optionToUse = option.toLowerCase().trim();
  }
  
  const currentFilters = [...selectedFilters.value[category]];
  const index = currentFilters.indexOf(optionToUse);
  
  if (index === -1) {
    // Добавляем опцию
    currentFilters.push(optionToUse);
  } else {
    // Удаляем опцию
    currentFilters.splice(index, 1);
  }
  
  selectedFilters.value[category] = currentFilters;
  
  // Очищаем зависимые фильтры при изменении NFT или model
  if (category === 'nft' || category === 'model') {
    clearDependentFilters(category);
  }
  
  // Принудительное обновление реактивности
  selectedFilters.value = { ...selectedFilters.value };
  
  // Принудительное обновление computed свойств
  await nextTick();
  
  console.log(`✅ Toggle ${category}: ${option}`, selectedFilters.value[category]);
};









const replayHtmlAnimation = (event) => {
  event.stopPropagation();
  
  if (htmlIframe.value) {
    try {
      // Пытаемся вызвать функцию replayAnimation внутри iframe
      const iframeWindow = htmlIframe.value.contentWindow;
      if (iframeWindow && typeof iframeWindow.replayAnimation === 'function') {
        iframeWindow.replayAnimation();
        console.log('✅ Анимация перезапущена через функцию iframe');
      } else {
        // Fallback: отправляем сообщение
        iframeWindow.postMessage({ 
          type: 'replayAnimation',
          timestamp: Date.now()
        }, '*');
        console.log('✅ Сообщение для перезапуска отправлено');
      }
    } catch (error) {
      console.log('❌ Ошибка при перезапуске анимации:', error);
      // Ultimate fallback: перезагружаем iframe
      const currentContent = htmlIframe.value.srcdoc;
      htmlIframe.value.srcdoc = '';
      setTimeout(() => {
        htmlIframe.value.srcdoc = currentContent;
      }, 50);
    }
  }
};

// Вспомогательная функция для извлечения ID из HTML контента
const extractNftIdFromHtml = (htmlContent) => {
  try {
    const match = htmlContent.match(/nftId['"]?\s*:\s*['"]([^'"]+)['"]/);
    return match ? match[1] : null;
  } catch (error) {
    console.error('Ошибка извлечения NFT ID из HTML:', error);
    return null;
  }
};


const getAllModelNames = () => {
  try {
    const allModelNames = [];
    
    // Проходим по всем выбранным NFT и собираем названия моделей
    selectedFilters.value.nft.forEach(nftType => {
      if (nftModelsCache.value[nftType]) {
        nftModelsCache.value[nftType].forEach(modelString => {
          // Извлекаем только название модели (до символа "—")
          const modelName = modelString.split(' — ')[0].trim();
          if (modelName && !allModelNames.includes(modelName)) {
            allModelNames.push(modelName);
          }
        });
      }
    });
    
    // Сортируем по алфавиту
    allModelNames.sort((a, b) => a.localeCompare(b));
    
    console.log(`Всего уникальных названий моделей: ${allModelNames.length}`);
    return allModelNames;
    
  } catch (error) {
    console.error('Ошибка получения названий моделей:', error);
    return [];
  }
};

const extractNftIdFromUnlisted = (nftData) => {
  try {
    if (!nftData.url) return 'Unknown';
    
    // Извлекаем ID из URL (формат: https://t.me/nft/bdaycandle-224527)
    const match = nftData.url.match(/-(\d+)(?:\?|$)/);
    return match ? match[1] : 'Unknown';
  } catch (error) {
    console.error('Error extracting NFT ID from unlisted:', error);
    return 'Error';
  }
};
// Состояние модального окна продажи
const sellModal = ref({
  show: false,
  nftType: '',
  nftData: null,
  price: '',
  amount: 1,
  confirmStep: false,
  totalPrice: 0,
  commission: 0,
  finalAmount: 0,
  isHtmlNft: false,
  loading: false // ← ДОБАВЬТЕ ЭТУ СТРОКУ
});


// Показать подтверждение продажи
const showSellConfirmation = () => {
  if (!sellModal.value.price || (!sellModal.value.isHtmlNft && !sellModal.value.amount)) {
    showNotification('Пожалуйста, укажите корректные данные', 'error');
    return;
  }
  
  sellModal.value.confirmStep = true;
};



// АГРЕССИВНАЯ ФУНКЦИЯ ОЧИСТКИ ДУБЛИКАТОВ МАРКЕТА
const cleanupMarketDuplicates = async () => {
  try {
    console.log('🧹 Агрессивная очистка дубликатов маркета...');
    
    const { data: allItems, error } = await supabase
      .from('market')
      .select('*')
      .order('created_at', 'asc');

    if (error) throw error;
    if (!allItems || allItems.length === 0) return;

    const itemsToKeep = new Map();
    const duplicatesToDelete = [];

    allItems.forEach(item => {
      // Создаем комплексный ключ для каждого объявления
      let key = `${item.seller}_${item.nft_type}`;
      
      // Для HTML NFT добавляем URL в ключ
      if (item.nft_object) {
        try {
          const nftObj = typeof item.nft_object === 'string' ? JSON.parse(item.nft_object) : item.nft_object;
          if (nftObj.url) {
            key += `_${nftObj.url}`;
          }
        } catch (e) {
          console.error('Error parsing nft_object:', e);
        }
      } else {
        // Для обычных NFT используем цену и количество
        key += `_${item.price_per_unit}_${item.amount || 1}`;
      }

      // Если ключ уже существует, помечаем как дубликат
      if (itemsToKeep.has(key)) {
        duplicatesToDelete.push(item.id);
        console.log(`🚫 Найден дубликат маркета: ${key} (ID: ${item.id})`);
      } else {
        itemsToKeep.set(key, item);
      }
    });

    // УДАЛЯЕМ ВСЕ ДУБЛИКАТЫ
    if (duplicatesToDelete.length > 0) {
      console.log(`🗑️ Удаляем ${duplicatesToDelete.length} дубликатов маркета...`);
      
      const { error: deleteError } = await supabase
        .from('market')
        .delete()
        .in('id', duplicatesToDelete);
        
      if (deleteError) throw deleteError;
      
      console.log(`✅ Удалено ${duplicatesToDelete.length} дубликатов маркета`);
    } else {
      console.log('✅ Дубликаты маркета не найдены');
    }
    
  } catch (error) {
    console.error('❌ Ошибка очистки дубликатов маркета:', error);
  }
};

// АГРЕССИВНАЯ ФУНКЦИЯ ОЧИСТКИ ДУБЛИКАТОВ UNLISTED
const cleanupUnlistedDuplicates = async () => {
  try {
    console.log('🧹 Агрессивная очистка дубликатов unlisted...');
    
    const { data: userData, error } = await supabase
      .from('users')
      .select('name, nft_links')
      .eq('name', currentAccountName.value)
      .single();

    if (error) throw error;

    const nftLinks = userData?.nft_links || [];
    if (nftLinks.length === 0) return;

    const uniqueNfts = [];
    const seenUrls = new Set();

    nftLinks.forEach(nft => {
      const nftUrl = typeof nft === 'object' ? nft.url : nft;
      
      if (!seenUrls.has(nftUrl)) {
        seenUrls.add(nftUrl);
        uniqueNfts.push(nft);
      } else {
        console.log(`🚫 Найден дубликат unlisted: ${nftUrl}`);
      }
    });

    // Если есть дубликаты, обновляем базу
    if (uniqueNfts.length !== nftLinks.length) {
      console.log(`🗑️ Удаляем ${nftLinks.length - uniqueNfts.length} дубликатов unlisted...`);
      
      const { error: updateError } = await supabase
        .from('users')
        .update({ nft_links: uniqueNfts })
        .eq('name', currentAccountName.value);

      if (updateError) throw updateError;
      
      console.log(`✅ Удалено ${nftLinks.length - uniqueNfts.length} дубликатов unlisted`);
    } else {
      console.log('✅ Дубликаты unlisted не найдены');
    }
    
  } catch (error) {
    console.error('❌ Ошибка очистки дубликатов unlisted:', error);
  }
};

// Функция для вывода всех символов с маркета в консоль
// Компактный вариант - только ссылки
const logAllMarketSymbols = () => {
  
  const allSymbols = new Set();
  
  marketItems.value.forEach(item => {
    const symbol = extractSymbolFromNft(item);
    if (symbol) {
      allSymbols.add(symbol);
    }
  });
  
  // Выводим только ссылки
  Array.from(allSymbols).forEach(symbol => {
    const symbolLink = `https://gifts.coffin.meme/patterns/${symbol.toLowerCase().replace(/\s+/g, '%20')}.tgs`;
  });
  
};
const renderTgsFirstFrame = async (tgsUrl, width = 512, height = 512) => {
  return new Promise(async (resolve) => {
    try {
      // Загружаем TGS данные
      const response = await fetch(tgsUrl);
      const animationData = await response.json();
      
      // Создаем временный контейнер
      const container = document.createElement('div');
      container.style.width = `${width}px`;
      container.style.height = `${height}px`;
      container.style.position = 'absolute';
      container.style.left = '-9999px';
      document.body.appendChild(container);
      
      // Загружаем анимацию
      const anim = lottie.loadAnimation({
        container: container,
        renderer: 'svg',
        loop: false,
        autoplay: false,
        animationData: animationData
      });
      
      // Ждем готовности и рендерим первый кадр
      anim.addEventListener('DOMLoaded', () => {
        // Переходим к первому кадру
        anim.goToAndStop(0, true);
        
        // Получаем SVG элемент
        const svgElement = container.querySelector('svg');
        
        // Конвертируем SVG в Data URL
        const svgString = new XMLSerializer().serializeToString(svgElement);
        const svgBlob = new Blob([svgString], { type: 'image/svg+xml' });
        const svgUrl = URL.createObjectURL(svgBlob);
        
        // Создаем изображение из SVG
        const img = new Image();
        img.onload = () => {
          // Создаем canvas для конвертации в PNG
          const canvas = document.createElement('canvas');
          canvas.width = width;
          canvas.height = height;
          const ctx = canvas.getContext('2d');
          
          // Рисуем изображение на canvas
          ctx.drawImage(img, 0, 0, width, height);
          
          // Получаем PNG Data URL
          const pngDataUrl = canvas.toDataURL('image/png');
          
          // Очищаем
          document.body.removeChild(container);
          URL.revokeObjectURL(svgUrl);
          anim.destroy();
          
          resolve(pngDataUrl);
        };
        img.src = svgUrl;
      });
      
    } catch (error) {
      console.error('Ошибка рендеринга TGS:', error);
      resolve(null);
    }
  });
};

// Использование
const logSymbolsWithPngPreview = async () => {
  const symbols = new Set(marketItems.value.map(item => extractSymbolFromNft(item)).filter(Boolean));
  
  for (const symbol of symbols) {
    const tgsUrl = `https://gifts.coffin.meme/patterns/${symbol.toLowerCase().replace(/\s+/g, '%20')}.tgs`;
    const pngPreview = await renderTgsFirstFrame(tgsUrl, 128, 128);
    
    if (pngPreview) {
      console.log(`🔗 ${symbol}: ${tgsUrl}`);
      // Выводим превью в консоль
      console.log('%c ', `font-size: 64px; background: url(${pngPreview}) no-repeat; background-size: contain;`);
    }
  }
};
// ФУНКЦИЯ ДЛЯ ПРИНУДИТЕЛЬНОЙ ОЧИСТКИ ВСЕХ ДУБЛИКАТОВ
const forceCleanupAllDuplicates = async () => {
  try {
    console.log('💥 ЗАПУСК ПРИНУДИТЕЛЬНОЙ ОЧИСТКИ ВСЕХ ДУБЛИКАТОВ...');
    
    // Очистка маркета
    await cleanupMarketDuplicates();
    
    // Очистка unlisted для всех пользователей
    const { data: allUsers, error } = await supabase
      .from('users')
      .select('name, nft_links');

    if (error) throw error;

    if (allUsers) {
      for (const user of allUsers) {
        if (user.nft_links && user.nft_links.length > 0) {
          const uniqueNfts = [];
          const seenUrls = new Set();
          
          user.nft_links.forEach(nft => {
            const nftUrl = typeof nft === 'object' ? nft.url : nft;
            if (!seenUrls.has(nftUrl)) {
              seenUrls.add(nftUrl);
              uniqueNfts.push(nft);
            }
          });
          
          if (uniqueNfts.length !== user.nft_links.length) {
            await supabase
              .from('users')
              .update({ nft_links: uniqueNfts })
              .eq('name', user.name);
              
            console.log(`✅ Очищены дубликаты для пользователя ${user.name}`);
          }
        }
      }
    }
    
    // Синхронизация состояний
    await syncNftState();
    
    // Перезагрузка данных
    await loadMarketItems();
    await loadUnlistedNfts();
    
    console.log('💥 ПРИНУДИТЕЛЬНАЯ ОЧИСТКА ЗАВЕРШЕНА');
    showNotification('Все дубликаты очищены!', 'success');
    
  } catch (error) {
    console.error('❌ Ошибка принудительной очистки:', error);
    showNotification('Ошибка очистки дубликатов', 'error');
  }
};


// Проверка, не находится ли NFT уже на маркете
const checkIfNftAlreadyListed = async (nftData) => {
  try {
    if (!nftData?.url) return false;

    const { data: marketItems, error } = await supabase
      .from('market')
      .select('*')
      .eq('seller', currentAccountName.value);

    if (error) throw error;
    if (!marketItems || marketItems.length === 0) return false;

    // Для HTML NFT сравниваем по URL
    const isListed = marketItems.some(item => {
      if (item.nft_object) {
        try {
          const itemNftObj = typeof item.nft_object === 'string' ? JSON.parse(item.nft_object) : item.nft_object;
          return itemNftObj.url === nftData.url;
        } catch (e) {
          console.error('Error parsing nft_object:', e);
        }
      }
      return false;
    });
    
    if (isListed) {
      console.warn('🚫 NFT уже на маркете:', nftData.url);
      return true;
    }

    return false;
  } catch (error) {
    console.error('❌ Ошибка проверки наличия на маркете:', error);
    return false; // В случае ошибки разрешаем продолжение
  }
};

// Проверка, что NFT действительно есть в unlisted у пользователя
const checkIfNftInUnlisted = async (nftData) => {
  try {
    if (!nftData?.url) return false;

    const { data: userData, error } = await supabase
      .from('users')
      .select('nft_links')
      .eq('name', currentAccountName.value)
      .single();

    if (error) throw error;

    const nftLinks = userData?.nft_links || [];
    
    // Ищем NFT в unlisted коллекции пользователя
    const isInCollection = nftLinks.some(nft => {
      const nftUrl = typeof nft === 'object' ? nft.url : nft;
      return nftUrl === nftData.url;
    });

    if (!isInCollection) {
      console.warn('🚫 NFT не найдено в коллекции пользователя:', nftData.url);
      return false;
    }

    console.log('✅ NFT найдено в коллекции пользователя');
    return true;
  } catch (error) {
    console.error('❌ Ошибка проверки наличия в коллекции:', error);
    return false;
  }
};
// Обновляем computed свойство для получения текущего источника данных
const getCurrentDataSource = computed(() => {
  // Для offers используем данные из nft_data
  return filteredOffers.value.map(offer => {
    let nftData = {};
    
    try {
      if (offer.nft_data) {
        nftData = typeof offer.nft_data === 'string' 
          ? JSON.parse(offer.nft_data) 
          : offer.nft_data;
      }
    } catch (parseError) {
      console.error('❌ Ошибка парсинга nft_data в offers:', parseError);
    }
    
    return {
      id: `offer-${offer.id}`,
      nft_type: `html_nft_${nftData.name?.replace(/\s+/g, '') || 'unknown'}`,
      nft_object: nftData,
      seller: offer.seller_name,
      buyer_name: offer.buyer_name,
      price_per_unit: offer.offer_price,
      currency: offer.currency,
      // Добавляем распарсенные данные для фильтрации
      nft_name: nftData.name,
      model: nftData.model,
      symbol: nftData.symbol,
      backdrop: nftData.backdrop,
      url: nftData.url,
      is_offer: true // маркер что это оффер
    };
  });
});

// Обновляем availableNftOptions для работы с offers
const availableNftOptions = computed(() => {
  const availableNfts = new Set();
  const items = getCurrentDataSource.value;
  
  console.group('🎯 AVAILABLE NFT OPTIONS FROM OFFERS');
  console.log('📊 Всего items для анализа:', items.length);
  
  // Собираем все уникальные NFT из offers
  items.forEach(item => {
    if (item.nft_name) {
      const normalizedItemName = normalizeNftName(item.nft_name);
      availableNfts.add(normalizedItemName);
      console.log(`📋 Найден NFT: "${item.nft_name}" -> "${normalizedItemName}"`);
    }
  });
  
  const result = Array.from(availableNfts);
  console.log(`✅ Доступные NFT опции: ${result.length}`, result);
  console.groupEnd();
  
  return result;
});

// Обновляем availableModelOptions для работы с offers
const availableModelOptions = computed(() => {
  const availableModels = new Set();
  const items = getCurrentDataSource.value;

  console.group('🎯 AVAILABLE MODEL OPTIONS FROM OFFERS');
  console.log('📊 Всего items для анализа:', items.length);
  
  // Фильтруем items по всем фильтрам кроме model
  const preFilteredItems = items.filter(item => {
    // NFT фильтр
    if (selectedFilters.value.nft.length > 0) {
      const itemName = item.nft_name;
      if (!itemName) return false;
      
      const normalizedItemName = normalizeNftName(itemName);
      
      const passesNftFilter = selectedFilters.value.nft.some(selectedNft => {
        const normalizedSelected = normalizeNftName(selectedNft);
        return normalizedItemName.includes(normalizedSelected);
      });
      if (!passesNftFilter) return false;
    }
    
    // Symbol фильтр
    if (selectedFilters.value.symbol.length > 0) {
      const itemSymbol = item.symbol;
      if (!itemSymbol) return false;
      
      const normalizedItemSymbol = normalizeSymbolName(itemSymbol);
      const passesSymbolFilter = selectedFilters.value.symbol.some(selectedSymbol => {
        const normalizedSelectedSymbol = normalizeSymbolName(selectedSymbol);
        return normalizedItemSymbol === normalizedSelectedSymbol;
      });
      if (!passesSymbolFilter) return false;
    }
    
    // Backdrop фильтр
    if (selectedFilters.value.backdrop.length > 0) {
      const itemBackdrop = item.backdrop;
      if (!itemBackdrop) return false;
      
      const cleanItemBackdrop = itemBackdrop.split(' ')[0].toLowerCase().trim();
      const passesBackdropFilter = selectedFilters.value.backdrop.some(selectedBackdrop => {
        const cleanSelectedBackdrop = selectedBackdrop.split(' ')[0].toLowerCase().trim();
        return cleanItemBackdrop === cleanSelectedBackdrop;
      });
      if (!passesBackdropFilter) return false;
    }
    
    return true;
  });
  
  console.log(`📊 После префильтрации: ${preFilteredItems.length} items`);
  
  // Собираем доступные модели
  preFilteredItems.forEach(item => {
    const model = item.model;
    if (model) {
      const fullModelName = model.toLowerCase().trim();
      if (fullModelName && fullModelName !== 'не указано') {
        availableModels.add(fullModelName);
        console.log(`📋 Найдена модель: "${model}" -> "${fullModelName}"`);
      }
    }
  });
  
  const result = Array.from(availableModels);
  console.log(`✅ Доступные модели: ${result.length}`, result);
  console.groupEnd();
  
  return result;
});


// Новая функция для извлечения backdrop с процентом из offers
const extractBackdropWithPercentageFromOffer = (item) => {
  try {
    const backdrop = item.backdrop;
    if (!backdrop) return { name: null, percentage: 0 };
    
    // Извлекаем процент
    const percentageMatch = backdrop.match(/(\d+\.?\d*)%/);
    const percentage = percentageMatch ? parseFloat(percentageMatch[1]) : 0;
    
    // Извлекаем название (убираем процент)
    const name = backdrop.replace(/\d+\.?\d*%/, '').trim();
    
    return { name, percentage };
  } catch (error) {
    console.error('❌ Ошибка извлечения backdrop:', error);
    return { name: null, percentage: 0 };
  }
};


// Обновляем функцию getFilteredNftOptions для генерации правильных imageUrl
const getFilteredNftOptions = async () => {
  const query = searchQuery.value ? searchQuery.value.toLowerCase() : '';
  
  console.group('🎯 GET FILTERED NFT OPTIONS FROM OFFERS');
  
  const currentDataSource = getCurrentDataSource.value;
  console.log('📊 Текущий источник данных:', currentDataSource.length, 'items');
  
  const nftTypesWithNames = new Map();
  
  // Собираем уникальные NFT из offers
  currentDataSource.forEach(item => {
    const displayName = item.nft_name;
    const nftType = item.nft_type;
    
    if (displayName && nftType) {
      nftTypesWithNames.set(nftType, displayName);
      console.log(`📋 Найден NFT: ${nftType} -> "${displayName}"`);
    }
  });
  
  // Асинхронно генерируем изображения для всех опций
  const optionsPromises = Array.from(nftTypesWithNames.entries()).map(async ([nftType, displayName]) => {
    // Генерируем URL используя реальные модели из БД
    const imageUrl = await generateNftImageUrlWithRealModel(displayName);
    const floorPrice = getFloorPriceForOffer('nft', nftType);
    
    console.log(`📸 Создана опция NFT: ${displayName} -> ${imageUrl}`);
    
    return {
      originalType: nftType,
      name: displayName,
      imageUrl: imageUrl,
      floorPrice: floorPrice
    };
  });
  
  const options = await Promise.all(optionsPromises);
  
  console.log(`📊 Всего опций: ${options.length}`);
  
  // Фильтрация по выбранным/невыбранным
  const selectedOptions = options.filter(option => 
    isOptionSelected('nft', option.originalType)
  );
  const unselectedOptions = options.filter(option => 
    !isOptionSelected('nft', option.originalType)
  );
  
  const sortedOptions = [...selectedOptions, ...unselectedOptions];
  
  if (!query) {
    console.log('✅ Без поискового запроса, возвращаем все опции');
    console.groupEnd();
    return sortedOptions;
  }
  
  const filteredOptions = sortedOptions.filter(option => 
    option.name.toLowerCase().includes(query) ||
    option.originalType.toLowerCase().includes(query)
  );
  
  console.log(`🔎 После фильтрации по запросу "${query}": ${filteredOptions.length} опций`);
  console.groupEnd();
  
  return filteredOptions;
};


// Удалите старую функцию getNftImageSync и замените её на эту:
const getNftImageForFilter = async (nftType, nftDisplayName) => {
  // Для NFT в фильтрах используем ту же логику что и в getFilteredNftOptions
  return await generateNftImageUrlWithRealModel(nftDisplayName);
};

// Новая функция для получения floor price для offers
const getFloorPriceForOffer = (category, optionName) => {
  // Для offers можно рассчитать минимальную цену среди офферов
  const relevantOffers = filteredOffers.value.filter(offer => {
    try {
      const nftData = getNftDataFromOffer(offer);
      if (!nftData) return false;
      
      if (category === 'nft') {
        const offerNftName = nftData.name;
        const normalizedOfferNft = normalizeNftName(offerNftName);
        const normalizedOption = normalizeNftName(optionName);
        return normalizedOfferNft.includes(normalizedOption);
      }
      
      if (category === 'model') {
        const offerModel = nftData.model?.replace(/\d+\.?\d*%/, '').trim().toLowerCase();
        return offerModel === optionName.toLowerCase();
      }
      
      return false;
    } catch (error) {
      return false;
    }
  });
  
  if (relevantOffers.length === 0) return null;
  
  const minPrice = Math.min(...relevantOffers.map(offer => offer.offer_price || Infinity));
  return minPrice !== Infinity ? minPrice : null;
};

// Функция для получения всех backdrop из ВСЕХ offers
const getAllBackdropsFromAllOffers = () => {
  try {
    console.log('🔍 Загрузка backdrop из ВСЕХ offers...');
    
    const allBackdrops = new Map();

    // Проходим по ВСЕМ offers
    allOffers.value.forEach(offer => {
      try {
        const nftData = offer.nft_data;
        if (nftData && nftData.backdrop) {
          const backdrop = nftData.backdrop;
          
          // Извлекаем название и процент
          const backdropName = backdrop.replace(/\d+\.?\d*%/, '').trim();
          const percentageMatch = backdrop.match(/(\d+\.?\d*)%/);
          const percentage = percentageMatch ? parseFloat(percentageMatch[1]) : 0;
          
          if (backdropName) {
            if (!allBackdrops.has(backdropName)) {
              allBackdrops.set(backdropName, {
                id: backdropName,
                name: backdropName,
                fullName: backdrop,
                percentage: percentage,
                rarityText: percentage > 0 ? `${percentage}%` : 'N/A',
                rarityClass: getRarityClass(percentage),
                svgContent: generateBackdropSvg(backdropName)
              });
            }
          }
        }
      } catch (error) {
        console.error('❌ Ошибка обработки offer backdrop:', error);
      }
    });

    const backdropData = Array.from(allBackdrops.values());
    
    // Сортируем по названию
    backdropData.sort((a, b) => a.name.localeCompare(b.name));
    
    console.log(`✅ Извлечено ${backdropData.length} уникальных backdrop из ВСЕХ offers`);
    return backdropData;

  } catch (error) {
    console.error('❌ Ошибка загрузки backdrop из offers:', error);
    return [];
  }
};

// Обновленная функция для получения backdrop с учетом выбранного статуса offer
const getAllBackdropsFromFilteredOffers = () => {
  try {
    console.log('🔍 Загрузка backdrop из offers с фильтром статуса:', selectedOfferType.value);
    
    const allBackdrops = new Map();

    // Используем filteredOffers вместо allOffers
    filteredOffers.value.forEach(offer => {
      try {
        // Проверяем статус offer
        if (selectedOfferType.value !== 'all' && offer.status !== selectedOfferType.value) {
          return; // Пропускаем offers с неподходящим статусом
        }
        
        const nftData = offer.nft_data;
        if (nftData && nftData.backdrop) {
          const backdrop = nftData.backdrop;
          
          const backdropName = backdrop.replace(/\d+\.?\d*%/, '').trim();
          const percentageMatch = backdrop.match(/(\d+\.?\d*)%/);
          const percentage = percentageMatch ? parseFloat(percentageMatch[1]) : 0;
          
          if (backdropName) {
            if (!allBackdrops.has(backdropName)) {
              allBackdrops.set(backdropName, {
                id: backdropName,
                name: backdropName,
                fullName: backdrop,
                percentage: percentage,
                rarityText: percentage > 0 ? `${percentage}%` : 'N/A',
                rarityClass: getRarityClass(percentage),
                svgContent: generateBackdropSvg(backdropName)
              });
            }
          }
        }
      } catch (error) {
        console.error('❌ Ошибка обработки offer backdrop:', error);
      }
    });

    const backdropData = Array.from(allBackdrops.values());
    backdropData.sort((a, b) => a.name.localeCompare(b.name));
    
    console.log(`✅ Извлечено ${backdropData.length} уникальных backdrop из offers со статусом: ${selectedOfferType.value}`);
    return backdropData;

  } catch (error) {
    console.error('❌ Ошибка загрузки backdrop из offers:', error);
    return [];
  }
};

// Обновленная функция для получения отфильтрованных backdrop
const getFilteredBackdrops = () => {
  const query = backdropSearchQuery.value ? backdropSearchQuery.value.toLowerCase() : '';
  
  console.log(`🔍 FILTERED BACKDROPS: query="${query}", offerType="${selectedOfferType.value}"`);
  
  // Берем backdrop из offers с учетом статуса
  const allBackdropsFromOffers = getAllBackdropsFromFilteredOffers();
  
  if (allBackdropsFromOffers.length === 0) {
    console.log('❌ Нет backdrop в offers с текущим фильтром статуса');
    return [];
  }
  
  const filtered = allBackdropsFromOffers
    .filter(backdrop => {
      const matchesSearch = query === '' || 
                           backdrop.name.toLowerCase().includes(query) ||
                           backdrop.id.toLowerCase().includes(query);
      return matchesSearch;
    })
    .map(backdrop => {
      return {
        id: backdrop.id,
        name: backdrop.name,
        svgContent: backdrop.svgContent,
        percentage: backdrop.percentage || 0,
        rarityText: backdrop.rarityText || 'N/A',
        rarityClass: backdrop.rarityClass || 'common'
      };
    })
    .sort((a, b) => a.percentage - b.percentage);

  console.log(`📊 RESULT: ${filtered.length} backdrops для статуса "${selectedOfferType.value}"`);
  return filtered;
};

// Функции для выбранных и невыбранных backdrop
const getSelectedBackdropOptions = () => {
  const allOptions = getFilteredBackdrops();
  
  const selectedOptions = allOptions.filter(backdrop => 
    isOptionSelected('backdrop', backdrop.id)
  );
  
  console.log(`🎯 SELECTED BACKDROPS: ${selectedOptions.length} out of ${allOptions.length}`);
  selectedOptions.forEach(backdrop => {
    console.log(`   ✅ ${backdrop.name}`);
  });
  
  return selectedOptions;
};

const getUnselectedBackdropOptions = () => {
  const allOptions = getFilteredBackdrops();
  
  const unselectedOptions = allOptions.filter(backdrop => 
    !isOptionSelected('backdrop', backdrop.id)
  );
  
  console.log(`📝 UNSELECTED BACKDROPS: ${unselectedOptions.length} out of ${allOptions.length}`);
  
  return unselectedOptions;
};
const generateBackdropSvg = (backdropName) => {
  try {
    // Приводим название к формату как в gradients
    const gradientKey = backdropName.replace(/\s+/g, '_');
    
    if (gradients[gradientKey]) {
      const gradient = gradients[gradientKey];
      const gradientId = `gradient-${gradientKey.replace(/\s+/g, '-')}`;
      
      return `
        <svg width="40" height="40" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="${gradientId}" x1="0%" y1="0%" x2="100%" y2="100%">
              ${gradient.stops.map((stop, index) => 
                `<stop offset="${stop.offset}" stop-color="${stop.color}"/>`
              ).join('')}
            </linearGradient>
          </defs>
          <rect width="40" height="40" rx="8" fill="url(#${gradientId})"/>
        </svg>
      `;
    } else {
      // Fallback для неизвестных backdrop
      return `
        <svg width="40" height="40" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg">
          <rect width="40" height="40" rx="8" fill="#ccc"/>
          <text x="20" y="22" text-anchor="middle" font-size="10" fill="#666">?</text>
        </svg>
      `;
    }
  } catch (error) {
    console.error('❌ Ошибка генерации SVG для backdrop:', error);
    return `
      <svg width="40" height="40" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg">
        <rect width="40" height="40" rx="8" fill="#f0f0f0"/>
      </svg>
    `;
  }
};

// Исправленная функция для выбранных символов
const getSelectedSymbolOptions = () => {
  const allOptions = getFilteredSymbols(); // Эта функция возвращает отфильтрованные по поиску символы
  
  // ВСЕГДА показываем ВСЕ выбранные символы, даже если они не подходят под поиск
  const selectedOptions = allOptions.filter(symbol => 
    isOptionSelected('symbol', symbol.name)
  );
  
  console.log(`🔍 Выбранные символы: ${selectedOptions.length} (всегда показываются)`);
  return selectedOptions;
};

// Исправленная функция для невыбранных символов  
const getUnselectedSymbolOptions = () => {
  const query = searchQuery.value ? searchQuery.value.toLowerCase() : '';
  const allOptions = getFilteredSymbols();
  
  // Показываем только невыбранные символы, которые подходят под поиск
  const unselectedOptions = allOptions.filter(symbol => 
    !isOptionSelected('symbol', symbol.name) && (
      symbol.name.toLowerCase().includes(query) ||
      (symbol.rarityText && symbol.rarityText.toLowerCase().includes(query))
    )
  );
  
  console.log(`🔍 Невыбранные символы: ${unselectedOptions.length} (только соответствующие поиску "${query}")`);
  return unselectedOptions;
};


const fetchUserBalance = async () => {
      try {
        if (!currentAccountName.value) return;
        
        const { data, error } = await supabase
          .from('users')
          .select('ton_balance')
          .eq('name', currentAccountName.value)
          .single();
          
        if (error) throw error;
        
        if (data) {
          tonBalance.value = parseFloat(data.ton_balance || 0).toFixed(2);
          console.log('💰 Баланс пользователя загружен:', tonBalance.value);
        }
      } catch (error) {
        console.error('❌ Ошибка загрузки баланса:', error);
        tonBalance.value = '0';
      }
    };
// Функция строгой проверки дубликатов
const checkForDuplicateListing = async (sellData) => {
  try {
    const { data: existingItems, error } = await supabase
      .from('market')
      .select('*')
      .eq('seller', currentAccountName.value);

    if (error) throw error;
    if (!existingItems || existingItems.length === 0) return false;

    // Проверяем каждый существующий item на дубликат
    for (const existingItem of existingItems) {
      if (areItemsDuplicates(existingItem, sellData)) {
        console.warn('🚫 Найден дубликат при создании:', {
          existing: existingItem,
          new: sellData
        });
        return true;
      }
    }

    return false;
  } catch (error) {
    console.error('❌ Ошибка проверки дубликатов:', error);
    return false; // В случае ошибки разрешаем создание
  }
};
// Обновите существующее состояние success
const operationSuccess = ref({
  show: false,
  animationData: SuccessAnimation,
  type: 'purchase', // 'purchase', 'delisting', 'price_edit'
  title: 'Purchase Successful!'
});

// Добавьте состояние для fail
const operationFail = ref({
  show: false,
  animationData: FailAnimation,
  type: 'purchase_failed', // 'purchase_failed', 'insufficient_balance', 'transfer_failed'
  title: 'Operation Failed'
});

let lottieAnimation = null;
let lottieFailAnimation = null;

const playLottieAnimation = () => {
  console.log('🎨 playLottieAnimation вызвана, show:', operationSuccess.value.show);
  
  if (operationSuccess.value.show && operationSuccess.value.animationData) {
    console.log('✅ Условия для анимации выполнены');
    
    nextTick(() => {
      if (lottieAnimation) {
        lottieAnimation.destroy();
      }
      
      const container = document.querySelector('.lottie-container');
      if (container) {
        try {
          lottieAnimation = lottie.loadAnimation({
            container: container,
            renderer: 'svg',
            loop: false,
            autoplay: true,
            animationData: operationSuccess.value.animationData,
            rendererSettings: {
              preserveAspectRatio: 'xMidYMid meet'
            }
          });
          
          // Обработчик завершения анимации
          lottieAnimation.addEventListener('complete', () => {
            console.log('🏁 Анимация завершена');
            // Анимация завершилась - ждем 2 секунды на последнем кадре
            setTimeout(() => {
              operationSuccess.value.show = false;
              
              // Переходим на /shop
              console.log('🔄 Переход на /shop');
              router.push('/shop');
            }, 1000);
          });
        } catch (error) {
          console.error('Error loading Lottie animation:', error);
          // Fallback: закрываем через 2 секунды даже если анимация не загрузилась
          setTimeout(() => {
            operationSuccess.value.show = false;
            router.push('/shop');
          }, 1000);
        }
      }
    });
  } else {
    console.log('❌ Условия не выполнены:', {
      show: operationSuccess.value.show,
      hasAnimationData: !!operationSuccess.value.animationData
    });
  }
};



const symbolImagesCache = ref({});

// Функция для загрузки и конвертации TGS в изображение
const loadSymbolImageFromTgs = async (symbolName) => {
  try {
    // Если уже есть в кэше, возвращаем
    if (symbolImagesCache.value[symbolName]) {
      return symbolImagesCache.value[symbolName];
    }

    console.log(`🔄 Загрузка TGS для символа: ${symbolName}`);
    
    const symbolLink = `https://gifts.coffin.meme/patterns/${symbolName.toLowerCase().replace(/\s+/g, '%20')}.tgs`;
    
    // Создаем iframe для рендеринга анимации
    const iframe = document.createElement('iframe');
    iframe.style.cssText = 'position: absolute; left: -9999px; width: 400px; height: 400px;';
    
    const htmlContent = `
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/bodymovin/5.7.13/lottie.min.js"><\/script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/pako/2.0.4/pako.min.js"><\/script>
    <style>
        body {
            margin: 0;
            padding: 0;
            background: transparent;
        }
        #animation {
            width: 400px;
            height: 400px;
        }
        #canvas-container {
            width: 400px;
            height: 400px;
        }
    </style>
</head>
<body>
    <div id="canvas-container">
        <canvas id="animation-canvas" width="400" height="400"></canvas>
    </div>

    <script>
        let animationInstance = null;
        let renderStarted = false;

        async function loadAnimation() {
            try {
                const response = await fetch('${symbolLink}');
                if (!response.ok) throw new Error('HTTP error ' + response.status);
                
                const arrayBuffer = await response.arrayBuffer();
                const compressedData = new Uint8Array(arrayBuffer);
                const decompressedData = pako.inflate(compressedData, { to: 'string' });
                const animationData = JSON.parse(decompressedData);

                animationInstance = lottie.loadAnimation({
                    container: document.getElementById('animation-canvas'),
                    renderer: 'canvas',
                    loop: true,
                    autoplay: true,
                    animationData: animationData
                });

                // Ждем когда анимация начнет рендериться
                animationInstance.addEventListener('DOMLoaded', () => {
                    renderStarted = true;
                    // Даем время на отрисовку первого кадра
                    setTimeout(() => {
                        captureFrame();
                    }, 100);
                });

                // Fallback: если DOMLoaded не сработал
                setTimeout(() => {
                    if (!renderStarted) {
                        captureFrame();
                    }
                }, 1000);

            } catch (error) {
                console.error('Error loading animation:', error);
                // Отправляем сообщение об ошибке
                window.parent.postMessage({
                    type: 'symbolImageError',
                    symbolName: '${symbolName}',
                    error: error.message
                }, '*');
            }
        }

        function captureFrame() {
            try {
                const canvas = document.getElementById('animation-canvas');
                if (canvas) {
                    // Конвертируем canvas в data URL
                    const dataUrl = canvas.toDataURL('image/png');
                    
                    // Отправляем изображение обратно
                    window.parent.postMessage({
                        type: 'symbolImageReady',
                        symbolName: '${symbolName}',
                        imageData: dataUrl
                    }, '*');
                }
            } catch (error) {
                console.error('Error capturing frame:', error);
                window.parent.postMessage({
                    type: 'symbolImageError',
                    symbolName: '${symbolName}',
                    error: error.message
                }, '*');
            }
        }

        document.addEventListener('DOMContentLoaded', loadAnimation);
    <\/script>
</body>
</html>
    `;

    return new Promise((resolve, reject) => {
      // Обработчик сообщений от iframe
      const messageHandler = (event) => {
        if (event.data.type === 'symbolImageReady' && event.data.symbolName === symbolName) {
          
          // Сохраняем в кэш
          symbolImagesCache.value[symbolName] = event.data.imageData;
          
          // Убираем обработчик
          window.removeEventListener('message', messageHandler);
          
          // Удаляем iframe
          document.body.removeChild(iframe);
          
          resolve(event.data.imageData);
        }
        
        if (event.data.type === 'symbolImageError' && event.data.symbolName === symbolName) {
          console.error(`❌ Ошибка загрузки TGS для: ${symbolName}`, event.data.error);
          
          window.removeEventListener('message', messageHandler);
          document.body.removeChild(iframe);
          reject(new Error(event.data.error));
        }
      };

      window.addEventListener('message', messageHandler);

      // Устанавливаем содержимое iframe и добавляем в DOM
      iframe.srcdoc = htmlContent;
      document.body.appendChild(iframe);

      // Таймаут на случай если iframe не загрузится
      setTimeout(() => {
        if (symbolImagesCache.value[symbolName] === undefined) {
          window.removeEventListener('message', messageHandler);
          if (document.body.contains(iframe)) {
            document.body.removeChild(iframe);
          }
          reject(new Error('Timeout loading symbol animation'));
        }
      }, 5000);
    });

  } catch (error) {
    console.error(`❌ Ошибка в loadSymbolImageFromTgs для ${symbolName}:`, error);
    throw error;
  }
};

// Функция для получения всех символов с маркета и загрузки их изображений
const loadAllMarketSymbolsWithImages = async () => {
  try {
    console.log('🔄 Загрузка всех символов с маркета с изображениями...');
    
    const allSymbols = new Set();
    
    // Собираем все уникальные символы
    marketItems.value.forEach(item => {
      const symbol = extractSymbolFromNft(item);
      if (symbol && symbol.trim() !== '') {
        allSymbols.add(symbol);
      }
    });
    
    const symbolsArray = Array.from(allSymbols);
    console.log(`📊 Найдено символов: ${symbolsArray.length}`);
    
    // Загружаем изображения для каждого символа
    const loadPromises = symbolsArray.map(async (symbol) => {
      try {
        await loadSymbolImageFromTgs(symbol);
      } catch (error) {
        console.warn(`⚠️ Не удалось загрузить изображение для символа: ${symbol}`);
        // Можно установить fallback изображение
        symbolImagesCache.value[symbol] = null;
      }
    });
    
    await Promise.allSettled(loadPromises);
    
    console.log('✅ Загрузка символов завершена', symbolImagesCache.value);
    
  } catch (error) {
    console.error('❌ Ошибка загрузки символов с маркета:', error);
  }
};

// Функция для получения всех символов из activity_history
const getSymbolsFromActivityHistory = async () => {
  try {
    console.log('🔍 Загрузка символов из activity_history...');
    
    const { data, error } = await supabase
      .from('activity_history')
      .select('nft_object')
      .not('nft_object', 'is', null);

    if (error) {
      console.error('❌ Ошибка загрузки activity_history:', error);
      return [];
    }

    console.log(`📊 Загружено ${data?.length || 0} записей из activity_history`);

    const symbols = new Set();
    const symbolData = [];

    data.forEach(item => {
      try {
        const nftObject = typeof item.nft_object === 'string' 
          ? JSON.parse(item.nft_object) 
          : item.nft_object;

        if (nftObject && nftObject.symbol) {
          const symbol = nftObject.symbol;
          
          // Добавляем в Set для уникальности
          if (!symbols.has(symbol)) {
            symbols.add(symbol);
            
            // Извлекаем название и процент
            const symbolName = symbol.replace(/\d+\.?\d*%/, '').trim();
            const percentageMatch = symbol.match(/(\d+\.?\d*)%/);
            const percentage = percentageMatch ? parseFloat(percentageMatch[1]) : 0;
            
            symbolData.push({
              name: symbolName,
              fullName: symbol,
              percentage: percentage,
              rarityText: percentage > 0 ? `${percentage}%` : 'N/A',
              rarityClass: getRarityClass(percentage),
              htmlContent: generateSymbolHtml(symbolName), // Генерируем HTML контент
              value: symbolName.toLowerCase()
            });
          }
        }
      } catch (parseError) {
        console.error('❌ Ошибка парсинга nft_object:', parseError);
      }
    });

    // Сортируем по названию
    symbolData.sort((a, b) => a.name.localeCompare(b.name));
    
    console.log(`✅ Извлечено ${symbolData.length} уникальных символов из activity_history`);
    
    return symbolData;

  } catch (error) {
    console.error('❌ Общая ошибка извлечения символов:', error);
    return [];
  }
};
// Обновите обработчик ошибок изображений
const handleSymbolImageError = (event, symbolName) => {
  console.warn(`❌ Ошибка загрузки изображения для символа: ${symbolName}`);
  
  // Пробуем перезагрузить изображение
  setTimeout(async () => {
    try {
      await loadSymbolImageFromTgs(symbolName);
      // Форсируем обновление компонента
      forceUpdate.value++;
    } catch (error) {
      console.error(`❌ Не удалось перезагрузить изображение для: ${symbolName}`);
    }
  }, 1000);
};


// В mounted добавьте загрузку символов
onMounted(async () => {
  // ... существующий код ...
  
  // Загружаем символы после загрузки marketItems
  if (marketItems.value.length > 0) {
    await loadAllMarketSymbolsWithImages();
  }
  
  // Следим за изменениями marketItems
  watch(() => marketItems.value, async (newItems) => {
    if (newItems.length > 0) {
      await loadAllMarketSymbolsWithImages();
    }
  }, { immediate: true });
});

// Функция для принудительной перезагрузки всех изображений символов
const reloadAllSymbolImages = async () => {
  console.log('🔄 Принудительная перезагрузка всех изображений символов...');
  symbolImagesCache.value = {};
  await loadAllMarketSymbolsWithImages();
  forceUpdate.value++;
};








// Функция для показа успешной операции
// Обновите функцию showSuccessAnimation
const showSuccessAnimation = (type) => {
  console.log('🎬 showSuccessAnimation вызвана с типом:', type);
  
  const titles = {
    purchase: 'Purchase Successful!',
    delisting: 'Delisting Successful!',
    price_edit: 'Price Edit Successful!',
    listing: 'Listing Successful!',
    transfer: 'Transfer Successful!'
  };
  
  // Просто показываем анимацию, не трогая другие модалки
  operationSuccess.value.show = true;
  operationSuccess.value.type = type;
  operationSuccess.value.title = titles[type] || 'Operation Successful!';
  
  console.log('✅ operationSuccess установлен:', operationSuccess.value);
};
// Функция для сравнения двух объявлений
const areItemsDuplicates = (item1, item2) => {
  // Сравниваем основные поля
  if (item1.nft_type !== item2.nftType) return false;
  if (item1.seller !== currentAccountName.value) return false;
  
  // Для HTML NFT сравниваем URL
  if (item1.nft_type?.startsWith('html_nft_') && item1.nft_object && item2.nftData) {
    try {
      const nftObj1 = typeof item1.nft_object === 'string' ? JSON.parse(item1.nft_object) : item1.nft_object;
      const nftObj2 = item2.nftData;
      
      if (nftObj1.url && nftObj2.url && nftObj1.url === nftObj2.url) {
        return true; // Найден дубликат по URL
      }
    } catch (e) {
      console.error('Error comparing NFT objects:', e);
    }
  }
  
  // Для обычных NFT сравниваем цену и количество
  if (Math.abs(item1.price_per_unit - parseFloat(item2.price)) < 0.001) {
    if (item1.amount === (item2.amount || 1)) {
      return true; // Найден дубликат по цене и количеству
    }
  }
  
  return false;
};



// Функция добавления NFT в коллекцию покупателя
const addNftToUnlistedForBuyer = async (nftData, buyerName) => {
  try {
    const { data: buyerData, error: fetchError } = await supabase
      .from('users')
      .select('nft_links')
      .eq('name', buyerName)
      .single();

    if (fetchError) throw fetchError;

    const currentLinks = buyerData.nft_links || [];
    
    // Проверяем, нет ли уже этого NFT в коллекции покупателя
    const alreadyExists = currentLinks.some(nft => {
      const nftUrl = typeof nft === 'object' ? nft.url : nft;
      return nftUrl === nftData.url;
    });

    if (alreadyExists) {
      console.warn('⚠️ NFT уже есть в коллекции покупателя:', nftData.url);
      return;
    }

    // Добавляем NFT в коллекцию покупателя
    const updatedLinks = [...currentLinks, nftData];

    const { error: updateError } = await supabase
      .from('users')
      .update({ nft_links: updatedLinks })
      .eq('name', buyerName);

    if (updateError) throw updateError;

    console.log('✅ NFT добавлено в коллекцию покупателя:', buyerName, nftData.url);

  } catch (error) {
    console.error('❌ Ошибка добавления NFT покупателю:', error);
  }
};

// ДОБАВЬТЕ ЭТУ ФУНКЦИЮ ДЛЯ УДАЛЕНИЯ КОНФЛИКТНЫХ NFT
const removeConflictingNfts = async () => {
  try {
    console.log('🔍 Поиск конфликтных NFT (в unlisted и на маркете одновременно)...');
    
    const { data: userData, error: userError } = await supabase
      .from('users')
      .select('name, nft_links')
      .eq('name', currentAccountName.value)
      .single();

    if (userError) throw userError;

    const { data: marketData, error: marketError } = await supabase
      .from('market')
      .select('*')
      .eq('seller', currentAccountName.value);

    if (marketError) throw marketError;

    const userNftLinks = userData.nft_links || [];
    const userMarketItems = marketData || [];

    const conflicts = [];
    const nftLinksToRemove = [];

    // Ищем NFT которые есть и в unlisted и на маркете
    userMarketItems.forEach(marketItem => {
      if (marketItem.nft_object) {
        try {
          const marketNftObj = typeof marketItem.nft_object === 'string' 
            ? JSON.parse(marketItem.nft_object) 
            : marketItem.nft_object;
          
          if (marketNftObj.url) {
            const isAlsoInUnlisted = userNftLinks.some(nft => {
              const nftUrl = typeof nft === 'object' ? nft.url : nft;
              return nftUrl === marketNftObj.url;
            });
            
            if (isAlsoInUnlisted) {
              conflicts.push(marketNftObj.url);
              nftLinksToRemove.push(marketNftObj.url);
            }
          }
        } catch (e) {
          console.error('Error parsing market nft_object:', e);
        }
      }
    });

    // Удаляем конфликтные NFT из unlisted
    if (nftLinksToRemove.length > 0) {
      console.log(`🚫 Найдено ${conflicts.length} конфликтных NFT:`, conflicts);
      
      const updatedLinks = userNftLinks.filter(nft => {
        const nftUrl = typeof nft === 'object' ? nft.url : nft;
        return !nftLinksToRemove.includes(nftUrl);
      });

      // Обновляем базу данных
      const { error: updateError } = await supabase
        .from('users')
        .update({ nft_links: updatedLinks })
        .eq('name', currentAccountName.value);

      if (updateError) throw updateError;

      console.log(`✅ Удалено ${conflicts.length} конфликтных NFT из unlisted`);
      
      // Обновляем локальные данные
      await loadUnlistedNfts();
      
      return conflicts.length;
    } else {
      console.log('✅ Конфликтные NFT не найдены');
      return 0;
    }
    
  } catch (error) {
    console.error('❌ Ошибка удаления конфликтных NFT:', error);
    return 0;
  }
};

// ОБНОВИТЕ ФУНКЦИЮ СИНХРОНИЗАЦИИ
const syncNftState = async () => {
  try {
    console.log('🔄 Синхронизация состояния NFT...');
    
    // Удаляем конфликтные NFT
    const conflictsRemoved = await removeConflictingNfts();
    
    if (conflictsRemoved > 0) {
      showNotification(`Удалено ${conflictsRemoved} конфликтных NFT из коллекции`, 'warning');
    }
    
    console.log('✅ Синхронизация завершена');
    
  } catch (error) {
    console.error('❌ Ошибка синхронизации:', error);
  }
};

// Computed свойство для отслеживания актуальности данных рынка
const marketItemsMap = computed(() => {
  const map = {};
  marketItems.value.forEach(item => {
    if (item.item_id) {
      map[item.item_id] = true;
    }
  });
  return map;
});

// В mounted, обновите обработчик сообщений:
window.addEventListener('message', (event) => {
  if (event.data.type === 'openFullscreenView') {
    const item = findItemById(event.data.nftId, event.data.nftName);
    if (item && item.item_id) {
      // Используем router для навигации с item_id
      router.push(`/shop/${item.item_id}`);
    } else if (item) {
      openFullscreenView(item);
    }
  }
});
// Валидация количества для продажи
const validateSellAmount = () => {
  const maxAmount = nfts.value[sellModal.value.nftType];
  const value = sellModal.value.amount;
  
  if (value === '') return;
  
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

// Обновление расчетов цены
const updateCalculations = () => {
  if (sellModal.value.price && sellModal.value.amount) {
    const totalPrice = parseFloat(sellModal.value.price) * parseInt(sellModal.value.amount);
    const commission = getCommission(totalPrice);
    const finalAmount = calculateWithCommission(totalPrice);
    
    sellModal.value.totalPrice = totalPrice;
    sellModal.value.commission = commission;
    sellModal.value.finalAmount = finalAmount;
  }
};


// Функции для записи различных типов активности
const recordSaleActivity = async (item, amount = 1) => {
  return await addActivityRecord({
    item_id: item.item_id || item.id,
    nft_type: item.nft_type,
    nft_object: item.nft_object,
    html_content: item.html_content,
    operation_type: 'sale',
    price_per_unit: item.price_per_unit,
    currency: item.currency || 'TON',
    amount: amount,
    total_price: item.price_per_unit * amount,
    counterparty: item.buyer || null
  });
};



const recordTransferActivity = async (nftData, recipient, amount = 1) => {
  return await addActivityRecord({
    nft_type: `html_nft_${extractNftNameFromUrl(nftData.url)}`,
    nft_object: nftData,
    html_content: generateNftHtmlForList(nftData),
    operation_type: 'transfer',
    amount: amount,
    counterparty: recipient
  });
};


// Форматирование значения TON
const formatTonValue = (value) => {
  if (value === undefined || value === null || isNaN(value)) {
    return '0.0';
  }
  
  const num = parseFloat(value);
  if (isNaN(num)) return '0.0';
  
  // Возвращаем строку с 2 знаками после запятой
  return num.toFixed(2);
};
function parseModelsArray(modelsArray, nftType) {
  if (!Array.isArray(modelsArray)) return [];
  
  return modelsArray.map((modelString, index) => {
    try {
      const [name, percentage] = modelString.split('—').map(part => part.trim());
      const probability = parseFloat(percentage?.replace('%', '')) || 0;
      
      return {
        id: `${nftType}-${index}-${Date.now()}`,
        name: name || `Model ${index}`,
        probability,
        percentage: percentage || '0%',
        rarity: getRarityLevel(probability),
        image: generateModelImage(name, nftType),
        nftType,
        originalString: modelString
      };
    } catch (e) {
      console.warn(`Ошибка парсинга модели: ${modelString}`, e);
      return null;
    }
  }).filter(model => model !== null);
}

// Остальные вспомогательные функции остаются без изменений
function getRarityLevel(probability) {
  const rarityMap = [
    { max: 0.5, name: 'legendary' },
    { max: 1, name: 'epic' },
    { max: 1.5, name: 'rare' },
    { max: 2, name: 'uncommon' },
    { max: 2.5, name: 'common' },
    { max: Infinity, name: 'basic' }
  ];
  
  return rarityMap.find(r => probability <= r.max)?.name || 'basic';
}

function generateModelImage(modelName, nftType) {
  const baseName = modelName.toLowerCase().replace(/\s+/g, '-');
  return `/images/${nftType.toLowerCase()}/${baseName}.png`;
}
// Computed свойство для моделей в режиме групп
const groupedModelOptions = computed(() => {
  const groups = {};
  
  selectedFilters.value.nft.forEach(nftType => {
    if (nftModelsCache.value[nftType]) {
      const models = nftModelsCache.value[nftType].map(modelString => {
        const parts = modelString.split(' — ');
        if (parts.length === 2) {
          const name = parts[0].trim();
          const rarityText = parts[1].trim();
          const rarity = parseFloat(rarityText.replace('%', ''));
          
          return {
            name,
            rarity,
            rarityText,
            parentNft: nftType,
            imageUrl: getModelImageUrl(nftType, name),
            isSelected: isOptionSelected('model', name),
            floorPrice: getFloorPrice('model', name)
          };
        }
        return null;
      }).filter(Boolean);
      
      // Сортируем: сначала выбранные, затем по редкости
      models.sort((a, b) => {
        if (a.isSelected && !b.isSelected) return -1;
        if (!a.isSelected && b.isSelected) return 1;
        return a.rarity - b.rarity;
      });
      
      groups[nftType] = models;
    }
  });
  
  return groups;
});

const pathMap = {
  'easteregg': 'easter%20egg',
  'tophat': 'top%20hat',
  'deskcalendar': 'desk%20calendar',
  'plushpepe': 'plush%20pepe',
  'jackinthebox': 'jack%20in%20the%20box',
  'nekohelmet': 'neko%20helmet',
  'lovepotion': 'love%20potion',
  'toybear': 'toy%20bear',
  'diamondring': 'diamond%20ring',
  'lootbag': 'loot%20bag',
  'lunarsnake': 'lunar%20snake',
  'tamagadget': 'tama%20gadget',
  'candycane': 'candy%20cane',
  'cookieheart': 'cookie%20heart',
  'partysparkler': 'party%20sparkler',
  'jinglebells': 'jingle%20bells',
  'gingercookie': 'ginger%20cookie',
  'winterwreath': 'winter%20wreath',
  'santahat': 'santa%20hat',
  'snowglobe': 'snow%20globe',
  'snowmittens': 'snow%20mittens',
  'sleighbelle': 'sleigh%20bell',
  'jesterhat': 'jester%20hat',
  'starnotepad': 'star%20notepad',
  'bunnymuffin': 'bunny%20muffin',
  'swisswatch': 'swiss%20watch',
  'signetring': 'signet%20ring',
  'genielamp': 'genie%20lamp',
  'astralshard': 'astral%20shard',
  'preciouspeach': 'precious%20peach',
  'spicedwine': 'spiced%20wine',
  'jellybunny': 'jelly%20bunny',
  'hangingstar': 'hanging%20star',
  'durovscap': 'durovs%20cap',
  'lovecandle': 'love%20candle',
  'perfumebottle': 'perfume%20bottle',
  'minioscar': 'mini%20oscar',
  'eternalrose': 'eternal%20rose',
  'berrybox': 'berry%20box',
  'vintagecigar': 'vintage%20cigar',
  'recordplayer': 'record%20player',
  'magicpotion': 'magic%20potion',
  'electricskull': 'electric%20skull',
  'kissedfrog': 'kissed%20frog',
  'hypnolollipop': 'hypno%20lollipop',
  'hexpot': 'hex%20pot',
  'evileye': 'evil%20eye',
  'iongem': 'ion%20gem',
  'sharptongue': 'sharp%20tongue',
  'madhumpkin': 'mad%20pumpkin',
  'trappedheart': 'trapped%20heart',
  'skullflower': 'skull%20flower',
  'crystalball': 'crystal%20ball',
  'flyingbroom': 'flying%20broom',
  'voodoodoll': 'voodoo%20doll',
  'scaredcat': 'scared%20cat',
  'witchhat': 'witch%20hat',
  'eternalcandle': 'eternal%20candle',
  'spyagaric': 'spy%20agaric',
  'lolpop': 'lol%20pop',
  'sakuraflower': 'sakura%20flower',
  'homemadecake': 'homemade%20cake',
  'bdaycandle': 'bday%20candle'
};

const toggleMyNftsViewMode = () => {
  myNftsViewMode.value = myNftsViewMode.value === 'listed' ? 'unlisted' : 'listed';
};

const getSortedNftOptions = async () => {
  // ДОБАВИТЬ await - это ключевое!
  const allOptions = await getFilteredNftOptions();
  
  // Проверка на массив (на всякий случай)
  if (!Array.isArray(allOptions)) {
    console.error('❌ allOptions не массив:', allOptions);
    return [];
  }
  
  console.log('🔍 Все опции NFT перед сортировкой:', allOptions.map(opt => ({
    name: opt.name,
    originalType: opt.originalType,
    normalized: normalizeNftName(opt.originalType),
    isSelected: isOptionSelected('nft', opt.originalType)
  })));
  
  const selectedOptions = allOptions.filter(option => 
    isOptionSelected('nft', option.originalType)
  );
  const unselectedOptions = allOptions.filter(option => 
    !isOptionSelected('nft', option.originalType)
  );
  
  console.log('✅ Выбранные:', selectedOptions.map(opt => opt.name));
  console.log('❌ Невыбранные:', unselectedOptions.map(opt => opt.name));
  
  const result = [...selectedOptions, ...unselectedOptions];
  console.log('📋 Итоговый список:', result.map(opt => opt.name));
  
  return result;
};

// Добавьте эти функции в script секцию

// Функция для извлечения номера NFT из URL
const extractNftNumberFromUrl = (url) => {
  try {
    if (!url) return null;
    const match = url.match(/-(\d+)(?:\?|$)/);
    return match ? match[1] : null;
  } catch (error) {
    console.error('Error extracting NFT number from URL:', error);
    return null;
  }
};

// Функция для извлечения номера из item (для market items)
const extractNftNumberFromItem = (item) => {
  try {
    // Для market items из nft_object
    if (item?.nft_object?.url) {
      return extractNftNumberFromUrl(item.nft_object.url);
    }
    // Для unlisted NFT из nftData
    if (item?.url) {
      return extractNftNumberFromUrl(item.url);
    }
    return null;
  } catch (error) {
    console.error('Error extracting NFT number from item:', error);
    return null;
  }
};

// Обновленная функция extractNameFromNftObject с номером
const extractNameFromNftObject = (item) => {
  if (!item) return { name: 'Unknown NFT', number: '' };
  
  try {
    let name = 'Unknown NFT';
    let number = '';
    
    if (item.nft_object) {
      const nftObj = typeof item.nft_object === 'string' 
        ? JSON.parse(item.nft_object) 
        : item.nft_object;
      name = nftObj.name || name;
      
      // Извлекаем номер из URL если есть
      if (nftObj.url) {
        const idMatch = nftObj.url.match(/-(\d+)(?:\?|$)/);
        if (idMatch) {
          number = idMatch[1];
        }
      }
    }
    
    return { name, number };
  } catch (error) {
    console.error('Error extracting name from NFT object:', error);
    return { name: 'Unknown NFT', number: '' };
  }
};

// Функция для извлечения данных из nftData (для transfer и sell modal)
const extractNftDataWithNumber = (nftData) => {
  try {
    if (!nftData) {
      return {
        name: 'Unknown NFT',
        number: null,
        fullName: 'Unknown NFT'
      };
    }
    
    const name = nftData.name || 'Unknown NFT';
    const number = extractNftNumberFromUrl(nftData.url);
    
    if (number) {
      return {
        name: name,
        number: number,
        fullName: `${name} #${number}`
      };
    }
    
    return {
      name: name,
      number: null,
      fullName: name
    };
  } catch (error) {
    console.error('Error extracting NFT data with number:', error);
    return {
      name: 'Unknown NFT',
      number: null,
      fullName: 'Unknown NFT'
    };
  }
};
// Единая функция для генерации корректных URL для МОДЕЛЕЙ
const generateCorrectImageUrl = (nftName, modelName) => {
  // Проверяем входные данные
  if (!nftName || !modelName) {
    console.warn('❌ generateCorrectImageUrl: отсутствуют nftName или modelName', { nftName, modelName });
    return default_nft_image;
  }
  
  // Очищаем пути - только буквы a-z (убираем все не-буквенные символы)
  const cleanNftPath = nftName.toLowerCase().replace(/[^a-z]/g, '');
  const cleanModelPath = modelName.toLowerCase().replace(/[^a-z]/g, '');
  
  console.log('🔄 Генерация URL для модели:', {
    originalNft: nftName,
    originalModel: modelName,
    cleanNftPath,
    cleanModelPath
  });
  
  // Проверяем, что пути не пустые после очистки
  if (!cleanNftPath || !cleanModelPath) {
    console.warn('❌ generateCorrectImageUrl: пустые пути после очистки');
    return default_nft_image;
  }
  
  const url = `https://storage.portal-market.com/portals-market/gifts/${cleanNftPath}/models/png/${cleanModelPath}.png`;
  
  console.log(`✅ Сгенерирован URL для модели: ${url}`);
  return url;
};


// Основная функция для получения URL модели
const getModelImageUrl = (nftType, modelName) => {
  if (!nftType || !modelName) {
    console.warn('❌ getModelImageUrl: отсутствуют параметры', { nftType, modelName });
    return default_nft_image;
  }
  
  let cleanNftType = nftType.toLowerCase();
  if (cleanNftType.startsWith('html_nft_')) {
    cleanNftType = cleanNftType.replace('html_nft_', '');
  }
  if (cleanNftType.startsWith('htmlnft')) {
    cleanNftType = cleanNftType.replace('htmlnft', '');
  }
  
  const folderName = groupDisplayNames[cleanNftType] || cleanNftType;
  
  return generateCorrectImageUrl(folderName, modelName);
};

// Улучшенная версия getNftImage с использованием моделей
const getNftImage = async (nftType) => {
  console.log(`🖼️ getNftImage вызван для: ${nftType}`);
  
  // Если у нас уже есть URL из loadNftImages, используем его
  if (nftImageUrls.value[nftType]) {
    return nftImageUrls.value[nftType];
  }
  
  let cleanNftType = nftType.toLowerCase();
  if (cleanNftType.startsWith('html_nft_')) {
    cleanNftType = cleanNftType.replace('html_nft_', '');
  }
  if (cleanNftType.startsWith('htmlnft')) {
    cleanNftType = cleanNftType.replace('htmlnft', '');
  }
  
  const folderName = groupDisplayNames[cleanNftType] || cleanNftType;
  
  try {
    // Пытаемся получить случайную модель
    const randomModel = await getRandomModelForNft(folderName);
    
    if (randomModel) {
      const url = generateCorrectImageUrl(folderName, randomModel);
      console.log(`🎨 Сгенерирован URL для NFT с моделью: ${url}`);
      
      // Сохраняем в кэш
      nftImageUrls.value[nftType] = url;
      return url;
    }
  } catch (error) {
    console.warn(`⚠️ Не удалось получить модель для ${folderName}, используем fallback`);
  }
  
  // Fallback: используем legacy URL
  const legacyUrl = `https://gifts.coffin.meme/${folderName.toLowerCase().replace(/\s+/g, '%20')}/Classic.png`;
  console.log(`🔄 Используем legacy URL: ${legacyUrl}`);
  
  return legacyUrl;
};
// Специальная функция для NFT в фильтрах
const getNftImageSync = (nftType) => {
  console.log(`🖼️ getNftImageSync вызван для NFT: ${nftType}`);
  
  let cleanNftType = nftType.toLowerCase();
  
  // Убираем префиксы
  if (cleanNftType.startsWith('html_nft_')) {
    cleanNftType = cleanNftType.replace('html_nft_', '');
  }
  if (cleanNftType.startsWith('htmlnft')) {
    cleanNftType = cleanNftType.replace('htmlnft', '');
  }
  
  console.log('🔧 Очищенный nftType:', cleanNftType);
  
  // Получаем отображаемое имя
  const folderName = groupDisplayNames[cleanNftType] || cleanNftType;
  console.log('📁 folderName:', folderName);
  
  // Для NFT в фильтрах используем первую доступную модель
  // Вместо имени NFT используем конкретную модель
  const nftNameForUrl = folderName.toLowerCase().replace(/[^a-z]/g, '');
  
  // Получаем первую модель для этого NFT
  const firstModel = getFirstModelForNft(cleanNftType);
  const modelNameForUrl = firstModel.toLowerCase().replace(/[^a-z]/g, '');
  
  console.log('🎯 Параметры для URL:', {
    nftNameForUrl,
    modelNameForUrl,
    firstModel
  });
  
  const url = `https://storage.portal-market.com/portals-market/gifts/${nftNameForUrl}/models/png/${modelNameForUrl}.png`;
  
  console.log(`✅ Сгенерирован URL для NFT фильтра: ${url}`);
  return url;
};

// Функция для получения первой модели NFT
const getFirstModelForNft = (nftType) => {
  const models = nftModelsCache.value[nftType];
  if (models && models.length > 0) {
    // Берем первую модель и извлекаем только название (до "—")
    const firstModelString = models[0];
    const modelName = firstModelString.split(' — ')[0].trim();
    console.log(`📦 Первая модель для ${nftType}: ${modelName}`);
    return modelName;
  }
  
  // Fallback модели для разных типов NFT
  const fallbackModels = {
    'lolpop': 'Classic',
    'jack-in-the-box': 'Classic', 
    'deskcalendar': 'Classic',
    'easteregg': 'Classic',
    'notebook': 'Classic',
    'phonecase': 'Classic',
    'playingcards': 'Classic',
    'smartwatch': 'Classic',
    'usb': 'Classic'
  };
  
  const fallback = fallbackModels[nftType.toLowerCase()] || 'Classic';
  console.log(`🔄 Используем fallback модель для ${nftType}: ${fallback}`);
  return fallback;
};


// Главная функция получения отсортированных и отфильтрованных items
const getSortedItems = () => {
  let items = [];
  
  // Определяем источник данных в зависимости от вкладки
  if (activeTab.value === 'market') {
    items = [...marketItems.value];
  } else if (activeTab.value === 'my-nfts') {
    if (myNftsViewMode.value === 'listed') {
      items = [...myMarketItems.value];
    } else {
      // Для unlisted преобразуем в формат market items
      items = myUnlistedNfts.value.map(nftData => ({
        id: `unlisted-${extractNftIdFromUnlisted(nftData)}`,
        nft_type: `html_nft_${extractNftNameFromUrl(nftData.url)}`,
        nft_object: nftData,
        html_content: generateNftHtmlForList(nftData),
        seller: currentAccountName.value,
        is_unlisted: true,
        created_at: new Date().toISOString()
      }));
    }
  }
  
  console.log('📊 Items before filtering:', items.length);
  
  // Применяем фильтр по ID
  if (selectedIdFilter.value !== null) {
    items = items.filter(item => {
      const itemId = extractNftIdFromData(item.nft_object || item);
      const matches = itemId === selectedIdFilter.value.toString();
      console.log(`🔍 ID Filter: ${itemId} === ${selectedIdFilter.value} = ${matches}`);
      return matches;
    });
    console.log('📊 After ID filter:', items.length);
  }
  
  // Применяем ценовой фильтр
  if (priceRangeMenu.value.minPrice || priceRangeMenu.value.maxPrice) {
    const min = parseFloat(priceRangeMenu.value.minPrice) || 0;
    const max = parseFloat(priceRangeMenu.value.maxPrice) || Infinity;
    
    items = items.filter(item => {
      const price = parseFloat(item.price_per_unit) || 0;
      const inRange = price >= min && price <= max;
      console.log(`💰 Price Filter: ${price} in [${min}, ${max}] = ${inRange}`);
      return inRange;
    });
    console.log('📊 After price filter:', items.length);
  }
  
  // Применяем сортировку
  items = applySorting(items, sortMenu.value.selected);
  
  console.log('✅ Final filtered items:', items.length);
  return items;
};

// Функция применения сортировки
// Функция применения сортировки
const applySorting = (items, sortType) => {
  const sorted = [...items];
  
  switch (sortType) {
    case 'newest':
      return sorted.sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0));
    
    case 'oldest':
      return sorted.sort((a, b) => new Date(a.created_at || 0) - new Date(b.created_at || 0));
    
    case 'price_low_high':
      return sorted.sort((a, b) => (parseFloat(a.price_per_unit) || 0) - (parseFloat(b.price_per_unit) || 0));
    
    case 'price_high_low':
      return sorted.sort((a, b) => (parseFloat(b.price_per_unit) || 0) - (parseFloat(a.price_per_unit) || 0));
    
    case 'id_low_high':
      return sorted.sort((a, b) => {
        const aId = parseInt(extractNftIdFromData(a.nft_object || a)) || 0;
        const bId = parseInt(extractNftIdFromData(b.nft_object || b)) || 0;
        return aId - bId;
      });
    
    case 'id_high_low':
      return sorted.sort((a, b) => {
        const aId = parseInt(extractNftIdFromData(a.nft_object || a)) || 0;
        const bId = parseInt(extractNftIdFromData(b.nft_object || b)) || 0;
        return bId - aId;
      });
    
    default:
      return sorted;
  }
};

const generateImageUrl = async (nftType) => {
  const path = pathMap[nftType] || 
              nftType.toLowerCase().replace(/([A-Z])/g, ' $1').trim().replace(/\s+/g, '%20');

  try {
    // Получаем случайную модель из базы данных
    const dbColumnName = pathMap[nftType]?.replace('%20', ' ') || nftType;
    const { data } = await supabase
      .from('nft')
      .select(`"${dbColumnName}"`)
      .not(`"${dbColumnName}"`, 'is', null)
      .limit(50);

    if (data?.length) {
      const models = data.flatMap(row => row[dbColumnName]);
      if (models.length > 0) {
        const randomModel = models[Math.floor(Math.random() * models.length)];
        const modelName = randomModel.split(' — ')[0].replace(/\s+/g, '%20');
        return `https://gifts.coffin.meme/${path}/${modelName}.png`;
      }
    }
  } catch (e) {
    console.error(`Error loading image for ${nftType}:`, e);
  }

  // Fallback URL
  return `https://gifts.coffin.meme/${path}/Pepe%20Plans.png`;
};
    const refreshNftImages = async () => {
      console.clear();
      console.log('🔄 Обновляем все NFT изображения...');
      await loadNftImages(getUniqueNftTypes.value);
    };



const showFilterDropdown = ref(false);

const toggleFilterDropdown = () => {
  showFilterDropdown.value = !showFilterDropdown.value;
};


// Обновленная функция применения ID фильтра
const applyIdFilter = () => {
  if (idFilterValue.value) {
    const id = parseInt(idFilterValue.value);
    if (!isNaN(id)) {
      selectedIdFilter.value = id;
      activeFilterCategory.value = null;
      idFilterValue.value = '';
      updateFilteredItems();
      showNotification(`Filter applied: ID ${id}`, 'success');
    } else {
      showNotification('Please enter a valid number', 'error');
    }
  }
};

// Обновленная функция очистки ID фильтра
const clearIdFilter = () => {
  selectedIdFilter.value = null;
  idFilterValue.value = '';
  selectedFilters.value.price = [];
  updateFilteredItems();
  showNotification('ID filter cleared', 'success');
  activeFilterCategory.value = null;
};

    // Добавьте эти методы в script секцию
const startModalDrag = (event, modalType) => {
  isDraggingModal.value = true;
  dragStartY.value = event.type.includes('touch') ? event.touches[0].clientY : event.clientY;
  dragCurrentY.value = 0;
};

const doModalDrag = (event, modalType) => {
  if (!isDraggingModal.value) return;
  
  const currentY = event.type.includes('touch') ? event.touches[0].clientY : event.clientY;
  dragCurrentY.value = currentY - dragStartY.value;
  
  // Можно добавить визуальную обратную связь при перетаскивании
  if (dragCurrentY.value > 50) {
    // Закрыть модальное окно при достаточном перетаскивании вниз
    closeModal(modalType);
  }
};

const isDraggingFromHandle = ref(false);

const handleTouchStart = (e) => {
  // Предотвращаем обработку свайпов по всему элементу
  // Свайпы будут работать только через handle
  if (!e.target.closest('.modal-drag-handle')) {
    return;
  }
};

const handleMouseDown = (e) => {
  // Аналогично для мыши
  if (!e.target.closest('.modal-drag-handle')) {
    return;
  }
};

const startDrag = (e) => {
  isDraggingFromHandle.value = true;
  
  // Ваша существующая логика для начала drag
  if (e.type === 'touchstart') {
    dragStartY.value = e.touches[0].clientY;
    document.addEventListener('touchmove', handleDragMove, { passive: false });
    document.addEventListener('touchend', handleDragEnd);
  } else {
    dragStartY.value = e.clientY;
    document.addEventListener('mousemove', handleDragMove);
    document.addEventListener('mouseup', handleDragEnd);
  }
  
  isDraggingModal.value = true;
};

const handleDragMove = (e) => {
  if (!isDraggingFromHandle.value) return;
  
  // Ваша существующая логика перемещения
  const clientY = e.type === 'touchmove' ? e.touches[0].clientY : e.clientY;
  const deltaY = clientY - dragStartY.value;
  
  if (deltaY > 0) {
    e.preventDefault();
    dragCurrentY.value = deltaY;
    
    // Закрытие при достаточном свайпе вниз
    if (deltaY > 100) {
      closeFilterMenu();
      handleDragEnd();
    }
  }
};

const handleDragEnd = () => {
  if (!isDraggingFromHandle.value) return;
  
  // Ваша существующая логика завершения drag
  document.removeEventListener('mousemove', handleDragMove);
  document.removeEventListener('mouseup', handleDragEnd);
  document.removeEventListener('touchmove', handleDragMove);
  document.removeEventListener('touchend', handleDragEnd);
  
  isDraggingModal.value = false;
  isDraggingFromHandle.value = false;
  
  // Анимация возврата или закрытия
  if (dragCurrentY.value < 100) {
    dragCurrentY.value = 0;
  } else {
    closeFilterMenu();
  }
};

const closeFilterMenu = () => {
  activeFilterCategory.value = null;
  dragCurrentY.value = 0;
  isDraggingFromHandle.value = false;
};
// Функция для получения минимальной цены с учетом всех активных фильтров
// Функция для получения минимальной цены с учетом всех активных фильтров
const getFloorPrice = (category, optionName) => {
  
  try {
    if (!optionName) {
      console.log('❌ optionName is empty');
      console.groupEnd();
      return null;
    }

    const currentItems = getCurrentDataSource.value;
    
    if (!currentItems || currentItems.length === 0) {
      console.log('❌ No items in data source');
      console.groupEnd();
      return null;
    }

    let filteredItems = [];
    
    if (category === 'nft') {
      const normalizedOptionName = normalizeNftName(optionName);
      
      filteredItems = currentItems.filter(item => {
        // Проверяем фильтр по ID
        if (selectedIdFilter.value !== null) {
          const itemId = extractNftIdFromData(item.nft_object || item);
          if (itemId.toString() !== selectedIdFilter.value.toString()) {
            console.log(`❌ Item ${itemId} doesn't match ID filter ${selectedIdFilter.value}`);
            return false;
          }
        }

        // НЕ ПРОВЕРЯЕМ фильтр по NFT для расчета floor price (чтобы невыбранные NFT тоже учитывались)
        // Проверяем только другие активные фильтры

        // Проверяем фильтр по Model
        if (selectedFilters.value.model.length > 0) {
          const itemModel = extractModelFromNft(item);
          if (!itemModel) {
            console.log(`❌ Item has no model, but model filter is active`);
            return false;
          }
          
          const passesModelFilter = selectedFilters.value.model.some(selectedModel => 
            itemModel.toLowerCase().includes(selectedModel.toLowerCase())
          );
          if (!passesModelFilter) {
            console.log(`❌ Item model "${itemModel}" doesn't match model filter`);
            return false;
          }
        }

        // Проверяем фильтр по Symbol
        if (selectedFilters.value.symbol.length > 0) {
          const itemSymbol = extractSymbolFromNft(item);
          if (!itemSymbol) {
            console.log(`❌ Item has no symbol, but symbol filter is active`);
            return false;
          }
          
          const normalizedItemSymbol = normalizeSymbolName(itemSymbol);
          const passesSymbolFilter = selectedFilters.value.symbol.some(selectedSymbol => {
            const normalizedSelectedSymbol = normalizeSymbolName(selectedSymbol);
            return normalizedItemSymbol === normalizedSelectedSymbol;
          });
          if (!passesSymbolFilter) {
            console.log(`❌ Item symbol "${itemSymbol}" doesn't match symbol filter`);
            return false;
          }
        }

        // Проверяем фильтр по Backdrop
        if (selectedFilters.value.backdrop.length > 0) {
          const itemBackdrop = extractBackdropFromNft(item);
          if (!itemBackdrop) {
            console.log(`❌ Item has no backdrop, but backdrop filter is active`);
            return false;
          }
          
          const cleanItemBackdrop = itemBackdrop.split(' ')[0].toLowerCase().trim();
          const passesBackdropFilter = selectedFilters.value.backdrop.some(selectedBackdrop => {
            const cleanSelectedBackdrop = selectedBackdrop.split(' ')[0].toLowerCase().trim();
            return cleanItemBackdrop === cleanSelectedBackdrop;
          });
          if (!passesBackdropFilter) {
            console.log(`❌ Item backdrop "${itemBackdrop}" doesn't match backdrop filter`);
            return false;
          }
        }

        // Основная проверка по NFT категории
        const itemName = getNftDisplayName(item.nft_type, item.nft_object);
        const normalizedItemName = normalizeNftName(itemName);
        const matches = normalizedItemName.includes(normalizedOptionName);
        
        return matches;
      });
      
    } else if (category === 'model') {
      const normalizedModelName = optionName.toLowerCase().trim();
      filteredItems = currentItems.filter(item => {
        // Проверяем все фильтры кроме model (для model категории)
        if (selectedIdFilter.value !== null) {
          const itemId = extractNftIdFromData(item.nft_object || item);
          if (itemId.toString() !== selectedIdFilter.value.toString()) return false;
        }

        if (selectedFilters.value.nft.length > 0) {
          const itemName = getNftDisplayName(item.nft_type, item.nft_object);
          const normalizedItemName = normalizeNftName(itemName);
          const passesNftFilter = selectedFilters.value.nft.some(selectedNft => {
            const normalizedSelected = normalizeNftName(selectedNft);
            return normalizedItemName.includes(normalizedSelected);
          });
          if (!passesNftFilter) return false;
        }

        if (selectedFilters.value.symbol.length > 0) {
          const itemSymbol = extractSymbolFromNft(item);
          if (!itemSymbol) return false;
          const normalizedItemSymbol = normalizeSymbolName(itemSymbol);
          const passesSymbolFilter = selectedFilters.value.symbol.some(selectedSymbol => {
            const normalizedSelectedSymbol = normalizeSymbolName(selectedSymbol);
            return normalizedItemSymbol === normalizedSelectedSymbol;
          });
          if (!passesSymbolFilter) return false;
        }

        if (selectedFilters.value.backdrop.length > 0) {
          const itemBackdrop = extractBackdropFromNft(item);
          if (!itemBackdrop) return false;
          const cleanItemBackdrop = itemBackdrop.split(' ')[0].toLowerCase().trim();
          const passesBackdropFilter = selectedFilters.value.backdrop.some(selectedBackdrop => {
            const cleanSelectedBackdrop = selectedBackdrop.split(' ')[0].toLowerCase().trim();
            return cleanItemBackdrop === cleanSelectedBackdrop;
          });
          if (!passesBackdropFilter) return false;
        }

        // Проверка по model
        const model = extractModelFromNft(item);
        const matches = model && model.toLowerCase().includes(normalizedModelName);
        return matches;
      });
      
    } else if (category === 'symbol') {
      const normalizedSymbolName = normalizeSymbolName(optionName);
      filteredItems = currentItems.filter(item => {
        // Проверяем все фильтры кроме symbol (для symbol категории)
        if (selectedIdFilter.value !== null) {
          const itemId = extractNftIdFromData(item.nft_object || item);
          if (itemId.toString() !== selectedIdFilter.value.toString()) return false;
        }

        if (selectedFilters.value.nft.length > 0) {
          const itemName = getNftDisplayName(item.nft_type, item.nft_object);
          const normalizedItemName = normalizeNftName(itemName);
          const passesNftFilter = selectedFilters.value.nft.some(selectedNft => {
            const normalizedSelected = normalizeNftName(selectedNft);
            return normalizedItemName.includes(normalizedSelected);
          });
          if (!passesNftFilter) return false;
        }

        if (selectedFilters.value.model.length > 0) {
          const itemModel = extractModelFromNft(item);
          if (!itemModel) return false;
          const passesModelFilter = selectedFilters.value.model.some(selectedModel => 
            itemModel.toLowerCase().includes(selectedModel.toLowerCase())
          );
          if (!passesModelFilter) return false;
        }

        if (selectedFilters.value.backdrop.length > 0) {
          const itemBackdrop = extractBackdropFromNft(item);
          if (!itemBackdrop) return false;
          const cleanItemBackdrop = itemBackdrop.split(' ')[0].toLowerCase().trim();
          const passesBackdropFilter = selectedFilters.value.backdrop.some(selectedBackdrop => {
            const cleanSelectedBackdrop = selectedBackdrop.split(' ')[0].toLowerCase().trim();
            return cleanItemBackdrop === cleanSelectedBackdrop;
          });
          if (!passesBackdropFilter) return false;
        }

        // Проверка по symbol
        const symbol = extractSymbolFromNft(item);
        const matches = symbol && normalizeSymbolName(symbol) === normalizedSymbolName;
        return matches;
      });
      
    } else if (category === 'backdrop') {
      const cleanBackdrop = optionName.split(' ')[0].toLowerCase().trim();
      filteredItems = currentItems.filter(item => {
        // Проверяем все фильтры кроме backdrop (для backdrop категории)
        if (selectedIdFilter.value !== null) {
          const itemId = extractNftIdFromData(item.nft_object || item);
          if (itemId.toString() !== selectedIdFilter.value.toString()) return false;
        }

        if (selectedFilters.value.nft.length > 0) {
          const itemName = getNftDisplayName(item.nft_type, item.nft_object);
          const normalizedItemName = normalizeNftName(itemName);
          const passesNftFilter = selectedFilters.value.nft.some(selectedNft => {
            const normalizedSelected = normalizeNftName(selectedNft);
            return normalizedItemName.includes(normalizedSelected);
          });
          if (!passesNftFilter) return false;
        }

        if (selectedFilters.value.model.length > 0) {
          const itemModel = extractModelFromNft(item);
          if (!itemModel) return false;
          const passesModelFilter = selectedFilters.value.model.some(selectedModel => 
            itemModel.toLowerCase().includes(selectedModel.toLowerCase())
          );
          if (!passesModelFilter) return false;
        }

        if (selectedFilters.value.symbol.length > 0) {
          const itemSymbol = extractSymbolFromNft(item);
          if (!itemSymbol) return false;
          const normalizedItemSymbol = normalizeSymbolName(itemSymbol);
          const passesSymbolFilter = selectedFilters.value.symbol.some(selectedSymbol => {
            const normalizedSelectedSymbol = normalizeSymbolName(selectedSymbol);
            return normalizedItemSymbol === normalizedSelectedSymbol;
          });
          if (!passesSymbolFilter) return false;
        }

        // Проверка по backdrop
        const backdrop = extractBackdropFromNft(item);
        const matches = backdrop && backdrop.split(' ')[0].toLowerCase().trim() === cleanBackdrop;
        return matches;
      });
    }

    
    if (filteredItems.length === 0) {
      console.log('❌ No matching items found');
      console.groupEnd();
      return null;
    }

    // Находим минимальную цену
    const prices = filteredItems
      .filter(item => item.price_per_unit && item.currency === 'TON')
      .map(item => parseFloat(item.price_per_unit))
      .filter(price => !isNaN(price) && price > 0);

    
    if (prices.length === 0) {
      console.log('❌ No valid prices found');
      console.groupEnd();
      return null;
    }

    const minPrice = Math.min(...prices);
    console.groupEnd();
    
    return minPrice;
    
  } catch (error) {
    console.error('❌ Error in getFloorPrice:', error);
    console.groupEnd();
    return null;
  }
};


// Функция для принудительного обновления всех floor prices
const updateAllFloorPrices = () => {
  floorPriceCache.value = {};
  
  // Форсируем пересчет computed свойств
  nextTick(() => {
    // Вызываем пересчет для всех категорий
    getFilteredNftOptions();
    getFilteredModels();
    getFilteredSymbols();
    getFilteredBackdrops();
  });
};



// Исправленная функция для получения всех символов из offers
const getAllSymbolsFromAllOffers = () => {
  try {
    console.log('🔍 Загрузка символов из ВСЕХ offers...');
    
    const allSymbols = new Map();

    allOffers.value.forEach(offer => {
      try {
        const nftData = offer.nft_data;
        if (nftData && nftData.symbol) {
          const symbol = nftData.symbol;
          
          // Извлекаем название и процент
          const symbolName = symbol.replace(/\d+\.?\d*%/, '').trim();
          const percentageMatch = symbol.match(/(\d+\.?\d*)%/);
          const percentage = percentageMatch ? parseFloat(percentageMatch[1]) : 0;
          
          if (symbolName) {
            if (!allSymbols.has(symbolName)) {
              allSymbols.set(symbolName, {
                name: symbolName,
                fullName: symbol,
                percentage: percentage,
                rarityText: percentage > 0 ? `${percentage}%` : 'N/A',
                rarityClass: getRarityClass(percentage),
                htmlContent: generateSymbolHtml(symbolName) // Передаем строку, а не объект
              });
            }
          }
        }
      } catch (error) {
        console.error('❌ Ошибка обработки offer:', error);
      }
    });

    const symbolData = Array.from(allSymbols.values());
    symbolData.sort((a, b) => a.name.localeCompare(b.name));
    
    console.log(`✅ Извлечено ${symbolData.length} уникальных символов из ВСЕХ offers`);
    return symbolData;

  } catch (error) {
    console.error('❌ Ошибка загрузки символов из offers:', error);
    return [];
  }
};

// Добавьте forceUpdate в data
const forceUpdate = ref(0);

// И добавьте метод для принудительного обновления
const triggerForceUpdate = () => {
  forceUpdate.value += 1;
};
// Обновленная функция для получения отфильтрованных символов
// Обновленная функция для получения отфильтрованных символов
// Обновленная функция для получения символов с учетом выбранного статуса offer
const getAllSymbolsFromFilteredOffers = () => {
  try {
    console.log('🔍 Загрузка символов из offers с фильтром статуса:', selectedOfferType.value);
    
    const allSymbols = new Map();

    // Используем filteredOffers вместо allOffers чтобы учитывать статус
    filteredOffers.value.forEach(offer => {
      try {
        // Проверяем статус offer
        if (selectedOfferType.value !== 'all' && offer.status !== selectedOfferType.value) {
          return; // Пропускаем offers с неподходящим статусом
        }
        
        const nftData = offer.nft_data;
        if (nftData && nftData.symbol) {
          const symbol = nftData.symbol;
          
          // Извлекаем название и процент
          const symbolName = symbol.replace(/\d+\.?\d*%/, '').trim();
          const percentageMatch = symbol.match(/(\d+\.?\d*)%/);
          const percentage = percentageMatch ? parseFloat(percentageMatch[1]) : 0;
          
          if (symbolName) {
            if (!allSymbols.has(symbolName)) {
              allSymbols.set(symbolName, {
                name: symbolName,
                fullName: symbol,
                percentage: percentage,
                rarityText: percentage > 0 ? `${percentage}%` : 'N/A',
                rarityClass: getRarityClass(percentage),
                htmlContent: generateSymbolHtml(symbolName)
              });
            }
          }
        }
      } catch (error) {
        console.error('❌ Ошибка обработки offer:', error);
      }
    });

    const symbolData = Array.from(allSymbols.values());
    symbolData.sort((a, b) => a.name.localeCompare(b.name));
    
    console.log(`✅ Извлечено ${symbolData.length} уникальных символов из offers со статусом: ${selectedOfferType.value}`);
    return symbolData;

  } catch (error) {
    console.error('❌ Ошибка загрузки символов из offers:', error);
    return [];
  }
};

// Добавьте в ref секцию
const offerActionLoading = ref(false);

// Обновите функцию acceptOffer в methods
// Обновите функцию acceptOffer в methods
const acceptOffer = async (offer) => {
  try {
    console.log('🔄 Принимаем полученный оффер:', offer.id);
    
    // Проверяем обязательные поля
    if (!offer || !offer.id || !offer.buyer_name || !offer.seller_name) {
      console.error('❌ Неполные данные оффера:', offer);
      showNotification('Неполные данные оффера', 'error');
      return;
    }

    // Проверяем, что оффер действительно предназначен текущему пользователю
    if (offer.seller_name !== currentAccountName.value) {
      console.error('❌ Оффер не предназначен текущему пользователю');
      showNotification('Этот оффер не предназначен вам', 'error');
      return;
    }

    // Проверяем статус оффера
    if (offer.status !== 'pending') {
      console.error('❌ Оффер уже обработан:', offer.status);
      showNotification('Этот оффер уже обработан', 'error');
      return;
    }

    offerActionLoading.value = true;

    // Обновляем статус оффера в базе данных
    const { error: updateError } = await supabase
      .from('offers')
      .update({ 
        status: 'accepted',
        updated_at: new Date().toISOString()
      })
      .eq('id', offer.id)
      .eq('status', 'pending'); // Дополнительная проверка для безопасности

    if (updateError) {
      throw updateError;
    }

    console.log('✅ Оффер принят успешно');

    // Здесь должна быть логика передачи NFT и обработки платежа
    await processAcceptedOffer(offer);

    showNotification('Оффер принят успешно!', 'success');
    
    // Закрываем fullscreen view
    htmlModal.value.show = false;
    
    // Обновляем список офферов
    await loadOffers();

  } catch (error) {
    console.error('❌ Ошибка принятия оффера:', error);
    showNotification(`Ошибка принятия оффера: ${error.message}`, 'error');
  } finally {
    offerActionLoading.value = false;
  }
};

// Обновите функцию processAcceptedOffer
const processAcceptedOffer = async (offer) => {
  try {
    console.log('🔄 Обработка принятого оффера...', offer.id);
    console.log('📊 Данные оффера:', offer);

    // 1. Проверяем, есть ли NFT на маркете у продавца
    const { data: marketItem, error: marketError } = await supabase
      .from('market')
      .select('*')
      .eq('item_id', offer.item_id)
      .eq('seller', currentAccountName.value)
      .single();

    if (marketError || !marketItem) {
      throw new Error('NFT не найдено на маркете у продавца');
    }

    console.log('✅ NFT найдено на маркете:', marketItem);

    // 2. Удаляем NFT с маркета (оно продано)
    const { error: deleteError } = await supabase
      .from('market')
      .delete()
      .eq('item_id', offer.item_id)
      .eq('seller', currentAccountName.value);

    if (deleteError) throw deleteError;

    // 3. Добавляем NFT покупателю в nft_links
    const { data: buyerData, error: buyerError } = await supabase
      .from('users')
      .select('nft_links')
      .eq('name', offer.buyer_name)
      .single();

    if (buyerError) throw buyerError;

    const buyerNfts = buyerData.nft_links || [];
    
    // Создаем объект NFT для покупателя
    const nftForBuyer = {
      url: marketItem.nft_object?.url || '',
      name: getNftDisplayName(marketItem.nft_type, marketItem.nft_object),
      model: marketItem.nft_object?.model || '',
      symbol: marketItem.nft_object?.symbol || '',
      backdrop: marketItem.nft_object?.backdrop || '',
      acquired_at: new Date().toISOString(),
      acquired_from: currentAccountName.value,
      acquired_price: offer.offer_price || offer.price_per_unit,
      item_id: marketItem.item_id
    };

    const updatedBuyerNfts = [...buyerNfts, nftForBuyer];

    // 4. Обновляем балансы
    const offerPrice = offer.offer_price || offer.price_per_unit || 0;
    
    // Получаем текущие балансы
    const { data: buyerBalanceData } = await supabase
      .from('users')
      .select('ton_balance')
      .eq('name', offer.buyer_name)
      .single();

    const { data: sellerBalanceData } = await supabase
      .from('users')
      .select('ton_balance')
      .eq('name', currentAccountName.value)
      .single();

    const currentBuyerBalance = parseFloat(buyerBalanceData?.ton_balance) || 0;
    const currentSellerBalance = parseFloat(sellerBalanceData?.ton_balance) || 0;

    // Расчет комиссии и сумм
    const commission = offerPrice * 0.02; // 2% комиссия
    const sellerAmount = offerPrice - commission;
    
    const newBuyerBalance = currentBuyerBalance - offerPrice;
    const newSellerBalance = currentSellerBalance + sellerAmount;

    // Проверяем баланс покупателя
    if (newBuyerBalance < 0) {
      throw new Error('Недостаточно средств у покупателя');
    }

    console.log('💰 Балансы:', {
      offerPrice,
      commission,
      sellerAmount,
      currentBuyerBalance,
      newBuyerBalance,
      currentSellerBalance,
      newSellerBalance
    });

    // 5. Выполняем все обновления
    const updates = [
      // Обновляем NFT покупателя
      supabase
        .from('users')
        .update({ nft_links: updatedBuyerNfts })
        .eq('name', offer.buyer_name),
      
      // Обновляем баланс покупателя
      supabase
        .from('users')
        .update({ ton_balance: newBuyerBalance })
        .eq('name', offer.buyer_name),
      
      // Обновляем баланс продавца
      supabase
        .from('users')
        .update({ ton_balance: newSellerBalance })
        .eq('name', currentAccountName.value)
    ];

    const results = await Promise.all(updates);
    
    // Проверяем ошибки
    results.forEach((result, index) => {
      if (result.error) {
        throw new Error(`Update ${index} failed: ${result.error.message}`);
      }
    });

    // 6. Записываем активность
    await addActivityRecord({
      user_name: currentAccountName.value,
      operation_type: 'offer_accepted',
      item_id: offer.item_id,
      nft_type: marketItem.nft_type,
      nft_object: marketItem.nft_object,
      html_content: marketItem.html_content,
      price_per_unit: offerPrice,
      currency: offer.currency || 'TON',
      amount: offer.amount || 1,
      total_price: offerPrice * (offer.amount || 1),
      counterparty: offer.buyer_name
    });

    // 7. Также записываем активность для покупателя
    await addActivityRecord({
      user_name: offer.buyer_name,
      operation_type: 'purchase',
      item_id: offer.item_id,
      nft_type: marketItem.nft_type,
      nft_object: marketItem.nft_object,
      html_content: marketItem.html_content,
      price_per_unit: offerPrice,
      currency: offer.currency || 'TON',
      amount: offer.amount || 1,
      total_price: offerPrice * (offer.amount || 1),
      counterparty: currentAccountName.value
    });

    console.log('✅ Оффер полностью обработан');

  } catch (error) {
    console.error('❌ Ошибка обработки оффера:', error);
    throw error;
  }
};

// Также обновите функцию rejectOffer для consistency
const rejectOffer = async (offer) => {
  try {
    console.log('🔄 Отклоняем полученный оффер:', offer.id);
    
    // Проверяем обязательные поля
    if (!offer || !offer.id || !offer.seller_name) {
      console.error('❌ Неполные данные оффера:', offer);
      showNotification('Неполные данные оффера', 'error');
      return;
    }

    // Проверяем, что оффер действительно предназначен текущему пользователю
    if (offer.seller_name !== currentAccountName.value) {
      console.error('❌ Оффер не предназначен текущему пользователю');
      showNotification('Этот оффер не предназначен вам', 'error');
      return;
    }

    offerActionLoading.value = true;

    const { error } = await supabase
      .from('offers')
      .update({ 
        status: 'rejected',
        updated_at: new Date().toISOString()
      })
      .eq('id', offer.id)
      .eq('status', 'pending');

    if (error) throw error;

    console.log('✅ Оффер отклонен');
    showNotification('Оффер отклонен', 'success');
    
    // Закрываем fullscreen view
    htmlModal.value.show = false;
    
    // Обновляем список офферов
    await loadOffers();

  } catch (error) {
    console.error('❌ Ошибка отклонения оффера:', error);
    showNotification(`Ошибка отклонения оффера: ${error.message}`, 'error');
  } finally {
    offerActionLoading.value = false;
  }
};



// Вспомогательные функции
const transferNftToBuyer = async (buyerName, nftData) => {
  try {
    // Получаем текущие NFT покупателя
    const { data: buyerData, error: fetchError } = await supabase
      .from('users')
      .select('nft_links')
      .eq('name', buyerName)
      .single();

    if (fetchError) throw fetchError;
    if (!buyerData) throw new Error(`Покупатель ${buyerName} не найден`);

    const currentLinks = buyerData.nft_links || [];
    
    // Проверяем, нет ли уже такого NFT
    const nftExists = currentLinks.some(item => {
      const itemUrl = typeof item === 'object' ? item.url : item;
      return itemUrl === nftData.url;
    });

    if (!nftExists) {
      // Добавляем NFT в коллекцию покупателя
      const nftToAdd = {
        url: nftData.url,
        name: nftData.name || 'NFT',
        model: nftData.model || '',
        symbol: nftData.symbol || '',
        backdrop: nftData.backdrop || '',
        acquired_at: new Date().toISOString()
      };

      const updatedLinks = [...currentLinks, nftToAdd];
      
      const { error: updateError } = await supabase
        .from('users')
        .update({ nft_links: updatedLinks })
        .eq('name', buyerName);

      if (updateError) throw updateError;
    }

    console.log(`✅ NFT передан покупателю ${buyerName}`);
    return true;
    
  } catch (error) {
    console.error('❌ Ошибка передачи NFT покупателю:', error);
    throw error;
  }
};

const transferFundsToSeller = async (sellerName, amount) => {
  try {
    // Получаем текущий баланс продавца
    const { data: sellerData, error: fetchError } = await supabase
      .from('users')
      .select('ton_balance')
      .eq('name', sellerName)
      .single();

    if (fetchError) throw fetchError;
    if (!sellerData) throw new Error(`Продавец ${sellerName} не найден`);

    const currentBalance = parseFloat(sellerData.ton_balance) || 0;
    const newBalance = currentBalance + amount;

    // Обновляем баланс продавца
    const { error: updateError } = await supabase
      .from('users')
      .update({ ton_balance: newBalance })
      .eq('name', sellerName);

    if (updateError) throw updateError;

    console.log(`💰 Продавец ${sellerName} получил ${amount} TON`);
    return true;
    
  } catch (error) {
    console.error('❌ Ошибка перевода средств продавцу:', error);
    throw error;
  }
};

const deductFundsFromBuyer = async (buyerName, amount) => {
  try {
    // Получаем текущий баланс покупателя
    const { data: buyerData, error: fetchError } = await supabase
      .from('users')
      .select('ton_balance')
      .eq('name', buyerName)
      .single();

    if (fetchError) throw fetchError;
    if (!buyerData) throw new Error(`Покупатель ${buyerName} не найден`);

    const currentBalance = parseFloat(buyerData.ton_balance) || 0;
    
    // Проверяем достаточность средств
    if (currentBalance < amount) {
      throw new Error(`Недостаточно средств у покупателя: ${currentBalance} < ${amount}`);
    }

    const newBalance = currentBalance - amount;

    // Обновляем баланс покупателя
    const { error: updateError } = await supabase
      .from('users')
      .update({ ton_balance: newBalance })
      .eq('name', buyerName);

    if (updateError) throw updateError;

    console.log(`💰 С покупателя ${buyerName} списано ${amount} TON`);
    return true;
    
  } catch (error) {
    console.error('❌ Ошибка списания средств с покупателя:', error);
    throw error;
  }
};

const refundOfferToBuyer = async (offer) => {
  try {
    const { data: buyerData, error: fetchError } = await supabase
      .from('users')
      .select('ton_balance')
      .eq('name', offer.buyer_name)
      .single();

    if (fetchError) throw fetchError;
    if (!buyerData) throw new Error(`Покупатель ${offer.buyer_name} не найден`);

    const currentBalance = parseFloat(buyerData.ton_balance) || 0;
    const newBalance = currentBalance + offer.offer_price;

    const { error: updateError } = await supabase
      .from('users')
      .update({ ton_balance: newBalance })
      .eq('name', offer.buyer_name);

    if (updateError) throw updateError;

    console.log(`✅ Средства ${offer.offer_price} TON возвращены покупателю ${offer.buyer_name}`);
    return true;
    
  } catch (error) {
    console.error('❌ Ошибка возврата средств покупателю:', error);
    throw error;
  }
};

const deleteMarketItem = async (itemId) => {
  try {
    const { error } = await supabase
      .from('market')
      .delete()
      .eq('item_id', itemId);

    if (error) throw error;

    console.log(`✅ Объявление ${itemId} удалено с рынка`);
    return true;
    
  } catch (error) {
    console.error('❌ Ошибка удаления объявления:', error);
    // Не блокируем выполнение из-за ошибки удаления
    return false;
  }
};

const updateOfferStatus = async (offerId, status) => {
  try {
    // Используем только существующие колонки
    const updateData = {
      status: status,
      updated_at: new Date().toISOString()
    };

    const { error } = await supabase
      .from('offers')
      .update(updateData)
      .eq('id', offerId);

    if (error) throw error;

    console.log(`✅ Статус оффера ${offerId} обновлен на: ${status}`);
    return true;
    
  } catch (error) {
    console.error('❌ Ошибка обновления статуса оффера:', error);
    throw error;
  }
};

const recordOfferAcceptActivity = async (offer) => {
  try {
    const activityData = {
      user_name: offer.seller_name,
      operation_type: 'offer_accepted',
      item_id: offer.item_id,
      nft_type: offer.nft_type || 'unknown',
      nft_object: offer.nft_data || {},
      price_per_unit: offer.offer_price,
      currency: 'TON',
      amount: 1,
      total_price: offer.offer_price,
      counterparty: offer.buyer_name,
      status: 'accepted',
      created_at: new Date().toISOString()
    };

    const { error } = await supabase
      .from('activity_history')
      .insert(activityData);

    if (error) throw error;

    console.log('✅ Активность принятия оффера записана');
    return true;
    
  } catch (error) {
    console.error('❌ Ошибка записи активности:', error);
    // Не блокируем выполнение из-за ошибки записи активности
    return false;
  }
};

const recordOfferRejectActivity = async (offer) => {
  try {
    const activityData = {
      user_name: offer.seller_name,
      operation_type: 'offer_rejected',
      item_id: offer.item_id,
      nft_type: offer.nft_type || 'unknown',
      nft_object: offer.nft_data || {},
      price_per_unit: offer.offer_price,
      currency: 'TON',
      amount: 1,
      total_price: offer.offer_price,
      counterparty: offer.buyer_name,
      status: 'rejected',
      created_at: new Date().toISOString()
    };

    const { error } = await supabase
      .from('activity_history')
      .insert(activityData);

    if (error) throw error;

    console.log('✅ Активность отклонения оффера записана');
    return true;
    
  } catch (error) {
    console.error('❌ Ошибка записи активности:', error);
    return false;
  }
};
// Обновленная функция для получения отфильтрованных символов
const getFilteredSymbols = () => {
  const query = searchQuery.value ? searchQuery.value.toLowerCase() : '';
  
  console.log(`🔍 FILTERED SYMBOLS: query="${query}", offerType="${selectedOfferType.value}"`);
  
  // Берем символы из offers с учетом статуса
  const allSymbolsFromOffers = getAllSymbolsFromFilteredOffers();
  
  if (allSymbolsFromOffers.length === 0) {
    console.log('❌ Нет символов в offers с текущим фильтром статуса');
    return [];
  }
  
  const filtered = allSymbolsFromOffers
    .filter(symbol => {
      const matchesSearch = query === '' || 
                           symbol.name.toLowerCase().includes(query) ||
                           (symbol.rarityText && symbol.rarityText.toLowerCase().includes(query));
      return matchesSearch;
    })
    .map(symbol => {
      return {
        name: symbol.name,
        value: normalizeSymbolName(symbol.name),
        htmlContent: symbol.htmlContent,
        percentage: symbol.percentage || 0,
        rarityText: symbol.rarityText || 'N/A',
        rarityClass: symbol.rarityClass || 'common'
      };
    })
    .sort((a, b) => a.percentage - b.percentage);

  console.log(`📊 RESULT: ${filtered.length} symbols для статуса "${selectedOfferType.value}"`);
  return filtered;
};






// Вспомогательная функция для получения процента backdrop
const getBackdropPercentage = (backdropId) => {
  const backdropData = availableBackdropOptions.value.find(
    opt => opt.id === backdropId.toLowerCase().trim()
  );
  return backdropData?.percentage || 0;
};

// Вспомогательная функция для получения текста редкости
const getRarityText = (percentage) => {
  if (percentage === 0) return 'N/A';
  return `${percentage}%`;
};

// Вспомогательная функция для получения класса редкости
const getRarityClass = (percentage) => {
  if (percentage < 1) return 'mythic';
  if (percentage < 5) return 'legendary';
  if (percentage < 15) return 'epic';
  if (percentage < 30) return 'rare';
  return 'common';
};
const endModalDrag = (modalType) => {
  isDraggingModal.value = false;
  dragStartY.value = 0;
  dragCurrentY.value = 0;
};

const closeModal = (modalType) => {
  switch (modalType) {
    case 'buy':
      buyModal.value.show = false;
      break;
    case 'cancelSale':
      cancelSaleModal.value.show = false;
      break;
    case 'transfer':
      transferModal.value.show = false;
      break;
    case 'editPrice':
      editPriceModal.value.show = false;
      break;
    case 'sell':
      sellModal.value.show = false;
      break;
  }
};


    // В секции методов добавьте:
const getNftDisplayNameFromUrl = (url) => {
  try {
    const match = url.match(/\/nft\/([^-]+)/);
    if (match && match[1]) {
      const name = match[1];
      // Преобразуем camelCase в нормальное название
      const displayName = name.replace(/([A-Z])/g, ' $1').trim();
      
      // Маппинг для правильного отображения
      const displayMapping = {
        'deskcalendar': 'Desk Calendar',
        'bdaycandle': 'B-Day Candle',
        'easteregg': 'Easter Egg',
        'tophat': 'Top Hat',
        'plushpepe': 'Plush Pepe',
        'jackinthebox': 'Jack-in-the-Box',
        'nekohelmet': 'Neko Helmet',
        'lovepotion': 'Love Potion',
        'toybear': 'Toy Bear',
        'diamondring': 'Diamond Ring',
        'lootbag': 'Loot Bag',
        'lunarsnake': 'Lunar Snake',
        'tamagadget': 'Tama Gadget',
        'candycane': 'Candy Cane',
        'cookieheart': 'Cookie Heart',
        'partysparkler': 'Party Sparkler',
        'jinglebells': 'Jingle Bells',
        'gingercookie': 'Ginger Cookie',
        'winterwreath': 'Winter Wreath',
        'santahat': 'Santa Hat',
        'snowglobe': 'Snow Globe',
        'snowmittens': 'Snow Mittens',
        'sleighbell': 'Sleigh Bell',
        'jesterhat': 'Jester Hat',
        'starnotepad': 'Star Notepad',
        'bunnymuffin': 'Bunny Muffin',
        'swisswatch': 'Swiss Watch',
        'signetring': 'Signet Ring',
        'genielamp': 'Genie Lamp',
        'astralshard': 'Astral Shard',
        'preciouspeach': 'Precious Peach',
        'spicedwine': 'Spiced Wine',
        'jellybunny': 'Jelly Bunny',
        'hangingstar': 'Hanging Star',
        'durovscap': 'Durov\'s Cap',
        'lovecandle': 'Love Candle',
        'perfumebottle': 'Perfume Bottle',
        'minioscar': 'Mini Oscar',
        'eternalrose': 'Eternal Rose',
        'berrybox': 'Berry Box',
        'vintagecigar': 'Vintage Cigar',
        'recordplayer': 'Record Player',
        'magicpotion': 'Magic Potion',
        'electricskull': 'Electric Skull',
        'kissedfrog': 'Kissed Frog',
        'hypnolollipop': 'Hypno Lollipop',
        'hexpot': 'Hex Pot',
        'evileye': 'Evil Eye',
        'iongem': 'Ion Gem',
        'sharptongue': 'Sharp Tongue',
        'madpumpkin': 'Mad Pumpkin',
        'trappedheart': 'Trapped Heart',
        'skullflower': 'Skull Flower',
        'crystalball': 'Crystal Ball',
        'flyingbroom': 'Flying Broom',
        'voodoodoll': 'Voodoo Doll',
        'scaredcat': 'Scared Cat',
        'witchhat': 'Witch Hat',
        'eternalcandle': 'Eternal Candle',
        'spyagaric': 'Spy Agaric',
        'lolpop': 'Lol Pop',
        'sakuraflower': 'Sakura Flower',
        'homemadecake': 'Homemade Cake'
      };
      
      return displayMapping[name.toLowerCase()] || displayName;
    }
    return 'Unknown NFT';
  } catch (error) {
    console.error('Error extracting NFT name from URL:', error);
    return 'Unknown NFT';
  }
};



const symbolHtmlCache = ref({});


// Вспомогательная функция для ошибок
const createErrorHtml = (message) => {
  return `
    <div style="width: 100%; height: 100%; background: #f0f0f0; display: flex; align-items: center; justify-content: center;">
      <span style="color: #666; font-size: 12px;">${message}</span>
    </div>
  `;
};

// Функция для загрузки всех символов с маркета
const loadAllMarketSymbolsWithHtml = async () => {
  try {
    console.log('🔄 Загрузка всех символов с маркета с HTML анимациями...');
    
    const allSymbols = new Set();
    
    // Собираем все уникальные символы
    marketItems.value.forEach(item => {
      const symbol = extractSymbolFromNft(item);
      if (symbol && symbol.trim() !== '') {
        allSymbols.add(symbol);
      }
    });
    
    const symbolsArray = Array.from(allSymbols);
    console.log(`📊 Найдено символов: ${symbolsArray.length}`);
    
    // Генерируем HTML для каждого символа
    symbolsArray.forEach(symbol => {
      if (!symbolHtmlCache.value[symbol]) {
        symbolHtmlCache.value[symbol] = generateSymbolHtml(symbol);
      }
    });
    
    console.log('✅ HTML анимации символов сгенерированы', symbolHtmlCache.value);
    
  } catch (error) {
    console.error('❌ Ошибка загрузки символов с маркета:', error);
  }
};

// В mounted добавьте загрузку символов
onMounted(async () => {
  // ... существующий код ...
  
  // Загружаем символы после загрузки marketItems
  if (marketItems.value.length > 0) {
    await loadAllMarketSymbolsWithHtml();
  }
  
  // Следим за изменениями marketItems
  watch(() => marketItems.value, async (newItems) => {
    if (newItems.length > 0) {
      await loadAllMarketSymbolsWithHtml();
    }
  }, { immediate: true });
});

// Функция для принудительной перезагрузки всех HTML анимаций
const reloadAllSymbolHtml = async () => {
  console.log('🔄 Принудительная перезагрузка всех HTML анимаций символов...');
  symbolHtmlCache.value = {};
  await loadAllMarketSymbolsWithHtml();
  forceUpdate.value++;
};



const getRandomModelForNft = async (nftName) => {
  try {
    console.log(`🔍 Загрузка моделей для NFT: "${nftName}"`);
    
    // Используем оригинальное имя для запроса в БД
    const dbColumnName = `"${nftName}"`;
    
    const { data, error } = await supabase
      .from('nft')
      .select(dbColumnName)
      .not(dbColumnName, 'is', null)
      .limit(1);

    if (error) {
      console.error(`❌ Ошибка БД для "${nftName}":`, error);
      return 'Classic';
    }

    if (!data || data.length === 0) {
      console.warn(`❌ Модели не найдены для: "${nftName}"`);
      return 'Classic';
    }

    const modelsArray = data[0][nftName];
    
    if (!Array.isArray(modelsArray) || modelsArray.length === 0) {
      console.warn(`❌ Массив моделей пуст для: "${nftName}"`);
      return 'Classic';
    }

    // Выбираем случайную модель
    const randomIndex = Math.floor(Math.random() * modelsArray.length);
    const randomModelString = modelsArray[randomIndex];
    
    // Извлекаем название модели (до символа "—")
    const modelName = randomModelString.split(' — ')[0]?.trim() || 'Classic';
    
    console.log(`✅ Случайная модель для "${nftName}": ${modelName}`);
    return modelName;

  } catch (error) {
    console.error(`❌ Критическая ошибка для "${nftName}":`, error);
    return 'Classic';
  }
};
const openHtmlModalForUnlisted = (nftData) => {
  initiateSellFromUnlisted(nftData);
  try {
    
    const modelData = extractValueAndPercentage(model);
    const symbolData = extractValueAndPercentage(symbol);
    const backdropData = extractValueAndPercentage(backdrop);

    htmlModal.value = {
      show: true,
      htmlContent: generateNftHtmlForFullscreen(nftData),
      title: getNftDisplayNameFromUrl(nftData.url),
      model: modelData.name,
      modelPercentage: modelData.percentage,
      symbol: symbolData.name,
      symbolPercentage: symbolData.percentage,
      backdrop: backdropData.name,
      backdropPercentage: backdropData.percentage,
      telegramLink: nftData.url,
      item: { 
        nft_object: nftData, 
        is_unlisted: true,
        nft_type: extractNftNameFromUrl(nftData.url)
      },
      isUnlisted: true,
      actionType: 'sell'
    };

    console.log('Unlisted NFT данные:', {
      model: modelData,
      symbol: symbolData,
      backdrop: backdropData
    });

  } catch (error) {
    console.error('Ошибка открытия модального окна для unlisted NFT:', error);
    htmlModal.value = {
      show: true,
      htmlContent: generateNftHtmlForFullscreen(nftData),
      title: getNftDisplayNameFromUrl(nftData.url),
      model: 'Ошибка загрузки',
      modelPercentage: '',
      symbol: 'Ошибка загрузки',
      symbolPercentage: '',
      backdrop: 'Ошибка загрузки',
      backdropPercentage: '',
      item: { nft_object: nftData, is_unlisted: true },
      isUnlisted: true,
      actionType: 'sell'
    };
  }
};






    
    const testSymbolExtraction = async () => {
  try {
    console.log('=== ТЕСТИРОВАНИЕ ИЗВЛЕЧЕНИЯ СИМВОЛОВ ===');
    
    const { data: testItems, error } = await supabase
      .from('market')
      .select('id, nft_object, symbol, nft_metadata, html_content')
      .limit(10);
    
    if (error) {
      console.error('Ошибка загрузки тестовых данных:', error);
      return;
    }
    
    testItems.forEach(item => {
      const extractedSymbol = extractSymbolFromNft(item);
      const normalizedSymbol = normalizeSymbolName(extractedSymbol || '');
      
      console.log('---');
      console.log('Item ID:', item.id);
      console.log('Raw nft_object:', item.nft_object);
      console.log('Raw symbol field:', item.symbol);
      console.log('Raw nft_metadata:', item.nft_metadata);
      console.log('Извлеченный символ:', extractedSymbol);
      console.log('Нормализованный символ:', normalizedSymbol);
    });
    
    console.log('=== ТЕСТИРОВАНИЕ ЗАВЕРШЕНО ===');
    
  } catch (error) {
    console.error('Ошибка тестирования:', error);
  }
};

// Вызовите для тестирования при необходимости
// testSymbolExtraction();



    const scrollToButton = (button) => {
      const container = categoriesContainer.value;
      const buttonRect = button.getBoundingClientRect();
      const containerRect = container.getBoundingClientRect();
      
      const scrollTo = button.offsetLeft - (container.offsetWidth / 2) + (button.offsetWidth / 2);
      
      container.scrollTo({
        left: scrollTo,
        behavior: 'smooth'
      });
    };
  


// Добавьте эти функции в methods
const getSelectedModelsInGroup = (nftType) => {
  try {
    const models = getModelsForNftSortedByRarity(nftType);
    return models.filter(model => 
      isOptionSelected('model', model.name)
    );
  } catch (error) {
    console.error('Error getting selected models in group:', error);
    return [];
  }
};

const getUnselectedModelsInGroup = (nftType) => {
  try {
    const models = getModelsForNftSortedByRarity(nftType);
    return models.filter(model => 
      !isOptionSelected('model', model.name)
    );
  } catch (error) {
    console.error('Error getting unselected models in group:', error);
    return [];
  }
};

const getGroupedModelOptions = () => {
  const grouped = {};
  
  selectedFilters.value.nft.forEach(nftType => {
    if (nftModelsCache.value[nftType]) {
      grouped[nftType] = getModelsForNftSortedByRarity(nftType);
    }
  });
  
  return grouped;
};
// Функция для проверки floor prices
const debugFloorPrices = () => {
  console.log('=== ДЕБАГ FLOOR PRICES ===');
  
  // Проверяем несколько моделей
  const testModels = ['Choco Bunny', 'Plum Peach', 'Pepe Plans'];
  testModels.forEach(model => {
    const price = getFloorPrice('model', model);
    console.log(`Модель "${model}": ${price} TON`);
  });
  
  // Проверяем несколько символов
  const testSymbols = ['Red Apple', 'Blue Moon', 'Golden Star'];
  testSymbols.forEach(symbol => {
    const price = getFloorPrice('symbol', symbol);
    console.log(`Символ "${symbol}": ${price} TON`);
  });
  
  // Проверяем несколько фонов
  const testBackdrops = ['Black', 'Aquamarine', 'Azure Blue'];
  testBackdrops.forEach(backdrop => {
    const price = getFloorPrice('backdrop', backdrop);
    console.log(`Фон "${backdrop}": ${price} TON`);
  });
  
  console.log('==========================');
};
const toggleCartFromFullscreen = () => {
  if (!htmlModal.value.item || htmlModal.value.isUnlisted) return;
  
  const item = htmlModal.value.item;
  
  if (isInCart(item.id)) {
    removeFromCart(item.id);
  } else {
    addToCart(item);
  }
  
  // Обновляем состояние кнопки
  htmlModal.value = { ...htmlModal.value };
};
// Вызовите эту функцию в mounted или по кнопке для тестирования



    onMounted(() => {
      const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
      if (isIOS) {
        const style = document.createElement('style');
        style.textContent = `
          .filter-categories-container {
            -webkit-overflow-scrolling: touch !important;
          }
        `;
        document.head.appendChild(style);
      }
    });

    const htmlModal = ref({
      show: false,
      htmlContent: '',
      title: '',
      seller: '',
      price: 0,
      currency: 'AMHSL',
      item: null,
      offset: 0,
      startY: 0,
      isDragging: false
    });

    function openTelegramLink(url) {
      window.open(url, '_blank');
    }

    const htmlNfts = ref([]);

    const openHtmlModal = async (item) => {
  try {
    const nftId = extractNftIdFromHtml(item.html_content);
    const telegramLink = nftId ? `https://t.me/nft/${nftId}` : null;
    
    console.log('nft_object raw:', item.nft_object);

    // Парсим nft_object для получения model, symbol, backdrop
    let modelName = 'Не указано';
    let modelPercentage = '';
    let symbolName = 'Не указано';
    let symbolPercentage = '';
    let backdropName = 'Не указано';
    let backdropPercentage = '';
    
    try {
      if (item.nft_object) {
        console.log('nft_object exists, type:', typeof item.nft_object);
        
        let nftObj;
        if (typeof item.nft_object === 'string') {
          try {
            nftObj = JSON.parse(item.nft_object);
            console.log('Parsed nft_object:', nftObj);
          } catch (parseError) {
            console.error('JSON parse error:', parseError);
            try {
              nftObj = JSON.parse(item.nft_object.replace(/'/g, '"'));
            } catch (e) {
              console.error('Second parse attempt failed:', e);
            }
          }
        } else {
          nftObj = item.nft_object;
        }
        
        if (nftObj) {
          // Разделяем модель и процент
          if (nftObj.model) {
            const modelParts = nftObj.model.split(' ');
            if (modelParts.length > 1) {
              modelPercentage = modelParts.pop();
              modelName = modelParts.join(' ');
            } else {
              modelName = nftObj.model;
            }
          }
          
          // Разделяем символ и процент
          if (nftObj.symbol) {
            const symbolParts = nftObj.symbol.split(' ');
            if (symbolParts.length > 1) {
              symbolPercentage = symbolParts.pop();
              symbolName = symbolParts.join(' ');
            } else {
              symbolName = nftObj.symbol;
            }
          }
          
          // Разделяем backdrop и процент
          if (nftObj.backdrop) {
            const backdropParts = nftObj.backdrop.split(' ');
            if (backdropParts.length > 1) {
              backdropPercentage = backdropParts.pop();
              backdropName = backdropParts.join(' ');
            } else {
              backdropName = nftObj.backdrop;
            }
          }
          
          console.log('Extracted values:', {
            modelName, 
            modelPercentage, 
            symbolName, 
            symbolPercentage, 
            backdropName, 
            backdropPercentage
          });
        }
      }
    } catch (parseError) {
      console.error('Ошибка парсинга nft_object:', parseError);
    }

    htmlModal.value = {
      show: true,
      htmlContent: item.html_content,
      title: getNftDisplayName(item.nft_type),
      model: modelName,
      modelPercentage: modelPercentage,
      symbol: symbolName,
      symbolPercentage: symbolPercentage,
      backdrop: backdropName,
      backdropPercentage: backdropPercentage,
      telegramLink,
      item: item
    };

  } catch (err) {
    console.error('Ошибка при открытии модального окна:', err);
    htmlModal.value = {
      show: true,
      htmlContent: item.html_content,
      title: getNftDisplayName(item.nft_type),
      model: 'Ошибка загрузки',
      modelPercentage: '',
      symbol: 'Ошибка загрузки',
      symbolPercentage: '',
      backdrop: 'Ошибка загрузки',
      backdropPercentage: '',
      telegramLink: null,
      item: item
    };
  }
};
const offerModal = ref({
  show: false,
  item: null,
  currentPrice: 0,
  offerPrice: '',
  loading: false,
  priceError: ''
});

const openOfferModal = (item) => {
  offerModal.value = {
    show: true,
    item: item,
    currentPrice: item.price_per_unit,
    offerPrice: '',
    loading: false,
    priceError: ''
  };
};
const sendOffer = async () => {
  try {
    const { item, offerPrice, currentPrice } = offerModal.value;
    
    // Валидация цены
    if (!offerPrice || offerPrice <= 0) {
      offerModal.value.priceError = 'Please enter a valid offer price';
      return;
    }
    
    if (offerPrice > currentPrice) {
      offerModal.value.priceError = 'Offer cannot be higher than current price';
      return;
    }
    
    offerModal.value.loading = true;
    offerModal.value.priceError = '';
    
    // Получаем информацию о продавце
    const { data: sellerData, error: sellerError } = await supabase
      .from('users')
      .select('telegram, name')
      .eq('name', item.seller)
      .single();
    
    if (sellerError) {
      throw new Error('Could not find seller information');
    }
    
    if (!sellerData.telegram) {
      throw new Error('Seller does not have Telegram account linked');
    }
    
    // Получаем информацию о покупателе
    const { data: buyerData, error: buyerError } = await supabase
      .from('users')
      .select('name')
      .eq('name', currentAccountName.value)
      .single();
    
    if (buyerError) {
      throw new Error('Could not find your account information');
    }
    
    // Подготовка данных для отправки в Telegram бот
    const nftId = extractNftId(item.nft_object);
    const nftName = getNftDisplayName(item.nft_type, item.nft_object);
    const savings = (currentPrice - offerPrice).toFixed(1);
    
    const offerData = {
      seller_telegram_id: sellerData.telegram,
      seller_name: sellerData.name,
      buyer_name: buyerData.name,
      nft_name: nftName,
      nft_id: nftId,
      current_price: parseFloat(currentPrice),
      offer_price: parseFloat(offerPrice),
      item_id: item.item_id || item.id,
      nft_data: item.nft_object || {}
    };
    
    // Сохраняем предложение в базе данных
    const { error: dbError } = await supabase
      .from('offers')
      .insert([{
        item_id: item.item_id || item.id,
        seller_name: item.seller,
        buyer_name: currentAccountName.value,
        current_price: parseFloat(currentPrice),
        offer_price: parseFloat(offerPrice),
        nft_data: item.nft_object || {},
        nft_name: nftName,
        nft_id: nftId,
        status: 'pending',
        created_at: new Date().toISOString()
      }]);
    
    if (dbError) throw dbError;
    
    // Формируем сообщение для Telegram
    const messageText = `🎯 *Новое предложение цены!*

*${nftName}*
🏷 ID: #${nftId}

💰 Текущая цена: ${currentPrice} TON
💵 Предложенная цена: ${offerPrice} TON
👤 От: ${buyerData.name}

✨ Экономия: ${savings} TON

Вы хотите принять это предложение?`;
    
    // Отправляем предложение в Telegram бот
    const telegramResponse = await fetch('https://api.telegram.org/bot8181445961:AAFYWVT-x7IVGWrVa1-n3X_dOTDM9fnhxbw/sendMessage', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        chat_id: sellerData.telegram,
        text: messageText,
        parse_mode: 'Markdown',
        reply_markup: {
          inline_keyboard: [
            [
              { 
                text: '✅ Принять предложение', 
                callback_data: `accept_offer:${offerData.item_id}` 
              },
              { 
                text: '❌ Отклонить предложение', 
                callback_data: `decline_offer:${offerData.item_id}` 
              }
            ],
            [
              { 
                text: '👀 Посмотреть товар', 
                url: `https://sivch-app-2.vercel.app/shop/${offerData.item_id}` 
              }
            ]
          ]
        }
      })
    });
    
    if (!telegramResponse.ok) {
      const errorData = await telegramResponse.json();
      console.error('Telegram API error:', errorData);
      
      // Если не удалось отправить в Telegram, удаляем предложение из базы
      await supabase
        .from('offers')
        .delete()
        .eq('item_id', item.item_id || item.id);
      
      throw new Error('Failed to send offer notification to seller');
    }
    
    showNotification('Offer sent successfully! The seller has been notified.', 'success');
    offerModal.value.show = false;
    
  } catch (error) {
    console.error('Error sending offer:', error);
    showNotification(`Error sending offer: ${error.message}`, 'error');
  } finally {
    offerModal.value.loading = false;
  }
};

const openOfferFullscreen = (offer) => {
  try {
    console.group('🔍 ОТКРЫТИЕ ОФФЕРА В FULLSCREEN');
    console.log('📊 Данные оффера:', {
      id: offer.id,
      status: offer.status,
      seller_name: offer.seller_name,
      buyer_name: offer.buyer_name,
      currentUser: currentAccountName.value
    });
    
    console.log('✅ Условия для кнопок:', {
      isPending: offer.status === 'pending',
      isSeller: offer.seller_name === currentAccountName.value,
      isNotBuyer: offer.buyer_name !== currentAccountName.value,
      shouldShowButtons: offer.status === 'pending' && 
                         offer.seller_name === currentAccountName.value && 
                         offer.buyer_name !== currentAccountName.value
    });

    // Создаем объект item с полными данными для info-container
    const item = {
      id: offer.id,
      item_id: offer.item_id || `offer-${offer.id}`,
      nft_type: offer.nft_type,
      nft_object: offer.nft_object || offer.nft_data,
      html_content: offer.html_content,
      seller: offer.seller_name,
      price_per_unit: offer.offer_price || offer.original_price,
      currency: offer.currency || 'TON',
      amount: offer.amount || 1,
      is_unlisted: false,
      // Сохраняем оригинальные поля оффера для кнопок
      status: offer.status,
      seller_name: offer.seller_name,
      buyer_name: offer.buyer_name
    };

    // Извлекаем данные для info-container
    const extractValueAndPercentage = (value) => {
      if (!value) return { name: 'Не указано', percentage: '' };
      
      try {
        const parts = value.split(' ');
        if (parts.length > 1 && parts[parts.length - 1].includes('%')) {
          const percentage = parts.pop();
          return { name: parts.join(' '), percentage };
        }
        return { name: value, percentage: '' };
      } catch (e) {
        return { name: value, percentage: '' };
      }
    };

    let modelData = { name: 'Не указано', percentage: '' };
    let symbolData = { name: 'Не указано', percentage: '' };
    let backdropData = { name: 'Не указано', percentage: '' };
    
    try {
      if (item.nft_object) {
        const nftObj = typeof item.nft_object === 'string' 
          ? JSON.parse(item.nft_object) 
          : item.nft_object;
        
        modelData = extractValueAndPercentage(nftObj.model);
        symbolData = extractValueAndPercentage(nftObj.symbol);
        backdropData = extractValueAndPercentage(nftObj.backdrop);
      }
    } catch (parseError) {
      console.error('Ошибка парсинга nft_object:', parseError);
    }

    // Генерируем HTML контент для оффера
    let htmlContent = '';
    try {
      htmlContent = generateNftHtmlForFullscreen(item.nft_object || item);
    } catch (htmlError) {
      console.error('Ошибка генерации HTML:', htmlError);
      htmlContent = `
        <div style="width: 100%; height: 100%; background: #f0f0f0; display: flex; align-items: center; justify-content: center;">
          <div style="text-align: center;">
            <h3>Error loading NFT</h3>
            <p>Unable to display content</p>
          </div>
        </div>
      `;
    }

    // Получаем Telegram ссылку
    let telegramLink = null;
    try {
      const url = item.url || (item.nft_object && item.nft_object.url);
      const fullNftName = extractFullNftName(url);
      telegramLink = fullNftName ? `https://t.me/nft/${fullNftName}` : null;
    } catch (urlError) {
      console.warn('Ошибка извлечения URL:', urlError);
    }

    htmlModal.value = {
      show: true,
      htmlContent: htmlContent,
      title: getNftDisplayName(item.nft_type, item.nft_object) || 'NFT',
      model: modelData.name,
      modelPercentage: modelData.percentage,
      symbol: symbolData.name,
      symbolPercentage: symbolData.percentage,
      backdrop: backdropData.name,
      backdropPercentage: backdropData.percentage,
      telegramLink: telegramLink,
      item: item, // Используем созданный объект item с полными данными
      isUnlisted: false
    };

    console.log('✅ Fullscreen открыт для оффера с полными данными');
    console.groupEnd();
    
  } catch (err) {
    console.error('❌ Ошибка открытия оффера в fullscreen:', err);
  }
};
// Новая функция для офферов без изменения маршрута
const openFullscreenViewForOffer = (item) => {
  try {
    console.log('🎯 Открываем fullscreen view для оффера (без маршрута):', item.item_id);
    
    // Извлекаем данные для отображения
    let fullNftName = null;
    let telegramLink = null;
    
    try {
      const url = item.url || (item.nft_object && item.nft_object.url);
      fullNftName = extractFullNftName(url);
      telegramLink = fullNftName ? `https://t.me/nft/${fullNftName}` : null;
    } catch (urlError) {
      console.warn('Ошибка извлечения URL:', urlError);
    }

    // Функция для извлечения значения и процента
    const extractValueAndPercentage = (value) => {
      if (!value) return { name: 'Не указано', percentage: '' };
      
      try {
        const parts = value.split(' ');
        if (parts.length > 1 && parts[parts.length - 1].includes('%')) {
          const percentage = parts.pop();
          return { name: parts.join(' '), percentage };
        }
        return { name: value, percentage: '' };
      } catch (e) {
        return { name: value, percentage: '' };
      }
    };

    let modelData = { name: 'Не указано', percentage: '' };
    let symbolData = { name: 'Не указано', percentage: '' };
    let backdropData = { name: 'Не указано', percentage: '' };
    
    try {
      if (item.nft_object) {
        const nftObj = typeof item.nft_object === 'string' 
          ? JSON.parse(item.nft_object) 
          : item.nft_object;
        
        modelData = extractValueAndPercentage(nftObj.model);
        symbolData = extractValueAndPercentage(nftObj.symbol);
        backdropData = extractValueAndPercentage(nftObj.backdrop);
      }
    } catch (parseError) {
      console.error('Ошибка парсинга nft_object:', parseError);
    }

    // Генерируем HTML контент
    let htmlContent = '';
    try {
      htmlContent = generateNftHtmlForFullscreen(item.nft_object || item);
    } catch (htmlError) {
      console.error('Ошибка генерации HTML:', htmlError);
      htmlContent = `
        <div style="width: 100%; height: 100%; background: #f0f0f0; display: flex; align-items: center; justify-content: center;">
          <div style="text-align: center;">
            <h3>Error loading NFT</h3>
            <p>Unable to display content</p>
          </div>
        </div>
      `;
    }

    // Определяем тип действия
    let actionType = 'sell';
    if (item.is_unlisted) {
      if (item.nft_object && item.nft_object.url) {
        actionType = 'send';
      }
    }

    // Открываем модальное окно БЕЗ изменения маршрута
    htmlModal.value = {
      show: true,
      htmlContent: htmlContent,
      title: getNftDisplayName(item.nft_type, item.nft_object) || 'NFT',
      model: modelData.name,
      modelPercentage: modelData.percentage,
      symbol: symbolData.name,
      symbolPercentage: symbolData.percentage,
      backdrop: backdropData.name,
      backdropPercentage: backdropData.percentage,
      telegramLink,
      item: item,
      isUnlisted: item.is_unlisted || false,
      actionType: actionType
    };

    console.log('✅ Fullscreen view для оффера успешно открыт (без изменения маршрута)');

  } catch (err) {
    console.error('❌ Критическая ошибка при открытии полноэкранного просмотра оффера:', err);
    
    // Fallback
    htmlModal.value = {
      show: true,
      htmlContent: `
        <div style="width: 100%; height: 100%; background: #f0f0f0; display: flex; align-items: center; justify-content: center;">
          <div style="text-align: center;">
            <h3>Error loading NFT</h3>
            <p>Click to retry</p>
          </div>
        </div>
      `,
      title: 'NFT',
      model: 'Ошибка загрузки',
      modelPercentage: '',
      symbol: 'Ошибка загрузки',
      symbolPercentage: '',
      backdrop: 'Ошибка загрузки',
      backdropPercentage: '',
      telegramLink: null,
      item: item,
      isUnlisted: item.is_unlisted || false
    };
  }
};

// Функция для проверки статуса предложения (можно вызвать при загрузке страницы)
const checkOfferStatus = async (itemId) => {
  try {
    const { data, error } = await supabase
      .from('offers')
      .select('status')
      .eq('item_id', itemId)
      .eq('buyer_name', currentAccountName.value)
      .single();

    if (error) return null;
    
    return data.status; // 'pending', 'accepted', 'declined'
  } catch (error) {
    console.error('Error checking offer status:', error);
    return null;
  }
};

const extractSymbolWithPercentage = (item) => {
  try {
    
    let rawSymbol = null;
    let percentage = 0;
    
    // Для activity items используем прямое поле symbol
    if (item.symbol) {
      rawSymbol = item.symbol;
    }
    // Для market items используем nft_object
    else if (item.nft_object) {
      try {
        const nftObj = typeof item.nft_object === 'string' 
          ? JSON.parse(item.nft_object) 
          : item.nft_object;
        
        if (nftObj.symbol) {
          rawSymbol = nftObj.symbol;
        }
      } catch (e) {
        console.log('❌ Ошибка парсинга nft_object:', e);
      }
    } else if (item.html_content) {
      const patterns = [
        /symbol["']?:\s*["']([^"']+)["']/i,
        /symbol["']?:\s*[']([^']+)[']/i,
        /Символ[:\s]+([^\n\r<]+)/i
      ];
      
      for (const pattern of patterns) {
        const match = item.html_content.match(pattern);
        if (match && match[1]) {
          rawSymbol = match[1];
          console.log('📋 Символ из HTML:', rawSymbol);
          break;
        }
      }
    }
    
    if (!rawSymbol) {
      console.log('❌ Символ не найден');
      return { name: null, percentage: 0 };
    }
    
    // Извлекаем название и процент
    const percentageMatch = rawSymbol.match(/(\d+\.?\d*)%/);
    if (percentageMatch) {
      percentage = parseFloat(percentageMatch[1]);
    }
    
    // Извлекаем название символа (убираем проценты)
    const symbolName = rawSymbol
      .replace(/\d+\.?\d*%/, '') // удаляем проценты
      .replace(/^\s+|\s+$/g, '') // обрезаем пробелы
      .replace(/\s+/g, ' '); // заменяем множественные пробелы на один
    
    return { name: symbolName, percentage };
    
  } catch (error) {
    console.error('❌ Ошибка извлечения символа с редкостью:', error);
    return { name: null, percentage: 0 };
  }
};

// Обновите функцию availableSymbolOptions для использования редкости из nft_object
const availableSymbolOptions = computed(() => {
  const availableSymbols = {};
  const items = getCurrentDataSource.value;
  
  // Фильтруем items по всем фильтрам кроме symbol
  const preFilteredItems = items.filter(item => {
    // NFT фильтр
    if (selectedFilters.value.nft.length > 0) {
      const itemName = getNftDisplayName(item.nft_type, item.nft_object);
      const normalizedItemName = normalizeNftName(itemName);
      
      const passesNftFilter = selectedFilters.value.nft.some(selectedNft => {
        const normalizedSelected = normalizeNftName(selectedNft);
        return normalizedItemName.includes(normalizedSelected);
      });
      if (!passesNftFilter) return false;
    }
    
    // Model фильтр
    if (selectedFilters.value.model.length > 0) {
      const itemModel = extractModelFromNft(item);
      if (!itemModel) return false;
      
      const passesModelFilter = selectedFilters.value.model.some(selectedModel => 
        itemModel.toLowerCase().includes(selectedModel.toLowerCase())
      );
      if (!passesModelFilter) return false;
    }
    
    // Backdrop фильтр
    if (selectedFilters.value.backdrop.length > 0) {
      const itemBackdrop = extractBackdropFromNft(item);
      if (!itemBackdrop) return false;
      
      const cleanItemBackdrop = itemBackdrop.split(' ')[0].toLowerCase().trim();
      const passesBackdropFilter = selectedFilters.value.backdrop.some(selectedBackdrop => {
        const cleanSelectedBackdrop = selectedBackdrop.split(' ')[0].toLowerCase().trim();
        return cleanItemBackdrop === cleanSelectedBackdrop;
      });
      if (!passesBackdropFilter) return false;
    }
    
    // НЕ фильтруем по symbol
    return true;
  });
  
  // Собираем символы из отфильтрованных items
  preFilteredItems.forEach(item => {
    const symbolData = extractSymbolWithPercentage(item);
    if (symbolData.name) {
      const normalizedSymbol = normalizeSymbolName(symbolData.name);
      const existing = availableSymbols[normalizedSymbol];
      
      if (!existing || symbolData.percentage < existing.percentage) {
        // ГЕНЕРИРУЕМ HTML КОНТЕНТ ЗДЕСЬ
        const htmlContent = generateSymbolHtml(symbolData.name);
        
        availableSymbols[normalizedSymbol] = {
          name: symbolData.name,
          percentage: symbolData.percentage,
          rarityText: symbolData.percentage > 0 ? `${symbolData.percentage}%` : 'N/A',
          count: 1,
          htmlContent: htmlContent // ← ДОБАВЛЯЕМ HTML КОНТЕНТ
        };
        
        // Сохраняем в кэш
        symbolHtmlCache.value[symbolData.name] = htmlContent;
      } else if (existing) {
        existing.count = (existing.count || 1) + 1;
      }
    }
  });
  
  const result = Object.values(availableSymbols);
  return result;
});



const initiateBuy = async (item) => {
  try {
    // Защита от повторных нажатий
    if (buyModal.value.loading) {
      console.log('⏳ Покупка уже обрабатывается...');
      return;
    }

    console.log('🔄 Инициализация покупки...', item.id);
    
    buyModal.value = {
      show: true,
      item: item,
      nftType: item.nft_type,
      pricePerUnit: item.price_per_unit,
      currency: item.currency || 'TON',
      amount: item.amount || 1,
      buyAmount: 1,
      loading: false
    };
    
  } catch (error) {
    console.error('Ошибка инициализации покупки:', error);
    showNotification('Error initializing purchase', 'error');
  }
};
// В функции openEditPriceModal
const openEditPriceModal = (item) => {
  editPriceModal.value = {
    show: true,
    item: item,
    nftType: item.nft_type,
    currentPrice: item.price_per_unit,
    newPrice: item.price_per_unit, // Устанавливаем начальное значение равным текущей цене
    loading: false
  };
};


const initiateSellFromUnlisted = (nftData) => {
  // Закрываем полноэкранное меню
  if (htmlModal.value && htmlModal.value.show) {
    htmlModal.value.show = false;
  }
  
  // Определяем тип NFT из URL
  const nftType = `html_nft_${extractNftNameFromUrl(nftData.url)}`;
  
  sellModal.value = {
    show: true,
    nftType: nftType,
    nftData: nftData,
    price: '',
    amount: 1,
    totalPrice: 0,
    commission: 0,
    finalAmount: 0,
    confirmStep: false,
    isHtmlNft: true
  };
};
// Исправленная функция для Backdrop
const getFilteredBackdropOptions = () => {
  const query = backdropSearchQuery.value ? backdropSearchQuery.value.toLowerCase() : '';
  
  // ВСЕГДА показываем выбранные опции
  const selectedOptions = backdropColors.value.filter(color => 
    isOptionSelected('backdrop', color.id)
  );
  
  // Фильтруем невыбранные опции по поисковому запросу
  const unselectedOptions = backdropColors.value
    .filter(color => 
      !isOptionSelected('backdrop', color.id) && (
        color.name.toLowerCase().includes(query) ||
        color.id.toLowerCase().includes(query)
      )
    );
  
  console.log(`🎨 Backdrop: выбрано ${selectedOptions.length}, найдено ${unselectedOptions.length} по запросу "${query}"`);
  
  return [...selectedOptions, ...unselectedOptions];
};
// Функция для извлечения backdrop с процентом
const extractBackdropWithPercentage = (item) => {
  try {
    
    let rawBackdrop = null;
    
    // 1. Проверяем разные источники по приоритету
    const sources = [
      { name: 'nft_metadata', value: item.nft_metadata?.backdrop },
      { name: 'backdrop field', value: item.backdrop },
      { name: 'nft_object', value: getBackdropFromNftObject(item.nft_object) },
      { name: 'html_content', value: getBackdropFromHtml(item.html_content) }
    ];
    
    for (const source of sources) {
      if (source.value) {
        rawBackdrop = source.value;
        break;
      }
    }
    
    if (!rawBackdrop) {
      console.log('❌ Backdrop не найден');
      return { name: null, percentage: 0 };
    }
    
    // Извлекаем название и процент
    const backdropMatch = rawBackdrop.match(/(.+?)\s*(\d+\.?\d*)%?$/);
    if (backdropMatch) {
      const name = backdropMatch[1].trim();
      const percentage = parseFloat(backdropMatch[2]) || 0;
      return { name, percentage };
    } else {
      // Если нет процента, возвращаем только название
      const name = rawBackdrop.replace(/\d+\.?\d*%/, '').trim();
      console.log('✅ Backdrop без процента:', name);
      return { name, percentage: 0 };
    }
    
  } catch (error) {
    console.error('❌ Ошибка извлечения backdrop:', error);
    return { name: null, percentage: 0 };
  }
};
// В methods или setup функции добавьте:
const openOfferBotLink = () => {
  // Открываем ссылку на Telegram бота в новой вкладке
  window.open('https://t.me/DROPS_OFC_bot', '_blank', 'noopener,noreferrer');
  
  // Также можно добавить закрытие модального окна если нужно
  // htmlModal.value.show = false;
};
const filteredActivity = computed(() => {
  let filtered = activityItems.value || [];
  
  // Фильтр "My Activity"
  if (showOnlyMyActivity.value && currentAccountName.value) {
    filtered = filtered.filter(activity => 
      activity.user_name === currentAccountName.value
    );
  }
  
  // Фильтр по типу операции
  if (selectedActivityType.value && selectedActivityType.value !== 'all') {
    filtered = filtered.filter(
      activity => activity.operation_type === selectedActivityType.value
    );
  }
  
  // Теперь используем общую систему фильтров
  // Преобразуем activity items в формат для фильтрации
  const activityAsMarketItems = filtered.map(activity => {
    let nftData = {};
    
    try {
      if (activity.nft_object) {
        nftData = typeof activity.nft_object === 'string' 
          ? JSON.parse(activity.nft_object) 
          : activity.nft_object;
      }
    } catch (parseError) {
      console.error('❌ Ошибка парсинга nft_object:', parseError);
    }
    
    return {
      id: `activity-${activity.id}`,
      nft_type: activity.nft_type,
      nft_object: nftData,
      seller: activity.user_name,
      // Добавляем данные для фильтрации
      nft_name: nftData.name,
      model: nftData.model,
      symbol: nftData.symbol,
      backdrop: nftData.backdrop
    };
  });
  
  // Применяем общие фильтры к преобразованным данным
  const filteredByCommonFilters = activityAsMarketItems.filter(item => {
    // NFT фильтр
    if (selectedFilters.value.nft.length > 0) {
      const itemName = getNftDisplayName(item.nft_type, item);
      const normalizedItemName = normalizeNftName(itemName);
      
      const passesNftFilter = selectedFilters.value.nft.some(selectedNft => {
        const normalizedSelected = normalizeNftName(selectedNft);
        return normalizedItemName.includes(normalizedSelected);
      });
      if (!passesNftFilter) return false;
    }
    
    // Model фильтр
    if (selectedFilters.value.model.length > 0) {
      const itemModel = extractModelFromNft(item);
      if (!itemModel) return false;
      
      const passesModelFilter = selectedFilters.value.model.some(selectedModel => 
        itemModel.toLowerCase().includes(selectedModel.toLowerCase())
      );
      if (!passesModelFilter) return false;
    }
    
    // Symbol фильтр
    if (selectedFilters.value.symbol.length > 0) {
      const itemSymbol = extractSymbolFromNft(item);
      if (!itemSymbol) return false;
      
      const normalizedItemSymbol = normalizeSymbolName(itemSymbol);
      const passesSymbolFilter = selectedFilters.value.symbol.some(selectedSymbol => {
        const normalizedSelectedSymbol = normalizeSymbolName(selectedSymbol);
        return normalizedItemSymbol === normalizedSelectedSymbol;
      });
      if (!passesSymbolFilter) return false;
    }
    
    // Backdrop фильтр
    if (selectedFilters.value.backdrop.length > 0) {
      const itemBackdrop = extractBackdropFromNft(item);
      if (!itemBackdrop) return false;
      
      const cleanItemBackdrop = itemBackdrop.split(' ')[0].toLowerCase().trim();
      const passesBackdropFilter = selectedFilters.value.backdrop.some(selectedBackdrop => {
        const cleanSelectedBackdrop = selectedBackdrop.split(' ')[0].toLowerCase().trim();
        return cleanItemBackdrop === cleanSelectedBackdrop;
      });
      if (!passesBackdropFilter) return false;
    }
    
    return true;
  });
  
  // Возвращаем оригинальные activity items, которые прошли фильтрацию
  const filteredActivityIds = new Set(filteredByCommonFilters.map(item => item.id.replace('activity-', '')));
  return filtered.filter(activity => filteredActivityIds.has(activity.id.toString()));
});


// Временно добавьте эту функцию для отладки
const debugImageGeneration = (nftType, modelName) => {
  console.group('🔍 ДЕБАГ ГЕНЕРАЦИИ URL:');
  console.log('nftType:', nftType);
  console.log('modelName:', modelName);
  
  let cleanNftType = nftType.toLowerCase();
  if (cleanNftType.startsWith('html_nft_')) {
    cleanNftType = cleanNftType.replace('html_nft_', '');
  }
  if (cleanNftType.startsWith('htmlnft')) {
    cleanNftType = cleanNftType.replace('htmlnft', '');
  }
  
  console.log('cleanNftType:', cleanNftType);
  
  const folderName = groupDisplayNames[cleanNftType] || cleanNftType;
  console.log('folderName:', folderName);
  
  const cleanNftPath = folderName.toLowerCase().replace(/[^a-z]/g, '');
  const cleanModelPath = modelName.toLowerCase().replace(/[^a-z]/g, '');
  
  console.log('cleanNftPath:', cleanNftPath);
  console.log('cleanModelPath:', cleanModelPath);
  
  const url = `https://storage.portal-market.com/portals-market/gifts/${cleanNftPath}/models/png/${cleanModelPath}.png`;
  console.log('Generated URL:', url);
  console.groupEnd();
  
  return url;
};

// Обновленная функция для получения отфильтрованных символов
// Исправленная функция для Symbol
const getFilteredSymbolOptions = () => {
  const query = searchQuery.value ? searchQuery.value.toLowerCase() : '';
  
  if (!availableSymbolOptions.value || availableSymbolOptions.value.length === 0) {
    return [];
  }
  
  // ВСЕГДА показываем выбранные опции (даже если не подходят под поиск)
  const selectedOptions = availableSymbolOptions.value.filter(symbol => 
    isOptionSelected('symbol', symbol.name)
  );
  
  // Фильтруем невыбранные опции по поисковому запросу
  const unselectedOptions = availableSymbolOptions.value
    .filter(symbol => 
      !isOptionSelected('symbol', symbol.name) && (
        symbol.name.toLowerCase().includes(query) ||
        (symbol.rarityText && symbol.rarityText.toLowerCase().includes(query))
      )
    );
  
  console.log(`🔍 Symbol: выбрано ${selectedOptions.length}, найдено ${unselectedOptions.length} по запросу "${query}"`);
  
  return [...selectedOptions, ...unselectedOptions];
};

// Функции для обработки событий iframe
const onSymbolIframeLoad = (symbolName) => {
  console.log(`✅ Symbol iframe loaded: ${symbolName}`);
};

const onSymbolIframeError = (symbolName) => {
  console.error(`❌ Symbol iframe error: ${symbolName}`);
};
// Замените все вызовы modelData.floorPrice.toFixed() на:
const formatFloorPrice = (price) => {
  if (!price || isNaN(parseFloat(price))) return null;
  return parseFloat(price).toFixed(1);
};


const getNftDisplayNameForGroup = (nftType) => {
  
  // Очищаем имя от префиксов и преобразуем в нижний регистр
  let cleanNftType = nftType.toLowerCase();
  if (cleanNftType.startsWith('html_nft_')) {
    cleanNftType = cleanNftType.replace('html_nft_', '');
    console.log('🧹 Удалили html_nft_:', cleanNftType);
  }
  if (cleanNftType.startsWith('htmlnft')) {
    cleanNftType = cleanNftType.replace('htmlnft', '');
    console.log('🧹 Удалили htmlnft:', cleanNftType);
  }
  
  
  // Используем маппинг для получения правильного имени
  const displayName = groupDisplayNames[cleanNftType] || cleanNftType;
  
  console.groupEnd();
  
  return displayName;
};

const extractNftName = (nftObject) => {
  try {
    const obj = typeof nftObject === 'string' ? JSON.parse(nftObject) : nftObject;
    if (obj.url) {
      // Извлекаем название из URL: https://t.me/nft/TopHat-11 → Top Hat
      const match = obj.url.match(/\/nft\/([^-]+)/);
      if (match && match[1]) {
        const name = match[1];
        // Преобразуем CamelCase в нормальное название
        return name.replace(/([A-Z])/g, ' $1').trim();
      }
    }
    return 'Unknown NFT';
  } catch (error) {
    console.error('Error extracting NFT name:', error);
    return 'Error';
  }
};


// Функция открытия модального окна подарка
const openGiftModal = (item) => {
  if (!item) {
    showNotification('Item not found', 'error');
    return;
  }

  const isOwnItem = item.seller === currentAccountName.value;
  
  giftModal.value = {
    show: true,
    item: item,
    recipientName: '',
    loading: false,
    isOwnItem: isOwnItem // Флаг своего/чужого объявления
  };
};

// Функция отправки подарка
// Функция отправки подарка
// Функция отправки подарка
const sendGift = async () => {
  try {
    giftModal.value.loading = true;

    const { item, recipientName, isOwnItem } = giftModal.value;
    const giftPrice = item.price_per_unit;

    // Проверяем существование получателя
    const { data: recipientData, error: recipientError } = await supabase
      .from('users')
      .select('name, nft_links')
      .eq('name', recipientName)
      .single();

    if (recipientError || !recipientData) {
      showNotification('Recipient not found', 'error');
      giftModal.value.loading = false;
      return;
    }

    if (isOwnItem) {
      // СВОЕ объявление - бесплатная передача
      await sendOwnItemAsGift(item, recipientName);
    } else {
      // ЧУЖОЕ объявление - покупка и отправка
      await sendPurchasedItemAsGift(item, recipientName, giftPrice);
    }

    showNotification(`Gift sent successfully to ${recipientName}!`, 'success');
    giftModal.value.show = false;
    
    // Закрываем полноэкранный просмотр если открыт
    if (htmlModal.value.show) {
      htmlModal.value.show = false;
    }

  } catch (error) {
    console.error('Error sending gift:', error);
    showNotification('Error sending gift', 'error');
  } finally {
    giftModal.value.loading = false;
  }
};









// Функция отправки СВОЕГО объявления как подарка (бесплатно)
// Функция отправки СВОЕГО объявления как подарка (бесплатно)
const sendOwnItemAsGift = async (item, recipientName) => {
  // Получаем данные получателя
  const { data: recipientData, error: recipientError } = await supabase
    .from('users')
    .select('nft_links')
    .eq('name', recipientName)
    .single();

  if (recipientError) {
    throw new Error('Failed to get recipient data');
  }

  // Подготавливаем данные NFT для получателя
  const nftData = {
    url: item.nft_object?.url || item.url || '',
    name: extractNameFromNftObject(item).name,
    model: item.nft_object?.model || '',
    symbol: item.nft_object?.symbol || '',
    backdrop: item.nft_object?.backdrop || '',
    acquired_at: new Date().toISOString(),
    gifted: true,
    gifted_from: currentAccountName.value,
    gifted_at: new Date().toISOString()
  };

  // Добавляем NFT получателю
  const recipientCurrentLinks = recipientData.nft_links || [];
  const updatedRecipientLinks = [...recipientCurrentLinks, nftData];

  await supabase
    .from('users')
    .update({ nft_links: updatedRecipientLinks })
    .eq('name', recipientName);

  // Удаляем NFT у отправителя (если это unlisted NFT)
  if (item.is_unlisted) {
    const { data: senderNftData } = await supabase
      .from('users')
      .select('nft_links')
      .eq('name', currentAccountName.value)
      .single();

    if (senderNftData && senderNftData.nft_links) {
      const updatedSenderLinks = senderNftData.nft_links.filter(nft => 
        nft.url !== nftData.url
      );

      await supabase
        .from('users')
        .update({ nft_links: updatedSenderLinks })
        .eq('name', currentAccountName.value);
    }
  } else {
    // Если это listed NFT, удаляем с рынка
    await supabase
      .from('market')
      .delete()
      .eq('id', item.id);
  }

  // УБРАНА ЗАПИСЬ АКТИВНОСТИ
  
  // Обновляем локальные данные
  if (item.is_unlisted) {
    await loadUnlistedNfts();
  } else {
    await loadMarketItems();
  }
  
};

// Упрощенная функция для генерации HTML с TGS анимацией
const generateSymbolHtml = (symbol) => {
  try {
    const symbolName = typeof symbol === 'string' ? symbol : symbol.name;
    
    console.log(`🎨 Генерация TGS HTML для символа: ${symbolName}`);
    
    const possibleTgsNames = [
      symbolName.toLowerCase().replace(/\s+/g, '%20'),
      symbolName.toLowerCase().replace(/\s+/g, '_'),
      symbolName.toLowerCase().replace(/\s+/g, ''),
      symbolName.toLowerCase().split(' ')[0]
    ];
    
    const tgsUrls = possibleTgsNames.map(name => 
      `https://gifts.coffin.meme/patterns/${name}.tgs`
    );

    return `
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/bodymovin/5.7.13/lottie.min.js"><\/script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/pako/2.0.4/pako.min.js"><\/script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body, html {
            width: 100%;
            height: 100%;
            background: transparent;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        #main-container {
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            background: transparent;
        }
        #animation-wrapper {
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: transparent;
        }
        .lottie-animation {
            width: 100%;
            height: 100%;
        }
        .fallback {
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #f8f8f8;
            border-radius: 6px;
            font-size: 8px;
            color: #666;
            text-align: center;
            padding: 2px;
            border: 1px solid #e0e0e0;
        }
    </style>
</head>
<body>
    <div id="main-container">
        <div id="animation-wrapper">
            <div class="lottie-animation" id="lottie"></div>
            <div class="fallback" id="fallback" style="display: none;">${symbolName}</div>
        </div>
    </div>
    
    <script>
        let animation = null;
        let currentUrlIndex = 0;
        const tgsUrls = ${JSON.stringify(tgsUrls)};
        
        function showAnimation() {
            document.getElementById('lottie').style.display = 'block';
            document.getElementById('fallback').style.display = 'none';
        }
        
        function showFallback() {
            document.getElementById('lottie').style.display = 'none';
            document.getElementById('fallback').style.display = 'flex';
        }
        
        async function loadTgsAnimation(url) {
            try {
                console.log('🔄 Fetching TGS file:', url);
                const response = await fetch(url);
                
                if (!response.ok) {
                    throw new Error('HTTP ' + response.status);
                }
                
                const arrayBuffer = await response.arrayBuffer();
                console.log('✅ TGS file fetched, size:', arrayBuffer.byteLength);
                
                // Декомпрессия TGS (gzip compressed JSON)
                const compressedData = new Uint8Array(arrayBuffer);
                const decompressedData = pako.inflate(compressedData, { to: 'string' });
                const animationData = JSON.parse(decompressedData);
                
                console.log('✅ TGS decompressed successfully');
                
                if (animation) {
                    animation.destroy();
                    animation = null;
                }
                
                animation = lottie.loadAnimation({
                    container: document.getElementById('lottie'),
                    renderer: 'svg',
                    loop: true,
                    autoplay: true,
                    animationData: animationData,
                    rendererSettings: {
                        preserveAspectRatio: 'xMidYMid meet',
                        progressiveLoad: false,
                        hideOnTransparent: false
                    }
                });
                
                animation.addEventListener('DOMLoaded', function() {
                    console.log('✅ Symbol animation loaded and playing');
                    showAnimation();
                    if (window.parent) {
                        window.parent.postMessage({
                            type: 'symbolIframeLoad',
                            symbolName: '${symbolName}',
                            status: 'success',
                            url: url
                        }, '*');
                    }
                });
                
                animation.addEventListener('error', function(err) {
                    console.error('❌ Lottie animation error:', err);
                    throw new Error('Lottie playback failed');
                });
                
            } catch (error) {
                console.error('❌ Error loading TGS animation:', error);
                throw error;
            }
        }
        
        async function loadAnimation() {
            if (currentUrlIndex >= tgsUrls.length) {
                console.log('❌ All TGS URLs failed, showing fallback');
                showFallback();
                return;
            }
            
            const currentUrl = tgsUrls[currentUrlIndex];
            console.log('🔄 Attempting to load symbol animation:', currentUrl);
            
            try {
                await loadTgsAnimation(currentUrl);
            } catch (error) {
                console.warn('❌ Animation load failed:', currentUrl, error.message);
                currentUrlIndex++;
                setTimeout(loadAnimation, 300);
            }
        }
        
        // Загружаем анимацию сразу
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', loadAnimation);
        } else {
            loadAnimation();
        }
        
        // Обработчик клика для перезапуска
        document.addEventListener('click', function() {
            currentUrlIndex = 0;
            if (animation) {
                animation.destroy();
                animation = null;
            }
            loadAnimation();
        });
    <\/script>
</body>
</html>
    `;
  } catch (error) {
    console.error('❌ Ошибка генерации HTML для символа:', error);
    const symbolName = typeof symbol === 'string' ? symbol : symbol.name;
    return `
      <div style="width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; background: #f8f8f8; border-radius: 6px;">
        <span style="font-size: 10px; color: #666;">${symbolName}</span>
      </div>
    `;
  }
};

// Добавьте эти функции в script секцию:

// Исправленная функция проверки наличия item на маркете
// Упрощенная и исправленная функция проверки
const isItemOnMarket = async (item) => {
  try {
    if (!item || !item.item_id) {
      console.log('❌ Нет item или item_id');
      return false;
    }
    
    console.log('🔍 Проверяем наличие на маркете для item_id:', item.item_id);
    
    // Сначала проверяем в локальном кэше marketItems
    const foundInCache = marketItems.value.some(marketItem => {
      const isMatch = marketItem.item_id === item.item_id;
      if (isMatch) {
        console.log('✅ Найден в локальном кэше marketItems');
        return true;
      }
      return false;
    });
    
    if (foundInCache) {
      return true;
    }
    
    console.log('🔍 Не найден в кэше, но возвращаем true для теста');
    return true; // ВРЕМЕННО ВСЕГДА TRUE ДЛЯ ТЕСТА
    
  } catch (error) {
    console.error('❌ Ошибка в isItemOnMarket:', error);
    return true; // ВРЕМЕННО ВСЕГДА TRUE ДЛЯ ТЕСТА
  }
};

// Метод для перехода к объявлению на маркете
const goToMarketItem = (item) => {
  try {
    if (!item || !item.item_id) {
      showNotification('Invalid item data', 'error');
      return;
    }
    
    console.log('🛒 Переход к маркетному объявлению:', item.item_id);
    
    // Находим объявление на маркете
    const marketItem = marketItems.value.find(marketItem => 
      marketItem.item_id === item.item_id
    );
    
    if (marketItem) {
      console.log('✅ Найден маркетный item, открываем...');
      
      // Закрываем текущий полноэкранный просмотр
      htmlModal.value.show = false;
      
      // Небольшая задержка для анимации закрытия
      setTimeout(() => {
        // Открываем полноэкранный просмотр для маркетного объявления
        openFullscreenView(marketItem);
      }, 300);
      
    } else {
      console.log('❌ Не найден в marketItems, проверяем в БД...');
      
      // Если не нашли в локальном кэше, ищем в БД
      supabase
        .from('market')
        .select('*')
        .eq('item_id', item.item_id)
        .limit(1)
        .then(({ data, error }) => {
          if (error) {
            throw error;
          }
          
          if (data && data.length > 0) {
            const marketItemFromDb = data[0];
            console.log('✅ Найден в БД, открываем...');
            
            // Закрываем текущий просмотр
            htmlModal.value.show = false;
            
            setTimeout(() => {
              // Открываем найденное объявление
              openFullscreenView(marketItemFromDb);
            }, 300);
            
          } else {
            showNotification('Listing not found on market', 'error');
            console.log('❌ Объявление не найдено на маркете');
          }
        })
        .catch(error => {
          console.error('❌ Ошибка поиска в БД:', error);
          showNotification('Error finding listing', 'error');
        });
    }
    
  } catch (error) {
    console.error('❌ Ошибка в goToMarketItem:', error);
    showNotification('Error opening market listing', 'error');
  }
};
// Функция покупки и отправки ЧУЖОГО объявления как подарка
// Функция покупки и отправки ЧУЖОГО объявления как подарка
const sendPurchasedItemAsGift = async (item, recipientName, giftPrice) => {
  // Проверяем баланс отправителя
  const { data: senderData, error: senderError } = await supabase
    .from('users')
    .select('ton_balance')
    .eq('name', currentAccountName.value)
    .single();

  if (senderError) throw senderError;

  const senderBalance = parseFloat(senderData.ton_balance) || 0;
  
  if (senderBalance < giftPrice) {
    throw new Error(`Insufficient TON balance. Need ${giftPrice} TON, have ${senderBalance} TON`);
  }

  // Получаем данные получателя
  const { data: recipientData, error: recipientError } = await supabase
    .from('users')
    .select('nft_links')
    .eq('name', recipientName)
    .single();

  if (recipientError) {
    throw new Error('Failed to get recipient data');
  }

  // Подготавливаем данные NFT для получателя
  const nftData = {
    url: item.nft_object?.url || item.url || '',
    name: extractNameFromNftObject(item).name,
    model: item.nft_object?.model || '',
    symbol: item.nft_object?.symbol || '',
    backdrop: item.nft_object?.backdrop || '',
    acquired_at: new Date().toISOString(),
    gifted: true,
    gifted_from: currentAccountName.value,
    gifted_at: new Date().toISOString(),
    original_seller: item.seller
  };

  // Обновляем баланс отправителя (списываем стоимость)
  const newSenderBalance = senderBalance - giftPrice;
  await supabase
    .from('users')
    .update({ ton_balance: newSenderBalance })
    .eq('name', currentAccountName.value);

  // Пополняем баланс оригинального продавца (98% от суммы)
  const sellerAmount = giftPrice * 0.98;

  const { data: sellerData } = await supabase
    .from('users')
    .select('ton_balance')
    .eq('name', item.seller)
    .single();

  if (sellerData) {
    const sellerCurrentBalance = parseFloat(sellerData.ton_balance) || 0;
    const newSellerBalance = sellerCurrentBalance + sellerAmount;

    await supabase
      .from('users')
      .update({ ton_balance: newSellerBalance })
      .eq('name', item.seller);
  }

  // Добавляем NFT получателю
  const recipientCurrentLinks = recipientData.nft_links || [];
  const updatedRecipientLinks = [...recipientCurrentLinks, nftData];

  await supabase
    .from('users')
    .update({ nft_links: updatedRecipientLinks })
    .eq('name', recipientName);

  // Удаляем объявление с рынка
  await supabase
    .from('market')
    .delete()
    .eq('id', item.id);

  // УБРАНЫ ВСЕ ЗАПИСИ АКТИВНОСТИ

  // Обновляем локальные данные
  tonBalance.value = newSenderBalance.toString();
  await loadMarketItems();
  
  // Обновляем корзину если товар был в ней
  if (isInCart(item.id)) {
    await removeFromCart(item.id);
  }
};

    const extractNftType = (nftType) => {
      if (!nftType) return '';
      if (nftType.startsWith('html_nft_')) {
        const parts = nftType.split('_')[2]?.split('-') || [];
        return parts[0] || nftType;
      }
      return nftType;
    };

    const getUniqueNftTypes = computed(() => {
      const types = new Set();
      marketItems.value.forEach(item => {
        const type = extractNftType(item.nft_type);
        if (type) types.add(type);
      });
      return Array.from(types).sort();
    });

    const activeFilterCategory = ref(null);
    const activeCategoryWidth = ref(0);


    const toggleFilterCategory = async (categoryId) => {
  if (activeFilterCategory.value === categoryId) {
    activeFilterCategory.value = null;
  } else {
    activeFilterCategory.value = categoryId;
    
    // Если выбрана категория Model - проверяем есть ли выбранные NFT
    if (categoryId === 'model') {
      if (selectedFilters.value.nft && selectedFilters.value.nft.length > 0) {
        const nftType = selectedFilters.value.nft[0];
        if (nftType && !nftModelsCache.value[nftType]) {
          await loadNftModels(nftType);
        }
      } else {
        console.log('Сначала выберите NFT для просмотра моделей');
        // Можно показать уведомление пользователю
        showNotification('Сначала выберите NFT в категории NFT', 'error');
        activeFilterCategory.value = null; // Закрываем меню
        return;
      }
    }
    
    nextTick(() => {
      const btn = document.querySelector(`.filter-category-btn.active`);
      if (btn) {
        activeCategoryWidth.value = btn.offsetWidth;
      }
    });
  }
};


  

// Обновите функцию handleSell (открытие модального окна)
const handleSell = async (nftData) => {
  try {
    console.log('🔄 Открытие модального окна продажи...');
    
    // Определяем тип NFT (HTML NFT или обычный)
    const isHtmlNft = nftData && nftData.url;
    
    // СРАЗУ ПРОВЕРЯЕМ И УДАЛЯЕМ ДУБЛИКАТЫ ПРИ ОТКРЫТИИ МОДАЛЬНОГО ОКНА
    console.log('🧹 Мгновенная очистка дубликатов...');
    await cleanupMarketDuplicates();
    await cleanupUnlistedDuplicates();
    
    // ПРОВЕРЯЕМ КОНФЛИКТЫ СРАЗУ
    const conflicts = await checkForImmediateConflicts(nftData);
    if (conflicts.hasMarketDuplicates) {
      console.log('🚫 Найдены дубликаты на маркете, удаляем из unlisted...');
      await removeNftFromUnlisted(nftData);
      await loadUnlistedNfts();
      showNotification('Обнаружены дубликаты на маркете. NFT удалено из вашей коллекции.', 'warning');
      return; // Не открываем модальное окно
    }
    
    if (conflicts.hasUnlistedDuplicates) {
      console.log('🚫 Найдены дубликаты в unlisted, очищаем...');
      await cleanupUnlistedDuplicates();
      await loadUnlistedNfts();
    }

    // Устанавливаем данные для модального окна продажи
    sellModal.value = {
      show: true,
      nftType: isHtmlNft ? `html_nft_${extractNftNameFromUrl(nftData.url)}` : nftData.nft_type,
      amount: isHtmlNft ? 1 : '',
      price: '',
      confirmStep: false,
      isHtmlNft: isHtmlNft,
      totalPrice: 0,
      commission: 0,
      finalAmount: 0,
      nftData: nftData
    };
    
    console.log('✅ Модальное окно продажи открыто');
    
  } catch (error) {
    console.error('❌ Ошибка при открытии модального окна продажи:', error);
    showNotification('Ошибка при подготовке к продаже', 'error');
  }
};

// Функция мгновенной проверки конфликтов
const checkForImmediateConflicts = async (nftData) => {
  try {
    console.log('🔍 Мгновенная проверка конфликтов для:', nftData?.url);
    
    const results = {
      hasMarketDuplicates: false,
      hasUnlistedDuplicates: false,
      marketDuplicatesCount: 0,
      unlistedDuplicatesCount: 0
    };

    // Проверка дубликатов на маркете
    if (nftData?.url) {
      const { data: marketItems, error } = await supabase
        .from('market')
        .select('*')
        .eq('seller', currentAccountName.value);

      if (!error && marketItems) {
        const duplicates = marketItems.filter(item => {
          if (item.nft_object) {
            try {
              const itemNftObj = typeof item.nft_object === 'string' ? JSON.parse(item.nft_object) : item.nft_object;
              return itemNftObj.url === nftData.url;
            } catch (e) {
              console.error('Error parsing nft_object:', e);
            }
          }
          return false;
        });

        if (duplicates.length > 0) {
          results.hasMarketDuplicates = true;
          results.marketDuplicatesCount = duplicates.length;
          console.log(`🚫 Найдено ${duplicates.length} дубликатов на маркете`);
          
          // СРАЗУ УДАЛЯЕМ ДУБЛИКАТЫ С МАРКЕТА
          const duplicateIds = duplicates.map(item => item.id);
          await supabase
            .from('market')
            .delete()
            .in('id', duplicateIds);
          console.log(`🗑️ Удалено ${duplicateIds.length} дубликатов с маркета`);
        }
      }
    }

    // Проверка дубликатов в unlisted
    const { data: userData, error: userError } = await supabase
      .from('users')
      .select('nft_links')
      .eq('name', currentAccountName.value)
      .single();

    if (!userError && userData?.nft_links) {
      const nftLinks = userData.nft_links;
      const seenUrls = new Set();
      const duplicates = [];

      nftLinks.forEach(nft => {
        const nftUrl = typeof nft === 'object' ? nft.url : nft;
        if (seenUrls.has(nftUrl)) {
          duplicates.push(nft);
        } else {
          seenUrls.add(nftUrl);
        }
      });

      if (duplicates.length > 0) {
        results.hasUnlistedDuplicates = true;
        results.unlistedDuplicatesCount = duplicates.length;
        console.log(`🚫 Найдено ${duplicates.length} дубликатов в unlisted`);
      }
    }

    console.log('✅ Результаты мгновенной проверки:', results);
    return results;
    
  } catch (error) {
    console.error('❌ Ошибка мгновенной проверки конфликтов:', error);
    return {
      hasMarketDuplicates: false,
      hasUnlistedDuplicates: false,
      marketDuplicatesCount: 0,
      unlistedDuplicatesCount: 0
    };
  }
};



// Улучшенная функция удаления NFT из unlisted
const removeNftFromUnlisted = async (nftData) => {
  try {
    if (!nftData?.url) {
      return { error: new Error('Invalid NFT data') };
    }

    const { data: userData, error: fetchError } = await supabase
      .from('users')
      .select('nft_links')
      .eq('name', currentAccountName.value)
      .single();

    if (fetchError) return { error: fetchError };

    const currentLinks = userData.nft_links || [];
    
    // Фильтруем удаляемый NFT (и все его дубликаты)
    const updatedLinks = currentLinks.filter(nft => {
      const nftUrl = typeof nft === 'object' ? nft.url : nft;
      return nftUrl !== nftData.url;
    });

    // Если ничего не изменилось, значит NFT не было в коллекции
    if (updatedLinks.length === currentLinks.length) {
      console.log('ℹ️ NFT не найдено в коллекции для удаления:', nftData.url);
      return { success: true };
    }

    // Обновляем базу данных
    const { error: updateError } = await supabase
      .from('users')
      .update({ nft_links: updatedLinks })
      .eq('name', currentAccountName.value);

    if (updateError) return { error: updateError };

    console.log('✅ NFT удалено из unlisted коллекции:', nftData.url);
    return { success: true };

  } catch (error) {
    console.error('❌ Ошибка удаления NFT из unlisted:', error);
    return { error };
  }
};

// Добавьте эту функцию для мгновенной очистки всех конфликтов
const instantCleanup = async () => {
  try {
    console.log('⚡ Мгновенная очистка всех конфликтов...');
    
    // Очистка маркета
    await cleanupMarketDuplicates();
    
    // Очистка unlisted
    await cleanupUnlistedDuplicates();
    
    // Удаление конфликтных NFT
    await removeConflictingNfts();
    
    // Обновление данных
    await loadMarketItems();
    await loadUnlistedNfts();
    
    console.log('✅ Мгновенная очистка завершена');
    showNotification('Все конфликты очищены!', 'success');
    
  } catch (error) {
    console.error('❌ Ошибка мгновенной очистки:', error);
  }
};

const groupDisplayNames = {
  'bdaycandle': 'B-Day Candle',
  'easteregg': 'Easter Egg',
  'tophat': 'Top Hat',
  'deskcalendar': 'Desk Calendar',
  'plushpepe': 'Plush Pepe',
  'jackinthebox': 'Jack-in-the-Box',
  'nekohelmet': 'Neko Helmet',
  'lovepotion': 'Love Potion',
  'toybear': 'Toy Bear',
  'diamondring': 'Diamond Ring',
  'lootbag': 'Loot Bag',
  'lunarsnake': 'Lunar Snake',
  'tamagadget': 'Tama Gadget',
  'candycane': 'Candy Cane',
  'cookieheart': 'Cookie Heart',
  'partysparkler': 'Party Sparkler',
  'jinglebells': 'Jingle Bells',
  'gingercookie': 'Ginger Cookie',
  'winterwreath': 'Winter Wreath',
  'santahat': 'Santa Hat',
  'snowglobe': 'Snow Globe',
  'snowmittens': 'Snow Mittens',
  'sleighbell': 'Sleigh Bell',
  'jesterhat': 'Jester Hat',
  'starnotepad': 'Star Notepad',
  'bunnymuffin': 'Bunny Muffin',
  'swisswatch': 'Swiss Watch',
  'signetring': 'Signet Ring',
  'genielamp': 'Genie Lamp',
  'astralshard': 'Astral Shard',
  'preciouspeach': 'Precious Peach',
  'spicedwine': 'Spiced Wine',
  'jellybunny': 'Jelly Bunny',
  'hangingstar': 'Hanging Star',
  'durovscap': 'Durov\'s Cap',
  'lovecandle': 'Love Candle',
  'perfumebottle': 'Perfume Bottle',
  'minioscar': 'Mini Oscar',
  'eternalrose': 'Eternal Rose',
  'berrybox': 'Berry Box',
  'vintagecigar': 'Vintage Cigar',
  'recordplayer': 'Record Player',
  'magicpotion': 'Magic Potion',
  'electricskull': 'Electric Skull',
  'kissedfrog': 'Kissed Frog',
  'hypnolollipop': 'Hypno Lollipop',
  'hexpot': 'Hex Pot',
  'evileye': 'Evil Eye',
  'iongem': 'Ion Gem',
  'sharptongue': 'Sharp Tongue',
  'madpumpkin': 'Mad Pumpkin',
  'trappedheart': 'Trapped Heart',
  'skullflower': 'Skull Flower',
  'crystalball': 'Crystal Ball',
  'flyingbroom': 'Flying Broom',
  'voodoodoll': 'Voodoo Doll',
  'scaredcat': 'Scared Cat',
  'witchhat': 'Witch Hat',
  'eternalcandle': 'Eternal Candle',
  'spyagaric': 'Spy Agaric',
  'lolpop': 'Lol Pop',
  'sakuraflower': 'Sakura Flower',
  'homemadecake': 'Homemade Cake'
};

const floorPrices = computed(() => {
  const floors = {
    nft: {},
    model: {},
    symbol: {},
    backdrop: {}
  };

  console.log('🔄 Вычисление floor prices...');
  
  marketItems.value.forEach(item => {
    const nftType = item.nft_type;
    const price = parseFloat(item.price_per_unit) || 0;
    
    // Для NFT
    let cleanNftType = nftType.toLowerCase();
    if (cleanNftType.startsWith('html_nft_')) {
      cleanNftType = cleanNftType.replace('html_nft_', '');
    }
    
    if (!floors.nft[cleanNftType] || price < floors.nft[cleanNftType]) {
      floors.nft[cleanNftType] = price;
    }
    
    // Для МОДЕЛЕЙ - ИСПРАВЛЕНО: сохраняем ПОЛНЫЕ названия
    const model = extractModelFromNft(item);
    if (model) {
      // Используем полное название модели в нижнем регистре
      const fullModel = model.toLowerCase().trim();
      if (fullModel && fullModel !== 'не указано') {
        if (!floors.model[fullModel] || price < floors.model[fullModel]) {
          floors.model[fullModel] = price;
          console.log(`💰 Установлен floor price для модели "${fullModel}": ${price}`);
        }
      }
    }
    
    // Для СИМВОЛОВ
    const symbol = extractSymbolFromNft(item);
    if (symbol) {
      const normalizedSymbol = normalizeSymbolName(symbol);
      if (normalizedSymbol && normalizedSymbol !== 'не указано') {
        if (!floors.symbol[normalizedSymbol] || price < floors.symbol[normalizedSymbol]) {
          floors.symbol[normalizedSymbol] = price;
        }
      }
    }
    
    // Для ФОНОВ - ИСПРАВЛЕНО: сохраняем ПОЛНЫЕ названия
    const backdrop = extractBackdropFromNft(item);
    if (backdrop) {
      // Используем полное название backdrop в нижнем регистре
      const fullBackdrop = backdrop.toLowerCase().trim();
      if (fullBackdrop && fullBackdrop !== 'не указано') {
        if (!floors.backdrop[fullBackdrop] || price < floors.backdrop[fullBackdrop]) {
          floors.backdrop[fullBackdrop] = price;
        }
      }
    }
  });

  console.log('✅ Floor prices вычислены:', {
    nft: Object.keys(floors.nft).length,
    model: Object.keys(floors.model), // Показываем ключи моделей
    symbol: Object.keys(floors.symbol).length,
    backdrop: Object.keys(floors.backdrop).length
  });
  
  return floors;
});




const normalizeModelName = (name) => {
  if (!name) return '';
  return name.toLowerCase().trim().replace(/\s+/g, ' ');
};

const normalizeBackdropName = (name) => {
  if (!name) return '';
  return name.toLowerCase().trim().split(' ')[0]; // Берем только первое слово для backdrop
};


const renderTgsFullscreen = async (tgsUrl, container) => {
  return new Promise(async (resolve) => {
    try {
      // Загружаем TGS данные
      const response = await fetch(tgsUrl);
      const animationData = await response.json();
      
      // Очищаем контейнер
      container.innerHTML = '';
      
      // Загружаем анимацию в полноэкранном режиме
      const anim = lottie.loadAnimation({
        container: container,
        renderer: 'svg',
        loop: true,
        autoplay: true,
        animationData: animationData
      });
      
      // Настраиваем контейнер для полноэкранного отображения
      container.style.width = '100%';
      container.style.height = '100%';
      container.style.display = 'flex';
      container.style.alignItems = 'center';
      container.style.justifyContent = 'center';
      container.style.background = 'transparent';
      
      // Ждем готовности
      anim.addEventListener('DOMLoaded', () => {
        console.log('✅ TGS анимация загружена в полноэкранном режиме');
        resolve(anim);
      });
      
      // Обработчик ошибок
      anim.addEventListener('data_failed', () => {
        console.error('❌ Ошибка загрузки TGS анимации');
        resolve(null);
      });
      
    } catch (error) {
      console.error('❌ Ошибка рендеринга TGS:', error);
      resolve(null);
    }
  });
};

// Функция для отображения TGS в полноэкранном режиме
const openTgsFullscreen = async (tgsUrl, title = 'TGS Animation') => {
  try {
    // Создаем полноэкранный контейнер
    const fullscreenContainer = document.createElement('div');
    fullscreenContainer.className = 'tgs-fullscreen-view';
    fullscreenContainer.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background: rgba(0, 0, 0, 0.9);
      z-index: 9999;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
    `;
    
    // Создаем заголовок
    const titleElement = document.createElement('div');
    titleElement.textContent = title;
    titleElement.style.cssText = `
      color: white;
      font-size: 24px;
      margin-bottom: 20px;
      text-align: center;
    `;
    
    // Создаем контейнер для анимации
    const animationContainer = document.createElement('div');
    animationContainer.style.cssText = `
      width: 90vw;
      height: 90vh;
      max-width: 800px;
      max-height: 800px;
      display: flex;
      align-items: center;
      justify-content: center;
    `;
    
    // Кнопка закрытия
    const closeButton = document.createElement('button');
    closeButton.textContent = '×';
    closeButton.style.cssText = `
      position: absolute;
      top: 20px;
      right: 20px;
      background: rgba(255, 255, 255, 0.2);
      color: white;
      border: none;
      border-radius: 50%;
      width: 50px;
      height: 50px;
      font-size: 30px;
      cursor: pointer;
      z-index: 10000;
    `;
    
    closeButton.onclick = () => {
      document.body.removeChild(fullscreenContainer);
    };
    
    // Собираем структуру
    fullscreenContainer.appendChild(titleElement);
    fullscreenContainer.appendChild(animationContainer);
    fullscreenContainer.appendChild(closeButton);
    document.body.appendChild(fullscreenContainer);
    
    // Загружаем анимацию
    const animation = await renderTgsFullscreen(tgsUrl, animationContainer);
    
    if (!animation) {
      // Если анимация не загрузилась, показываем сообщение об ошибке
      animationContainer.innerHTML = `
        <div style="color: white; text-align: center;">
          <h3>Ошибка загрузки анимации</h3>
          <p>Не удалось загрузить TGS файл</p>
        </div>
      `;
    }
    
    // Закрытие по клику на фон
    fullscreenContainer.onclick = (e) => {
      if (e.target === fullscreenContainer) {
        document.body.removeChild(fullscreenContainer);
      }
    };
    
    // Закрытие по ESC
    const handleEsc = (e) => {
      if (e.key === 'Escape') {
        document.body.removeChild(fullscreenContainer);
        document.removeEventListener('keydown', handleEsc);
      }
    };
    document.addEventListener('keydown', handleEsc);
    
  } catch (error) {
    console.error('❌ Ошибка открытия полноэкранного просмотра:', error);
  }
};

const shareToTelegram = () => {
  try {
    console.log('🔄 Starting Telegram share with app closing...');
    
    const nftData = htmlModal.value.item;
    
    if (!nftData) {
      console.error('❌ No NFT data available');
      showNotification('No NFT data available', 'error');
      return;
    }

    const itemId = nftData.item_id || nftData.id;
    if (!itemId) {
      console.error('❌ No item ID available');
      showNotification('Cannot generate share link', 'error');
      return;
    }

    // Создаем ссылку на товар
    const shareUrl = `${window.location.origin}/shop/${itemId}`;
    console.log('🔗 Share URL:', shareUrl);
    
    const nftName = getNftDisplayName(nftData.nft_type, nftData.nft_object);
    const nftId = extractNftId(nftData.nft_object || nftData);
    const price = nftData.price_per_unit || 'N/A';
    const currency = nftData.currency || 'TON';
    
    const message = `🎁 ${nftName} #${nftId}\n💰 ${price} ${currency}\n\n${shareUrl}`;
    console.log('📝 Message:', message);

    // Основной метод для Telegram Mini Apps - сворачивает апп и открывает интерфейс пересылки
    if (window.Telegram && window.Telegram.WebApp) {
      console.log('📱 Using Telegram WebApp API');
      
      // Метод 1: openTelegramLink - сворачивает мини-апп и открывает ссылку в Telegram
      if (window.Telegram.WebApp.openTelegramLink) {
        try {
          // Создаем ссылку для пересылки сообщения
          const telegramShareUrl = `https://t.me/share/url?url=${encodeURIComponent(shareUrl)}&text=${encodeURIComponent(message)}`;
          
          // Этот метод сворачивает мини-апп и открывает ссылку в основном интерфейсе Telegram
          window.Telegram.WebApp.openTelegramLink(telegramShareUrl);
          console.log('✅ Telegram.WebApp.openTelegramLink called - app should close');
          return;
        } catch (linkError) {
          console.error('❌ openTelegramLink failed:', linkError);
        }
      }
      
      // Метод 2: close() + открытие ссылки
      if (window.Telegram.WebApp.close) {
        try {
          const telegramShareUrl = `https://t.me/share/url?url=${encodeURIComponent(shareUrl)}&text=${encodeURIComponent(message)}`;
          
          // Сначала сворачиваем мини-апп
          window.Telegram.WebApp.close();
          
          // Затем открываем ссылку (это сработает после сворачивания)
          setTimeout(() => {
            window.location.href = telegramShareUrl;
          }, 100);
          
          console.log('✅ Telegram.WebApp.close called + link opening');
          return;
        } catch (closeError) {
          console.error('❌ close failed:', closeError);
        }
      }
    }

    // Fallback для случаев вне Telegram
    console.log('🔄 Using fallback method outside Telegram');
    const telegramShareUrl = `https://t.me/share/url?url=${encodeURIComponent(shareUrl)}&text=${encodeURIComponent(message)}`;
    window.open(telegramShareUrl, '_blank');
    
  } catch (error) {
    console.error('❌ Error in shareToTelegram:', error);
    showNotification('Error sharing to Telegram', 'error');
  }
};
// Функция для логирования всех символов с возможностью полноэкранного просмотра
const logSymbolsWithFullscreenPreview = async () => {
  const symbols = new Set(marketItems.value.map(item => extractSymbolFromNft(item)).filter(Boolean));
  
  console.log('🎨 Доступные символы для полноэкранного просмотра:');
  
  for (const symbol of symbols) {
    const tgsUrl = `https://gifts.coffin.meme/patterns/${symbol.toLowerCase().replace(/\s+/g, '%20')}.tgs`;
    
    // Создаем интерактивный элемент в консоли
    console.log(
      `%c🔗 ${symbol}`,
      `color: blue; cursor: pointer; font-size: 16px; text-decoration: underline;`,
      `- ${tgsUrl}`
    );
    
    // Добавляем обработчик клика (работает в некоторых консолях)
    console.log(
      `%c 👆 Нажмите здесь для полноэкранного просмотра "${symbol}"`,
      `color: green; font-size: 14px; cursor: pointer;`
    );
    
    // Для реального использования лучше создать UI кнопки
    console.log(`Для просмотра "${symbol}" выполните: openTgsFullscreen("${tgsUrl}", "${symbol}")`);
  }
};

// Интеграция с вашим существующим кодом - добавьте кнопку для полноэкранного просмотра TGS
const addTgsFullscreenButton = (item) => {
  const symbol = extractSymbolFromNft(item);
  if (symbol) {
    const tgsUrl = `https://gifts.coffin.meme/patterns/${symbol.toLowerCase().replace(/\s+/g, '%20')}.tgs`;
    
    // Создаем кнопку для полноэкранного просмотра
    const fullscreenButton = document.createElement('button');
    fullscreenButton.textContent = '🎨 Полноэкранный просмотр';
    fullscreenButton.style.cssText = `
      background: #007bff;
      color: white;
      border: none;
      padding: 10px 15px;
      border-radius: 5px;
      cursor: pointer;
      margin: 10px 0;
    `;
    
    fullscreenButton.onclick = () => {
      openTgsFullscreen(tgsUrl, symbol);
    };
    
    // Добавляем кнопку в интерфейс (нужно адаптировать под вашу структуру)
    const actionsContainer = document.querySelector('.action-buttons'); // Замените на ваш селектор
    if (actionsContainer) {
      actionsContainer.appendChild(fullscreenButton);
    }
  }
};
// В script секции, добавьте ref и метод replayHtmlAnimation

// В script секции, добавьте метод replayHtmlAnimation
const htmlIframe = ref(null);

// Функция для извлечения ID из URL
const extractGiftIdFromUrl = (url) => {
  if (!url) return 0;
  const match = url.match(/-(\d+)(?:\?|$)/);
  return match ? parseInt(match[1]) : 0;
};

// Функция для извлечения Gift ID из nft_object
const extractGiftIdFromNftObject = (nftObject) => {
  try {
    if (!nftObject) return 0;
    
    const obj = typeof nftObject === 'string' ? JSON.parse(nftObject) : nftObject;
    if (!obj.url) return 0;
    
    const match = obj.url.match(/-(\d+)(?:\?|$)/);
    return match ? parseInt(match[1]) : 0;
  } catch (error) {
    console.error('Error extracting gift ID:', error);
    return 0;
  }
};


// Функция для извлечения редкости модели из nft_object
const extractModelRarityFromNftObject = (nftObject) => {
  try {
    if (!nftObject) return 0;
    
    const obj = typeof nftObject === 'string' ? JSON.parse(nftObject) : nftObject;
    if (!obj.model) return 0;
    
    const match = obj.model.match(/(\d+\.?\d*)%/);
    return match ? parseFloat(match[1]) : 0;
  } catch (error) {
    console.error('Error parsing model rarity:', error);
    return 0;
  }
};

// Функция для извлечения данных из nft_object
const parseNftObject = (item) => {
  try {
    if (!item.nft_object) return { giftId: 0, modelRarity: 0 };
    
    const nftObj = typeof item.nft_object === 'string' 
      ? JSON.parse(item.nft_object) 
      : item.nft_object;
    
    return {
      giftId: extractGiftIdFromUrl(nftObj.url),
      modelRarity: extractModelRarityFromNftObject(item.nft_object)
    };
  } catch (error) {
    console.error('Error parsing nft_object:', error);
    return { giftId: 0, modelRarity: 0 };
  }
};

const applySort = (sortType) => {
  sortMenu.value.selected = sortType;
  sortMenu.value.show = false;
  
  // Применяем сортировку к filteredMarketItems
  applySortingToMarketItems(sortType);
};

const applySortingToMarketItems = (sortType) => {
  if (!filteredMarketItems.value) return;
  
  const items = [...filteredMarketItems.value];
  
  switch (sortType) {
    case 'latest':
      // Сортировка по дате создания (предполагая, что есть поле created_at)
      items.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
      break;
      
    case 'price_low_high':
      items.sort((a, b) => a.price_per_unit - b.price_per_unit);
      break;
      
    case 'price_high_low':
      items.sort((a, b) => b.price_per_unit - a.price_per_unit);
      break;
      
    case 'id_asc':
      items.sort((a, b) => {
        const aData = parseNftObject(a);
        const bData = parseNftObject(b);
        return aData.giftId - bData.giftId;
      });
      break;
      
    case 'id_desc':
      items.sort((a, b) => {
        const aData = parseNftObject(a);
        const bData = parseNftObject(b);
        return bData.giftId - aData.giftId;
      });
      break;
      
    case 'model_rarity_asc':
      items.sort((a, b) => {
        const aData = parseNftObject(a);
        const bData = parseNftObject(b);
        return aData.modelRarity - bData.modelRarity;
      });
      break;
      
    case 'model_rarity_desc':
      items.sort((a, b) => {
        const aData = parseNftObject(a);
        const bData = parseNftObject(b);
        return bData.modelRarity - aData.modelRarity;
      });
      break;
      
    default:
      // По умолчанию сортируем по latest
      items.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  }
  
  // Обновляем отображаемые элементы
  filteredMarketItems.value = items;
};



const extractRarityPercentage = (category, item) => {
  try {
    if (!item.nft_object) return null;
    
    const nftObj = typeof item.nft_object === 'string' 
      ? JSON.parse(item.nft_object) 
      : item.nft_object;
    
    let fieldValue = '';
    
    switch (category) {
      case 'symbol':
        fieldValue = nftObj.symbol || '';
        break;
      case 'backdrop':
        fieldValue = nftObj.backdrop || '';
        break;
      default:
        return null;
    }
    
    // Извлекаем процент из строки (формат: "Название X.X%")
    const percentageMatch = fieldValue.match(/(\d+\.?\d*)%/);
    return percentageMatch ? percentageMatch[1] + '%' : null;
    
  } catch (error) {
    console.error(`Error extracting ${category} rarity:`, error);
    return null;
  }
};

// Функция для получения среднего процента редкости по всем предметам
const getAverageRarityPercentage = (category, optionName) => {
  const items = getCurrentDataSource.value;
  const percentages = [];
  
  items.forEach(item => {
    const extractedName = category === 'symbol' 
      ? extractSymbolFromNft(item) 
      : extractBackdropFromNft(item);
    
    if (extractedName && normalizeSymbolName(extractedName) === normalizeSymbolName(optionName)) {
      const percentage = extractRarityPercentage(category, item);
      if (percentage) {
        percentages.push(parseFloat(percentage));
      }
    }
  });
  
  if (percentages.length === 0) return null;
  
  // Вычисляем среднее значение
  const average = percentages.reduce((sum, val) => sum + val, 0) / percentages.length;
  return average.toFixed(1) + '%';
};



// В разделе refs замените sortMenu:
const sortMenu = ref({
  show: false,
  selected: 'latest',
  options: [
    { id: 'latest', name: 'Latest' },
    { id: 'price_low_high', name: 'Price: Low to High' },
    { id: 'price_high_low', name: 'Price: High to Low' },
    { id: 'id_asc', name: 'Gift ID: Ascending' },
    { id: 'id_desc', name: 'Gift ID: Descending' },
    { id: 'model_rarity_asc', name: 'Model rarity: Ascending' },
    { id: 'model_rarity_desc', name: 'Model rarity: Descending' }
  ]
});


const priceRangeMenu = ref({
  show: false,
  minPrice: null,
  maxPrice: null
});

const currentSort = ref('newest');
const priceRange = ref({
  min: null,
  max: null
});

// Функции для работы с меню
const toggleSortMenu = () => {
  sortMenu.value.show = !sortMenu.value.show;
  priceRangeMenu.value.show = false;
  cartMenu.value.show = false;
};


const applyPriceRange = () => {
  console.log('Applying price range:', {
    min: priceRangeMenu.value.minPrice,
    max: priceRangeMenu.value.maxPrice
  });
  priceRangeMenu.value.show = false;
  // Здесь должна быть логика применения фильтра по цене
};

const resetPriceRange = () => {
  priceRangeMenu.value.minPrice = null;
  priceRangeMenu.value.maxPrice = null;
  console.log('Price range reset');
  // Здесь должна быть логика сброса фильтра по цене
};
const togglePriceRangeMenu = () => {
  priceRangeMenu.value.show = !priceRangeMenu.value.show;
  sortMenu.value.show = false;
  cartMenu.value.show = false;
};

// Функция получения названия опции сортировки
const getSortOptionName = (sortId) => {
  const option = sortMenu.value.options.find(opt => opt.id === sortId);
  return option ? option.name : 'Unknown';
};

// Вспомогательная функция для извлечения ID из NFT типа
const extractIdFromNftType = (nftType) => {
  try {
    const match = nftType.match(/(\d+)$/);
    return match ? parseInt(match[1]) : 0;
  } catch {
    return 0;
  }
};

// В секции computed свойств обновите filteredMarketItems
// В секции computed свойств обновите filteredMarketItems
const filteredMarketItems = computed(() => {
  const items = getCurrentDataSource.value;
  
  return items.filter(item => {
    if (priceRangeMenu.value.minPrice !== null || priceRangeMenu.value.maxPrice !== null) {
      const itemPrice = item.price_per_unit;
      
      if (priceRangeMenu.value.minPrice !== null && itemPrice < priceRangeMenu.value.minPrice) {
        return false;
      }
      
      if (priceRangeMenu.value.maxPrice !== null && itemPrice > priceRangeMenu.value.maxPrice) {
        return false;
      }
    }
    // NFT фильтр - должен работать независимо
    if (selectedFilters.value.nft.length > 0) {
      const itemName = getNftDisplayName(item.nft_type, item.nft_object);
      const normalizedItemName = normalizeNftName(itemName);
      
      const passesNftFilter = selectedFilters.value.nft.some(selectedNft => {
        const normalizedSelected = normalizeNftName(selectedNft);
        return normalizedItemName.includes(normalizedSelected);
      });
      if (!passesNftFilter) return false;
    }
    
    // Model фильтр - должен работать независимо от NFT
    if (selectedFilters.value.model.length > 0) {
      const itemModel = extractModelFromNft(item);
      if (!itemModel) return false;
      
      const cleanItemModel = itemModel.toLowerCase().trim();
      const passesModelFilter = selectedFilters.value.model.some(selectedModel => {
        const cleanSelectedModel = selectedModel.toLowerCase().trim();
        return cleanItemModel === cleanSelectedModel;
      });
      if (!passesModelFilter) return false;
    }
    
    // Symbol фильтр
    if (selectedFilters.value.symbol.length > 0) {
      const itemSymbol = extractSymbolFromNft(item);
      if (!itemSymbol) return false;
      
      const normalizedItemSymbol = normalizeSymbolName(itemSymbol);
      const passesSymbolFilter = selectedFilters.value.symbol.some(selectedSymbol => {
        const normalizedSelectedSymbol = normalizeSymbolName(selectedSymbol);
        return normalizedItemSymbol === normalizedSelectedSymbol;
      });
      if (!passesSymbolFilter) return false;
    }
    
    // Backdrop фильтр
    if (selectedFilters.value.backdrop.length > 0) {
      const itemBackdrop = extractBackdropFromNft(item);
      if (!itemBackdrop) return false;
      
      const cleanItemBackdrop = itemBackdrop.toLowerCase().trim();
      const passesBackdropFilter = selectedFilters.value.backdrop.some(selectedBackdrop => {
        const cleanSelectedBackdrop = selectedBackdrop.toLowerCase().trim();
        return cleanItemBackdrop === cleanSelectedBackdrop;
      });
      if (!passesBackdropFilter) return false;
    }
    
    // ID фильтр
    if (selectedIdFilter.value !== null) {
      const itemId = extractGiftIdFromNftObject(item.nft_object);
      if (parseInt(itemId) !== selectedIdFilter.value) return false;
    }
    
    return true;
  }).sort((a, b) => {
    // Новая логика сортировки согласно требованиям
    switch (sortMenu.value.selected) {
      case 'price_low_high':
        return a.price_per_unit - b.price_per_unit;
      case 'price_high_low':
        return b.price_per_unit - a.price_per_unit;
      case 'id_asc':
        return extractGiftIdFromNftObject(a.nft_object) - extractGiftIdFromNftObject(b.nft_object);
      case 'id_desc':
        return extractGiftIdFromNftObject(b.nft_object) - extractGiftIdFromNftObject(a.nft_object);
      case 'model_rarity_asc':
        return extractModelRarityFromNftObject(a.nft_object) - extractModelRarityFromNftObject(b.nft_object);
      case 'model_rarity_desc':
        return extractModelRarityFromNftObject(b.nft_object) - extractModelRarityFromNftObject(a.nft_object);
      default: // 'latest'
        return new Date(b.created_at || 0) - new Date(a.created_at || 0);
    }
  });
});

const applyCurrentSort = (items) => {
  const sortType = sortMenu.value.selected;
  
  switch (sortType) {
    case 'latest':
      return items.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
      
    case 'price_low_high':
      return items.sort((a, b) => a.price_per_unit - b.price_per_unit);
      
    case 'price_high_low':
      return items.sort((a, b) => b.price_per_unit - a.price_per_unit);
      
    case 'id_asc':
      return items.sort((a, b) => {
        const aData = parseNftObject(a);
        const bData = parseNftObject(b);
        return aData.giftId - bData.giftId;
      });
      
    case 'id_desc':
      return items.sort((a, b) => {
        const aData = parseNftObject(a);
        const bData = parseNftObject(b);
        return bData.giftId - aData.giftId;
      });
      
    case 'model_rarity_asc':
      return items.sort((a, b) => {
        const aData = parseNftObject(a);
        const bData = parseNftObject(b);
        return aData.modelRarity - bData.modelRarity;
      });
      
    case 'model_rarity_desc':
      return items.sort((a, b) => {
        const aData = parseNftObject(a);
        const bData = parseNftObject(b);
        return bData.modelRarity - aData.modelRarity;
      });
      
    default:
      return items.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  }
};

// Функции для получения доступных опций с учетом текущих фильтров
const getAvailableNftOptions = () => {
  const currentItems = filteredMarketItems.value;
  const availableNfts = new Set();
  
  currentItems.forEach(item => {
    const itemName = getNftDisplayName(item.nft_type, item.nft_object);
    const normalizedItemName = normalizeNftName(itemName);
    availableNfts.add(normalizedItemName);
  });
  
  return Array.from(availableNfts);
};

const getAvailableModelOptions = () => {
  const currentItems = filteredMarketItems.value;
  const availableModels = new Set();
  
  currentItems.forEach(item => {
    const model = extractModelFromNft(item);
    if (model) {
      availableModels.add(model.toLowerCase());
    }
  });
  
  return Array.from(availableModels);
};

// Добавьте эти функции для получения доступных символов и фонов
const getAvailableSymbolOptions = () => {
  const availableSymbols = new Set();
  
  marketItems.value.forEach(item => {
    const symbol = extractSymbolFromNft(item);
    if (symbol) {
      const normalizedSymbol = normalizeSymbolName(symbol);
      availableSymbols.add(normalizedSymbol);
    }
  });
  
  return Array.from(availableSymbols);
};






const getAvailableBackdropOptions = () => {
  const availableBackdrops = new Set();
  
  marketItems.value.forEach(item => {
    const backdrop = extractBackdropFromNft(item);
    if (backdrop) {
      // Берем только название цвета (до первого пробела)
      const cleanBackdrop = backdrop.split(' ')[0].toLowerCase().trim();
      if (cleanBackdrop && cleanBackdrop !== 'не указано') {
        availableBackdrops.add(cleanBackdrop);
      }
    }
  });
  
  return Array.from(availableBackdrops);
};

const addSquareStyles = (htmlContent) => {
  // Добавляем инлайн-стили для квадратного отображения
  const style = `
    <style>
      body, html {
        border-radius: 12px !important;
        overflow: hidden !important;
      }
      #main-container, #animation-container, #image-container, .nft-image {
        border-radius: 12px !important;
      }
    </style>
  `;
  return htmlContent.replace('</head>', style + '</head>');
};

const forceSquareStyles = (event) => {
  // Принудительно применяем стили после загрузки
  const iframe = event.target;
  try {
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const elements = iframeDoc.querySelectorAll('body, html, #main-container, #animation-container, #image-container, .nft-image');
    elements.forEach(el => {
      el.style.borderRadius = '12px !important';
      el.style.overflow = 'hidden !important';
    });
  } catch (e) {
    console.log('Cannot access iframe content:', e);
  }
};
    

    
const idFilterValue = ref('');
    // Функция для извлечения ID из nft_object
const extractIdFromNftObject = (nftObject) => {
  try {
    if (!nftObject) return null;
    
    // Парсим nft_object (может быть строкой или объектом)
    const obj = typeof nftObject === 'string' ? JSON.parse(nftObject) : nftObject;
    
    // Проверяем разные возможные форматы URL
    if (obj.url) {
      // Формат: https://t.me/nft/DeskCalendar-66666
      const match = obj.url.match(/-(\d+)(?:\?|$)/);
      return match ? parseInt(match[1]) : null;
    }
    
    // Альтернативный вариант - проверяем другие поля
    if (obj.id) {
      return parseInt(obj.id);
    }
    
    return null;
  } catch (error) {
    console.error('Error extracting ID from nft_object:', error);
    return null;
  }
};





    const extractUrlFromHtml = (html) => {
      try {
        const iframeMatch = html.match(/<iframe[^>]*src=["']([^"']+)["']/i);
        if (iframeMatch && iframeMatch[1]) return iframeMatch[1];
        
        const urlMatch = html.match(/https?:\/\/[^\s"'<>]+/i);
        return urlMatch ? urlMatch[0] : null;
      } catch {
        return null;
      }
    };

    const dropdownPosition = ref({
      left: 0,
      width: 0
    });

    const filterButtons = ref([]);
    
    const nfts = ref({});
    const loading = ref(true);
    const marketLoading = ref(false);
    const userScore = ref(0);
    const showHistory = ref(false);
    const historyTab = ref('sales');
    const salesHistory = ref([]);
    const transfersHistory = ref([]);
    const marketHistory = ref([]);
    const loadingHistory = ref(false);
    const marketItems = ref([]);

// Обработчик скролла для lazy loading
const handleScroll = (event) => {
  if (loadingMore.value || !hasMoreOffers.value) return;
  
  const container = event.target;
  const { scrollTop, scrollHeight, clientHeight } = container;
  
  // Проверяем, достигли ли мы нижней части контейнера
  const distanceFromBottom = scrollHeight - (scrollTop + clientHeight);
  const threshold = 100; // Пикселей от нижнего края
  
  console.log('📊 Скролл позиция:', {
    scrollTop,
    scrollHeight,
    clientHeight,
    distanceFromBottom,
    threshold
  });
  
  if (distanceFromBottom <= threshold) {
    console.log('🔄 Достигнут нижний край, загружаем дополнительные офферы...');
    loadOffers(true);
  }
};

// Функция для наблюдения за скроллом
const setupScrollObserver = () => {
  nextTick(() => {
    const scrollContainer = document.querySelector('.activity-list');
    if (scrollContainer) {
      scrollContainer.addEventListener('scroll', handleScroll);
      console.log('👀 Наблюдатель скролла установлен');
    }
  });
};

    onMounted(() => {
      categoriesContainer.value?.addEventListener('scroll', handleScroll);
    });

    onUnmounted(() => {
      categoriesContainer.value?.removeEventListener('scroll', handleScroll);
    });

    const selectedNftTypes = ref([]);
    const easterEggNfts = [''];
    const featuredNfts = [''];
    



    const startHtmlModalDrag = (e) => {
      htmlModal.value.isDragging = true;
      htmlModal.value.startY = e.clientY ?? e.touches[0].clientY;
      
      document.addEventListener('mousemove', handleHtmlModalDrag);
      document.addEventListener('mouseup', stopHtmlModalDrag);
      document.addEventListener('touchmove', handleHtmlModalDrag, { passive: false });
      document.addEventListener('touchend', stopHtmlModalDrag);
    };
    
    
    

    const handleHtmlModalDrag = (e) => {
      if (!htmlModal.value.isDragging) return;
      e.preventDefault();
      
      const clientY = e.clientY ?? e.touches[0].clientY;
      const offset = clientY - htmlModal.value.startY;
      
      htmlModal.value.offset = Math.max(0, offset);
    };

    const stopHtmlModalDrag = () => {
      if (!htmlModal.value.isDragging) return;

      if (htmlModal.value.offset > window.innerHeight * 0.25) {
        closeHtmlModal();
      } else {
        htmlModal.value.isDragging = false;
        htmlModal.value.offset = 0;
      }

      document.removeEventListener('mousemove', handleHtmlModalDrag);
      document.removeEventListener('mouseup', stopHtmlModalDrag);
      document.removeEventListener('touchmove', handleHtmlModalDrag);
      document.removeEventListener('touchend', stopHtmlModalDrag);
    };

    const handleHtmlModalClose = (e) => {
      if (e.target.classList.contains('html-modal-overlay')) {
        htmlModal.value.show = false;
      }
    };

    const filteredEasterEggNfts = computed(() => {
      return easterEggNfts.filter(nft => 
        getNftDisplayName(nft).toLowerCase().includes(searchQuery.value.toLowerCase()))
    });

    const filteredFeaturedNfts = computed(() => {
      return featuredNfts.filter(nft => 
        getNftDisplayName(nft).toLowerCase().includes(searchQuery.value.toLowerCase()))
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

const buyModal = ref({
  show: false,
  item: null,
  nftType: '',
  pricePerUnit: 0,
  currency: 'TON',
  amount: 1,
  buyAmount: 1,
  loading: false // ← ДОБАВЬТЕ ЭТУ СТРОКУ
});


    const itemDetailsModal = ref({
      show: false,
      item: null,
      offset: 0,
      startY: 0,
      isDragging: false
    });

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
  const loadSymbolOptionsFromMarket = () => {
  try {
    console.log('🔄 Загрузка символов с маркета...');
    
    const symbols = new Set();
    const symbolData = [];

    // Проходим по всем элементам маркета
    marketItems.value.forEach(item => {
      const symbol = extractSymbolFromNft(item);
      if (symbol && symbol.trim() !== '') {
        const normalizedSymbol = normalizeSymbolName(symbol);
        
        if (!symbols.has(normalizedSymbol)) {
          symbols.add(normalizedSymbol);
          
          // Пытаемся найти изображение в patterns
          const symbolFromPatterns = symbolOptions.value.find(s => 
            normalizeSymbolName(s.name) === normalizedSymbol
          );
          
          symbolData.push({
            name: symbol,
            value: normalizedSymbol,
            imageUrl: symbolFromPatterns?.imageUrl || null, // Если нет в patterns - null
            count: 1
          });
        } else {
          // Увеличиваем счетчик если символ уже есть
          const existingSymbol = symbolData.find(s => 
            normalizeSymbolName(s.name) === normalizedSymbol
          );
          if (existingSymbol) {
            existingSymbol.count++;
          }
        }
      }
    });

    // Сортируем по имени
    symbolData.sort((a, b) => a.name.localeCompare(b.name));
    symbolOptions.value = symbolData;
    
    console.log(`✅ Загружено ${symbolData.length} символов с маркета:`, symbolData);
    
  } catch (error) {
    console.error('❌ Ошибка загрузки символов с маркета:', error);
    symbolOptions.value = [];
  }
};




const handleModelSearch = () => {
  // При поиске автоматически раскрываем все группы в режиме групп
  if (displayMode.value === 'grouped' && modelSearchQuery.value) {
    const newExpandedGroups = {};
    selectedFilters.value.nft.forEach(nftType => {
      newExpandedGroups[nftType] = true;
    });
    expandedNftGroups.value = newExpandedGroups;
  }
};
const getTotalModelsCount = () => {
  let total = 0;
  selectedFilters.value.nft.forEach(nftType => {
    const models = getModelsForNftSortedByRarity(nftType);
    total += models.length;
  });
  return total;
};
watch(modelSearchQuery, (newQuery) => {
  if (newQuery && displayMode.value === 'grouped') {
    // При активном поиске раскрываем все группы
    const newExpandedGroups = {};
    selectedFilters.value.nft.forEach(nftType => {
      newExpandedGroups[nftType] = true;
    });
    expandedNftGroups.value = newExpandedGroups;
  }
});

const nftDisplayNames = {
  'EasterEgg': 'Easter Egg',
  'JackInTheBox': 'Jack-in-the-Box',
  'NekoHelmet': 'Neko Helmet',
  'TopHat': 'Top Hat',
  'LovePotion': 'Love Potion',
  'ToyBear': 'Toy Bear',
  'DiamondRing': 'Diamond Ring',
  'LootBag': 'Loot Bag',
  'LunarSnake': 'Lunar Snake',
  'TamaGadget': 'Tama Gadget',
  'CandyCane': 'Candy Cane',
  'CookieHeart': 'Cookie Heart',
  'PartySparkler': 'Party Sparkler',
  'JingleBells': 'Jingle Bells',
  'GingerCookie': 'Ginger Cookie',
  'WinterWreath': 'Winter Wreath',
  'SantaHat': 'Santa Hat',
  'SnowGlobe': 'Snow Globe',
  'SnowMittens': 'Snow Mittens',
  'SleighBell': 'Sleigh Bell',
  'JesterHat': 'Jester Hat',
  'StarNotepad': 'Star Notepad',
  'BunnyMuffin': 'Bunny Muffin',
  'SwissWatch': 'Swiss Watch',
  'SignetRing': 'Signet Ring',
  'GenieLamp': 'Genie Lamp',
  'AstralShard': 'Astral Shard',
  'PreciousPeach': 'Precious Peach',
  'PlushPepe': 'Plush Pepe',
  'SpicedWine': 'Spiced Wine',
  'JellyBunny': 'Jelly Bunny',
  'HangingStar': 'Hanging Star',
  'DurovsCap': 'Durov\'s Cap',
  'LoveCandle': 'Love Candle',
  'PerfumeBottle': 'Perfume Bottle',
  'MiniOscar': 'Mini Oscar',
  'EternalRose': 'Eternal Rose',
  'BerryBox': 'Berry Box',
  'VintageCigar': 'Vintage Cigar',
  'RecordPlayer': 'Record Player',
  'MagicPotion': 'Magic Potion',
  'ElectricSkull': 'Electric Skull',
  'KissedFrog': 'Kissed Frog',
  'HypnoLollipop': 'Hypno Lollipop',
  'HexPot': 'Hex Pot',
  'EvilEye': 'Evil Eye',
  'IonGem': 'Ion Gem',
  'SharpTongue': 'Sharp Tongue',
  'MadPumpkin': 'Mad Pumpkin',
  'TrappedHeart': 'Trapped Heart',
  'SkullFlower': 'Skull Flower',
  'CrystalBall': 'Crystal Ball',
  'FlyingBroom': 'Flying Broom',
  'VoodooDoll': 'Voodoo Doll',
  'ScaredCat': 'Scared Cat',
  'WitchHat': 'Witch Hat',
  'EternalCandle': 'Eternal Candle',
  'SpyAgaric': 'Spy Agaric',
  'LolPop': 'Lol Pop',
  'SakuraFlower': 'Sakura Flower',
  'HomemadeCake': 'Homemade Cake',
  'DeskCalendar': 'Desk Calendar',
  'BDayCandle': 'B-Day Candle'
};

const imageCache = ref({});




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

    const htmlNftModal = ref({
      show: false,
      htmlContent: '',
      title: ''
    });
    
    const openHtmlNftModal = async (htmlNftId) => {
      try {
        const { data, error } = await supabase
          .from('market')
          .select('html_content, display_name')
          .eq('id', htmlNftId)
          .single();

        if (error) throw error;
        
        htmlNftModal.value = {
          show: true,
          htmlContent: data.html_content,
          title: data.display_name || 'HTML NFT'
        };
        
      } catch (error) {
        console.error('Error loading HTML NFT:', error);
        showNotification('Ошибка загрузки HTML NFT', 'error');
      }
    };

// Функция для расчета суммы с комиссией
const calculateWithCommission = (price) => {
  const commission = price * 0.02; // 2% комиссия
  return price - commission;
};

// Функция для получения комиссии
const getCommission = (price) => {
  return price * 0.02;
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

    const handleAddNft = () => {
  // Логика для добавления нового NFT
  showNotification('Функция добавления NFT будет реализована в ближайшее время', 'info');
  
  // Здесь можно открыть модальное окно для добавления NFT по ссылке или другим способом
  console.log('Add NFT clicked');
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
    const { nftData, recipientName } = transferModal.value;
    
    if (!nftData || !recipientName) {
      showNotification('Missing transfer data', 'error');
      return;
    }

    // Проверяем существование получателя
    const { data: recipientData, error: recipientError } = await supabase
      .from('users')
      .select('name, nft_links')
      .eq('name', recipientName)
      .single();

    if (recipientError || !recipientData) {
      showNotification('Recipient not found', 'error');
      return;
    }

    // Подготавливаем данные NFT для получателя
    const transferredNftData = {
      url: nftData.url || '',
      name: extractNftDataWithNumber(nftData).name,
      model: nftData.model || '',
      symbol: nftData.symbol || '',
      backdrop: nftData.backdrop || '',
      acquired_at: new Date().toISOString(),
      transferred: true,
      transferred_from: currentAccountName.value,
      transferred_at: new Date().toISOString()
    };

    // Добавляем NFT получателю
    const recipientCurrentLinks = recipientData.nft_links || [];
    const updatedRecipientLinks = [...recipientCurrentLinks, transferredNftData];

    await supabase
      .from('users')
      .update({ nft_links: updatedRecipientLinks })
      .eq('name', recipientName);

    // Удаляем NFT у отправителя
    const { data: senderData } = await supabase
      .from('users')
      .select('nft_links')
      .eq('name', currentAccountName.value)
      .single();

    if (senderData && senderData.nft_links) {
      const updatedSenderLinks = senderData.nft_links.filter(nft => 
        nft.url !== nftData.url
      );

      await supabase
        .from('users')
        .update({ nft_links: updatedSenderLinks })
        .eq('name', currentAccountName.value);
    }

    showNotification('NFT transferred successfully!', 'success');
    transferModal.value.show = false;
    
    // Обновляем локальные данные
    await loadUnlistedNfts();

  } catch (error) {
    console.error('Transfer failed:', error);
    showNotification('Transfer failed', 'error');
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
    
    

const getActivityNftHtml = (activity) => {
  try {
    // Проверяем, есть ли это объявление на рынке
    const isOnMarket = checkIfActivityItemIsOnMarket(activity);
    
    if (isOnMarket) {
      // Если объявление есть на рынке - используем компактный вид
      return generateNftHtmlForListActivity(activity.nft_object || activity);
    } else {
      // Если объявления нет на рынке - используем полноэкранный вид
      return generateNftHtmlForFullscreenActivity(activity.nft_object || activity);
    }
  } catch (error) {
    console.error('Error generating activity NFT HTML:', error);
    // Fallback на полноэкранный вид при ошибке
    return generateNftHtmlForFullscreenActivity(activity.nft_object || activity);
  }
};
// Добавьте эту функцию для проверки возможностей
const checkTelegramCapabilities = () => {
  if (window.Telegram && window.Telegram.WebApp) {
    console.log('📱 Telegram WebApp detected');
    console.log('🔧 Available methods:', {
      shareMessage: !!window.Telegram.WebApp.shareMessage,
      openTelegramLink: !!window.Telegram.WebApp.openTelegramLink,
      openLink: !!window.Telegram.WebApp.openLink,
      version: window.Telegram.WebApp.version
    });
  } else {
    console.log('❌ Telegram WebApp not detected');
  }
};
// Функция для предварительной загрузки изображений NFT
const preloadNftImages = async (nftOptions) => {
  for (const option of nftOptions) {
    if (!nftImageUrls.value[option.originalType]) {
      try {
        const url = await getNftImage(option.originalType);
        nftImageUrls.value[option.originalType] = url;
        console.log(`✅ Предзагружено изображение для ${option.name}: ${url}`);
      } catch (error) {
        console.warn(`❌ Не удалось загрузить изображение для ${option.name}`);
      }
    }
  }
};

// Вызовите проверку при монтировании
onMounted(() => {
  checkTelegramCapabilities();
});
// Вспомогательная функция для проверки наличия объявления на рынке
const checkIfActivityItemIsOnMarket = (activity) => {
  try {
    // Проверяем по item_id или другим идентификаторам
    if (activity.item_id) {
      return marketItems.value.some(item => item.item_id === activity.item_id);
    }
    
    // Альтернативная проверка по данным NFT
    if (activity.nft_object) {
      const nftId = extractNftIdFromData(activity.nft_object);
      return marketItems.value.some(item => {
        const itemNftId = extractNftIdFromData(item.nft_object || item);
        return itemNftId === nftId;
      });
    }
    
    return false;
  } catch (error) {
    console.error('Error checking if activity item is on market:', error);
    return false;
  }
};

// Вспомогательная функция для извлечения имени NFT из активности
const extractNftNameFromActivity = (activity) => {
  try {
    if (activity.nft_type) {
      return getNftDisplayName(activity.nft_type, activity.nft_object);
    }
    
    if (activity.nft_object) {
      const nftObj = typeof activity.nft_object === 'string' 
        ? JSON.parse(activity.nft_object) 
        : activity.nft_object;
      
      if (nftObj.url) {
        const match = nftObj.url.match(/\/nft\/([^-]+)/);
        if (match && match[1]) {
          return match[1].replace(/([A-Z])/g, ' $1').trim();
        }
      }
    }
    
    return 'Unknown NFT';
  } catch (error) {
    console.error('Error extracting NFT name from activity:', error);
    return 'Unknown NFT';
  }
};








// Обновите существующие функции для записи активности:

// В executeBuy добавьте:
const recordBuyActivity = async (item) => {
  await addActivityRecord({
    item_id: item.item_id,
    nft_type: item.nft_type,
    nft_object: item.nft_object,
    html_content: item.html_content,
    operation_type: 'buy',
    price_per_unit: item.price_per_unit,
    currency: item.currency,
    amount: item.amount,
    total_price: item.total_price,
    counterparty: item.seller
  });
};

// В executeSell добавьте:
const recordSellActivity = async (item) => {
  await addActivityRecord({
    item_id: item.item_id,
    nft_type: item.nft_type,
    nft_object: item.nft_object,
    html_content: item.html_content,
    operation_type: 'sell',
    price_per_unit: item.price_per_unit,
    currency: item.currency,
    amount: item.amount,
    total_price: item.total_price
  });
};

// В executeCancelSale добавьте:
const recordCancelActivity = async (item) => {
  await addActivityRecord({
    item_id: item.item_id,
    nft_type: item.nft_type,
    nft_object: item.nft_object,
    html_content: item.html_content,
    operation_type: 'cancel_sale',
    price_per_unit: item.price_per_unit,
    currency: item.currency,
    amount: item.amount
  });
};

// Обновите mounted для загрузки истории
onMounted(async () => {
  // ... существующий код ...
  
  // Загружаем историю если пользователь авторизован
  if (currentAccountName.value) {
    await loadActivityHistory();
  }
});













// Функция для генерации ID для таблицы market
const generateMarketId = () => {
  return 'market_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
};
// Функция для генерации числового ID (временное решение)
const generateNumericId = () => {
  return Date.now() + Math.floor(Math.random() * 1000);
};

// В функции executeSell используйте:
const marketData = {
  id: generateNumericId(), // Числовой ID
  item_id: generateItemId(),
  // ... остальные поля
};
// Функция для генерации следующего порядкового ID
const generateNextMarketId = async () => {
  try {
    // Получаем максимальный ID из таблицы market
    const { data, error } = await supabase
      .from('market')
      .select('id')
      .order('id', { ascending: false })
      .limit(1);
    
    if (error) throw error;
    
    // Если есть записи, берем максимальный ID + 1, иначе начинаем с 1
    const maxId = data && data.length > 0 ? data[0].id : 0;
    return maxId + 1;
    
  } catch (error) {
    console.error('Ошибка получения максимального ID:', error);
    // Fallback - начинаем с 1
    return 1;
  }
};
const nftImageUrls = ref({});
const isNftImagesLoading = ref(false);
const nftImagesLoadAttempts = ref({}); // Счетчик попыток загрузки для каждого NFT

const loadNftImages = async (nftTypesWithNames) => {
  // Защита от параллельных вызовов
  if (isNftImagesLoading.value) {
    console.log('⏳ Загрузка изображений уже выполняется, пропускаем...');
    return;
  }

  const urls = {...nftImageUrls.value};
  
  // Фильтруем только те NFT, для которых изображения ещё не загружены
  const typesToLoad = nftTypesWithNames.filter(([type, name]) => {
    const attempts = nftImagesLoadAttempts.value[type] || 0;
    const shouldLoad = !urls[type] && attempts < 3;
    
    if (shouldLoad) {
      console.log(`📥 Будет загружено: ${name} (${type})`);
    }
    
    return shouldLoad;
  });
  
  if (typesToLoad.length === 0) {
    console.log('✅ Все изображения уже загружены или превышен лимит попыток');
    console.log('📊 Текущие nftImageUrls:', Object.keys(urls));
    return;
  }

  console.log(`🔄 Загрузка ${typesToLoad.length} изображений`);
  isNftImagesLoading.value = true;

  try {
    // Загружаем все изображения ОДНОРАЗОВО
    const loadPromises = typesToLoad.map(async ([nftType, nftName]) => {
      try {
        // Увеличиваем счетчик попыток
        nftImagesLoadAttempts.value[nftType] = (nftImagesLoadAttempts.value[nftType] || 0) + 1;
        
        console.log(`🎯 Загрузка изображения для: ${nftName} (${nftType})`);
        
        // Получаем модель из существующей функции
        const model = await getRandomModelForNft(nftName);
        
        if (model) {
          // Используем единую функцию генерации URL
          const imageUrl = generateCorrectImageUrl(nftName, model);
          
          console.log(`🔗 Генерация URL для ${nftName}: ${imageUrl}`);
          
          // Проверяем существование изображения
          const exists = await checkImageExists(imageUrl);
          
          if (exists) {
            urls[nftType] = imageUrl;
            console.log(`✅ Изображение найдено: ${imageUrl}`);
            
            // Сбрасываем счетчик попыток при успехе
            nftImagesLoadAttempts.value[nftType] = 0;
            
            // НЕМЕДЛЕННО обновляем для этого NFT
            nftImageUrls.value = { ...nftImageUrls.value, [nftType]: imageUrl };
          } else {
            console.warn(`❌ Изображение не существует: ${imageUrl}`);
          }
        } else {
          console.warn(`❌ Модель не найдена для: ${nftName}`);
        }
        
      } catch (error) {
        console.error(`Ошибка загрузки для ${nftName}:`, error);
      }
    });

    // Ждем завершения всех загрузок
    await Promise.all(loadPromises);
    
  } catch (error) {
    console.error('🔥 Общая ошибка загрузки изображений:', error);
  } finally {
    // Устанавливаем fallback для NFT, которые так и не загрузились
    typesToLoad.forEach(([nftType, nftName]) => {
      if (!urls[nftType] && (nftImagesLoadAttempts.value[nftType] || 0) >= 3) {
        urls[nftType] = default_nft_image;
        console.log(`🔄 Установлен fallback для ${nftName} после 3 попыток`);
        
        // НЕМЕДЛЕННО обновляем fallback
        nftImageUrls.value = { ...nftImageUrls.value, [nftType]: default_nft_image };
      }
    });
    
    isNftImagesLoading.value = false;
    
    console.log('🎨 Загрузка изображений завершена');
    console.log('📊 Итоговые nftImageUrls:', JSON.parse(JSON.stringify(nftImageUrls.value)));
  }
};

// Добавьте эту функцию для перехвата всех созданий изображений
const debugImageCreation = () => {
  const originalImage = window.Image;
  
  window.Image = class extends originalImage {
    constructor() {
      super();
      const originalSetSrc = Object.getOwnPropertyDescriptor(originalImage.prototype, 'src');
      
      Object.defineProperty(this, 'src', {
        get: () => originalSetSrc.get.call(this),
        set: (value) => {
          console.log('🖼️ Создается изображение с URL:', value);
          if (value.includes('%20') || value.includes('gifts.coffin.meme')) {
            console.trace('❌ Обнаружен старый URL, требуется исправление');
          }
          originalSetSrc.set.call(this, value);
        }
      });
    }
  };
};

// Вызовите в mounted
debugImageCreation();
const executeSell = async () => {
  try {
    // Защита от повторных нажатий
    if (sellModal.value.loading) {
      console.log('⏳ Продажа уже обрабатывается, пожалуйста подождите...');
      return;
    }
    
    // Блокируем кнопку
    sellModal.value.loading = true;
    
    const { nftType, price, amount, nftData, isHtmlNft } = sellModal.value;
    
    // Дополнительная проверка данных
    if (!price || price <= 0) {
      showNotification('Пожалуйста, введите корректную цену', 'error');
      sellModal.value.loading = false;
      return;
    }

    const marketId = await generateNextMarketId();
    const itemId = generateItemId();

    // ТОЛЬКО ОСНОВНЫЕ ДАННЫЕ
    const marketData = {
      id: marketId,
      item_id: itemId,
      nft_type: nftType,
      nft_object: nftData,
      seller: currentAccountName.value,
      price_per_unit: parseFloat(price), // Цена БЕЗ комиссии
      currency: 'TON',
      amount: amount || 1,
      total_price: parseFloat(price) * (amount || 1),
      created_at: new Date().toISOString()
    };

    if (isHtmlNft && nftData) {
      marketData.html_content = generateNftHtmlForList(nftData);
    }

    console.log('🔄 Сохранение NFT на рынок...', marketData);

    // Вставляем в market
    const { data, error } = await supabase
      .from('market')
      .insert([marketData])
      .select();

    if (error) throw error;

    console.log('✅ NFT успешно размещено на рынке');

    // Дальше твой обычный код...
    if (nftData && nftData.url) {
      await removeNftFromUserCollection(nftData);
    }

    if (nftData && nftData.url) {
      myUnlistedNfts.value = myUnlistedNfts.value.filter(
        nft => nft.url !== nftData.url
      );
    }

    await recordListingActivity(data[0]);
    await loadMarketItems();

    showNotification('NFT успешно выставлено на продажу!', 'success');
    
    // Сбрасываем модальное окно
    sellModal.value.show = false;
    sellModal.value.confirmStep = false;
    
    if (htmlModal.value.show) {
      htmlModal.value.show = false;
    }
    
    showSuccessAnimation('listing');

  } catch (error) {
    console.error('❌ Ошибка выставления на продажу:', error);
    showNotification(`Ошибка выставления на продажу: ${error.message}`, 'error');
  } finally {
    // ВСЕГДА разблокируем кнопку, даже при ошибке
    sellModal.value.loading = false;
  }
};
// Функция для удаления NFT из коллекции пользователя после продажи
const removeNftFromUserCollection = async (nftData) => {
  try {
    const { data: userData, error: fetchError } = await supabase
      .from('users')
      .select('nft_links')
      .eq('name', currentAccountName.value)
      .single();

    if (fetchError) throw fetchError;

    const currentLinks = userData.nft_links || [];
    
    console.log('🔍 До удаления NFT ссылок:', currentLinks.length);
    
    // Удаляем NFT из списка пользователя
    const updatedLinks = currentLinks.filter(link => {
      const linkUrl = typeof link === 'object' ? link.url : link;
      const shouldKeep = linkUrl !== nftData.url;
      if (!shouldKeep) {
        console.log('🗑️ Удаляем NFT с URL:', nftData.url);
      }
      return shouldKeep;
    });

    console.log('🔍 После удаления NFT ссылок:', updatedLinks.length);

    // Обновляем в базе данных
    const { error: updateError } = await supabase
      .from('users')
      .update({ 
        nft_links: updatedLinks,
        updated_at: new Date().toISOString()
      })
      .eq('name', currentAccountName.value);

    if (updateError) throw updateError;

    console.log('✅ NFT удалено из коллекции пользователя в базе данных');
    
  } catch (error) {
    console.error('❌ Ошибка удаления NFT из коллекции:', error);
    throw error;
  }
};
// Функция для записи активности листинга
const recordListingActivity = async (marketItem) => {
  return await addActivityRecord({
    user_name: currentAccountName.value,
    item_id: marketItem.item_id,
    nft_type: marketItem.nft_type,
    nft_object: marketItem.nft_object,
    html_content: marketItem.html_content,
    operation_type: 'listing',
    price_per_unit: marketItem.price_per_unit,
    currency: marketItem.currency,
    amount: marketItem.amount,
    total_price: marketItem.total_price
  });
};

// Функция для получения метки типа активности
const getActivityTypeLabel = (operationType) => {
  const labels = {
    'purchase': 'Purchase',
    'listing': 'Listing', 
    'price_edit': 'Edit Price',
    'delisting': 'Delisting',
    'transfer': 'Transfer',
    'offer': 'Offer'
  };
  
  return labels[operationType] || operationType;
};



// Функция для объединения типа операции и времени
const getActivityTypeWithTime = (operationType, dateString) => {
  const typeLabel = getActivityTypeLabel(operationType);
  const time = formatActivityDate(dateString);
  return `${typeLabel} • ${time}`;
};

// Функция для форматирования даты в формате "03.05 12:40"
// Функция с полным месяцем и временем
const formatActivityDate = (dateString) => {
  try {
    const date = new Date(dateString);
    
    const monthNames = [
      'January', 'February', 'March', 'April', 'May', 'June',
      'July', 'August', 'September', 'October', 'November', 'December'
    ];
    
    const day = date.getDate();
    const month = monthNames[date.getMonth()];
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    
    return `${day} ${month} ${hours}:${minutes}`;
    
  } catch (error) {
    console.error('Error formatting activity date:', error);
    return 'Unknown date';
  }
};

// Типы активности
const activityTypes = [
  { value: 'all', label: 'All' },
  { value: 'purchase', label: 'Purchases' },
  { value: 'listing', label: 'Listings' },
  { value: 'price_edit', label: 'Price Edits' }
];




// Также убедитесь, что функция initiateCancelSale правильно передает данные
const initiateCancelSale = async (item) => {
  try {
    // Проверка существования товара
    const { data: currentItem, error } = await supabase
      .from('market')
      .select('*')
      .eq('id', item.id)
      .single();

    if (error || !currentItem) {
      showNotification('This item is no longer available or has been sold', 'error');
      
      // Синхронизируем локальное состояние
      marketItems.value = marketItems.value.filter(marketItem => marketItem.id !== item.id);
      myMarketItems.value = myMarketItems.value.filter(myItem => myItem.id !== item.id);
      
      return;
    }

    // Проверяем, что пользователь действительно владелец
    if (currentItem.seller !== currentAccountName.value) {
      showNotification('You are no longer the owner of this item', 'error');
      return;
    }

    // Открываем модальное окно снятия с продажи
    cancelSaleModal.value = {
      show: true,
      item: currentItem,
      nftType: currentItem.nft_type
    };
    
  } catch (error) {
    console.error('Error initiating cancel sale:', error);
    showNotification('Error opening cancel sale dialog', 'error');
  }
};

// И проверьте, что в шаблоне правильно вызывается функция
// Вместо этого:
// <button @click="initiateCancelSale">Cancel sale</button>

// Должно быть:
// <button @click="initiateCancelSale(item)">Cancel sale</button>
  


    

// Добавьте новое reactive состояние
// Обновите reactive состояние
const purchaseSuccess = ref({
  show: false,
  animationData: null // Будет загружено из JSON
});


// Или если импорт не работает, используйте динамический импорт:
const loadAnimationData = async () => {
  try {
    const response = await fetch('@/assets/Success.json');
    purchaseSuccess.value.animationData = await response.json();
  } catch (error) {
    console.error('Error loading animation data:', error);
  }
};

// Вызовите при монтировании компонента
onMounted(() => {
  purchaseSuccess.value.animationData = SuccessAnimation;
});

const executeBuy = async () => {
  try {
    // Защита от повторных нажатий
    if (buyModal.value.loading) {
      console.log('⏳ Покупка уже обрабатывается...');
      return;
    }
    
    // Блокируем кнопку
    buyModal.value.loading = true;
    
    const { item, buyAmount, pricePerUnit, currency } = buyModal.value;

    if (!item || !buyAmount || buyAmount <= 0) {
      showNotification('Invalid purchase data', 'error');
      buyModal.value.loading = false;
      return;
    }

    console.log('🔄 Выполнение покупки...', item.id);

    // Проверяем доступность товара
    const { data: currentItem, error: checkError } = await supabase
      .from('market')
      .select('*')
      .eq('id', item.id)
      .single();

    if (checkError || !currentItem) {
      showNotification('Item is no longer available', 'error');
      buyModal.value.loading = false;
      return;
    }

    // Проверяем баланс пользователя
    const totalCost = pricePerUnit * buyAmount;
    const { data: userData } = await supabase
      .from('users')
      .select('ton_balance, nft_links')
      .eq('name', currentAccountName.value)
      .single();

    const currentBalance = parseFloat(userData.ton_balance) || 0;
    
    if (currentBalance < totalCost) {
      showNotification(`Insufficient TON balance. Need ${totalCost} TON, have ${currentBalance} TON`, 'error');
      buyModal.value.loading = false;
      return;
    }

    // Рассчитываем сумму для продавца (98%) и комиссию (2%)
    const sellerAmount = totalCost * 0.98;
    const platformFee = totalCost * 0.02;

    // Подготавливаем данные NFT
    const nftData = {
      url: item.nft_object?.url || item.url || '',
      name: getNftDisplayName(item.nft_type, item.nft_object),
      model: item.nft_object?.model || '',
      symbol: item.nft_object?.symbol || '',
      backdrop: item.nft_object?.backdrop || '',
      acquired_at: new Date().toISOString()
    };

    // Обновляем nft_links покупателя
    const currentLinks = userData.nft_links || [];
    const updatedLinks = [...currentLinks, nftData];

    // Пополняем баланс продавца
    const { data: sellerData } = await supabase
      .from('users')
      .select('ton_balance')
      .eq('name', item.seller)
      .single();

    if (sellerData) {
      const sellerCurrentBalance = parseFloat(sellerData.ton_balance) || 0;
      const newSellerBalance = sellerCurrentBalance + sellerAmount;

      await supabase
        .from('users')
        .update({ ton_balance: newSellerBalance })
        .eq('name', item.seller);
    }

    // Обновляем баланс покупателя
    const newBuyerBalance = currentBalance - totalCost;
    await supabase
      .from('users')
      .update({ 
        ton_balance: newBuyerBalance,
        nft_links: updatedLinks
      })
      .eq('name', currentAccountName.value);

    // Удаляем товар с рынка
    const { error: deleteError } = await supabase
      .from('market')
      .delete()
      .eq('id', item.id);

    if (deleteError) throw deleteError;

    // Записываем активность
    await recordPurchaseActivity(item, currentAccountName.value, buyAmount);

    console.log('✅ Покупка успешно завершена');
    
    showNotification('Purchase completed successfully!', 'success');
    
    // Закрываем модальные окна
    buyModal.value.show = false;
    
    // Показываем успешную покупку с анимацией
    showSuccessAnimation('purchase');
    
    // Закрываем fullscreen view если он открыт
    if (htmlModal.value.show) {
      htmlModal.value.show = false;
    }
    
    // Переходим на /shop
    router.push('/shop');

    // Обновляем данные
    await loadMarketItems();
    await loadUnlistedNfts();
    
    // Обновляем локальный баланс
    tonBalance.value = newBuyerBalance.toString();

  } catch (error) {
    console.error('Ошибка выполнения покупки:', error);
    showNotification('Error completing purchase', 'error');
  } finally {
    // Всегда разблокируем кнопку
    buyModal.value.loading = false;
  }
};
watch(() => [sellModal.value.price, sellModal.value.amount], () => {
  updateCalculations();
}, { immediate: true });
onMounted(async () => {
      const savedAccount = localStorage.getItem('currentAccount');
      if (savedAccount) {
        currentAccountName.value = JSON.parse(savedAccount).name;
      }
      
      if (currentAccountName.value) {
        await loadUserData();
        await loadMarketItems();
        await loadCartFromDatabase();
        await fetchUserBalance(); // ← ДОБАВИТЬ ЗДЕСЬ загрузку баланса
        
        
      }
      
    });

    // Также обновляем баланс при изменении подключения кошелька
    watch(() => props.tonConnectUI?.connected, (connected) => {
      if (connected) {
        fetchUserBalance(); // Баланс из базы данных
      } else {
        tonBalance.value = '0';
      }
    }, { immediate: true });
onMounted(() => {
  // Обработка открытия по item_id из URL
  const route = useRoute();
  
  // Если в URL есть item_id, открываем соответствующий NFT
  if (route.params.itemId) {
    const item = findItemByItemId(route.params.itemId);
    if (item) {
      openFullscreenView(item);
    }
  }

  // Обработка сообщений от iframe
  window.addEventListener('message', (event) => {
    if (event.data.type === 'openFullscreenView') {
      const item = findItemById(event.data.nftId, event.data.nftName);
      if (item && item.item_id) {
        // Используем router для навигации с item_id
        router.push(`/shop/${item.item_id}`);
      } else if (item) {
        openFullscreenView(item);
      }
    }
  });
});

    const getAllModelData = () => {
  try {
    const allModelData = [];
    
    // Проходим по всем выбранным NFT и собираем данные моделей
    selectedFilters.value.nft.forEach(nftType => {
      if (nftModelsCache.value[nftType]) {
        nftModelsCache.value[nftType].forEach(modelString => {
          // Парсим строку модели (формат: "Название — процент%")
          const parts = modelString.split(' — ');
          if (parts.length === 2) {
            const name = parts[0].trim();
            const rarity = parts[1].trim().replace('%', '');
            
            // Проверяем, нет ли уже такой модели в списке
            if (name && !allModelData.some(item => item.name === name)) {
              allModelData.push({
                name,
                rarity,
                parentNft: nftType
              });
            }
          }
        });
      }
    });
    
    // Сортируем по названию
    allModelData.sort((a, b) => a.name.localeCompare(b.name));
    
    console.log(`Всего моделей с данными: ${allModelData.length}`);
    return allModelData;
    
  } catch (error) {
    console.error('Ошибка получения данных моделей:', error);
    return [];
  }
};
const scrollContainer = ref(null);

const extractMetadataFromUnlistedNft = (nftData) => {
  try {
    let model = 'Не указано';
    let modelPercentage = '';
    let symbol = 'Не указано';
    let symbolPercentage = '';
    let backdrop = 'Не указано';
    let backdropPercentage = '';

    // Если данные содержат метаданные в объекте
    if (nftData.model) {
      const modelParts = nftData.model.split(' ');
      if (modelParts.length > 1) {
        modelPercentage = modelParts.pop();
        model = modelParts.join(' ');
      } else {
        model = nftData.model;
      }
    }

    if (nftData.symbol) {
      const symbolParts = nftData.symbol.split(' ');
      if (symbolParts.length > 1) {
        symbolPercentage = symbolParts.pop();
        symbol = symbolParts.join(' ');
      } else {
        symbol = nftData.symbol;
      }
    }

    if (nftData.backdrop) {
      const backdropParts = nftData.backdrop.split(' ');
      if (backdropParts.length > 1) {
        backdropPercentage = backdropParts.pop();
        backdrop = backdropParts.join(' ');
      } else {
        backdrop = nftData.backdrop;
      }
    }

    // Альтернативно, пытаемся извлечь из URL или других полей
    if (model === 'Не указано' && nftData.url) {
      // Пытаемся извлечь информацию из URL
      const urlMatch = nftData.url.match(/\/nft\/([^-]+)/);
      if (urlMatch && urlMatch[1]) {
        model = urlMatch[1].replace(/([A-Z])/g, ' $1').trim();
      }
    }

    return {
      model,
      modelPercentage,
      symbol,
      symbolPercentage,
      backdrop,
      backdropPercentage
    };
  } catch (error) {
    console.error('Ошибка извлечения метаданных из unlisted NFT:', error);
    return {
      model: 'Не указано',
      modelPercentage: '',
      symbol: 'Не указано',
      symbolPercentage: '',
      backdrop: 'Не указано',
      backdropPercentage: ''
    };
  }
};

watch(modelSearchQuery, (newQuery) => {
  if (newQuery && displayMode.value === 'grouped') {
    // При активном поиске раскрываем все группы
    const newExpandedGroups = {};
    selectedFilters.value.nft.forEach(nftType => {
      newExpandedGroups[nftType] = true;
    });
    expandedNftGroups.value = newExpandedGroups;
  }
});

    const showFilterMenu = () => {
      showFilterDropdown.value = true;
    };


    const handleDrag = (e) => {
      if (!isDraggingModal.value) return;
      e.preventDefault();
      
      const clientY = e.clientY ?? e.touches[0].clientY;
      dragCurrentY.value = clientY - dragStartY.value;
      
      if (dragCurrentY.value > 50) {
        closeFilterMenu();
      }
    };

    const stopDrag = () => {
      isDraggingModal.value = false;
      document.removeEventListener('mousemove', handleDrag);
      document.removeEventListener('mouseup', stopDrag);
      document.removeEventListener('touchmove', handleDrag);
      document.removeEventListener('touchend', stopDrag);
    };

    const handleModalClose = (e) => {
      if (e.target.classList.contains('item-details-modal-overlay')) {
        itemDetailsModal.value.show = false;
      }
    };



// Для Sell оставляем как было (без actionType)
const handleBuyClick = async (item) => {
  if (activeTab.value === 'my-nfts' && myNftsViewMode.value === 'unlisted') {
    // Для unlisted NFT открываем fullscreen с кнопкой Sell по умолчанию
    await openHtmlModalForUnlisted(item); // Без actionType = кнопка Sell
  } else if (item.html_content) {
    await openHtmlModal(item);
  } else {
    initiateBuy(item);
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
      try {
        const { data, error } = await supabase
          .from('users')
          .select('nft1, nft2, nft3, nft4, nft5, nft6, nft7, nft8, nft9, nft10, nft_links')
          .eq('name', currentAccountName.value)
          .single();

        if (error) throw error;

        if (data) {
          nfts.value = Object.fromEntries(
            Object.entries(data).filter(([key, val]) => 
              key.startsWith('nft') && !key.includes('links') && val > 0
            )
          );

          htmlNfts.value = (data.nft_links || []).map((item, index) => ({
            id: `html_nft_${index}`,
            ...item
          }));
        }
            await loadUnlistedNfts();

      } catch (error) {
        console.error('Ошибка загрузки данных пользователя:', error);
      }
    };

    const goBack = () => {
      router.go(-1);
    };
    const initiateBuyFromFullscreen = async () => {
  if (!htmlModal.value.item) {
    return;
  }
  
  await initiateBuy(htmlModal.value.item);
};
// В onMounted добавьте:
const setupRealtimeUpdates = () => {
  const marketSubscription = supabase
    .channel('market_realtime')
    .on(
      'postgres_changes',
      {
        event: '*',
        schema: 'public',
        table: 'market'
      },
      (payload) => {
        console.log('Market update received:', payload);
        
        if (payload.eventType === 'DELETE') {
          // Удаляем товар из всех локальных списков
          const deletedId = payload.old.id;
          marketItems.value = marketItems.value.filter(item => item.id !== deletedId);
          
          // Удаляем из корзины
          if (isInCart(deletedId)) {
            removeFromCart(deletedId);
          }
          
          // Закрываем модальные окна если они открыты для этого товара
          if (htmlModal.value.show && htmlModal.value.item?.id === deletedId) {
            htmlModal.value.show = false;
          }
          if (cancelSaleModal.value.show && cancelSaleModal.value.item?.id === deletedId) {
            cancelSaleModal.value.show = false;
          }
        } 
        else if (payload.eventType === 'INSERT') {
          // Добавляем новый товар
          marketItems.value.unshift(payload.new);
        }
        else if (payload.eventType === 'UPDATE') {
          // Обновляем существующий товар
          const index = marketItems.value.findIndex(item => item.id === payload.new.id);
          if (index !== -1) {
            marketItems.value[index] = payload.new;
          }
        }
      }
    )
    .subscribe();

  return marketSubscription;
};


// Функция для создания уникального ключа объявления
const createMarketItemKey = (item) => {
  // Для HTML NFT используем URL как уникальный идентификатор
  if (item.nft_type?.startsWith('html_nft_') && item.nft_object) {
    try {
      const nftObj = typeof item.nft_object === 'string' ? JSON.parse(item.nft_object) : item.nft_object;
      if (nftObj.url) {
        return `html_${nftObj.url}_${item.seller}`;
      }
    } catch (e) {
      console.error('Error parsing nft_object:', e);
    }
  }
  
  // Для обычных NFT используем комбинацию полей
  return `${item.nft_type}_${item.seller}_${item.price_per_unit}_${item.amount || 1}_${item.nft_object || ''}`;
};

// Функция для пометки дубликата на удаление
const markDuplicateForRemoval = async (duplicateId) => {
  try {
    const { error } = await supabase
      .from('market')
      .delete()
      .eq('id', duplicateId);
      
    if (error) {
      console.error('❌ Ошибка удаления дубликата:', error);
    } else {
      console.log(`🗑️ Дубликат ${duplicateId} удален из базы`);
    }
  } catch (error) {
    console.error('❌ Ошибка при удалении дубликата:', error);
  }
};

// Добавьте эту функцию для проверки дубликатов
const checkForDuplicates = async () => {
  try {
    console.log('🔍 Проверка на дубликаты...');
    
    const { data: allItems, error } = await supabase
      .from('market')
      .select('*');
    
    if (error) throw error;

    const duplicates = [];
    const seen = new Map(); // item_id -> first occurrence
    
    allItems.forEach(item => {
      const key = generateItemKey(item);
      
      if (seen.has(key)) {
        duplicates.push({
          duplicate: item,
          original: seen.get(key)
        });
      } else {
        seen.set(key, item);
      }
    });
    
    if (duplicates.length > 0) {
      console.log(`🗑️ Найдено ${duplicates.length} дубликатов:`, duplicates);
      
      // Удаляем дубликаты
      const deletePromises = duplicates.map(async ({ duplicate }) => {
        const { error: deleteError } = await supabase
          .from('market')
          .delete()
          .eq('id', duplicate.id);
        
        if (deleteError) {
          console.error('❌ Ошибка удаления дубликата:', deleteError);
        } else {
          console.log('✅ Дубликат удален:', duplicate.id);
        }
      });
      
      await Promise.all(deletePromises);
      showNotification(`Удалено ${duplicates.length} дубликатов`, 'success');
    } else {
      console.log('✅ Дубликаты не найдены');
    }
    
    return duplicates.length;
  } catch (error) {
    console.error('❌ Ошибка проверки дубликатов:', error);
    return 0;
  }
};

// Функция для генерации уникального ключа для каждого товара
const generateItemKey = (item) => {
  // Создаем уникальный ключ на основе основных характеристик
  const nftData = item.nft_object ? (typeof item.nft_object === 'string' ? JSON.parse(item.nft_object) : item.nft_object) : {};
  
  return [
    item.seller,
    item.nft_type,
    nftData.url || '',
    nftData.model || '',
    nftData.symbol || '', 
    nftData.backdrop || '',
    item.price_per_unit,
    item.currency
  ].join('|');
};

// Функция проверки перед добавлением на рынок
const checkDuplicateBeforeListing = async (itemData) => {
  try {
    const { data: existingItems, error } = await supabase
      .from('market')
      .select('*')
      .eq('seller', itemData.seller)
      .eq('nft_type', itemData.nft_type);
    
    if (error) throw error;

    const newItemKey = generateItemKey(itemData);
    
    const isDuplicate = existingItems.some(existingItem => {
      const existingKey = generateItemKey(existingItem);
      return existingKey === newItemKey;
    });
    
    return isDuplicate;
  } catch (error) {
    console.error('❌ Ошибка проверки дубликата:', error);
    return false;
  }
};


// Функция для периодической проверки дубликатов
const startDuplicateChecker = () => {
  // Проверяем каждые 30 секунд
  setInterval(() => {
    checkForDuplicates();
  }, 30000);
  
  // Также проверяем при загрузке страницы
  checkForDuplicates();
};

// Добавьте в onMounted
onMounted(() => {
  // ... существующий код
  
  // Запускаем проверку дубликатов
  startDuplicateChecker();
  
  // Подписка на изменения рынка для проверки дубликатов
  const marketSubscription = supabase
    .channel('market_duplicates_check')
    .on(
      'postgres_changes',
      {
        event: 'INSERT',
        schema: 'public',
        table: 'market'
      },
      (payload) => {
        // Проверяем новые добавления на дубликаты
        setTimeout(() => {
          checkForDuplicates();
        }, 1000);
      }
    )
    .subscribe();
});

// Также обновите функцию loadMarketItems для проверки дубликатов
const loadMarketItems = async () => {
  try {
    loading.value = true;
    
    // Сначала проверяем дубликаты
    await checkForDuplicates();
    
    // Затем загружаем данные
    const { data, error } = await supabase
      .from('market')
      .select('*')
      .order('created_at', { ascending: false });
    
    if (error) throw error;
    
    marketItems.value = data || [];
    
  } catch (error) {
    console.error('Ошибка загрузки товаров:', error);
    marketItems.value = [];
  } finally {
    loading.value = false;
  }
};

   const shopStore = useShopStore()
    const activeTab = computed(() => shopStore.activeTab)

    const setActiveTab = (tab) => {
      shopStore.setActiveTab(tab)
    }

    const router = useRouter()

    // Основные данные
    const loadingOffers = ref(false)
    const offersItems = ref([])
    const showOnlyMyOffers = ref(true)
    const offersSubscription = ref(null)
// В секции setup() добавьте все необходимые ref переменные:
const displayedOffers = ref([]);
const offersLoading = ref(false);
const loadingMore = ref(false);
const currentPage = ref(0);
const pageSize = ref(10);
const loadMoreSize = ref(20);
const hasMoreOffers = ref(true);
const totalOffersCount = ref(0);

// Также добавьте другие используемые переменные:
const selectedOfferType = ref('all');
const selectedFilters = ref({
  nft: [],
  model: [],
  symbol: [],
  backdrop: [],
  price: []
});
const selectedIdFilter = ref(null);
const currentAccountName = ref('');
    // Типы офферов
    // Типы офферов
    const offerTypes = ref([
      { value: 'all', label: 'All' },
      { value: 'accepted', label: 'Accepted' },
      { value: 'pending', label: 'Pending' },

    ])


    // Переключение типа оффера
    const setOfferType = (type) => {
      selectedOfferType.value = type
    }

    // Переключение "My Offers"
    const toggleMyOffers = () => {
      showOnlyMyOffers.value = !showOnlyMyOffers.value
      console.log(`🔍 My Offers: ${showOnlyMyOffers.value ? 'ON' : 'OFF'}`)
    }

    // Форматирование даты
    const formatOfferDate = (dateString) => {
      try {
        if (!dateString) return 'Unknown date'
        
        const date = new Date(dateString)
        const now = new Date()
        const diffTime = Math.abs(now - date)
        const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
        
        if (diffDays === 0) {
          return 'Today'
        } else if (diffDays === 1) {
          return 'Yesterday'
        } else if (diffDays < 7) {
          return `${diffDays} days ago`
        } else {
          return date.toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric'
          })
        }
      } catch (error) {
        return 'Unknown date'
      }
    }



    // Извлечение ID NFT
    const extractNftId = (nftObject) => {
      try {
        if (!nftObject) return 'Unknown'
        
        const nftObj = typeof nftObject === 'string' ? JSON.parse(nftObject) : nftObject
        if (nftObj && nftObj.url) {
          const match = nftObj.url.match(/-(\d+)(?:\?|$)/)
          return match ? match[1] : 'Unknown'
        }
        return 'Unknown'
      } catch (error) {
        console.error('Error extracting NFT ID:', error)
        return 'Error'
      }
    }

    // Метка статуса оффера
    const getOfferStatusLabel = (status) => {
      if (!status) return 'Unknown Status'
      
      const statusMap = {
        'pending': 'Pending',
        'accepted': 'Accepted',
        'expired': 'Expired',
        'cancelled': 'Cancelled'
      }
      return statusMap[status] || status
    }

    // Форматирование цены
    const formatPrice = (price) => {
      if (!price) return '0.00'
      return parseFloat(price).toFixed(2)
    }

    // Генерация HTML для NFT (аналогично существующей функции)
    const generateNftHtmlForList = (nftData) => {
      try {
        if (!nftData) {
          throw new Error('nftData is undefined')
        }
        
        const nftId = extractNftIdFromData(nftData)
        const nftNameMatch = nftData.url?.match(/\/nft\/([^-]+)/)
        const nftName = nftNameMatch ? nftNameMatch[1] : 'unknown'
        
        return `
<!DOCTYPE html>
<html>
<head>
  <title>NFT Display - ${nftName}-${nftId}</title>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/bodymovin/5.12.2/lottie.min.js"><\/script>
  <style>
    body, html {
      margin: 0;
      padding: 0;
      width: 100%;
      height: 100%;
      background: transparent;
      overflow: hidden;
      cursor: pointer;
    }
    #main-container {
      width: 100%;
      height: 100%;
      position: relative;
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    #animation-container {
      width: 100%;
      height: 100%;
      position: relative;
      overflow: hidden;
      flex-grow: 1;
    }
    #image-container {
      width: 100%;
      height: 100%;
      position: absolute;
      top: 0;
      left: 0;
      display: none;
      background: transparent;
      overflow: hidden;
    }
    .nft-image {
      width: 100%;
      height: 100%;
      object-fit: contain;
    }
  </style>
</head>
<body>
  <div id="main-container">
    <div id="animation-container"></div>
    <div id="image-container"></div>
  </div>
  <script>
    let currentAnimation = null;
    let currentImage = null;
    let animationLoaded = false;

    function loadAnimationWhenVisible() {
      if (currentAnimation) {
        currentAnimation.destroy();
        currentAnimation = null;
      }
      
      if (currentImage && currentImage.parentNode) {
        currentImage.parentNode.removeChild(currentImage);
        currentImage = null;
      }
      
      document.getElementById('animation-container').style.display = 'block';
      document.getElementById('image-container').style.display = 'none';
      document.getElementById('animation-container').innerHTML = '';

      currentAnimation = lottie.loadAnimation({
        container: document.getElementById("animation-container"),
        renderer: "svg",
        loop: false,
        autoplay: true,
        path: "https://nft.fragment.com/gift/${nftName}-${nftId}.lottie.json"
      });

      currentImage = new Image();
      currentImage.src = "https://nft.fragment.com/gift/${nftName}-${nftId}.webp";
      currentImage.className = 'nft-image';
      
      document.getElementById('image-container').innerHTML = '';
      document.getElementById('image-container').appendChild(currentImage);

      currentAnimation.addEventListener('complete', function() {
        if (currentImage.complete && currentImage.naturalWidth !== 0) {
          document.getElementById('animation-container').style.display = 'none';
          document.getElementById('image-container').style.display = 'block';
        } else {
          currentImage.onload = function() {
            document.getElementById('animation-container').style.display = 'none';
            document.getElementById('image-container').style.display = 'block';
          };
          currentImage.onerror = function() {
            console.error('Failed to load image, keeping animation');
          };
        }
      });

      animationLoaded = true;
    }

    // Обработчик клика - открываем полноэкранный просмотр
    document.addEventListener('click', function() {
      if (window.parent) {
        window.parent.postMessage({
          type: 'openFullscreenView',
          nftId: '${nftId}',
          nftName: '${nftName}'
        }, '*');
      }
    });

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting && !animationLoaded) {
          loadAnimationWhenVisible();
          observer.disconnect();
        }
      });
    }, { threshold: 0.1 });

    observer.observe(document.getElementById('main-container'));

    setTimeout(() => {
      if (!animationLoaded && document.getElementById('main-container').getBoundingClientRect().top < window.innerHeight) {
        loadAnimationWhenVisible();
        observer.disconnect();
      }
    }, 100);
  <\/script>
</body>
</html>
        `
      } catch (error) {
        console.error('Error generating NFT HTML for list:', error)
        return `
          <div style="width: 100%; height: 100%; background: #f0f0f0; display: flex; align-items: center; justify-content: center; cursor: pointer;">
            <div style="text-align: center;">
              <h3>Error loading NFT</h3>
              <p>Click to open</p>
            </div>
          </div>
        `
      }
    }


    const getOfferNftName = (offer) => {
      try {
        if (offer.nft_data) {
          const nftData = typeof offer.nft_data === 'string' 
            ? JSON.parse(offer.nft_data) 
            : offer.nft_data
          
          if (nftData.name) {
            return nftData.name
          }
          
          // Если нет name, извлекаем из URL
          if (nftData.url) {
            const match = nftData.url.match(/\/nft\/([^-]+)/)
            if (match && match[1]) {
              const name = match[1]
              return name.replace(/([A-Z])/g, ' $1').trim()
            }
          }
        }
        
        // Fallback
        return `Offer #${offer.id.slice(0, 8)}`
        
      } catch (error) {
        console.error('Error in getOfferNftName:', error)
        return 'Unknown NFT'
      }
    }

    // ФУНКЦИЯ: Извлечение ID NFT из nft_data
    const extractOfferNftId = (offer) => {
      try {
        if (offer.nft_data) {
          const nftData = typeof offer.nft_data === 'string' 
            ? JSON.parse(offer.nft_data) 
            : offer.nft_data
          
          if (nftData.url) {
            const match = nftData.url.match(/-(\d+)(?:\?|$)/)
            return match ? match[1] : 'Unknown'
          }
        }
        
        // Fallback на ID оффера
        return offer.id.slice(-6)
        
      } catch (error) {
        console.error('Error extracting offer NFT ID:', error)
        return 'Error'
      }
    }

    // ФУНКЦИЯ: Получение атрибутов NFT (model, symbol, backdrop)
    const getNftAttributes = (nftData) => {
      try {
        if (!nftData) return null
        
        const data = typeof nftData === 'string' ? JSON.parse(nftData) : nftData
        const attributes = []
        
        if (data.model) attributes.push(data.model)
        if (data.symbol) attributes.push(data.symbol)
        if (data.backdrop) attributes.push(data.backdrop)
        
        return attributes.length > 0 ? attributes.join(' • ') : null
        
      } catch (error) {
        console.error('Error getting NFT attributes:', error)
        return null
      }
    }


// Функция для получения имени колонки в БД - используем оригинальные имена
const getDbColumnName = (nftDisplayName) => {
  console.log(`🗂️ Получение имени колонки для: "${nftDisplayName}"`);
  
  // В БД колонки называются именно как отображаемые имена
  // "Jack-in-the-Box", "Lol Pop" и т.д.
  const dbName = nftDisplayName;
  
  console.log(`✅ Имя колонки в БД: "${dbName}"`);
  return dbName;
};

// Функция загрузки моделей из базы данных с экранированием имен колонок
const loadModelsFromDatabase = async (dbColumnName) => {
  try {
    console.log(`📥 Загрузка моделей из БД для колонки: "${dbColumnName}"`);
    
    // Экранируем имя колонки для SQL
    const quotedColumnName = `"${dbColumnName}"`;
    console.log(`🔧 Экранированное имя колонки: ${quotedColumnName}`);
    
    const { data, error } = await supabase
      .from('nft')
      .select(quotedColumnName)
      .not(quotedColumnName, 'is', null)
      .limit(1);
    
    if (error) {
      console.error('❌ Ошибка запроса к БД:', error);
      return null;
    }
    
    if (!data || data.length === 0) {
      console.warn(`❌ Нет данных в БД для колонки: ${dbColumnName}`);
      return null;
    }
    
    const modelsArray = data[0][dbColumnName];
    
    if (!Array.isArray(modelsArray)) {
      console.warn(`❌ Данные не являются массивом:`, modelsArray);
      return null;
    }
    
    console.log(`✅ Загружено ${modelsArray.length} моделей из БД`);
    return modelsArray;
    
  } catch (error) {
    console.error('❌ Ошибка загрузки из БД:', error);
    return null;
  }
};

// Основная функция для генерации URL с реальными моделями из БД
const generateNftImageUrlWithRealModel = async (nftDisplayName) => {
  try {
    console.log(`🔄 Генерация URL для NFT: "${nftDisplayName}"`);
    
    // Получаем случайную модель ИЗ БАЗЫ ДАННЫХ
    const randomModel = await getRandomModelFromDatabase(nftDisplayName);
    
    if (!randomModel) {
      console.warn(`❌ Не найдены модели в БД для NFT: ${nftDisplayName}`);
      // Попробуем использовать существующую функцию как fallback
      const fallbackUrl = await generateFallbackUrl(nftDisplayName);
      return fallbackUrl;
    }
    
    console.log(`🎲 Случайная модель из БД: "${randomModel}" для NFT: "${nftDisplayName}"`);
    
    // Очищаем имена для URL (только буквы a-z в нижнем регистре)
    const cleanNftPath = nftDisplayName.toLowerCase().replace(/[^a-z]/g, '');
    const cleanModelPath = randomModel.toLowerCase().replace(/[^a-z]/g, '');
    
    console.log('🔧 Очищенные пути:', {
      originalNft: nftDisplayName,
      cleanNftPath,
      originalModel: randomModel,
      cleanModelPath
    });
    
    // Проверяем что пути не пустые
    if (!cleanNftPath || !cleanModelPath) {
      console.warn('❌ Пустые пути после очистки');
      return await generateFallbackUrl(nftDisplayName);
    }
    
    const newFormatUrl = `https://storage.portal-market.com/portals-market/gifts/${cleanNftPath}/models/png/${cleanModelPath}.png`;
    
    console.log(`✅ Новый формат URL: ${newFormatUrl}`);
    
    return newFormatUrl;
    
  } catch (error) {
    console.error('❌ Ошибка генерации URL:', error);
    return await generateFallbackUrl(nftDisplayName);
  }
};

// Fallback функция если не удалось загрузить из БД
const generateFallbackUrl = async (nftDisplayName) => {
  try {
    console.log(`🔄 Используем fallback для: ${nftDisplayName}`);
    
    // Пробуем получить модель через существующую функцию
    const randomModel = await getRandomModelForNft(nftDisplayName);
    
    if (randomModel) {
      // Генерируем legacy URL
      const formattedNftName = nftDisplayName.replace(/\s+/g, '%20');
      const formattedModelName = randomModel.replace(/\s+/g, '%20');
      const legacyUrl = `https://gifts.coffin.meme/${formattedNftName}/${formattedModelName}.png`;
      
      console.log(`🔄 Fallback legacy URL: ${legacyUrl}`);
      return legacyUrl;
    }
  } catch (error) {
    console.error('❌ Ошибка fallback:', error);
  }
  
  return default_nft_image;
};

// Функция для получения случайной модели ИЗ БАЗЫ ДАННЫХ
const getRandomModelFromDatabase = async (nftDisplayName) => {
  try {
    console.log(`🔍 Поиск моделей в БД для: "${nftDisplayName}"`);
    
    // Получаем имя колонки для БД (оригинальное имя)
    const dbColumnName = getDbColumnName(nftDisplayName);
    
    if (!dbColumnName) {
      console.warn(`❌ Не найдено имя колонки для: ${nftDisplayName}`);
      return null;
    }
    
    console.log(`📁 Имя колонки в БД: "${dbColumnName}"`);
    
    // Загружаем модели из базы данных
    const models = await loadModelsFromDatabase(dbColumnName);
    
    if (!models || models.length === 0) {
      console.warn(`❌ Нет моделей в БД для: ${dbColumnName}`);
      return null;
    }
    
    console.log(`📊 Загружено моделей из БД: ${models.length}`);
    
    // Выбираем случайную модель
    const randomIndex = Math.floor(Math.random() * models.length);
    const randomModelString = models[randomIndex];
    
    // Извлекаем только название модели (до "—")
    const modelName = extractModelNameFromString(randomModelString);
    
    console.log(`🎲 Случайная модель: "${modelName}" из "${randomModelString}"`);
    
    return modelName;
    
  } catch (error) {
    console.error('❌ Ошибка получения модели из БД:', error);
    return null;
  }
};

// Функция извлечения названия модели из строки
const extractModelNameFromString = (modelString) => {
  if (!modelString) return null;
  
  // Разделяем по "—" и берем первую часть
  const parts = modelString.split('—');
  if (parts.length > 0) {
    const modelName = parts[0].trim();
    console.log(`✂️ Извлечено название модели: "${modelName}" из "${modelString}"`);
    return modelName;
  }
  
  // Если нет "—", возвращаем всю строку
  return modelString.trim();
};

// Упрощенный обработчик ошибок изображений для NFT фильтров
const handleNftImageError = (event, nftDisplayName) => {
  const img = event.target;
  const originalSrc = img.src;
  
  console.error('❌ Ошибка загрузки NFT изображения:', {
    src: originalSrc,
    nft: nftDisplayName
  });
  
  // Генерируем legacy URL как fallback
  const legacyUrl = generateLegacyFallbackUrl(nftDisplayName);
  console.log(`🔄 Пробуем legacy URL: ${legacyUrl}`);
  img.src = legacyUrl;
};

// Функция генерации legacy fallback URL
const generateLegacyFallbackUrl = async (nftDisplayName) => {
  try {
    // Получаем случайную модель из БД для legacy URL
    const randomModel = await getRandomModelFromDatabase(nftDisplayName);
    
    if (!randomModel) {
      // Если не получилось из БД, используем существующую функцию
      const fallbackModel = await getRandomModelForNft(nftDisplayName);
      if (!fallbackModel) return default_nft_image;
      
      const formattedNftName = nftDisplayName.replace(/\s+/g, '%20');
      const formattedModelName = fallbackModel.replace(/\s+/g, '%20');
      return `https://gifts.coffin.meme/${formattedNftName}/${formattedModelName}.png`;
    }
    
    const formattedNftName = nftDisplayName.replace(/\s+/g, '%20');
    const formattedModelName = randomModel.replace(/\s+/g, '%20');
    
    const legacyUrl = `https://gifts.coffin.meme/${formattedNftName}/${formattedModelName}.png`;
    
    console.log(`🔄 Legacy fallback URL: ${legacyUrl}`);
    return legacyUrl;
    
  } catch (error) {
    console.error('❌ Ошибка генерации legacy URL:', error);
    return default_nft_image;
  }
};

// Альтернативная функция генерации URL для NFT
const generateNftImageUrl = async (dbName, urlName) => {
  try {
    // dbName - для запросов в БД (например, "Jack-in-the-Box")
    // urlName - для генерации URL (например, "jack-in-the-box")
    
    console.log(`🔍 Поиск моделей для БД: "${dbName}", URL: "${urlName}"`);
    
    // Для БД используем оригинальное имя (dbName)
    const randomModel = await getRandomModelForNft(dbName);
    
    // Для URL используем имя в нижнем регистре (urlName)
    const formattedNftName = urlName.replace(/\s+/g, '%20');
    const formattedModelName = randomModel.replace(/\s+/g, '%20');
    
    const imageUrl = `https://gifts.coffin.meme/${formattedNftName}/${formattedModelName}.png`;
    
    console.log(`✅ Сгенерирован URL: ${imageUrl}`);
    return imageUrl;
    
  } catch (error) {
    console.error('❌ Ошибка генерации URL:', error);
    return default_nft_image;
  }
};

// Обновляем availableBackdropOptions для генерации SVG контента
const availableBackdropOptions = computed(() => {
  const availableBackdrops = {};
  const items = getCurrentDataSource.value;

  console.group('🎯 AVAILABLE BACKDROP OPTIONS FROM OFFERS');
  console.log('📊 Всего items для анализа:', items.length);
  
  // Фильтруем items
  const preFilteredItems = items.filter(item => {
    // NFT фильтр
    if (selectedFilters.value.nft.length > 0) {
      const itemName = item.nft_name;
      if (!itemName) return false;
      
      const normalizedItemName = normalizeNftName(itemName);
      
      const passesNftFilter = selectedFilters.value.nft.some(selectedNft => {
        const normalizedSelected = normalizeNftName(selectedNft);
        return normalizedItemName.includes(normalizedSelected);
      });
      if (!passesNftFilter) return false;
    }
    
    // Model фильтр
    if (selectedFilters.value.model.length > 0) {
      const itemModel = item.model;
      if (!itemModel) return false;
      
      const passesModelFilter = selectedFilters.value.model.some(selectedModel => 
        itemModel.toLowerCase().includes(selectedModel.toLowerCase())
      );
      if (!passesModelFilter) return false;
    }
    
    // Symbol фильтр
    if (selectedFilters.value.symbol.length > 0) {
      const itemSymbol = item.symbol;
      if (!itemSymbol) return false;
      
      const normalizedItemSymbol = normalizeSymbolName(itemSymbol);
      const passesSymbolFilter = selectedFilters.value.symbol.some(selectedSymbol => {
        const normalizedSelectedSymbol = normalizeSymbolName(selectedSymbol);
        return normalizedItemSymbol === normalizedSelectedSymbol;
      });
      if (!passesSymbolFilter) return false;
    }
    
    return true;
  });
  
  console.log(`📊 После префильтрации: ${preFilteredItems.length} items`);
  
  // Собираем доступные backdrop
  preFilteredItems.forEach(item => {
    const backdrop = item.backdrop;
    if (backdrop) {
      const backdropData = extractBackdropWithPercentageFromOffer(item);
      if (backdropData.name) {
        const cleanBackdrop = backdropData.name.toLowerCase().trim();
        const existing = availableBackdrops[cleanBackdrop];
        
        if (!existing || backdropData.percentage < existing.percentage) {
          // Генерируем SVG контент для backdrop
          const svgContent = generateBackdropSVG(backdropData.name);
          
          availableBackdrops[cleanBackdrop] = {
            id: cleanBackdrop,
            name: backdropData.name,
            percentage: backdropData.percentage,
            rarityText: backdropData.percentage > 0 ? `${backdropData.percentage}%` : 'N/A',
            count: 1,
            svgContent: svgContent // Добавляем SVG контент
          };
          console.log(`📋 Найден backdrop: "${backdrop}" -> "${backdropData.name}" (${backdropData.percentage}%)`);
        } else if (existing) {
          existing.count = (existing.count || 1) + 1;
        }
      }
    }
  });
  
  const result = Object.values(availableBackdrops);
  console.log(`✅ Доступные backdrop: ${result.length}`, result);
  console.groupEnd();
  
  return result;
});

// Функция генерации SVG для backdrop (должна быть у вас уже)
const generateBackdropSVG = (colorName) => {
  try {
    // Создаем корректный ID для SVG (убираем пробелы)
    const svgId = colorName.replace(/\s+/g, '_');
    
    // Получаем градиент из вашего объекта gradients
    const gradient = gradients[svgId] || gradients['Black'];
    
    return `
      <svg width="100%" height="100%" viewBox="0 0 420 420" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid slice">
        <defs>
          <radialGradient id="${svgId}" cx="50%" cy="50%" fx="50%" fy="50%" r="69.65%" gradientTransform="translate(0.5, 0.5), scale(0.6667, 1), rotate(90), translate(-0.5, -0.5)">
            ${gradient.stops.map(stop => 
              `<stop stop-color="${stop.color}" offset="${stop.offset}"></stop>`
            ).join('')}
          </radialGradient>
        </defs>
        <rect x="0" y="0" width="420" height="420" fill="url(#${svgId})"></rect>
      </svg>
    `;
  } catch (error) {
    console.error('Error generating backdrop SVG:', error);
    return `
      <svg width="100%" height="100%" viewBox="0 0 420 420" xmlns="http://www.w3.org/2000/svg">
        <rect x="0" y="0" width="420" height="420" fill="#cccccc"></rect>
      </svg>
    `;
  }
};


const handleImageError = (event) => {
  const img = event.target;
  const originalSrc = img.src;
  
  console.error('❌ Ошибка загрузки изображения:', {
    src: originalSrc,
    alt: img.alt
  });
  
  // Если это новый URL, попробуем legacy URL
  if (originalSrc.includes('storage.portal-market.com')) {
    const legacyUrl = convertToLegacyUrl(originalSrc);
    console.log(`🔄 Пробуем legacy URL: ${legacyUrl}`);
    img.src = legacyUrl;
  } else {
    // Если и legacy не работает, используем fallback
    console.log('🔄 Используем fallback изображение');
    img.src = default_nft_image;
    img.onerror = null; // Предотвращаем бесконечный цикл
  }
};

// Функция конвертации нового URL в legacy
const convertToLegacyUrl = (newUrl) => {
  try {
    // Извлекаем части из нового URL
    const matches = newUrl.match(/gifts\/([^\/]+)\/models\/png\/([^\.]+)/);
    if (matches) {
      const nftName = matches[1];
      const modelName = matches[2];
      
      // Конвертируем обратно в читаемый формат
      const readableNft = nftName.replace(/([a-z])([A-Z])/g, '$1 $2');
      const readableModel = modelName.replace(/([a-z])([A-Z])/g, '$1 $2');
      
      const legacyUrl = `https://gifts.coffin.meme/${readableNft.replace(/\s+/g, '%20')}/${readableModel.replace(/\s+/g, '%20')}.png`;
      return legacyUrl;
    }
  } catch (error) {
    console.error('Ошибка конвертации URL:', error);
  }
  
  return default_nft_image;
};

onMounted(async () => {
  await loadAllOffers(); // Загружаем все offers
  // ... остальной код
});
// Добавляем новое reactive свойство для всех offers





const getOfferNftHtml = (offer) => {
  try {
    // Всегда используем generateNftHtmlForFullscreenMyGifts для генерации анимации
    if (offer.nft_data) {
      const nftData = typeof offer.nft_data === 'string' 
        ? JSON.parse(offer.nft_data) 
        : offer.nft_data
      
      return generateNftHtmlForFullscreenMyGifts(nftData)
    }
    
    // Fallback если нет nft_data
    const nftName = getOfferNftName(offer)
    return `
      <div style="width: 100%; height: 100%; background: #f0f0f0; display: flex; align-items: center; justify-content: center;">
        <div style="text-align: center;">
          <h3>NFT Preview</h3>
          <p>Offer on ${nftName}</p>
        </div>
      </div>
    `
  } catch (error) {
    console.error('Error generating offer NFT HTML:', error)
    return `
      <div style="width: 100%; height: 100%; background: #f0f0f0; display: flex; align-items: center; justify-content: center;">
        <div style="text-align: center;">
          <h3>Error loading NFT</h3>
        </div>
      </div>
    `
  }
}
const getNftDisplayName = (nftType, nftObject = null) => {
  try {
    console.log('🔍 Получение имени NFT:', { nftType, nftObject });
    
    let displayName = 'Unknown NFT';
    
    // Пытаемся извлечь имя из nft_object
    if (nftObject) {
      try {
        const nftObj = typeof nftObject === 'string' ? JSON.parse(nftObject) : nftObject;
        
        // Пробуем разные поля, где может быть имя
        if (nftObj.name) {
          displayName = nftObj.name;
          console.log('✅ Имя из nft_object.name:', displayName);
        } else if (nftObj.url) {
          // Извлекаем имя из URL
          const nameFromUrl = extractNftNameFromUrl(nftObj.url);
          if (nameFromUrl) {
            displayName = formatNftDisplayName(nameFromUrl);
            console.log('✅ Имя из URL:', displayName);
          }
        }
      } catch (parseError) {
        console.warn('❌ Ошибка парсинга nft_object:', parseError);
      }
    }
    
    // Если из nft_object не получили имя, пробуем из nftType
    if (displayName === 'Unknown NFT' && nftType) {
      // Убираем префиксы
      let cleanName = nftType
        .replace('html_nft_', '')
        .replace('htmlnft', '')
        .replace('nft_', '');
      
      if (cleanName && cleanName !== 'unknown') {
        displayName = formatNftDisplayName(cleanName);
        console.log('✅ Имя из nftType:', displayName);
      }
    }
    
    console.log('🎯 Финальное имя NFT:', displayName);
    return displayName;
    
  } catch (error) {
    console.error('❌ Критическая ошибка в getNftDisplayName:', error);
    return 'NFT';
  }
};

// Вспомогательная функция для форматирования имени
const formatNftDisplayName = (name) => {
  if (!name) return 'Unknown NFT';
  
  return name
    .replace(/([A-Z])/g, ' $1') // Добавляем пробелы перед заглавными буквами
    .replace(/^./, str => str.toUpperCase()) // Первую букву заглавной
    .replace(/_/g, ' ') // Заменяем подчеркивания на пробелы
    .replace(/\s+/g, ' ') // Убираем лишние пробелы
    .trim();
};

// Улучшенная функция извлечения имени из URL
const extractNftNameFromUrl = (url) => {
  try {
    if (!url) return null;
    
    // Разные форматы URL:
    // https://t.me/nft/bdaycandle-224527
    // https://nft.fragment.com/gift/bdaycandle-224527.lottie.json
    const patterns = [
      /\/nft\/([^-]+)/, // /nft/name-id
      /\/gift\/([^-]+)/, // /gift/name-id
      /\/([a-zA-Z]+)-\d+/ // /name-id
    ];
    
    for (const pattern of patterns) {
      const match = url.match(pattern);
      if (match && match[1]) {
        return match[1];
      }
    }
    
    return null;
  } catch (error) {
    console.error('❌ Ошибка извлечения имени из URL:', error);
    return null;
  }
};

// Функция для извлечения ID из NFT данных
const extractNftIdFromData = (nftData) => {
  try {
    if (!nftData) return 'Unknown';
    
    // Если nftData - строка, парсим её
    const data = typeof nftData === 'string' ? JSON.parse(nftData) : nftData;
    
    // Пробуем разные источники для ID
    if (data.url) {
      const match = data.url.match(/-(\d+)(?:\?|$)/);
      return match ? match[1] : 'Unknown';
    }
    
    if (data.id) return data.id.toString();
    if (data.nft_id) return data.nft_id.toString();
    
    return 'Unknown';
  } catch (error) {
    console.error('❌ Ошибка извлечения ID:', error);
    return 'Error';
  }
};
// ФУНКЦИЯ: Генерация HTML для полноэкранного просмотра (только изображение)
const generateNftHtmlForFullscreenMyGifts = (nftData) => {
  try {
    const nftId = extractNftIdFromData(nftData);
    const nftNameMatch = nftData.url?.match(/\/nft\/([^-]+)/);
    const nftName = nftNameMatch ? nftNameMatch[1] : 'unknown';
    
    const imageUrl = `https://nft.fragment.com/gift/${nftName}-${nftId}.webp`;
    
    return `
<!DOCTYPE html>
<html>
<head>
  <title>NFT Display - ${nftName}-${nftId}</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    
    body, html {
      margin: 0;
      padding: 0;
      width: 100%;
      height: 100%;
      background: transparent;
      overflow: hidden;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    
    #image-container {
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      background: transparent;
    }
    
    .nft-image {
      max-width: 100%;
      max-height: 100%;
      object-fit: contain;
      display: block;
    }
  </style>
</head>
<body>
  <div id="image-container">
    <img src="${imageUrl}" alt="${nftName}" class="nft-image" 
         onerror="this.onerror=null; this.src='${default_nft_image}';">
  </div>
  <script>
    function reloadImage() {
      const img = document.querySelector('.nft-image');
      if (img) {
        // Добавляем timestamp для принудительной перезагрузки
        const newSrc = img.src.split('?')[0] + '?t=' + Date.now();
        img.src = newSrc;
      }
    }

    // Обработчик клика - перезагружаем изображение
    document.addEventListener('click', function() {
      reloadImage();
    });

    window.addEventListener('message', function(event) {
      if (event.data.type === 'replayAnimation') {
        reloadImage();
      }
    });

    // Уведомляем родителя о загрузке
    if (window.parent) {
      window.parent.postMessage({
        type: 'animationRestarted',
        nftId: '${nftName}-${nftId}'
      }, '*');
    }

    window.reloadImage = reloadImage;
  <\/script>
</body>
</html>
    `;
  } catch (error) {
    console.error('Error generating NFT HTML for fullscreen:', error);
    return `
      <div style="width: 100%; height: 100%; background: #f0f0f0; display: flex; align-items: center; justify-content: center; cursor: pointer;">
        <img src="${default_nft_image}" alt="Default NFT" style="max-width: 80%; max-height: 80%;">
      </div>
    `;
  }
}











// В начале секции setup, добавьте эти ref переменные
const imageUrlCache = ref({});
const nftOptionsWithImages = ref([]);

// Упрощенная и надежная версия функции
// Исправленная функция getNftImageUrl
const getNftImageUrl = async (nftType, optionName = null) => {
  try {
    // Используем переданное optionName или получаем через getNftDisplayName
    const displayName = optionName || getNftDisplayName(nftType);
    const randomModel = await getRandomModelForNft(displayName);
    
    // Форматируем имена для URL - используем option.name в нижнем регистре
    const formattedNftName = displayName.toLowerCase().replace(/\s+/g, '%20');
    const formattedModelName = randomModel.replace(/\s+/g, '%20');
    
    const imageUrl = `https://gifts.coffin.meme/${formattedNftName}/${formattedModelName}.png`;
    
    console.log(`✅ URL для ${displayName}: ${imageUrl}`);
    return imageUrl;
    
  } catch (error) {
    console.error(`❌ Ошибка генерации URL для ${nftType}:`, error);
    return default_nft_image;
  }
};


// Простая синхронная версия для немедленного отображения
const getSortedNftOptionsSync = () => {
  if (!availableNftOptions.value || availableNftOptions.value.length === 0) {
    return [];
  }

  return availableNftOptions.value.map(nftType => {
    const displayName = getNftDisplayName(nftType);
    
    return {
      name: displayName,
      originalType: nftType,
      imageUrl: default_nft_image, // временное изображение
      value: normalizeNftName(nftType),
      floorPrice: null,
      count: 0
    };
  }).sort((a, b) => a.name.localeCompare(b.name));
};

// Асинхронная версия для обновления изображений
const updateNftImages = async () => {
  if (!nftOptionsWithImages.value || nftOptionsWithImages.value.length === 0) {
    return;
  }

  const updatedOptions = [...nftOptionsWithImages.value];
  
  for (let i = 0; i < updatedOptions.length; i++) {
    const option = updatedOptions[i];
    try {
      const imageUrl = await getNftImageUrl(option.originalType, option.name);
      if (imageUrl && imageUrl !== default_nft_image) {
        updatedOptions[i] = { ...option, imageUrl };
      }
    } catch (error) {
      console.error(`❌ Ошибка обновления изображения для ${option.name}:`, error);
    }
  }
  
  nftOptionsWithImages.value = updatedOptions;
};

// Основная функция загрузки
const loadNftOptionsWithImages = async () => {
  try {
    console.log('🎯 Загрузка NFT опций...');
    
    // 1. Сначала загружаем синхронную версию для немедленного отображения
    const syncOptions = getSortedNftOptionsSync();
    nftOptionsWithImages.value = syncOptions;
    
    console.log(`✅ Синхронно загружено ${syncOptions.length} опций`);
    
    // 2. Затем асинхронно обновляем изображения
    if (syncOptions.length > 0) {
      setTimeout(() => {
        updateNftImages();
      }, 100);
    }
    
  } catch (error) {
    console.error('❌ Ошибка загрузки NFT опций:', error);
    nftOptionsWithImages.value = [];
  }
};



    // ОБНОВЛЕННАЯ ФУНКЦИЯ загрузки offers с правильными полями
    const loadOffersHistory = async () => {
      try {
        loadingOffers.value = true
        
        console.log('📊 Загрузка offers пользователя')

        const savedAccount = localStorage.getItem('currentAccount')
        if (savedAccount) {
          currentAccountName.value = JSON.parse(savedAccount).name
        }

        if (!currentAccountName.value) {
          console.log('❌ Имя пользователя не найдено')
          offersItems.value = []
          return
        }

        // Загружаем offers с полем nft_data
        const { data, error } = await supabase
          .from('offers')
          .select('*')
          .eq('buyer_name', currentAccountName.value)
          .order('created_at', { ascending: false })

        if (error) {
          console.error('❌ Ошибка загрузки offers:', error)
          offersItems.value = []
        } else {
          console.log(`✅ Загружено ${data?.length || 0} offers`)
          
          // Отладочная информация о структуре данных
          console.log('🔍 Структура offers данных:')
          data.forEach((offer, index) => {
            console.log(`Offer ${index + 1}:`, {
              id: offer.id,
              has_nft_data: !!offer.nft_data,
              nft_data: offer.nft_data,
              buyer_name: offer.buyer_name,
              seller_name: offer.seller_name,
              status: offer.status
            })
          })
          
          offersItems.value = data || []
        }
        
      } catch (error) {
        console.error('❌ Общая ошибка загрузки offers:', error)
        offersItems.value = []
      } finally {
        loadingOffers.value = false
      }
    }

// В секции ref добавьте:
const allOffers = ref([]); // Все офферы из базы
const filteredOffers = ref([]); // Отфильтрованные офферы

const offersPage = ref(1);
const initialLoadCount = 10; // Первоначальная загрузка
const loadMoreCount = 20; // Подгрузка при скролле
    // Добавьте эти ref переменные
// В секции ref добавьте:
const offers = ref([]); // Все офферы

const offersPerPage = ref(10);
const loadMoreThreshold = 20; // Загружать новые когда осталось 20 элементов


// Функция для загрузки офферов с пагинацией и фильтрацией
const loadOffers = async (loadMore = false) => {
  if (offersLoading.value || (loadMore && loadingMore.value) || (loadMore && !hasMoreOffers.value)) {
    console.log('⏸️ Загрузка пропущена:', {
      offersLoading: offersLoading.value,
      loadingMore: loadingMore.value,
      hasMore: hasMoreOffers.value,
      loadMore
    });
    return;
  }
  
  try {
    if (loadMore) {
      loadingMore.value = true;
      console.log('📥 Начинаем загрузку дополнительных офферов...');
    } else {
      offersLoading.value = true;
      currentPage.value = 0;
      displayedOffers.value = [];
      console.log('📥 Начинаем первоначальную загрузку офферов...');
    }

    const from = loadMore ? displayedOffers.value.length : 0;
    const limit = loadMore ? loadMoreSize.value : pageSize.value;

    console.log(`📊 Параметры загрузки: from ${from}, limit ${limit}`, {
      loadMore,
      currentDisplayed: displayedOffers.value.length,
      filters: {
        myOffers: showOnlyMyActivity.value,
        offerType: selectedOfferType.value
      }
    });

    // Строим базовый запрос
    let query = supabase
      .from('offers')
      .select('*', { count: 'exact' })
      .order('created_at', { ascending: false })
      .range(from, from + limit - 1);

    // Применяем фильтры
    query = applyFiltersToQuery(query);

    const { data, error, count } = await query;

    if (error) {
      console.error('❌ Ошибка загрузки офферов:', error);
      return;
    }

    const loadedCount = data?.length || 0;
    console.log(`✅ Загружено ${loadedCount} офферов (всего в базе: ${count})`);

    if (data && loadedCount > 0) {
      if (loadMore) {
        displayedOffers.value = [...displayedOffers.value, ...data];
        console.log(`📈 Добавлено ${loadedCount} офферов. Всего отображается: ${displayedOffers.value.length}`);
      } else {
        displayedOffers.value = data;
        console.log(`🔄 Установлено ${loadedCount} офферов`);
      }
      
      currentPage.value += 1;
    }

    // Проверяем, есть ли еще офферы для загрузки
    const totalLoaded = from + loadedCount;
    hasMoreOffers.value = totalLoaded < (count || 0);
    totalOffersCount.value = count || 0;

    console.log(`📊 Состояние пагинации:`, {
      displayed: displayedOffers.value.length,
      total: totalOffersCount.value,
      hasMore: hasMoreOffers.value,
      nextLoad: loadMore ? 'Дополнительная загрузка' : 'Первая загрузка'
    });

  } catch (error) {
    console.error('❌ Общая ошибка загрузки офферов:', error);
  } finally {
    offersLoading.value = false;
    loadingMore.value = false;
    console.log('🏁 Загрузка завершена');
  }
};

// Функция применения фильтров к запросу Supabase
const applyFiltersToQuery = (query) => {
  let filteredQuery = query;

  // ФИЛЬТРАЦИЯ ПО MY OFFERS
  if (showOnlyMyActivity.value) {
    // Когда ползунок ВКЛЮЧЕН - показываем полученные офферы
    filteredQuery = filteredQuery.eq('seller_name', currentAccountName.value)
                                 .neq('buyer_name', currentAccountName.value);
  } else {
    // Когда ползунок ВЫКЛЮЧЕН - показываем отправленные офферы  
    filteredQuery = filteredQuery.neq('seller_name', currentAccountName.value)
                                 .eq('buyer_name', currentAccountName.value);
  }

  // Фильтрация по типу оффера
  if (selectedOfferType.value && selectedOfferType.value !== 'all') {
    filteredQuery = filteredQuery.eq('status', selectedOfferType.value);
  }

  // Фильтрация по ID (если нужно)
  if (selectedIdFilter.value !== null) {
    // Для фильтрации по ID NFT нужно использовать текстовый поиск в nft_data
    // Это сложнее, так как требует фильтрации по JSON полю
    console.log('⚠️ Фильтрация по ID требует дополнительной реализации');
  }

  // Примечание: фильтрация по NFT, модели, символу, backdrop 
  // требует сложных запросов к JSON полям и лучше делается на клиенте
  // или требует дополнительных индексов в базе данных

  return filteredQuery;
};

// Функция для применения клиентских фильтров (для сложных фильтров)
const applyClientSideFilters = (offers) => {
  if (!offers || offers.length === 0) return offers;

  let filtered = [...offers];
  const filterLog = [];

  // ФИЛЬТРАЦИЯ ПО NFT (клиентская)
  if (selectedFilters.value.nft && selectedFilters.value.nft.length > 0) {
    const before = filtered.length;
    filtered = filtered.filter(offer => {
      try {
        const nftData = offer.nft_data || offer.nft_object;
        if (!nftData || !nftData.name) return false;
        
        const offerNftName = nftData.name;
        const normalizedOfferNft = normalizeNftName(offerNftName);
        
        return selectedFilters.value.nft.some(selectedNft => {
          const normalizedSelected = normalizeNftName(selectedNft);
          return normalizedOfferNft.includes(normalizedSelected);
        });
      } catch (error) {
        console.error('❌ Ошибка фильтрации по NFT:', error);
        return false;
      }
    });
    filterLog.push(`NFT: ${before} -> ${filtered.length}`);
  }

  // ФИЛЬТРАЦИЯ ПО МОДЕЛИ (клиентская)
  if (selectedFilters.value.model && selectedFilters.value.model.length > 0) {
    const before = filtered.length;
    filtered = filtered.filter(offer => {
      try {
        const nftData = offer.nft_data || offer.nft_object;
        if (!nftData || !nftData.model) return false;
        
        const offerModel = nftData.model.replace(/\d+\.?\d*%/, '').trim().toLowerCase();
        
        return selectedFilters.value.model.some(selectedModel => {
          const normalizedSelected = selectedModel.toLowerCase().trim();
          return offerModel.includes(normalizedSelected);
        });
      } catch (error) {
        console.error('❌ Ошибка фильтрации по модели:', error);
        return false;
      }
    });
    filterLog.push(`Модель: ${before} -> ${filtered.length}`);
  }

  // ФИЛЬТРАЦИЯ ПО СИМВОЛУ (клиентская)
  if (selectedFilters.value.symbol && selectedFilters.value.symbol.length > 0) {
    const before = filtered.length;
    filtered = filtered.filter(offer => {
      try {
        const nftData = offer.nft_data || offer.nft_object;
        if (!nftData || !nftData.symbol) return false;
        
        const offerSymbol = nftData.symbol.replace(/\d+\.?\d*%/, '').trim().toLowerCase();
        
        return selectedFilters.value.symbol.some(selectedSymbol => {
          const normalizedSelected = normalizeSymbolName(selectedSymbol);
          return offerSymbol === normalizedSelected;
        });
      } catch (error) {
        console.error('❌ Ошибка фильтрации по символу:', error);
        return false;
      }
    });
    filterLog.push(`Символ: ${before} -> ${filtered.length}`);
  }

  // ФИЛЬТРАЦИЯ ПО BACKDROP (клиентская)
  if (selectedFilters.value.backdrop && selectedFilters.value.backdrop.length > 0) {
    const before = filtered.length;
    filtered = filtered.filter(offer => {
      try {
        const nftData = offer.nft_data || offer.nft_object;
        if (!nftData || !nftData.backdrop) return false;
        
        const offerBackdrop = nftData.backdrop.replace(/\d+\.?\d*%/, '').trim().toLowerCase();
        
        return selectedFilters.value.backdrop.some(selectedBackdrop => {
          const cleanSelected = selectedBackdrop.split(' ')[0].toLowerCase().trim();
          const cleanOffer = offerBackdrop.split(' ')[0].toLowerCase().trim();
          return cleanOffer === cleanSelected;
        });
      } catch (error) {
        console.error('❌ Ошибка фильтрации по backdrop:', error);
        return false;
      }
    });
    filterLog.push(`Backdrop: ${before} -> ${filtered.length}`);
  }

  if (filterLog.length > 0) {
    console.log('🔍 Клиентская фильтрация:', filterLog.join(', '));
  }

  return filtered;
};

// Функция для загрузки всех офферов
const loadAllOffers = async () => {
  try {
    offersLoading.value = true;
    
    console.log('📥 Загрузка всех офферов...');
    
    const { data, error } = await supabase
      .from('offers') // Замените на вашу таблицу офферов
      .select('*')
      .order('created_at', { ascending: false });

    if (error) {
      console.error('❌ Ошибка загрузки офферов:', error);
      allOffers.value = [];
      return;
    }

    allOffers.value = data || [];
    console.log(`✅ Загружено ${allOffers.value.length} офферов`);
    
    // Применяем фильтрацию ко всем офферам
    applyFilters();
    
  } catch (error) {
    console.error('❌ Общая ошибка загрузки офферов:', error);
    allOffers.value = [];
  } finally {
    offersLoading.value = false;
  }
};

// Функция применения фильтров ко всем офферам
// Функция применения фильтров ко всем офферам
const applyFilters = () => {
  console.group('🔍 ПРИМЕНЕНИЕ ФИЛЬТРОВ КО ВСЕМ ОФФЕРАМ');
  console.log('📦 Всего офферов до фильтрации:', allOffers.value.length);
  console.log('🎯 Выбранные фильтры:', selectedFilters.value);
  console.log('📊 Тип оффера:', selectedOfferType.value);
  console.log('👤 My Offers:', showOnlyMyActivity.value);

  if (!allOffers.value || allOffers.value.length === 0) {
    filteredOffers.value = [];
    resetDisplayedOffers();
    console.groupEnd();
    return;
  }

  let filtered = [...allOffers.value];
  let filterLog = [];

  // ФИЛЬТРАЦИЯ ПО MY OFFERS
  const beforeMyOffers = filtered.length;
  
  if (showOnlyMyActivity.value) {
    // Когда ползунок ВКЛЮЧЕН - показываем полученные офферы
    filtered = filtered.filter(offer => {
      const isReceived = offer.seller_name === currentAccountName.value && 
                        offer.buyer_name !== currentAccountName.value;
      return isReceived;
    });
    filterLog.push(`Received Offers: ${beforeMyOffers} -> ${filtered.length}`);
  } else {
    // Когда ползунок ВЫКЛЮЧЕН - показываем отправленные офферы  
    filtered = filtered.filter(offer => {
      const isSent = offer.seller_name !== currentAccountName.value && 
                    offer.buyer_name === currentAccountName.value;
      return isSent;
    });
    filterLog.push(`Sent Offers: ${beforeMyOffers} -> ${filtered.length}`);
  }

  // Фильтрация по типу оффера
  if (selectedOfferType.value && selectedOfferType.value !== 'all') {
    const before = filtered.length;
    filtered = filtered.filter(offer => offer.status === selectedOfferType.value);
    filterLog.push(`Тип: ${before} -> ${filtered.length}`);
  }

  // ФИЛЬТРАЦИЯ ПО NFT (используем nft_data)
  if (selectedFilters.value.nft && selectedFilters.value.nft.length > 0) {
    const before = filtered.length;
    filtered = filtered.filter(offer => {
      try {
        // Используем nft_data из структуры оффера
        const nftData = offer.nft_data || offer.nft_object;
        if (!nftData || !nftData.name) {
          console.log('❌ Оффер без nft_data.name:', offer.id);
          return false;
        }
        
        const offerNftName = nftData.name;
        const normalizedOfferNft = normalizeNftName(offerNftName);
        
        const matches = selectedFilters.value.nft.some(selectedNft => {
          const normalizedSelected = normalizeNftName(selectedNft);
          const result = normalizedOfferNft.includes(normalizedSelected);
          console.log(`   🔍 NFT Сравнение: "${normalizedOfferNft}" включает "${normalizedSelected}" = ${result}`);
          return result;
        });
        
        return matches;
      } catch (error) {
        console.error('❌ Ошибка фильтрации по NFT:', error, offer);
        return false;
      }
    });
    filterLog.push(`NFT: ${before} -> ${filtered.length}`);
  }

  // ФИЛЬТРАЦИЯ ПО МОДЕЛИ (используем nft_data)
  if (selectedFilters.value.model && selectedFilters.value.model.length > 0) {
    const before = filtered.length;
    filtered = filtered.filter(offer => {
      try {
        const nftData = offer.nft_data || offer.nft_object;
        if (!nftData || !nftData.model) {
          console.log('❌ Оффер без nft_data.model:', offer.id);
          return false;
        }
        
        const offerModel = nftData.model.replace(/\d+\.?\d*%/, '').trim().toLowerCase();
        
        const matches = selectedFilters.value.model.some(selectedModel => {
          const normalizedSelected = selectedModel.toLowerCase().trim();
          const result = offerModel.includes(normalizedSelected);
          console.log(`   🔍 Модель: "${offerModel}" включает "${normalizedSelected}" = ${result}`);
          return result;
        });
        
        return matches;
      } catch (error) {
        console.error('❌ Ошибка фильтрации по модели:', error, offer);
        return false;
      }
    });
    filterLog.push(`Модель: ${before} -> ${filtered.length}`);
  }

  // ФИЛЬТРАЦИЯ ПО СИМВОЛУ (используем nft_data)
  if (selectedFilters.value.symbol && selectedFilters.value.symbol.length > 0) {
    const before = filtered.length;
    filtered = filtered.filter(offer => {
      try {
        const nftData = offer.nft_data || offer.nft_object;
        if (!nftData || !nftData.symbol) {
          console.log('❌ Оффер без nft_data.symbol:', offer.id);
          return false;
        }
        
        const offerSymbol = nftData.symbol.replace(/\d+\.?\d*%/, '').trim().toLowerCase();
        
        const matches = selectedFilters.value.symbol.some(selectedSymbol => {
          const normalizedSelected = normalizeSymbolName(selectedSymbol);
          const result = offerSymbol === normalizedSelected;
          console.log(`   🔍 Символ: "${offerSymbol}" === "${normalizedSelected}" = ${result}`);
          return result;
        });
        
        return matches;
      } catch (error) {
        console.error('❌ Ошибка фильтрации по символу:', error, offer);
        return false;
      }
    });
    filterLog.push(`Символ: ${before} -> ${filtered.length}`);
  }

  // ФИЛЬТРАЦИЯ ПО BACKDROP (используем nft_data)
  if (selectedFilters.value.backdrop && selectedFilters.value.backdrop.length > 0) {
    const before = filtered.length;
    filtered = filtered.filter(offer => {
      try {
        const nftData = offer.nft_data || offer.nft_object;
        if (!nftData || !nftData.backdrop) {
          console.log('❌ Оффер без nft_data.backdrop:', offer.id);
          return false;
        }
        
        const offerBackdrop = nftData.backdrop.replace(/\d+\.?\d*%/, '').trim().toLowerCase();
        
        const matches = selectedFilters.value.backdrop.some(selectedBackdrop => {
          const cleanSelected = selectedBackdrop.split(' ')[0].toLowerCase().trim();
          const cleanOffer = offerBackdrop.split(' ')[0].toLowerCase().trim();
          const result = cleanOffer === cleanSelected;
          console.log(`   🔍 Backdrop: "${cleanOffer}" === "${cleanSelected}" = ${result}`);
          return result;
        });
        
        return matches;
      } catch (error) {
        console.error('❌ Ошибка фильтрации по backdrop:', error, offer);
        return false;
      }
    });
    filterLog.push(`Backdrop: ${before} -> ${filtered.length}`);
  }

  // ФИЛЬТРАЦИЯ ПО ID (используем nft_data)
  if (selectedIdFilter.value !== null) {
    const before = filtered.length;
    filtered = filtered.filter(offer => {
      try {
        const nftData = offer.nft_data || offer.nft_object;
        if (!nftData || !nftData.url) {
          console.log('❌ Оффер без nft_data.url:', offer.id);
          return false;
        }
        
        const nftId = extractNftIdFromUrl(nftData.url);
        const result = nftId === selectedIdFilter.value.toString();
        console.log(`   🔍 ID: "${nftId}" === "${selectedIdFilter.value}" = ${result}`);
        return result;
      } catch (error) {
        console.error('❌ Ошибка фильтрации по ID:', error, offer);
        return false;
      }
    });
    filterLog.push(`ID: ${before} -> ${filtered.length}`);
  }

  filteredOffers.value = filtered;
  
  console.log(`✅ Результат фильтрации: ${filteredOffers.value.length} офферов`);
  console.log('📋 Лог фильтрации:', filterLog.join(', '));
  
  // Дополнительная отладочная информация
  console.log('🔍 Детали офферов после фильтрации:');
  filteredOffers.value.forEach(offer => {
    console.log(`   - ID: ${offer.id}, Seller: ${offer.seller_name}, Buyer: ${offer.buyer_name}, Status: ${offer.status}`);
  });
  
  console.groupEnd();

  // Сбрасываем пагинацию после фильтрации
  resetDisplayedOffers();
};
// Добавьте computed свойство
const isCurrentItemOnMarket = computed(() => {
  if (!htmlModal.value.item || !htmlModal.value.item.item_id) return false;
  
  const found = marketItems.value.some(marketItem => 
    marketItem.item_id === htmlModal.value.item.item_id
  );
  
  console.log('🔄 Computed проверка isOnMarket:', found);
  return found;
});

// Функция сброса отображаемых офферов
const resetDisplayedOffers = () => {
  offersPage.value = 1;
  const endIndex = Math.min(initialLoadCount, filteredOffers.value.length);
  displayedOffers.value = filteredOffers.value.slice(0, endIndex);
  hasMoreOffers.value = filteredOffers.value.length > initialLoadCount;
  
  console.log(`🔄 Сброс отображения: показано ${displayedOffers.value.length} из ${filteredOffers.value.length}`);
};

// Функция загрузки дополнительных офферов
const loadMoreOffers = () => {
  if (offersLoading.value || !hasMoreOffers.value) return;
  
  const startIndex = displayedOffers.value.length;
  const endIndex = startIndex + loadMoreCount;
  
  if (startIndex >= filteredOffers.value.length) {
    hasMoreOffers.value = false;
    return;
  }
  
  const newOffers = filteredOffers.value.slice(startIndex, endIndex);
  displayedOffers.value = [...displayedOffers.value, ...newOffers];
  
  hasMoreOffers.value = endIndex < filteredOffers.value.length;
  
  console.log(`📥 Загружено еще ${newOffers.length} офферов. Всего: ${displayedOffers.value.length} из ${filteredOffers.value.length}`);
};
// Вспомогательная функция для получения nft_data
const getNftDataFromOffer = (offer) => {
  try {
    if (!offer.nft_data) {
      console.log('❌ Оффер без nft_data:', offer.id);
      return null;
    }
    
    if (typeof offer.nft_data === 'string') {
      return JSON.parse(offer.nft_data);
    }
    
    return offer.nft_data;
  } catch (error) {
    console.error('❌ Ошибка парсинга nft_data:', error, offer.nft_data);
    return null;
  }
};

// Функция нормализации имени NFT
const normalizeNftName = (name) => {
  if (!name) return '';
  let cleanName = name.toLowerCase().replace(/[^a-z0-9]/g, '');
  
  // Убираем префиксы
  if (cleanName.startsWith('htmlnft')) {
    cleanName = cleanName.replace('htmlnft', '');
  }
  if (cleanName.startsWith('html_nft_')) {
    cleanName = cleanName.replace('html_nft_', '');
  }
  
  return cleanName;
};

// Функция нормализации имени символа
const normalizeSymbolName = (symbolName) => {
  if (!symbolName) return '';
  return symbolName.toLowerCase().replace(/[^a-z0-9]/g, '');
};

// Функция извлечения ID из URL
const extractNftIdFromUrl = (url) => {
  try {
    const match = url.match(/-(\d+)(?:\?|$)/);
    return match ? match[1] : null;
  } catch (error) {
    console.error('Error extracting NFT ID from URL:', error);
    return null;
  }
};
// 1. Создаем реактивный массив для хранения опций
const nftOptions = ref([]);

// 2. Функция для загрузки опций
const loadNftOptions = async () => {
  try {
    const allOptions = await getFilteredNftOptions();
    
    if (!Array.isArray(allOptions)) {
      console.warn('❌ allOptions не является массивом:', allOptions);
      nftOptions.value = [];
      return;
    }
    
    console.log('🔍 Все опции NFT перед сортировкой:', allOptions.length);
    
    const selectedOptions = allOptions.filter(option => 
      isOptionSelected('nft', option.originalType)
    );
    const unselectedOptions = allOptions.filter(option => 
      !isOptionSelected('nft', option.originalType)
    );
    
    console.log('✅ Выбранные:', selectedOptions.length);
    console.log('❌ Невыбранные:', unselectedOptions.length);
    
    nftOptions.value = [...selectedOptions, ...unselectedOptions];
    console.log('📋 Итоговый список:', nftOptions.value.length);
    
  } catch (error) {
    console.error('❌ Ошибка загрузки NFT опций:', error);
    nftOptions.value = [];
  }
};

// 3. Функции для получения опций (синхронные, работают с реактивным массивом)
const getSelectedNftOptions = () => {
  return nftOptions.value.filter(option => 
    isOptionSelected('nft', option.originalType)
  );
};

const getUnselectedNftOptions = () => {
  return nftOptions.value.filter(option => 
    !isOptionSelected('nft', option.originalType)
  );
};

// 4. Загружаем опции при открытии категории NFT
watch(() => activeFilterCategory.value, async (newCategory) => {
  if (newCategory === 'nft') {
    console.log('🔍 Категория NFT активирована, загружаем опции...');
    await loadNftOptions();
  }
});

// Watch для обновления моделей при выходе из фильтр категории
watch(() => activeFilterCategory.value, (newCategory, oldCategory) => {
  // Если выходим из категории NFT
  if (oldCategory === 'nft' && newCategory !== 'nft') {
    console.log('🚪 Выходим из категории NFT, очищаем опции...');
    nftOptions.value = [];
  }
  
  // Если выходим из категории Model
  if (oldCategory === 'model' && newCategory !== 'model') {
    console.log('🚪 Выходим из категории Model, очищаем кэш моделей...');
    // Очищаем кэш моделей если нужно
    nftModelsCache.value = {};
    expandedNftGroups.value = {};
  }
  
  // Если выходим из категории Symbol
  if (oldCategory === 'symbol' && newCategory !== 'symbol') {
    console.log('🚪 Выходим из категории Symbol, очищаем кэш...');
    // Очищаем кэш символов если нужно
    symbolImagesCache.value = {};
  }
  
  // Если выходим из категории Backdrop
  if (oldCategory === 'backdrop' && newCategory !== 'backdrop') {
    console.log('🚪 Выходим из категории Backdrop...');
    // Дополнительная очистка если нужна
  }
  
  // Если выходим из категории Price/ID
  if (oldCategory === 'price' && newCategory !== 'price') {
    console.log('🚪 Выходим из категории Price...');
    // Можно сбросить поисковый запрос если нужно
    // searchQuery.value = '';
  }
});
// В секции setup() добавьте:
const marketSubscription = ref(null);
const userSubscription = ref(null);

onMounted(async () => {
  // ... существующий код ...
  
  // Создаем подписки только если они еще не созданы
  if (!marketSubscription.value) {
    marketSubscription.value = supabase
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
  }

  if (!userSubscription.value) {
    userSubscription.value = supabase
      .channel('user_cart_changes')
      .on(
        'postgres_changes',
        {
          event: 'UPDATE',
          schema: 'public',
          table: 'users',
          filter: `name=eq.${currentAccountName.value}`
        },
        (payload) => {
          if (payload.new.bucket && Array.isArray(payload.new.bucket)) {
            const newCartIds = payload.new.bucket;
            const currentCartIds = cartItems.value.map(item => item.id);
            
            if (JSON.stringify(newCartIds.sort()) !== JSON.stringify(currentCartIds.sort())) {
              loadCartFromDatabase();
            }
          }
        }
      )
      .subscribe();
  }
});

// ДОБАВЬТЕ ЭТОТ КОД для очистки подписок
onUnmounted(() => {
  console.log('🧹 Очистка подписок Supabase...');
  
  if (marketSubscription.value) {
    supabase.removeChannel(marketSubscription.value);
    marketSubscription.value = null;
  }
  
  if (userSubscription.value) {
    supabase.removeChannel(userSubscription.value);
    userSubscription.value = null;
  }
});

// Также добавьте для деактивации компонента
onDeactivated(() => {
  console.log('🔌 Деактивация подписок Supabase...');
  
  if (marketSubscription.value) {
    supabase.removeChannel(marketSubscription.value);
    marketSubscription.value = null;
  }
  
  if (userSubscription.value) {
    supabase.removeChannel(userSubscription.value);
    userSubscription.value = null;
  }
});
// Загружаем офферы при монтировании
onMounted(async () => {
  await loadOffers();
});
    watch(() => selectedFilters.value.nft, async (newVal) => {
  if (activeFilterCategory.value === 'model' && newVal.length > 0) {
    await loadNftModels(newVal[0]);
  }
}, { deep: true });
// Добавьте watch для отслеживания изменений
watch(selectedFilters, (newFilters) => {
  console.log('🔄 Фильтры изменены:', newFilters);
}, { deep: true });

watch(selectedIdFilter, (newIdFilter) => {
  console.log('🔄 ID фильтр изменен:', newIdFilter);
});

watch(selectedOfferType, (newType) => {
  console.log('🔄 Тип оффера изменен:', newType);
});
    // Инициализация при монтировании
    onMounted(async () => {
      await loadOffersHistory()
      
      // Подписка на изменения offers
      if (currentAccountName.value) {
        offersSubscription.value = supabase
          .channel('offers_changes')
          .on(
            'postgres_changes',
            {
              event: '*',
              schema: 'public',
              table: 'offers',
              filter: `buyer_name=eq.${currentAccountName.value}`
            },
            () => {
              loadOffersHistory()
            }
          )
          .subscribe()
      }
    })

    // Очистка подписки при размонтировании
    onUnmounted(() => {
      if (offersSubscription.value) {
        supabase.removeChannel(offersSubscription.value)
      }
    })


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

watch(() => operationSuccess.value.show, (newVal) => {
  if (newVal) {
    playLottieAnimation();
  } else {
    if (lottieAnimation) {
      lottieAnimation.destroy();
      lottieAnimation = null;
    }
  }
});
watch([() => activeTab.value, () => myNftsViewMode.value], () => {
  // Сбрасываем фильтры при смене вкладки
  selectedFilters.value = {
    nft: [],
    model: [],
    symbol: [],
    backdrop: [],
    price: [],
    rarity: []
  };
  selectedIdFilter.value = null;
  searchQuery.value = '';
  modelSearchQuery.value = '';
  backdropSearchQuery.value = '';
  
  console.log('🔄 Фильтры сброшены при смене вкладки/режима');
}, { immediate: true });



    // Добавьте этот watch для отслеживания floorPrices
watch(floorPrices, (newVal) => {
  console.log('🔄 floorPrices обновились:');
  console.log('   Модели:', Object.keys(newVal.model));
  console.log('   Фоны:', Object.keys(newVal.backdrop));
}, { deep: true });
    onMounted(() => {
      const container = document.querySelector('.filter-categories-container');
      if (container) {
        let isDown = false;
        let startX;
        let scrollLeft;

        container.addEventListener('mousedown', (e) => {
          isDown = true;
          startX = e.pageX - container.offsetLeft;
          scrollLeft = container.scrollLeft;
        });

        container.addEventListener('mouseleave', () => {
          isDown = false;
        });

        container.addEventListener('mouseup', () => {
          isDown = false;
        });

        container.addEventListener('mousemove', (e) => {
          if (!isDown) return;
          e.preventDefault();
          const x = e.pageX - container.offsetLeft;
          const walk = (x - startX) * 2;
          container.scrollLeft = scrollLeft - walk;
        });
      }
    });

const dataLoaded = ref(false);


watch(() => selectedFilters.value.nft, async (newNftFilters, oldNftFilters) => {
  if (newNftFilters.length > 0 && activeFilterCategory.value === 'model') {
    console.log('Загружаем модели для выбранных NFT:', newNftFilters);
    
    modelsLoading.value = true;
    
    try {
      // Загружаем модели для каждого нового выбранного NFT
      const loadPromises = newNftFilters.map(async (nftType) => {
        if (!nftModelsCache.value[nftType]) {
          console.log(`Загружаем модели для ${nftType}`);
          return await loadNftModels(nftType);
        }
        return Promise.resolve();
      });
      
      // Ждем завершения загрузки всех моделей
      await Promise.all(loadPromises);
      
      console.log('Все модели загружены, обновляем отображение');
    } catch (error) {
      console.error('Ошибка загрузки моделей:', error);
    } finally {
      modelsLoading.value = false;
    }
    
    // Форсируем обновление отображения
    nextTick();
  }
}, { immediate: true, deep: true });
watch(() => activeTab.value, (newTab) => {
  if (newTab === 'activity') {
    loadActivityHistory();
  }
});
watch(() => activeFilterCategory.value, async (newCategory) => {
  
    if (newCategory === 'symbol' && symbolOptions.value.length === 0) {
    await loadSymbolOptions();
  }
  if (newCategory === 'model' && selectedFilters.value.nft.length > 0) {
    console.log('Активирована категория Model, загружаем модели...');
    
    modelsLoading.value = true;
    
    try {
      const loadPromises = selectedFilters.value.nft.map(async (nftType) => {
        if (!nftModelsCache.value[nftType]) {
          console.log(`Загружаем модели для ${nftType}`);
          return await loadNftModels(nftType);
        }
        return Promise.resolve();
      });
      
      await Promise.all(loadPromises);
      
      // Автоматически раскрываем первую группу после загрузки
      if (selectedFilters.value.nft.length > 0) {
        const firstNftType = selectedFilters.value.nft[0];
        expandedNftGroups.value[firstNftType] = true;
      }
      
      console.log('Все модели загружены для категории Model');
    } catch (error) {
      console.error('Ошибка загрузки моделей:', error);
    } finally {
      modelsLoading.value = false;
    }
  }
});

// Фильтрация по выбранным моделям
if (selectedFilters.value.model.length > 0) {
  filtered = filtered.filter(item => {
    const itemModel = extractModelFromNft(item);
    
    // Если модель не найдена, пропускаем фильтрацию для этого элемента
    if (!itemModel) return true;
    
    // Проверяем, совпадает ли модель с выбранными фильтрами
    return selectedFilters.value.model.some(selectedModel => 
      itemModel.toLowerCase().includes(selectedModel.toLowerCase()) ||
      selectedModel.toLowerCase().includes(itemModel.toLowerCase())
    );
  });
}
const filterCategories = ref([
  { id: 'nft', name: 'NFT' },
  { id: 'model', name: 'Model' },
  { id: 'symbol', name: 'Symbol' },
  { id: 'backdrop', name: 'Backdrop' },
  { id: 'price', name: selectedIdFilter.value ? `ID: ${selectedIdFilter.value}` : 'ID' }
]);

watch(selectedIdFilter, (newVal) => {
  const idCategory = filterCategories.value.find(cat => cat.id === 'price');
  if (idCategory) {
    idCategory.name = newVal ? `ID: ${newVal}` : 'ID';
  }
});

// Watcher для обновления фильтров при изменении вкладки или режима просмотра
watch([() => activeTab.value, () => myNftsViewMode.value], () => {
  // Сбрасываем фильтры NFT при переключении вкладок
  if (selectedFilters.value.nft.length > 0) {
    selectedFilters.value.nft = [];
  }
  
  // Принудительно обновляем отображение фильтров
  nextTick(() => {
    // Триггерим обновление, если фильтр NFT активен
    if (activeFilterCategory.value === 'nft') {
      activeFilterCategory.value = null;
      nextTick(() => {
        activeFilterCategory.value = 'nft';
      });
    }
  });
});
const route = useRoute();

// Создайте ref для отслеживания itemId
const currentItemId = ref(route.params.itemId);
// Отслеживаем изменения маршрута
watch(
  () => route.params.itemId, 
  async (newItemId, oldItemId) => {
    console.log('🔄 Watcher сработал:', { newItemId, oldItemId });
    
    if (!newItemId && oldItemId && htmlModal.value.show) {
      console.log('❌ Закрываем модалку - itemId удален из URL');
      closeHtmlModal();
      return;
    }
    
    if (newItemId) {
      console.log('🎯 Обрабатываем новый itemId:', newItemId);
      
      // Проверяем, не открыт ли уже этот item
      if (htmlModal.value.show && htmlModal.value.item?.item_id === newItemId) {
        console.log('ℹ️ Этот item уже открыт');
        return;
      }
      
      // Закрываем текущую модалку перед открытием новой
      if (htmlModal.value.show) {
        htmlModal.value.show = false;
        await nextTick(); // Ждем закрытия
      }
      
      // Добавляем задержку для гарантии рендера
      setTimeout(async () => {
        await handleRouteItemId(newItemId);
      }, 50);
    }
  }, 
  { immediate: true, flush: 'post' } // Добавляем flush: 'post' для гарантии
);

// Наблюдатель для воспроизведения анимации когда она показывается
watch(() => purchaseSuccess.value.show, (newVal) => {
  if (newVal) {
    playLottieAnimation();
  } else {
    // Очищаем анимацию при скрытии
    if (lottieAnimation) {
      lottieAnimation.destroy();
      lottieAnimation = null;
    }
  }
});
onMounted(async () => {
  const savedAccount = localStorage.getItem('currentAccount');
  if (savedAccount) {
    currentAccountName.value = JSON.parse(savedAccount).name;
  }
  
  if (currentAccountName.value) {
    await loadUserData();
    await loadMarketItems();
    await loadCartFromDatabase();
    
    // Создаем подписки только если они еще не созданы
    if (!marketSubscription.value) {
      marketSubscription.value = supabase
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
    }

    if (!userSubscription.value) {
      userSubscription.value = supabase
        .channel('user_cart_changes')
        .on(
          'postgres_changes',
          {
            event: 'UPDATE',
            schema: 'public',
            table: 'users',
            filter: `name=eq.${currentAccountName.value}`
          },
          (payload) => {
            if (payload.new.bucket && Array.isArray(payload.new.bucket)) {
              const newCartIds = payload.new.bucket;
              const currentCartIds = cartItems.value.map(item => item.id);
              
              if (JSON.stringify(newCartIds.sort()) !== JSON.stringify(currentCartIds.sort())) {
                loadCartFromDatabase();
              }
            }
          }
        )
        .subscribe();
    }
  } else {
    loading.value = false;
  }
  

});

onMounted(async () => {
  const savedAccount = localStorage.getItem('currentAccount');
  if (savedAccount) {
    currentAccountName.value = JSON.parse(savedAccount).name;
  }
  
  // Загружаем первоначальные офферы
  await loadOffers(false);
  
  // Устанавливаем наблюдатель скролла
  nextTick(() => {
    const container = scrollContainer.value;
    if (container) {
      container.addEventListener('scroll', handleScroll);
      console.log('👀 Наблюдатель скролла установлен на:', container);
      console.log('📏 Размеры контейнера:', {
        scrollHeight: container.scrollHeight,
        clientHeight: container.clientHeight,
        hasScroll: container.scrollHeight > container.clientHeight
      });
    } else {
      console.error('❌ Контейнер скролла не найден');
    }
  });
});
onMounted(async () => {
                // В mounted
      subscribeToChannel('market_changes', () => {
        loadMarketItems();
      });

  const savedAccount = localStorage.getItem('currentAccount');
  if (savedAccount) {
    currentAccountName.value = JSON.parse(savedAccount).name;
  }
  
  if (currentAccountName.value) {
    await loadUserData();
    await loadMarketItems();
    await loadCartFromDatabase();
    
    // Настраиваем real-time подписки
    const marketSubscription = setupRealtimeUpdates();
    
    // Создаем подписки только если они еще не созданы
    if (!marketSubscription.value) {
      marketSubscription.value = supabase
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
    }

    if (!userSubscription.value) {
      userSubscription.value = supabase
        .channel('user_cart_changes')
        .on(
          'postgres_changes',
          {
            event: 'UPDATE',
            schema: 'public',
            table: 'users',
            filter: `name=eq.${currentAccountName.value}`
          },
          (payload) => {
            if (payload.new.bucket && Array.isArray(payload.new.bucket)) {
              const newCartIds = payload.new.bucket;
              const currentCartIds = cartItems.value.map(item => item.id);
              
              if (JSON.stringify(newCartIds.sort()) !== JSON.stringify(currentCartIds.sort())) {
                loadCartFromDatabase();
              }
            }
          }
        )
        .subscribe();
    }

    // Убираем подписки при размонтировании
    onUnmounted(() => {
      supabase.removeChannel(marketSubscription);
      supabase.removeChannel(userSubscription);
    });
  } else {
    loading.value = false;
  }

  // Обработка маршрута
  const route = useRoute();
  console.log('Текущий маршрут:', route.path, 'itemId:', route.params.itemId);
  
  if (route.params.itemId) {
    await handleRouteItemId(route.params.itemId);
  }

  // Обработчик сообщений от iframe
  window.addEventListener('message', handleIframeMessage);
  
  // Обработчик кнопки "Назад"
  window.addEventListener('popstate', handlePopState);

  watch(() => props.tonConnectUI?.connected, (connected) => {
    if (connected) {
      fetchTonBalance();
    } else {
      tonBalance.value = '0';
    }
  }, { immediate: true });
});
onUnmounted(() => {
        // В unmounted
      unsubscribeFromChannel('market_changes');
  // Отписываемся от каналов
  if (marketSubscription.value) {
    supabase.removeChannel(marketSubscription.value);
    marketSubscription.value = null;
  }
  
  if (userSubscription.value) {
    supabase.removeChannel(userSubscription.value);
    userSubscription.value = null;
  }
  
  // Убираем обработчики событий
  window.removeEventListener('message', handleIframeMessage);
  window.removeEventListener('popstate', handlePopState);
});
// Watcher для обновления floor prices при изменении фильтров
watch([
  () => selectedFilters.value.nft,
  () => selectedFilters.value.model,
  () => selectedFilters.value.symbol,
  () => selectedFilters.value.backdrop,
  () => selectedIdFilter.value,
  () => activeTab.value,
  () => myNftsViewMode.value
], () => {
  // Очищаем кэш floor prices при изменении фильтров
  updateAllFloorPrices();
}, { deep: true });
// Добавьте в секцию setup()
watch(() => selectedFilters.value, (newFilters, oldFilters) => {
  console.log('🔄 Filters changed, updating floor prices...');
  updateAllFloorPrices();
}, { deep: true });

watch(() => selectedIdFilter.value, () => {
  console.log('🔄 ID filter changed, updating floor prices...');
  updateAllFloorPrices();
});

watch(() => activeTab.value, () => {
  console.log('🔄 Active tab changed, updating floor prices...');
  updateAllFloorPrices();
});

watch(() => myNftsViewMode.value, () => {
  console.log('🔄 My NFTs view mode changed, updating floor prices...');
  updateAllFloorPrices();
});
watch(() => marketItems.value, () => {
  // Можно обновлять кэш при каждом изменении marketItems
  // или использовать дебаунс для оптимизации
  updateAllFloorPrices();
}, { deep: true });
onMounted(async () => {
  // ... существующий код ...

  // Загружаем офферы
  await loadAllOffers();
  
  // Устанавливаем наблюдатель скролла
  setupScrollObserver();

  // ... остальной код ...
});
// При изменении фильтров сбрасываем пагинацию
watch([selectedFilters, selectedOfferType, selectedIdFilter, showOnlyMyActivity], () => {
  console.log('🔄 Фильтры изменены, сбрасываем пагинацию');
  resetDisplayedOffers();
}, { deep: true });

// При изменении исходных офферов также сбрасываем
watch(offers, () => {
  resetDisplayedOffers();
});
onMounted(() => {

  // ... существующий код ...
  
  // Обработчик для анимации неудачи
  watch(() => operationFail.value.show, (show) => {
    if (show && lottieFailContainer.value) {
      const animation = lottie.loadAnimation({
        container: lottieFailContainer.value,
        renderer: 'svg',
        loop: false,
        autoplay: true,
        animationData: FailAnimation
      });
      
      animation.setSpeed(1.5);
      
      // Очистка анимации после завершения
      animation.addEventListener('complete', () => {
        setTimeout(() => {
          animation.destroy();
        }, 1000);
      });
    }
  });
});
onMounted(() => {
  
  // ... существующий код ...
  
  // Watcher для success анимации
  watch(() => operationSuccess.value.show, (show) => {
    if (show) {
      playLottieAnimation();
    }
  });
  
  // Watcher для fail анимации
  watch(() => operationFail.value.show, (show) => {
    if (show) {
      playLottieFailAnimation();
    }
  });
});
// Добавьте watch для отслеживания изменений отфильтрованных items
watch(filteredMarketItems, (newItems) => {
  const currentSymbols = new Set();
  
  newItems.forEach(item => {
    const symbol = extractSymbolFromNft(item);
    if (symbol) {
      currentSymbols.add(symbol);
    }
  });
  
}, { deep: true });
onDeactivated(() => {
  // Временно приостанавливаем подписки при переходе на другую страницу
  if (marketSubscription.value) {
    supabase.removeChannel(marketSubscription.value);
  }
  if (userSubscription.value) {
    supabase.removeChannel(userSubscription.value);
  }
});

// Добавьте watch для отслеживания изменений фильтров
watch(selectedFilters, (newFilters) => {
  console.log('🔄 Фильтры изменены, обновляем офферы:', newFilters);
}, { deep: true });

watch(selectedIdFilter, (newIdFilter) => {
  console.log('🔄 ID фильтр изменен:', newIdFilter);
});

watch(selectedOfferType, (newType) => {
  console.log('🔄 Тип оффера изменен:', newType);
});
watch(() => activeFilterCategory.value, (newVal) => {
  if (newVal) {
    document.body.classList.add('filter-menu-open');
  } else {
    document.body.classList.remove('filter-menu-open');
  }
});
// Сбрасываем кэш при смене категории
watch(activeFilterCategory, () => {
  imageCache.value = {};
});


    // Для моделей предзагружаем изображения
    watch(() => activeFilterCategory.value, async (category) => {
      if (category === 'model') {
        const nftType = selectedFilters.value.nft[0];
        const models = await loadNftModels(nftType);
        
        models.forEach(model => {
          const id = `${nftType}-${model}`;
          if (!modelImageCache.value[id]) {
            modelImageCache.value[id] = generateImageUrl(nftType);
          }
        });
      }
    });

    
        


if (selectedFilters.value.nft.length > 0) {
  filtered = filtered.filter(item => {
    // Получаем красивое имя из nft_object
    const itemName = getNftDisplayName(item.nft_type, item.nft_object);
    
    // Проверяем, совпадает ли имя с выбранными фильтрами
    const isIncluded = selectedFilters.value.nft.some(selectedNft => {
      // Сравниваем нормализованные имена
      const normalizedItemName = itemName.toLowerCase().replace(/[^a-z0-9]/g, '');
      const normalizedSelected = selectedNft.toLowerCase().replace(/[^a-z0-9]/g, '');
      
      return normalizedItemName.includes(normalizedSelected) || 
             normalizedSelected.includes(normalizedItemName);
    });
    
    console.log(`NFT "${itemName}" включен в фильтр:`, isIncluded);
    return isIncluded;
  });
}
// Отслеживаем изменения фильтров и применяем их ко всем офферам
watch([
  () => selectedFilters.value.nft,
  () => selectedFilters.value.model,
  () => selectedFilters.value.symbol,
  () => selectedFilters.value.backdrop,
  () => selectedIdFilter.value,
  () => selectedOfferType.value,
  () => showOnlyMyActivity.value
], () => {
  console.log('🔄 Фильтры изменены, применяем ко всем офферам');
  applyFilters();
}, { deep: true });

// При изменении исходных офферов также применяем фильтры
watch(allOffers, () => {
  applyFilters();
});
onMounted(async () => {
  // ... существующий код ...

  // Загружаем офферы
  await loadAllOffers();
  
  // Устанавливаем наблюдатель скролла
  nextTick(() => {
    const scrollContainer = document.querySelector('.activity-list');
    if (scrollContainer) {
      scrollContainer.addEventListener('scroll', handleScroll);
      console.log('👀 Наблюдатель скролла установлен');
    }
  });

  // ... остальной код ...
});
// Вызывайте эту функцию после получения NFT опций
watch(() => getFilteredNftOptions(), async (options) => {
  if (options.length > 0) {
    await preloadNftImages(options);
  }
}, { immediate: true });

watch(activeFilterCategory, (newCategory, oldCategory) => {
  // Очищаем поисковые запросы при смене категории
  if (newCategory !== oldCategory) {
    searchQuery.value = '';
    modelSearchQuery.value = '';
    backdropSearchQuery.value = '';
  }
  
  if (newCategory === 'symbol' && symbolOptions.value.length === 0) {
    loadSymbolOptions();
  }
  
  if (newCategory === 'model' && selectedFilters.value.nft.length > 0) {
    console.log('Активирована категория Model, загружаем модели...');
    
    modelsLoading.value = true;
    
    try {
      const loadPromises = selectedFilters.value.nft.map(async (nftType) => {
        if (!nftModelsCache.value[nftType]) {
          console.log(`Загружаем модели для ${nftType}`);
          return await loadNftModels(nftType);
        }
        return Promise.resolve();
      });
      
      
      if (selectedFilters.value.nft.length > 0) {
        const firstNftType = selectedFilters.value.nft[0];
        expandedNftGroups.value[firstNftType] = true;
      }
      
      console.log('Все модели загружены для категории Model');
    } catch (error) {
      console.error('Ошибка загрузки моделей:', error);
    } finally {
      modelsLoading.value = false;
    }
  }
});
onUnmounted(() => {
  console.log('🧹 Cleaning up MyOffers subscriptions...');
  
  // Отменяем все подписки Supabase
  if (marketSubscription.value) {
    supabase.removeChannel(marketSubscription.value);
    marketSubscription.value = null;
  }
  
  if (userSubscription.value) {
    supabase.removeChannel(userSubscription.value);
    userSubscription.value = null;
  }
  
  // Удаляем обработчики событий
  window.removeEventListener('message', handleIframeMessage);
  window.removeEventListener('popstate', handlePopState);
  
  // Очищаем интервалы и таймеры
  if (window.resizeInterval) {
    clearInterval(window.resizeInterval);
  }
  
  // Останавливаем Lottie анимации
  if (lottieAnimation) {
    lottieAnimation.destroy();
    lottieAnimation = null;
  }
  
  if (lottieFailAnimation) {
    lottieFailAnimation.destroy();
    lottieFailAnimation = null;
  }
  
  // Сбрасываем все модальные окна
  resetAllModals();
  
  console.log('✅ MyOffers cleanup completed');
});
// В начале setup() добавьте:
const subscriptions = ref([]);



// Функция для создания всех подписок
const setupAllSubscriptions = () => {
  // Очищаем старые подписки
  cleanupSubscriptions();
  
  // 1. Подписка на изменения market
  const marketSub = supabase
    .channel('myoffers_market_changes')
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
  subscriptions.value.push(marketSub);

  // 2. Подписка на корзину пользователя
  const userSub = supabase
    .channel('myoffers_user_cart_changes')
    .on(
      'postgres_changes',
      {
        event: 'UPDATE',
        schema: 'public',
        table: 'users',
        filter: `name=eq.${currentAccountName.value}`
      },
      (payload) => {
        if (payload.new.bucket && Array.isArray(payload.new.bucket)) {
          const newCartIds = payload.new.bucket;
          const currentCartIds = cartItems.value.map(item => item.id);
          
          if (JSON.stringify(newCartIds.sort()) !== JSON.stringify(currentCartIds.sort())) {
            loadCartFromDatabase();
          }
        }
      }
    )
    .subscribe();
  subscriptions.value.push(userSub);

  // 3. Подписка на offers
  const offersSub = supabase
    .channel('myoffers_offers_changes')
    .on(
      'postgres_changes',
      {
        event: '*',
        schema: 'public',
        table: 'offers',
        filter: `buyer_name=eq.${currentAccountName.value}`
      },
      () => {
        loadOffersHistory();
      }
    )
    .subscribe();
  subscriptions.value.push(offersSub);

  console.log(`✅ Created ${subscriptions.value.length} subscriptions for MyOffers`);
};
// Отслеживаем изменения основных фильтров (те, что в applyFiltersToQuery)
watch([
  () => showOnlyMyActivity.value,
  () => selectedOfferType.value
], () => {
  console.log('🔄 Основные фильтры изменены, перезагружаем офферы');
  loadOffers(false); // Полная перезагрузка
});

// Отслеживаем изменения сложных фильтров (применяем на клиенте)
watch([
  () => selectedFilters.value.nft,
  () => selectedFilters.value.model,
  () => selectedFilters.value.symbol,
  () => selectedFilters.value.backdrop,
  () => selectedIdFilter.value
], () => {
  console.log('🔄 Сложные фильтры изменены, применяем клиентскую фильтрацию');
  // Для сложных фильтров применяем клиентскую фильтрацию
  // к уже загруженным данным
  if (displayedOffers.value.length > 0) {
    const filtered = applyClientSideFilters(displayedOffers.value);
    // Здесь можно обновить отображение, если нужно
    console.log(`📊 Клиентская фильтрация: ${displayedOffers.value.length} -> ${filtered.length}`);
  }
}, { deep: true });
onMounted(async () => {
  // ... существующий код ...

  // Загружаем первоначальные офферы
  await loadOffers(false);
  
  // Устанавливаем наблюдатель скролла
  nextTick(() => {
    const scrollContainer = document.querySelector('.activity-list');
    if (scrollContainer) {
      scrollContainer.addEventListener('scroll', handleScroll);
      console.log('👀 Наблюдатель скролла установлен');
    }
  });

  // ... остальной код ...
});
// Computed свойство для отображения информации о загрузке
const offersInfo = computed(() => {
  return {
    displayed: displayedOffers.value.length,
    total: totalOffersCount.value,
    hasMore: hasMoreOffers.value,
    loading: offersLoading.value,
    loadingMore: loadingMore.value
  };
});
// Функция очистки всех подписок
const cleanupSubscriptions = () => {
  if (subscriptions.value.length > 0) {
    console.log(`🧹 Cleaning up ${subscriptions.value.length} subscriptions...`);
    subscriptions.value.forEach(channel => {
      supabase.removeChannel(channel);
    });
    subscriptions.value = [];
  }
};

// Единый onUnmounted хук
onUnmounted(() => {
  console.log('🧹 MyOffers unmounted - cleaning up...');
  
  // Очищаем все подписки
  cleanupSubscriptions();
  
  // Удаляем обработчики событий
  window.removeEventListener('message', handleIframeMessage);
  window.removeEventListener('popstate', handlePopState);
  
  // Очищаем интервалы
  if (window.resizeInterval) {
    clearInterval(window.resizeInterval);
  }
  
  // Останавливаем анимации
  if (lottieAnimation) {
    lottieAnimation.destroy();
    lottieAnimation = null;
  }
  
  if (lottieFailAnimation) {
    lottieFailAnimation.destroy();
    lottieFailAnimation = null;
  }
  
  // Сбрасываем модальные окна
  resetAllModals();
  
  console.log('✅ MyOffers cleanup completed');
});

// onDeactivated для навигации
onDeactivated(() => {
  console.log('⏸️ MyOffers deactivated - pausing subscriptions');
  cleanupSubscriptions();
});
    return {
      
      telegram: telegramIcon,
      tonBalance,
      activeTab,
      nfts,
      loading,
        symbolsLoading,

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
      generateNftHtmlForFullscreenMyGifts,
      sellModal,
      buyModal,
            getAllModelDataSortedByRarity,

      backdropSearchQuery,
      modelSearchQuery,
      searchQuery,
      activeTab,
  nfts,
  loading,
      cancelSaleModal,
      recipientCheck,
      logAllMarketSymbols,
      extractNameFromNftObject,
      modelsLoading,
      toggleCartFromFullscreen,
      applyIdFilter,
      clearIdFilter,
      sendGift,
      openGiftModal,
      giftModal,
      extractIdFromNftObject,
      itemDetailsModal,
      getAllModelDataSortedByRarity,
      showFilterDropdown,
      searchQuery,
      generateNftHtmlForListActivity,
      generateNftHtmlForFullscreenActivity,
      selectedNftTypes,
      filteredEasterEggNfts,
      filteredOffers, 
      extractNftIdFromUrl,
       normalizeSymbolName,
       loadOffers,
       normalizeNftName,
      filteredFeaturedNfts,
      activityItems,
      setActiveTab,
      getFilteredSymbolsFromActivityHistory,
      extractNftDataWithNumber,
      isItemOnMarket,
      openHtmlModalForUnlisted,
      getNftDisplayName,
      getNftImage,
      shareToTelegram,
      checkIfNftAlreadyListed,
      TIME_yellow,
      isTONNFT,
      getNftSellPrice,
      logSymbolsWithPngPreview,
      getTotalSellPrice,
      getCommission,
      getActivityNftHtml,
      offerActionLoading,
      
      getFinalAmount,
      bucket_img,
      cartItems,
      cartMenu,
      toggleCartMenu,
      addToCart,
      removeFromCart,
      withdraw_icon,
      cennik,
      clearCart,
      acceptOffer,
      rejectOffer,
      handleSell,
      calculateCartTotal,
      tonlogoblack,
      buyAllFromCart,
      getSortedNftOptions,
      openOfferModal,
      offerModal,
            handleBack,
      sendOffer,
      validateTransferAmount,
      validateSellAmount,
      checkRecipientExists,
      formatDate,
      
      formatDateTime,
      showNotification,
      loadHistory,
      getActivityTypeLabel,
      
      
      getTotalNFTsInCart,
      getOfferNftName,
      extractOfferNftId,
      getNftAttributes,
      getOfferNftHtml,
      getNftImage,
      loadOffersHistory,
      initiateCancelSale,
      executeCancelSale,
      initiateTransfer,
      handleBackButton,
      formatPrice,
      showConfirmation,
      getOptionImageUrl,
  getModelImageUrl,
  getNftImage,
  generateCorrectImageUrl,
      
            tonBalance,
      fetchUserBalance,
      debugFloorPrices,
      executeTransfer,
      clearFilterCategory,
      initiateSell,
      showSellConfirmation,
      executeSell,
      initiateBuy,
      executeBuy,
       generateSymbolHtml,
  getFilteredSymbolOptions,
  onSymbolIframeLoad,
  onSymbolIframeError,
      KPECTUK_red,
      galochka_green,
      checkIfNftInUnlisted,
      goBack,
      onSymbolIframeLoad,
      
      startDrag,
      stopDrag,
        extractNftId,
      bucket_icon,
      myNftsViewMode,
      myUnlistedNfts,
      extractNftNameFromUrl,
      listIcon,
      openOfferBotLink,
      goToMarketItem,
      editIcon,
      purschaseIcon,
      generateNftHtmlForList,
      initiateSellFromUnlisted,
      syncNftState,
      addNftToUnlistedForBuyer,
      executePriceEdit,
      openEditPriceModal,
      editPriceModal,
      rubish_bucket_icon,
      isInCart,
        extractNftIdFromUnlisted,
        operationSuccess,
        
      modelSearchQuery,
      generateBackdropSVG,
      nftOptions,
  getSelectedNftOptions, 
  getUnselectedNftOptions,
      getSelectedNftOptions,
      galochka,
      KPECTUK,
      getUnselectedNftOptions,
      handleModelSearch,
      getTotalModelsCount,
      handleModalClose,
      FailAnimation,
      handleDrag,
      getFilteredBackdrops,
      getFilteredModels,
      share,
      giftbox,
      scrollContainer,
      telega,
      purchaseSuccess,
      bucket_white_img,
      rubish_bucket,
      checkForDuplicateListing,
      
      areItemsDuplicates,
      removeNftFromUnlisted,
      openOfferFullscreen,  
      addNftToUnlistedForBuyer,
      getFilteredNftOptions,
      getSelectedSymbolOptions,
      getUnselectedSymbolOptions,
      getSelectedBackdropOptions,
      getUnselectedBackdropOptions,
      getFilteredSymbols,
      isCurrentItemOnMarket,
      htmlNftModal,
      htmlModal,
      BANK,
      Giveaway,
      handleWithdraw,
      handleTransfer,
      toggleMyNftsViewMode,
      getModelsForNftSortedByRarity,
      openHtmlModal,
      handleAddNft,
      extractSymbolsFromActivityHistoryPaginated,
      startHtmlModalDrag,
      handleHtmlModalDrag,
      stopHtmlModalDrag,
      handleBuyClick,
      extractUrlFromHtml,
      replayHtmlAnimation,
      htmlIframe,
      handleHtmlModalClose,
      htmlNfts,
      extractSymbolFromNftAdvanced,
      loadSymbolOptionsAlternative,
      getAllModelData,
      getAllModelNames,
      openTelegramLink,
      addSquareStyles,
      extractNftName,
      openFullscreenView,
      forceSquareStyles,
      extractMetadataFromUnlistedNft,
      closeHtmlModal,
      getSelectedModelOptions,
      getUnselectedModelOptions,
      
      filterCategories,
      activeFilterCategory,
          showOnlyMyActivity,
    displayedOffers,
    offersLoading,
    loadingMore,
    hasMoreOffers,
    totalOffersCount,
    selectedOfferType,
    selectedFilters,
    selectedIdFilter,
    currentAccountName,
    
    // Функции
    toggleMyActivity,
    setOfferType,
    handleScroll,
    loadOffers,
    
    // Ваши существующие функции и computed свойства
    getOfferNftHtml,
    getOfferNftName,
    extractOfferNftId,
    getOfferStatusLabel,
    formatOfferDate,
    formatPrice,
      activeCategoryWidth,
      toggleFilterCategory,
      getFilterOptions,
      listIcon_blue,
      TIME_active,
      editIcon_blue,
      purschaseIcon_green,
      getAllModelOptions,
      toggleFilterOption,
      tonlogofloor,
      checkPriceChange,
      isOptionSelected,
      // Данные
      loadingOffers,
      offersItems,
      filteredOffers,
      selectedOfferType,
      showOnlyMyOffers,
      currentAccountName,
      
      // Типы
      offerTypes,
      
      // Методы
      setOfferType,
      toggleMyOffers,
      loadOffersHistory,
      formatOfferDate,
      getOfferNftHtml,
      getNftImage,
      extractNftId,
      getOfferStatusLabel,
      formatPrice,
      
      // Существующие функции и данные (если нужны для совместимости)
      activeTab,
      setActiveTab,
      dropdownPosition,
      initiateSellFromUnlisted,
      handleTransfer,
      replayHtmlAnimation,
      filterButtons,
      setActiveFilter,
      categoriesContainer,
      setActiveFilter,
      closeFilterMenu,
      toggleSortMenu,
      generateNftHtmlForList,
      generateNftHtmlForFullscreen,
      tonlogo,
      togglePriceRangeMenu,
      operationFail,
      applySort,
      openHtmlModal,
      applyPriceRange,
      formatActivityDateWithYear,
      resetPriceRange,
      fallbackImageUrl: 'https://gifts.coffin.meme/desk%20calendar/Pepe%20Plans.png',
      imageUrl: 'https://gifts.coffin.meme/desk%20calendar/Pepe%20Plans.png',
      filter_img,
      sell_img,
      TIME,
      sortMenu, 
      getNftDisplayNameForGroup,
      nftImageUrls,
      openCartItemModal,
      expandedNfts,
      expandedModelNfts,
      selectedNftModels,
      priceRangeMenu,
      isPriceChanged,
      expandedModelNfts,
      nftModelsCache,
      
      selectedFilters,
      toggleModelNftExpansion,
      handleOptionClick,
      nftImageCache,
      modelImageCache,
      getModelImageUrl,
      getSelectedModelsInGroup,
      toggleMyActivity,
      getUnselectedModelsInGroup,
      getGroupedModelOptions,
      selectedImageCache,
      getNftOptions,
      getModelOptions,
      displayMode,
      expandedNftGroups,
      
      setDisplayMode,
      toggleNftGroup,
      getModelsForNft,
      setupRealtimeUpdates,
      initiateBuyFromFullscreen,
      loadNftModels,
      getModelsForNft,
      getModelImageUrl,
      handleImageError,
      idFilterValue,
      handleWithdrawFromFullscreen,
      handleTransferFromFullscreen,
      selectedIdFilter,
      availableModelOptions,
      availableNftOptions,
      applyIdFilter,
      clearIdFilter,
      getNftImageSync,
      bucket_icon,
      getNftDisplayNameFromUrl,
      myMarketItems,
      tonlogogray,
      tonlogoyellow,
      formatTonValue,
      selectedActivityType,
  loadingActivity,
  activityTypes,
  filteredActivity,

  // Activity functions
  setActivityType,
  loadActivityHistory,
  addActivityRecord,
  getActivityTypeLabel,
  cleanupDuplicates,
  formatActivityDate,
  recordBuyActivity,
  recordSellActivity,
  recordCancelActivity,
  recordPriceEditActivity,
  recordTransferActivity,
  checkTelegramCapabilities,
      handleImageError
    };
    
  }
  
};
</script>
<style scoped>
.filter-dropdown-menu {
  top: 40vh;
  position: fixed;
  left: 0;
  width: calc(100vw);
  height: 100vh;
  background-color: #1d1d1d;
  z-index: 1000;
  padding: 20px 15px ;
  overflow-y: auto;
  touch-action: pan-y;
  box-shadow: 0 0 20px rgba(255, 187, 0, 0.2);
  margin: 0 0px ;
  border-radius: 50px 50px 0 0 ;
}
.filter-dropdown-menu-indiv {
  top: 25vh;
  position: fixed;
  right: 0;
  width: calc(100vw);
  height: 100vh;
  background-color: #1d1d1d;
  z-index: 1000;
  padding: 20px 15px ;
  overflow-y: auto;
  touch-action: pan-y;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.726);
  margin: 0 0px ;
  border-radius: 50px;
}

.modal-drag-handle {
  width: 50px;
  height: 6px;
  background-color: #666;
  border-radius: 3px;
  margin: 0 auto 20px;
  cursor: grab;
}

.search-box {
  padding: 0 10px 15px;
}

.search-input {
  width: 100%;
  padding: 12px 15px;
  background-color: #3a3a3a;
  border-radius: 10px;
  color: white;
  font-size: 1rem;
}


.filter-option {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  margin-bottom: 8px;
  background-color: #2c2c2c;
  border-radius: 10px;
  font-size: 1rem;
  gap: 12px;
}

.option-image {
  width: 30px;
  height: 30px;
  border-radius: 6px;
  object-fit: cover;
}

.option-text {
  flex-grow: 1;
}
.nft-group-models
.checkmark {
  color: #ffc400;
  font-weight: bold;
  padding: 10px;
}

/* Остальные стили остаются без изменений */
.filter-system {
  position: relative;
  margin-bottom: 15px;
}

.filter-categories-container {
  position: relative;
  width: 100%;
  overflow-x: auto;
  padding-bottom: 10px;
  scrollbar-width: none;
}

.filter-categories-container::-webkit-scrollbar {
  display: none;
}

.filter-categories-scroll {
  display: inline-flex;
  gap: 10px;
  padding: 0 ;
}

.filter-option {
  padding: 15px;
  margin-bottom: 10px;
  background-color: #2c2c2c;
  border-radius: 10px;
  font-size: 1rem;
  display: flex;
  justify-content: space-between;
}

.filter-option.selected {
  background-color: rgba(255, 196, 0, 0.2);
  color: #ffc400;
}

.checkmark {
  color: #ffc400;
  font-weight: bold;
}

.filter-category-btn {
  flex-shrink: 0;
  padding: 8px 20px;
  background-color: #3a3a3a;
  color: #e0e0e0;
  border: none;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight:600 ;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.filter-category-btn:hover {
  background-color: #4a4a4a;
  
}

.filter-category-btn.active {
  background-color: #ffbb00;
  color: #000;
  font-weight: 900;
}

.filter-dropdown-enter-active,
.filter-dropdown-leave-active {
  transition: all 0.3s ease;
}

.filter-dropdown-enter-from,
.filter-dropdown-leave-to {
  opacity: 0;
  transform: translateY(20px);
}
.filter-option {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  margin-bottom: 8px;
  background-color: #2c2c2c;
  border-radius: 10px;
  font-size: 1rem;
  gap: 12px;
}

.option-content {
  flex-grow: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.option-rarity {
  color: #ffc400;
  font-size: 0.9rem;
  margin-left: 10px;
}
/*-----------------------------------------------------------------------------------------------
/* Стили для карточек товаров на рынке */
.market-item {
  display: flex;
  flex-direction: column;
  border-radius: 30px 30px 7px 7px;
  overflow: hidden;
  background: #2b2b2b;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
  width: 100%;
  min-height: 200px; /* Минимальная высота для консистентности */
}


.item-image-container {
  cursor: pointer;
  position: relative;
  width: 100%; /* Занимает всю ширину */
}

.nft-html-wrapper {
  width: 100%;
  height: 0;
  padding-bottom: 100%; /* Квадратное соотношение */
  position: relative;
}

.nft-html-content {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: none;
}


.nft-image {
  width: 100%;
  height: auto;
  max-height: 200px;
  object-fit: contain;
  aspect-ratio: 1/1; /* Сохраняем пропорции */
}

.item-actions {
  padding-top: 10px;
  padding-bottom: 7px;
  padding: 7px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%; /* Занимает всю ширину */
}
.buy-button, .cancel-sale-button {
  width: 100%; /* Занимает всю ширину контейнера */
  padding: 8px 12px;
  border: none;
  border-radius: 20px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.2s;
}

.buy-button {
  background-color: #ffbb00;
  color: rgb(14, 14, 14);
}

.cancel-sale-button {
  background-color: #a02d24;
  color: rgb(170, 170, 170);
  font-weight: bolder;
}

.market-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 2fr));
  gap: 15px;
  width: 100%;
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
  background-color: #ffbb00; /* Голубой цвет */
  color: rgb(0, 0, 0);
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
  background-color: #ffbb00; /* Жёлтый цвет */
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
  left:0;
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
  background-color: #19a3ff;
  color: #ffffff;
  font-weight: 600;

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
  display: flex;
  justify-content: center;
  align-items: center;
}

.item-details-modal-content {
  position: relative;
  background-color: #2c2c2c;
  border-radius: 20px;
  padding: 20px;
  max-width: 95%;
  width: 400px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
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


.buy-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
  opacity: 0.7;
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
  font-weight: 600;
  color: #8b8b8b;
  cursor: pointer;
  transition: all 0.3s ease;
}

.nav-button.active {
  background-color: #ffbb00;
  color: #000;
  font-weight: 700;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  box-shadow: 0 0 20px rgba(255, 217, 0, 0.5);
}

.nav-button:hover:not(.active) {
  background-color: #ffbb00;
}

/* Общие элементы */
.back-button {
  position: fixed;
  top: 15px;
  left: 15px;
  padding: 8px 15px;
  background-color: #ffbb00;
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
  background-color: rgb(28, 131, 31);
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
  background-color: #ffbb00;
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
  background-color: rgb(28, 131, 31); /* Зеленый цвет */
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
  color:rgb(28, 131, 31);
  font-weight: bold;
}

.item-total {
  font-weight: bold;
  color: #333;
}



.buy-button {
  padding: 8px 12px;
  background-color: #ffbb00;
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


.item-type.cancel {
  background-color: #ff9800;
}

.hustler{
  padding-left: 2px;
  color: #cacaca;
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
  color: rgb(28, 131, 31);
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
  color: rgb(28, 131, 31);
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
  border-bottom: 1px solid #ebebeb;
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
  border-radius: 20px;
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
  background-color:rgb(28, 131, 31);
  color: white;
  font-weight: bold;
}

.confirm-button:hover:not(:disabled) {
  background-color: rgb(28, 131, 31);
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
  background-color: rgb(28, 131, 31);
  color: rgb(0, 0, 0);
}

.item-type.transfer {
  background-color: rgb(28, 131, 31);
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
  color: rgb(28, 131, 31);
  font-weight: bold;
}

.item-recipient, 
.item-counterparty {
  color: rgb(28, 131, 31);
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
@media (max-width: 500px) {
  .market-grid {
    grid-template-columns: 2fr;
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

.telegram-link {
  color: #0088cc;
  text-decoration: none;
  font-weight: bold;
}

.telegram-link:hover {
  text-decoration: underline;
}
.modal-actions {
  display: flex;
  justify-content: center;
}

.buy-button {
  padding: 12px 24px;
  background-color: #ffc400;
  color: #000;
  border: none;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s;
  width: 100%;
  max-width: 200px;
}

.buy-button:hover:not(:disabled) {
  background-color: #ffd700;
}

.buy-button:disabled {
  background-color: #666;
  color: #999;
  cursor: not-allowed;
}
.html-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  justify-content: center;
  align-items: flex-end; /* Изменено с center на flex-end */
}

.html-modal-content {
  position: relative;
  background-color: #2c2c2c;
  border-radius: 20px 20px 0 0;
  padding: 20px;
  width: 100%;
  max-width: 100%;
  max-height: 100vh;
  box-shadow: 0 -5px 20px rgba(0, 0, 0, 0.3);
  touch-action: none;
}



.html-content-container {
  flex: 1;
  overflow: hidden;
  width: 100%;
  height: 45vh;
  padding-left: 9%;

}

.html-content-iframe {

  border: none;
  align-items: center;

}

.modal-drag-handle {
  width: 50px;
  height: 6px;
  background-color: #666;
  border-radius: 3px;
  margin: 0 auto 15px;
  cursor: grab;
}


/* Убираем лишние отступы и границы */
.modal-item-info {
  padding: 10px;
  border: none;
  margin: 0;
}

/* Адаптация для мобильных устройств */
@media (max-width: 768px) {
  .html-modal-content {
    padding: 10px;
  }
  
  .modal-item-info h3 {
    font-size: 1.2rem;
  }
}

.modal-item-info h3 {
  margin: 0 0 10px 0;
  color: #ffc400;
  text-align: center;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 5px 0;
  color: #ccc;
}
.pizdec{
  display: flex;
  justify-content: space-between;
  color: #5f5f5f;
}
.modal-actions {
  display: flex;
  justify-content: center;
}

.buy-button {
  padding: 12px 24px;
  background-color: #ffc400;
  color: #000;
  border: none;
  border-radius: 20px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s;
}

.buy-button:hover:not(:disabled) {
  background-color: #ffd700;
}

.buy-button:disabled {
  background-color: #666;
  color: #999;
  cursor: not-allowed;
}
.fullscreen-view {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: #1d1d1d;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  overflow-y: auto; /* Добавьте скролл при необходимости */
}
.html-container {
  top:10vh;
  position: relative;
  width: 100%; /* Увеличьте ширину до 95% от экрана */
  max-width: 100%; /* Уберите ограничение по максимальной ширине */
  height: auto;
  margin: 0 auto;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.html-content-iframe {
  width: 100%; /* Занимает всю ширину контейнера */
  height: 60vh; /* Гибкая высота */
  min-height: 300px; /* Минимальная высота */
  max-height: 80vh; /* Максимальная высота */
  border: none;

  margin: 0 auto;
}

.telegram-icon {
  position: absolute;

  width: 50px;
  height: 42px;
  cursor: pointer;
  transition: transform 0.2s;
  filter: drop-shadow(0 0 2px rgba(0, 0, 0, 0.7));
  z-index: 10; /* Убедитесь, что иконка поверх контента */
}

.telegram-icon:hover {
  transform: scale(1.1);
}

.item-info {
  width: 100%; /* Занимает всю доступную ширину */
  max-width: 600px; /* Максимальная ширина (можно регулировать) */
  padding: 0 10px; /* Отступы по бокам */
  border-radius: 20px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  background: #2a2a2a;
  border-radius: 8px;
  padding: 8px 12px;

}
.info-item-name {
  display: flex;
  justify-content: space-between; /* Растягивает элементы по краям */
  align-items: center;
  background: #1d1d1d;
  padding: 8px 12px;
  border-radius: 8px;
  width: 100%; /* Занимает всю доступную ширину */

}
.info-item {
  display: flex;
  justify-content: space-between; /* Растягивает элементы по краям */
  align-items: center;
  background: #2a2a2a;
  padding: 8px 12px;
  border-radius: 8px;
  width: 100%; /* Занимает всю доступную ширину */

}
.info-grid {
  width: 100%; /* Занимает всю ширину родителя */
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); /* Колонки адаптируются */
  gap: 10px; /* Расстояние между элементами */
  margin-top: 1px;
}
.info-label-name {
  color: #ccc;
  font-size: 1.4rem;
  /* text-align: left; - по умолчанию и так слева */
}
.info-label {
  color: #888;
  font-size: 0.8rem;

  /* text-align: left; - по умолчанию и так слева */
}
.info-value-id {
  color: #707070;
  font-size: 1.1rem;
  font-weight: 700;
  text-align: right; /* Выравниваем значение по правому краю */
}
.info-value {
  color: #ccc;
  font-size: 0.9rem;
  font-weight: 500;
  text-align: right; /* Выравниваем значение по правому краю */
}
.info-container{
  background-color:rgb(29, 29, 29);
  box-shadow: 0 0 5px rgba(0, 0, 0, 0.5);

  margin-top: 45px;
  width: 90%; /* Занимает всю доступную ширину */
  max-width: 600px; /* Максимальная ширина (можно регулировать) */
  border-radius: 20px;
}
.action-buttons {
  display: flex;
  gap: 10px;
  width: 100%;
  max-width: 500px;
  margin: 30px 0 0 0;
  padding: 18px;
}

.transfer-button {
  flex: 1;
  padding: 12px;
  background:#ffbb00;
  color: #000;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}

.sell-button {
  flex: 1;
  padding: 12px;
  background:rgb(28, 131, 31);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}

.back-button {
  position: fixed;
  top: 20px;
  left: 20px;
  background: rgba(255, 215, 0, 0.3);
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 215, 0, 0.5);
  z-index: 1001;
  padding: 10px 15px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #ffd700;
}
@media (max-width: 768px) {
  .html-container {
    width: 98%; /* Еще больше на мобильных */
  }

  .html-content-iframe {
    height: 50vh; /* Уменьшите высоту на мобильных */
  }
}

@media (min-width: 1024px) {
  .html-content-iframe {
    height: 70vh; /* Увеличьте высоту на десктопах */
  }
}
.fullscreen-view {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: #1d1d1d;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  overflow-y: auto;
}

.fullscreen-content {
  width: 100%;
  max-width: 800px;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.html-container {
  position: relative;
  width: 85%;
  max-width: 70%;
  height: auto;
  margin: 0 auto;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.html-content-iframe {
  width: 100%;
  min-height: 3vh;
  max-height: 35vh;
  border: none;

  margin: 0 auto;
}

.telegram-icon {
  bottom: 25px;
  right: -1px;
  position: absolute;
  width: 50px;
  height: 42px;
  cursor: pointer;
  transition: transform 0.2s;
  filter: drop-shadow(0 0 2px rgba(0, 0, 0, 0.7));
  z-index: 10;
}

.telegram-icon:hover {
  transform: scale(1.1);
}

.item-info {
  width: 100%;
  max-width: 600px;
  padding: 0 10px;
  border-radius: 20px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  background: #2a2a2a;
  border-radius: 8px;
  padding: 8px 12px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #2a2a2a;
  padding: 8px 12px;
  border-radius: 8px;
  width: 100%;
}

.info-grid {
  width: 100%;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
  margin-top: 1px;
}

.info-label {
  color: #888;
  font-size: 0.8rem;
}

.info-value {
  color: #ccc;
  font-size: 0.9rem;
  font-weight: 500;
  text-align: right;
}

.info-container {
  background-color: rgb(29, 29, 29);
  box-shadow: 0 0 5px rgba(0, 0, 0, 0.5);
  margin-top: 45px;
  width: 100%;
  max-width: 600px;
  border-radius: 20px;
}

.action-buttons {
  display: flex;
  gap: 10px;
  width: 100%;
  max-width: 500px;
  margin: -6px 0 0 0;
  padding: 18px;
}

.transfer-button {
  flex: 1;
  padding: 12px;
  background: #ffbb00;
  color: #000;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}

.sell-button {
  flex: 1;
  padding: 12px;
  background:rgb(28, 131, 31);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}

.back-button {
  position: fixed;
  top: 20px;
  left: 20px;
  background: rgba(255, 215, 0, 0.3);
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 215, 0, 0.5);
  z-index: 1001;
  padding: 10px 15px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #ffd700;
}

@media (max-width: 768px) {
  .html-container {
    width: 98%;
  }

  .html-content-iframe {
    height: 50vh;
  }
}

@media (min-width: 1024px) {
  .html-content-iframe {
    height: 70vh;
  }
}

.modal-actions button {
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s;
  width: 100%;
  max-width: 200px;
}
.buy-button-fullscreen {
  background-color:rgb(28, 131, 31);
  color: white;
}
.cancel-sale-button-fullscreen {
  padding: 12px 24px;
  background-color: #e23b2f7e;
  color: rgb(194, 194, 194);
  border: none;
  border-radius: 20px;
  cursor: pointer;
  width: 100%;
  margin-bottom: 60px;
  font-size: 16px;
  font-weight: 600;
  border: 2px solid #971515;


}
.buy-button-fullscreen {
  padding: 12px 24px;
  background-color: #ffbb00;
  color: #000;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  width: 100%;
  font-size:20px;
  font-weight: 800;
}

.buy-button-fullscreen:hover:not(:disabled) {
  background-color: #ffd700;
}

.buy-button-fullscreen:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
.filter-buttons {
  display: flex;
  gap: 10px;
  margin-left: auto;
}

.filter-button {
  background: #2c2c2c;
  border: none;
  border-radius: 8px;
  padding: 8px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
}

.filter-button:hover {
  background: #3a3a3a;
}

.filter-icon-img {
  width: 24px;
  height: 24px;
  object-fit: contain;
}

/* Анимации */
.slide-fade-enter-active {
  transition: all 0.2s ease-out;
}
.slide-fade-leave-active {
  transition: all 0.15s cubic-bezier(1, 0.5, 0.8, 1);
}
.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}

/* Стили меню */
.sort-menu, .price-range-menu {
  position: absolute;
  width: 50vw;
  max-width: 280px;
  background: #2c2c2c;
  border-radius: 12px;
  padding: 8px 0;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.7);
  z-index: 100;
  border: 1px solid #363636;
}

.sort-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  transition: all 0.2s;
  color: rgb(175, 175, 175);
  font-weight: 700;
}

.sort-option:hover {
  background: rgba(255, 196, 0, 0.1);
}

.sort-option.selected {
  background: rgba(255, 196, 0, 0.2);
  color: #ffc400;
}

.sort-option.selected svg {
  color: #ffc400;
}

/* Стили для меню диапазона цен */
.price-range-header {
  padding: 12px 16px;
  border-bottom: 1px solid #3a3a3a;
}

.price-range-header h4 {
  margin: 0;
  color: #ffc400;
  font-size: 1rem;
}

.price-range-inputs {
  padding: 12px 16px;
  display: flex;
  gap: 12px;
}

.input-group {
  flex: 1;
}

.input-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 0.8rem;
  color: #999;
  font-weight: 750;
}

.input-group input {
  width: 100%;
  padding: 8px 12px;
  background: #3a3a3a;
  border: 1px solid #555;
  border-radius: 6px;
  color: white;
  font-size: 0.9rem;
}

.input-group input:focus {
  outline: none;
  border-color: #ffc400;
}

.price-range-actions {
  display: flex;
  padding: 12px 16px;
  border-top: 1px solid #3a3a3a;
  gap: 8px;
}

.price-range-actions button {
  flex: 1;
  padding: 8px;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 800;
}

.reset-btn {
  background: #3a3a3a;
  color: #ccc;
  border: none;
}

.reset-btn:hover {
  background: #444;
}

.apply-btn {
  background: #ffc400;
  color: #000;
  border: none;
  font-weight: 500;
}

.apply-btn:hover {
  background: #ffd700;
}
.filter-option {
  display: flex;
  align-items: center;
  padding: 12px 15px ;
  margin-bottom: 8px;
  background-color: #2c2c2c;
  border-radius: 10px;
  font-size: 1rem;
  gap: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-option.nft-item {
  background-color: #3a3a3a;
  font-weight: 500;
}

.filter-option.model-item {
  margin-left: 30px;
  background-color: #252525;
}

.filter-option.selected {
  background-color: rgba(255, 196, 0, 0.2);
}

.filter-option:hover {
  background-color: #3a3a3a;
}

.option-image {
  width: 30px;
  height: 30px;
  border-radius: 6px;
  object-fit: cover;
}

.option-content {
  flex-grow: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.option-text {
  flex-grow: 1;
  font-weight: 700;
}

.option-rarity {
  color: #ffc400;
  font-size: 0.9rem;
  margin-left: 10px;
}

.expand-icon {
  font-weight: bold;
  font-size: 1.2rem;
  width: 20px;
  text-align: center;
}

.checkmark {
  color: #ffc400;
  font-weight: bold;
}
.filter-option.nft-item {
  background-color: #3a3a3a;
  font-weight: 500;
  margin-bottom: 5px;
}

.filter-option.nft-item.expanded {
  margin-bottom: 0;
  border-bottom-left-radius: 0;
  border-bottom-right-radius: 0;
}

.filter-option.model-item {
  margin-left: 30px;
  background-color: #252525;
  margin-top: 0;
  border-top-left-radius: 0;
  border-top-right-radius: 0;
}

.filter-option.model-item:last-child {
  margin-bottom: 8px;
}
.filter-option.nft-item {
  position: relative;
}

.filter-option.model-item {
  margin-left: 30px;
  background-color: #252525;
  animation: fadeIn 0.2s ease-out;
}

.expand-icon {
  position: absolute;
  right: 15px;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(255, 196, 0, 0.2);
  border-radius: 4px;
  cursor: pointer;
  user-select: none;
}

.expand-icon:hover {
  background-color: rgba(255, 196, 0, 0.3);
}

.checkmark {
  color: #ffc400;
  font-weight: bold;
  right: 20px;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}
/* Стиль для модели внутри развернутого NFT */
.filter-option.model-item {
  margin-left: 30px;
  background-color: #252525;
  animation: fadeIn 0.2s ease-out;
}

/* Кнопка разворачивания */
.expand-icon {
  position: absolute;
  right: 15px;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(255, 196, 0, 0.2);
  border-radius: 4px;
  cursor: pointer;
  user-select: none;
}

.expand-icon:hover {
  background-color: rgba(255, 196, 0, 0.3);
}

/* Анимация появления моделей */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}
.filter-dropdown-content {
  padding-bottom: 60px; /* Добавляем достаточно места внизу */
}
@media (max-width: 768px) {
  .filter-dropdown-menu {
    padding-bottom: calc(270px + env(safe-area-inset-bottom));

  }
}
.filter-category-btn.active {
  background-color: #ffbb00;
  color: #000;
  font-weight: 500;
  box-shadow: 0 0 10px rgba(255, 196, 0, 0.5);
}

.filter-dropdown-menu {
  /* Добавьте этот стиль, если его нет */
  transition: transform 0.3s ease, opacity 0.3s ease;
}
.filter-dropdown-menu-nft {
  /* Специфичные стили для NFT фильтра */
  background-color: #1d1d1d;
}

.filter-dropdown-menu-model {
  /* Специфичные стили для Model фильтра */
  background-color: #1d1d1d;
}

.no-nft-selected {
  padding: 20px;
  text-align: center;
  color: #888;
  font-size: 0.9rem;
}

/* Общие стили для обоих фильтров */
.filter-dropdown-menu {
  top: 30.6vh;
  position: fixed;
  left: 0;
  width: calc(100vw);
  height: 100vh;
  z-index: 100000;
  padding: 20px 15px;
  overflow-y: auto;
  touch-action: pan-y;
  box-shadow: 0 0 20px rgba(255, 187, 0, 0.2);
  margin: 0 0px;
  border-radius: 50px 50px 0 0;
}
/* Кнопки режимов отображения */
.display-mode-buttons {
  display: flex;
  margin: 10px 0;
  border-bottom: 1px solid #333;
  padding-bottom: 10px;
}

.mode-button {
  flex: 1;
  padding: 8px;
  background: #2c2c2c;
  border: none;
  color: #aaa;
  cursor: pointer;
  transition: all 0.2s;
}

.mode-button.active {
  background: #ffbb00;
  color: #000;
  font-weight:800;
}

.mode-button:first-child {
  border-radius: 5px 0 0 5px;
}

.mode-button:last-child {
  border-radius: 0 5px 5px 0;
}

/* Группы NFT */
.nft-group {
  margin-bottom: 10px;
  background: #2c2c2c;
  border-radius: 8px;
  overflow: hidden;
}

.nft-group-header {
  display: flex;
  align-items: center;
  padding: 10px;
  cursor: pointer;
  transition: background 0.2s;
}

.nft-group-header:hover {
  background: #3a3a3a;
}

.group-nft-image {
  width: 30px;
  height: 30px;
  border-radius: 4px;
  margin-right: 10px;
}

.group-nft-name {
  flex: 1;
  font-weight: 500;
  color: #ccc;
}

.group-toggle-icon {
  width: 20px;
  text-align: center;
  font-weight: bold;
}

.nft-group-models {
  padding: 5px 10px 10px;
  background: #252525;
}

/* Анимация раскрытия */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
  padding: 0;
}

.expand-enter-to,
.expand-leave-from {
  max-height: 500px;
  opacity: 1;
}

.model-option {
  margin-left: 20px;
  background: #333;
}




.option-parent {
  font-size: 0.8rem;
  color: #888;
  margin-left: 5px;
}
.no-models-message {
  padding: 20px;
  text-align: center;
  color: #888;
  font-size: 0.9rem;
}
.option-content {
  flex-grow: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.option-text {
  flex-grow: 1;
  font-weight: 700;
}

.option-rarity {
  color: #ffc400;
  font-size: 0.9rem;
  font-weight: 600;
  min-width: 40px;
  text-align: right;
}
.loading-models {
  text-align: center;
  padding: 20px;
  color: #888;
  font-size: 0.9rem;
}

.nft-group {
  margin-bottom: 10px;
  background: #2c2c2c;
  border-radius: 10px;
  overflow: hidden;
}

.nft-group-header {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  cursor: pointer;
  transition: background 0.2s;
  background: #3a3a3a;
}

.nft-group-header:hover {
  background: #4a4a4a;
}

.group-nft-image {
  width: 30px;
  height: 30px;
  border-radius: 6px;
  margin-right: 12px;
  object-fit: cover;
}

.group-nft-name {
  flex: 1;
  font-weight: 600;
  color: #e0e0e0;
}

.group-toggle-icon {
  width: 20px;
  text-align: center;
  font-weight: bold;
  font-size: 1.2rem;
  color: #ffc400;
}

.nft-group-models {
  padding: 10px;
  background: #252525;

}

.model-option {
  margin-left: 20px;
  background: #333;
}

/* Анимация раскрытия */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
  padding: 0;
}

.expand-enter-to,
.expand-leave-from {
  max-height: 500px;
  opacity: 1;
}
.search-results-info {
  padding: 8px 15px;
  color: #888;
  font-size: 0.9rem;
  border-bottom: 1px solid #3a3a3a;
}
.clear-search-btn {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #888;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 5px;
}

.clear-search-btn:hover {
  color: #ffc400;
}
.backdrop-option {
  display: flex;
  align-items: center;
  gap: 12px;
}

.color-square {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  flex-shrink: 0;
  border: 1px solid #444;
}

/* Градиенты для цветов */
:root {
  --color-Black: linear-gradient(#363738, #0e0f0f);
  --color-Aquamarine: linear-gradient(#60b195, #46abb4);
  --color-AzureBlue: linear-gradient(#5db1cb, #448bab);
  --color-BattleshipGrey: linear-gradient(#8c8c85, #6c6c66);
}


.backdrop-option {
  display: flex;
  align-items: center;
  gap: 12px;
}

.backdrop-icon-container {
  width: 24px;
  height: 24px;
  flex-shrink: 0;
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid #444;
}

.backdrop-svg-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.backdrop-svg-wrapper svg {
  width: 100%;
  height: 100%;
}

.option-content {
  flex-grow: 1;
}

.checkmark {
  color: #ffc400;
  font-weight: bold;
}
.option-text {
  color: #ffffff; /* или другой цвет, не черный */
  word-wrap: break-word;
}
.symbol-options-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 10px;
  padding: 10px;
}

.symbol-option {
  flex-direction: column;
  text-align: center;
  padding: 10px;
}

.symbol-image {
  width: 50px;
  height: 50px;
  object-fit: contain;
  margin-bottom: 8px;
  border-radius: 8px;
}

.loading-symbols {
  text-align: center;
  padding: 30px;
  color: #888;
}

.no-symbols-message {
  text-align: center;
  padding: 20px;
  color: #888;
}
.no-nft-message {
  text-align: center;
  padding: 20px;
  color: #888;
}
/* Стили для опций символов */
.symbol-option {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  margin-bottom: 8px;
  background-color: #2c2c2c;
  border-radius: 10px;
  gap: 12px;
}

.symbol-image {
  width: 30px;
  height: 30px;
  border-radius: 6px;
  object-fit: cover;
  flex-shrink: 0;
}

.option-content {
  flex-grow: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.option-text {
  color: #e0e0e0;
}

.checkmark {
  color: #ffc400;
  font-weight: bold;
  flex-shrink: 0;
}

/* Адаптивность для мобильных */
@media (max-width: 480px) {
  .symbol-option {
    padding: 10px 12px;
    gap: 10px;
  }
  
  .symbol-image {
    width: 25px;
    height: 25px;
  }
}
.filter-dropdown-menu-id {
  top: 23vh;
  position: fixed;
  right: 0;
  width: calc(50vw);
  height: auto;
  max-height: 250px;
  background-color: #1d1d1d;
  z-index: 1000;
  padding: 20px 15px;
  border-radius: 20px;
}

.apply-id-filter-btn,
.clear-id-filter-btn {
  width: 100%;
  padding: 12px;
  margin-top: 10px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  font-size: 0.9rem;
}

.apply-id-filter-btn {
  background-color: #ffbb00;
  color: black;
}

.apply-id-filter-btn:disabled {
  background-color: #666;
  cursor: not-allowed;
}

.clear-id-filter-btn {
  background-color: #666;
  color: white;
}

.id-filter-help {
  margin-top: 15px;
  padding: 10px;
  background-color: #2a2a2a;
  border-radius: 8px;
  font-size: 0.8rem;
  color: #888;
}

.id-filter-help p {
  margin: 5px 0;
}
.id-filter-status {
  padding: 10px;
  background-color: rgba(255, 187, 0, 0.1);
  border: 1px solid #ffbb00;
  border-radius: 8px;
  margin-bottom: 10px;
  text-align: center;
  color: #ffbb00;
  font-size: 0.9rem;
}

.apply-id-filter-btn:disabled {
  background-color: #666;
  color: #999;
  cursor: not-allowed;
}

/* Добавьте стиль для активной кнопки ID */
.filter-category-btn.active[data-v-430fb218] {
  background-color: #ffbb00;
  font-weight: 700;
  color: #000;
}
.symbol{
  padding-bottom: 240px;
}
.models{
  padding-bottom: 240px;
}
.backdrop{
  padding-bottom: 260px;
}
.nft{
  padding-bottom: 240px;
}
.cart-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background-color: #ff4757;
  color: white;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  font-size: 0.7rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cart-menu {
  position: absolute;
  right: 10px;
  top: 50px;
  background-color: #2c2c2c;
  border: 1px solid #444;
  border-radius: 8px;
  padding: 15px;
  z-index: 1000;
  min-width: 300px;
  max-height: 400px;
  overflow-y: auto;
}

.cart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #444;
}

.clear-cart-btn {
  background: rgba(255, 179, 14, 0.15); /* Полупрозрачный красный фон */
  border: none; /* Убираем обводку */
  border-radius: 20px; /* Овальная форма */
  color: #ffbb00;
  cursor: pointer;
  font-size: 0.9rem;
  padding: 8px 16px;
  transition: all 0.2s ease;
  font-weight: 500;
}

.clear-cart-btn:hover {
  background: rgba(255, 179, 14, 0.15); /* Немного темнее при наведении */
}

.clear-cart-btn:active {
  background: rgba(255, 179, 14, 0.15); /* Еще темнее при нажатии */
  transform: scale(0.98); /* Легкое сжатие */
}

.clear-cart-btn:disabled {
  background: rgba(128, 128, 128, 0.1);
  color: #666;
  cursor: not-allowed;
  transform: none;
}

.cart-items {
  margin-bottom: 15px;
}

.cart-item {
  display: flex;
  align-items: center;
  padding: 10px;
  margin-bottom: 8px;
  background-color: #3a3a3a;
  border-radius: 6px;
}

.cart-item-image {
  width: 40px;
  height: 40px;
  border-radius: 4px;
  margin-right: 10px;
  object-fit: cover;
}

.cart-item-info {
  flex-grow: 1;
}

.cart-item-name {
  display: block;
  margin-bottom: 2px;
  font-weight: 600;
  color: #1f1f1f;
}

.cart-item-price {
  font-weight: 600;
  color: #ffbb00;
}

.remove-from-cart-btn {
  background: none;
  border: none;
  color: #ff4757;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0 5px;
}

.cart-total {
  text-align: center;
  font-weight: bold;
  margin: 10px 0;
  padding: 10px;
  background-color: #3a3a3a;
  border-radius: 6px;
  color: #aaaaaa;
}

.buy-all-btn {
  width: 100%;
  padding: 10px;
  background-color: #ffbb00;
  color: black;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
}

.buy-all-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.empty-cart {
  text-align: center;
  padding: 20px;
  color: #888;
}
.nft-html-wrapper {
  position: relative;
  width: 100%;
  height: 0;
  padding-bottom: 100%;
}

.add-to-cart-html-button {
  position: absolute;
  bottom: 15px;
  left: 15px;
  background-color: rgba(255, 187, 0, 0.95);
  border: none;
  border-radius: 50%;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 10;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
  padding: 0;
}

.add-to-cart-html-button:hover:not(:disabled) {
  background-color: #ffbb00;
  transform: scale(1.15);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.5);
}

.add-to-cart-html-button:active:not(:disabled) {
  transform: scale(1.05);
}

.add-to-cart-html-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  background-color: rgba(128, 128, 128, 0.7);
}

.bucket-icon {
  width: 35px;
  height: 35px;
  object-fit: contain;
  display: block;
}

/* Анимация при добавлении в корзину */
@keyframes addToCartAnimation {
  0% { transform: scale(1); }
  50% { transform: scale(1.2); }
  100% { transform: scale(1); }
}

.add-to-cart-html-button.added {
  animation: addToCartAnimation 0.6s ease;
  background-color: #4CAF50;
}

/* Адаптивность для мобильных устройств */
@media (max-width: 768px) {
  .add-to-cart-html-button {
    width: 50px;
    height: 50px;
    bottom: 12px;
    left: 12px;
  }
  
  .bucket-icon {
    width: 28px;
    height: 28px;
  }
}

@media (max-width: 480px) {
  .add-to-cart-html-button {
    width: 30px;
    height: 30px;
    bottom: 10px;
    left: 10px;
  }
  
  .bucket-icon {
    width: 24px;
    height: 24px;
  }
}
.cart-button-wrapper {
  position: relative;
  display: inline-block;
}
.cart-badge {
  position: absolute;
  top: -8px;       /* Располагается над иконкой */
  right: -8px;     /* Справа от иконки */
  background-color: #ff4757; /* Красный цвет */
  color: white;
  border-radius: 50%;
  width: 22px;
  height: 22px;
  font-size: 0.75rem;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #1d1d1d;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  z-index: 2;
}

/* Стили для иконок */
.filter-icon-img {
  width: 20px;
  height: 20px;
  object-fit: contain;
}

/* Адаптивность */
@media (max-width: 768px) {
  .cart-badge {
    width: 20px;
    height: 20px;
    font-size: 0.7rem;
    top: -6px;
    right: -6px;
  }
  
  .filter-icon-img {
    width: 18px;
    height: 18px;
  }
}

@media (max-width: 480px) {
  .cart-badge {
    width: 18px;
    height: 18px;
    font-size: 0.65rem;
    top: -5px;
    right: -5px;
  }
  
  .filter-icon-img {
    width: 16px;
    height: 16px;
  }
}
.nft-html-wrapper {
  position: relative;
  width: 100%;
  height: 0;
  padding-bottom: 100%;
}

.cart-action-button {
  position: absolute;
  bottom: 15px;
  left: 15px;
  background-color: rgba(255, 187, 0, 0.95);
  border: none;
  border-radius: 50%;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 10;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
  padding: 0;
}

.cart-action-button:hover:not(:disabled) {
  transform: scale(1.15);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.5);
}

.cart-action-button:active:not(:disabled) {
  transform: scale(1.05);
}

.cart-action-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  background-color: rgba(128, 128, 128, 0.7);
}

/* Стиль для товара в корзине */
.cart-action-button.in-cart {
  background-color: rgba(255, 71, 87, 0.95); /* Красный цвет для удаления */
}

.cart-action-button.in-cart:hover:not(:disabled) {
  background-color: rgba(255, 71, 87, 1);
}

.cart-action-icon {
  width: 35px;
  height: 35px;
  object-fit: contain;
  display: block;
}

/* Анимации */
@keyframes addToCartAnimation {
  0% { transform: scale(1); }
  50% { transform: scale(1.2); }
  100% { transform: scale(1); }
}

@keyframes removeFromCartAnimation {
  0% { transform: scale(1); }
  50% { transform: scale(0.8); }
  100% { transform: scale(1); }
}

.cart-action-button.added {
  animation: addToCartAnimation 0.6s ease;
}

.cart-action-button.removed {
  animation: removeFromCartAnimation 0.6s ease;
}

/* Адаптивность */
@media (max-width: 768px) {
  .cart-action-button {
    width: 50px;
    height: 50px;
    bottom: 12px;
    left: 12px;
  }
  
  .cart-action-icon {
    width: 28px;
    height: 28px;
  }
}

@media (max-width: 480px) {
  .cart-action-button {
    width: 30px;
    height: 30px;
    bottom: 10px;
    left: 10px;
  }
  
  .cart-action-icon {
    width: 24px;
    height: 24px;
  }
}
.cart-item-html-wrapper {
  width: 60px;
  height: 60px;
  overflow: hidden;
  margin-right: 12px;
}

.cart-item-html-content {
  width: 100%;
  height: 100%;
  border: none;
  background: transparent;
}
.cart-item-html-wrapper {
  width: 60px;
  height: 60px;
  border-radius: 12px; /* Сглаженные углы */
  overflow: hidden;
  margin-right: 12px;
  background: #2a2a2a;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cart-item-html-content {
  width: 100%;
  height: 100%;
  border: none;
  background: transparent;
  border-radius: 12px; /* Сглаженные углы для iframe */
}

.cart-item-image {
  width: 60px;
  height: 60px;
  border-radius: 12px; /* Сделаем также сглаженные углы у обычных изображений */
  object-fit: cover;
  margin-right: 12px;
}
.nft-title {
  font-size: 1.4rem;
  font-weight: 600;
  color: #fff;
}

.nft-id {
  color: #888;
  font-size: 1rem;
  font-weight: 500;
  right:0;
}

.info-grid {
  margin-top: 15px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  padding: 8px 0;
}

.info-label {
  color: #aaa;
  font-weight: 500;
}

.info-value {
  color: #fff;
  font-weight: 400;
}
.nft-header {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #333;
}

.nft-title {
  margin: 0;
  font-size: 1.4rem;
  font-weight: 600;
  color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
}

.nft-id {
  color: #888;
  font-size: 1rem;
  font-weight: 500;
  margin-left: 10px;
}

.info-grid {
  margin-top: 15px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1px;
  padding: 8px 0;
}

.info-label {
  padding-left: 7px;
  color: #aaa;
  font-weight: 700;
  min-width: 80px;
}

.info-value-procent {
  color: #ffbb00;
  font-size: 0.9em;
  font-weight: 500;
  background: rgba(255, 179, 14, 0.15); /* Полупрозрачный красный фон */
  border-radius: 20px; /* Овальная форма */
  padding: 4px 4px 4px 4px;

}



.info-value {
  border: none; /* Убираем обводку */
  border-radius: 20px; /* Овальная форма */
  color: #ffbb00;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s ease;
  font-weight: 600;
}
.nft-header {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #333;
}

.nft-title {
  margin: 0;
  font-size: 1.4rem;
  font-weight: 600;
  color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
}

.nft-id {
  color: #888;
  font-size: 1rem;
  font-weight: 500;
  margin-left: 10px;
}
.nft-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  margin: 0;
  padding: 0;
}

.nft-name {
  font-weight: bold;
  text-align: left;
}

.nft-id {
  color: #666;
  font-size: 0.9em;
  text-align: right;
}
.html-container-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
}

.telegram-icon {
  position: absolute;
  bottom: 10px;
  right: 10px;
  width: 46px;
  height: 39px;
  cursor: pointer;
  z-index: 10;
  border-radius: 50%;
  transition: transform 0.2s;
}

.telegram-icon:hover {
  transform: scale(1.1);
}

.cart-action-button-modal {
  position: absolute;
  bottom: 10px;
  left: 10px;
  border: none;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 10;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  transition: all 0.2s;
}

.cart-action-button-modal:hover {
  background: white;
  transform: scale(1.1);
}

.cart-action-button-modal:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.cart-action-button-modal .cart-action-icon {
  width: 20px;
  height: 20px;
}
.info-item {
  display: flex;
  align-items: center;
}
.info-value-container {
  display: flex;
  align-items: center;
  flex-wrap: nowrap;
  padding-right: 4px;
}



.info-value-procent {
  margin-left: 4px;
  font-size: 0.9em;
  font-weight: 500;
  white-space: nowrap;
}
.currency-icon {
  width: 16px;
  height: 16px;
  vertical-align: middle;
}

.buy-button .currency-icon,
.buy-button-fullscreen .currency-icon {
  width: 14px;
  height: 14px;
}
.currency-icon-black {
  width: 15px;
  height: 15px;
  vertical-align:-2px;
}
.listed-unlisted-toggle {
  display: flex;
  justify-content: center;
  margin: 15px 0;
  gap: 100px;
}

.toggle-button {
  background-color: #ffbb00;
  border: none;
  border-radius: 20px;
  padding: 10px 20px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
}

.toggle-button.active {
  background-color: #e6a500;
  box-shadow: 0 0 10px rgba(255, 187, 0, 0.5);
}

.toggle-button:hover {
  background-color: #e6a500;
  transform: translateY(-2px);
}

/* Стили для кнопки List for sale */
/* Контейнер для всех кнопок */
.action-buttons-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  gap: 2px;
  margin-top: 5px;
}

/* Кнопка Send на всю ширину */
.action-btn-send.full-width.flat-button {
  width: 100%;
  height: 37px;
  background: #ffbb00;
  border: none;
  border-radius: 20px;
  color: #222222;
  font-weight: 800;
  font-size: 14px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.action-btn-send.full-width.flat-button:hover {
  background: #e6a500;
  transform: translateY(-2px);
}

.action-btn-send.full-width.flat-button:active {
  transform: translateY(1px);
}

/* Контейнер для кнопок в ряд */
.row-buttons.with-spacing {
  display: flex;
  width: 100%;
  gap: 1px;
}

/* Общие стили для кнопок Sale и Withdraw */
.action-btn-sale.compact-btn,
.action-btn-withdraw.compact-btn {
  flex: 1;
  height: 60px;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-width: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

/* Специфичные стили для кнопки Sale */
.action-btn-sale.compact-btn {
  background: #1c831f90;
  border: 3px solid #1c831f;
  border-radius: 20px 0px 0px 20px;
}

.action-btn-sale.compact-btn:hover {
  background: #1c831f99;
}

/* Специфичные стили для кнопки Withdraw */
.action-btn-withdraw.compact-btn {
  background: #6300008a;
  border: 3px solid #630000;
  border-radius: 0px 20px 20px 0px;
}

.action-btn-withdraw.compact-btn:hover {
  background: #630000aa;
}

/* Контейнер для содержимого кнопки Sale */
.btn-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

/* Иконки */
.btn-icon-img-large-sell {
  width: 50px;
  height: 50px;
  object-fit: contain;
}

.btn-icon-img-large {
  width: 32px;
  height: 32px;
  object-fit: contain;
}

/* Текст под иконками */
.btn-text-independent {
  display: block;
  font-size: 12px;
  color: #ffffff;
  font-weight: 500;
  text-transform: lowercase;
  text-align: center;
  margin: 0;
  padding: 0;
  line-height: 1;
  background: none;
  border: none;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.btn-text-small {
  display: block;
  font-size: 12px;
  color: #858585;
  font-weight: 500;
  text-transform: lowercase;
  text-align: center;
  margin: 0;
  padding: 0;
  line-height: 1;
  background: none;
  border: none;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

/* Текст кнопки Send */
.btn-text {
  font-size: 14px;
  font-weight: 800;
  color: #222222;
}
/* Анимации при наведении и нажатии */
.action-btn-sale.compact-btn:hover,
.action-btn-withdraw.compact-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.action-btn-sale.compact-btn:active,
.action-btn-withdraw.compact-btn:active {
  transform: translateY(1px);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}
/* Адаптивность для мобильных устройств */
@media (max-width: 768px) {
  .action-buttons-container {
    gap: 4px;
    padding: 0 5px 5px 5px;
  }
  
  .action-btn-send.full-width.flat-button {
    height: 32px;
    font-size: 13px;
    
  }
  
  .action-btn-sale.compact-btn,
  .action-btn-withdraw.compact-btn {
    height: 35px;
  }
  
  .btn-icon-img-large-sell {
    margin-top: 3px;
    width: 60px;
    height: 60px;
    object-fit: contain;

  }
  
  .btn-icon-img-large {
    width: 35px;
    height: 35px;
    margin-right: 7px;
  }
  
  .btn-text-independent,
  .btn-text-small {
    font-size: 11px;
  }
}

/* Анимация при нажатии */
@keyframes buttonPress {
  0% { transform: scale(1); }
  50% { transform: scale(0.95); }
  100% { transform: scale(1); }
}

.action-btn-sale.compact-btn:active,
.action-btn-withdraw.compact-btn:active,
.action-btn-send.full-width.flat-button:active {
  animation: buttonPress 0.2s ease;
}
.nft-info-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 8px 12px;
}

.hustler {
  margin-top: 0;
  font-size: 14px;
  font-weight: 600;
}

.nft-id {
  font-size: 14px;
  color: #888;
  font-weight: 700;
}
/* Стили для модального окна продажи */
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
  border: 5px solid #ffc400;
}

.modal-content h3 {
  margin: 0 0 20px 0;
  color: #ffbb00;
  font-size: 1.3rem;
  text-align: center;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.form-group-input {
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

.input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #313131;
  border-radius: 8px;
  font-size: 1rem;
  transition: border 0.2s;
  background-color: #2c2c2c;
  color: #ffff;
}

.input:focus {
  outline: none;
  border-color: #ffc400;
}

.price-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-size: 0.95rem;
}

.price-row-commission {
  color: rgb(170, 170, 170);
}

.price-value {
  font-weight: bold;
}

.price-value-comm {
  color: rgb(109, 109, 109);
  font-weight: 600;
  font-style: italic;
}

.total {
  font-weight: bold;
  color: rgb(28, 131, 31);
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px dashed #ddd;
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

.detail-row-sale {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #494949;
}

.got-a-drop {
  color: #d4d4d4;
  font-weight: 600;
}

.got-a-drop-comm {
  color: #838383;
  font-weight: 600;
  font-style: italic;
}

.modal-buttons {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  margin-top: 20px;
  
}

.cancel-button, 
.confirm-button {
  margin-bottom: 10px ;
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 20px;
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
  background-color: rgb(28, 131, 31);
  color: white;
  font-weight: bold;
}

.confirm-button:hover:not(:disabled) {
  background-color: rgb(28, 131, 31);
}

.confirm-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  background-color: #a5d6a7;
}

/* Стили для кнопки продажи */
.sell-button {
  padding: 8px 12px;
  background-color: rgb(28, 131, 31);
  color: white;
  border: none;
  border-radius: 5px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
}

.sell-button:hover:not(:disabled) {
  opacity: 0.9;
  transform: translateY(-1px);
}

.sell-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
/* Стили для зеленой кнопки Sell в полноэкранном режиме */
.sell-button-fullscreen {
  background-color: rgb(28, 131, 31);
  color: white;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
  padding: 12px 24px;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  width: 100%;
  margin-bottom: 40px;
  font-size: 16px;
  font-weight: 800;

}

.sell-button-fullscreen:hover {
  background-color: rgb(24, 110, 26);
  transform: translateY(-2px);
}

.sell-button-fullscreen:active {
  transform: translateY(0);
}
.send-button-fullscreen {
  background: #ffbb00;
  color: #222222;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  margin: 5px;
}

.withdraw-button-fullscreen {
  background: #ff000093;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  margin: 5px;
}

.action-buttons {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-top: 20px;
}
.send-button-fullscreen {
  background: #ffbb00;
  color: #222222;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
  padding: 12px 24px;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  width: 100%;
  margin-bottom: 40px;
  font-size: 16px;
  font-weight: 800;
}

.withdraw-button-fullscreen {
  background-color: #a02d24;
  color: rgb(170, 170, 170);
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
  padding: 12px 24px;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  width: 100%;
  margin-bottom: 40px;
  font-size: 16px;
  font-weight: 800;
}


.action-buttons {
  display: flex;
  justify-content: center;
}




.market-item.add-card {
  position: relative;
  min-height: 200px; /* Минимальная высота для карточки */
}

.empty-nft-square {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 120px;
  height: 210px;
  text-align: center;
  border-radius: 20px;
  padding: 15px;
  box-sizing: border-box;
  position: absolute;
  top: 50%; /* Центрирование по вертикали относительно карточки */
  left: 50%; /* Центрирование по горизонтали относительно карточки */
  transform: translate(-50%, -50%); /* Точное центрирование */
}

.add-icon {
  font-size: 6rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
  color: #c2c2c2cc;
}

.add-text {
  font-size: 1.2rem;
  font-weight: 900;
  color: #c2c2c2cc;
}
.listed-unlisted-toggle-container {
  width: 100%;
  max-width: 400px;
  margin: 0 auto 20px auto;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.listed-unlisted-toggle.ios-toggle {
  position: relative;
  width: 100%;
  max-width: 1000px;
  height: 30px;
  background: #1f1f1f;
  border-radius: 22px;
  display: flex;
  align-items: center;
  padding: 4px;
  box-sizing: border-box;
}

.toggle-track {
  position: absolute;
  top: 0px;
  left: 0px;
  right: 0px;
  bottom: 0px;
  background: #1f1f1f;
  border-radius: 50px;
  transition: all 0.3s ease;
}

.toggle-track.active {
  background: #1f1f1f;
}

.toggle-thumb {
  position: absolute;

  width: 50%;
  height: calc(100%);
  background: #ffbb00;
  border-radius: 20px;
  transition: all 0.3s ease;
}

.toggle-thumb.active {
  transform: translateX(100%);
}

.toggle-input {
  position: absolute;
  opacity: 0;
  width: 100%;
  height: 100%;
  cursor: pointer;
  z-index: 2;
}

.toggle-labels {
  position: relative;
  display: flex;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.toggle-label {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 500;
  color: #666;
  transition: color 0.3s ease;
  z-index: 1;
}

.toggle-label.active {
  color: white;
}

/* Расположение меток - Listed слева, Unlisted справа */
.toggle-labels {
  position: relative;
}

.toggle-label:first-child {
  order: 1;
}

.toggle-label:last-child {
  order: 2;
}

/* Для активного состояния - меняем порядок если нужно */
.toggle-track.active ~ .toggle-labels .toggle-label:first-child {
  color: #666;
}

.toggle-track.active ~ .toggle-labels .toggle-label:last-child {
  color: white;
}
.toggle-labels-below {
  display: flex;
  width: 100%;
  max-width: 1000px;
  margin-top: 5px;
}

.toggle-labels-below .toggle-label {
  font-size: 14px;
  font-weight: 500;
  color: #666;
  transition: color 0.3s ease;
}

.toggle-labels-below .toggle-label.active {
  color: #ffbb00;
  font-weight: 600;
}
.floor-price {
  display: block;
  font-size: 13px;
  color: rgb(109, 109, 109);
  margin-top: 4px;
  font-weight: 800 ;
}

.floor-price.no-floor {
  color: #ccc;
  font-style: italic;
}

/* Увеличьте специфичность для выбранных элементов */

/* Убедитесь, что hover не переопределяет selected */
.filter-option.selected:hover {
  background-color: rgba(255, 196, 0, 0.2) !important;
  transform: none !important;
}


.filter-header {
  display: flex;
  align-items: center; /* Выравниваем по центру по вертикали */
  gap: 10px;
  padding: 12px;

  height: 60px; /* Фиксированная высота для контейнера */
  box-sizing: border-box;
}

.search-box {
  flex: 1;
  display: flex;
}

.search-input {
  width: 100%;
  height: 36px; /* Фиксированная высота */
  padding: 0 12px;
  border-radius: 6px;
  font-size: 14px;
  box-sizing: border-box;
  margin: 0;
  line-height: 36px; /* Центрируем текст по вертикали */
  vertical-align: middle; /* Убираем смещение */
}

.clear-filter-btn {
  height: 36px; /* Такая же высота как у input */
  padding: 0 16px;
  background: #ca3a3a;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  flex-shrink: 0;
  min-width: 70px;
  font-weight: 800;
  line-height: 36px; /* Центрируем текст */
  vertical-align: middle; /* Убираем смещение */
}
.clear-filter-btn:hover:not(:disabled) {
  background: #ff5252;
  transform: translateY(-1px);
}

.clear-filter-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
  opacity: 0.6;
}

.clear-filter-btn:active:not(:disabled) {
  transform: translateY(0);
}
/* Убираем все возможные отступы и границы по умолчанию */
.search-input, .clear-filter-btn {
  margin: 0;
}

.clear-filter-btn {
  border-color: #ff6b6b; /* Граница того же цвета что и фон */
}

/* Адаптивность для мобильных */
@media (max-width: 768px) {
  .filter-header {
    height: 56px;
    padding: 10px;
    gap: 8px;
  }
  
  .search-input {
    height: 36px;
    line-height: 36px;
    padding: 0 10px;
    font-size: 16px; /* Увеличиваем для мобильных */
    font-weight: 700;
  }
  
  .clear-filter-btn {
    height: 36px;
    line-height: 36px;
    padding: 0 14px;
    min-width: 65px;
    font-size: 13px;
  }
}
.ton-floor-icon {
  width: 10px;
  height: 10px;
  vertical-align: middle;
  margin-left: 2px;
}

.floor-price {
  display: flex;
  align-items: center;
  gap: 2px;
}

.currency-icon-small{
  height: 11px;
  width: 11px;
  margin-left: 4px;
}


.filter-option.selected .option-rarity {
  color: #666;
}
.action-buttons-row {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin: 70px 0 10px 0;
  width: 100%;
}

.action-button-row {
  background-color: #2a2a2a;
  border: none;
  border-radius: 15px;
  width: 45.5%;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.action-button-row:hover {
  background-color: #3a3a3a;
  transform: translateY(-2px);
}

.action-button-row:active {
  transform: translateY(0);
}

.action-button-row:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.action-button-row.in-cart {
  background-color: #3a2a2a;
}

.action-button-icon {
  width: 20px;
  height: 20px;
  object-fit: contain;
}

/* Убедитесь, что info-container теперь идет после кнопок */
.info-container {
  margin-top: 0;
}
/* Добавьте в CSS */
.html-container {
  cursor: pointer;
  position: relative;
}

.html-container::after {
  position: absolute;
  bottom: 10px;
  left: 50%;
  transform: translateX(-50%);
  color: white;
  padding: 5px 10px;
  border-radius: 5px;
  font-size: 12px;
  opacity: 0;
  transition: opacity 0.3s;
  pointer-events: none;
}

.html-container:hover::after {
  opacity: 1;
}


.html-content-iframe {
  cursor: pointer;
  transition: transform 0.2s ease;
}

.html-content-iframe:active {
  transform: scale(0.98);
}

/* Опционально: добавить подсказку при наведении */
.html-container-wrapper {
  position: relative;
}

.html-container-wrapper::after {
  position: absolute;
  bottom: -25px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 5px 10px;
  border-radius: 4px;
  font-size: 12px;
  opacity: 0;
  transition: opacity 0.3s;
  pointer-events: none;
  white-space: nowrap;
}

.html-container-wrapper:hover::after {
  opacity: 1;
}
.offer-button-fullscreen {
  padding: 12px 24px;
  background-color: #2e2e2e;
  color: #cccccc;
  border: none;
  border-radius: 40px;
  cursor: pointer;
  width: 100%;
  font-size:20px;
  font-weight: 800;
}
.info-value-procent {
  color: #ffbb00;
  font-size: 0.9em;
  font-weight: 500;
  background: rgba(255, 179, 14, 0.15);
  border-radius: 20px;
  padding: 4px 8px;
  margin-left: 8px;
  white-space: nowrap;
}

.info-value-container {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.action-buttons-row-fullscreen {
  position: absolute;
  bottom: -10%;
  left: 0;
  right: 0;
  width: 100%;
  display: flex;
  gap: 10px;
  padding: 0 20px 20px;
  background: transparent;
}

.action-buttons-row-fullscreen button {
  flex: 1;
  padding: 12px 16px;
  border: none;
  border-radius: 15px;
  font-weight: 600;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
/* Кнопка Edit Price в карточках */
.edit-price-button {
  background: #19a3ff;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.95rem;
  margin-top: 5px;
  width: 100%;
  font-weight: bolder;
    width: 100%; /* Занимает всю ширину контейнера */
  padding: 8px 12px;
  border: none;
  border-radius: 20px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.2s;

}

.edit-price-button:hover {
  background: #0056b3;
}

.edit-price-button:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

/* Кнопка Edit Price в полноэкранном режиме */
.edit-price-button-fullscreen {
  padding: 12px 24px;
  background-color: #19a3ff7e;
  color: rgb(194, 194, 194);
  border: none;
  border-radius: 20px;
  cursor: pointer;
  width: 100%;
  margin-bottom: 60px;
  font-size: 16px;
  font-weight: 600;
  border: 2px solid #971515;

}

.edit-price-button-fullscreen:hover {
  background: #0056b3;
}

/* Стили для модального окна редактирования цены */
.price-details {
  margin: 15px 0;
  padding: 15px;
  background: #2a2a2a;
  border-radius: 8px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.detail-row:last-child {
  margin-bottom: 0;
}
/* Для карточек в гриде */
.item-actions {
  display: flex;
  flex-direction: column;
  gap: 5px;
  margin-top: 10px;
}

/* Для полноэкранного режима */
.action-buttons-row-fullscreen {
  display: flex;
  gap: 1 0px;
  margin-top: 20px;
  width: 100%;
  justify-content: space-between;
}
.unlisted-actions-fullwidth {
  position: fixed;
  bottom: 60px; /* Отступ снизу, чтобы не залезала на нижнее меню */
  left: 20px;
  right: 20px;
  z-index: 1000; /* Высокий z-index чтобы была поверх других элементов */
}

.full-width-button {
  width: 100%;
  margin-bottom: 12px;
  padding: 16px 20px;
  border: none;
  border-radius: 12px;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}
/* Гарантируем, что кнопки не перекрывают другие важные элементы */
.fullscreen-view {
  padding-bottom: 120px; /* Добавляем отступ снизу для контента */
}


.cart-overlay-button {
  position: absolute;
  bottom: 5px;
  left: 5px;
  width: 32px;
  height: 32px;
  background: rgba(0, 0, 0, 0);
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 10;
  transition: all 0.2s ease;
}

.cart-overlay-button:hover:not(:disabled) {
  background: rgba(0, 0, 0, 0.0);
  transform: scale(1.1);
}

.cart-overlay-button:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.cart-overlay-button.in-cart {
  background: rgba(0,0,0, 0.0);
}

.cart-overlay-button.in-cart:hover:not(:disabled) {
  background: rgba(220, 53, 69, 0.9);
}

.cart-overlay-icon {
  width: 35px;
  height: 35px;
  object-fit: contain;
}
/* Общие стили для всех модальных окон в стиле filter-dropdown */
.modal-dropdown {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 95%;
  max-width: 500px;
  max-height: 80vh;
  background: #1a1a1a;
  border-radius: 20px 20px 0 0;
  box-shadow: 0 -5px 25px rgba(0, 0, 0, 0.5);
  z-index: 1000;
  overflow: hidden;
  animation: slideUp 0.3s ease-out;
}

.modal-dropdown-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
  animation: fadeIn 0.3s ease-out;
}

.modal-drag-handle {
  width: 40px;
  height: 4px;
  background: #666;
  border-radius: 2px;
  margin: 12px auto;
  cursor: grab;
}

.modal-dropdown-header {
  padding: 16px 20px;
  border-bottom: 1px solid #333;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-dropdown-title {
  font-size: 18px;
  font-weight: 600;
  color: white;
  margin: 0;
}

.modal-dropdown-content {
  padding: 20px;
  max-height: calc(80vh - 120px);
  overflow-y: auto;
}

.modal-dropdown-actions {
  padding: 16px 20px;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

@keyframes slideUp {
  from {
    transform: translateX(-50%) translateY(100%);
  }
  to {
    transform: translateX(-50%) translateY(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
/* Обновленные стили для модальных окон - подняты выше */
.modal-dropdown {
  position: fixed;
  bottom: 60px; /* Поднимаем над нижним меню */
  left: 50%;
  transform: translateX(-50%);
  width: 95%;
  max-width: 500px;
  max-height: 70vh; /* Уменьшаем высоту чтобы не упиралось в верх */
  background: #1a1a1a;
  border-radius: 20px;
  box-shadow: 0 -5px 25px rgba(0, 0, 0, 0.5);
  z-index: 1000;
  overflow: hidden;
  animation: slideUpHigher 0.3s ease-out;
}

.modal-dropdown-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
  animation: fadeIn 0.3s ease-out;
}

.modal-drag-handle {
  width: 40px;
  height: 4px;
  background: #666;
  border-radius: 2px;
  margin: 12px auto;
  cursor: grab;
}

.modal-dropdown-header {
  padding: 16px 20px;
  border-bottom: 1px solid #333;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-dropdown-title {
  font-size: 18px;
  font-weight: 600;
  color: white;
  margin: 0;
}

.modal-dropdown-content {
  padding: 20px;
  max-height: calc(70vh - 120px); /* Уменьшаем высоту контента */
  overflow-y: auto;
}

.modal-dropdown-actions {
  padding: 16px 20px;
  border-top: 1px solid #333;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

/* Новая анимация - появляется выше */
@keyframes slideUpHigher {
  from {
    transform: translateX(-50%) translateY(100%);
    opacity: 0;
  }
  to {
    transform: translateX(-50%) translateY(0);
    opacity: 1;
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* Адаптация для маленьких экранов */
@media (max-height: 700px) {
  .modal-dropdown {
    bottom: 60px;
    max-height: 60vh;
  }
  
  .modal-dropdown-content {
    max-height: calc(60vh - 120px);
    padding: 15px;
  }
}

/* Убедимся что кнопки доступны */
.modal-dropdown-actions .cancel-button,
.modal-dropdown-actions .confirm-button {
  min-height: 44px; /* Минимальная высота для удобного тапа */
  padding: 20px 20px;
  font-size: 16px;
}

/* Стили для инпутов в модалках */
.modal-dropdown-content .input {
  min-height: 44px;
  font-size: 16px; /* Увеличиваем для удобства на мобильных */
}
.modal-dropdown-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}


.modal-drag-handle {
  width: 40px;
  height: 4px;
  background: #ddd;
  border-radius: 2px;
  margin: 8px auto;
}

.modal-dropdown-header {
  padding: 16px;
  border-bottom: 1px solid #333;
}

.modal-dropdown-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.modal-dropdown-content {
  padding: 16px;
}

.modal-dropdown-actions {
  padding: 16px;
  display: flex;
  gap: 12px;
  width: 100%;
}




.confirm-button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* Адаптация для полноэкранного режима */
.fullscreen-modal .modal-dropdown {
  width: 95%;
  max-width: 500px;
}
.cart-item-preview {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #2a2a2a;
  border-radius: 12px;
  margin-bottom: 16px;
}

.cart-item-html-wrapper {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
}

.cart-item-html-content {
  width: 100%;
  height: 100%;
  border: none;
  border-radius: 8px;
}

.cart-item-image {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  object-fit: cover;
  flex-shrink: 0;
}



.cart-item-name {
  font-weight: 600;
  font-size: 14px;
  color: #cccccc;
}

.cart-item-price-section {
  display: flex;
  align-items: center;
  gap: 4px;
}

.cart-item-price {
  font-weight: 600;
  font-size: 16px;
  color: #f59e0b;
}


.detail-label {
  font-weight: 500;
  color: #666;
}

.detail-value {
  font-weight: 600;
  color: #333;
}

.form-group-input {
  margin-bottom: 16px;
}

.form-group-input label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.form-group-input .input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
}
/* Добавьте эти стили в ваш CSS */
.cart-item-preview {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.cart-item-html-wrapper,
.cart-item-image {
  width: 60px;
  height: 60px;
  flex-shrink: 0;
}

.cart-item-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.cart-item-name-container {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.cart-item-name {
  font-weight: 600;
  font-size: 14px;
  color: #cccccc;
}

.cart-item-number {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

.cart-item-price-section {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

.cart-item-price {
  font-weight: 600;
  font-size: 17px;
  color: #ffbb00;
}

.currency-icon-small {
  width: 16px;
  height: 16px;
}
/* Activity Page Styles */
.activity-page {
  padding: 20px;
}

.activity-filters {
  margin-bottom: 20px;
}

.activity-filters .filter-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.activity-filters .filter-button {
  padding: 8px 16px;
  border: 1px solid #1b1b1b;
  border-radius: 20px;
  background: #3a3a3a;
  cursor: pointer;
  transition: all 0.3s ease;
}

.activity-filters .filter-button.active {
  background: #ffbb00;
  color: black;
  border-color: #ffbb00;
}

.activity-list {
  min-height: 400px;
}

.activity-items {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.activity-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border: 1px solid #1d1d1d;
  border-radius: 12px;
  background: #2a2a2a;
  gap: 15px;
}

.activity-nft-preview {
  flex-shrink: 0;
  width: 110px;
  height: 110px;
}
.activity-page {
  padding: 0;
  width: 100%;
}

.activity-container {
  width: 100%;
  max-width: 100%;
  margin: 0;
}
.activity-nft-preview .cart-item-html-wrapper {
  width: 100%;
  height: 100%;
}

.activity-nft-preview .cart-item-html-content {
  width: 100%;
  height: 100%;
  border-radius: 8px;
}

.activity-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.activity-nft-name {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #cccccc;
}

.nft-id {
  color: #666;
  font-size: 14px;
}

.activity-date {
  color: #888;
  font-size: 12px;
}

.activity-info {
  display: flex;
  align-items: center;
  gap: 15px;
  flex-wrap: wrap;
}

.activity-type {
  padding: 4px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
  text-transform: capitalize;
}

.activity-type.buy {
  background: #3d3d3d;
  font-size: 12px;
  font-weight: 800;  
  color: #2e7d32;

}

.activity-type.sell {
background: #3d3d3d;
  font-size: 12px;
  font-weight: 800;
    color: #ef6c00;
}

.activity-type.cancel_sale {
background: #3d3d3d;
  font-size: 12px;
  font-weight: 800;
    color: #c62828;
}

.activity-type.edit_price {
  color: #1565c0;
  background: #3d3d3d;
  font-size: 12px;
  font-weight: 800;
}
/* Стили для типов активности */
.activity-type.pending {
  color: #ffbb00;
  background: rgba(255, 187, 0, 0.1);
  font-size: 12px;
  font-weight: 800;
}

.activity-type.accepted {
  color: #16a34a;
  background: rgba(22, 163, 74, 0.1);
  font-size: 12px;
  font-weight: 800;
}

.activity-type.rejected {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
  font-size: 12px;
  font-weight: 800;
}


.activity-type.transfer {
background: #3d3d3d;
  font-size: 12px;
  font-weight: 800;  color: #7b1fa2;
}

.activity-price {
  display: flex;
  align-items: center;
  gap: 4px;
  font-weight: 600;
}

.price-amount {
  color: #ffbb00;
}

.activity-counterparty {
  color: #666;
  font-size: 14px;
}

.activity-amount {
  color: #666;
  font-size: 14px;
}

.loading-activity,
.empty-activity {
  text-align: center;
  padding: 40px;
  color: #666;
}
/* Стили для заголовка Activity */
.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 0 10px;
}

.activity-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0;
  color: #333;
}

.my-activity-toggle {
  display: flex;
  align-items: center;
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.toggle-text {
  font-size: 14px;
  font-weight: 500;
  color: #666;
}

.toggle-switch {
  width: 44px;
  height: 24px;
  background: #e0e0e0;
  border-radius: 12px;
  position: relative;
  transition: background 0.3s ease;
  cursor: pointer;
}

.toggle-switch.active {
  background: #007bff;
}

.toggle-slider {
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 50%;
  position: absolute;
  top: 2px;
  left: 2px;
  transition: transform 0.3s ease;
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}

.toggle-switch.active .toggle-slider {
  transform: translateX(20px);
}

/* Стили для элементов активности */
.activity-header-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.activity-user-badge {
  background: #007bff;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
}

.activity-user {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

.activity-item.my-activity {
  border-left: 3px solid #007bff;
}
/* Стили для Activity с ценой справа */
.activity-main-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  width: 100%;
  gap: 16px;
  
}

.activity-info-left {
  flex: 1;
  min-width: 0; /* Для правильного обрезания текста */
}

.activity-price-section {
  text-align: right;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.activity-price {
  left: 50px;
  gap: 4px;
  font-weight: 600;
  font-size: 16px;
  color: #333;
  
}

.price-amount {
  font-weight: 700;
}

.activity-total {
  font-size: 12px;
  color: #666;
  white-space: nowrap;
}

.activity-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
  flex-wrap: wrap;
}

.activity-type {
  font-size: 12px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 10px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Цвета для типов операций */
.activity-type.purchase {
  background: rgba(34, 197, 94, 0.1);
  color: #16a34a;
    border-radius: 10px;

}

.activity-type.delisting {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
    border-radius: 10px;

}

.activity-type.price_edit {
  background: rgba(59, 130, 246, 0.1);
  color: #2563eb;
  border-radius: 10px;

}

.activity-user {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

.activity-date {
  font-size: 12px;
  color: #999;
}

/* Адаптивность для мобильных */
@media (max-width: 768px) {
  .activity-main-row {
    flex-direction: column;
    gap: 8px;
  }
  
  .activity-price-section {
    align-items: flex-start;
    text-align: left;
    width: 100%;
  }
  
  .activity-meta {
    gap: 6px;
  }
}

/* Стили для элементов активности */
.activity-header-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.activity-nft-name {
  font-size: 14px;
  font-weight: 600;
  color: #cccccc;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
}

.nft-id {
  font-size: 12px;
  color: #666;
  font-weight: 400;
}

.activity-user-badge {
  background: #007bff;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
}

.activity-item.pending {
  border-left: 3px solid #ffbb00;
}
.activity-item.accepted {
  border-left: 3px solid #16a34a;
}
.activity-item.rejected {
  border-left: 3px solid #ef4444;
}
.activity-price-section {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  flex-shrink: 0;
}

.activity-price {
  display: flex;
  align-items: center;
  gap: 4px;
  font-weight: 600;
  font-size: 14px;
  color: #333;
}

.price-amount {
  font-weight: 700;
  font-size: 16px;
}

.currency-icon-small {
  width: 14px;
  height: 14px;
}

.currency-text {
  font-size: 12px;
  color: #666;
}

.activity-total {
  font-size: 11px;
  color: #888;
  text-align: right;
}
.activity-type-container {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.activity-type {
  font-weight: 600;
  font-size: 14px;
}

.activity-date {
  font-size: 12px;
  color: #888;
  margin-top: 2px;
}
/* Добавьте цвет для Listing */
.activity-type.listing {
  background: rgba(59, 130, 246, 0.1);
  color: #2563eb;
  border-radius: 10px;
}



.purchase-success-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10000;
}

.purchase-success-content {
  text-align: center;
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  animation: scaleIn 0.3s ease;
}

.success-title {
  color: #22c55e;
  font-size: 1.5rem;
  font-weight: bold;
  margin: 0;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@keyframes scaleIn {
  from {
    transform: scale(0.8);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}
.lottie-container {
  width: 200px;
  height: 200px;
  margin: 0 auto 1rem auto;
}

.purchase-success-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10000;
}

.purchase-success-content {
  text-align: center;
  background: none;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  animation: scaleIn 0.3s ease;
}

.success-title {
  color: #22c55e;
  font-size: 1.5rem;
  font-weight: bold;
  margin: 0;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@keyframes scaleIn {
  from {
    transform: scale(0.8);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}
.filter-button-icon {
  width: 20px;
  height: 20px;
  object-fit: contain;
}
.filter-button-icon-pending {
  width: 40px;
  height: 40px;
  object-fit: contain;
}
.filter-button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px 12px;
}
.tgs-fullscreen-view {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.95);
  z-index: 9999;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
}

.tgs-fullscreen-view svg {
  max-width: 90%;
  max-height: 90%;
  width: auto;
  height: auto;
}

.tgs-fullscreen-view .close-button {
  position: absolute;
  top: 20px;
  right: 20px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  font-size: 30px;
  cursor: pointer;
  transition: background 0.3s;
}

.tgs-fullscreen-view .close-button:hover {
  background: rgba(255, 255, 255, 0.3);
}

.tgs-fullscreen-view .title {
  color: white;
  font-size: 24px;
  margin-bottom: 20px;
  text-align: center;
  font-weight: bold;
}
.symbol-placeholder {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f0f0;
  border-radius: 8px;
  font-size: 20px;
}

.symbol-image {
  width: 40px;
  height: 40px;
  object-fit: contain;
  border-radius: 8px;
}
.symbol-placeholder {
  width: 40px;
  height: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f0f0f0;
  border-radius: 8px;
  font-size: 16px;
  position: relative;
}

.loading-text {
  font-size: 8px;
  margin-top: 2px;
  color: #666;
}

.symbol-image {
  width: 40px;
  height: 40px;
  object-fit: contain;
  border-radius: 8px;
}

.symbol-html-container {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  overflow: hidden;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
}

.symbol-html-iframe {
  width: 100%;
  height: 100%;
  border: none;
  background: transparent;
  pointer-events: none; /* Чтобы клики проходили сквозь iframe */
}

.symbol-placeholder {
  width: 60px;
  height: 60px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f0f0f0;
  border-radius: 8px;
  font-size: 16px;
}

.loading-text {
  font-size: 8px;
  margin-top: 2px;
  color: #666;
}



/* Адаптация для мобильных устройств */
@media (max-width: 768px) {
  .symbol-html-container {
    width: 50px;
    height: 50px;
  }
  
  .symbol-placeholder {
    width: 50px;
    height: 50px;
    font-size: 14px;
  }
}
.activity-price-section {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}

.activity-type-icon {
  position: absolute;
  top: -92px;
  right: -5px;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #252525;
}

.activity-type-image {
  width: 16px;
  height: 16px;
  object-fit: contain;
}
.activity-type-image-pending {
  width: 30px;
  height: 30px;
  object-fit: contain;
}
.activity-price {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 8px;
}

.activity-total {
  font-size: 12px;
  color: #666;
  text-align: right;
}
/* Стили для переключателя My Activity */
.my-activity-toggle {
  display: flex;
  align-items: center;
  margin-left: auto;
}

.toggle-label-activity {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.toggle-text {
  font-size: 14px;
  color: #666;
  white-space: nowrap;
}

.toggle-switch-activity {
  width: 44px;
  height: 24px;
  background-color: #e9ecef;
  border-radius: 12px;
  position: relative;
  transition: background-color 0.3s ease;
  border: 1px solid #ddd;
}

.toggle-switch.active {
  background-color: #007bff;
  border-color: #007bff;
}

.toggle-slider-activity {
  width: 20px;
  height: 20px;
  background-color: white;
  border-radius: 50%;
  position: absolute;
  top: 1px;
  left: 1px;
  transition: transform 0.3s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.toggle-slider-activity.active {
  transform: translateX(20px);
}

/* iOS-подобная анимация */
.toggle-switch-activity {
  -webkit-tap-highlight-color: transparent;
}

.toggle-slider-activity {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.toggle-input-activity {
  display: none;
}

.toggle-label-activity {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  cursor: pointer;
}

.toggle-text-activity {
  font-size: 12px;
  color: #666;
  white-space: nowrap;
  font-weight: 800;
}

.toggle-switch-activity {
  width: 78px;
  height: 20px;
  background-color: #e9ecef;
  border-radius: 12px;
  position: relative;
  transition: background-color 0.3s ease;
  border: 1px solid #ddd;
  cursor: pointer;
}

.toggle-input-activity:checked + .toggle-switch-activity {
  background-color: #ffbb00;
  border-color: #ffbb00;
}

.toggle-slider-activity {
  width: 16px;
  height: 16px;
  background-color: white;
  border-radius: 50%;
  position: absolute;
  top: 1px;
  left: 1px;
  transition: transform 0.3s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.4);
}

.toggle-input-activity:checked + .toggle-switch-activity .toggle-slider-activity {
  transform: translateX(58px);
}


.nft-id-activity {
  font-size: 11px;
  color: #666;
  font-weight: bolder;
  margin-top: 2px;
}
.filter-dropdown-menu {
  /* Остальные стили остаются без изменений */
  display: flex;
  flex-direction: column;
}

.filter-header {
  position: sticky;
  top: 0;
  z-index: 10;
  padding: 12px 16px;
  /* Остальные стили остаются */
}

.modal-drag-handle {
  position: sticky;
  top: 0;
  z-index: 11;
  /* Остальные стили остаются */
}

.filter-options-container {
  overflow-y: auto;
  flex: 1;
  /* Остальные стили остаются */
}
.purchase-fail-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10000;
}

.purchase-fail-content {
  background: none;
  border: none;
  border-radius: 16px;
  padding: 2rem;
  text-align: center;
}

.fail-title {
  color: #ef4444;
  margin-top: 1rem;
  font-size: 1.5rem;
  font-weight: 600;
}
.action-button-row.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-button-row.disabled:hover {
  transform: none;
}
.free-transfer-info {
  padding: 10px 0;
  margin-bottom: 15px;
  background: #f8fff8;
  border-radius: 8px;
  padding: 15px;
}

.free-badge {
  background: #22c55e;
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.free-button {
  background: #22c55e !important;
}

.free-button:hover {
  background: #16a34a !important;
}
/* В существующие стили добавьте: */

.market-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  padding: 16px;
}

/* Для маленьких экранов (500px и меньше) */
@media (max-width: 800px) {
  .market-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
    padding: 8px;
  }
  
  .market-item {
    min-width: unset;
    width: 100%;
  }
}
.filter-dropdown-menu {
  touch-action: pan-y; /* Разрешаем только вертикальный скролл */
}

/* Когда фильтр открыт, предотвращаем скролл body */
body.filter-menu-open {
  overflow: hidden;
  position: fixed;
  width: 100%;
  height: 100%;
}
.offer-button-fullscreen,
.buy-button-fullscreen {
    margin-bottom: 130px; /* Поднимаем каждую кнопку */
}
.edit-price-button-fullscreen,
.cancel-sale-button-fullscreen {
    margin-bottom: 130px; /* Поднимаем каждую кнопку */
}


.modal-dropdown.sell-modal {
  display: flex;
  flex-direction: column;
  max-height: 70vh;
}

.modal-dropdown.sell-modal .modal-dropdown-content {
  flex: 1;
  overflow-y: auto;
  max-height: none;
}

.modal-dropdown.sell-modal .modal-dropdown-actions {
  flex-shrink: 0;
  margin-top: auto;
  padding-top: 15px;
  gap:10px

}
.modal-dropdown.sell-modal .modal-dropdown-actions {
  display: flex;
  width: 100%;
  gap: 8px;
}

.modal-dropdown.sell-modal .modal-dropdown-actions > div {
  display: flex;
  width: 100%;
  gap: 8px;
}

.modal-dropdown.sell-modal .cancel-button,
.modal-dropdown.sell-modal .confirm-button {
  height:20px;
  width: 100%;
  margin: 0;
  box-sizing: border-box;
  border-radius: 15px;
}
.modal-dropdown-actions {
  display: flex;
  gap: 10px;
  padding: 16px;
  border-top: 1px solid #e0e0e0;
}

.cancel-button, .confirm-button {
  flex: 1;
  padding: 12px 16px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 44px; /* Минимальная высота для удобства касания */
  line-height: 1.2; /* Нормальный межстрочный интервал */
}

/* Специфичные стили для каждой кнопки */
.cancel-button {
  color: #666;
}


.confirm-button {
  color: white;
}



.confirm-button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}
.confirm-button.disabled {
  background-color: #95a5a6 !important;
  border-color: #95a5a6 !important;
  color: #7f8c8d !important;
  cursor: not-allowed !important;
  opacity: 0.7 !important;
}

.confirm-button:disabled {
  background-color: #95a5a6 !important;
  border-color: #95a5a6 !important;
  color: #7f8c8d !important;
  cursor: not-allowed !important;
  opacity: 0.7 !important;
}
.ton-balance.balance-container {
  display: flex;
  align-items: center;
  gap: 3px;
}

.ton-balance .currency-icon-black {
  width: 16px;
  height: 16px;
  object-fit: contain;
  left:2px;
}
/* Стили для HTML контента офферов */
.activity-nft-preview {
  width: 110px;
  height: 110px;
  border-radius: 12px;
  overflow: hidden;
  flex-shrink: 0;
  position: relative;
}

.cart-item-html-wrapper {
  width: 100%;
  height: 100%;
  position: relative;
}

.cart-item-html-content {
  width: 100%;
  height: 100%;
  border: none;
  background: transparent;
  border-radius: 12px;
}
.symbol-html-container {
  width: 40px;
  height: 40px;
  min-width: 40px;
  min-height: 40px;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.symbol-html-iframe {
  width: 100%;
  height: 100%;
  border: none;
  background: transparent;
  display: block;
}

.symbol-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f0f0f0;
  color: #999;
  font-size: 12px;
}

.loading-text {
  font-size: 8px;
  margin-top: 2px;
}
.back-button-container {
  padding: 16px 20px;
  position: sticky;
  top: 0;
  z-index: 100;
}

.modern-back-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: linear-gradient(135deg, #FFD700, #FFA500);
  border: none;
  border-radius: 20px;
  color: #000;
  font-weight: 600;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(255, 215, 0, 0.3);
  position: relative;
  overflow: hidden;
  
}

.modern-back-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
  transition: left 0.5s ease;
}

.modern-back-button:hover::before {
  left: 100%;
}

.modern-back-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 215, 0, 0.4);
  background: linear-gradient(135deg, #FFE135, #FFB347);
}

.modern-back-button:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(255, 215, 0, 0.3);
}

.back-arrow {
  font-size: 18px;
  font-weight: bold;
  transition: transform 0.2s ease;
}

.modern-back-button:hover .back-arrow {
  transform: translateX(-2px);
}

/* Адаптивность */
@media (max-width: 768px) {
  .back-button-container {
    padding: 12px 16px;
  }
  
  .modern-back-button {
    padding: 10px 16px;
    font-size: 14px;
  }
}
.back-button-container {

  
  /* Регулировка отступов */
  margin: -20px 0 0 -10px; /* сверху 20px, слева 20px */
}
.activity-nft-preview {
  cursor: pointer;
  transition: transform 0.2s ease;
}

.activity-nft-preview:hover {
  transform: scale(1.02);
}

.cart-item-html-wrapper {
  pointer-events: none; /* Чтобы клики проходили через iframe к контейнеру */
}

.cart-item-html-content {
  pointer-events: none; /* Отключаем взаимодействие с iframe */
}
.activity-nft-preview {
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 12px;
  overflow: hidden;
  position: relative;
}

.activity-nft-preview::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.1);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.activity-nft-preview:hover::after {
  opacity: 1;
}

.activity-nft-preview:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
.pending-offer-actions-fullwidth {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
}

.accept-button-fullscreen {
  background: linear-gradient(135deg, #4CAF50, #45a049);
  color: white;
  border: none;
  padding: 16px 24px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;
}

.accept-button-fullscreen:hover:not(:disabled) {
  background: linear-gradient(135deg, #45a049, #4CAF50);
  transform: translateY(-2px);
}

.accept-button-fullscreen:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.reject-button-fullscreen {
  background: linear-gradient(135deg, #f44336, #d32f2f);
  color: white;
  border: none;
  padding: 16px 24px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;
}

.reject-button-fullscreen:hover:not(:disabled) {
  background: linear-gradient(135deg, #d32f2f, #f44336);
  transform: translateY(-2px);
}

.reject-button-fullscreen:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.pending-offer-actions-horizontal {
  display: flex;
  gap: 12px;
  width: 100%;
  justify-content: space-between;
}

.horizontal-button {
  flex: 1;
  min-height: 50px;
  border-radius: 12px;
  border: none;
  font-weight: 600;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.accept-button-fullscreen.horizontal-button {
  background: #16a34a;
  color: white;
}

.accept-button-fullscreen.horizontal-button:hover:not(:disabled) {
  background:#16a34a;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 184, 148, 0.3);
}

.accept-button-fullscreen.horizontal-button:disabled {
  background: #b2bec3;
  cursor: not-allowed;
  transform: none;
}

.reject-button-fullscreen.horizontal-button {
  background:  #ef4444;
  color: white;
}

.reject-button-fullscreen.horizontal-button:hover:not(:disabled) {
  background:  #ef4444;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(225, 112, 85, 0.3);
}

.reject-button-fullscreen.horizontal-button:disabled {
  background: #b2bec3;
  cursor: not-allowed;
  transform: none;
}
.action-button-row.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}
.activity-list {
  max-height: 70vh;
  overflow-y: auto;
  scroll-behavior: smooth;
  border-radius: 8px;
  padding: 10px;
}

/* Стили для индикаторов загрузки */
.loading-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  color: #666;
}



@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}



.load-more-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  gap: 10px;
}

.load-more-btn {
  background: #007bff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
  transition: background 0.3s;
}

.load-more-btn:hover:not(:disabled) {
  background: #0056b3;
}

.load-more-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.debug-info {
  color: #888;
  font-size: 12px;
}
.go-to-market-button.prominent {
  background: linear-gradient(135deg, #28a745, #20c997);
  padding: 16px 28px;
  min-width: 280px;
}

.go-to-market-button.prominent:hover {
  background: linear-gradient(135deg, #218838, #1e7e34);
}

.button-content {
  text-align: left;
  flex-grow: 1;
}

.button-main-text {
  font-size: 16px;
  font-weight: 700;
}

.button-sub-text {
  font-size: 12px;
  opacity: 0.9;
  margin-top: 2px;
}
.market-action-button-container {
  width: 100%;
  margin-bottom: 16px;
}

.market-action-button.full-width {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 16px 24px;
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
}

.market-action-button.full-width:hover {
  background: linear-gradient(135deg, #218838, #1e7e34);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(40, 167, 69, 0.4);
}

.market-action-button.full-width:active {
  transform: translateY(0);
}

.market-action-button .button-text {
  font-size: 16px;
  font-weight: 600;
}

.market-action-button .button-icon {
  transition: transform 0.3s ease;
}

.market-action-button:hover .button-icon {
  transform: translateX(3px);
}

/* Адаптация для мобильных устройств */
@media (max-width: 768px) {
  .market-action-button.full-width {
    padding: 14px 20px;
    font-size: 15px;
  }
}
/* Добавьте в style секцию: */
.market-action-button-container {
  padding: 0 20px 20px;
  margin-top: 10px;
}

.market-action-button {
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 14px 20px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.market-action-button:hover {
  background: linear-gradient(135deg, #0056b3, #004085);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 123, 255, 0.4);
}

.market-action-button:active {
  transform: translateY(0);
}

.market-action-button.full-width {
  width: 100%;
}

.button-text {
  font-size: 15px;
  font-weight: 600;
}

.debug-info {
  display: none; /* Скрываем debug информацию в продакшене */
}
/* Добавьте в style секцию */
.market-action-button-container {
  padding: 0 20px;
  margin: 15px 0;
}

.market-action-button {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 14px 20px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
}

.market-action-button:hover {
  background: linear-gradient(135deg, #218838, #1e9e8a);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(40, 167, 69, 0.4);
}

.market-action-button:active {
  transform: translateY(0);
}

.button-text {
  font-size: 15px;
  font-weight: 600;
}
/* Убедитесь что эти стили не скрывают кнопку */
.market-action-button-container {
  display: block !important;
  visibility: visible !important;
  opacity: 1 !important;
}

.market-action-button {
  display: block !important;
  width: 100% !important;
  background: green !important; /* Яркий цвет для теста */
  color: white !important;
  padding: 15px !important;
  font-size: 16px !important;
  border: none !important;
  border-radius: 10px !important;
  margin: 10px 0 !important;
}
/* Стили для кнопки маркета под другими кнопками */
.market-action-button-container.full-width-container {
  width: 100%;
  padding: 0 20px;
  margin-top: 15px;
}

.market-action-button.full-width {
  width: 100%;
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 16px 20px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
}

.market-action-button.full-width:hover {
  background: linear-gradient(135deg, #218838, #1e9e8a);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(40, 167, 69, 0.4);
}

.market-action-button.full-width:active {
  transform: translateY(0);
}

.button-text {
  font-size: 15px;
  font-weight: 600;
}

/* Стили для горизонтальных кнопок офферов */
.pending-offer-actions-horizontal {
  display: flex;
  gap: 12px;
  width: 100%;
  padding: 0 20px;
}

.horizontal-button {
  flex: 1;
  padding: 14px 20px;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.reject-button-fullscreen {
  background: linear-gradient(135deg, #dc3545, #c82333);
  color: white;
}

.accept-button-fullscreen {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
}

.horizontal-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.horizontal-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}
.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 15px;
  width: 100%;
  padding: 0 20px;
}

.market-action-button-container {
  width: 100%;
}

.market-action-button.full-width {
  width: 100%;
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 16px 20px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
}

.market-action-button.full-width:hover {
  background: linear-gradient(135deg, #218838, #1e9e8a);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(40, 167, 69, 0.4);
}

.market-action-button.full-width:active {
  transform: translateY(0);
}

.button-text {
  font-size: 15px;
  font-weight: 600;
}

/* Стили для горизонтальных кнопок офферов */
.pending-offer-actions-horizontal {
  display: flex;
  gap: 12px;
  width: 100%;
}

.horizontal-button {
  flex: 1;
  padding: 14px 20px;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.reject-button-fullscreen {
  background: linear-gradient(135deg, #dc3545, #c82333);
  color: white;
}

.accept-button-fullscreen {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
}

.horizontal-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.horizontal-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}
.offer-action-button-container {
  width: 100%;
  margin-top: 20px;
}

.offer-action-button {
  width: 100%;
  padding: 14px 20px;
  background-color: #ffbb00; /* Фон кнопки */
  color: #1b1b1b; /* Цвет текста */
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.offer-action-button:hover {
  background-color: #ffcc33; /* Более светлый желтый при наведении */
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 187, 0, 0.3);
}

.offer-action-button:active {
  transform: translateY(0);
  background-color: #e6a800; /* Более темный желтый при нажатии */
}

.button-text {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Добавьте это в глобальные стили вашего приложения */
* {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif !important;
}

</style>