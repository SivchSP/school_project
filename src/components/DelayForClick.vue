<template>
  <!-- Видео-баннер как Instagram Stories вместо кнопки BANK -->
  <div v-if="hasActiveVideo" class="video-banner-wrapper" :style="buttonContainerStyle">
    <div class="fancy-video-parallelogram">
      <!-- Прогресс-бар ПОД видео/изображением -->
      <div class="stories-progress-container">
        <div 
          v-for="item in activeMediaList"
          :key="item.type"
          class="progress-bar" 
          :class="{ 
            active: currentMedia === item.type, 
            completed: getProgress(item.type) === 100 
          }"
          @click="switchMedia(item.type)"
        >
          <div 
            class="progress-fill" 
            :style="{ width: getProgress(item.type) + '%' }"
          ></div>
        </div>
      </div>

      <div class="video-border">
        <!-- Видео для Bank и Giveaway -->
        <video 
          v-if="currentMedia === 'Bank' || currentMedia === 'GIVEAWAY'"
          ref="videoPlayer"
          autoplay 
          muted 
          playsinline
          class="banner-video"
          @timeupdate="updateProgress"
          @ended="handleMediaEnd"
          @loadedmetadata="onMediaLoaded"
          @click="handleMediaClick"
          @error="handleVideoError"
        >
          <source :src="currentMediaSrc" type="video/mp4">
          Ваш браузер не поддерживает видео.
        </video>
        
        <!-- Изображение для BonusTon и ZeroFee -->
        <img 
          v-else-if="currentMedia === 'BONUSTON' || currentMedia === 'ZEROFEE'"
          :src="currentMediaSrc"
          :alt="currentMedia"
          class="banner-image"
          @click="handleMediaClick"
          @load="onImageLoaded"
          @error="handleImageError"
        />
      </div>
    </div>
  </div>
</template>
<script setup>
import { useScoreStore } from '@/stores/score';
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue';
import supabase from '../../services/supabase';
import { useRouter } from 'vue-router';
import Bank from '@/assets/BANK.mp4';
import Giveaway from '@/assets/GiveAway.mp4';
import BonusTon from '@/assets/bonus_ton.png';
import ZeroFee from '@/assets/zero_fees.png';

const router = useRouter();
const store = useScoreStore();

// Переменные для прогресс-баров
const currentUserName = computed(() => store.currentAccount?.name);

const screenWidth = ref(window.screen.width);
const width_size = ref('369px');
const maxClicks = 100;
const availableClicks = ref(maxClicks);
const userBoost = ref(0);
const userData = ref(null);

// Переменные для медиа-баннера
const videoPlayer = ref(null);
const currentMedia = ref('Bank');
const mediaProgress = ref({
  Bank: 0,
  GIVEAWAY: 0,
  BONUSTON: 0,
  ZEROFEE: 0
});
const currentMediaSrc = ref(Bank);
const isMediaLoading = ref(false);
const imageTimer = ref(null);
const imageDisplayDuration = 8000; // Увеличил до 8 секунд для изображений
const videoPlaybackRate = 0.7; // Замедляем видео на 30%

const videoConfig = ref({
  bank: false,
  giveaway: false,
  bonuston: false,
  zerofee: false
});

const videoLinks = ref({
  bank: '',
  giveaway: '',
  bonuston: '',
  zerofee: ''
});

let interval;
let progressAnimationFrame = null;

// Вспомогательная функция для получения прогресса
const getProgress = (mediaType) => {
  return mediaProgress.value[mediaType] || 0;
};

// Список активных медиа для цикла
const activeMediaList = computed(() => {
  const list = [];
  if (videoConfig.value.bank) list.push({ type: 'Bank', src: Bank });
  if (videoConfig.value.giveaway) list.push({ type: 'GIVEAWAY', src: Giveaway });
  if (videoConfig.value.bonuston) list.push({ type: 'BONUSTON', src: BonusTon });
  if (videoConfig.value.zerofee) list.push({ type: 'ZEROFEE', src: ZeroFee });
  return list;
});

// Функция для преобразования строковых значений в булевы
const parseBooleanString = (value) => {
  if (value === true || value === false) return value;
  if (value === 'true') return true;
  if (value === 'false') return false;
  return false;
};

// Загрузка конфигурации видео
const loadVideoConfig = async () => {
  try {
    const { data, error } = await supabase
      .from('configurations')
      .select('home_video, video_link')
      .single();
    
    if (error) {
      console.error('Ошибка загрузки конфигурации видео:', error);
      return;
    }
    
    // Загружаем конфигурацию видео (статусы)
    if (data && data.home_video) {
      let config = { bank: false, giveaway: false, bonuston: false, zerofee: false };
      
      if (Array.isArray(data.home_video) && data.home_video.length > 0) {
        const rawConfig = data.home_video[0];
        config = {
          bank: parseBooleanString(rawConfig.bank),
          giveaway: parseBooleanString(rawConfig.giveaway),
          bonuston: parseBooleanString(rawConfig.bonuston),
          zerofee: parseBooleanString(rawConfig.zerofee)
        };
      } else if (typeof data.home_video === 'object' && data.home_video !== null) {
        config = {
          bank: parseBooleanString(data.home_video.bank),
          giveaway: parseBooleanString(data.home_video.giveaway),
          bonuston: parseBooleanString(data.home_video.bonuston),
          zerofee: parseBooleanString(data.home_video.zerofee)
        };
      }
      
      videoConfig.value = config;
    }
    
    // Загружаем ссылки для видео
    if (data && data.video_link) {
      let links = { bank: '', giveaway: '', bonuston: '', zerofee: '' };
      
      if (Array.isArray(data.video_link) && data.video_link.length > 0) {
        const rawLinks = data.video_link[0];
        links = {
          bank: rawLinks.bank || '',
          giveaway: rawLinks.giveaway || '',
          bonuston: rawLinks.bonuston || '',
          zerofee: rawLinks.zerofee || ''
        };
      } else if (typeof data.video_link === 'object' && data.video_link !== null) {
        links = {
          bank: data.video_link.bank || '',
          giveaway: data.video_link.giveaway || '',
          bonuston: data.video_link.bonuston || '',
          zerofee: data.video_link.zerofee || ''
        };
      }
      
      videoLinks.value = links;
    }
    
    // Устанавливаем начальное медиа на основе конфигурации
    if (activeMediaList.value.length > 0) {
      currentMedia.value = activeMediaList.value[0].type;
      currentMediaSrc.value = activeMediaList.value[0].src;
    }
    
  } catch (error) {
    console.error('Ошибка при загрузке конфигурации:', error);
  }
};

// Проверяем, есть ли активное медиа для отображения
const hasActiveVideo = computed(() => {
  return activeMediaList.value.length > 0;
});

// Обработчик клика по медиа
const handleMediaClick = () => {
  let link = '';
  if (currentMedia.value === 'Bank') {
    link = videoLinks.value.bank;
  } else if (currentMedia.value === 'GIVEAWAY') {
    link = videoLinks.value.giveaway;
  } else if (currentMedia.value === 'BONUSTON') {
    link = videoLinks.value.bonuston;
  } else if (currentMedia.value === 'ZEROFEE') {
    link = videoLinks.value.zerofee;
  }
  
  if (link && link.trim() !== '') {
    window.open(link, '_blank');
  } else {
    router.push('/records');
  }
};

// Загружаем данные пользователя и восстанавливаем клики
const loadUserData = async () => {
  if (!currentUserName.value) return;

  const { data, error } = await supabase
    .from('users')
    .select('*')
    .eq('name', currentUserName.value)
    .single();
    
  if (data) {
    userData.value = data;
    userBoost.value = data.boost || 0;

    const lastUpdate = new Date(data.last_click_update || new Date());
    const now = new Date();
    const secondsPassed = Math.floor((now - lastUpdate) / 1000);

    const newClicks = Math.min(
      maxClicks,
      (data.available_clicks || maxClicks) + secondsPassed
    );

    availableClicks.value = newClicks;
    store.setCurrentAccount(data);

    await supabase
      .from('users')
      .update({ 
        available_clicks: newClicks,
        last_click_update: now.toISOString() 
      })
      .eq('name', currentUserName.value);
  } else if (error) {
    console.error('Ошибка загрузки данных:', error);
  }
};

// Сохраняем клики и время обновления
const saveClicks = async () => {
  if (!currentUserName.value) return;

  const { error } = await supabase
    .from('users')
    .update({ 
      available_clicks: availableClicks.value,
      last_click_update: new Date().toISOString() 
    })
    .eq('name', currentUserName.value);

  if (error) {
    console.error('Ошибка сохранения:', error);
  }
};

const useClick = () => {
  const clickCost = userBoost.value + 1;
  
  if (availableClicks.value >= clickCost) {
    availableClicks.value -= clickCost;
    saveClicks();
    return true;
  }
  return false;
};

// Функции для медиа-баннера
const onMediaLoaded = () => {
  isMediaLoading.value = false;
  if (videoPlayer.value && (currentMedia.value === 'Bank' || currentMedia.value === 'GIVEAWAY')) {
    videoPlayer.value.playbackRate = videoPlaybackRate;
    videoPlayer.value.play().catch(e => console.log('Ошибка воспроизведения:', e));
  }
};

const onImageLoaded = () => {
  isMediaLoading.value = false;
  startImageTimer();
};

const handleVideoError = (e) => {
  console.error('Ошибка видео:', e);
  isMediaLoading.value = false;
  handleMediaEnd();
};

const handleImageError = (e) => {
  console.error('Ошибка загрузки изображения:', e);
  isMediaLoading.value = false;
  handleMediaEnd();
};

const startImageTimer = () => {
  // Очищаем предыдущую анимацию
  if (progressAnimationFrame) {
    cancelAnimationFrame(progressAnimationFrame);
  }
  
  // Сбрасываем прогресс для текущего изображения
  mediaProgress.value[currentMedia.value] = 0;
  
  // Запускаем анимацию прогресса
  const startTime = Date.now();
  const duration = imageDisplayDuration;
  
  const updateImageProgress = () => {
    const elapsed = Date.now() - startTime;
    const progress = (elapsed / duration) * 100;
    
    if (progress < 100) {
      mediaProgress.value[currentMedia.value] = progress;
      progressAnimationFrame = requestAnimationFrame(updateImageProgress);
    } else {
      mediaProgress.value[currentMedia.value] = 100;
      progressAnimationFrame = null;
      handleMediaEnd();
    }
  };
  
  progressAnimationFrame = requestAnimationFrame(updateImageProgress);
};

const updateProgress = () => {
  if (!videoPlayer.value || isMediaLoading.value) return;
  
  const currentTime = videoPlayer.value.currentTime;
  const duration = videoPlayer.value.duration;
  
  if (duration && duration > 0) {
    const progress = (currentTime / duration) * 100;
    mediaProgress.value[currentMedia.value] = Math.min(progress, 100);
  }
};

const handleMediaEnd = () => {
  const activeList = activeMediaList.value;
  
  // Если нет активных медиа - выходим
  if (activeList.length === 0) return;
  
  // Находим индекс текущего медиа
  const currentIndex = activeList.findIndex(item => item.type === currentMedia.value);
  
  // Вычисляем следующий индекс
  const nextIndex = (currentIndex + 1) % activeList.length;
  
  // Переключаемся на следующее медиа
  switchToMedia(activeList[nextIndex].type);
};

const switchToMedia = async (mediaType) => {
  if (currentMedia.value === mediaType || isMediaLoading.value) return;
  
  // Останавливаем текущее видео/анимацию
  if (videoPlayer.value) {
    videoPlayer.value.pause();
  }
  
  if (progressAnimationFrame) {
    cancelAnimationFrame(progressAnimationFrame);
    progressAnimationFrame = null;
  }
  
  isMediaLoading.value = true;
  
  // Находим src для нового медиа
  const mediaItem = activeMediaList.value.find(item => item.type === mediaType);
  if (!mediaItem) {
    isMediaLoading.value = false;
    return;
  }
  
  // Устанавливаем прогресс для всех на 0
  Object.keys(mediaProgress.value).forEach(key => {
    mediaProgress.value[key] = 0;
  });
  
  currentMedia.value = mediaType;
  currentMediaSrc.value = mediaItem.src;
  
  await nextTick();
  
  // Запускаем новое медиа
  if (mediaType === 'Bank' || mediaType === 'GIVEAWAY') {
    if (videoPlayer.value) {
      videoPlayer.value.currentTime = 0;
      videoPlayer.value.load();
      videoPlayer.value.playbackRate = videoPlaybackRate;
      
      try {
        await videoPlayer.value.play();
        isMediaLoading.value = false;
      } catch (e) {
        console.log('Ошибка воспроизведения видео:', e);
        isMediaLoading.value = false;
        handleMediaEnd();
      }
    }
  } else {
    isMediaLoading.value = false;
    startImageTimer();
  }
};

const switchMedia = (mediaType) => {
  // Проверяем доступность медиа
  const mediaExists = activeMediaList.value.some(item => item.type === mediaType);
  if (!mediaExists || currentMedia.value === mediaType) return;
  
  switchToMedia(mediaType);
};

onMounted(async () => {
  await loadVideoConfig();
  await loadUserData();

  interval = setInterval(() => {
    if (availableClicks.value < maxClicks) {
      availableClicks.value += 1;
      saveClicks();
    }
  }, 1000);

  const calculatedWidthSize = Math.ceil((screenWidth.value - 6));
  width_size.value = `${calculatedWidthSize}px`;
  
  if (screenWidth.value > 500) {
    width_size.value = '424px';
  }

  // Запускаем начальное медиа
  if (hasActiveVideo.value) {
    if (currentMedia.value === 'Bank' || currentMedia.value === 'GIVEAWAY') {
      nextTick(() => {
        if (videoPlayer.value) {
          videoPlayer.value.playbackRate = videoPlaybackRate;
          videoPlayer.value.play().catch(e => {});
        }
      });
    } else {
      startImageTimer();
    }
  }
});

onUnmounted(() => {
  clearInterval(interval);
  saveClicks();
  
  if (progressAnimationFrame) {
    cancelAnimationFrame(progressAnimationFrame);
  }
  
  if (videoPlayer.value) {
    videoPlayer.value.pause();
    videoPlayer.value = null;
  }
});

watch(currentUserName, (newVal) => {
  if (newVal) {
    loadUserData();
  }
});

watch(videoConfig, () => {
  // Если текущее медиа стало неактивным, переключаемся на первое доступное
  const mediaExists = activeMediaList.value.some(item => item.type === currentMedia.value);
  if (!mediaExists && activeMediaList.value.length > 0) {
    switchToMedia(activeMediaList.value[0].type);
  }
}, { deep: true });

const buttonContainerStyle = computed(() => ({
  position: 'fixed',
  top: '0px',
  left: '3px',
  width: width_size.value,
}));

defineExpose({
  availableClicks,
  useClick,
  userData,
});
</script>

<style scoped>
.progress-bar-container {
  text-align: center;
  background-color: #1f1f1f;
  border-radius: 0px;
  padding: 8px 0;
}

.progress-bar {
  width: 100%;
  height: 10px;
  background-color: #3d3d3d;
  border-radius: 10px;
  overflow: hidden;
}

.progress-valueperchik {
  height: 100%;
  background-color: #e7b81f;
  transition: width 0.3s ease;
}

.progress-info {
  margin-top: 8px;
  font-size: 15px;
  color: #e0e0e0;
  font-family: 'Inter', sans-serif;
  font-weight: 600;
}

.text {
  margin-top: 8px;
  font-size: 15px;
  color: #e0e0e0;
}

.fancy-video-parallelogram {
  width: 100%;
  height: 100px;
  position: relative;
  background: #3a3a3ab6;
  border-radius: 20px;
  padding: 3px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

.video-border {
  width: 100%;
  height: 100%;
  border-radius: 17px;
  overflow: hidden;
  background: #00000000;
  position: relative;
}

.fancy-video-parallelogram .banner-video,
.fancy-video-parallelogram .banner-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 17px;
}

.stories-progress-container {
  position: absolute;
  top: 8px;
  left: 8px;
  right: 8px;
  display: flex;
  gap: 4px;
  z-index: 10;
}

.progress-bar {
  flex: 1;
  height: 2px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 1px;
  overflow: hidden;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.progress-bar.active {
  background: rgba(255, 255, 255, 0.5);
}

.progress-bar:hover {
  background: rgba(255, 255, 255, 0.6);
}

.progress-fill {
  height: 100%;
  background: #ffffff;
  border-radius: 1px;
  transition: width 0.1s linear;
  box-shadow: 0 0 2px rgba(255, 255, 255, 0.8);
}

.fancy-video-parallelogram:hover {
  transform: scale(1.02);
  transition: transform 0.3s ease;
}

@media (max-width: 768px) {
  .stories-progress-container {
    top: 6px;
    left: 6px;
    right: 6px;
    gap: 3px;
  }
  
  .progress-bar {
    height: 1.5px;
  }
}

.stories-progress-container {
  display: flex;
  gap: 4px;
  padding: 12px;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  z-index: 10;
}

.progress-bar {
  flex: 1;
  height: 3px;
  background: rgba(255, 255, 255, 0.4);
  border-radius: 2px;
  overflow: hidden;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.progress-bar.active {
  background: rgba(255, 255, 255, 0.6);
}

.progress-bar.completed {
  background: rgba(255, 255, 255, 0.9);
}

.progress-fill {
  height: 100%;
  background: white;
  border-radius: 2px;
  transition: width 0.1s linear;
  transform-origin: left;
}

.video-banner-wrapper {
  position: relative;
  margin-bottom: 20px;
}

@media (max-width: 768px) {
  .banner-video,
  .banner-image {
    height: 180px;
  }
  
  .stories-progress-container {
    padding: 0 10px;
    top: calc(100% + 4px);
  }
}

@media (max-width: 480px) {
  .banner-video,
  .banner-image {
    height: 160px;
  }
  
  .stories-progress-container {
    padding: 0 8px;
    top: calc(100% + 3px);
  }
}
</style>