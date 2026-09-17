import datetime
import threading
import telebot
from telebot import types
import random
import string
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from supabase import create_client, Client
import requests
from bs4 import BeautifulSoup
import os
import re
from datetime import datetime, timedelta  
import json
import ast
import hashlib
import uuid
import asyncio
from typing import Dict, Any
# Конфигурация
TOKEN = '8549009179:AAES5a75EWbQs5roRKyosjUiNCTCgSUwRB4'
WEB_APP_URL = 'https://drops-gifts.vercel.app/'
SUPABASE_URL = 'https://nohkjfzicycrdyjastxn.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5vaGtqZnppY3ljcmR5amFzdHhuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjAxODg2MTcsImV4cCI6MjA3NTc2NDYxN30.1Vxvd2fi7tcUKaiTYv8uzO6KTu6fAgXfOw-cjZKpOBA'
SECRET_CODE = "AMAHASLA_SECRET_123"

# Инициализация клиентов
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
bot = telebot.TeleBot(TOKEN)

# Хранилище для пользователей с доступом к NFT функциям
nft_access_users = set()
# Добавьте эти функции в app.py

import time
from datetime import datetime, timedelta

# Хранилище последних отправленных операций
last_sent_operations = {}


# Добавьте эти функции в ваш app.py перед bot.polling()

def process_unrecorded_operations():
    """
    Проверяет всех пользователей на наличие операций с is_recorded = "false"
    и отправляет уведомление пользователю.
    Запускается в отдельном потоке каждые 5 секунд.
    """
    print("🔄 Запущен мониторинг неподтвержденных операций...")
    
    while True:
        try:
            # Получаем всех пользователей
            response = supabase.table('users').select('telegram, name, operation_history').execute()
            
            if not response.data:
                time.sleep(5)
                continue
            
            for user in response.data:
                telegram_id = user.get('telegram')
                name = user.get('name')
                operation_history = user.get('operation_history', [])
                
                if not telegram_id or not operation_history:
                    continue
                
                # Ищем операции с is_recorded = "false"
                for operation in operation_history:
                    # Проверяем, что это topup или withdraw и is_recorded = "false"
                    if operation.get('type') in ['topup', 'withdraw'] and operation.get('is_recorded') == "false":
                        print(f"📝 Найдена неподтвержденная операция: {operation.get('type')} для {name}")
                        
                        # Отправляем уведомление пользователю
                        success = send_transaction_notification_to_user(telegram_id, operation, name)
                        
                        if success:
                            # Обновляем статус is_recorded на "true"
                            update_operation_recorded_status(name, operation.get('id'), "true")
                            print(f"✅ Операция {operation.get('id')} помечена как recorded")
                        else:
                            print(f"⚠️ Не удалось отправить уведомление для операции {operation.get('id')}, пробуем позже")
            
            # Пауза между проверками
            time.sleep(5)
            
        except Exception as e:
            print(f"❌ Ошибка в process_unrecorded_operations: {e}")
            time.sleep(10)


def send_transaction_notification_to_user(telegram_id: int, operation: Dict[str, Any], user_name: str) -> bool:
    """
    Отправляет уведомление пользователю о совершенной транзакции
    """
    try:
        op_type = operation.get('type')
        amount = operation.get('amount')
        tx_hash = operation.get('transactionHash')
        timestamp = operation.get('timestamp')
        
        # Форматируем дату
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                # Добавляем +5 часов (Тюмень)
                dt = dt + timedelta(hours=5)
                formatted_date = dt.strftime('%d.%m.%Y %H:%M:%S')
            except:
                formatted_date = timestamp
        else:
            formatted_date = "Не указано"
        
        # Ссылка на транзакцию
        tx_url = f"https://tonscan.org/tx/{tx_hash}"
        
        # Получаем язык пользователя
        lang = Localization.get_user_language(telegram_id)
        
        # Формируем сообщение в зависимости от типа и языка
        if op_type == 'topup':
            if lang == 'ru':
                message = f"""✅ *Пополнение баланса*

💰 Сумма: *+{amount} TON*
🔗 [Ссылка на транзакцию]({tx_url})

✨ Ваш баланс успешно пополнен!"""
            else:
                message = f"""✅ *Balance Top-up*

💰 Amount: *+{amount} TON*
🔗 [Transaction link]({tx_url})

✨ Your balance has been successfully topped up!"""
        
        else:  # withdraw
            if lang == 'ru':
                message = f"""💸 *Вывод средств*

💰 Сумма: *-{amount} TON*
🔗 [Ссылка на транзакцию]({tx_url})

✨ Средства успешно выведены!"""
            else:
                message = f"""💸 *Withdrawal*

💰 Amount: *-{amount} TON*
🔗 [Transaction link]({tx_url})

✨ Funds successfully withdrawn!"""
        
        # Отправляем сообщение пользователю
        bot.send_message(
            telegram_id,
            message,
            parse_mode='Markdown',
            disable_web_page_preview=False
        )
        
        print(f"📨 Уведомление отправлено пользователю {telegram_id} о {op_type} на {amount} TON")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка отправки уведомления пользователю {telegram_id}: {e}")
        return False


def update_operation_recorded_status(user_name: str, operation_id, new_status: str) -> bool:
    """
    Обновляет статус is_recorded для операции в БД
    """
    try:
        # Получаем пользователя
        response = supabase.table('users').select('operation_history').eq('name', user_name).execute()
        
        if not response.data:
            print(f"❌ Пользователь {user_name} не найден")
            return False
        
        operation_history = response.data[0].get('operation_history', [])
        
        # Обновляем конкретную операцию
        updated = False
        for i, op in enumerate(operation_history):
            if op.get('id') == operation_id:
                operation_history[i]['is_recorded'] = new_status
                updated = True
                break
        
        if not updated:
            print(f"⚠️ Операция {operation_id} не найдена у {user_name}")
            return False
        
        # Сохраняем обратно
        supabase.table('users').update({
            'operation_history': operation_history
        }).eq('name', user_name).execute()
        
        print(f"✅ Статус is_recorded обновлен на {new_status} для операции {operation_id}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка обновления статуса: {e}")
        return False


def start_unrecorded_monitoring():
    """Запускает мониторинг неподтвержденных операций"""
    monitor_thread = threading.Thread(target=process_unrecorded_operations, daemon=True)
    monitor_thread.start()
    print("✅ Мониторинг неподтвержденных операций запущен")


def force_check_all_users():
    """
    Принудительная проверка всех пользователей (можно вызвать по команде /check_operations)
    """
    try:
        print("🔍 Принудительная проверка всех операций...")
        response = supabase.table('users').select('telegram, name, operation_history').execute()
        
        total_unrecorded = 0
        
        for user in response.data:
            telegram_id = user.get('telegram')
            name = user.get('name')
            operation_history = user.get('operation_history', [])
            
            if not telegram_id:
                continue
                
            for operation in operation_history:
                if operation.get('type') in ['topup', 'withdraw'] and operation.get('is_recorded') == "false":
                    total_unrecorded += 1
                    print(f"📝 Найдена операция {operation.get('id')} у {name}")
                    
                    # Отправляем уведомление
                    success = send_transaction_notification_to_user(telegram_id, operation, name)
                    if success:
                        update_operation_recorded_status(name, operation.get('id'), "true")
        
        print(f"✅ Проверка завершена. Обработано {total_unrecorded} операций")
        return total_unrecorded
        
    except Exception as e:
        print(f"❌ Ошибка принудительной проверки: {e}")
        return 0


# Добавьте команду для бота (принудительная проверка)
@bot.message_handler(commands=['check_operations'])
def check_operations_command(message):
    """Команда для принудительной проверки всех неподтвержденных операций"""
    # Проверяем, что команду выполняет админ (укажите ID админов)
    admin_ids = ['123456789', '987654321']  # Замените на реальные ID
    
    if str(message.from_user.id) in admin_ids:
        bot.reply_to(message, "🔍 Начинаю проверку всех неподтвержденных операций...")
        
        # Запускаем в отдельном потоке, чтобы не блокировать бота
        def run_check():
            count = force_check_all_users()
            bot.send_message(message.chat.id, f"✅ Проверка операций завершена! Обработано {count} операций.")
        
        thread = threading.Thread(target=run_check)
        thread.start()
    else:
        bot.reply_to(message, "❌ У вас нет прав для этой команды")


# Функция для получения времени в UTC+5
def get_tyumen_time():
    """
    Возвращает текущее время в часовом поясе Тюмени (UTC+5)
    Без использования pytz для совместимости
    """
    utc_time = datetime.utcnow()
    tyumen_time = utc_time + timedelta(hours=5)
    return tyumen_time.isoformat()
# Альтернативная функция без pytz (если не хотите устанавливать библиотеку)
def get_tyumen_time_simple():
    """
    Простая версия без pytz - просто добавляет 5 часов к UTC
    """
    utc_time = datetime.utcnow()
    tyumen_time = utc_time + timedelta(hours=5)
    return tyumen_time.isoformat()
# ==================== ЛОКАЛИЗАЦИЯ ====================
class Localization:
    """Класс для управления локализацией сообщений"""
    
    # Словарь с переводами для всех сообщений
    translations = {
        'ru': {
            # Приветствие
            'welcome': "👋 Привет {name}, добро пожаловать в Drops! Здесь ты можешь:\n • Совершать транзакции без комиссии\n • Получать бонусы за задания, покупки и приглашения друзей\n • Участвовать в розыгрышах бесплатно\nИ многое другое! И это только начало.\n \n<b>🌙 Встречай рассвет с Drops.</b>",
            # В класс Localization добавьте:
            'refund_other_sale': "💰 *Возврат средств*\n\nВаше предложение на *{nft_name}* было отклонено, так как NFT был продан другому покупателю.\n\n💸 *{offer_price} TON* возвращены на ваш баланс.\n📊 Новый баланс: *{new_balance} TON*",
            # Уведомления о предложениях
            'new_offer_title': "🎯 *Новое предложение цены!*",
            'nft_label': "*NFT:*",
            'current_price_label': "*Текущая цена:*",
            'offer_price_label': "*Предложенная цена:*",
            'accept_offer_question': "Хотите принять это предложение?",
            'accept_button': "✅ Принять предложение",
            'decline_button': "❌ Отклонить предложение",
            'view_item_button': "👀 Посмотреть товар",
            
            # Сообщения для продавца при принятии/отклонении
            'offer_accepted_seller': "✅ *Вы приняли предложение!*\n\n🎁 Товар: *{nft_name}* #{nft_id}\n💵 Сумма: *{offer_price} TON*\n💰 Вы получили: *{seller_amount:.2f} TON*\n\nNFT успешно передан покупателю.\nСделка завершена!",
            'offer_declined_seller': "❌ *Вы отклонили предложение*\n\n🎁 Товар: *{nft_name}* #{nft_id}\n💵 Предложение: *{offer_price} TON*\n\n💰 Средства возвращены покупателю.",
            
            # Сообщения для покупателя
            'offer_accepted_buyer': "🎉 *Ваше предложение принято!*\n\n*{nft_name}* #{nft_id}\n💵 Сумма сделки: *{offer_price} TON*\n\n✅ *NFT успешно передан вам!*",
            'offer_declined_buyer': "❌ *Ваше предложение отклонено*\n\n*{nft_name}* #{nft_id}\n💵 Ваше предложение: *{offer_price} TON*\n\n💰 *Средства возвращены на ваш баланс!*",
            
            # Автоматическое отклонение
            'offer_auto_declined_buyer': "❌ *Ваше предложение автоматически отклонено*\n\n*{nft_name}* #{nft_id}\n💵 Ваше предложение: *{offer_price} TON*\n\n⚠️ *Продавец больше не владеет этим NFT*\n💰 *Средства возвращены на ваш баланс!*",
            'offer_auto_declined_seller': "❌ *Предложение автоматически отклонено*\n\n⚠️ *Вы больше не владеете этим NFT*\n\n🎁 Товар: *{nft_name}*\n💵 Предложение: *{offer_price} TON*\n\n💰 Средства возвращены покупателю.",
            
            # Возврат средств при продаже другому
            'refund_other_sale': "💰 *Возврат средств*\n\nВаше предложение на *{nft_name}* было отменено, так как NFT был продан другому покупателю.\n\n💸 *{offer_price} TON* возвращены на ваш баланс.\n📊 Новый баланс: *{new_balance} TON*",
            
            # Кнопки и общие фразы
            'back_button': "🔙 Назад",
            'main_menu_button': "🏠 Главное меню",
            'error_occurred': "❌ Произошла ошибка при обработке",
            'processing_request': "⏳ Обрабатываем ваш запрос...",
            'offer_not_found': "❌ Предложение не найдено",
            'offer_already_processed': "❌ Это предложение уже обрабатывается",
            'buyer_not_found': "❌ Ошибка: покупатель не найден",
        },
        'en': {
            # Welcome message
            'welcome': "👋 Hi {name}, welcome to Drops! Here you can:\n • Make transactions with no extra fees\n • Earn bonuses for tasks, purchases, and friend invites\n • Join giveaways for free\nAnd much more! And this is just the beginning.\n \n<b>🌙 Meet moonrise with Drops.</b>",
            
            # Offer notifications
            'new_offer_title': "🎯 *New price offer!*",
            'nft_label': "*NFT:*",
            'current_price_label': "*Current price:*",
            'offer_price_label': "*Offered price:*",
            'accept_offer_question': "Do you want to accept this offer?",
            'accept_button': "✅ Accept offer",
            'decline_button': "❌ Decline offer",
            'view_item_button': "👀 View item",
            
            # Messages for seller when accepting/declining
            'offer_accepted_seller': "✅ *You accepted the offer!*\n\n🎁 Item: *{nft_name}* #{nft_id}\n💵 Amount: *{offer_price} TON*\n💰 You received: *{seller_amount:.2f} TON*\n\nNFT successfully transferred to buyer.\nTransaction completed!",
            'offer_declined_seller': "❌ *You declined the offer*\n\n🎁 Item: *{nft_name}* #{nft_id}\n💵 Offer: *{offer_price} TON*\n\n💰 Funds returned to buyer.",
            
            # Messages for buyer
            'offer_accepted_buyer': "🎉 *Your offer was accepted!*\n\n*{nft_name}* #{nft_id}\n💵 Transaction amount: *{offer_price} TON*\n\n✅ *NFT successfully transferred to you!*",
            'offer_declined_buyer': "❌ *Your offer was declined*\n\n*{nft_name}* #{nft_id}\n💵 Your offer: *{offer_price} TON*\n\n💰 *Funds returned to your balance!*",
            
            # Automatic decline
            'offer_auto_declined_buyer': "❌ *Your offer was automatically declined*\n\n*{nft_name}* #{nft_id}\n💵 Your offer: *{offer_price} TON*\n\n⚠️ *Seller no longer owns this NFT*\n💰 *Funds returned to your balance!*",
            'offer_auto_declined_seller': "❌ *Offer automatically declined*\n\n⚠️ *You no longer own this NFT*\n\n👤 Buyer: *{buyer_name}*\n🎁 Item: *{nft_name}*\n💵 Offer: *{offer_price} TON*\n\n💰 Funds returned to buyer.",
            
            # Refund when sold to another
            'refund_other_sale': "💰 *Refund*\n\nYour offer for *{nft_name}* was canceled because the NFT was sold to another buyer.\n\n💸 *{offer_price} TON* returned to your balance.\n📊 New balance: *{new_balance} TON*",
            
            # Buttons and common phrases
            'back_button': "🔙 Back",
            'main_menu_button': "🏠 Main menu",
            'error_occurred': "❌ An error occurred while processing",
            'processing_request': "⏳ Processing your request...",
            'offer_not_found': "❌ Offer not found",
            'offer_already_processed': "❌ This offer is already being processed",
            'buyer_not_found': "❌ Error: buyer not found",
        }
    }
    
    @staticmethod
    def get_user_language(user_id):
        """
        Получает язык пользователя из базы данных
        """
        try:
            response = supabase.table('users').select('language_code').eq('telegram', user_id).execute()
            if response.data and len(response.data) > 0:
                lang = response.data[0].get('language_code', 'en')
                return lang if lang in Localization.translations else 'en'
            return 'en'
        except Exception as e:
            print(f"❌ Ошибка получения языка пользователя {user_id}: {e}")
            return 'en'
    
    @staticmethod
    def get_text(user_id, key, **kwargs):
        """
        Получает локализованный текст для пользователя
        """
        lang = Localization.get_user_language(user_id)
        text = Localization.translations.get(lang, Localization.translations['en']).get(key, key)
        return text.format(**kwargs) if kwargs else text
    
    @staticmethod
    def set_user_language(user_id, language_code):
        """
        Устанавливает язык пользователя в базу данных
        """
        try:
            # Проверяем существование пользователя
            user_data = get_user_data(user_id)
            if user_data:
                supabase.table('users').update({'language_code': language_code}).eq('telegram', user_id).execute()
            else:
                # Если пользователя нет, создаем с указанным языком
                numeric_id = generate_numeric_id()
                supabase.table('users').insert({
                    'id': numeric_id,
                    'telegram': user_id,
                    'language_code': language_code,
                    'created_at': datetime.now().isoformat()
                }).execute()
            print(f"✅ Язык пользователя {user_id} установлен: {language_code}")
            return True
        except Exception as e:
            print(f"❌ Ошибка установки языка пользователя {user_id}: {e}")
            return False

def save_referrer_to_user(telegram_id, referrer_telegram_id):
    """
    Сохраняет ID реферера (того, кто пригласил) в колонку from_refer
    """
    try:
        # Проверяем, существует ли пользователь
        response = supabase.table('users') \
            .select('from_refer') \
            .eq('telegram', telegram_id) \
            .execute()
        
        if not response.data:
            print(f"❌ Пользователь {telegram_id} не найден")
            return False
        
        current_refer = response.data[0].get('from_refer')
        
        # Если from_refer уже установлен и не 0, не перезаписываем
        if current_refer is not None and current_refer != 0:
            print(f"ℹ️ У пользователя {telegram_id} уже есть from_refer = {current_refer}")
            return True
        
        # Сохраняем ID пригласившего
        update_response = supabase.table('users') \
            .update({'from_refer': int(referrer_telegram_id)}) \
            .eq('telegram', telegram_id) \
            .execute()
        
        print(f"✅ Для пользователя {telegram_id} сохранен from_refer = {referrer_telegram_id}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка сохранения from_refer: {e}")
        return False
def register_ref_sync(userName, refId):
    """Синхронная версия функции registerRef"""
    try:
        print(f"🔍 Регистрация реферала: {userName} от {refId}")
        
        # 1. Получаем данные реферера
        response = supabase.table('users') \
            .select('friends, score') \
            .eq('telegram', int(refId)) \
            .execute()
        
        if not response.data:
            print(f"❌ Реферер с ID {refId} не найден")
            return False
        
        refData = response.data[0]

        # 2. Получаем ID текущего пользователя по имени
        user_response = supabase.table('users') \
            .select('telegram') \
            .eq('name', userName) \
            .execute()
            
        if not user_response.data:
            print(f"❌ Пользователь с именем {userName} не найден")
            return False
            
        current_user_id = str(user_response.data[0]['telegram'])

        # 3. Проверяем, есть ли текущий пользователь уже в друзьях
        friends = refData.get('friends', {})
        
        if friends.get(current_user_id):
            print('✅ Пользователь уже был добавлен в друзья ранее')
            return True

        # 4. Добавляем в друзья и начисляем бонус
        update_response = supabase.table('users') \
            .update({
                'friends': {**friends, current_user_id: userName},
                'score': refData.get('score', 0) + 10000,
            }) \
            .eq('telegram', int(refId)) \
            .execute()
            
        print(f"✅ Реферал {userName} успешно добавлен к пользователю {refId}")
        return True
        
    except Exception as e:
        print(f'❌ Ошибка при обновлении данных реферала: {e}')
        return False

def generate_numeric_id():
    """Генерирует числовой ID на основе временной метки"""
    return int(datetime.now().timestamp() * 1000000)


def get_user_avatar_url(user_id):
    """
    Получает ссылку на аватар пользователя по его ID
    Формат ссылки: https://t.me/i/userpic/320/{hash}.svg
    """
    try:
        # Получаем информацию о пользователе
        user_profile_photos = bot.get_user_profile_photos(user_id, limit=1)
        
        if user_profile_photos.total_count > 0:
            # Если у пользователя есть фото профиля, получаем file_id
            file_id = user_profile_photos.photos[0][0].file_id
            
            # Получаем информацию о файле
            file_info = bot.get_file(file_id)
            file_path = file_info.file_path
            
            # Формируем прямую ссылку на файл
            avatar_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
            
            print(f"🔗 Ссылка на аватар пользователя {user_id}: {avatar_url}")
            return avatar_url
        else:
            # Если у пользователя нет аватара, используем стандартный шаблон
            # Генерируем хеш на основе ID пользователя для consistency
            hash_object = hashlib.md5(str(user_id).encode())
            hash_hex = hash_object.hexdigest()[:20]
            
            # Стандартный формат ссылки Telegram для аватаров
            avatar_url = f"https://t.me/i/userpic/320/{hash_hex}.svg"
            
            print(f"🔗 Стандартная ссылка на аватар пользователя {user_id}: {avatar_url}")
            return avatar_url
            
    except Exception as e:
        print(f"❌ Ошибка при получении аватара пользователя {user_id}: {e}")
        return None


def get_user_display_name(telegram_user):
    """
    Получает отображаемое имя пользователя
    """
    # Сначала пробуем получить username
    if telegram_user.username:
        return telegram_user.username
    
    # Если username нет, используем полное имя
    if telegram_user.first_name and telegram_user.last_name:
        return f"{telegram_user.first_name} {telegram_user.last_name}"
    elif telegram_user.first_name:
        return telegram_user.first_name
    elif telegram_user.last_name:
        return telegram_user.last_name
    else:
        return "Неизвестный пользователь"


def save_user_avatar_to_db(telegram_id, avatar_url, telegram_user=None):
    """
    Сохраняет ссылку на аватар пользователя в базу данных
    в колонку avatar_link формата jsonb
    """
    try:
        # Получаем имя пользователя для сохранения
        if telegram_user:
            user_name = get_user_display_name(telegram_user)
        else:
            # Если объект пользователя не передан, пытаемся получить из базы
            user_data = get_user_data(telegram_id)
            if user_data and user_data.get('name'):
                user_name = user_data['name']
            else:
                user_name = f"User_{telegram_id}"
        
        # Сначала проверяем, существует ли пользователь
        user_data = get_user_data(telegram_id)
        
        if not user_data:
            # Если пользователя нет, создаем базовую запись с числовым ID
            numeric_id = generate_numeric_id()
            supabase.table('users').insert({
                'id': numeric_id,
                'telegram': telegram_id,
                'avatar_link': {
                    "url": avatar_url,
                    "updated_at": datetime.now().isoformat(),
                    "name": user_name
                },
                'name': user_name,
                'password': f"temp_{telegram_id}",
                'created_at': datetime.now().isoformat()
            }).execute()
            print(f"✅ Создан новый пользователь {telegram_id} с аватаром и именем: {user_name}, ID: {numeric_id}")
            return True
        
        # Создаем JSON объект для сохранения
        avatar_data = {
            "url": avatar_url,
            "updated_at": datetime.now().isoformat(),
            "name": user_name
        }
        
        # Обновляем запись пользователя
        response = supabase.table('users') \
            .update({'avatar_link': avatar_data}) \
            .eq('telegram', telegram_id) \
            .execute()
        
        if response.data:
            print(f"✅ Аватар пользователя {telegram_id} ({user_name}) сохранен в базу данных")
            return True
        else:
            print(f"❌ Не удалось сохранить аватар пользователя {telegram_id}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при сохранении аватара в базу данных: {e}")
        return False


def update_user_avatar(telegram_id, telegram_user=None):
    """
    Получает ссылку на аватар и сохраняет в базу данных
    """
    avatar_url = get_user_avatar_url(telegram_id)
    if avatar_url:
        return save_user_avatar_to_db(telegram_id, avatar_url, telegram_user)
    return False


def ensure_user_exists(telegram_id, username=None, first_name=None):
    try:
        user_data = get_user_data(telegram_id)
        if not user_data:
            # Создаем пользователя с числовым ID
            numeric_id = generate_numeric_id()
            user_data = {
                'id': numeric_id,
                'telegram': telegram_id,
                'created_at': datetime.now().isoformat(),
                'name': f"User_{telegram_id}",
                'password': f"temp_{telegram_id}",
                'from_refer': 0  # Инициализируем поле from_refer значением 0
            }
            
            if username:
                user_data['username'] = username
            if first_name:
                user_data['first_name'] = first_name
                
            supabase.table('users').insert(user_data).execute()
            print(f"✅ Создан новый пользователь: {telegram_id} с ID: {numeric_id}")
            return True
        return True
    except Exception as e:
        print(f"❌ Ошибка при создании пользователя: {e}")
        return False

def extract_data(html_content):
    """Извлекает данные о NFT из HTML страницы"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 1. Извлекаем мета-данные
    og_title = soup.find('meta', property='og:title')
    title = og_title['content'] if og_title and og_title.get('content') else None

    og_description = soup.find('meta', property='og:description')
    description = og_description['content'] if og_description and og_description.get('content') else None

    # 2. Извлекаем таблицу с характеристиками
    table = soup.find('table', class_='tgme_gift_table')
    table_data = {}
    if table:
        for row in table.find_all('tr'):
            cells = row.find_all(['th', 'td'])
            if len(cells) == 2:
                key = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True)
                
                # Обрабатываем Model, Backdrop и Symbol для разделения названия и числа
                if key in ['Model', 'Backdrop', 'Symbol']:
                    # Вариант 1: Разделяем по последней букве (если число в конце)
                    match = re.match(r'(.+?)([\d,\.%]+)$', value)
                    if match:
                        name_part = match.group(1).strip()
                        num_part = match.group(2).strip()
                        value = f"{name_part} {num_part}"
                    # Вариант 2: Разделяем по первому числу (если число в середине)
                    else:
                        match = re.match(r'(.+?)([\d,\.%]+)(.*)$', value)
                        if match:
                            name_part = match.group(1).strip()
                            num_part = match.group(2).strip()
                            rest_part = match.group(3).strip()
                            value = f"{name_part} {num_part}{rest_part}"
                
                table_data[key] = value

    return {
        'title': title,
        'description': description,
        'table_data': table_data
    }


@bot.callback_query_handler(func=lambda call: True)
def handle_all_callbacks(call):
    """
    Обрабатывает все callback запросы для отладки
    """
    print(f"🔔 Callback получен: {call.data} от пользователя {call.from_user.id}")
    
    # Обработка предложений
    if call.data.startswith(('accept_offer:', 'decline_offer:')):
        handle_offer_response(call)
    elif call.data.startswith('set_lang_'):
        set_language_callback(call)
    elif call.data == 'language_menu':
        language_menu_callback(call)
    else:
        # Остальные обработчики
        get_user_message(call)


def save_nft_metadata(nft_id, name, model, backdrop, symbol, telegram_user_id, telegram_user=None):
    """Сохраняет метаданные NFT в базу данных"""
    try:
        # Получаем и сохраняем ссылку на аватар пользователя
        update_user_avatar(telegram_user_id, telegram_user)
        
        # Проверяем, существует ли уже запись для этого NFT и пользователя
        existing = supabase.table('nft_metadata') \
                         .select('*') \
                         .eq('nft_id', nft_id) \
                         .eq('telegram_user_id', telegram_user_id) \
                         .execute()
        
        if not existing.data:
            # Если записи нет, создаем новую
            supabase.table('nft_metadata').insert({
                'nft_id': nft_id,
                'name': name,
                'model': model,
                'backdrop': backdrop,
                'symbol': symbol,
                'telegram_user_id': telegram_user_id
            }).execute()
    except Exception as e:
        print(f"Ошибка при сохранении метаданных NFT: {e}")


# Добавляем команду для смены языка
@bot.message_handler(commands=['language', 'lang'])
def set_language_command(message):
    """Команда для смены языка"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🇷🇺 Русский", callback_data="set_lang_ru"),
        types.InlineKeyboardButton("🇬🇧 English", callback_data="set_lang_en")
    )
    markup.add(types.InlineKeyboardButton(
        Localization.get_text(message.from_user.id, 'main_menu_button'),
        callback_data='menu'
    ))
    
    bot.send_message(
        message.chat.id,
        "🌐 Select language / Выберите язык:",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('set_lang_'))
def set_language_callback(call):
    """Обработчик выбора языка"""
    lang = call.data.split('_')[-1]  # ru или en
    user_id = call.from_user.id
    
    if Localization.set_user_language(user_id, lang):
        bot.answer_callback_query(call.id, f"✅ Language set to {'English' if lang == 'en' else 'Русский'}")
        
        # Обновляем сообщение
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(
            Localization.get_text(user_id, 'main_menu_button'),
            callback_data='menu'
        ))
        
        bot.edit_message_text(
            f"✅ Language changed to {'English' if lang == 'en' else 'Русский'}",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
    else:
        bot.answer_callback_query(call.id, "❌ Error / Ошибка", show_alert=True)


@bot.message_handler(commands=['start'])
def start(message):
    # Сначала убеждаемся, что пользователь существует в базе
    ensure_user_exists(
        message.from_user.id, 
        username=message.from_user.username,
        first_name=message.from_user.first_name
    )
    
    # Устанавливаем язык пользователя, если его нет
    user_data = get_user_data(message.from_user.id)
    if user_data and not user_data.get('language_code'):
        # Получаем язык из Telegram клиента
        user_lang = message.from_user.language_code or 'en'
        if user_lang not in ['ru', 'en']:
            user_lang = 'en'
        Localization.set_user_language(message.from_user.id, user_lang)
    
    # Затем получаем и сохраняем ссылку на аватар пользователя
    update_user_avatar(message.from_user.id, message.from_user)
    
    payload = message.text.split()[1] if len(message.text.split()) > 1 else ''
    url = f"{WEB_APP_URL}?ref={payload}"

    # ОБРАБОТКА РЕФЕРАЛА
    if payload and payload.isdigit():
        referrer_id = int(payload)
        
        try:
            # Проверяем, что реферер существует
            referrer_check = supabase.table('users') \
                .select('telegram') \
                .eq('telegram', referrer_id) \
                .execute()
            
            if referrer_check.data:
                # СОХРАНЯЕМ from_refer ДЛЯ ТЕКУЩЕГО ПОЛЬЗОВАТЕЛЯ
                save_referrer_to_user(message.from_user.id, referrer_id)
                
                # Получаем имя текущего пользователя для регистрации реферала
                user_data_current = get_user_data(message.from_user.id)
                if user_data_current and user_data_current.get('name'):
                    # Регистрируем реферала в друзьях
                    register_ref_sync(user_data_current['name'], payload)
                    print(f"✅ Реферал обработан: {message.from_user.id} от {payload}")
                else:
                    print(f"⚠️ У пользователя {message.from_user.id} нет имени в базе")
            else:
                print(f"⚠️ Реферер с ID {referrer_id} не существует в базе")
                
        except Exception as e:
            print(f"❌ Ошибка регистрации реферала: {e}")

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Open Drops", web_app=types.WebAppInfo(url)))
    markup.add(types.InlineKeyboardButton('Join the community', url='https://t.me/official_drops'))
    
    # Используем локализованное приветствие
    welcome_text = Localization.get_text(
        message.from_user.id, 
        'welcome', 
        name=message.from_user.first_name
    )
    
    photo_instruction_Amahasla = open(r"bot/picture/bot_section.png", 'rb')
    bot.send_photo(message.chat.id, photo=photo_instruction_Amahasla, 
                caption=welcome_text, 
                reply_markup=markup, parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data == 'language_menu')
def language_menu_callback(call):
    """Обработчик меню выбора языка"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🇷🇺 Русский", callback_data="set_lang_ru"),
        types.InlineKeyboardButton("🇬🇧 English", callback_data="set_lang_en")
    )
    markup.add(types.InlineKeyboardButton(
        Localization.get_text(call.from_user.id, 'main_menu_button'),
        callback_data='menu'
    ))
    
    bot.edit_message_text(
        "🌐 Select language / Выберите язык:",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup
    )


@bot.message_handler(commands=['avatar'])
def get_avatar_command(message):
    """Команда для получения ссылки на аватар"""
    # Убеждаемся, что пользователь существует
    ensure_user_exists(message.from_user.id)
    
    success = update_user_avatar(message.from_user.id, message.from_user)
    
    if success:
        # Получаем сохраненные данные из базы
        user_data = get_user_data(message.from_user.id)
        if user_data and user_data.get('avatar_link'):
            avatar_url = user_data['avatar_link'].get('url')
            user_name = user_data['avatar_link'].get('name', 'Неизвестно')
            bot.reply_to(message, f"🔗 Ваша ссылка на аватар:\n{avatar_url}\n👤 Имя: {user_name}")
            
            # Выводим в консоль для отладки
            print(f"📊 Данные аватара из базы для пользователя {message.from_user.id}:")
            print(f"   URL: {avatar_url}")
            print(f"   Имя: {user_name}")
            print(f"   Полные данные: {user_data['avatar_link']}")
        else:
            bot.reply_to(message, "❌ Не удалось получить ссылку на аватар из базы данных")
    else:
        bot.reply_to(message, "❌ Не удалось обновить аватар в базе данных")


@bot.message_handler(commands=['update_avatar'])
def update_avatar_command(message):
    """Команда для принудительного обновления аватара"""
    # Убеждаемся, что пользователь существует
    ensure_user_exists(message.from_user.id)
    
    success = update_user_avatar(message.from_user.id, message.from_user)
    if success:
        bot.reply_to(message, "✅ Аватар успешно обновлен в базе данных")
    else:
        bot.reply_to(message, "❌ Не удалось обновить аватар")


@bot.message_handler(commands=['debug_avatar'])
def debug_avatar_command(message):
    """Команда для отладки аватара"""
    user_data = get_user_data(message.from_user.id)
    
    debug_info = f"""
🔍 Отладочная информация для пользователя {message.from_user.id}:

📊 Данные из базы:
{user_data}

🖼 Аватар в базе:
{user_data.get('avatar_link') if user_data else 'Нет данных'}
"""
    bot.reply_to(message, f"```{debug_info}```", parse_mode='Markdown')


@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    # Убеждаемся, что пользователь существует
    ensure_user_exists(message.from_user.id)
    
    # Получаем и сохраняем ссылку на аватар пользователя
    update_user_avatar(message.from_user.id, message.from_user)
    
    # Проверка секретного кода
    if message.text == SECRET_CODE:
        nft_access_users.add(message.from_user.id)
        bot.reply_to(message, "🔓 Доступ к NFT функциям активирован!")
        return
    
    # Обработка массива NFT данных в формате Python (с одинарными кавычками)
    if message.text.startswith('[') and message.text.endswith(']'):
        try:
            # Пытаемся распарсить как JSON (с двойными кавычками)
            try:
                nft_array = json.loads(message.text)
            except json.JSONDecodeError:
                # Если не получается как JSON, пробуем распарсить как Python literal
                nft_array = ast.literal_eval(message.text)
            
            if isinstance(nft_array, list) and len(nft_array) > 0:
                processed_count = 0
                for nft_item in nft_array:
                    if isinstance(nft_item, dict) and 'url' in nft_item and 'name' in nft_item and 'from_user' in nft_item:
                        nft_url = nft_item['url']
                        nft_name = nft_item['name']
                        recipient_id = nft_item['from_user']
                        
                        # Проверяем, что ID состоит только из цифр
                        if not str(recipient_id).isdigit():
                            bot.reply_to(message, f"❌ ID пользователя должен содержать только цифры: {recipient_id}")
                            continue
                        
                        # Убеждаемся, что получатель существует в базе
                        ensure_user_exists(recipient_id)
                        
                        # Получаем и сохраняем аватар получателя
                        # Для получателя мы не можем получить объект пользователя, поэтому передаем None
                        update_user_avatar(recipient_id, None)
                        
                        # Получаем данные о NFT
                        try:
                            headers = {'User-Agent': 'Mozilla/5.0'}
                            response = requests.get(nft_url, headers=headers)
                            response.raise_for_status()
                            data = extract_data(response.text)
                            
                            # Извлекаем характеристики Model, Backdrop и Symbol
                            model = data['table_data'].get('Model', 'не указано')
                            backdrop = data['table_data'].get('Backdrop', 'не указано')
                            symbol = data['table_data'].get('Symbol', 'не указано')
                            
                            # Получаем текущие NFT пользователя
                            user_data = supabase.table('users').select('nft_links').eq('telegram', recipient_id).execute()
                            current_links = user_data.data[0].get('nft_links', []) if user_data.data else []
                            
                            # Создаем объект NFT с характеристиками
                            nft_data = {
                                'name': nft_name,
                                'url': nft_url,
                                'model': model,
                                'backdrop': backdrop,
                                'symbol': symbol
                            }
                            
                            # Проверяем, есть ли уже такой NFT в списке
                            nft_exists = False
                            for item in current_links:
                                if isinstance(item, dict) and item.get('url') == nft_url:
                                    nft_exists = True
                                    break
                            
                            # Добавляем новый NFT (если его ещё нет)
                            if not nft_exists:
                                updated_links = current_links + [nft_data]
                                supabase.table('users').update({'nft_links': updated_links}).eq('telegram', recipient_id).execute()
                            
                            # Сохраняем метаданные в отдельную таблицу
                            nft_id = nft_url.split('/')[-1]
                            save_nft_metadata(nft_id, nft_name, model, backdrop, symbol, recipient_id, None)
                            
                            # Отправляем уведомление получателю
                            try:
                                bot.send_message(recipient_id, f"🎁 NFT добавлен в ваш профиль!\nНазвание: {nft_name}\nСсылка: {nft_url}\nModel: {model}\nBackdrop: {backdrop}\nSymbol: {symbol}")
                            except Exception as e:
                                print(f"Не удалось отправить уведомление пользователю {recipient_id}: {e}")
                            
                            processed_count += 1
                            
                        except Exception as e:
                            print(f"Ошибка обработки NFT {nft_url}: {e}")
                            continue
                
                if processed_count > 0:
                    bot.reply_to(message, f"✅ Успешно обработано {processed_count} NFT из массива")
                else:
                    bot.reply_to(message, "❌ Не удалось обработать ни один NFT из массива")
            else:
                bot.reply_to(message, "❌ Неверный формат массива NFT данных")
                
        except (json.JSONDecodeError, SyntaxError, ValueError) as e:
            bot.reply_to(message, f"❌ Ошибка парсинга данных: {str(e)}")
        except Exception as e:
            bot.reply_to(message, f"⚠️ Ошибка обработки массива NFT: {str(e)}")
            print(f"Ошибка обработки массива NFT: {e}")
    
    # Обработка обычных NFT ссылок (для пользователей с доступом)
    elif message.from_user.id in nft_access_users and re.match(r'https?://t\.me/nft/[\w-]+', message.text):
        handle_nft_link(message)
    

def handle_nft_link(message, nft_url=None):
    try:
        url = nft_url if nft_url else message.text
        nft_id = url.split('/')[-1]
        
        # Получаем данные о NFT
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = extract_data(response.text)
        
        # Извлекаем характеристики Model, Backdrop и Symbol
        model = data['table_data'].get('Model', 'не указано')
        backdrop = data['table_data'].get('Backdrop', 'не указано')
        symbol = data['table_data'].get('Symbol', 'не указано')
        
        # Сохраняем метаданные в базу (если нужно)
        save_nft_metadata(nft_id, data['title'] or 'Неизвестно', model, backdrop, symbol, message.from_user.id, message.from_user)
        
        # Формируем сообщение с характеристиками
        caption = f"🎁 NFT Анимация\n\n🏷 ID: {nft_id}\n"
        if data['title']:
            caption += f"📌 {data['title']}\n"
        if data['description']:
            caption += f"📝 {data['description']}\n"
        if data['table_data']:
            caption += "\n📊 Характеристики:\n"
            for key, value in data['table_data'].items():
                caption += f"  • {key}: {value}\n"
        
        # Отправляем характеристики
        bot.send_message(message.chat.id, caption)
        
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка при получении информации о NFT: {str(e)}")


@bot.callback_query_handler(func=lambda call: call.data.startswith(('send_link_', 'get_html_')))
def handle_nft_actions(call):
    nft_id = call.data.split('_')[-1]
    if call.data.startswith('send_link_'):
        # Отправка ссылки на NFT
        bot.send_message(call.message.chat.id, f"🔗 Ссылка на NFT:\nhttps://t.me/nft/{nft_id}")
    elif call.data.startswith('get_html_'):
        # Отправка HTML страницы с анимацией
        html_content = create_nft_html(nft_id)
        with open(f"{nft_id}.html", 'w', encoding='utf-8') as f:
            f.write(html_content)
        with open(f"{nft_id}.html", 'rb') as f:
            bot.send_document(call.message.chat.id, f)
        os.remove(f"{nft_id}.html")


def create_nft_html(nft_id):
    """Создает HTML страницу с анимацией NFT"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
      <script src="https://cdnjs.cloudflare.com/ajax/libs/bodymovin/5.12.2/lottie.min.js"></script>
      <style>
        body {{
          display: flex;
          justify-content: center;
          align-items: center;
          height: 100vh;
          margin: 0;
          background-color: #f0f0f0;
        }}
        #animation {{
          width: 500px;
          height: 500px;
          overflow: visible;
        }}
      </style>
    </head>
    <body>
      <div id="animation"></div>
      <script>
        const animation = lottie.loadAnimation({{
          container: document.getElementById("animation"),
          renderer: "svg",
          loop: true,
          autoplay: true,
          path: "https://nft.fragment.com/gift/{nft_id}.lottie.json"
        }});
      </script>
    </body>
    </html>
    """


def get_user_telegram_id(username):
    """
    Получает telegram_id пользователя по его имени
    """
    try:
        print(f"🔍 Поиск telegram_id для пользователя: {username}")
        response = supabase.table('users').select('telegram').eq('name', username).execute()
        
        if response.data and len(response.data) > 0:
            telegram_id = response.data[0]['telegram']
            print(f"✅ Найден telegram_id {telegram_id} для пользователя {username}")
            return telegram_id
        else:
            print(f"❌ Пользователь {username} не найден в базе")
            return None
    except Exception as e:
        print(f"❌ Ошибка получения telegram_id пользователя {username}: {e}")
        return None


def save_offer_to_db(offer_data):
    """
    Сохраняет предложение в базу данных
    """
    try:
        # Создаем таблицу offers если её нет
        create_offers_table()
        
        response = supabase.table('offers').insert({
            'item_id': offer_data['item_id'],
            'seller_name': offer_data['seller_name'],
            'buyer_name': offer_data['buyer_name'],
            'current_price': offer_data['current_price'],
            'offer_price': offer_data['offer_price'],
            'nft_data': offer_data.get('nft_data', {}),
            'nft_name': offer_data.get('nft_name', ''),
            'nft_id': offer_data.get('nft_id', ''),
            'seller_telegram_id': offer_data.get('seller_telegram_id'),
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }).execute()
        
        if response.data:
            print(f"✅ Предложение сохранено в базу данных: {offer_data['item_id']}")
            return True
        return False
        
    except Exception as e:
        print(f"❌ Ошибка сохранения предложения в базу: {e}")
        return False


def get_offer_data(item_id):
    """
    Получает данные предложения по item_id
    """
    try:
        response = supabase.table('offers').select('*').eq('item_id', item_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        print(f"❌ Ошибка получения данных предложения {item_id}: {e}")
        return None


def update_offer_status(item_id, status):
    """
    Обновляет статус предложения
    """
    try:
        supabase.table('offers').update({
            'status': status,
            'updated_at': datetime.now().isoformat()
        }).eq('item_id', item_id).execute()
        
        print(f"✅ Статус предложения {item_id} обновлен на: {status}")
        return True
    except Exception as e:
        print(f"❌ Ошибка обновления статуса предложения: {e}")
        return False


def create_offers_table():
    """
    Создает таблицу offers если она не существует
    """
    try:
        # Проверяем существование таблицы
        response = supabase.table('offers').select('*').limit(1).execute()
        print("✅ Таблица offers существует")
        return True
    except Exception as e:
        print(f"❌ Таблица offers не существует или ошибка доступа: {e}")
        return False


def delete_offer(offer_id):
    """
    Удаляет предложение из базы данных по ID предложения
    """
    try:
        response = supabase.table('offers').delete().eq('id', offer_id).execute()
        
        if response.data:
            print(f"✅ Предложение {offer_id} удалено из базы данных")
            return True
        else:
            print(f"⚠️ Предложение {offer_id} не найдено для удаления")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка удаления предложения {offer_id}: {e}")
        return False
    

def cleanup_old_offers():
    """
    Очищает старые отклоненные или завершенные предложения
    """
    try:
        # Удаляем предложения старше 7 дней
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        
        response = supabase.table('offers') \
                         .delete() \
                         .lt('created_at', week_ago) \
                         .execute()
        
        if response.data:
            print(f"✅ Очищено {len(response.data)} старых предложений")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка очистки старых предложений: {e}")
        return False


# Глобальный словарь для отслеживания обрабатываемых офферов
processed_offers = {}


def check_market_item_exists(item_id):
    """
    Проверяет, существует ли объявление на рынке
    """
    try:
        response = supabase.table('market').select('*').eq('item_id', item_id).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"❌ Ошибка проверки объявления {item_id}: {e}")
        return False


def find_market_item_by_id(market_id):
    """
    Находит объявление в market по ID записи
    """
    try:
        response = supabase.table('market').select('*').eq('id', int(market_id)).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        print(f"❌ Ошибка поиска объявления по ID {market_id}: {e}")
        return None


def check_nft_ownership(username, nft_data):
    """
    Проверяет, владеет ли пользователь данным NFT
    """
    try:
        user_data = get_user_data_by_name(username)
        if not user_data:
            return False
            
        user_nfts = user_data.get('nft_links', [])
        nft_url = nft_data.get('url')
        
        for nft in user_nfts:
            if isinstance(nft, dict) and nft.get('url') == nft_url:
                return True
        return False
    except Exception as e:
        print(f"❌ Ошибка проверки владения NFT: {e}")
        return False


def send_offer_notification(offer_data):
    """
    Отправляет уведомление о предложении цены продавцу в Telegram
    """
    try:
        seller_telegram_id = offer_data['seller_telegram_id']
        buyer_name = offer_data['buyer_name']
        nft_name = offer_data['nft_name']
        nft_id = offer_data['nft_id']
        current_price = offer_data['current_price']
        offer_price = offer_data['offer_price']
        item_id = offer_data['item_id']
        
        # Получаем локализованные тексты для продавца
        message = f"""
{Localization.get_text(seller_telegram_id, 'new_offer_title')}

{Localization.get_text(seller_telegram_id, 'nft_label')} {nft_name} #{nft_id}
{Localization.get_text(seller_telegram_id, 'current_price_label')} {current_price} TON
{Localization.get_text(seller_telegram_id, 'offer_price_label')} {offer_price} TON

{Localization.get_text(seller_telegram_id, 'accept_offer_question')}

/item_{item_id}
        """
        
        # Создаем инлайн-кнопки с локализованными текстами
        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton(
                Localization.get_text(seller_telegram_id, 'accept_button'), 
                callback_data=f'accept_offer:{item_id}'
            ),
            InlineKeyboardButton(
                Localization.get_text(seller_telegram_id, 'decline_button'), 
                callback_data=f'decline_offer:{item_id}'
            )
        )
        keyboard.add(
            InlineKeyboardButton(
                Localization.get_text(seller_telegram_id, 'view_item_button'), 
                url=f'https://shop/{item_id}'
            )
        )
        
        # Отправляем сообщение продавцу
        bot.send_message(
            seller_telegram_id,
            message,
            parse_mode='Markdown',
            reply_markup=keyboard
        )
        
        print(f"✅ Уведомление о предложении отправлено продавцу {seller_telegram_id}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка отправки уведомления о предложении: {e}")
        return False


@bot.callback_query_handler(func=lambda call: call.data.startswith(('accept_offer:', 'decline_offer:')))
def handle_offer_response(call):
    """
    Обрабатывает ответы на предложения цены с защитой от двойной обработки
    """
    try:
        print(f"\n{'='*50}")
        print(f"🔔 НАЧАЛО ОБРАБОТКИ: {call.data}")
        print(f"👤 Пользователь: {call.from_user.id} (@{call.from_user.username})")
        print(f"{'='*50}")
        
        # Разбираем callback_data
        parts = call.data.split(':')
        if len(parts) < 2:
            print(f"❌ Ошибка: неверный формат callback_data: {call.data}")
            bot.answer_callback_query(call.id, "❌ Ошибка формата", show_alert=True)
            return False
        
        action = parts[0]
        offer_uuid = parts[1]
        
        print(f"📋 Действие: {action}")
        print(f"📋 UUID оффера: {offer_uuid}")
        
        # ПОЛУЧАЕМ ДАННЫЕ ОФФЕРА С БЛОКИРОВКОЙ
        print(f"🔍 Запрашиваем оффер с UUID: {offer_uuid} из базы...")
        try:
            offer_response = supabase.table('offers').select('*').eq('id', offer_uuid).execute()
        except Exception as e:
            print(f"❌ Ошибка при запросе к БД: {e}")
            bot.answer_callback_query(call.id, "❌ Ошибка базы данных", show_alert=True)
            return False
        
        if not offer_response.data or len(offer_response.data) == 0:
            print(f"❌ Оффер с UUID {offer_uuid} не найден в базе")
            bot.answer_callback_query(call.id, "❌ Предложение не найдено", show_alert=True)
            return False
        
        offer = offer_response.data[0]
        print(f"✅ Оффер найден:")
        print(f"   - UUID: {offer.get('id')}")
        print(f"   - Статус: {offer.get('status')}")
        print(f"   - Продавец: {offer.get('seller_name')}")
        print(f"   - Покупатель: {offer.get('buyer_name')}")
        print(f"   - Сумма: {offer.get('offer_price')} TON")
        print(f"   - Item ID: {offer.get('item_id')}")
        
        # ========== ПРОВЕРКА СТАТУСА ==========
        current_status = offer.get('status', 'unknown')
        print(f"📊 Текущий статус оффера: {current_status}")
        
        # Разрешенные статусы для обработки
        if current_status != 'pending':
            print(f"❌ Оффер уже обработан (статус: {current_status})")
            
            status_messages = {
                'accepted': "✅ Это предложение уже было принято",
                'rejected': "❌ Это предложение уже было отклонено",
                'refunded': "💰 Средства по этому предложению уже возвращены",
                'processing': "⏳ Это предложение уже обрабатывается"
            }
            
            message = status_messages.get(current_status, f"❌ Предложение уже {current_status}")
            bot.answer_callback_query(call.id, message, show_alert=True)
            
            # Обновляем сообщение в чате
            try:
                nft_name = offer.get('nft_name', 'NFT')
                nft_id = offer.get('nft_id', '')
                offer_price = offer.get('offer_price', 0)
                
                status_text = {
                    'accepted': f"✅ *Предложение уже принято*",
                    'rejected': f"❌ *Предложение уже отклонено*",
                    'refunded': f"💰 *Предложение неактуально*\n\nСредства возвращены покупателю",
                    'processing': f"⏳ *Предложение обрабатывается*\n\nПожалуйста, подождите..."
                }.get(current_status, f"❌ *Предложение неактуально*")
                
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=f"{status_text}\n\n🎁 Товар: {nft_name} #{nft_id}\n💵 Сумма: {offer_price} TON",
                    parse_mode='Markdown'
                )
            except:
                pass
            
            return False
        
        # Получаем telegram_id продавца
        seller_name = offer.get('seller_name')
        print(f"🔍 Ищем telegram_id продавца {seller_name}...")
        
        seller_telegram = get_user_telegram_id(seller_name)
        print(f"📊 Результат: seller_telegram = {seller_telegram}")
        
        if not seller_telegram:
            print(f"❌ Не удалось найти telegram_id для продавца {seller_name}")
            bot.answer_callback_query(call.id, "❌ Продавец не найден", show_alert=True)
            return False
        
        # Проверяем, что продавец - это тот, кто нажимает кнопку
        if str(seller_telegram) != str(call.from_user.id):
            print(f"❌ Ошибка прав: пользователь {call.from_user.id} не является продавцом (продавец: {seller_telegram})")
            bot.answer_callback_query(call.id, "❌ Это не ваше объявление", show_alert=True)
            return False
        
        print(f"✅ Права подтверждены")
        
        # ===== АТОМАРНАЯ БЛОКИРОВКА ОФФЕРА =====
        # Пытаемся изменить статус на 'processing' только если он всё еще 'pending'
        print(f"🔒 Попытка атомарной блокировки оффера...")
        
        try:
            lock_result = supabase.table('offers') \
                .update({
                    'status': 'processing',
                    'updated_at': datetime.now().isoformat()
                }) \
                .eq('id', offer_uuid) \
                .eq('status', 'pending') \
                .execute()
            
            # Проверяем, был ли обновлен оффер
            if not lock_result.data or len(lock_result.data) == 0:
                print(f"❌ Не удалось заблокировать оффер - статус изменился")
                
                # Получаем актуальный статус
                check = supabase.table('offers').select('status').eq('id', offer_uuid).execute()
                if check.data:
                    actual_status = check.data[0].get('status')
                    print(f"📊 Актуальный статус: {actual_status}")
                    
                    status_messages = {
                        'accepted': "✅ Это предложение уже было принято",
                        'rejected': "❌ Это предложение уже было отклонено",
                        'refunded': "💰 Средства по этому предложению уже возвращены",
                        'processing': "⏳ Это предложение уже обрабатывается"
                    }
                    
                    message = status_messages.get(actual_status, f"❌ Предложение уже {actual_status}")
                    bot.answer_callback_query(call.id, message, show_alert=True)
                else:
                    bot.answer_callback_query(call.id, "❌ Оффер не найден", show_alert=True)
                
                return False
            
            print(f"✅ Оффер успешно заблокирован (статус -> processing)")
            
        except Exception as e:
            print(f"❌ Ошибка при блокировке оффера: {e}")
            bot.answer_callback_query(call.id, "❌ Ошибка блокировки", show_alert=True)
            return False
        
        # Вызываем соответствующую функцию обработки
        if action == 'accept_offer':
            print(f"✅ Выбрано действие: ПРИНЯТЬ")
            result = process_offer_acceptance(call, offer, offer_uuid)
            
            # Если произошла ошибка, возвращаем статус обратно на pending
            if not result:
                print(f"⚠️ Ошибка при принятии оффера, возвращаем статус на pending")
                try:
                    supabase.table('offers').update({
                        'status': 'pending',
                        'updated_at': datetime.now().isoformat()
                    }).eq('id', offer_uuid).execute()
                except:
                    pass
            return result
            
        elif action == 'decline_offer':
            print(f"❌ Выбрано действие: ОТКЛОНИТЬ")
            result = process_offer_decline(call, offer, offer_uuid)
            
            # Если произошла ошибка, возвращаем статус обратно на pending
            if not result:
                print(f"⚠️ Ошибка при отклонении оффера, возвращаем статус на pending")
                try:
                    supabase.table('offers').update({
                        'status': 'pending',
                        'updated_at': datetime.now().isoformat()
                    }).eq('id', offer_uuid).execute()
                except:
                    pass
            return result
        else:
            print(f"❌ Неизвестное действие: {action}")
            bot.answer_callback_query(call.id, "❌ Неизвестное действие", show_alert=True)
            return False
        
    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        
        try:
            bot.answer_callback_query(call.id, "❌ Ошибка обработки", show_alert=True)
        except:
            pass
        return False
    
def process_offer_acceptance(call, offer, offer_uuid):
    """Обрабатывает принятие оффера и возвращает средства по другим офферам"""
    try:
        print(f"✅ ПРИНЯТИЕ оффера {offer_uuid}")
        
        # ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА СТАТУСА
        # Проверяем, что статус все еще 'processing' (не изменился за время вызова)
        check_response = supabase.table('offers').select('status').eq('id', offer_uuid).execute()
        if not check_response.data:
            print(f"❌ Оффер не найден при повторной проверке")
            bot.answer_callback_query(call.id, "❌ Оффер не найден", show_alert=True)
            return False
        
        current_status = check_response.data[0].get('status')
        if current_status != 'processing':
            print(f"❌ Статус оффера изменился на {current_status}")
            status_messages = {
                'accepted': "✅ Это предложение уже было принято",
                'rejected': "❌ Это предложение уже было отклонено",
                'refunded': "💰 Средства по этому предложению уже возвращены",
            }
            message = status_messages.get(current_status, f"❌ Оффер уже {current_status}")
            bot.answer_callback_query(call.id, message, show_alert=True)
            return False
        
        # Получаем текущее время в UTC+5
        current_time = get_tyumen_time()
        print(f"🕐 Текущее время (UTC+5): {current_time}")
        
        # Получаем данные
        item_id = offer['item_id']
        seller_name = offer['seller_name']
        buyer_name = offer['buyer_name']
        offer_price = float(offer['offer_price'])
        nft_data = offer.get('nft_data', {})
        nft_name = offer.get('nft_name', 'NFT')
        nft_id = offer.get('nft_id', '')
        
        # Получаем ссылку на изображение
        image_link = None
        if isinstance(nft_data, dict):
            image_link = nft_data.get('url')
        if not image_link:
            image_link = f"https://t.me/nft/{nft_name}-{nft_id}".lower().replace(' ', '')
        
        print(f"📊 Детали сделки:")
        print(f"   - Item ID: {item_id}")
        print(f"   - Продавец: {seller_name}")
        print(f"   - Покупатель: {buyer_name}")
        print(f"   - Цена: {offer_price} TON")
        print(f"   - NFT: {nft_name} #{nft_id}")
        print(f"   - Ссылка: {image_link}")
        
        # Получаем данные покупателя и продавца ДО всех операций
        buyer_data = get_user_data_by_name(buyer_name)
        seller_data = get_user_data_by_name(seller_name)
        
        if not buyer_data:
            print(f"❌ Покупатель {buyer_name} не найден")
            bot.answer_callback_query(call.id, "❌ Покупатель не найден", show_alert=True)
            # Возвращаем статус на pending
            supabase.table('offers').update({
                'status': 'pending',
                'updated_at': datetime.now().isoformat()
            }).eq('id', offer_uuid).execute()
            return False
            
        if not seller_data:
            print(f"❌ Продавец {seller_name} не найден")
            bot.answer_callback_query(call.id, "❌ Продавец не найден", show_alert=True)
            # Возвращаем статус на pending
            supabase.table('offers').update({
                'status': 'pending',
                'updated_at': datetime.now().isoformat()
            }).eq('id', offer_uuid).execute()
            return False
        
        # 1. Проверяем наличие товара в market
        print(f"🔍 Проверка наличия товара в market...")
        market_response = supabase.table('market').select('*').eq('item_id', item_id).execute()
        
        if not market_response.data or len(market_response.data) == 0:
            print(f"❌ Товар {item_id} не найден в market")
            
            # Возвращаем средства только этому покупателю
            refund_offer_to_buyer(offer)
            
            # СОЗДАЕМ ЗАПИСЬ О ВОЗВРАТЕ ДЛЯ ПОКУПАТЕЛЯ
            refund_operation = {
                "id": f"op_{int(datetime.utcnow().timestamp() * 1000)}_{''.join(random.choices(string.ascii_lowercase + string.digits, k=9))}",
                "type": "refund",
                "nftId": nft_id,
                "amount": str(offer_price),
                "itemId": item_id,
                "reason": "item_not_found",
                "status": "completed",
                "nftName": nft_name,
                "offerId": offer_uuid,
                "currency": "TON",
                "timestamp": current_time,
                "walletAddress": buyer_name,
                "transactionHash": None
            }
            
            print(f"📝 Создана операция возврата: {json.dumps(refund_operation, ensure_ascii=False)}")
            
            # Обновляем историю покупателя
            buyer_history = buyer_data.get('operation_history', []) or []
            buyer_updated = [refund_operation] + buyer_history
            update_result = supabase.table('users').update({
                'operation_history': buyer_updated[:100]
            }).eq('name', buyer_name).execute()
            
            print(f"✅ История покупателя обновлена, результат: {update_result}")
            
            # УДАЛЯЕМ ОФФЕР ИЗ БД
            supabase.table('offers').delete().eq('id', offer_uuid).execute()
            print(f"🗑️ Оффер {offer_uuid} удален из БД")
            
            # Обновляем сообщение
            try:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=f"❌ *Товар не найден*\n\n💰 Средства возвращены покупателю *{buyer_name}*\n💵 Сумма: *{offer_price} TON*",
                    parse_mode='Markdown'
                )
            except Exception as e:
                print(f"⚠️ Ошибка при обновлении сообщения: {e}")
            
            bot.answer_callback_query(call.id, "❌ Товар не найден, средства возвращены", show_alert=True)
            return True
        
        # ТОВАР НАЙДЕН - ПРОДОЛЖАЕМ ОБРАБОТКУ
        market_item = market_response.data[0]
        market_id = market_item['id']
        print(f"✅ Товар найден в market, ID записи: {market_id}")
        
        # НАХОДИМ ВСЕ ДРУГИЕ АКТИВНЫЕ ОФФЕРЫ
        other_offers = supabase.table('offers').select('*').eq('item_id', item_id).eq('status', 'pending').neq('id', offer_uuid).execute()
        other_offers_list = other_offers.data or []
        print(f"📊 Найдено {len(other_offers_list)} других активных офферов")
        
        # ВОЗВРАЩАЕМ СРЕДСТВА ПО ДРУГИМ ОФФЕРАМ
        for other in other_offers_list:
            try:
                other_buyer = other['buyer_name']
                other_amount = float(other['offer_price'])
                other_uuid = other['id']
                
                print(f"🔄 Возврат {other_amount} TON покупателю {other_buyer}")
                
                # Возвращаем средства
                refund_offer_to_buyer(other)
                
                # СОЗДАЕМ ЗАПИСЬ О ВОЗВРАТЕ ДЛЯ ДРУГОГО ПОКУПАТЕЛЯ
                refund_op = {
                    "id": f"op_{int(datetime.utcnow().timestamp() * 1000)}_{''.join(random.choices(string.ascii_lowercase + string.digits, k=9))}",
                    "type": "refund",
                    "nftId": other.get('nft_id', nft_id),
                    "amount": str(other_amount),
                    "itemId": item_id,
                    "reason": "item_sold_to_other",
                    "status": "completed",
                    "nftName": other.get('nft_name', nft_name),
                    "offerId": other_uuid,
                    "currency": "TON",
                    "timestamp": current_time,
                    "walletAddress": other_buyer,
                    "transactionHash": None
                }
                
                print(f"📝 Создана операция возврата для {other_buyer}: {json.dumps(refund_op, ensure_ascii=False)}")
                
                # Обновляем историю другого покупателя
                other_data = get_user_data_by_name(other_buyer)
                if other_data:
                    other_history = other_data.get('operation_history', []) or []
                    other_updated = [refund_op] + other_history
                    supabase.table('users').update({
                        'operation_history': other_updated[:100]
                    }).eq('name', other_buyer).execute()
                    print(f"✅ История {other_buyer} обновлена")
                
                # УДАЛЯЕМ ДРУГОЙ ОФФЕР ИЗ БД
                supabase.table('offers').delete().eq('id', other_uuid).execute()
                print(f"🗑️ Оффер {other_uuid} удален из БД")
                
                # Уведомляем другого покупателя
                other_telegram = get_user_telegram_id(other_buyer)
                if other_telegram:
                    try:
                        refund_msg = f"💰 *Возврат средств*\n\nВаше предложение на *{nft_name}* было отклонено, так как NFT был продан другому покупателю.\n\n💸 *{other_amount} TON* возвращены на ваш баланс."
                        bot.send_message(other_telegram, refund_msg, parse_mode='Markdown')
                        print(f"📨 Уведомление отправлено {other_buyer}")
                    except Exception as e:
                        print(f"⚠️ Ошибка отправки уведомления: {e}")
                
            except Exception as e:
                print(f"❌ Ошибка при возврате по офферу {other.get('id')}: {e}")
                continue
        
        # ПЕРЕДАЕМ NFT ПОКУПАТЕЛЮ
        current_links = buyer_data.get('nft_links', []) or []
        print(f"📊 Текущие NFT покупателя: {len(current_links)} шт.")
        
        updated_nft = nft_data.copy() if isinstance(nft_data, dict) else {}
        updated_nft['from_user'] = seller_name
        updated_nft['acquired_at'] = current_time
        
        updated_links = current_links + [updated_nft]
        update_result = supabase.table('users').update({
            'nft_links': updated_links
        }).eq('name', buyer_name).execute()
        
        print(f"✅ NFT передан покупателю, результат: {update_result}")
        
        # УДАЛЯЕМ ОБЪЯВЛЕНИЕ
        delete_result = supabase.table('market').delete().eq('id', market_id).execute()
        print(f"🗑️ Объявление удалено, результат: {delete_result}")
        
        # УДАЛЯЕМ NFT У ПРОДАВЦА
        seller_links = seller_data.get('nft_links', []) or []
        nft_url = nft_data.get('url') if isinstance(nft_data, dict) else None
        updated_seller_links = [n for n in seller_links if isinstance(n, dict) and n.get('url') != nft_url]
        
        update_result = supabase.table('users').update({
            'nft_links': updated_seller_links
        }).eq('name', seller_name).execute()
        
        print(f"✅ NFT удален у продавца, результат: {update_result}")
        
        # ПЕРЕВОДИМ СРЕДСТВА ПРОДАВЦУ
        seller_amount = offer_price * 0.98
        commission = offer_price * 0.02
        
        current_seller_balance = float(seller_data.get('ton_balance', 0))
        new_seller_balance = current_seller_balance + seller_amount
        
        update_result = supabase.table('users').update({
            'ton_balance': new_seller_balance
        }).eq('name', seller_name).execute()
        
        print(f"💰 Продавцу переведено {seller_amount} TON, результат: {update_result}")
        
        # ===== СОЗДАЕМ ЗАПИСИ В ИСТОРИЮ ОПЕРАЦИЙ =====
        print(f"📝 СОЗДАНИЕ ЗАПИСЕЙ В ИСТОРИЮ...")
        
        # Для ПОКУПАТЕЛЯ (offer_purchase)
        purchase_operation = {
            "id": f"op_{int(datetime.utcnow().timestamp() * 1000)}_{''.join(random.choices(string.ascii_lowercase + string.digits, k=9))}",
            "link": image_link,
            "type": "offer_purchase",
            "nftId": nft_id,
            "amount": str(offer_price),
            "seller": seller_name,
            "nftName": nft_name,
            "offerId": offer_uuid,
            "currency": "TON",
            "timestamp": current_time,
            "commission": str(commission),
            "walletAddress": buyer_name,
            "seller_username": seller_name
        }
        
        # Для ПРОДАВЦА (offer_sale)
        sale_operation = {
            "id": f"op_{int(datetime.utcnow().timestamp() * 1000)}_{''.join(random.choices(string.ascii_lowercase + string.digits, k=9))}",
            "link": image_link,
            "type": "offer_sale",
            "buyer": buyer_name,
            "nftId": nft_id,
            "amount": str(seller_amount),
            "nftName": nft_name,
            "offerId": offer_uuid,
            "currency": "TON",
            "timestamp": current_time,
            "commission": str(commission),
            "walletAddress": seller_name,
            "buyer_username": buyer_name
        }
        
        print(f"📝 Запись для покупателя: {json.dumps(purchase_operation, ensure_ascii=False, indent=2)}")
        print(f"📝 Запись для продавца: {json.dumps(sale_operation, ensure_ascii=False, indent=2)}")
        
        # Обновляем историю покупателя
        buyer_history = buyer_data.get('operation_history', []) or []
        print(f"📊 Текущая история покупателя: {len(buyer_history)} записей")
        
        buyer_updated = [purchase_operation] + buyer_history
        buyer_updated = buyer_updated[:100]
        
        update_result = supabase.table('users').update({
            'operation_history': buyer_updated
        }).eq('name', buyer_name).execute()
        
        print(f"✅ История покупателя обновлена, результат: {update_result}")
        
        # Проверяем, что запись сохранилась
        check_result = supabase.table('users').select('operation_history').eq('name', buyer_name).execute()
        if check_result.data:
            saved_count = len(check_result.data[0].get('operation_history', []))
            print(f"✅ Проверка: в истории покупателя теперь {saved_count} записей")
        
        # Обновляем историю продавца
        seller_history = seller_data.get('operation_history', []) or []
        print(f"📊 Текущая история продавца: {len(seller_history)} записей")
        
        seller_updated = [sale_operation] + seller_history
        seller_updated = seller_updated[:100]
        
        update_result = supabase.table('users').update({
            'operation_history': seller_updated
        }).eq('name', seller_name).execute()
        
        print(f"✅ История продавца обновлена, результат: {update_result}")
        
        # Проверяем, что запись сохранилась
        check_result = supabase.table('users').select('operation_history').eq('name', seller_name).execute()
        if check_result.data:
            saved_count = len(check_result.data[0].get('operation_history', []))
            print(f"✅ Проверка: в истории продавца теперь {saved_count} записей")
        
        # ОБНОВЛЯЕМ СТАТУС ПРИНЯТОГО ОФФЕРА
        supabase.table('offers').update({
            'status': 'accepted',
            'updated_at': datetime.now().isoformat()
        }).eq('id', offer_uuid).execute()
        
        # УДАЛЯЕМ ПРИНЯТЫЙ ОФФЕР ИЗ БД
        supabase.table('offers').delete().eq('id', offer_uuid).execute()
        print(f"🗑️ Принятый оффер {offer_uuid} удален из БД")
        
        # Отправляем уведомления
        buyer_telegram = get_user_telegram_id(buyer_name)
        if buyer_telegram:
            buyer_message = f"🎉 *Ваше предложение принято!*\n\n*{nft_name}* #{nft_id}\n💵 Сумма сделки: *{offer_price} TON*\n\n✅ *NFT успешно передан вам!*"
            bot.send_message(buyer_telegram, buyer_message, parse_mode='Markdown')
            print(f"📨 Уведомление отправлено покупателю {buyer_telegram}")
        
        # Обновляем сообщение продавца
        seller_message = f"✅ *Вы приняли предложение!*\n\n🎁 Товар: *{nft_name}* #{nft_id}\n💵 Сумма: *{offer_price} TON*\n💰 Вы получили: *{seller_amount:.2f} TON*\n\nСделка завершена!"
        
        try:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=seller_message,
                parse_mode='Markdown'
            )
            print(f"📨 Сообщение продавца обновлено")
        except Exception as e:
            print(f"⚠️ Не удалось отредактировать сообщение: {e}")
            bot.send_message(call.message.chat.id, seller_message, parse_mode='Markdown')
        
        bot.answer_callback_query(call.id, "✅ Сделка завершена!")
        print(f"✅ Сделка завершена успешно! Создано записей: покупка для {buyer_name}, продажа для {seller_name}, возврат для {len(other_offers_list)} других")
        print(f"🕐 Время сделки: {current_time}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в process_offer_acceptance: {e}")
        import traceback
        traceback.print_exc()
        
        # В случае ошибки возвращаем статус на pending
        try:
            supabase.table('offers').update({
                'status': 'pending',
                'updated_at': datetime.now().isoformat()
            }).eq('id', offer_uuid).execute()
            print(f"✅ Статус оффера возвращен на pending после ошибки")
        except:
            pass
            
        return False


def process_offer_decline(call, offer, offer_uuid):
    """Обрабатывает отклонение оффера и возвращает средства"""
    try:
        print(f"❌ ОТКЛОНЕНИЕ оффера {offer_uuid}")
        
        # ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА СТАТУСА
        check_response = supabase.table('offers').select('status').eq('id', offer_uuid).execute()
        if not check_response.data:
            print(f"❌ Оффер не найден при повторной проверке")
            bot.answer_callback_query(call.id, "❌ Оффер не найден", show_alert=True)
            return False
        
        current_status = check_response.data[0].get('status')
        if current_status != 'processing':
            print(f"❌ Статус оффера изменился на {current_status}")
            status_messages = {
                'accepted': "✅ Это предложение уже было принято",
                'rejected': "❌ Это предложение уже было отклонено",
                'refunded': "💰 Средства по этому предложению уже возвращены",
            }
            message = status_messages.get(current_status, f"❌ Оффер уже {current_status}")
            bot.answer_callback_query(call.id, message, show_alert=True)
            return False
        
        # Получаем текущее время в UTC+5
        current_time = get_tyumen_time()
        print(f"🕐 Текущее время (UTC+5): {current_time}")
        
        buyer_name = offer['buyer_name']
        offer_price = float(offer['offer_price'])
        nft_name = offer.get('nft_name', 'NFT')
        nft_id = offer.get('nft_id', '')
        item_id = offer.get('item_id', '')
        
        # Получаем данные покупателя
        buyer_data = get_user_data_by_name(buyer_name)
        if not buyer_data:
            print(f"❌ Покупатель {buyer_name} не найден")
            bot.answer_callback_query(call.id, "❌ Покупатель не найден", show_alert=True)
            # Возвращаем статус на pending
            supabase.table('offers').update({
                'status': 'pending',
                'updated_at': datetime.now().isoformat()
            }).eq('id', offer_uuid).execute()
            return False
        
        # Возвращаем средства
        refund_offer_to_buyer(offer)
        
        # СОЗДАЕМ ЗАПИСЬ О ВОЗВРАТЕ ДЛЯ ПОКУПАТЕЛЯ
        refund_operation = {
            "id": f"op_{int(datetime.utcnow().timestamp() * 1000)}_{''.join(random.choices(string.ascii_lowercase + string.digits, k=9))}",
            "type": "refund",
            "nftId": nft_id,
            "amount": str(offer_price),
            "itemId": item_id,
            "reason": "seller_declined",
            "status": "completed",
            "nftName": nft_name,
            "offerId": offer_uuid,
            "currency": "TON",
            "timestamp": current_time,
            "walletAddress": buyer_name,
            "transactionHash": None
        }
        
        print(f"📝 Запись о возврате: {json.dumps(refund_operation, ensure_ascii=False, indent=2)}")
        
        # Обновляем историю покупателя
        buyer_history = buyer_data.get('operation_history', []) or []
        print(f"📊 Текущая история покупателя: {len(buyer_history)} записей")
        
        buyer_updated = [refund_operation] + buyer_history
        buyer_updated = buyer_updated[:100]
        
        update_result = supabase.table('users').update({
            'operation_history': buyer_updated
        }).eq('name', buyer_name).execute()
        
        print(f"✅ История покупателя обновлена, результат: {update_result}")
        
        # Проверяем, что запись сохранилась
        check_result = supabase.table('users').select('operation_history').eq('name', buyer_name).execute()
        if check_result.data:
            saved_count = len(check_result.data[0].get('operation_history', []))
            print(f"✅ Проверка: в истории покупателя теперь {saved_count} записей")
        
        # УДАЛЯЕМ ОФФЕР ИЗ БД
        supabase.table('offers').delete().eq('id', offer_uuid).execute()
        print(f"🗑️ Отклоненный оффер {offer_uuid} удален из БД")
        
        # Уведомляем покупателя
        buyer_telegram = get_user_telegram_id(buyer_name)
        if buyer_telegram:
            buyer_message = f"❌ *Ваше предложение отклонено*\n\n*{nft_name}* #{nft_id}\n💵 Ваше предложение: *{offer_price} TON*\n\n💰 *Средства возвращены на ваш баланс!*"
            bot.send_message(buyer_telegram, buyer_message, parse_mode='Markdown')
            print(f"📨 Уведомление отправлено покупателю {buyer_telegram}")
        
        # Обновляем сообщение продавца
        seller_message = f"❌ *Вы отклонили предложение*\n\n🎁 Товар: *{nft_name}* #{nft_id}\n💵 Предложение: *{offer_price} TON*"
        
        try:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=seller_message,
                parse_mode='Markdown'
            )
            print(f"📨 Сообщение продавца обновлено")
        except Exception as e:
            print(f"⚠️ Не удалось отредактировать сообщение: {e}")
            bot.send_message(call.message.chat.id, seller_message, parse_mode='Markdown')
        
        bot.answer_callback_query(call.id, "❌ Предложение отклонено")
        print(f"✅ Оффер {offer_uuid} отклонен, средства возвращены {buyer_name}, запись создана")
        print(f"🕐 Время отклонения: {current_time}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в process_offer_decline: {e}")
        import traceback
        traceback.print_exc()
        
        # В случае ошибки возвращаем статус на pending
        try:
            supabase.table('offers').update({
                'status': 'pending',
                'updated_at': datetime.now().isoformat()
            }).eq('id', offer_uuid).execute()
            print(f"✅ Статус оффера возвращен на pending после ошибки")
        except:
            pass
            
        return False
    
     
def refund_offer_to_buyer(offer):
    """Возвращает средства покупателю по офферу"""
    try:
        buyer_name = offer['buyer_name']
        offer_price = float(offer['offer_price'])
        
        print(f"💰 Возврат {offer_price} TON покупателю {buyer_name}")
        
        # Получаем данные покупателя
        buyer_data = get_user_data_by_name(buyer_name)
        if not buyer_data:
            print(f"❌ Покупатель {buyer_name} не найден")
            return False
        
        current_balance = float(buyer_data.get('ton_balance', 0))
        new_balance = current_balance + offer_price
        
        print(f"📊 Баланс покупателя: было {current_balance}, стало {new_balance}")
        
        # Обновляем баланс
        supabase.table('users').update({
            'ton_balance': new_balance
        }).eq('name', buyer_name).execute()
        
        print(f"✅ Баланс обновлен")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка возврата средств: {e}")
        return False

def transfer_nft_to_buyer(buyer_name, nft_data):
    """Передает NFT покупателю"""
    try:
        buyer_data = get_user_data_by_name(buyer_name)
        if not buyer_data:
            raise Exception(f"Покупатель {buyer_name} не найден")
        
        # Получаем username для поля from_user
        buyer_username = buyer_data.get('username', '')
        from_user_value = f"@{buyer_username}" if buyer_username else buyer_name
        
        # Обновляем NFT объект
        updated_nft = nft_data.copy() if isinstance(nft_data, dict) else {}
        updated_nft['from_user'] = from_user_value
        updated_nft['user_name'] = str(buyer_data.get('telegram', ''))
        updated_nft['acquired_at'] = datetime.now().isoformat()
        
        # Добавляем в коллекцию покупателя
        current_links = buyer_data.get('nft_links', [])
        if current_links is None:
            current_links = []
        
        nft_exists = False
        nft_url = updated_nft.get('url')
        
        for item in current_links:
            if isinstance(item, dict) and item.get('url') == nft_url:
                item.update(updated_nft)
                nft_exists = True
                break
        
        if not nft_exists:
            updated_links = current_links + [updated_nft]
        else:
            updated_links = current_links
        
        supabase.table('users').update({
            'nft_links': updated_links
        }).eq('name', buyer_name).execute()
        
        print(f"✅ NFT передан {buyer_name}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка передачи NFT: {e}")
        raise e


def remove_nft_from_seller(seller_name, nft_data):
    """Удаляет NFT у продавца"""
    try:
        seller_data = get_user_data_by_name(seller_name)
        if not seller_data:
            return False
        
        current_links = seller_data.get('nft_links', [])
        if current_links is None:
            current_links = []
            
        nft_url = nft_data.get('url')
        
        updated_links = []
        for nft in current_links:
            if isinstance(nft, dict) and nft.get('url') != nft_url:
                updated_links.append(nft)
        
        supabase.table('users').update({
            'nft_links': updated_links
        }).eq('name', seller_name).execute()
        
        print(f"✅ NFT удален у продавца {seller_name}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка удаления NFT: {e}")
        return False


def update_commission_stats(amount, commission_type):
    """Обновляет статистику комиссий (исправленная версия)"""
    try:
        # Проверяем существование таблицы configurations
        try:
            # Получаем текущие значения
            response = supabase.table('configurations').select('*').eq('key', 'commission_stats').execute()
            
            if response.data and len(response.data) > 0:
                current_stats = response.data[0].get('value', {})
                if isinstance(current_stats, str):
                    try:
                        current_stats = json.loads(current_stats)
                    except:
                        current_stats = {}
                
                total = float(current_stats.get('total', 0)) + amount
                count = int(current_stats.get('count', 0)) + 1
                
                supabase.table('configurations').update({
                    'value': {
                        'total': total,
                        'count': count,
                        'last_amount': amount,
                        'last_date': datetime.now().isoformat(),
                        'type': commission_type
                    }
                }).eq('key', 'commission_stats').execute()
            else:
                supabase.table('configurations').insert({
                    'key': 'commission_stats',
                    'value': {
                        'total': amount,
                        'count': 1,
                        'last_amount': amount,
                        'last_date': datetime.now().isoformat(),
                        'type': commission_type
                    }
                }).execute()
                
            print(f"✅ Статистика комиссий обновлена: +{amount} {commission_type}")
            
        except Exception as e:
            print(f"⚠️ Таблица configurations не существует или ошибка доступа: {e}")
            # Пробуем создать таблицу или просто логируем
            pass
            
    except Exception as e:
        print(f"⚠️ Ошибка обновления статистики: {e}")


def get_user_telegram_id(username):
    """Получает telegram_id пользователя по имени"""
    try:
        response = supabase.table('users').select('telegram').eq('name', username).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]['telegram']
        return None
    except Exception as e:
        print(f"❌ Ошибка получения telegram_id: {e}")
        return None


def get_user_data_by_name(username):
    """Получает данные пользователя по имени"""
    try:
        response = supabase.table('users').select('*').eq('name', username).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        print(f"❌ Ошибка получения данных пользователя {username}: {e}")
        return None

def update_config_commission(amount, commission_type):
    """Обновляет статистику комиссий"""
    try:
        # Получаем текущие значения
        response = supabase.table('configurations').select('*').eq('key', 'commission_stats').execute()
        
        if response.data:
            current_stats = response.data[0].get('value', {})
            total = float(current_stats.get('total', 0)) + amount
            count = int(current_stats.get('count', 0)) + 1
            
            supabase.table('configurations').update({
                'value': {
                    'total': total,
                    'count': count,
                    'last_amount': amount,
                    'last_date': datetime.now().isoformat(),
                    'type': commission_type
                }
            }).eq('key', 'commission_stats').execute()
        else:
            supabase.table('configurations').insert({
                'key': 'commission_stats',
                'value': {
                    'total': amount,
                    'count': 1,
                    'last_amount': amount,
                    'last_date': datetime.now().isoformat(),
                    'type': commission_type
                }
            }).execute()
            
    except Exception as e:
        print(f"⚠️ Ошибка обновления статистики: {e}")

async def check_seller_owns_nft_simple(seller_name, item_id):
    """
    Упрощенная проверка - только market по seller и item_id
    """
    try:
        print(f"🔍 ПРОСТАЯ проверка: seller={seller_name}, item_id={item_id}")
        
        # Прямой запрос к market
        response = supabase.table('market').select('*') \
            .eq('seller', seller_name) \
            .eq('item_id', item_id) \
            .execute()
        
        print(f"📊 Результат запроса: {len(response.data)} записей")
        
        if response.data and len(response.data) > 0:
            print(f"✅ Объявление найдено!")
            print(f"   Данные: {response.data[0]}")
            return True
        else:
            print(f"❌ Объявление НЕ найдено!")
            print(f"   Seller '{seller_name}' не имеет объявления с item_id '{item_id}'")
            
            # Для отладки: проверим какие объявления есть у этого seller
            all_seller_items = supabase.table('market').select('item_id') \
                .eq('seller', seller_name).execute()
            
            if all_seller_items.data:
                print(f"📋 Все объявления продавца {seller_name}:")
                for item in all_seller_items.data:
                    print(f"   - {item.get('item_id')}")
            else:
                print(f"📋 У продавца {seller_name} нет активных объявлений")
            
            return False
            
    except Exception as e:
        print(f"❌ Ошибка простой проверки: {e}")
        return False


async def check_seller_owns_nft(seller_name, item_id, nft_data=None):
    """
    Проверяет, владеет ли продавец данным NFT
    ИСКЛЮЧИТЕЛЬНО в таблице market по seller и item_id
    """
    try:
        print(f"🔍 Проверка владения NFT для продавца: {seller_name}")
        print(f"📋 Ищем объявление с item_id: {item_id}")
        
        # 1. Проверяем market - ищем запись у этого продавца С ЭТИМ item_id
        market_query = supabase.table('market') \
            .select('*') \
            .eq('seller', seller_name) \
            .eq('item_id', item_id) \
            .single()
        
        market_item = await market_query.execute()
        
        if not market_item.data:
            print(f"❌ Объявление не найдено!")
            print(f"   - Seller: {seller_name}")
            print(f"   - Item ID: {item_id}")
            print(f"   - В базе нет такого объявления у этого продавца")
            return False
        
        print(f"✅ Объявление найдено в market!")
        print(f"📊 Данные объявления:")
        print(f"   - ID: {market_item.data.get('id')}")
        print(f"   - Seller: {market_item.data.get('seller')}")
        print(f"   - Item ID: {market_item.data.get('item_id')}")
        print(f"   - Created at: {market_item.data.get('created_at')}")
        
        # Дополнительная проверка NFT данных (опционально)
        if nft_data:
            item_nft_data = market_item.data.get('nft_object')
            if isinstance(item_nft_data, str):
                try:
                    item_nft_data = json.loads(item_nft_data)
                except:
                    item_nft_data = {}
            
            nft_url = nft_data.get('url', '')
            item_nft_url = item_nft_data.get('url', '')
            
            if nft_url and item_nft_url and nft_url == item_nft_url:
                print(f"✅ URL NFT совпадает: {nft_url}")
            else:
                print(f"⚠️ URL NFT не совпадает или отсутствует")
                print(f"   Ищем: {nft_url}")
                print(f"   Нашли: {item_nft_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка проверки владения: {e}")
        import traceback
        traceback.print_exc()
        return False


def extract_nft_id(nft_data):
    """Извлекает ID NFT из разных форматов данных"""
    try:
        if isinstance(nft_data, str):
            try:
                nft_data = json.loads(nft_data)
            except:
                # Если это не JSON, пробуем извлечь ID из строки
                match = re.search(r'-(\d+)(?:\.|$)', nft_data)
                return match.group(1) if match else None
        
        if isinstance(nft_data, dict):
            # 1. Из URL
            url = nft_data.get('url', '')
            if url:
                match = re.search(r'-(\d+)(?:\.|$)', url)
                if match:
                    return match.group(1)
            
            # 2. Из специального поля nft_id
            if nft_data.get('nft_id'):
                return str(nft_data['nft_id'])
            
            # 3. Из gift_id
            if nft_data.get('gift_id'):
                return str(nft_data['gift_id'])
            
            # 4. Из имени (последние цифры)
            name = nft_data.get('name', '')
            if name:
                match = re.search(r'#(\d+)', name)
                if match:
                    return match.group(1)
                
                match = re.search(r'(\d+)$', name)
                if match:
                    return match.group(1)
        
        return None
    except Exception as e:
        print(f"❌ Ошибка извлечения NFT ID: {e}")
        return None


def cancel_offers_for_sold_item(item_id):
    """
    Автоматическая отмена всех офферов при продаже NFT
    """
    try:
        print(f"🔄 Автоматическая отмена офферов для проданного товара {item_id}")
        
        # 1. Находим все активные офферы
        response = supabase.table('offers').select('*').eq('item_id', item_id).in_('status', ['pending', 'active']).execute()        
        offers = response.data if response.data else []
        
        if not offers:
            print(f"✅ Нет активных офферов для товара {item_id}")
            return True
        
        print(f"📋 Найдено {len(offers)} активных офферов")
        
        # 2. Возвращаем средства и отменяем каждый оффер
        for offer in offers:
            try:
                buyer_name = offer['buyer_name']
                offer_price = float(offer['offer_price'])
                
                print(f"💸 Возвращаем {offer_price} TON покупателю {buyer_name}")
                
                # Получаем текущий баланс покупателя
                buyer_data = get_user_data_by_name(buyer_name)
                if not buyer_data:
                    print(f"❌ Покупатель {buyer_name} не найден")
                    continue
                
                # Обновляем баланс покупателя
                current_balance = float(buyer_data.get('ton_balance', 0))
                new_balance = current_balance + offer_price
                
                supabase.table('users') \
                        .update({'ton_balance': str(new_balance)}) \
                        .eq('name', buyer_name) \
                        .execute()
                
                # Обновляем статус оффера
                supabase.table('offers') \
                        .update({
                            'status': 'refunded',
                            'updated_at': datetime.now().isoformat(),
                            'refund_reason': 'item_sold_to_other'
                        }) \
                        .eq('id', offer['id']) \
                        .execute()
                
                print(f"✅ Средства возвращены {buyer_name}")
                
                # Уведомляем покупателя
                try:
                    buyer_telegram_id = get_user_telegram_id(buyer_name)
                    if buyer_telegram_id:
                        nft_name = offer.get('nft_name', 'NFT')
                        buyer_message = Localization.get_text(
                            buyer_telegram_id,
                            'refund_other_sale',
                            nft_name=nft_name,
                            offer_price=offer_price,
                            new_balance=new_balance
                        )
                        
                        bot.send_message(
                            buyer_telegram_id,
                            buyer_message,
                            parse_mode='Markdown'
                        )
                except Exception as notify_error:
                    print(f"⚠️ Не удалось уведомить покупателя: {notify_error}")
                    
            except Exception as e:
                print(f"❌ Ошибка обработки оффера {offer.get('id')}: {e}")
                continue
        
        print(f"✅ Все офферы для товара {item_id} обработаны")
        return True
        
    except Exception as e:
        print(f"❌ Критическая ошибка отмены офферов: {e}")
        return False


def record_offer_accept_activity(offer_data):
    """
    Записывает активность принятия оффера
    """
    try:
        activity_data = {
            'user_name': offer_data['buyer_name'],
            'operation_type': 'purchase',
            'item_id': offer_data['item_id'],
            'nft_type': 'html_nft',  # или извлечь из nft_data
            'nft_object': offer_data.get('nft_data', {}),
            'price_per_unit': offer_data['offer_price'],
            'currency': 'TON',
            'amount': 1,
            'total_price': offer_data['offer_price'],
            'counterparty': offer_data['seller_name'],
            'created_at': datetime.now().isoformat()
        }
        
        supabase.table('activity_history').insert(activity_data).execute()
        print(f"✅ Активность оффера записана для {offer_data['item_id']}")
        
    except Exception as e:
        print(f"⚠️ Не удалось записать активность: {e}")


def decline_offer_with_refund(offer_data, call):
    """
    Автоматически отклоняет оффер и возвращает средства покупателю
    """
    try:
        item_id = offer_data['item_id']
        buyer_name = offer_data['buyer_name']
        offer_price = offer_data['offer_price']
        nft_name = offer_data.get('nft_name', 'Неизвестный NFT')
        
        # Возвращаем средства покупателю
        refund_offer_to_buyer(offer_data)
        
        # Обновляем статус предложения
        update_offer_status(item_id, 'auto_declined')
        
        # Уведомляем покупателя
        buyer_telegram_id = get_user_telegram_id(buyer_name)
        if buyer_telegram_id:
            try:
                buyer_message = Localization.get_text(
                    buyer_telegram_id,
                    'offer_auto_declined_buyer',
                    nft_name=nft_name,
                    nft_id=offer_data.get('nft_id', 'unknown'),
                    offer_price=offer_price
                )
                
                bot.send_message(
                    buyer_telegram_id,
                    buyer_message,
                    parse_mode='Markdown'
                )
            except Exception as e:
                print(f"⚠️ Не удалось уведомить покупателя: {e}")
        
        # Обновляем сообщение у продавца
        try:
            seller_message = Localization.get_text(
                call.from_user.id if call else None,
                'offer_auto_declined_seller',
                buyer_name=buyer_name,
                nft_name=nft_name,
                nft_id=offer_data.get('nft_id', 'unknown'),
                offer_price=offer_price
            )
            
            if call:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=seller_message,
                    parse_mode='Markdown'
                )
        except Exception as e:
            print(f"⚠️ Не удалось обновить сообщение продавца: {e}")
        
        # Удаляем оффер из базы данных
        delete_offer(item_id)
        
        print(f"✅ Оффер {item_id} автоматически отклонен (продавец не владеет NFT)")
        
    except Exception as e:
        print(f"❌ Ошибка автоматического отклонения оффера: {e}")



def remove_nft_from_seller(seller_name, nft_data):
    """
    Удаляет NFT из коллекции продавца
    """
    try:
        seller_data = get_user_data_by_name(seller_name)
        if not seller_data:
            raise Exception(f"Продавец {seller_name} не найден")
        
        current_links = seller_data.get('nft_links', [])
        nft_url = nft_data.get('url')
        
        # Фильтруем NFT, удаляя тот, который передается
        updated_links = []
        for nft in current_links:
            if isinstance(nft, dict) and nft.get('url') != nft_url:
                updated_links.append(nft)
        
        # Обновляем базу данных
        supabase.table('users').update({
            'nft_links': updated_links
        }).eq('name', seller_name).execute()
        
        print(f"✅ NFT удален из коллекции продавца {seller_name}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка удаления NFT у продавца: {e}")
        # Не блокируем выполнение из-за этой ошибки
        return False


def transfer_nft_to_buyer_fast(buyer_name, nft_data):
    """
    Быстрая передача NFT покупателю с обновлением данных владельца
    """
    try:
        # Получаем данные покупателя
        buyer_data = get_user_data_by_name(buyer_name)
        if not buyer_data:
            raise Exception(f"Покупатель {buyer_name} не найден")
        
        # Извлекаем данные покупателя из базы
        buyer_telegram_id = buyer_data.get('telegram', '')
        buyer_username = buyer_data.get('username', '')
        
        # Подготавливаем username покупателя (с @ если есть)
        if buyer_username:
            from_user_value = f"@{buyer_username}" if not buyer_username.startswith('@') else buyer_username
        else:
            # Если username нет, используем имя
            from_user_value = buyer_name
        
        # Обновляем NFT объект с данными покупателя
        updated_nft_data = nft_data.copy() if isinstance(nft_data, dict) else {}
        
        # Обновляем поля владельца
        updated_nft_data['from_user'] = from_user_value
        updated_nft_data['user_name'] = str(buyer_telegram_id) if buyer_telegram_id else ''
        
        # Обновляем дату получения (текущее время)
        updated_nft_data['acquired_at'] = datetime.now().isoformat()
        
        print(f"📝 Обновлен NFT объект для покупателя {buyer_name}:")
        print(f"   - from_user: {updated_nft_data.get('from_user')}")
        print(f"   - user_name: {updated_nft_data.get('user_name')}")
        print(f"   - acquired_at: {updated_nft_data.get('acquired_at')}")
        
        # Получаем текущие NFT покупателя
        current_links = buyer_data.get('nft_links', [])
        
        # Проверяем, нет ли уже такого NFT
        nft_exists = False
        nft_url = updated_nft_data.get('url')
        
        for item in current_links:
            if isinstance(item, dict) and item.get('url') == nft_url:
                nft_exists = True
                # Если NFT уже есть, обновляем его данные
                item.update(updated_nft_data)
                break
        
        if not nft_exists:
            # Добавляем обновленный NFT в коллекцию покупателя
            updated_links = current_links + [updated_nft_data]
        else:
            # Используем существующий список (данные уже обновлены)
            updated_links = current_links
        
        # Обновляем базу данных
        supabase.table('users').update({
            'nft_links': updated_links
        }).eq('name', buyer_name).execute()
        
        print(f"✅ NFT передан покупателю {buyer_name} с обновленными данными владельца")
        return updated_nft_data  # Возвращаем обновленный объект
        
    except Exception as e:
        print(f"❌ Ошибка передачи NFT покупателю: {e}")
        raise e


def delete_market_item_fast(item_id):
    """
    Быстрое удаление объявления с рынка по item_id или id
    """
    try:
        print(f"🗑️ Пытаемся удалить объявление с item_id: {item_id}")
        
        # Сначала пытаемся найти объявление по item_id
        response = supabase.table('market').select('id, item_id, seller').eq('item_id', item_id).execute()
        
        if response.data and len(response.data) > 0:
            market_item = response.data[0]
            market_id = market_item.get('id')
            print(f"📊 Найдено объявление:")
            print(f"   - ID в market: {market_id}")
            print(f"   - item_id: {market_item.get('item_id')}")
            print(f"   - seller: {market_item.get('seller')}")
            
            # Удаляем по ID из таблицы market
            delete_response = supabase.table('market').delete().eq('id', market_id).execute()
            
            if delete_response.data:
                print(f"✅ Объявление {item_id} (market_id: {market_id}) успешно удалено с рынка")
                return True
            else:
                print(f"⚠️ Не удалось удалить объявление {item_id} (market_id: {market_id})")
                return False
        else:
            print(f"❌ Объявление с item_id {item_id} не найдено в market")
            
            # Для отладки: покажем все объявления
            all_market_items = supabase.table('market').select('id, item_id, seller').execute()
            print(f"📋 Все объявления в market:")
            for item in all_market_items.data:
                print(f"   - ID: {item.get('id')}, item_id: {item.get('item_id')}, seller: {item.get('seller')}")
            
            return False
            
    except Exception as e:
        print(f"❌ Ошибка удаления объявления {item_id}: {e}")
        import traceback
        traceback.print_exc()
        return False


def record_offer_accept_activity_async(offer_data):
    """
    Асинхронная запись активности (не блокирует основной поток)
    """
    try:
        import threading
        
        def save_activity():
            try:
                activity_data = {
                    'user_name': offer_data['buyer_name'],
                    'operation_type': 'offer_accepted',
                    'item_id': offer_data['item_id'],
                    'nft_type': offer_data.get('nft_type', 'unknown'),
                    'nft_object': offer_data.get('nft_data', {}),
                    'price_per_unit': offer_data['offer_price'],
                    'currency': 'TON',
                    'amount': 1,
                    'total_price': offer_data['offer_price'],
                    'counterparty': offer_data['seller_name'],
                    'created_at': datetime.now().isoformat()
                }
                
                supabase.table('activity_history').insert(activity_data).execute()
                print(f"✅ Активность оффера записана для {offer_data['item_id']}")
                
            except Exception as e:
                print(f"⚠️ Не удалось записать активность: {e}")
        
        # Запускаем в отдельном потоке
        thread = threading.Thread(target=save_activity)
        thread.daemon = True
        thread.start()
        
    except Exception as e:
        print(f"⚠️ Ошибка запуска потока для записи активности: {e}")


def refund_offer_to_buyer(offer):
    """Возвращает средства покупателю по офферу"""
    try:
        buyer_name = offer['buyer_name']
        offer_price = float(offer['offer_price'])
        
        print(f"💰 Возврат {offer_price} TON покупателю {buyer_name}")
        
        # Получаем данные покупателя
        buyer_data = get_user_data_by_name(buyer_name)
        if not buyer_data:
            print(f"❌ Покупатель {buyer_name} не найден")
            return False
        
        current_balance = float(buyer_data.get('ton_balance', 0))
        new_balance = current_balance + offer_price
        
        print(f"📊 Баланс покупателя: было {current_balance}, стало {new_balance}")
        
        # Обновляем баланс
        update_result = supabase.table('users').update({
            'ton_balance': new_balance
        }).eq('name', buyer_name).execute()
        
        print(f"✅ Баланс обновлен, результат: {update_result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка возврата средств: {e}")
        import traceback
        traceback.print_exc()
        return False
def update_user_balance(username, new_balance):
    """
    Обновляет баланс пользователя с повторными попытками
    """
    max_retries = 3
    for attempt in range(max_retries):
        try:
            supabase.table('users').update({
                'ton_balance': new_balance
            }).eq('name', username).execute()
            return True
            
        except Exception as e:
            print(f"⚠️ Попытка {attempt + 1} обновления баланса не удалась: {e}")
            if attempt < max_retries - 1:
                import time
                time.sleep(1)  # Ждем секунду перед повторной попыткой
            else:
                raise e


def get_user_data_by_name(username):
    """
    Получает данные пользователя по имени
    """
    try:
        response = supabase.table('users').select('*').eq('name', username).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        print(f"❌ Ошибка получения данных пользователя {username}: {e}")
        return None


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


def my_account(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    telegram_id = call.from_user.id
    markup = types.InlineKeyboardMarkup()
    user_data = get_user_data(telegram_id)
    if user_data:
        name = user_data.get('name', 'не указан')
        password = user_data.get('password', 'не указан')
        avatar_link = user_data.get('avatar_link', {})
        avatar_url = avatar_link.get('url', 'не указан') if avatar_link else 'не указан'
        avatar_name = avatar_link.get('name', 'не указан') if avatar_link else 'не указан'
        
        bot.send_message(call.message.chat.id, 
                        f"Ваши данные:\n\n👤 Никнейм: <code>{name}</code>\n🔑 Пароль: <code>{password}</code>\n🖼 Аватар: <code>{avatar_url}</code>\n📝 Имя в аватаре: <code>{avatar_name}</code>",
                        reply_markup=markup, parse_mode='HTML')
    elif (call.data == 'back'):
        bot.delete_message(call.message.chat.id, call.message.message_id)
    else:
        bot.send_message(call.message.chat.id, "Вы еще не зарегистрированы!")


def get_user_data(telegram_id):
    response = supabase.table('users').select('*').eq('telegram', telegram_id).execute()
    if response.data:
        return response.data[0]  # Возвращаем первую запись (если есть)
    return None


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
        # Если пользователь не существует, создаем новую запись с числовым ID
        numeric_id = generate_numeric_id()
        data['id'] = numeric_id
        data['telegram'] = telegram_id
        data['created_at'] = datetime.now().isoformat()
        supabase.table('users').insert(data).execute()
        print(f"Пользователь успешно зарегистрирован с ID: {numeric_id}!")


# Обработчик callback-запросов (оставлен для обратной совместимости)
@bot.callback_query_handler(func=lambda message: True)
def get_user_message(message):
    telegram_id = message.from_user.id
    
    # Убеждаемся, что пользователь существует
    ensure_user_exists(telegram_id)
    
    markup = types.InlineKeyboardMarkup()
    if message.data == 'garant':
        bot.delete_message(message.message.chat.id, message.message.message_id)
        markup.add(types.InlineKeyboardButton('⛓Гарант⛓', url ="https://t.me/amahaslareplenishment"))
        markup.add(types.InlineKeyboardButton('🏠Главное меню🏠', callback_data='menu'))
        bot.send_message(message.message.chat.id, "*🔑Гарант сделок🔑* \n\n_Кто такой «Гарант»?_\n•Гарант - человек, который поможет провести сделку безопасно как для потребителя, так и для продавца\n\n _Как проходит сделка с участием гаранта?_ \n1.Потребитель и продавец договариваются касательно оплаты гаранта (определяются кто будет платить за гаранта, можно разделить оплату на двоих, но передавать оплату гаранту должен только один участник сделки. То есть у кого то из участников сделки должна собраться сумма оплаты гаранта)\n2.Продавец отправляет товар(NFT), а потребитель - ожидает сообщение от гаранта о том, что NFT у него и готово к отправке. \nТакже один из участников сделки должен оплатить участие гаранта (Если вы договорились разделить оплату гаранта, то в данном случае сумма оплаты должна быть либо у потребителя, либо у продавца. *Будьте предельно осторожны при отправлении средств для оплаты гаранта*) \n3.Гарант отправляет сообщение потребителю о том, что NFT готово к отправке\n4.Потребитель сообщает о переводе средств продавцу и гарант проверяет квитанцию\n5.Если квитанция не фейковая и продавец подтвердил получение средств, в этом случае гарант передаёт NFT потребителю.\n\nОфициальный гарант - AMAHASLA (Имя, используемое при передаче NFT)" , reply_markup=markup, parse_mode='Markdown')
    if message.data == 'menu':
        # Получаем и сохраняем аватар при переходе в главное меню
        update_user_avatar(telegram_id, message.from_user)
        
        bot.delete_message(message.message.chat.id, message.message.message_id)
        payload = message.message.text.split()[1] if len(message.message.text.split()) > 1 else ''
        # Формируем URL с параметром ref
        url = f"{WEB_APP_URL}?ref={payload}"
        markup.add(types.InlineKeyboardButton('🔐Создать аккаунт🔐', callback_data='get_akk'))
        markup.add(types.InlineKeyboardButton('📱Услуга гаранта📱', callback_data='garant'))
        markup.add(types.InlineKeyboardButton('💰Пополнить аккаунт💰', callback_data='get_money'),types.InlineKeyboardButton('💰Купить NFT💰', callback_data='get_money_nft'))
        markup.add(types.InlineKeyboardButton("Запустить AMAHASLA", web_app=types.WebAppInfo(url)))
        markup.add(types.InlineKeyboardButton('Присоединиться к нам', url='https://t.me/amahaslacoin'))
        markup.add(types.InlineKeyboardButton('🌐 Language', callback_data='language_menu'))
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
        bot.send_message(message.message.chat.id, "*💰Пополнение баланса💰* \n \n Пополнить аккаунт вы можете через @Amahaslareplenishment. Оплата суммы пополнения аккаунта происходит через @*CryptoBot*, @*Wallet* или же *Telegram Stars*.\n\n Алгоритм оплаты:\n▾Вы выбираете сумму пополнения (пополнить можно не меньше 20000 Амахаслы - 0,3 TON)\n▾Отправляете оплату @Amahaslareplenishment и *ваш ID* \n▾Вы пополнили аккаунт!🎉 \n \n Перед пополнении обязательно ознакомьтесь с прайс-листом (_если вы отправили не соответсвующую сумму оплаты или неверный ID  - возврат средств не предусмотрен_)", reply_markup=markup, parse_mode='Markdown')
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
        # Получаем и сохраняем аватар при создании аккаунта
        update_user_avatar(telegram_id, message.from_user)
        
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

# start_monitoring()
start_unrecorded_monitoring()

bot.polling(none_stop=True)