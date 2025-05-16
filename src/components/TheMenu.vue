<template>
  <div class="menu">
    <RouterLink to="/" custom v-slot="{ isActive, navigate }">
      <i
        class="menu-button fa fa-home"
        :class="{ active: isActive }"
        @click="navigate"
        aria-hidden="true"
      ></i>
    </RouterLink>
    <RouterLink to="/friends" custom v-slot="{ isActive, navigate }">
      <i
        class="menu-button fa fa-users"
        :class="{ active: isActive }"
        @click="navigate"
        aria-hidden="true"
      ></i>
    </RouterLink>

    <RouterLink to="/tasks" custom v-slot="{ isActive, navigate }">
      <i
        class="menu-button fa fa-tasks"
        :class="{ active: isActive }"
        @click="navigate"
        aria-hidden="true"
      ></i>
    </RouterLink>

    <RouterLink to="/shop" custom v-slot="{ isActive, navigate }">
      <i
        class="menu-button fa fa-shopping-cart"
        :class="{ active: isActive }"
        @click="navigate"
        aria-hidden="true"
      ></i>
    </RouterLink>
    <RouterLink to="/register" custom v-slot="{ isActive, navigate }">
      <i
        class="menu-button fa fa-user"
        :class="{ active: isActive }"
        @click="navigate"
        aria-hidden="true"
      ></i>
    </RouterLink>
    <RouterLink to="/casinopage" custom v-slot="{ isActive, navigate }">
      <i
        class="menu-button fa fa-dice"
        :class="{ active: isActive }"
        @click="navigate"
        aria-hidden="true"
      ></i>
    </RouterLink>
  </div>
</template>

<script>
import { RouterLink } from 'vue-router';
// В main.js или в компоненте
document.documentElement.style.overflow = 'auto'; // Для <html>
document.body.style.overflow = 'auto'; // Для <body>
export default {
  components: {
    RouterLink,
  },
};
</script>

<style scoped>
.menu {
  position: fixed; /* Фиксированное позиционирование */
  bottom: 0; /* Прижимаем к нижней части экрана */
  left: 0; /* Выравниваем по левому краю */
  width: 100%; /* Ширина на весь экран */
  display: flex;
  justify-content: space-around; /* Равномерное распределение кнопок */
  align-items: center;
  background-color: #333; /* Цвет фона меню */
  padding: 10px 0; /* Отступы сверху и снизу */
  z-index: 1000; /* Убедимся, что меню поверх других элементов */
}

.menu-button {
  color: white; /* Цвет иконок */
  font-size: 24px; /* Размер иконок */
  cursor: pointer; /* Курсор в виде указателя */
}

.menu-button.active {
  color: #ffd900; /* Цвет активной иконки */
}

.menu-button:hover {
  opacity: 0.8; /* Эффект при наведении */
}
</style>




