<template>
  <div class="menu">
    <RouterLink to="/" custom v-slot="{ isActive, navigate }">
      <div class="menu-item" :class="{ active: isActive }" @click="navigate">
        <i
          class="menu-button fa fa-home"
          :class="{ active: isActive }"
          aria-hidden="true"
        ></i>
        <span class="menu-label" :class="{ active: isActive }">Home</span>
      </div>
    </RouterLink>

    <RouterLink to="/shop" custom v-slot="{ isActive, navigate }">
      <div class="menu-item" :class="{ active: isActive }" @click="navigate">
        <i
          class="menu-button fa fa-shop"
          :class="{ active: isActive }"
          aria-hidden="true"
        ></i>
        <span class="menu-label" :class="{ active: isActive }">Store</span>
      </div>
    </RouterLink>
    
    <RouterLink to="/profile" custom v-slot="{ isActive, navigate }">
      <div class="menu-item" :class="{ active: isActive }" @click="navigate">
        <i
          class="menu-button fa fa-user"
          :class="{ active: isActive }"
          aria-hidden="true"
        ></i>
        <span class="menu-label" :class="{ active: isActive }">Profile</span>
      </div>
    </RouterLink>
  </div>
</template>

<script>
import { RouterLink } from 'vue-router';

export default {
  components: {
    RouterLink,
  },
  mounted() {
    // Устанавливаем overflow при монтировании компонента
    document.documentElement.style.overflow = 'auto';
    document.body.style.overflow = 'auto';
  },
  beforeUnmount() {
    // Возвращаем overflow в исходное состояние при размонтировании (опционально)
    // document.documentElement.style.overflow = '';
    // document.body.style.overflow = '';
  }
};
</script>

<style scoped>
.menu {
  left: 2.5%;
  position: fixed;
  bottom: 18px;
  width: 95%;
  display: flex;
  justify-content: space-around;
  align-items: center;
  background-color: rgba(51, 51, 51, 0.2);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  padding: 8px 0 12px 0;
  z-index: 1000;
  border: 2px solid rgba(65, 65, 65, 0.2);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  border-radius: 30px;
}

.menu-item {
  margin-top: 5px;
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 25px;
  transition: all 0.2s ease;
  font-weight: 600;
  width: 115px;
}

.menu-item:hover {
  background-color: rgba(255, 255, 255, 0.025);
}

/* Эффект объёма у активного пункта */
.menu-item.active {
  box-shadow: 
    0 4px 8px rgba(0, 0, 0, 0.2),
    0 2px 4px rgba(0, 0, 0, 0.1),
    inset 0 -1px 2px rgba(0, 0, 0, 0.1),
    inset 0 1px 2px rgba(255, 255, 255, 0.2);
  
  
  transform: translateY(-1px);
}

.menu-button {
  color: white;
  font-size: 22px;
  margin-bottom: 3px;
  transition: all 0.2s ease;
}

.menu-button.active {
  color: #ffbb00;
}

.menu-label {
  color: white;
  font-size: 11px;
  font-weight: 500;
  opacity: 0.8;
  transition: all 0.2s ease;
  font-weight: 750;
}

.menu-label.active {
  color: #ffbb00;
  opacity: 1;
  text-shadow: 0 2px 4px rgba(255, 187, 0, 0.3);
  font-weight: 750;
}

</style>