<template>
  <div class="page-container">
    <div class="profile-card">
      <img :src="amahaslaImage" alt="Profile" class="avatar" />
      <h2 class="username">{{ currentAccountName }}</h2>
      <div class="score">
        <span>{{ userScore }}</span>
      </div>
    
    <!-- Навигация между страницами -->
    <div class="navigation">
      <button class="nav-button" @click="setActiveTab('my-nfts')" :class="{ active: activeTab === 'my-nfts' }">
        My Gifts
      </button>
      <button class="nav-button" @click="setActiveTab('activity')" :class="{ active: activeTab === 'activitly' }">
        Activity
      </button>
    </div>
    </div>
   <div class="filter-system" v-click-outside="closeFilterMenu">
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
    @touchstart.passive="startDrag"
    @mousedown="startDrag"
  >
    <div class="modal-drag-handle"></div>
    
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
        :key="'selected-' + symbol.value"
        class="filter-option selected"
        @click.stop="toggleFilterOption('symbol', symbol.name)"
      >
        <img 
          :src="symbol.imageUrl" 
          :alt="symbol.name" 
          class="symbol-image"
          @error="handleSymbolImageError"
        >
        <div class="option-content">
  <span class="option-text">{{ symbol.name }}</span>
  <span class="option-count" v-if="symbol.count">({{ symbol.count }})</span>
  <span v-if="symbol.floorPrice" class="floor-price">
    {{ symbol.floorPrice }} <img :src="tonlogofloor" alt="TON" class="ton-floor-icon">
  </span>
  <span v-else class="floor-price no-floor"></span>
  <span class="option-rarity">{{ symbol.rarityText }}</span>
  
</div>
      </div>
      
      <!-- Затем невыбранные символы -->
      <div 
        v-for="symbol in getUnselectedSymbolOptions()"
        :key="'unselected-' + symbol.value"
        class="filter-option"
        :class="{ selected: isOptionSelected('symbol', symbol.name) }"
        @click.stop="toggleFilterOption('symbol', symbol.name)"
      >
        <img 
          :src="symbol.imageUrl" 
          :alt="symbol.name" 
          class="symbol-image"
          @error="handleSymbolImageError"
        >
        <div class="option-content">
  <span class="option-text">{{ symbol.name }}</span>
  <span class="option-count" v-if="symbol.count">({{ symbol.count }})</span>
  <span v-if="symbol.floorPrice" class="floor-price">
    {{ symbol.floorPrice }} <img :src="tonlogofloor" alt="TON" class="ton-floor-icon">
  </span>
  <span v-else class="floor-price no-floor"></span>
  <span class="option-rarity">{{ symbol.rarityText }}</span>
  
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
<transition name="filter-dropdown" class="nft">
  <div 
    class="filter-dropdown-menu filter-dropdown-menu-nft"
    v-if="activeFilterCategory === 'nft'"
    @touchstart.passive="startDrag"
    @mousedown="startDrag"
  >
    <div class="modal-drag-handle"></div>
    
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
      <div 
        v-for="option in getSortedNftOptions()"
        :key="option.originalType"
        class="filter-option"
        :class="{ selected: isOptionSelected('nft', option.originalType) }"
        @click.stop="toggleFilterOption('nft', option.originalType)"
      >
        <img 
          v-if="option.imageUrl" 
          :src="option.imageUrl" 
          :alt="option.name" 
          class="option-image"
          @error="handleImageError"
        >
        <div class="option-content">
          <span class="option-text">{{ option.name }}</span>
          <span v-if="option.floorPrice" class="floor-price">
            {{ option.floorPrice }} <img :src="tonlogofloor" alt="TON" class="ton-floor-icon">
          </span>
          <span v-else class="floor-price no-floor"></span>
        </div>
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
    @touchstart.passive="startDrag"
    @mousedown="startDrag"
  >
    <div class="modal-drag-handle"></div>
    
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
          :src="modelData.imageUrl" 
          :alt="modelData.name" 
          class="option-image"
          @error="handleImageError"
        >
        <div class="option-content">
          <span class="option-text">{{ modelData.name }}</span>
          <span class="option-rarity">{{ modelData.rarityText }}</span>
          <span v-if="modelData.floorPrice" class="floor-price">
            {{ modelData.floorPrice.toFixed(1) }} <img :src="tonlogofloor" alt="TON" class="ton-floor-icon">
          </span>
          <span v-else class="floor-price no-floor"></span>
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
          :src="modelData.imageUrl" 
          :alt="modelData.name" 
          class="option-image"
          @error="handleImageError"
        >
        <div class="option-content">
          <span class="option-text">{{ modelData.name }}</span>
          <span class="option-rarity">{{ modelData.rarityText }}</span>
          <span v-if="modelData.floorPrice" class="floor-price">
            {{ modelData.floorPrice.toFixed(1) }} <img :src="tonlogofloor" alt="TON" class="ton-floor-icon">
          </span>
          <span v-else class="floor-price no-floor"></span>
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
              :src="model.imageUrl" 
              :alt="model.name"
              class="option-image"
              @error="handleImageError"
            >
            <div class="option-content">
              <span class="option-text">{{ model.name }}</span>
              <span class="option-rarity">{{ model.rarityText }}</span>
              <span v-if="model.floorPrice" class="floor-price">
                {{ model.floorPrice.toFixed(1) }} <img :src="tonlogofloor" alt="TON" class="ton-floor-icon">
              </span>
              <span v-else class="floor-price no-floor"></span>
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
              :src="model.imageUrl" 
              :alt="model.name"
              class="option-image"
              @error="handleImageError"
            >
            <div class="option-content">
              <span class="option-text">{{ model.name }}</span>
              <span class="option-rarity">{{ model.rarityText }}</span>
              <span v-if="model.floorPrice" class="floor-price">
                {{ model.floorPrice.toFixed(1) }} <img :src="tonlogofloor" alt="TON" class="ton-floor-icon">
              </span>
              <span v-else class="floor-price no-floor"></span>
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
  </div>
<!-- Backdrop Filter Dropdown -->
<transition name="filter-dropdown">
   <div 
    class="filter-dropdown-menu filter-dropdown-menu-backdrop"
    v-if="activeFilterCategory === 'backdrop'"
    @click.stop 
    @mousedown.stop
  >
    <div class="modal-drag-handle"></div>
    
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
    {{ color.floorPrice }} <img :src="tonlogofloor" alt="TON" class="ton-floor-icon">
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
    {{ color.floorPrice }} <img :src="tonlogofloor" alt="TON" class="ton-floor-icon">
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
  </div>
   <div class="balance-filter-container" v-if="activeTab === 'market'">
      <div v-if="tonConnectUI?.connected" class="ton-balance balance-container">
        <span>{{ tonBalance }} TON</span>
      </div>
      
    
    <div class="filter-buttons">
      <!-- Кнопка корзины -->
      <div class="cart-button-wrapper">
        <button class="filter-button" @click.stop="toggleCartMenu">
          <img :src="bucket_img" alt="Cart" class="filter-icon-img">
          <!-- Вот эта красная иконка с количеством -->
          <span v-if="cartItems.length > 0" class="cart-badge">{{ getTotalNFTsInCart() }}</span>
        </button>
      </div>
      
      <button class="filter-button" @click.stop="toggleSortMenu">
        <img :src="filter_img" alt="Filter" class="filter-icon-img">
      </button>
      
      <button class="filter-button" @click.stop="togglePriceRangeMenu">
        <img :src="sell_img" alt="Price Range" class="filter-icon-img">
      </button>

<transition name="slide-fade">
    <div 
      v-if="sortMenu.show" 
      class="sort-menu" 
      v-click-outside="() => sortMenu.show = false"
      :style="{ right: '10px', top: '50px' }"
    >
      <div 
        v-for="option in sortMenu.options" 
        :key="option.id"
        class="sort-option"
        :class="{ selected: sortMenu.selected === option.id }"
        @click="applySort(option.id)"
      >
        <span>{{ option.name }}</span>
      
      </div>
    </div>
  </transition>
  <transition name="slide-fade">
        <div 
          v-if="cartMenu.show" 
          class="cart-menu" 
          v-click-outside="() => cartMenu.show = false"
          :style="{ right: '10px', top: '50px' }"
        >
          <div class="cart-header">
            <h4 class="cart-total-obyav">Cart ({{ cartItems.length }})</h4>
            <button class="clear-cart-btn" @click="clearCart" v-if="cartItems.length > 0">
              Clear
            </button>
          </div>
          
          <div v-if="cartItems.length === 0" class="empty-cart">
            Your cart is empty
          </div>
          
          <div v-else class="cart-items">
  <div 
    v-for="(item, index) in cartItems" 
    :key="item.id + '-' + index" 
    class="cart-item"
    @click="openCartItemModal(item)" 
  >
    <!-- HTML контент вместо изображения -->
    <div v-if="item.html_content" class="cart-item-html-wrapper">
      <iframe 
        sandbox="allow-scripts allow-same-origin"
        :srcdoc="addSquareStyles(item.html_content)"
        class="cart-item-html-content"
        @load="forceSquareStyles"
      ></iframe>
    </div>
    <img v-else :src="getNftImage(item.nft_type)" :alt="item.nft_type" class="cart-item-image">
    <div class="cart-item-info">
        <span class="cart-item-name">{{ getNftDisplayName(item.nft_type) }}</span>
        <span class="cart-item-price">{{ item.price_per_unit }}</span>
        <img v-if="item.currency === 'TON'" :src="tonlogoyellow" alt="TON" class="currency-icon-small">
      </div>
    <button class="remove-from-cart-btn" @click.stop="removeFromCart(item.id)">
      ×
    </button>
  </div>
</div>
          
          <div class="cart-total" v-if="cartItems.length > 0">
    <span>{{ calculateCartTotal() }}</span>
    <img :src="tonlogogray" alt="TON" class="currency-icon-small">
  </div>
          
          <button 
            class="buy-all-btn" 
            @click="buyAllFromCart"
            :disabled="cartItems.length === 0"
            v-if="cartItems.length > 0"
          >
            Buy All
          </button>
        </div>
      </transition>
  <transition name="slide-fade">
    <div 
      v-if="priceRangeMenu.show" 
      class="price-range-menu" 
      v-click-outside="() => priceRangeMenu.show = false"
      :style="{ right: '10px', top: '50px' }"
    >
      <div class="price-range-header">
        <h4>Price</h4>
      </div>
      <div class="price-range-inputs">
        <div class="input-group">
          <label>Min</label>
          <input 
            v-model="priceRangeMenu.minPrice" 
            type="number" 
            placeholder="0"
            min="0"
            step="0.01"
          >
        </div>
        <div class="input-group">
          <label>Max</label>
          <input 
            v-model="priceRangeMenu.maxPrice" 
            type="number" 
            placeholder="∞"
            min="0"
            step="0.01"
          >
        </div>
      </div>
      <div class="price-range-actions">
        <button class="reset-btn" @click="resetPriceRange">
          Reset
        </button>
        <button class="apply-btn" @click="applyPriceRange">
          Apply
        </button>
      </div>
    </div>
  </transition>
</div>
      <div v-if="activeTab === 'market'" class="filter-container">
        
        <div v-if="showFilterDropdown" class="filter-dropdown">
    <div class="search-box">
      <input 
        v-model="searchQuery" 
        type="text" 
        placeholder="Search..." 
        class="search-input"
      >
    </div>
        </div>

            </div>
    </div>
    <!-- Страница "Мои NFT" -->
<!-- Страница "Мои NFT" -->
<div v-if="activeTab === 'my-nfts'" class="market-page">
  <div class="listed-unlisted-toggle-container">
    <div class="listed-unlisted-toggle ios-toggle">
      <div class="toggle-track" :class="{ active: myNftsViewMode === 'unlisted' }">
        <div class="toggle-thumb" :class="{ active: myNftsViewMode === 'unlisted' }"></div>
      </div>
      
      <input 
        type="checkbox" 
        class="toggle-input" 
        :checked="myNftsViewMode === 'unlisted'"
        @change="toggleMyNftsViewMode"
      >
    </div>
    
    <div class="toggle-labels-below">
      <span class="toggle-label" :class="{ active: myNftsViewMode === 'listed' }">Listed</span>
      <span class="toggle-label" :class="{ active: myNftsViewMode === 'unlisted' }">Unlisted</span>
    </div>
  </div>
  
  <div class="market-container">
    <div class="market-grid">
      <!-- Используем filteredMarketItems для обеих вкладок -->
      <template v-if="myNftsViewMode === 'listed'">
        <div v-for="item in filteredMarketItems" :key="item.id" class="market-item" :class="{ 'ton': item.currency === 'TON' }">
          <!-- HTML контент -->
          <div v-if="item.html_content" class="nft-html-wrapper">
            <iframe 
              sandbox="allow-scripts allow-same-origin"
              :srcdoc="item.html_content"
              class="nft-html-content"
            ></iframe>
            <!-- Кнопка добавления/удаления из корзины -->
            <button 
              v-if="item.seller !== currentAccountName" 
              class="cart-action-button"
              @click.stop="isInCart(item.id) ? removeFromCart(item.id, $event) : addToCart(item, $event)"
              :disabled="item.seller === currentAccountName"
              :title="isInCart(item.id) ? 'Remove from cart' : 'Add to cart'"
              :class="{ 'in-cart': isInCart(item.id) }"
            >
              <img 
                :src="isInCart(item.id) ? rubish_bucket_icon : bucket_icon" 
                :alt="isInCart(item.id) ? 'Remove from cart' : 'Add to cart'" 
                class="cart-action-icon"
              >
            </button>
          </div>
          <img v-else :src="getNftImage(item.nft_type)" class="nft-image">
          
          <div class="nft-info-container">
            <h6 class="hustler">{{ getNftDisplayName(item.nft_type, item.nft_object)}} </h6>
            <span class="nft-id" v-if="item.nft_object">#{{ extractNftId(item.nft_object) }}</span>
          </div>  
          <div class="item-actions">
            <button 
              v-if="item.seller !== currentAccountName" 
              class="buy-button" 
              @click.stop="handleBuyClick(item)" 
              :disabled="item.seller === currentAccountName"
            >
              {{ item.price_per_unit }} {{ item.currency }}
            </button>
            <button 
              v-if="item.seller === currentAccountName" 
              class="cancel-sale-button" 
              @click.stop="handleBuyClick(item)"
            >
              Cancel sale
            </button>
          </div>
        </div>
        
        <div v-if="filteredMarketItems.length === 0" class="empty-message">
          У вас нет активных объявлений на рынке
        </div>
      </template>
      
      <!-- Показываем unlisted NFT -->
      <template v-else>
        <div class="market-item add-card" @click="handleAddNft">
          <div class="empty-nft-square">
            <span class="add-icon">+</span>
            <span class="add-text">Add Gift</span>
          </div>
        </div>
        
        <div v-for="item in filteredMarketItems" :key="'unlisted-'+item.id" class="market-item">
          <!-- HTML контент -->
          <div class="nft-html-wrapper">
            <iframe 
              sandbox="allow-scripts allow-same-origin"
              :srcdoc="generateNftHtml(item.nft_object)"
              class="nft-html-content"
            ></iframe>
          </div>
          
          <div class="nft-info-container">
            <h6 class="hustler">{{ getNftDisplayName(item.nft_type, item.nft_object) }}</h6>
            <span class="nft-id">#{{ extractNftId(item.nft_object) }}</span>
          </div>  
          
          <div class="action-buttons-container">
            <button 
              class="action-btn action-btn-send full-width flat-button"
              @click.stop="handleTransfer(item.nft_object)"
            >
              <span class="btn-text">Send</span>
            </button>
            
            <div class="row-buttons with-spacing">
              <button 
                class="action-btn action-btn-sale compact-btn"
                @click.stop="openHtmlModalForUnlisted(item.nft_object)"
              >
                <div class="btn-content">
                  <img :src="cennik" alt="Sell" class="btn-icon-img-large-sell">
                </div>
              </button>
              <button 
                class="action-btn action-btn-withdraw compact-btn"
                @click.stop="handleWithdraw(item.nft_object)"
              >
                <img :src="withdraw_icon" alt="Withdraw" class="btn-icon-img-large">
              </button>
            </div>
          </div>
        </div>
        
        <div v-if="filteredMarketItems.length === 0" class="empty-message">
          У вас нет непредложенных NFT
        </div>
      </template>
    </div>
  </div>
</div>

    <!-- Страница "Рынок" -->
    <!-- Страница "Рынок" -->
<div v-else class="market-page">
  <div class="market-container">
    <div class="market-grid">
      <!-- В шаблоне, в секции market-item -->
<!-- В шаблоне, в секции market-item -->
<div v-for="item in filteredMarketItems" :key="item.id" class="market-item" :class="{ 'ton': item.currency === 'TON' }">
    <!-- HTML контент -->
    <div v-if="item.html_content" class="nft-html-wrapper">
      <iframe 
        sandbox="allow-scripts allow-same-origin"
        :srcdoc="item.html_content"
        class="nft-html-content"
      ></iframe>
      <!-- Кнопка добавления/удаления из корзины -->
      <button 
        v-if="item.seller !== currentAccountName" 
        class="cart-action-button"
        @click.stop="isInCart(item.id) ? removeFromCart(item.id, $event) : addToCart(item, $event)"
        :disabled="item.seller === currentAccountName"
        :title="isInCart(item.id) ? 'Remove from cart' : 'Add to cart'"
        :class="{ 'in-cart': isInCart(item.id) }"
      >
        <img 
          :src="isInCart(item.id) ? rubish_bucket_icon : bucket_icon" 
          :alt="isInCart(item.id) ? 'Remove from cart' : 'Add to cart'" 
          class="cart-action-icon"
        >
      </button>
    </div>
    <img v-else :src="getNftImage(item.nft_type)" class="nft-image">
    
<div class="nft-info-container">
    <h6 class="hustler">{{ getNftDisplayName(item.nft_type, item.nft_object)}}</h6>
    <span class="nft-id" v-if="item.nft_object">#{{ extractNftId(item.nft_object) }}</span>
  </div>
    <!-- Найдите этот блок в шаблоне -->
<div class="item-actions">
  <button 
    v-if="item.seller !== currentAccountName" 
    class="buy-button" 
    @click.stop="handleBuyClick(item)" 
    :disabled="item.seller === currentAccountName"
  >
    {{ item.price_per_unit }} 
    <span v-if="item.currency === 'TON'">
      <img :src="tonlogo" alt="TON" class="currency-icon">
    </span>
    <span v-else>{{ item.currency }}</span>
  </button>
  <button 
    v-if="item.seller === currentAccountName" 
    class="cancel-sale-button" 
    @click.stop="handleBuyClick(item)"
  >
    Cancel sale
  </button>
</div>
  </div>
</div>
    
    <div v-if="filteredMarketItems.length === 0" class="empty-message">
      На рынке пока нет предложений 
    </div>
  </div>
</div>


<div v-if="htmlModal.show" class="fullscreen-view">
  <button class="back-button" @click="closeHtmlModal">
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
      <path d="M15 18L9 12L15 6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    </svg>
  </button>
  
  <div class="fullscreen-content">
<div class="html-container">
<div class="html-container-wrapper">
  <iframe 
    sandbox="allow-scripts allow-same-origin"
    :srcdoc="htmlModal.htmlContent"
    class="html-content-iframe"
  ></iframe>
  
  <!-- Иконка телеграмма в правом нижнем углу -->
  <img 
    v-if="htmlModal.telegramLink" 
    :src="telegram" 
    class="telegram-icon"
    @click="openTelegramLink(htmlModal.telegramLink)"
  >
  
  <!-- Кнопка корзины в левом нижнем углу -->
  <button 
    v-if="htmlModal.item && htmlModal.item.seller !== currentAccountName" 
    class="cart-action-button cart-action-button-modal"
    @click.stop="isInCart(htmlModal.item.id) ? removeFromCart(htmlModal.item.id, $event) : addToCart(htmlModal.item, $event)"
    :disabled="htmlModal.item.seller === currentAccountName"
    :title="isInCart(htmlModal.item.id) ? 'Remove from cart' : 'Add to cart'"
    :class="{ 'in-cart': isInCart(htmlModal.item.id) }"
  >
    <img 
      :src="isInCart(htmlModal.item.id) ? rubish_bucket_icon : bucket_icon" 
      :alt="isInCart(htmlModal.item.id) ? 'Remove from cart' : 'Add to cart'" 
      class="cart-action-icon"
    >
  </button>
</div>
</div>
    <div class="info-container">
  <div class="item-info">
    <!-- Добавляем заголовок с названием и номером NFT -->

    
    <div class="info-grid">
          <div v-if="htmlModal.item && htmlModal.item.nft_object">
      <h3 class="info-item-name">
  <span class="info-label-name">{{ getNftDisplayName(htmlModal.item.nft_type, htmlModal.item.nft_object) }}</span>
  <span class="info-value-id">#{{ extractNftId(htmlModal.item.nft_object) }}</span>
</h3>
    </div>
            <div class="info-item" v-if="htmlModal.model">
        <span class="info-label">Model:</span>
        <div class="info-value-container">
          <span class="info-value">{{ htmlModal.model }}</span>
          <span class="info-value-procent" v-if="htmlModal.modelPercentage">
            {{ htmlModal.modelPercentage }}
          </span>
        </div>
      </div>
      
      <div class="info-item" v-if="htmlModal.backdrop">
        <span class="info-label">Backdrop:</span>
        <div class="info-value-container">
          <span class="info-value">{{ htmlModal.backdrop }}</span>
          <span class="info-value-procent" v-if="htmlModal.backdropPercentage">
            {{ htmlModal.backdropPercentage }}
          </span>
        </div>
      </div>
      
      <div class="info-item" v-if="htmlModal.symbol">
        <span class="info-label">Symbol:</span>
        <div class="info-value-container">
          <span class="info-value">{{ htmlModal.symbol }}</span>
          <span class="info-value-procent" v-if="htmlModal.symbolPercentage">
            {{ htmlModal.symbolPercentage }}
          </span>
        </div>
      </div>
    </div>
  </div>
</div>
    
    <!-- В fullscreen-view модальном окне -->

<div class="action-buttons">
  <!-- Для unlisted NFT показываем только одну кнопку -->
  <template v-if="htmlModal.isUnlisted">
    <!-- Кнопка Send (желтая) -->
    <button 
      v-if="htmlModal.actionType === 'send'"
      class="send-button-fullscreen" 
      @click="handleTransferFromFullscreen(htmlModal.item.nft_object)"
    >
      Send
    </button>
    
    <!-- Кнопка Withdraw (красная) -->
    <button 
      v-else-if="htmlModal.actionType === 'withdraw'"
      class="withdraw-button-fullscreen" 
      @click="handleWithdrawFromFullscreen(htmlModal.item.nft_object)"
    >
      Withdraw
    </button>
    
    <!-- Кнопка Sell (зеленая) по умолчанию -->
    <button 
      v-else
      class="sell-button-fullscreen" 
      @click="initiateSellFromUnlisted(htmlModal.item.nft_object)"
    >
      Sell
    </button>
  </template>
  
  <!-- Для listed NFT оставляем существующие кнопки -->
  <template v-else>
    <button 
      v-if="htmlModal.item && htmlModal.item.seller === currentAccountName"
      class="cancel-sale-button-fullscreen" 
      @click="initiateCancelSale(htmlModal.item)"
    >
      Cancel sale
    </button>
    <button 
      v-else-if="htmlModal.item"
      class="buy-button-fullscreen" 
      @click="initiateBuy(htmlModal.item)"
    >
      {{ htmlModal.item.price_per_unit }} 
      <span v-if="htmlModal.item.currency === 'TON'">
        <img :src="tonlogoblack" alt="TON" class="currency-icon-black">
      </span>
      <span v-else>{{ htmlModal.item.currency }}</span>
    </button>
  </template>
</div>
  </div>
</div>
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
        <div v-if="itemDetailsModal.item.html_content" class="nft-html-content" v-html="itemDetailsModal.item.html_content"></div>
        <img v-else :src="getNftImage(itemDetailsModal.item.nft_type)" :alt="itemDetailsModal.item.nft_type" class="modal-nft-image">
            <div class="item-details-info">
            <h3>{{ getNftDisplayName(itemDetailsModal.item.nft_type) }}</h3>
            <div class="detail-row">
              <span>Price</span>
              <span>{{ itemDetailsModal.item.price_per_unit }} {{ itemDetailsModal.item.currency }}</span>
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
            Cancel Sale
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
          </div>
          
          <div class="modal-buttons">
            <button @click="transferModal.confirmStep = false" class="cancel-button">Назад</button>
            <button @click="executeTransfer" class="confirm-button">Подтвердить передачу</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно продажи NFT -->
    <!-- Модальное окно продажи NFT -->
<div v-if="sellModal.show" class="modal-overlay">
  <div class="modal-content">
    <h3>Выставление на рынок {{ getNftDisplayName(sellModal.nftType) }}</h3>
    
    <div v-if="!sellModal.confirmStep">
      <!-- Поле количества только для обычных NFT -->
      <div class="form-group-input" v-if="!sellModal.isHtmlNft">
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
        <label>Цена (TON):</label>
        <input 
          type="number" 
          v-model="sellModal.price" 
          min="0.1"
          step="0.1"
          placeholder="Введите цену (например, 2.5)"
          class="input"
          @input="updateCalculations"
        >
      </div>
      
      <div class="form-group">
        <div class="price-row total">
          <span>Сумма:</span>
          <span class="price-value">{{ formatTonValue(sellModal.totalPrice) }} TON</span>
        </div>
        <div class="price-row-commission" v-if="sellModal.isHtmlNft">
          <span>Комиссия системы (5%):</span>
          <span class="price-value-comm"> -{{ formatTonValue(sellModal.commission) }} TON</span>
        </div>
        <div class="price-row total">
          <span>Вы получите:</span>
          <span class="price-value">{{ formatTonValue(sellModal.finalAmount) }} TON</span>
        </div>
      </div>
      
      <div class="modal-buttons">
        <button @click="sellModal.show = false" class="cancel-button">Отмена</button>
        <button 
          @click="showSellConfirmation" 
          class="confirm-button"
          :disabled="!sellModal.price || (!sellModal.isHtmlNft && !sellModal.amount)"
        >
          Далее
        </button>
      </div>
    </div>
    
    <div v-else>
      <div class="confirmation-details-sale">
        <h4>Подтверждение продажи</h4>
      
        <div v-if="!sellModal.isHtmlNft" class="detail-row-sale">
          <span>Количество: </span>
          <span class="got-a-drop">{{ sellModal.amount }}</span>
        </div>
        <div class="detail-row-sale">
          <span>Цена: </span>
          <span class="got-a-drop">{{ formatTonValue(sellModal.price) }} TON</span>
        </div>
        
        <div v-if="sellModal.isHtmlNft">
          <span>Комиссия системы: </span>
          <span class="got-a-drop-comm">-{{ formatTonValue(sellModal.commission) }} TON</span>
        </div>
        <div class="detail-row-sale total">
          <span>К получению:</span>
          <span>{{ formatTonValue(sellModal.finalAmount) }} TON</span>
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


          <div class="detail-item total">
            <span class="detail-label">К оплате</span>
            <span class="detail-label">{{ buyModal.buyAmount * buyModal.pricePerUnit }} {{ buyModal.currency }}</span>
          </div>
        </div>
        
        <div class="modal-buttons">
          <button @click="buyModal.show = false" class="cancel-button">Отмена</button>
          <button 
            @click="executeBuy" 
            class="confirm-button"
            :disabled="!buyModal.buyAmount || buyModal.buyAmount > buyModal.amount"
          >
            {{ buyModal.buyAmount * buyModal.pricePerUnit }} {{ buyModal.currency }}
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
import tonlogoblack from '@/assets/Ton.png';
import cennik from '@/assets/cennik.png';
import withdraw_icon from '@/assets/withdraw.png';
import tonlogogray from '@/assets/ton-logo-gray.png';
import tonlogoyellow  from '@/assets/ton-logo-yellow.png';
import tonlogofloor from '@/assets/ton-logo-floor.png'
// Добавьте эти импорты для профиля
import amahaslaImage from '@/assets/amahasla.png';
import frogIcon from '@/assets/frog1.png';





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
      return marketItems.value.filter(item => item.seller === currentAccountName.value);
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


const generateNftHtml = (nftData) => {
  try {
    // Извлекаем ID из URL (формат: https://t.me/nft/bdaycandle-224527)
    const urlMatch = nftData.url?.match(/-(\d+)(?:\?|$)/);
    const nftId = urlMatch ? urlMatch[1] : 'unknown';
    
    // Извлекаем название NFT из URL
    const nftNameMatch = nftData.url?.match(/\/nft\/([^-]+)/);
    const nftName = nftNameMatch ? nftNameMatch[1] : 'unknown';
    
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
      border-radius: 30px 30px 3px 3px;
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
      border-radius: 30px 30px 3px 3px;
    }
    .nft-image {
      width: 100%;
      height: 100%;
      object-fit: contain;
      border-radius: 30px 30px 3px 3px;
    }
  </style>
</head>
<body>
  <div id="main-container">
    <div id="animation-container"></div>
    <div id="image-container"></div>
  </div>
  <script>
    // Функция для загрузки анимации
    function loadAnimationWhenVisible() {
      // 1. Инициализация анимации
      const animation = lottie.loadAnimation({
        container: document.getElementById("animation-container"),
        renderer: "svg",
        loop: false,
        autoplay: true,
        path: "https://nft.fragment.com/gift/${nftName}-${nftId}.lottie.json"
      });

      // 2. Создаем изображение с скругленными углами
      const img = new Image();
      img.src = "https://nft.fragment.com/gift/${nftName}-${nftId}.webp";
      img.className = 'nft-image';
      
      // 3. Добавляем изображение в контейнер
      document.getElementById('image-container').appendChild(img);

      // 4. Обработчик завершения анимации
      animation.addEventListener('complete', function() {
        if (img.complete && img.naturalWidth !== 0) {
          document.getElementById('animation-container').style.display = 'none';
          document.getElementById('image-container').style.display = 'block';
        } else {
          img.onload = function() {
            document.getElementById('animation-container').style.display = 'none';
            document.getElementById('image-container').style.display = 'block';
          };
          img.onerror = function() {
            console.error('Failed to load image, keeping animation');
          };
        }
      });
    }

    // Создаем наблюдатель за видимостью
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          // Элемент стал видимым - загружаем анимацию
          loadAnimationWhenVisible();
          // Отключаем наблюдатель после первого срабатывания
          observer.disconnect();
          
          // Отправляем сообщение родительскому окну о том, что анимация загружена
          if (window.parent) {
            window.parent.postMessage({
              type: 'nftVisible',
              nftId: '${nftName}-${nftId}'
            }, '*');
          }
        }
      });
    }, {
      threshold: 0.1
    });

    // Начинаем наблюдение за контейнером
    observer.observe(document.getElementById('main-container'));
  <\/script>
</body>
</html>
    `;
  } catch (error) {
    console.error('Error generating NFT HTML:', error);
    return `
      <div style="width: 100%; height: 100%; background: #f0f0f0; display: flex; align-items: center; justify-content: center;">
        <div style="text-align: center;">
          <h3>Error loading NFT</h3>
          <p>Please try again later</p>
        </div>
      </div>
    `;
  }
};

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
    const router = useRouter();
    const tonBalance = ref(0);
    const isDraggingModal = ref(false);
    const dragStartY = ref(0);
    const dragCurrentY = ref(0);
    const categoriesContainer = ref(null);
    const nftModels = ref([]);
    const nftImageUrls = ref({});
    const expandedModelNfts = ref({});
    const nftModelsCache = ref({});
   
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
    for (const item of cartItems.value) {
      await executeBuy(item);
    }
    await clearCart(); // Это очистит и базу данных тоже
    showNotification('All items purchased successfully!', 'success');
  } catch (error) {
    showNotification('Error purchasing items from cart', 'error');
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


const getCurrentDataSource = computed(() => {
  if (activeTab.value === 'market') {
    return marketItems.value;
  } else if (activeTab.value === 'my-nfts') {
    if (myNftsViewMode.value === 'listed') {
      return myMarketItems.value;
    } else {
      // Для unlisted NFT преобразуем в формат похожий на market items
      return myUnlistedNfts.value.map(nftData => ({
        id: `unlisted-${extractNftIdFromUnlisted(nftData)}`,
        nft_type: `html_nft_${extractNftNameFromUrl(nftData.url)}`,
        nft_object: nftData,
        html_content: generateNftHtml(nftData),
        seller: currentAccountName.value,
        // Добавляем другие необходимые поля
        is_unlisted: true
      }));
    }
  }
  return [];
});
// Обновите все availableOptions функции чтобы использовать текущий источник данных
// availableNftOptions должен показывать ВСЕ доступные NFT, независимо от других фильтров
const availableNftOptions = computed(() => {
  const availableNfts = new Set();
  const items = getCurrentDataSource.value;
  
  // Просто собираем все уникальные NFT без учета других фильтров
  items.forEach(item => {
    const itemName = getNftDisplayName(item.nft_type, item.nft_object);
    const normalizedItemName = normalizeNftName(itemName);
    availableNfts.add(normalizedItemName);
  });
  
  return Array.from(availableNfts);
});

// availableModelOptions должен показывать модели только для выбранных NFT
// Функция для получения доступных моделей (БЕЗ фильтрации по выбранным моделям)
// Функция для получения доступных моделей (С фильтрацией но без скрытия опций)
const availableModelOptions = computed(() => {
  const availableModels = new Set();
  const items = getCurrentDataSource.value;

  // Фильтруем items по всем фильтрам кроме model
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
  
  // Собираем доступные модели
  preFilteredItems.forEach(item => {
    const model = extractModelFromNft(item);
    if (model) {
      const fullModelName = model.toLowerCase().trim();
      if (fullModelName && fullModelName !== 'не указано') {
        availableModels.add(fullModelName);
      }
    }
  });
  
  return Array.from(availableModels);
});


// Обновим availableSymbolOptions для работы с процентами
// Функция для получения доступных символов с процентами (С фильтрацией но без скрытия опций)
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
  
  preFilteredItems.forEach(item => {
    const symbolData = extractSymbolWithPercentage(item);
    if (symbolData.name) {
      const normalizedSymbol = normalizeSymbolName(symbolData.name);
      const existing = availableSymbols[normalizedSymbol];
      if (!existing || symbolData.percentage < existing.percentage) {
        availableSymbols[normalizedSymbol] = {
          name: symbolData.name,
          percentage: symbolData.percentage,
          rarityText: symbolData.percentage > 0 ? `${symbolData.percentage}%` : 'N/A',
          count: 1
        };
      } else if (existing) {
        existing.count = (existing.count || 1) + 1;
      }
    }
  });
  
  return Object.values(availableSymbols);
});

// Функция для получения отфильтрованных символов с редкостями
const getFilteredSymbols = () => {
  const query = searchQuery.value ? searchQuery.value.toLowerCase() : '';
  
  console.log('🔍 Поиск символов, запрос:', query);
  console.log('📊 Доступные символы:', availableSymbolOptions.value);
  console.log('📦 Опции символов:', symbolOptions.value.length);
  
  // Если нет доступных символов, возвращаем пустой массив
  if (!availableSymbolOptions.value || availableSymbolOptions.value.length === 0) {
    console.log('❌ Нет доступных символов');
    return [];
  }
  
  const filtered = symbolOptions.value
    .filter(symbol => {
      const normalizedSymbolName = normalizeSymbolName(symbol.name);
      const isAvailable = availableSymbolOptions.value.some(
        opt => normalizeSymbolName(opt.name) === normalizedSymbolName
      );
      
      const matchesSearch = symbol.name.toLowerCase().includes(query) ||
                           symbol.value.toLowerCase().includes(query);
      
      console.log(`🔍 Символ "${symbol.name}": доступен=${isAvailable}, соответствует поиску=${matchesSearch}`);
      
      return isAvailable && matchesSearch;
    })
    .map(symbol => {
      // Находим данные о редкости для этого символа
      const symbolData = availableSymbolOptions.value.find(
        opt => normalizeSymbolName(opt.name) === normalizeSymbolName(symbol.name)
      );
      
      const result = {
        ...symbol,
        floorPrice: getFloorPrice('symbol', symbol.value),
        percentage: symbolData?.percentage || 0,
        rarityText: symbolData?.rarityText || 'N/A'
      };
      
      console.log(`✅ Символ "${symbol.name}": процент=${result.percentage}, редкость=${result.rarityText}`);
      
      return result;
    })
    .sort((a, b) => a.percentage - b.percentage); // Сортируем по редкости

  console.log(`📊 Отфильтровано символов: ${filtered.length}`);
  return filtered;
};

// Функция для получения отфильтрованных backdrop с редкостями
const getFilteredBackdrops = () => {
  const query = backdropSearchQuery.value ? backdropSearchQuery.value.toLowerCase() : '';
  
  console.group('🎨 [getFilteredBackdrops] НАЧАЛО ФИЛЬТРАЦИИ');
  
  const filtered = backdropColors.value
    .filter(color => {
      const cleanColorId = color.id.toLowerCase().trim();
      const isAvailable = availableBackdropOptions.value.some(
        opt => opt.id === cleanColorId
      );
      const matchesSearch = color.name.toLowerCase().includes(query) ||
                           color.id.toLowerCase().includes(query);
      
      return isAvailable && matchesSearch;
    })
    .map(color => {
      // Находим данные о редкости для этого backdrop
      const backdropData = availableBackdropOptions.value.find(
        opt => opt.id === color.id.toLowerCase().trim()
      );
      
      return {
        id: color.id,
        name: color.name,
        svgContent: generateBackdropSVG(color.id),
        floorPrice: getFloorPrice('backdrop', color.id),
        percentage: backdropData?.percentage || 0,
        rarityText: backdropData?.rarityText || 'N/A'
      };
    })
    .sort((a, b) => a.percentage - b.percentage); // Сортируем по редкости
  
  console.log('✅ Отфильтрованные backdrop с редкостями:', filtered);
  console.groupEnd();
  
  return filtered;
};



// Функция для получения доступных backdrop с процентами (БЕЗ фильтрации по выбранным backdrop)
const availableBackdropOptions = computed(() => {
  const availableBackdrops = {};
  const items = getCurrentDataSource.value;
  
  // ВОССТАНАВЛИВАЕМ фильтрацию, но для определения ДОСТУПНЫХ опций
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
    
    // НЕ фильтруем по backdrop - чтобы все backdrop оставались в доступных опциях
    return true;
  });
  
  preFilteredItems.forEach(item => {
    const backdropData = extractBackdropWithPercentage(item);
    if (backdropData.name) {
      const cleanBackdrop = backdropData.name.toLowerCase().trim();
      const existing = availableBackdrops[cleanBackdrop];
      if (!existing || backdropData.percentage < existing.percentage) {
        availableBackdrops[cleanBackdrop] = {
          id: cleanBackdrop,
          name: backdropData.name,
          percentage: backdropData.percentage,
          rarityText: backdropData.percentage > 0 ? `${backdropData.percentage}%` : 'N/A',
          // Добавляем счетчик для отображения сколько items соответствуют
          count: 1
        };
      } else if (existing) {
        // Увеличиваем счетчик
        existing.count = (existing.count || 1) + 1;
      }
    }
  });
  
  return Object.values(availableBackdrops);
});




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
    console.log('🎨 Извлечение backdrop для item:', item.id);
    
    let backdrop = null;
    
    // 1. Проверяем разные источники по приоритету
    const sources = [
      { name: 'nft_metadata', value: item.nft_metadata?.backdrop },
      { name: 'backdrop field', value: item.backdrop },
      { name: 'nft_object', value: getBackdropFromNftObject(item.nft_object) },
      { name: 'html_content', value: getBackdropFromHtml(item.html_content) }
    ];
    
    for (const source of sources) {
      if (source.value) {
        backdrop = source.value;
        console.log(`📋 Backdrop найден в ${source.name}:`, backdrop);
        break;
      }
    }
    
    if (backdrop) {
      // ИСПРАВЛЕНО: убираем ТОЛЬКО проценты, сохраняем ВСЕ слова
      const cleanBackdrop = backdrop
        .replace(/\d+\.?\d*%/, '') // удаляем проценты
        .replace(/^\s+|\s+$/g, '') // обрезаем пробелы
        .replace(/\s+/g, ' '); // заменяем множественные пробелы на один
      
      console.log('✅ Очищенный backdrop:', cleanBackdrop);
      return cleanBackdrop;
    }
    
    console.log('❌ Backdrop не найден ни в одном источнике');
    return null;
    
  } catch (error) {
    console.error('❌ Ошибка извлечения backdrop:', error);
    return null;
  }
};

const applyIdFilter = () => {
  if (idFilterValue.value) {
    const id = parseInt(idFilterValue.value);
    if (!isNaN(id)) {
      selectedIdFilter.value = id;
      activeFilterCategory.value = null; // Закрываем меню
      idFilterValue.value = ''; // Очищаем поле ввода
      
      // Показываем уведомление
      showNotification(`Filter applied: ID ${id}`, 'success');
      
      // Логируем для отладки
      console.log('Applied ID filter:', id);
      console.log('Filtered items count:', filteredMarketItems.value.length);
    } else {
      showNotification('Please enter a valid number', 'error');
    }
  }
};

// Обновите функцию clearIdFilter
const clearIdFilter = () => {
  selectedIdFilter.value = null;
  idFilterValue.value = '';
  // Также очищаем фильтр price в selectedFilters для consistency
  selectedFilters.value.price = [];
  showNotification('ID filter cleared', 'success');
  activeFilterCategory.value = null;
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
    console.log(`   ${backdrop ? '✅' : '❌'} Backdrop из nft_object: "${backdrop}"`);
    return backdrop;
  } catch (e) {
    console.log('   ❌ Ошибка парсинга nft_object:', e);
    return null;
  }
};

// Отладка для getBackdropFromHtml
const getBackdropFromHtml = (htmlContent) => {
  if (!htmlContent) {
    console.log('   ❌ htmlContent пустой');
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
  
  console.log('   ❌ Backdrop не найден в HTML');
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
      scrollToButton(button);
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


// Функция для загрузки символов из базы данных
const symbolOptions = ref([]);
const symbolsLoading = ref(false);

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


const extractNftNameFromUrl = (url) => {
  try {
    const match = url.match(/\/nft\/([^-]+)/);
    if (match && match[1]) {
      // Возвращаем имя в нижнем регистре для использования в маппинге
      return match[1].toLowerCase();
    }
    return null;
  } catch (error) {
    console.error('Error extracting NFT name from URL:', error);
    return null;
  }
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
// Функция для получения выбранных NFT опций (вверху списка)
const getSelectedNftOptions = () => {
  const allOptions = getFilteredNftOptions();
  const selected = allOptions.filter(option => 
    isOptionSelected('nft', option.originalType)
  ).map(option => ({
    ...option,
    onRemove: () => removeNftFromFilter(option.originalType)
  }));
  
  const unselected = allOptions.filter(option => 
    !isOptionSelected('nft', option.originalType)
  );
  
  return [...selected, ...unselected];
};

// Функция для получения невыбранных NFT опций (после выбранных)
const getUnselectedNftOptions = () => {
  const allOptions = getFilteredNftOptions();
  
  const unselectedOptions = allOptions.filter(option => 
    !isOptionSelected('nft', option.originalType)
  );
  
  // Сортируем невыбранные опции по имени
  return unselectedOptions.sort((a, b) => a.name.localeCompare(b.name));
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
      return [];
    }
    
    if (nftModelsCache.value[nftName]) {
      return nftModelsCache.value[nftName];
    }

    let cleanNftName = nftName.toLowerCase();
    if (cleanNftName.startsWith('html_nft_')) {
      cleanNftName = cleanNftName.replace('html_nft_', '');
    }
    if (cleanNftName.startsWith('htmlnft')) {
      cleanNftName = cleanNftName.replace('htmlnft', '');
    }

    const dbColumnName = groupDisplayNames[cleanNftName] || 
                        cleanNftName.replace(/([a-z])([A-Z])/g, '$1 $2')
                                   .replace(/^./, str => str.toUpperCase())
                                   .trim();

    if (!dbColumnName) {
      return [];
    }

    const quotedColumnName = `"${dbColumnName}"`;
    
    const { data, error } = await supabase
      .from('nft')
      .select(quotedColumnName)
      .not(quotedColumnName, 'is', null)
      .limit(1);

    if (error) {
      return [];
    }

    if (!data || data.length === 0) {
      return [];
    }

    const modelsArray = data[0][dbColumnName];
    
    if (!Array.isArray(modelsArray)) {
      return [];
    }

    nftModelsCache.value[nftName] = modelsArray;
    return modelsArray;

  } catch (error) {
    return [];
  }
};



// Улучшенная функция нормализации имен NFT
const normalizeNftName = (name) => {
  if (!name) return '';
  
  let cleanName = name.toLowerCase().replace(/[^a-z0-9]/g, '');
  
  // Убираем префиксы HTML NFT
  if (cleanName.startsWith('htmlnft')) {
    cleanName = cleanName.replace('htmlnft', '');
  }
  if (cleanName.startsWith('html_nft_')) {
    cleanName = cleanName.replace('html_nft_', '');
  }
  
  return cleanName;
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


// Обработчик ошибок загрузки изображений символов
const handleSymbolImageError = (event) => {
  event.target.src = default_nft_image;
  console.warn('Ошибка загрузки изображения символа');
};
const extractSymbolFromNft = (item) => {
  try {
    console.log('🔍 Извлечение символа для item:', item.id);
    
    let rawSymbol = null;
    
    // 1. Пытаемся получить symbol из metadata
    if (item.nft_metadata?.symbol) {
      rawSymbol = item.nft_metadata.symbol;
      console.log('📋 Символ из nft_metadata:', rawSymbol);
    }
    
    // 2. Пытаемся получить из прямого поля symbol
    else if (item.symbol) {
      rawSymbol = item.symbol;
      console.log('📋 Символ из поля symbol:', rawSymbol);
    }
    
    // 3. Парсим nft_object если есть
    else if (item.nft_object) {
      try {
        const nftObj = typeof item.nft_object === 'string' 
          ? JSON.parse(item.nft_object) 
          : item.nft_object;
        
        if (nftObj.symbol) {
          rawSymbol = nftObj.symbol;
          console.log('📋 Символ из nft_object:', rawSymbol);
        }
      } catch (e) {
        console.log('❌ Ошибка парсинга nft_object:', e);
      }
    }
    
    // 4. Парсим HTML контент
    else if (item.html_content) {
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
    
    console.log('✅ Очищенный символ:', cleanedSymbol);
    return cleanedSymbol;
    
  } catch (error) {
    console.error('❌ Ошибка извлечения символа:', error);
    return null;
  }
};

const myNftsViewMode = ref('listed'); // 'listed' или 'unlisted'
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
    
    myUnlistedNfts.value = data?.nft_links || [];
    
  } catch (error) {
    console.error('Ошибка загрузки unlisted NFT:', error);
    myUnlistedNfts.value = [];
  }
};
    
    
    

    // Функция для инициации продажи unlisted NFT
    // Инициализация продажи для unlisted NFT
const initiateSellFromUnlisted = (nftData) => {
  const nftName = extractNftNameFromUrl(nftData.url);
  const nftId = extractNftIdFromUnlisted(nftData).replace('#', '');
  const nftType = `html_nft_${nftId}`;
  
  // Закрываем полноэкранное меню
  htmlModal.value.show = false;
  
  // Открываем модальное окно продажи
  sellModal.value = {
    show: true,
    nftType,
    amount: 1,
    price: 1,
    confirmStep: false,
    isHtmlNft: true,
    totalPrice: 1,
    commission: 0.05,
    finalAmount: 0.95,
    nftData: nftData
  };
  updateCalculations();
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
    
    // Проверяем разные источники по приоритету
    if (item.nft_metadata?.model) {
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

// Функция для обновления всех floor prices
const updateAllFloorPrices = () => {
  floorPriceCache.value = {}; // Очищаем кэш
  console.log('Floor prices cache cleared');
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



const generateBackdropSVG = (colorId) => {
  // Создаем корректный ID для SVG (убираем пробелы)
  const svgId = colorId.replace(/\s+/g, '_');
  

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



const getFilteredNftOptions = () => {
  const query = searchQuery.value ? searchQuery.value.toLowerCase() : '';
  
  // Для вкладки "My Gifts" -> "Unlisted" используем NFT из инвентаря пользователя
  if (activeTab.value === 'my-nfts' && myNftsViewMode.value === 'unlisted') {
    console.group('🎁 GIFTS UNLISTED - Генерация ссылок для опций NFT');
    console.log('📋 Режим: My Gifts -> Unlisted');
    
    const nftTypesWithNames = new Map();
    
    // Собираем уникальные NFT типы из unlisted NFT пользователя
    myUnlistedNfts.value.forEach(item => {
      const nftName = extractNftNameFromUrl(item.url);
      const displayName = getNftDisplayNameFromUrl(item.url);
      if (nftName && displayName) {
        nftTypesWithNames.set(nftName, displayName);
        console.log(`🔍 Найден NFT: ${nftName} -> "${displayName}"`);
      }
    });
    
    const options = Array.from(nftTypesWithNames.entries()).map(([nftType, displayName]) => {
      const imageUrl = nftImageUrls.value[nftType] || generateMarketStyleImageUrl(nftType, displayName);
      const floorPrice = getFloorPrice('nft', nftType);
      
      return {
        originalType: nftType,
        name: displayName,
        imageUrl: imageUrl,
        floorPrice: floorPrice
      };
    });

    console.log(`📊 Всего опций: ${options.length}`);
    
    // Загружаем изображения для unlisted NFT так же, как для маркета
    loadNftImages(Array.from(nftTypesWithNames.entries()));
    
    // СОРТИРОВКА: сначала выбранные, потом невыбранные
    const selectedOptions = options.filter(option => 
      isOptionSelected('nft', option.originalType)
    );
    const unselectedOptions = options.filter(option => 
      !isOptionSelected('nft', option.originalType)
    );
    
    const sortedOptions = [...selectedOptions, ...unselectedOptions];
    
    if (!query) {
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
  }
  
  // Для остальных случаев (рынок, listed NFT) используем старую логику
  console.group('🏪 MARKET - Генерация ссылок для опций NFT');
  console.log('📋 Режим: Market или My Gifts -> Listed');
  
  const currentDataSource = getCurrentDataSource.value; // ← ИСПОЛЬЗУЕМ ТЕКУЩИЙ ИСТОЧНИК
  
  console.group(`🏪 ${activeTab.value.toUpperCase()} - Генерация ссылок для опций NFT`);
  console.log('📋 Режим:', activeTab.value, myNftsViewMode.value);
  console.log('📊 Источник данных:', currentDataSource.length, 'items');
  
  const nftTypesWithNames = new Map();
  
  // Используем текущий источник данных
  currentDataSource.forEach(item => {
    const displayName = getNftDisplayName(item.nft_type, item.nft_object);
    const normalizedName = normalizeNftName(displayName);
    
    if (availableNftOptions.value.includes(normalizedName)) {
      nftTypesWithNames.set(item.nft_type, displayName);
    }
  });
  marketItems.value.forEach(item => {
    const displayName = getNftDisplayName(item.nft_type, item.nft_object);
    const normalizedName = normalizeNftName(displayName);
    
    // ИСПРАВЛЕННАЯ ПРОВЕРКА:
    if (availableNftOptions.value.includes(normalizedName)) {
      nftTypesWithNames.set(item.nft_type, displayName);
    }
  });
  
  const options = Array.from(nftTypesWithNames.entries()).map(([nftType, displayName]) => {
    const imageUrl = nftImageUrls.value[nftType] || default_nft_image;
    const floorPrice = getFloorPrice('nft', nftType);
    
    return {
      originalType: nftType,
      name: displayName,
      imageUrl: imageUrl,
      floorPrice: floorPrice
    };
  });
  
  console.log(`📊 Всего опций: ${options.length}`);
  
  // Загружаем изображения только для market items
  loadNftImages(Array.from(nftTypesWithNames.entries()));
  
  // СОРТИРОВКА: сначала выбранные, потом невыбранные
  const selectedOptions = options.filter(option => 
    isOptionSelected('nft', option.originalType)
  );
  const unselectedOptions = options.filter(option => 
    !isOptionSelected('nft', option.originalType)
  );
  
  const sortedOptions = [...selectedOptions, ...unselectedOptions];
  
  if (!query) {
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
  amount: '',
  price: '',
  confirmStep: false,
  isHtmlNft: false,
  totalPrice: 0,
  commission: 0,
  finalAmount: 0,
  nftData: null
});


// Показать подтверждение продажи
const showSellConfirmation = () => {
  if (!sellModal.value.price || (!sellModal.value.isHtmlNft && !sellModal.value.amount)) {
    showNotification('Пожалуйста, укажите корректные данные', 'error');
    return;
  }
  
  sellModal.value.confirmStep = true;
};

// Выполнить продажу
const executeSell = async () => {
  try {
    const { nftType, amount, price, isHtmlNft, totalPrice, commission, finalAmount, nftData } = sellModal.value;
    
    if (isHtmlNft) {
      // Логика продажи HTML NFT
      if (!nftData || !nftData.url) {
        throw new Error('Данные NFT не найдены');
      }

      const { data: userData, error: fetchError } = await supabase
        .from('users')
        .select('nft_links')
        .eq('name', currentAccountName.value)
        .single();

      if (fetchError) throw fetchError;

      const currentLinks = userData.nft_links || [];
      const nftLinkIndex = currentLinks.findIndex(link => {
        const linkUrl = typeof link === 'object' ? link.url : link;
        return linkUrl === nftData.url;
      });

      if (nftLinkIndex === -1) {
        throw new Error('Ссылка на NFT не найдена в вашем профиле');
      }

      const nftLink = currentLinks[nftLinkIndex];
      const nftObject = typeof nftLink === 'object' ? nftLink : { url: nftLink };
      const nftId = extractNftIdFromUnlisted(nftData).replace('#', '');
      
      if (!nftId || nftId === 'Unknown') {
        throw new Error('Не удалось извлечь ID NFT из URL');
      }

      const htmlContent = generateNftHtml(nftData);

      // ОБНОВЛЕННЫЙ БЛОК ДЛЯ HTML NFT
      const { data: marketItem, error: marketError } = await supabase
        .from('market')
        .insert([{
          nft_type: `html_nft_${extractNftNameFromUrl(nftData.url)}`, // ← ДОБАВЛЕН ПРЕФИКС
          seller: currentAccountName.value,
          amount: 1,
          price_per_unit: price,
          total_price: totalPrice,
          is_html_nft: true,
          html_content: htmlContent,
          nft_object: nftObject,
          currency: 'TON'
        }]);

      if (marketError) throw marketError;

      const updatedLinks = [...currentLinks];
      updatedLinks.splice(nftLinkIndex, 1);

      const { error: updateError } = await supabase
        .from('users')
        .update({ 
          nft_links: updatedLinks
        })
        .eq('name', currentAccountName.value);

      if (updateError) throw updateError;

      // Обновляем локальные данные
      myUnlistedNfts.value = myUnlistedNfts.value.filter(item => 
        item.url !== nftData.url
      );
      
      showNotification('NFT успешно выставлено на продажу!', 'success');
      sellModal.value.show = false;
      await loadMarketItems();
      return;
    }

    // Логика продажи обычных NFT
    const numAmount = Number(amount) || 0;
    const numPrice = Number(price) || 0;

    if (numAmount <= 0 || numPrice <= 0) {
      throw new Error('Некорректное количество или цена');
    }

    const { data: userData, error: fetchError } = await supabase
      .from('users')
      .select('*')
      .eq('name', currentAccountName.value)
      .single();
    
    if (fetchError) throw fetchError;
    
    if (!userData || userData[nftType] < numAmount) {
      throw new Error('Недостаточно NFT для продажи');
    }

    // ОБНОВЛЕННЫЙ БЛОК ДЛЯ ОБЫЧНЫХ NFT
    const { data: marketItem, error: marketError } = await supabase
      .from('market')
      .insert([{
        nft_type: `html_nft_${nftType}`, // ← ДОБАВЛЕН ПРЕФИКС
        seller: currentAccountName.value,
        amount: numAmount,
        price_per_unit: numPrice,
        total_price: numAmount * numPrice,
        is_html_nft: false,
        currency: 'TON'
      }])
      .select()
      .single();

    if (marketError) throw marketError;

    const updates = {
      [nftType]: userData[nftType] - numAmount
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
    
    await loadMarketItems();
    
    showNotification('NFT успешно выставлено на продажу!', 'success');
    sellModal.value.show = false;
    
  } catch (error) {
    console.error('Ошибка продажи:', error);
    showNotification(`Ошибка: ${error.message}`, 'error');
  }
};

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
  if (sellModal.value.isHtmlNft) {
    const price = parseFloat(sellModal.value.price) || 0;
    sellModal.value.totalPrice = price;
    sellModal.value.commission = parseFloat((price * 0.05).toFixed(1));
    sellModal.value.finalAmount = parseFloat((price - sellModal.value.commission).toFixed(1));
  } else {
    const price = parseFloat(sellModal.value.price) || 0;
    const amount = parseInt(sellModal.value.amount) || 0;
    sellModal.value.totalPrice = price * amount;
    sellModal.value.commission = 0;
    sellModal.value.finalAmount = sellModal.value.totalPrice;
  }
};

// Форматирование значения TON
const formatTonValue = (value) => {
  if (value === undefined || value === null || isNaN(value)) {
    return '0.0';
  }
  return parseFloat(value.toFixed(1));
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

const getSortedNftOptions = () => {
  const allOptions = getFilteredNftOptions();
  
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

const getModelImageUrl = (nftType, modelName) => {
  let cleanNftType = nftType.toLowerCase();
  if (cleanNftType.startsWith('html_nft_')) {
    cleanNftType = cleanNftType.replace('html_nft_', '');
  }
  if (cleanNftType.startsWith('htmlnft')) {
    cleanNftType = cleanNftType.replace('htmlnft', '');
  }
  
  const folderName = groupDisplayNames[cleanNftType] || cleanNftType;
  const nftPath = folderName.toLowerCase().replace(/\s+/g, '%20');
  
  // Заменяем только "?" на "%3F", остальное как было
  const modelPath = modelName.replace(/\s+/g, '%20').replace(/\?/g, '%3F');
  
  return `https://gifts.coffin.meme/${nftPath}/${modelPath}.png`;
};
const handleImageError = (e) => {
  console.error('❌ Ошибка загрузки изображения:', e.target.src);
  e.target.src = default_nft_image;
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

    const sortMenu = ref({
      show: false,
      options: [
        { id: 'latest', name: 'Latest' },
        { id: 'price_asc', name: 'Price: Low to High' },
        { id: 'price_desc', name: 'Price: High to Low' },
        { id: 'id_asc', name: 'Gift id: Ascending' },
        { id: 'id_desc', name: 'Gift id: Descending' },
        { id: 'model_asc', name: 'Model Rarity: Ascending' },
        { id: 'model_desc', name: 'Model Rarity: Descending' }
      ],
      selected: 'latest'
    });

    const priceRangeMenu = ref({
      show: false,
      minPrice: '',
      maxPrice: ''
    });
    
    const toggleSortMenu = () => {
      sortMenu.value.show = !sortMenu.value.show;
      priceRangeMenu.value.show = false;
    };
    
    const togglePriceRangeMenu = () => {
      priceRangeMenu.value.show = !priceRangeMenu.value.show;
      sortMenu.value.show = false;
    };

    const applySort = (sortOption) => {
      sortMenu.value.selected = sortOption;
      sortMenu.value.show = false;
    };

    const applyPriceRange = () => {
      priceRangeMenu.value.show = false;
    };
    
    const resetPriceRange = () => {
      priceRangeMenu.value.minPrice = '';
      priceRangeMenu.value.maxPrice = '';
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







const getRandomModelForNft = async (nftName) => {
  try {
    // Преобразуем имя NFT в формат имени колонки в БД
    const columnMapping = {
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
    
    // Получаем правильное название колонки из маппинга
    const dbColumnName = columnMapping[nftName.toLowerCase()] || nftName;
    console.log(`🔍 Поиск моделей для NFT: "${nftName}" -> колонка БД: "${dbColumnName}"`);
    
    if (!dbColumnName) {
      console.error('Не удалось определить название колонки для БД');
      return null;
    }

    // Правильное экранирование имени столбца с пробелами
    const quotedColumnName = `"${dbColumnName}"`;
    
    // Выполняем запрос к Supabase
    const { data, error } = await supabase
      .from('nft')
      .select(quotedColumnName)
      .not(quotedColumnName, 'is', null)
      .limit(50);

    if (error) {
      console.error(`Ошибка Supabase для ${nftName}:`, error);
      return null;
    }

    if (!data || data.length === 0) {
      console.log(`Нет данных для ${nftName} в колонке ${dbColumnName}`);
      return null;
    }

    // Извлекаем массив моделей
    const allModels = [];
    data.forEach(item => {
      const modelsArray = item[dbColumnName];
      if (Array.isArray(modelsArray)) {
        modelsArray.forEach(model => {
          if (model && typeof model === 'string') {
            // Извлекаем только название модели (до символа "—")
            const modelName = model.split(' — ')[0].trim();
            if (modelName) {
              allModels.push(modelName);
            }
          }
        });
      }
    });

    if (allModels.length === 0) {
      console.log(`Не найдено моделей для ${nftName}`);
      return null;
    }

    // Выбираем случайную модель
    const randomIndex = Math.floor(Math.random() * allModels.length);
    const randomModel = allModels[randomIndex];
    
    console.log(`🎲 Случайная модель для ${nftName}: ${randomModel}`);
    console.log(`📊 Всего доступно моделей: ${allModels.length}`);
    
    return randomModel.replace(/\s+/g, '%20');
    
  } catch (err) {
    console.error(`Ошибка для ${nftName}:`, err);
    return null;
  }
};
const openHtmlModalForUnlisted = (nftData) => {
  try {
    // Извлекаем данные из nftData
    const model = nftData.model || 'Не указано';
    const symbol = nftData.symbol || 'Не указано';
    const backdrop = nftData.backdrop || 'Не указано';
    
    // Разделяем значения и проценты
    const extractValueAndPercentage = (value) => {
      if (!value) return { name: 'Не указано', percentage: '' };
      
      const parts = value.split(' ');
      if (parts.length > 1 && parts[parts.length - 1].includes('%')) {
        const percentage = parts.pop();
        return { name: parts.join(' '), percentage };
      }
      return { name: value, percentage: '' };
    };

    const modelData = extractValueAndPercentage(model);
    const symbolData = extractValueAndPercentage(symbol);
    const backdropData = extractValueAndPercentage(backdrop);

    htmlModal.value = {
      show: true,
      htmlContent: generateNftHtml(nftData),
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
      htmlContent: generateNftHtml(nftData),
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

// Также обновите функцию extractNftId для корректной работы с unlisted NFT
const extractNftId = (nftObject) => {
  try {
    if (!nftObject) return 'Unknown';
    
    // Для unlisted объектов с url
    if (nftObject.url) {
      const match = nftObject.url.match(/-(\d+)(?:\?|$)/);
      return match ? match[1] : 'Unknown';
    }
    
    // Для обычных nft_object (строка или объект)
    const obj = typeof nftObject === 'string' ? JSON.parse(nftObject) : nftObject;
    
    if (obj.url) {
      const match = obj.url.match(/-(\d+)(?:\?|$)/);
      return match ? match[1] : 'Unknown';
    }
    
    if (obj.id) {
      return obj.id;
    }
    
    return 'Unknown';
  } catch (error) {
    console.error('Error extracting NFT ID:', error);
    return 'Error';
  }
};


const extractIdFromNftType = (nftType) => {
  const match = nftType.match(/html_nft_.*-(\d+)/);
  return match ? parseInt(match[1]) : 0;
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
  
// Функция для получения моделей сгруппированных по NFT с сортировкой
const getGroupedModelOptions = () => {
  try {
    if (modelsLoading.value) {
      return {};
    }
    
    const groups = {};
    const searchQuery = modelSearchQuery.value.toLowerCase().trim();
    
    selectedFilters.value.nft.forEach(nftType => {
      if (nftModelsCache.value[nftType]) {
        const modelsData = [];
        
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
              
              modelsData.push({
                name,
                rarity,
                rarityText,
                parentNft: nftType,
                imageUrl: imageUrl,
                isSelected: isOptionSelected('model', name),
                floorPrice: getFloorPrice('model', name)
              });
            }
          }
        });
        
        modelsData.sort((a, b) => {
          if (a.isSelected && !b.isSelected) return -1;
          if (!a.isSelected && b.isSelected) return 1;
          return a.rarity - b.rarity;
        });
        
        groups[nftType] = modelsData;
      } else {
        groups[nftType] = [];
      }
    });
    
    return groups;
    
  } catch (error) {
    return {};
  }
};

// Функция для получения выбранных моделей в конкретной группе
const getSelectedModelsInGroup = (nftType) => {
  const group = getGroupedModelOptions()[nftType] || [];
  return group.filter(model => model.isSelected);
};

const getUnselectedModelsInGroup = (nftType) => {
  const group = getGroupedModelOptions()[nftType] || [];
  return group.filter(model => !model.isSelected);
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

// Функция для извлечения символа с процентом
const extractSymbolWithPercentage = (item) => {
  try {
    console.log('🔍 Извлечение символа с процентом для item:', item.id);
    
    let rawSymbol = null;
    
    // 1. Пытаемся получить symbol из metadata
    if (item.nft_metadata?.symbol) {
      rawSymbol = item.nft_metadata.symbol;
    }
    // 2. Пытаемся получить из прямого поля symbol
    else if (item.symbol) {
      rawSymbol = item.symbol;
    }
    // 3. Парсим nft_object если есть
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
    }
    
    if (!rawSymbol) {
      return { name: null, percentage: 0 };
    }
    
    // Извлекаем название и процент
    const symbolMatch = rawSymbol.match(/(.+?)\s*(\d+\.?\d*)%?$/);
    if (symbolMatch) {
      const name = symbolMatch[1].trim();
      const percentage = parseFloat(symbolMatch[2]) || 0;
      return { name, percentage };
    } else {
      // Если нет процента, возвращаем только название
      const name = rawSymbol.replace(/\d+\.?\d*%/, '').trim();
      return { name, percentage: 0 };
    }
    
  } catch (error) {
    console.error('❌ Ошибка извлечения символа:', error);
    return { name: null, percentage: 0 };
  }
};

// Функция для извлечения backdrop с процентом
const extractBackdropWithPercentage = (item) => {
  try {
    console.log('🎨 Извлечение backdrop с процентом для item:', item.id);
    
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
        console.log(`📋 Backdrop найден в ${source.name}:`, rawBackdrop);
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
      console.log('✅ Backdrop с процентом:', { name, percentage });
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



function getNftDisplayName(nftKey, nftObject = null) {
  // Если передан nft_object и в нем есть name, используем его
  if (nftObject) {
    try {
      const obj = typeof nftObject === 'string' ? JSON.parse(nftObject) : nftObject;
      if (obj && obj.name) {
        return obj.name;
      }
      // Для HTML NFT из URL
      if (obj && obj.url) {
        const match = obj.url.match(/\/nft\/([^-]+)/);
        if (match && match[1]) {
          const name = match[1];
          // Преобразуем camelCase в нормальное название
          return name.replace(/([A-Z])/g, ' $1').trim();
        }
      }
    } catch (e) {
      console.error('Error parsing nft_object:', e);
    }
  }
  
  // Для HTML NFT по типу
  if (nftKey.startsWith('html_nft_')) {
    const parts = nftKey.split('_')[2]?.split('-') || [];
    const name = parts[0] || 'HTML NFT';
    return name.replace(/([A-Z])/g, ' $1').trim();
  }
  
  // Маппинг для названий групп моделей (соответствует названиям колонок в БД)
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
  
  // Проверяем, есть ли ключ в маппинге для групп моделей
  const normalizedKey = nftKey.toLowerCase();
  if (groupDisplayNames[normalizedKey]) {
    return groupDisplayNames[normalizedKey];
  }
  
  // Стандартные имена из mapping
  return nftDisplayNames[nftKey] || nftKey;
}
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
    const selectedFilters = ref({
      nft: [],
      model: [],
      symbol: [],
      backdrop: [],
      price: [],
      rarity: []
    });

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

// Функция normalizeSymbolName уже существует, добавим ее для полноты
const normalizeSymbolName = (name) => {
  if (!name) return '';
  return name.toLowerCase().replace(/[^a-z0-9]/g, '');
};

// Функция для получения floor price
// Функция для получения floor price для опции
const getFloorPrice = (category, optionName) => {
  try {
    if (!marketItems.value || marketItems.value.length === 0) {
      return null;
    }

    let filteredItems = [];

    // Фильтруем items в зависимости от категории
    switch (category) {
      case 'model':
        filteredItems = marketItems.value.filter(item => {
          const itemModel = extractModelFromNft(item);
          return itemModel && normalizeModelName(itemModel) === normalizeModelName(optionName);
        });
        break;

      case 'symbol':
        filteredItems = marketItems.value.filter(item => {
          const itemSymbol = extractSymbolFromNft(item);
          return itemSymbol && normalizeSymbolName(itemSymbol) === normalizeSymbolName(optionName);
        });
        break;

      case 'backdrop':
        filteredItems = marketItems.value.filter(item => {
          const itemBackdrop = extractBackdropFromNft(item);
          return itemBackdrop && normalizeBackdropName(itemBackdrop) === normalizeBackdropName(optionName);
        });
        break;

      case 'nft':
        filteredItems = marketItems.value.filter(item => {
          const itemName = getNftDisplayName(item.nft_type, item.nft_object);
          return normalizeNftName(itemName) === normalizeNftName(optionName);
        });
        break;

      default:
        return null;
    }

    // Если нет подходящих items, возвращаем null
    if (filteredItems.length === 0) {
      return null;
    }

    // Находим минимальную цену среди отфильтрованных items
    const prices = filteredItems
      .map(item => {
        const price = parseFloat(item.price_per_unit);
        return !isNaN(price) && price > 0 ? price : null;
      })
      .filter(price => price !== null);

    if (prices.length === 0) {
      return null;
    }

    const minPrice = Math.min(...prices);

    // Возвращаем число, а не строку
    return isFinite(minPrice) ? minPrice : null;

  } catch (error) {
    console.error(`Error calculating floor price for ${category} "${optionName}":`, error);
    return null;
  }
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

// Функция для получения выбранных символов (вверху списка)
const getSelectedSymbolOptions = () => {
  const allOptions = getFilteredSymbols();
  console.log('✅ Выбранные символы:', allOptions.filter(option => 
    isOptionSelected('symbol', option.name)
  ));
  return allOptions.filter(option => 
    isOptionSelected('symbol', option.name)
  );
};

// Функция для получения невыбранных символов (после выбранных)
const getUnselectedSymbolOptions = () => {
  const allOptions = getFilteredSymbols();
  console.log('❌ Невыбранные символы:', allOptions.filter(option => 
    !isOptionSelected('symbol', option.name)
  ));
  return allOptions.filter(option => 
    !isOptionSelected('symbol', option.name)
  );
};
// Функция для получения выбранных backdrop (вверху списка)
const getSelectedBackdropOptions = () => {
  const allOptions = getFilteredBackdrops();
  return allOptions.filter(option => 
    isOptionSelected('backdrop', option.id)
  );
};

// Функция для получения невыбранных backdrop (после выбранных)
const getUnselectedBackdropOptions = () => {
  const allOptions = getFilteredBackdrops();
  return allOptions.filter(option => 
    !isOptionSelected('backdrop', option.id)
  );
};



// В секции computed свойств обновите filteredMarketItems
const filteredMarketItems = computed(() => {
  const items = getCurrentDataSource.value;
  
  return items.filter(item => {
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
      const itemId = extractNftId(item.nft_object);
      if (parseInt(itemId) !== selectedIdFilter.value) return false;
    }
    
    return true;
  }).sort((a, b) => {
    // Логика сортировки остается прежней
    switch (sortMenu.value.selected) {
      case 'price_asc':
        return a.price_per_unit - b.price_per_unit;
      case 'price_desc':
        return b.price_per_unit - a.price_per_unit;
      case 'id_asc':
        return extractIdFromNftType(a.nft_type) - extractIdFromNftType(b.nft_type);
      case 'id_desc':
        return extractIdFromNftType(b.nft_type) - extractIdFromNftType(a.nft_type);
      case 'model_asc':
        return extractModelRarity(a) - extractModelRarity(b);
      case 'model_desc':
        return extractModelRarity(b) - extractModelRarity(a);
      default:
        return new Date(b.created_at || 0) - new Date(a.created_at || 0);
    }
  });
});

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
const selectedIdFilter = ref(null);
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




    const extractNftIdFromHtml = (html) => {
      try {
        const postMessageMatch = html.match(/nftId:\s*['"]([^'"]+)['"]/);
        if (postMessageMatch && postMessageMatch[1]) return postMessageMatch[1];
        
        const urlMatch = html.match(/https?:\/\/[^\s"'<>]+/i);
        if (urlMatch) {
          const url = new URL(urlMatch[0]);
          return url.pathname.split('/').filter(Boolean).pop();
        }
        
        return null;
      } catch {
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
    const currentAccountName = ref('');
    const userScore = ref(0);
    
    // Функция для загрузки данных пользователя
    const loadUserProfileData = async () => {
      try {
        const savedAccount = localStorage.getItem('currentAccount');
        if (savedAccount) {
          const account = JSON.parse(savedAccount);
          currentAccountName.value = account.name;
          
          // Загружаем данные пользователя из базы данных
          const { data: userData, error } = await supabase
            .from('users')
            .select('score')
            .eq('name', account.name)
            .single();
            
          if (error) throw error;
          
          if (userData) {
            userScore.value = userData.score || 0;
          }
        }
      } catch (error) {
        console.error('Ошибка загрузки данных профиля:', error);
      }
    };
    const activeTab = ref('my-nfts');
    const nfts = ref({});
    const loading = ref(true);
    const marketLoading = ref(false);
    const showHistory = ref(false);
    const historyTab = ref('sales');
    const salesHistory = ref([]);
    const transfersHistory = ref([]);
    const marketHistory = ref([]);
    const loadingHistory = ref(false);
    const marketItems = ref([]);
    const closeFilterMenu = () => {
  activeFilterCategory.value = null;
  nftImageUrls.value = {}; // Сбрасываем кеш изображений
};

    const handleScroll = () => {
      if (activeFilterCategory.value) {
        closeFilterMenu();
      }
    };

    onMounted(() => {
      categoriesContainer.value?.addEventListener('scroll', handleScroll);
    });

    onUnmounted(() => {
      categoriesContainer.value?.removeEventListener('scroll', handleScroll);
    });

    const showFilterDropdown = ref(false);
    const selectedNftTypes = ref([]);
    const easterEggNfts = [''];
    const featuredNfts = [''];
    
const loadNftImages = async (nftTypesWithNames) => {
  const urls = {...nftImageUrls.value};
  
  // Фильтруем только те NFT, для которых изображения ещё не загружены
  const typesToLoad = nftTypesWithNames.filter(([type, name]) => !urls[type]);
  
  if (typesToLoad.length === 0) return;
  
  console.groupCollapsed('🎨 Генерация случайных ссылок для NFT');
  
  try {
    for (const [nftType, nftName] of typesToLoad) {
      let attempt = 0;
      let randomModel;
      const maxAttempts = 5;
      
      while (attempt < maxAttempts) {
        randomModel = await getRandomModelForNft(nftName);
        
        if (!randomModel) break;
        
        if (!modelCache[nftType]?.includes(randomModel)) {
          break;
        }
        
        attempt++;
        console.log(`🔄 Попытка ${attempt}: найти новую модель для ${nftName}`);
      }
      
      if (randomModel) {
        if (!modelCache[nftType]) modelCache[nftType] = [];
        modelCache[nftType].push(randomModel);
        
        // Генерируем путь на основе имени NFT
        const path = nftName.replace(/\s+/g, '%20').toLowerCase();
        const imageUrl = `https://gifts.coffin.meme/${path}/${randomModel}.png`;
        urls[nftType] = imageUrl;
        
        console.log(`✨ NFT: ${nftName}`);
        console.log(`📁 Папка: ${path}`);
        console.log(`🎲 Модель: ${randomModel}`);
        console.log(`🔗 Ссылка: ${imageUrl}`);
      } else {
        urls[nftType] = default_nft_image;
        console.warn(`⚠️ Для ${nftName} используется изображение по умолчанию`);
      }
    }
  } catch (error) {
    console.error('🔥 Ошибка:', error);
  } finally {
    console.groupEnd();
    nftImageUrls.value = urls;
  }
};


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

// Сбрасываем кэш при смене категории
watch(activeFilterCategory, () => {
  imageCache.value = {};
});

const getNftImage = async (nftType, nftObject = null) => {
  if (imageCache.value[nftType]) {
    console.log(`🔄 Используется кэшированная ссылка для ${nftType}: ${imageCache.value[nftType]}`);
    return imageCache.value[nftType];
  }
  
  let nftName = getNftDisplayName(nftType, nftObject);
  console.log(`🎯 Начинаем генерацию ссылки для: ${nftName} (тип: ${nftType})`);
  
  try {
    const randomModel = await getRandomModelForNft(nftName);
    console.log(`🎲 Получена случайная модель: ${randomModel}`);
    
    if (randomModel) {
      const path = nftName.replace(/\s+/g, '%20').toLowerCase();
      const imageUrl = `https://gifts.coffin.meme/${path}/${randomModel}.png`;
      
      imageCache.value[nftType] = imageUrl;
      
      // ВЫВОДИМ ССЫЛКУ В КОНСОЛЬ ТОЛЬКО ДЛЯ КАТЕГОРИИ MODEL
      if (activeFilterCategory.value === 'model') {
        console.log(`✅ Сгенерирована ссылка для категории Model: ${imageUrl}`);
        console.log(`📁 Путь: ${path}`);
        console.log(`🎨 Модель: ${randomModel}`);
        console.log('---');
      }
      
      return imageUrl;
    }
  } catch (error) {
    console.error(`❌ Ошибка генерации:`, error);
  }
  
  // Fallback
  const randomModel = await getRandomModelForNft(nftName);
    console.log(`🎲 Получена случайная модель: ${randomModel}`);
  const path = nftName.replace(/\s+/g, '%20').toLowerCase();
  const fallbackUrl = `https://gifts.coffin.meme/${path}/${randomModel}.png`;
  imageCache.value[nftType] = fallbackUrl;
  
  // ВЫВОДИМ FALLBACK ССЫЛКУ В КОНСОЛЬ ТОЛЬКО ДЛЯ КАТЕГОРИИ MODEL
  if (activeFilterCategory.value === 'model') {
    console.log(`🔄 Используется fallback ссылка для категории Model: ${fallbackUrl}`);
  }
  return fallbackUrl;
};

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

    const initiateCancelSale = (item) => {
      cancelSaleModal.value = {
        show: true,
        id: item.id,
        nftType: item.nft_type,
        amount: item.amount
      };
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
    
    
    
    const executeCancelSale = async () => {
      try {
        const { id, nftType, amount } = cancelSaleModal.value;
        const isHtmlNft = nftType.startsWith('html_nft_');

        const { data: marketItem, error: marketError } = await supabase
          .from('market')
          .select('*, nft_object')
          .eq('id', id)
          .single();

        if (marketError || !marketItem) throw new Error('Объявление не найдено');
        
        if (isHtmlNft && !marketItem.nft_object) {
          throw new Error('Отсутствуют данные NFT');
        }

        const { data: userData, error: userError } = await supabase
          .from('users')
          .select('*')
          .eq('name', currentAccountName.value)
          .single();

        if (userError) throw userError;

        const { error: deleteError } = await supabase
          .from('market')
          .delete()
          .eq('id', id);

        if (deleteError) throw deleteError;

        let updates = {};
        
        if (isHtmlNft) {
          const currentLinks = userData.nft_links || [];
          updates.nft_links = [...currentLinks, marketItem.nft_object];
        } else {
          updates[nftType] = (userData[nftType] || 0) + amount;
        }

        const { error: updateError } = await supabase
          .from('users')
          .update(updates)
          .eq('name', currentAccountName.value);

        if (updateError) throw updateError;

        if (isHtmlNft) {
          htmlNfts.value = [...(htmlNfts.value || []), {
            ...marketItem.nft_object,
            id: nftType
          }];
        } else {
          nfts.value[nftType] = (nfts.value[nftType] || 0) + amount;
        }

        showNotification('NFT успешно снято с продажи!', 'success');
        cancelSaleModal.value.show = false;
        await loadMarketItems();

      } catch (error) {
        console.error('Ошибка снятия:', error);
        showNotification(`Ошибка: ${error.message}`, 'error');
      }
    };
  

    
    // Загружаем unlisted NFT при переходе на вкладку
    watch(() => activeTab.value, (newTab) => {
      if (newTab === 'my-nfts') {
        loadUnlistedNfts();
      }
    });
    
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
        const isHtmlNft = nftType.startsWith('html_nft_');

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
          .select('*, nft_object')
          .eq('id', id)
          .single();

        if (marketError || !marketItem) throw new Error('Объявление не найдено');
        
        if (isHtmlNft && !marketItem.nft_object) {
          throw new Error('Отсутствуют данные NFT');
        }

        const { error: deleteError } = await supabase
          .from('market')
          .delete()
          .eq('id', id);

        if (deleteError) throw new Error('Ошибка удаления объявления');

        const buyerUpdates = {
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

        if (isHtmlNft) {
          buyerUpdates.nft_links = [
            ...(buyerData.nft_links || []),
            marketItem.nft_object
          ];
        } else {
          buyerUpdates[nftType] = (buyerData[nftType] || 0) + numAmount;
        }

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

        const { error: updateBuyerError } = await supabase
          .from('users')
          .update(buyerUpdates)
          .eq('name', currentAccountName.value);

        if (updateBuyerError) throw updateBuyerError;

        const { error: updateSellerError } = await supabase
          .from('users')
          .update(sellerUpdates)
          .eq('name', seller);

        if (updateSellerError) throw updateSellerError;

        tonBalance.value = isTONPurchase ? buyerUpdates.ton_balance : tonBalance.value;
        userScore.value = isTONPurchase ? userScore.value : buyerUpdates.score;
        
        if (isHtmlNft) {
          htmlNfts.value = [...htmlNfts.value, {
            ...marketItem.nft_object,
            id: nftType
          }];
        } else {
          nfts.value[nftType] = (nfts.value[nftType] || 0) + numAmount;
        }

        marketItems.value = marketItems.value.filter(item => item.id !== id);

        showNotification(`Успешная покупка! Получено ${numAmount} ${getNftDisplayName(nftType)}`, 'success');
        buyModal.value.show = false;
        cartItems.value = cartItems.value.filter(cartItem => cartItem.id !== item.id);
        await saveCartToDatabase(); // Сохраняем изменения в базу данных
        localStorage.setItem('userCart', JSON.stringify(cartItems.value));
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
    watch(() => selectedFilters.value.nft, async (newVal) => {
  if (activeFilterCategory.value === 'model' && newVal.length > 0) {
    await loadNftModels(newVal[0]);
  }
}, { deep: true });

function getNftDisplayName(nftKey, nftObject = null) {
  // Если передан nft_object и в нем есть name, используем его
  if (nftObject && typeof nftObject === 'object' && nftObject.name) {
    return nftObject.name;
  }
  
  // Для unlisted NFT (объекты с url)
  if (nftObject && nftObject.url) {
    const match = nftObject.url.match(/\/nft\/([^-]+)/);
    if (match && match[1]) {
      const name = match[1];
      // Преобразуем camelCase в нормальное название
      return name.replace(/([A-Z])/g, ' $1').trim();
    }
    return 'Unknown NFT';
  }
  
  // Для HTML NFT по типу
  if (nftKey.startsWith('html_nft_')) {
    const parts = nftKey.split('_')[2]?.split('-') || [];
    const name = parts[0] || 'HTML NFT';
    return name.replace(/([A-Z])/g, ' $1').trim();
  }
  
  // Стандартные имена из mapping
  return nftDisplayNames[nftKey] || nftKey;
}
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

    const loadMarketItems = async () => {
  marketLoading.value = true;
  
  try {
    // Простой запрос без joins, так как связи нет
    const { data: marketData, error: marketError } = await supabase
      .from('market')
      .select('*')
      .order('created_at', { ascending: false });

    if (marketError) throw marketError;

    // Вручную добавляем metadata если есть поле metadata_id
    const itemsWithMetadata = await Promise.all(
      marketData.map(async (item) => {
        if (item.metadata_id) {
          try {
            const { data: metadata, error: metaError } = await supabase
              .from('nft_metadata')
              .select('model, backdrop, symbol')
              .eq('id', item.metadata_id)
              .single();

            if (!metaError && metadata) {
              return { ...item, nft_metadata: metadata };
            }
          } catch (metaError) {
            console.error('Ошибка загрузки metadata для item', item.id, metaError);
          }
        }
        return { ...item, nft_metadata: null };
      })
    );

    marketItems.value = itemsWithMetadata;
    
  } catch (error) {
    console.error('Ошибка загрузки рынка:', error);
    showNotification('Ошибка загрузки рыночных предложений', 'error');
  } finally {
    marketLoading.value = false;
  }
};


    
    const closeHtmlModal = () => {
      htmlModal.value = {
        show: false,
        htmlContent: '',
        title: '',
        seller: '',
        price: 0,
        currency: 'AMHSL',
        item: null,
        offset: 0,
        startY: 0,
        isDragging: false,
        isClosing: false,
        telegramLink: null
      };
      document.body.style.overflow = 'auto';
    };

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



watch(() => marketItems.value, () => {
  // Можно обновлять кэш при каждом изменении marketItems
  // или использовать дебаунс для оптимизации
  updateAllFloorPrices();
}, { deep: true });


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
      modelsLoading,
      applyIdFilter,
      clearIdFilter,
      extractIdFromNftObject,
      itemDetailsModal,
      getAllModelDataSortedByRarity,
      showFilterDropdown,
      searchQuery,
      selectedNftTypes,
      filteredEasterEggNfts,
      filteredFeaturedNfts,
      setActiveTab,
      openHtmlModalForUnlisted,
      getNftDisplayName,
      getNftImage,
      isTONNFT,
      getNftSellPrice,
      getTotalSellPrice,
      getCommission,
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
      calculateCartTotal,
      tonlogoblack,
      buyAllFromCart,
      getSortedNftOptions,
      validateTransferAmount,
      validateSellAmount,
      checkRecipientExists,
      formatDate,
      formatDateTime,
      showNotification,
      loadHistory,
      getTotalNFTsInCart,
      initiateCancelSale,
      executeCancelSale,
      initiateTransfer,
      showConfirmation,
      debugFloorPrices,
      executeTransfer,
      clearFilterCategory,
      initiateSell,
      showSellConfirmation,
      executeSell,
      initiateBuy,
      executeBuy,
      loadMarketItems,
      goBack,
      startDrag,
      stopDrag,
        extractNftId,
      bucket_icon,
      myNftsViewMode,
      myUnlistedNfts,
      extractNftNameFromUrl,
      generateNftHtml,
      initiateSellFromUnlisted,
      rubish_bucket_icon,
      isInCart,
        extractNftIdFromUnlisted,
      modelSearchQuery,
      generateBackdropSVG,
      getSelectedNftOptions,
      getUnselectedNftOptions,
      handleModelSearch,
      getTotalModelsCount,
      handleModalClose,
      handleDrag,
      getFilteredBackdrops,
      getFilteredModels,
      getFilteredNftOptions,
      getSelectedSymbolOptions,
      getUnselectedSymbolOptions,
      getSelectedBackdropOptions,
      getUnselectedBackdropOptions,
      getFilteredSymbols,
      htmlNftModal,
      htmlModal,
      handleWithdraw,
      handleTransfer,
      toggleMyNftsViewMode,
      getModelsForNftSortedByRarity,
      openHtmlModal,
      handleAddNft,
      startHtmlModalDrag,
      handleHtmlModalDrag,
      stopHtmlModalDrag,
      handleBuyClick,
      extractUrlFromHtml,
      handleHtmlModalClose,
      htmlNfts,
      extractSymbolFromNftAdvanced,
      loadSymbolOptionsAlternative,
      getAllModelData,
      getAllModelNames,
      openTelegramLink,
      addSquareStyles,
      extractNftName,
      forceSquareStyles,
      extractMetadataFromUnlistedNft,
      closeHtmlModal,
      getSelectedModelOptions,
      getUnselectedModelOptions,
      filterCategories,
      activeFilterCategory,
      activeCategoryWidth,
      toggleFilterCategory,
      getFilterOptions,
      getAllModelOptions,
      toggleFilterOption,
      loadUserProfileData,
      tonlogofloor,
      isOptionSelected,
      dropdownPosition,
      filterButtons,
      setActiveFilter,
      categoriesContainer,
      setActiveFilter,
      closeFilterMenu,
      toggleSortMenu,
      
      tonlogo,
      togglePriceRangeMenu,
      applySort,
      openHtmlModal,
      applyPriceRange,
      resetPriceRange,
      fallbackImageUrl: 'https://gifts.coffin.meme/desk%20calendar/Pepe%20Plans.png',
      imageUrl: 'https://gifts.coffin.meme/desk%20calendar/Pepe%20Plans.png',
      filter_img,
      sell_img,
      sortMenu, 
      amahaslaImage,
      getNftDisplayNameForGroup,
      nftImageUrls,
      openCartItemModal,
      expandedNfts,
      expandedModelNfts,
      selectedNftModels,
      priceRangeMenu,
      expandedModelNfts,
      nftModelsCache,
      
      selectedFilters,
      toggleModelNftExpansion,
      handleOptionClick,
      nftImageCache,
      modelImageCache,
      getModelImageUrl,
      getSelectedModelsInGroup,
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
      bucket_icon,
      getNftDisplayNameFromUrl,
      myMarketItems,
      tonlogogray,
      tonlogoyellow,
      formatTonValue,
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
  box-shadow: 0 0 20px rgba(255, 187, 0, 0.2);
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
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
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
}

.nav-button {
  padding: 12px 20px;
  background-color: transparent;
  border: none;
  border-radius: 8px;
  font-size: 100px;
  font-weight: 600;
  color: #353535;
  cursor: pointer;
  transition: all 0.3s ease;
  
}

.nav-button.active {
  color: #cccccc;
  font-weight: 700;

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
  width: 90%;
  height: 100%;
  border: none;
  background-color: #2e2e2e;
  border-radius: 50px;
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
  top:5vh;
  position: relative;
  width: 85%; /* Увеличьте ширину до 95% от экрана */
  max-width: 90%; /* Уберите ограничение по максимальной ширине */
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
  border-radius: 20px;
  background: #1d1d1d;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
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
  font-weight: 500;
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
  margin: -6px 0 0 0;
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
  max-width: 90%;
  height: auto;
  margin: 0 auto;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.html-content-iframe {
  width: 100%;
  height: 10vh;
  min-height: 37vh;
  max-height: 45vh;
  border: none;
  border-radius: 20px;
  background: #1d1d1d;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
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
  width: 90%;
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
  background-color: #ff110054;
  color: #888888;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  width: 100%;
  margin-bottom: 40px;
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
  margin-bottom: 40px;
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
  background-color: #252525;
}

.no-nft-selected {
  padding: 20px;
  text-align: center;
  color: #888;
  font-size: 0.9rem;
}

/* Общие стили для обоих фильтров */
.filter-dropdown-menu {
  top: 30vh;
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
  font-weight: 500;
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
  margin-bottom: 8px;
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
  width: 20px;
  height: 19px;
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
  margin-top: 20px;
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
  height: 12px;
  width: 12px;
  margin-left: 4px;
}


.filter-option.selected .option-rarity {
  color: #666;
}
.profile-card {
  background-color: #2c2c2c;
  border-radius: 30px;
  padding: 20px 15px;
  text-align: center;
  margin-bottom: 15px;
  color: #000;
}

.avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #1d1d1d;
  margin-bottom: 12px;
}

.username {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 10px;
  color: #cccccc;
}

.score {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 6px;
  font-size: 18px;
  font-weight: 600;
  color: #000;
}

.frog-icon {
  width: 20px;
  height: 20px;
}
</style>



