// services/tonWithdraw.js
import { TonClient, internal, toNano } from '@ton/ton';
import { mnemonicToPrivateKey, sign } from '@ton/crypto';
import { Cell, SendMode, storeMessageRelaxed, beginCell } from '@ton/core';
import { HighloadWalletV3 } from '../wrappers/HighloadWalletV3';
import { HighloadQueryId } from '../wrappers/HighloadQueryId';
import supabase from './supabase.js';

// ============ ФУНКЦИЯ ДЛЯ ПОЛУЧЕНИЯ КОНФИГА С СЕРВЕРА ============
let cachedConfig = null;
let isConfigLoaded = false;

async function fetchConfig() {
    if (cachedConfig) return cachedConfig;
    
    try {
        console.log('📡 Fetching config from /api/debug-env...');
        
        // Определяем базовый URL для Vercel
        const baseUrl = process.env.VERCEL_URL 
            ? `https://${process.env.VERCEL_URL}`
            : (process.env.NODE_ENV === 'development' ? 'http://localhost:3000' : '');
        
        const url = `${baseUrl}/api/debug-env`;
        console.log(`📍 Request URL: ${url}`);
        
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success && data.environment) {
            cachedConfig = data.environment;
            console.log('✅ Config fetched successfully');
            return cachedConfig;
        } else {
            throw new Error('Invalid response format');
        }
    } catch (error) {
        console.error('❌ Failed to fetch config:', error.message);
        return null;
    }
}

// ============ ПЕРЕМЕННЫЕ (будут заполнены асинхронно) ============
let MNEMONIC = null;
let SUBWALLET_ID = null;
let TIMEOUT = null;
let ENDPOINT = null;
let API_KEY = null;
let CODE_HEX = null;
let TELEGRAM_BOT_TOKEN = null;
let CODE = null;
let MAX_QUERY_SEQNO = 2 ** 23 - 1; // Максимальное значение для query_id
let FEE_PER_MESSAGE = 5000000n; // Комиссия за сообщение (0.005 TON)

// Функция для загрузки конфигурации (вызывать перед использованием)
async function ensureConfig() {
    if (isConfigLoaded && MNEMONIC && CODE) return true;
    
    console.log('🔄 Loading configuration from API...');
    
    const config = await fetchConfig();
    if (!config) {
        console.error('❌ Failed to load configuration');
        return false;
    }
    
    // Присваиваем переменные из полученного конфига
    MNEMONIC = config.CONTRACT_MNEMONIC && config.CONTRACT_MNEMONIC !== 'NOT SET' 
        ? config.CONTRACT_MNEMONIC 
        : null;
    
    SUBWALLET_ID = config.CONTRACT_SUBWALLET_ID && config.CONTRACT_SUBWALLET_ID !== 'NOT SET' 
        ? parseInt(config.CONTRACT_SUBWALLET_ID) 
        : 0;
    
    TIMEOUT = config.CONTRACT_TIMEOUT && config.CONTRACT_TIMEOUT !== 'NOT SET' 
        ? parseInt(config.CONTRACT_TIMEOUT) 
        : 3600;
    
    ENDPOINT = config.CONTRACT_ENDPOINT && config.CONTRACT_ENDPOINT !== 'NOT SET' 
        ? config.CONTRACT_ENDPOINT 
        : 'https://toncenter.com/api/v2/jsonRPC';
    
    API_KEY = config.API_KEY_TG && config.API_KEY_TG !== 'NOT SET' 
        ? config.API_KEY_TG 
        : null;
    
    CODE_HEX = config.CODE_HEX && config.CODE_HEX !== 'NOT SET' 
        ? config.CODE_HEX 
        : null;
    
    TELEGRAM_BOT_TOKEN = config.TELEGRAM_TOKEN && config.TELEGRAM_TOKEN !== 'NOT SET' 
        ? config.TELEGRAM_TOKEN 
        : null;
    
    // Создаем CODE из CODE_HEX
    if (CODE_HEX) {
        try {
            CODE = Cell.fromHex(CODE_HEX);
            console.log('✅ CODE created from CODE_HEX');
        } catch (error) {
            console.error('❌ Error creating CODE from CODE_HEX:', error);
            CODE = null;
        }
    }
    
    // Проверяем обязательные переменные
    if (!MNEMONIC) {
        console.error('❌ CONTRACT_MNEMONIC is not set!');
        return false;
    }
    
    if (!CODE) {
        console.error('❌ CODE_HEX is not set or invalid!');
        return false;
    }
    
    isConfigLoaded = true;
    
    console.log('✅ Configuration loaded successfully:');
    console.log(`   - MNEMONIC: ${MNEMONIC.split(' ').length} words`);
    console.log(`   - SUBWALLET_ID: ${SUBWALLET_ID}`);
    console.log(`   - TIMEOUT: ${TIMEOUT}`);
    console.log(`   - ENDPOINT: ${ENDPOINT}`);
    console.log(`   - API_KEY: ${API_KEY ? 'SET' : 'NOT SET'}`);
    console.log(`   - TELEGRAM_TOKEN: ${TELEGRAM_BOT_TOKEN ? 'SET' : 'NOT SET'}`);
    
    return true;
}

// ============ ДЕБАГ: ВЫВОД ПЕРЕМЕННЫХ ПРИ ЗАГРУЗКЕ ============


// Вызываем дебаг функцию при загрузке модуля (асинхронно)
(async () => {
    console.log('🚀 TON Withdraw module loading...');
    await debugEnvironment();
    await ensureConfig();
})();

console.log('✅ TON Withdraw loaded with config from API');

// Проверка
if (!MNEMONIC) {
    console.error('❌ MNEMONIC is undefined in tonWithdraw.js (will be loaded async)');
}

const QUEUE_CONFIG = {
    BATCH_SIZE: 3,
    BATCH_TIMEOUT_MS: 10000,
    MIN_BATCH_SIZE: 2,
};

let keyPair = null;
let client = null;
let highloadWallet = null;
let isInitialized = false;
let lastCreatedAt = 0;
let pollingInterval = null;

// ============ ФУНКЦИЯ ДЛЯ ОТПРАВКИ УВЕДОМЛЕНИЯ В TELEGRAM ============

/**
 * Получает telegram_id пользователя из таблицы users по его username (varchar)
 * @param {string} username - Имя пользователя (из таблицы users, поле name)
 * @returns {Promise<string|null>} - telegram_id или null
 */
async function getUserTelegramId(username) {
    try {
        console.log(`🔍 Поиск telegram_id для username: ${username}`);
        
        const { data, error } = await supabase
            .from('users')
            .select('telegram')
            .eq('name', username)
            .maybeSingle();
        
        if (error) {
            console.error(`❌ Ошибка получения telegram_id:`, error.message);
            return null;
        }
        
        if (!data) {
            console.log(`⚠️ Пользователь с name="${username}" не найден в таблице users`);
            return null;
        }
        
        const telegramId = data.telegram;
        console.log(`📊 Значение telegram из БД: ${telegramId}`);
        
        if (!telegramId) {
            console.log(`⚠️ У пользователя ${username} не заполнено поле telegram`);
            return null;
        }
        
        const telegramIdStr = String(telegramId);
        console.log(`✅ Найден telegram_id: ${telegramIdStr} для username ${username}`);
        
        return telegramIdStr;
        
    } catch (error) {
        console.error(`❌ Исключение при запросе telegram_id:`, error.message);
        return null;
    }
}

/**
 * Получает language_code пользователя из таблицы users по его telegram_id
 * @param {string} telegramId - Telegram ID пользователя
 * @returns {Promise<string>} - language_code ('ru' или 'en', по умолчанию 'ru')
 */
async function getUserLanguageCode(telegramId) {
    try {
        console.log(`🔍 Поиск language_code для telegram_id: ${telegramId}`);
        
        const { data, error } = await supabase
            .from('users')
            .select('language_code')
            .eq('telegram', telegramId)
            .maybeSingle();
        
        if (error) {
            console.error(`❌ Ошибка получения language_code:`, error.message);
            return 'ru';
        }
        
        if (!data || !data.language_code) {
            console.log(`⚠️ Пользователь с telegram=${telegramId} не найден или language_code не указан, используем 'ru'`);
            return 'ru';
        }
        
        const languageCode = data.language_code;
        console.log(`✅ Найден language_code: ${languageCode} для telegram_id ${telegramId}`);
        
        return languageCode;
        
    } catch (error) {
        console.error(`❌ Исключение при запросе language_code:`, error.message);
        return 'ru';
    }
}

/**
 * Отправляет пользователю уведомление об успешном выводе средств
 * @param {string} telegramId - Telegram ID пользователя
 * @param {number|string} amount - Сумма вывода в TON
 * @param {string} txHash - Хэш транзакции
 * @returns {Promise<boolean>} - Успех отправки
 */
async function sendTelegramNotification(telegramId, amount, txHash) {
    try {
        await ensureConfig();
        
        if (!TELEGRAM_BOT_TOKEN) {
            console.error('❌ TELEGRAM_BOT_TOKEN не установлен!');
            return false;
        }
        
        console.log(`📤 =========== ОТПРАВКА УВЕДОМЛЕНИЯ О ВЫВОДЕ ===========`);
        console.log(`👤 Telegram ID: ${telegramId}`);
        console.log(`💰 Сумма: ${amount} TON`);
        console.log(`🔗 Tx Hash: ${txHash}`);
        
        // Получаем язык пользователя из базы данных
        const languageCode = await getUserLanguageCode(telegramId);
        console.log(`🌐 Язык пользователя: ${languageCode}`);
        
        const txUrl = `https://tonscan.org/tx/${txHash}`;
        
        let messageText;
        
        // Проверяем язык
        const isRussian = languageCode === 'ru';
        
        if (isRussian) {
            messageText = `💸 *Вывод средств*\n\n` +
                         `💰 Сумма: *${amount} TON*\n` +
                         `🔗 [Ссылка на транзакцию](${txUrl})\n\n` +
                         `✨ Средства успешно выведены!`;
        } else {
            messageText = `💸 *Withdrawal*\n\n` +
                         `💰 Amount: *${amount} TON*\n` +
                         `🔗 [Transaction link](${txUrl})\n\n` +
                         `✨ Funds successfully withdrawn!`;
        }
        
        console.log(`📝 Текст сообщения:\n${messageText}`);
        
        const telegramUrl = `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`;
        
        const payload = {
            chat_id: String(telegramId),
            text: messageText,
            parse_mode: 'Markdown',
        };
        
        const response = await fetch(telegramUrl, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            console.log(`✅ Уведомление успешно отправлено!`);
            return true;
        } else {
            console.error(`❌ Ошибка Telegram API:`, result.description);
            return false;
        }
    } catch (error) {
        console.error(`❌ Ошибка при отправке уведомления:`, error.message);
        return false;
    }
}

// ============ ФУНКЦИЯ ДЛЯ ПОЛУЧЕНИЯ ХЭША ИЗ EXTERNAL MESSAGE ============

function getTxHashFromExternalMessage(externalMessageCell) {
    const hashBuffer = externalMessageCell.hash();
    const txHashHex = Buffer.from(hashBuffer).toString('hex');
    return txHashHex;
}

async function createExternalMessageAndGetHash(message, queryId, createdAt) {
    let messageCell;
    
    if (message instanceof Cell) {
        messageCell = message;
    } else {
        const messageBuilder = beginCell();
        messageBuilder.store(storeMessageRelaxed(message));
        messageCell = messageBuilder.endCell();
    }
    
    const messageInner = beginCell()
        .storeUint(SUBWALLET_ID, 32)
        .storeRef(messageCell)
        .storeUint(SendMode.PAY_GAS_SEPARATELY, 8)
        .storeUint(queryId.getQueryId(), 23)
        .storeUint(createdAt, 64)
        .storeUint(TIMEOUT, 22)
        .endCell();
    
    const signature = sign(messageInner.hash(), keyPair.secretKey);
    
    const externalMessageCell = beginCell()
        .storeBuffer(signature)
        .storeRef(messageInner)
        .endCell();
    
    const txHash = getTxHashFromExternalMessage(externalMessageCell);
    
    return { externalMessageCell, txHash };
}

// ============ РАБОТА С БД ============

async function addToGlobalQueue(userId, userName, address, amount) {
    const amountNum = Number(amount);
    
    console.log(`📝 addToGlobalQueue: userId=${userId}, userName=${userName}, amount=${amountNum}`);
    
    if (isNaN(amountNum) || amountNum <= 0) {
        throw new Error(`Invalid amount: ${amount}. Must be a positive number.`);
    }
    
    const { data, error } = await supabase
        .from('withdraw_queue')
        .insert({
            user_id: String(userId),
            user_name: String(userName),
            address: String(address),
            amount: amountNum,
            status: 'pending'
        })
        .select('id')
        .single();
    
    if (error) throw error;
    return data.id;
}

async function getNextSeqno() {
    const { data: current, error: readError } = await supabase
        .from('global_counter')
        .select('value')
        .eq('id', 1)
        .single();
    
    if (readError) throw readError;
    
    let newSeqno = current.value + 1;
    if (newSeqno > Number(MAX_QUERY_SEQNO)) {
        newSeqno = 17;
    }
    
    await supabase
        .from('global_counter')
        .update({ value: newSeqno })
        .eq('id', 1);
    
    return current.value;
}

async function getAndLockPendingItems() {
    const { data: items, error } = await supabase
        .from('withdraw_queue')
        .select('*')
        .eq('status', 'pending')
        .order('created_at', { ascending: true })
        .limit(10);
    
    if (error) throw error;
    if (items.length === 0) return [];
    
    const ids = items.map(i => i.id);
    await supabase
        .from('withdraw_queue')
        .update({ status: 'processing', processed_at: new Date().toISOString() })
        .in('id', ids);
    
    return items;
}

// НОВАЯ ФУНКЦИЯ ДЛЯ УДАЛЕНИЯ ЗАПИСИ ИЗ ОЧЕРЕДИ
async function deleteFromQueue(id) {
    try {
        console.log(`🗑️ Удаление записи ${id} из очереди...`);
        
        const { error } = await supabase
            .from('withdraw_queue')
            .delete()
            .eq('id', id);
        
        if (error) {
            console.error(`❌ Ошибка удаления записи ${id}:`, error.message);
            return false;
        }
        
        console.log(`✅ Запись ${id} успешно удалена из очереди`);
        return true;
    } catch (error) {
        console.error(`❌ Ошибка при удалении записи ${id}:`, error.message);
        return false;
    }
}

// ОБНОВЛЕННАЯ ФУНКЦИЯ markAsCompleted - отправляет уведомление и УДАЛЯЕТ запись
async function markAsCompleted(id, txHash, amount, userName) {
    console.log(`📝 markAsCompleted: id=${id}, userName=${userName}, amount=${amount}, txHash=${txHash}`);
    
    // Сначала отправляем уведомление (пока запись еще есть в БД)
    let notificationSent = false;
    
    if (userName && txHash && amount) {
        console.log(`📨 Попытка отправить уведомление для userName=${userName}, amount=${amount}`);
        
        const telegramId = await getUserTelegramId(userName);
        
        if (telegramId) {
            notificationSent = await sendTelegramNotification(telegramId, amount, txHash);
            if (notificationSent) {
                console.log(`✅ Уведомление успешно отправлено!`);
            } else {
                console.log(`⚠️ Не удалось отправить уведомление пользователю ${telegramId}`);
            }
        } else {
            console.log(`⚠️ Не найден telegram_id для userName=${userName}`);
        }
    } else {
        console.log(`⚠️ Пропущена отправка уведомления: userName=${userName}, txHash=${txHash}, amount=${amount}`);
    }
    
    // Удаляем запись из очереди (независимо от успеха уведомления)
    const deleted = await deleteFromQueue(id);
    
    if (deleted) {
        console.log(`✅ Операция завершена: запись ${id} удалена`);
    } else {
        // Если не удалось удалить, хотя бы обновим статус
        console.log(`⚠️ Не удалось удалить запись ${id}, обновляем статус...`);
        const { error: updateError } = await supabase
            .from('withdraw_queue')
            .update({ status: 'completed', tx_hash: txHash })
            .eq('id', id);
        
        if (updateError) {
            console.error(`❌ Ошибка обновления статуса:`, updateError);
        }
    }
}

async function markAsFailed(id, errorMsg) {
    console.log(`❌ markAsFailed: id=${id}, error=${errorMsg}`);
    
    // При ошибке просто обновляем статус, не удаляем
    const { error: updateError } = await supabase
        .from('withdraw_queue')
        .update({ status: 'failed', error: errorMsg })
        .eq('id', id);
    
    if (updateError) {
        console.error(`❌ Ошибка обновления статуса:`, updateError);
    }
}

// ============ ОСНОВНЫЕ ФУНКЦИИ ============

function getUniqueCreatedAt() {
    let now = Math.floor(Date.now() / 1000);
    if (now <= lastCreatedAt) {
        now = lastCreatedAt + 1;
    }
    lastCreatedAt = now;
    return now - 30;
}

async function init() {
    // Убеждаемся что конфиг загружен
    await ensureConfig();
    
    if (isInitialized && highloadWallet) return highloadWallet;
    
    try {
        console.log('🔧 Инициализация Highload Wallet...');
        
        if (!MNEMONIC) {
            throw new Error('MNEMONIC не загружена!');
        }
        
        if (!CODE) {
            throw new Error('CODE не создан! Проверьте CODE_HEX');
        }
        
        const mnemonic = MNEMONIC.split(' ');
        keyPair = await mnemonicToPrivateKey(mnemonic);
        
        client = new TonClient({
            endpoint: ENDPOINT,
            apiKey: API_KEY,
        });
        
        highloadWallet = client.open(
            HighloadWalletV3.createFromConfig(
                {
                    publicKey: keyPair.publicKey,
                    subwalletId: SUBWALLET_ID,
                    timeout: TIMEOUT,
                },
                CODE
            )
        );
        
        isInitialized = true;
        console.log(`✅ Highload Wallet: ${highloadWallet.address.toString()}`);
        
        return highloadWallet;
    } catch (error) {
        console.error('❌ Ошибка инициализации:', error);
        throw error;
    }
}

async function sendSingleWithdraw(address, amount, userId, userName, queueId) {
    try {
        await init();
        
        const createdAt = getUniqueCreatedAt();
        const seqno = await getNextSeqno();
        const queryId = HighloadQueryId.fromSeqno(BigInt(seqno));
        
        console.log(`📤 Одиночный перевод ${amount} TON для ${userName}`);
        
        const internalMessage = internal({
            to: address,
            value: toNano(amount.toString()),
            bounce: false,
        });
        
        await highloadWallet.sendExternalMessage(keyPair.secretKey, {
            message: internalMessage,
            mode: SendMode.PAY_GAS_SEPARATELY,
            query_id: queryId,
            createdAt: createdAt,
            subwalletId: SUBWALLET_ID,
            timeout: TIMEOUT,
        });
        
        console.log(`⏳ Ждем 5 секунд перед получением хэша...`);
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        const txHashHex = await getLastTransactionHash(highloadWallet.address.toString());
        
        if (txHashHex) {
            console.log(`🔗 Tx hash: ${txHashHex}`);
            console.log(`🔍 Ссылка: https://tonscan.org/tx/${txHashHex}`);
            await markAsCompleted(queueId, txHashHex, amount, userName);
        } else {
            console.log(`⚠️ Не удалось получить хэш, используем fallback`);
            const fallbackHash = `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            await markAsCompleted(queueId, fallbackHash, amount, userName);
        }
        
        console.log(`✅ Перевод отправлен!`);
        return { success: true, txHash: txHashHex };
    } catch (error) {
        console.error('❌ Ошибка:', error);
        await markAsFailed(queueId, error.message);
        return { success: false, error: error.message };
    }
}

async function getLastTransactionHash(walletAddress) {
    try {
        const response = await fetch(
            `https://toncenter.com/api/v2/getTransactions?address=${walletAddress}&limit=1`
        );
        const data = await response.json();
        
        if (data.ok && data.result && data.result[0]) {
            return data.result[0].transaction_id.hash;
        }
        return null;
    } catch (error) {
        console.error('Ошибка получения хэша:', error);
        return null;
    }
}

async function sendBatchWithdraw(items) {
    try {
        await init();
        
        const createdAt = getUniqueCreatedAt();
        const seqno = await getNextSeqno();
        const queryId = HighloadQueryId.fromSeqno(BigInt(seqno));
        
        let totalAmount = 0n;
        for (const item of items) {
            totalAmount += toNano(item.amount.toString());
        }
        
        const totalFee = FEE_PER_MESSAGE * BigInt(items.length);
        const totalToSend = totalAmount + totalFee;
        
        console.log(`📦 BATCH из ${items.length} переводов`);
        
        const batchMessages = items.map((item) => ({
            type: 'sendMsg',
            mode: SendMode.PAY_GAS_SEPARATELY,
            outMsg: internal({
                to: item.address,
                value: toNano(item.amount.toString()),
                bounce: false,
            }),
        }));
        
        await highloadWallet.sendBatch(
            keyPair.secretKey,
            batchMessages,
            SUBWALLET_ID,
            queryId,
            TIMEOUT,
            createdAt,
            totalToSend
        );
        
        console.log(`⏳ Ждем 5 секунд перед получением хэша...`);
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        const txHashHex = await getLastTransactionHash(highloadWallet.address.toString());
        
        if (txHashHex) {
            console.log(`🔗 Tx hash: ${txHashHex}`);
            console.log(`🔍 Ссылка: https://tonscan.org/tx/${txHashHex}`);
            
            for (const item of items) {
                console.log(`📨 Отправка уведомления для ${item.user_name}`);
                await markAsCompleted(item.id, txHashHex, item.amount, item.user_name);
            }
        } else {
            console.log(`⚠️ Не удалось получить хэш`);
            const fallbackHash = `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            for (const item of items) {
                await markAsCompleted(item.id, fallbackHash, item.amount, item.user_name);
            }
        }
        
        console.log(`✅ Batch отправлен!`);
        return { success: true, txHash: txHashHex };
    } catch (error) {
        console.error('❌ Ошибка batch:', error);
        for (const item of items) {
            await markAsFailed(item.id, error.message);
        }
        return { success: false, error: error.message };
    }
}

// ============ ПРОЦЕССОР ОЧЕРЕДИ ============
let currentTimer = null;
let pendingCount = 0;

async function processGlobalQueue() {
    // Теперь считаем ТОЛЬКО записи со статусом 'pending' (не 'processing')
    const { count, error } = await supabase
        .from('withdraw_queue')
        .select('*', { count: 'exact', head: true })
        .eq('status', 'pending');
    
    if (error) throw error;
    
    if (count === 0) {
        pendingCount = 0;
        if (currentTimer) {
            clearTimeout(currentTimer);
            currentTimer = null;
        }
        return;
    }
    
    if (count > pendingCount) {
        console.log(`📥 Запросов в очереди: ${count}`);
        pendingCount = count;
        
        if (currentTimer) {
            clearTimeout(currentTimer);
        }
        
        currentTimer = setTimeout(async () => {
            const items = await getAndLockPendingItems();
            if (items.length === 0) return;
            
            if (items.length === 1) {
                await sendSingleWithdraw(items[0].address, items[0].amount, items[0].user_id, items[0].user_name, items[0].id);
            } else {
                await sendBatchWithdraw(items);
            }
            
            pendingCount = 0;
            currentTimer = null;
        }, QUEUE_CONFIG.BATCH_TIMEOUT_MS);
    }
}

function startQueueProcessor() {
    if (pollingInterval) clearInterval(pollingInterval);
    
    pollingInterval = setInterval(async () => {
        try {
            await processGlobalQueue();
        } catch (error) {
            console.error('Ошибка процессора:', error);
        }
    }, 2000);
    
    console.log('🔄 Глобальный процессор очереди запущен');
}

// ============ ЭКСПОРТ ============

export async function sendWithdrawTransaction(userId, userName, address, amount) {
    await ensureConfig();
    const amountNum = typeof amount === 'number' ? amount : parseFloat(amount);
    const queueId = await addToGlobalQueue(userId, userName, address, amountNum);
    console.log(`✅ Запрос добавлен в очередь (ID: ${queueId})`);
    return { success: true, queueId };
}

export async function getQueueStatus() {
    // Возвращаем только записи со статусом 'pending'
    const { data, error } = await supabase
        .from('withdraw_queue')
        .select('id, user_name, amount, status, created_at')
        .eq('status', 'pending')
        .order('created_at', { ascending: true });
    
    if (error) throw error;
    return { queueLength: data.length, items: data };
}

export async function getHighloadWalletBalance() {
    try {
        await init();
        const balance = await client.getBalance(highloadWallet.address);
        return Number(balance) / 1e9;
    } catch (error) {
        console.error('Ошибка получения баланса:', error);
        return 0;
    }
}

export async function initWithdrawSystem() {
    try {
        await ensureConfig();
        await init();
        const balance = await getHighloadWalletBalance();
        startQueueProcessor();
        console.log(`✅ Система вывода инициализирована. Баланс: ${balance} TON`);
        return true;
    } catch (error) {
        console.error('❌ Ошибка инициализации системы:', error);
        return false;
    }
}

export function shutdown() {
    if (pollingInterval) {
        clearInterval(pollingInterval);
        pollingInterval = null;
    }
    console.log('🛑 Система вывода остановлена');
}

// Экспортируем функцию для принудительной перезагрузки конфига
export async function reloadConfig() {
    cachedConfig = null;
    isConfigLoaded = false;
    MNEMONIC = null;
    CODE = null;
    return await ensureConfig();
}