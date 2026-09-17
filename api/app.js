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
  // 1. Пытаемся найти пользователя
  const { data, error } = await supabase
    .from('users')
    .select('*')
    .eq('telegram', MY_ID);

  if (error) {
    console.error('Ошибка при поиске пользователя:', error);
    throw error; // Можно обработать иначе, если нужно
  }

  // 2. Если пользователь найден — возвращаем его
  if (data && data.length > 0) {
    return data[0];
  }

  // 3. Если пользователя нет — создаём нового
  const newUser = {
    id:0,
    telegram: MY_ID,
    friends: {},
    tasks: {},
    score: 0,
    available_clicks: 100,
    maxclicks: 100,
    pensia_task: {},
    name: null,
    password: null,
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
    boost: 0,
    boost_1: false,
    boost_2: false,
    boost_3: false,
    boost_4: false,
    boost_5: false,
    last_click_update: "2025-01-01 00:00:00.031+00",
    ton_balance: 0,
    nft_links: [],
  };

  // 4. Сохраняем нового пользователя в базу
  const { error: insertError } = await supabase.from('users').insert(newUser);

  if (insertError) {
    console.error('Ошибка при создании пользователя:', insertError);
    throw insertError;
  }

  return newUser;
}

// НОВАЯ ФУНКЦИЯ: Получение или создание пользователя по Telegram ID
export async function getOrCreateUserByTelegramId(telegramId) {
  try {
    // 1. Пытаемся найти пользователя по telegram ID
    const { data: existingUsers, error: searchError } = await supabase
      .from('users')
      .select('*')
      .eq('telegram', telegramId);

    if (searchError) {
      console.error('Ошибка при поиске пользователя:', searchError);
      throw searchError;
    }

    // 2. Если пользователь найден — возвращаем его
    if (existingUsers && existingUsers.length > 0) {
      console.log('Пользователь найден:', existingUsers[0]);
      return existingUsers[0];
    }

    // 3. Если пользователя нет — создаём нового
    const newUser = {
      telegram: telegramId,
      friends: {},
      tasks: {},
      score: 0,
      available_clicks: 100,
      maxclicks: 100,
      pensia_task: {},
      name: `user_${telegramId}`,
      password: null,
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
      boost: 0,
      boost_1: false,
      boost_2: false,
      boost_3: false,
      boost_4: false,
      boost_5: false,
      last_click_update: "2025-01-01 00:00:00.031+00",
      ton_balance: 0,
      nft_links: [],
    };

    // 4. Сохраняем нового пользователя в базу
    const { data: createdUser, error: insertError } = await supabase
      .from('users')
      .insert([newUser])
      .select()
      .single();

    if (insertError) {
      console.error('Ошибка при создании пользователя:', insertError);
      throw insertError;
    }

    console.log('Новый пользователь создан:', createdUser);
    return createdUser;
  } catch (error) {
    console.error('Ошибка в getOrCreateUserByTelegramId:', error);
    throw error;
  }
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
    const { data, error } = await supabase
      .from('users')
      .update({ score })
      .eq('name', username)
      .select('*') // ДОБАВЬТЕ ЭТО - возвращаем все поля
      
    if (error) throw error
    console.log('Счет успешно обновлен для пользователя:', username, 'with boost:', data[0]?.boost)
    return data[0] // Возвращаем обновленные данные
  } catch (error) {
    console.error('Ошибка при обновлении счета:', error)
    throw error
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