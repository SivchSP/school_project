<template>
  <section class="tasks-container">
    <div class="task-card">
      <div class="task-header">
        <div class="task-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2Z" fill="#FFC400"/>
            <path d="M16.59 7.58L10 14.17L7.41 11.59L6 13L10 17L18 9L16.59 7.58Z" fill="black"/>
          </svg>
        </div>
        <h3 class="task-title">Tasks</h3>
      </div>
      
      <div class="task-content">
        <!-- Premium ads at the top -->
        <div 
          v-for="task in premiumTasks" 
          :key="task.id"
          class="task-item premium-task"
          :class="{ 'premium-border': getTaskType(task) === 'premium advertising' }"
        >
          <div class="task-info">
            <div class="task-name">{{ task.description }}</div>
            <!-- Task-reward only for completed tasks -->
            <div v-if="isTaskCompleted(task.id)" class="task-reward">
              <span class="reward-amount">{{ formatNumber(task.price) }}</span>
              <span class="reward-currency">Drops</span>
            </div>
          </div>
          
          <!-- Success icon in the top right corner -->
          <div v-if="isTaskCompleted(task.id)" class="success-badge">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2Z" fill="#4CAF50"/>
              <path d="M10 17L5 12L6.41 10.59L10 14.17L17.59 6.58L19 8L10 17Z" fill="white"/>
            </svg>
          </div>
          
          <button
            v-if="!isTaskCompleted(task.id)"
            @click="handleTask(task)"
            class="task-button"
            :disabled="!currentAccount"
          >
            <span class="button-text">
              <span class="reward-number">{{ formatNumber(task.price) }}</span>
              <span class="drops-text">Drops</span>
            </span>
          </button>
        </div>

        <!-- Other tasks -->
        <div 
          v-for="task in regularTasks" 
          :key="task.id"
          class="task-item"
        >
          <div class="task-info">
            <div class="task-name">{{ task.description }}</div>
            <!-- Task-reward only for completed tasks -->
            <div v-if="isTaskCompleted(task.id)" class="task-reward">
              <span class="reward-amount">{{ formatNumber(task.price) }}</span>
              <span class="reward-currency">Drops</span>
            </div>
          </div>
          
          <!-- Success icon in the top right corner -->
          <div v-if="isTaskCompleted(task.id)" class="success-badge">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2Z" fill="#4CAF50"/>
              <path d="M10 17L5 12L6.41 10.59L10 14.17L17.59 6.58L19 8L10 17Z" fill="white"/>
            </svg>
          </div>
          
          <button
            v-if="!isTaskCompleted(task.id)"
            @click="handleTask(task)"
            class="task-button"
            :disabled="!currentAccount"
          >
            <span class="button-text">
              <span class="reward-number">{{ formatNumber(task.price) }}</span>
              <span class="drops-text">Drops</span>
            </span>
          </button>
        </div>
        
        <div v-if="loading" class="loading-message">
          Loading tasks...
        </div>
        
        <div v-if="tasks.length === 0 && !loading" class="no-tasks-message">
          No tasks available at the moment
        </div>
        
        <div v-if="message" class="message" :class="{ error: isError }">
          <div class="message-icon">
            <svg v-if="isError" width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM13 17H11V15H13V17ZM13 13H11V7H13V13Z" fill="currentColor"/>
            </svg>
            <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM10 17L5 12L6.41 10.59L10 14.17L17.59 6.58L19 8L10 17Z" fill="currentColor"/>
            </svg>
          </div>
          {{ message }}
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useScoreStore } from '@/stores/score';
import supabase from '../../services/supabase';

const scoreStore = useScoreStore();
const currentAccount = ref(null);
const tasks = ref([]);
const completedTasks = ref({});
const message = ref('');
const isError = ref(false);
const loading = ref(false);

// Computed properties for task separation
const premiumTasks = computed(() => {
  return tasks.value.filter(task => getTaskType(task) === 'premium advertising');
});

const regularTasks = computed(() => {
  return tasks.value.filter(task => getTaskType(task) !== 'premium advertising');
});

// Load tasks when component mounts
onMounted(async () => {
  if (scoreStore.currentAccount) {
    currentAccount.value = scoreStore.currentAccount;
    await loadTasks();
    await checkTasksStatus();
  }
});

// Load tasks from database
async function loadTasks() {
  try {
    loading.value = true;
    const { data, error } = await supabase
      .from('tasks')
      .select('*')
      .order('id', { ascending: true });

    if (error) throw error;
    
    tasks.value = data || [];
    console.log('Loaded tasks:', tasks.value); // For debugging
  } catch (error) {
    console.error('Error loading tasks:', error);
    showMessage('Error loading tasks', true);
  } finally {
    loading.value = false;
  }
}

// Get task type (handle array)
function getTaskType(task) {
  if (!task.type) return 'default';
  
  // If type is an array, take first element
  if (Array.isArray(task.type) && task.type.length > 0) {
    return task.type[0];
  }
  
  // If type is a JSONB object, extract value
  if (typeof task.type === 'object' && task.type.value) {
    return task.type.value;
  }
  
  // If type is a string
  if (typeof task.type === 'string') {
    return task.type;
  }
  
  return 'default';
}

// Get task link (handle array)
function getTaskLink(task) {
  if (!task.link) return null;
  
  // If link is an array, take first element
  if (Array.isArray(task.link) && task.link.length > 0) {
    return task.link[0];
  }
  
  // If link is a JSONB object, extract url
  if (typeof task.link === 'object' && task.link.url) {
    return task.link.url;
  }
  
  // If link is a string
  if (typeof task.link === 'string') {
    return task.link;
  }
  
  return null;
}

// Check task completion status
async function checkTasksStatus() {
  if (!currentAccount.value) return;

  try {
    const { data } = await supabase
      .from('users')
      .select('tasks')
      .eq('name', currentAccount.value.name)
      .single();

    completedTasks.value = data?.tasks || {};
  } catch (error) {
    console.error('Error checking tasks status:', error);
  }
}

// Check if task is completed
function isTaskCompleted(taskId) {
  return completedTasks.value[taskId] === true;
}

// Task completion handler
async function handleTask(task) {
  if (!currentAccount.value) {
    showMessage('Please log in first!', true);
    return;
  }

  try {
    const taskType = getTaskType(task);
    const taskLink = getTaskLink(task);

    console.log('Processing task:', { taskType, taskLink, task }); // For debugging

    // For tasks with links, open the link first
    if (taskLink) {
      // Open link in new window
      window.open(taskLink, '_blank', 'noopener,noreferrer');
      
      // Wait a bit before awarding the reward (user should navigate)
      showMessage('Navigating to link... Checking task completion.');
      
      // Give user time to navigate
      setTimeout(async () => {
        await completeTask(task);
      }, 1000);
    } else {
      // For regular tasks, award reward immediately
      await completeTask(task);
    }
    
  } catch (error) {
    console.error('Error completing task:', error);
    showMessage(error.message || 'Error completing task', true);
  }
}

// Complete task function and award reward
async function completeTask(task) {
  // Check if task is already completed
  if (isTaskCompleted(task.id)) {
    showMessage('You have already completed this task!');
    return;
  }

  try {
    // Get current user data
    const { data: userData, error: fetchError } = await supabase
      .from('users')
      .select('tasks, score')
      .eq('name', currentAccount.value.name)
      .single();

    if (fetchError) throw fetchError;
    if (!userData) throw new Error('User not found');

    // Double-check on server if task is completed
    if (userData.tasks?.[task.id]) {
      showMessage('You have already completed this task!');
      completedTasks.value[task.id] = true;
      return;
    }

    // Calculate new score
    const newScore = (userData.score || 0) + task.price;
    const updatedTasks = {
      ...(userData.tasks || {}),
      [task.id]: true
    };

    // Update data in database
    const { error: updateError } = await supabase
      .from('users')
      .update({
        tasks: updatedTasks,
        score: newScore
      })
      .eq('name', currentAccount.value.name);

    if (updateError) throw updateError;

    // Update local state
    scoreStore.setScore(newScore);
    completedTasks.value[task.id] = true;
    showMessage(`You received ${formatNumber(task.price)} Drops!`);
    
  } catch (error) {
    console.error('Error completing task:', error);
    throw error;
  }
}

// Format number with separators
function formatNumber(number) {
  return number?.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".") || '0';
}

// Show message
function showMessage(msg, error = false) {
  message.value = msg;
  isError.value = error;
  setTimeout(() => message.value = '', 3000);
}
</script>

<style scoped>
.tasks-container {
  max-width: 480px;
  margin: 0 auto;
  padding: 10px;
  width: 100%;
}

.task-card {
  background: #222222;
  border: 2px solid #ffc4001f;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
}

.task-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 24px 16px;
  background: linear-gradient(135deg, rgba(255, 196, 0, 0.1) 0%, rgba(255, 196, 0, 0.05) 100%);
  border-bottom: 1px solid #ffc4001f;
}

.task-icon {
  width: 40px;
  height: 40px;
  background: #ffc400;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.task-title {
  color: #ffc400;
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
  text-shadow: 0 2px 4px rgba(255, 196, 0, 0.3);
}

.task-content {
  padding: 24px;
}

.task-item {
  background: rgba(54, 54, 54, 0.726);
  border-radius: 25px;
  padding: 20px;
  margin-bottom: 16px;
  transition: all 0.3s ease;
  position: relative; /* For badge positioning */
}

.task-item.premium-border {
  border: 2px solid #ff9800 !important;
  box-shadow: 0 0px 8px rgba(255, 152, 0, 0.3);
}

.task-info {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  gap: 12px;
}

.task-name {
  color: white;
  font-weight: 600;
  font-size: 1.1rem;
  line-height: 1.4;
  flex: 1;
}

.task-reward {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 196, 0, 0.2);
  padding: 6px 12px;
  border-radius: 8px;
  border: 2px solid rgba(255, 196, 0, 0.527);
}

.reward-amount {
  color: #ffc400;
  font-weight: 700;
  font-size: 1.1rem;
}

.reward-currency {
  color: rgba(255, 196, 0, 0.8);
  font-weight: 600;
  font-size: 0.9rem;
}

/* Success badge in the top right corner */
.success-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 32px;
  height: 32px;
  background: #4CAF50;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.4);
  animation: popIn 0.3s ease;
}

@keyframes popIn {
  0% {
    transform: scale(0);
    opacity: 0;
  }
  70% {
    transform: scale(1.1);
    opacity: 1;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

.task-button {
  width: 100%;
  background: linear-gradient(135deg, #ffc400 0%, #ffb300 100%);
  color: black;
  border: none;
  padding: 14px 20px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  border-radius: 20px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  box-shadow: 0 4px 12px rgba(255, 196, 0, 0.3);
}

.task-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(255, 196, 0, 0.4);
  background: linear-gradient(135deg, #ffca28 0%, #ffc400 100%);
}

.task-button:active:not(:disabled) {
  transform: translateY(0);
}

.task-button:disabled {
  cursor: not-allowed;
  opacity: 0.7;
  transform: none;
  box-shadow: none;
}

.task-button.link-button:not(.completed) {
  background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
  box-shadow: 0 4px 12px rgba(33, 150, 243, 0.3);
}

.task-button.link-button:not(.completed):hover:not(:disabled) {
  background: linear-gradient(135deg, #42A5F5 0%, #1E88E5 100%);
  box-shadow: 0 6px 16px rgba(33, 150, 243, 0.4);
}

.button-text {
  display: flex;
  align-items: center;
  gap: 6px;
}

.message {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.9rem;
  background: rgba(0, 146, 5, 0.1);
  border: 1px solid rgba(0, 146, 5, 0.3);
  color: #4caf50;
  animation: slideIn 0.3s ease;
}

.message.error {
  background: rgba(244, 67, 54, 0.1);
  border: 1px solid rgba(244, 67, 54, 0.3);
  color: #f44336;
}

.message-icon {
  display: flex;
  align-items: center;
}

.loading-message,
.no-tasks-message {
  text-align: center;
  padding: 20px;
  color: rgba(255, 255, 255, 0.7);
  font-style: italic;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 480px) {
  .tasks-container {
    padding: 16px;
  }
  
  .task-content {
    padding: 16px;
  }
  
  .task-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .task-reward {
    align-self: flex-start;
  }
  
  .success-badge {
    top: 10px;
    right: 10px;
    width: 28px;
    height: 28px;
  }
}
</style>