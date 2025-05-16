import telebot
from telebot import types
import random
import string
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from supabase import create_client, Client  # Импортируем библиотеку Supabase

# Токен вашего бота
TOKEN = '8181445961:AAFYWVT-x7IVGWrVa1-n3X_dOTDM9fnhxbw'
# URL вашего веб-приложения
WEB_APP_URL = 'https://sivch-coin-632b8.web.app/'

# Supabase credentials (замените на свои)
SUPABASE_URL = 'https://jgkfvqiophgvswqvatbx.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impna2Z2cWlvcGhndnN3cXZhdGJ4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk4ODI5NTMsImV4cCI6MjA1NTQ1ODk1M30.GTN1V9NJwnmwy8GmXOOz3SxepV7n4yVKkhLYZTYuFEQ'

# Инициализация клиента Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Создаем экземпляр бота
bot = telebot.TeleBot(TOKEN)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    # Получаем payload (если есть)
    payload = message.text.split()[1] if len(message.text.split()) > 1 else ''
    # Формируем URL с параметром ref
    url = f"{WEB_APP_URL}?ref={payload}"

    # Создаем кнопку с веб-приложением
   

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('🔐Создать аккаунт🔐', callback_data='get_akk'))
    markup.add(types.InlineKeyboardButton('💰Пополнить аккаунт💰', callback_data='get_money'),types.InlineKeyboardButton('💰Купить NFT💰', callback_data='get_money_nft'))
    markup.add(types.InlineKeyboardButton('📱Услуга гаранта📱', callback_data='garant'))
    markup.add(types.InlineKeyboardButton("Запустить AMAHASLA", web_app=types.WebAppInfo(url)))
    markup.add(types.InlineKeyboardButton('Присоединиться к нам', url='https://t.me/amahaslacoin'))
    photo_instruction_Amahasla = open(r"picture/hasla.jpg", 'rb')
    # Отправляем сообщение с кнопкой
    bot.send_photo(message.chat.id,photo= photo_instruction_Amahasla , caption = f"------👋Привет {message.from_user.first_name}!------  \n \n💰Очень рады тебя приветствовать в AMAHASLA\n \n В AMAHASLA можно заработать сам токен и покупать NFT. Также можно торговать аккаунтами с вашими NFT. Каждое NFT эксклюзивное, а это значит, что аккаунт с первыми коллекциями NFT вырастет в цене! В нашем телеграм канале мы проводим розыгрыши на Амахаслу почти каждый день! Продавайте, покупайте, развивайтесь вместе с нами!🎉\n \n (Перед началом фарма токена создайте аккаунт и войдите в него в приложении)",  reply_markup=markup)

# Обработчик callback-запросов
@bot.callback_query_handler(func=lambda message: True)
def get_user_message(message):
    telegram_id = message.from_user.id
    markup = types.InlineKeyboardMarkup()
    if message.data == 'garant':
        bot.delete_message(message.message.chat.id, message.message.message_id)
        markup.add(types.InlineKeyboardButton('⛓Гарант⛓', url ="https://t.me/amahaslareplenishment"))
        markup.add(types.InlineKeyboardButton('🏠Главное меню🏠', callback_data='menu'))
        bot.send_message(message.message.chat.id, "*🔑Гарант сделок🔑* \n\n_Кто такой «Гарант»?_\n•Гарант - человек, который поможет провести сделку безопасно как для потребителя, так и для продавца\n\n _Как проходит сделка с участием гаранта?_ \n1.Потребитель и продавец договариваются касательно оплаты гаранта (определяются кто будет платить за гаранта, можно разделить оплату на двоих, но передавать оплату гаранту должен только один участник сделки. То есть у кого то из участников сделки должна собраться сумма оплаты гаранта)\n2.Продавец отправляет товар(NFT), а потребитель - ожидает сообщение от гаранта о том, что NFT у него и готово к отправке. \nТакже один из участников сделки должен оплатить участие гаранта (Если вы договорились разделить оплату гаранта, то в данном случае сумма оплаты должна быть либо у потребителя, либо у продавца. *Будьте предельно осторожны при отправлении средств для оплаты гаранта*) \n3.Гарант отправляет сообщение потребителю о том, что NFT готово к отправке\n4.Потребитель сообщает о переводе средств продавцу и гарант проверяет квитанцию\n5.Если квитанция не фейковая и продавец подтвердил получение средств, в этом случае гарант передаёт NFT потребителю.\n\nОфициальный гарант - AMAHASLA (Имя, используемое при передаче NFT)" , reply_markup=markup, parse_mode='Markdown')
    if message.data == 'menu':
        bot.delete_message(message.message.chat.id, message.message.message_id)
        payload = message.message.text.split()[1] if len(message.message.text.split()) > 1 else ''
        # Формируем URL с параметром ref
        url = f"{WEB_APP_URL}?ref={payload}"
        markup.add(types.InlineKeyboardButton('🔐Создать аккаунт🔐', callback_data='get_akk'))
        markup.add(types.InlineKeyboardButton('📱Услуга гаранта📱', callback_data='garant'))
        markup.add(types.InlineKeyboardButton('💰Пополнить аккаунт💰', callback_data='get_money'),types.InlineKeyboardButton('💰Купить NFT💰', callback_data='get_money_nft'))
        markup.add(types.InlineKeyboardButton("Запустить AMAHASLA", web_app=types.WebAppInfo(url)))
        markup.add(types.InlineKeyboardButton('Присоединиться к нам', url='https://t.me/amahaslacoin'))
        photo_instruction_Amahasla = open(r"picture/hasla.jpg", 'rb')
        # Отправляем сообщение с кнопкой
        bot.send_photo(message.from_user.id, photo=photo_instruction_Amahasla, caption = f"------👋Привет {message.from_user.first_name}!------  \n \n💰Очень рады тебя приветствовать в AMAHASLA\n \n В AMAHASLA можно заработать сам токен и покупать NFT. Также можно торговать аккаунтами с вашими NFT. Каждое NFT эксклюзивное, а это значит, что аккаунт с первыми коллекциями NFT вырастет в цене! В нашем телеграм канале мы проводим розыгрыши на Амахаслу почти каждый день! Продавайте, покупайте, развивайтесь вместе с нами!🎉\n \n (Перед началом фарма токена создайте аккаунт и войдите в него в приложении)",  reply_markup=markup)
    if message.data == 'get_id':
        bot.delete_message(message.message.chat.id, message.message.message_id)
        markup.add(types.InlineKeyboardButton('🏠Главное меню🏠', callback_data='menu'))
        markup.add(types.InlineKeyboardButton('Назад', callback_data='get_money'))
        bot.send_message(message.message.chat.id, "Ваш ID: "+ f"<code>{str(message.from_user.id)}</code>" , reply_markup=markup, parse_mode='HTML')
    if message.data == 'get_money_nft':
        bot.delete_message(message.message.chat.id, message.message.message_id)
        markup.add(types.InlineKeyboardButton('Прайс лист', callback_data='price_nft'))
        markup.add(types.InlineKeyboardButton('Мой ID', callback_data='get_id'))
        markup.add(types.InlineKeyboardButton('Купить NFT', url='https://t.me/amahaslareplenishment'))
        markup.add(types.InlineKeyboardButton('🏠Главное меню🏠', callback_data='menu'))
        bot.send_message(message.message.chat.id, "*💰Покупка NFT💰* \n \n Купить NFT вы можете через @Amahaslareplenishment. Оплата суммы NFT аккаунта происходит через @*CryptoBot*, @*Wallet* или же *Telegram Stars*.\n\n Алгоритм оплаты:\n▾Вы выбираете NFT \n▾Отправляете оплату @Amahaslareplenishment и *ваш ID* \n▾NFT на вашем аккаунте!🎉 \n \n Перед покупкой обязательно ознакомьтесь с прайс-листом (_если вы отправили не соответсвующую сумму оплаты или неверный ID  - возврат средств не предусмотрен_)", reply_markup=markup, parse_mode='Markdown')
    if message.data == 'get_money':
        bot.delete_message(message.message.chat.id, message.message.message_id)
        markup.add(types.InlineKeyboardButton('Прайс лист', callback_data='price'))
        markup.add(types.InlineKeyboardButton('Мой ID', callback_data='get_id'))
        markup.add(types.InlineKeyboardButton('Пополнить баланс', url='https://t.me/amahaslareplenishment'))
        markup.add(types.InlineKeyboardButton('🏠Главное меню🏠', callback_data='menu'))
        bot.send_message(message.message.chat.id, "*💰Пополнение баланса💰* \n \n Пополнить аккаунт вы можете через @Amahaslareplenishment. Оплата суммы пополнения аккаунта происходит через @*CryptoBot*, @*Wallet* или же *Telegram Stars*.\n\n Алгоритм оплаты:\n▾Вы выбираете сумму пополнения (пополнить можно не меньше 20000 Амахаслы - 0,3 TON)\n▾Отправляете оплату @Amahaslareplenishment и *ваш ID* \n▾Вы пополнили аккаунт!🎉 \n \n Перед пополнением обязательно ознакомьтесь с прайс-листом (_если вы отправили не соответсвующую сумму оплаты или неверный ID  - возврат средств не предусмотрен_)", reply_markup=markup, parse_mode='Markdown')
    if message.data == 'price_nft':
        bot.delete_message(message.message.chat.id, message.message.message_id)
        markup.add(types.InlineKeyboardButton('Купить NFT', url='https://t.me/amahaslareplenishment'))
        markup.add(types.InlineKeyboardButton('🏠Главное меню🏠', callback_data='menu'))
        markup.add(types.InlineKeyboardButton('Назад', callback_data='get_money_nft'))
        bot.send_message(message.message.chat.id, '*💵Прайс лист💵* \n\n HUSTLER - 0,275 TON 🔹 | 100 Stars ✨ \n COWBOY HUSTLER - 0,3 TON 🔹 | 200 Stars ✨\n BOSS HUSTLER - 0,4 TON 🔹 | 300 Stars ✨\n STEEP HUSTLER - 0,5 TON 🔹 | 400 Stars ✨ \n STALKER HUSTLER - 0,6 TON 🔹 | 4000 Stars ✨', reply_markup=markup, parse_mode='Markdown')
    if message.data == 'price':
        bot.delete_message(message.message.chat.id, message.message.message_id)
        markup.add(types.InlineKeyboardButton('Пополнить баланс', url='https://t.me/amahaslareplenishment'))
        markup.add(types.InlineKeyboardButton('🏠Главное меню🏠', callback_data='menu'))
        markup.add(types.InlineKeyboardButton('Назад', callback_data='get_money'))
        bot.send_message(message.message.chat.id, '*💵Прайс лист💵* \n\n 20k AMHSL - 0,3 TON 🔹 | 100 Stars ✨ \n 50k AMHSL - 0,6 TON 🔹 | 200 Stars ✨\n 75k AMHSL - 0,8 TON 🔹 | 300 Stars ✨\n 100k AMHSL - 1,2 TON 🔹 | 400 Stars ✨ \n 1m AMHSL - 10 TON 🔹 | 4000 Stars ✨', reply_markup=markup, parse_mode='Markdown')
    if message.data == 'get_akk':
        # Проверяем, зарегистрирован ли пользователь
        user_data = get_user_data(telegram_id)
        if user_data:
            # Если пользователь уже зарегистрирован
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Данные моего аккаунта', callback_data='my_account'))
            bot.send_message(message.message.chat.id, "*🔐Вы уже зарегистрированы!🔐*", reply_markup=markup, parse_mode='Markdown')
        else:
            # Если пользователь не зарегистрирован
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Сгенерировать пароль', callback_data='password'))
            markup.add(types.InlineKeyboardButton('Придумать никнейм', callback_data='name'))
            bot.send_message(message.message.chat.id, 'Чтобы войти в аккаунт в игре, вам нужно создать аккаунт', reply_markup=markup)
    elif message.data == 'password':
        # Проверяем, есть ли уже пароль у пользователя
        user_data = get_user_data(telegram_id)
        if user_data and user_data.get('password'):
            bot.send_message(message.message.chat.id, "*🔑Пароль уже есть*🔑",reply_markup=markup, parse_mode='Markdown')
        else:
            def generate_random_string(length):
                characters = string.ascii_letters + string.digits
                return ''.join(random.choice(characters) for i in range(length))
            password = generate_random_string(10)
            print(password)
            pass_mess = f'Ваш пароль:  <code>{password}</code>'
            bot.send_message(message.message.chat.id, pass_mess, parse_mode='HTML')
            # Сохраняем пароль в Supabase
            update_user_data(telegram_id, password=password)
    elif message.data == 'name':
        # Проверяем, есть ли уже имя у пользователя
        user_data = get_user_data(telegram_id)
        if user_data and user_data.get('name'):
            bot.send_message(message.message.chat.id, "*👤Никнейм уже есть👤*",reply_markup=markup,parse_mode='Markdown')
        else:
            bot.send_message(message.message.chat.id, 'Придумайте никнейм (до 10 символов)')
            bot.register_next_step_handler(message.message, proverka_nika)
    elif message.data == 'my_account':
        # Обработка кнопки "Данные моего аккаунта"
        my_account(message)



def proverka_nika(message):
    markup = types.InlineKeyboardMarkup()
    if len(message.text) > 10:
        bot.send_message(message.chat.id, 'Придумайте никнейм (до 10 символов)')
        bot.register_next_step_handler(message, proverka_nika)
    else:
        name = message.text
        # Проверяем, существует ли уже такой никнейм
        response = supabase.table('users').select('name').eq('name', name).execute()
        if response.data:
            bot.send_message(message.chat.id, "Этот никнейм уже занят, попробуйте другой")
            bot.register_next_step_handler(message, proverka_nika)
        else:
            print(name)
            # Сохраняем никнейм в Supabase
            telegram_id = message.from_user.id
            update_user_data(telegram_id, name=name)
            bot.send_message(message.chat.id, f"Никнейм успешно сохранен: <code>{name}</code>",parse_mode='HTML')

# Обработчик для кнопки "Данные моего аккаунта"
def my_account(call):
    
    bot.delete_message(call.message.chat.id, call.message.message_id)
    telegram_id = call.from_user.id
    markup = types.InlineKeyboardMarkup()
    user_data = get_user_data(telegram_id)
    if user_data:
        name = user_data.get('name', 'не указан')
        password = user_data.get('password', 'не указан')
        bot.send_message(call.message.chat.id, f"Ваши данные:\n\n👤 Никнейм: <code>{name}</code>\n🔑 Пароль: <code>{password}</code>",reply_markup=markup, parse_mode='HTML')
    elif (call.data == 'back'):
        bot.delete_message(call.message.chat.id, call.message.message_id)
    else:
        bot.send_message(call.message.chat.id, "Вы еще не зарегистрированы!")
# Функция для получения данных пользователя из Supabase
def get_user_data(telegram_id):
    response = supabase.table('users').select('*').eq('telegram', telegram_id).execute()
    if response.data:
        return response.data[0]  # Возвращаем первую запись (если есть)
    return None

# Функция для обновления данных пользователя в Supabase
def update_user_data(telegram_id, name=None, password=None):
    data = {}
    if name:
        data['name'] = name
    if password:
        data['password'] = password
    user_data = get_user_data(telegram_id)
    if user_data:
        # Если пользователь существует, обновляем данные
        supabase.table('users').update(data).eq('telegram', telegram_id).execute()
        print("Данные успешно обновлены!")
    else:
        # Если пользователь не существует, создаем новую запись
        data['telegram'] = telegram_id
        supabase.table('users').insert(data).execute()
        print("Пользователь успешно зарегистрирован!")

bot.polling(none_stop=True)