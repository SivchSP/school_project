import supabase from '../services/supabase'
import { useScoreStore } from '@/stores/score'
import { useTelegram } from '../services/telegram'
const { user } = useTelegram()

export const MY_ID = user?.id ?? 4252

export async function fetchTasks() {
  const { data } = await supabase.from('tasks').select('*')
  return data
}


export async function getOrCreateUser() {
  const pontentialUser = await supabase
    .from('users')
    .select()
    .eq('telegram', MY_ID)

  if (pontentialUser.data.length !== 0) {
    return pontentialUser.data[0]
  }

  const newUser = {
    telegram: MY_ID,
    friends: {},
    tasks: {},
    score: 0,
    available_clicks: 100,
    maxClicks: 100,
    pensia_task: {},
    name:{},
    password: {},
    register: {},
    nft1: 0,
    nft2: 0,
    nft3: 0,
    nft4: 0,
    nft5: 0,
    nft6: 0,
    nft7: 0,
    nft8: 0,
    nft9: 0,
    nft10: 0,
    owner_id: {},
    sales_history: [],
    transfers_history: [],
    market_history: [],
    score_click: 1,
    boost: 0

  }

  await supabase.from('users').insert(newUser)
  return newUser
}
// Добавим новую функцию для получения данных пользователя по имени
export async function getUserByName(username) {
  const { data, error } = await supabase
    .from('users')
    .select('*')
    .eq('name', username)
    .single()

  if (error) throw error
  return data
}

// Обновим функцию updateScoreClick
export async function updateBoost(username, newBoost) {
  try {
    const { error } = await supabase
      .from('users')
      .update({ 
        boost: newBoost
      })
      .eq('name', username)

    if (error) throw error
    return true
  } catch (error) {
    console.error('Error updating boost:', error)
    return false
  }
}

export async function updateScore(score, username) {
  try {
    const { error } = await supabase
      .from('users')
      .update({ score })
      .eq('name', username)
      
    if (error) throw error
    console.log('Счет успешно обновлен для пользователя:', username)
  } catch (error) {
    console.error('Ошибка при обновлении счета:', error)
  }
}

export async function registerRef(userName, refId) {
  // 1. Получаем данные реферера
  const { data: refData } = await supabase
    .from('users')
    .select('friends, score')
    .eq('telegram', +refId)
    .single(); // Используем single() для получения одной записи

  if (!refData) return; // Если пользователь не найден, выходим

  // 2. Проверяем, есть ли текущий пользователь уже в друзьях
  const friends = refData.friends || {}; // Если friends null, создаем пустой объект
  
  // Проверяем по MY_ID (если у вас друзья хранятся как { "id123": "name" })
  if (friends[MY_ID]) {
    console.log('Пользователь уже был добавлен в друзья ранее');
    return;
  }

  // 3. Добавляем в друзья и начисляем бонус (только если друга не было)
  const { error } = await supabase
    .from('users')
    .update({
      friends: { ...friends, [MY_ID]: userName },
      score: refData.score + 10000,
    })
    .eq('telegram', +refId);

  if (error) {
    console.error('Ошибка при обновлении данных:', error);
  }
}

export async function completeTaskGetMoney(user, username) {
  try {
      // Получаем текущий счет пользователя
      const { data: userData, error: fetchError } = await supabase
          .from('users')
          .select('score, pensia_task')
          .eq('name', username)
          .single();

      if (fetchError) throw fetchError;

      // Проверяем, выполнено ли уже задание
      if (userData.pensia_task && userData.pensia_task["1"] === true) {
          throw new Error('Это задание уже выполнено');
      }

      // Обновляем счет и статус задания
      const scoreStore = useScoreStore();
      const reward = 25000;
      const newScore = (userData.score || 0) + reward;
      
      // Обновляем хранилище
      scoreStore.setScore(newScore);
      
      // Обновляем данные в базе
      const { error: updateError } = await supabase
          .from('users')
          .update({
              pensia_task: { ...(userData.pensia_task || {}), 1: true },
              score: newScore
          })
          .eq('name', username);

      if (updateError) throw updateError;

      return newScore;
  } catch (error) {
      console.error('Ошибка при начислении вознаграждения:', error);
      throw error;
  }
}
export async function completeTask(task, username) {
  try {
    // 1. Получаем текущие данные пользователя
    const { data: userData, error: fetchError } = await supabase
      .from('users')
      .select('tasks, score')
      .eq('name', username)
      .single();

    if (fetchError) throw fetchError;
    if (!userData) throw new Error('Пользователь не найден');

    // 2. Проверяем, не выполнено ли уже задание
    if (userData.tasks?.[task.id]) {
      throw new Error('Это задание уже выполнено');
    }

    // 3. Рассчитываем новый счет
    const newScore = (userData.score || 0) + task.amount;
    const updatedTasks = {
      ...(userData.tasks || {}),
      [task.id]: true
    };

    // 4. Обновляем данные в базе
    const { error: updateError } = await supabase
      .from('users')
      .update({
        tasks: updatedTasks,
        score: newScore
      })
      .eq('name', username);

    if (updateError) throw updateError;

    // 5. Возвращаем обновленные данные
    return { newScore, updatedTasks };
  } catch (error) {
    console.error('Ошибка выполнения задания:', error);
    throw error;
  }
}
export async function completeFirstTask(username) {
  const { data: userData, error: fetchError } = await supabase
    .from('users')
    .select('tasks, score')
    .eq('name', username)
    .single();

  if (fetchError) throw fetchError;
  if (!userData) throw new Error('Пользователь не найден');

  // Проверяем, выполнено ли уже задание
  if (userData.tasks && userData.tasks["1"] === true) {
    return { alreadyCompleted: true };
  }

  // Начисляем 10000 очков и отмечаем задание выполненным
  const newScore = (userData.score || 0) + 30000;
  const updatedTasks = { "1": true };

  const { error: updateError } = await supabase
    .from('users')
    .update({
      tasks: updatedTasks,
      score: newScore
    })
    .eq('name', username);

  if (updateError) throw updateError;

  return { newScore, updatedTasks };
}