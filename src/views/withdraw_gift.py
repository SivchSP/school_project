from pyrogram import Client
from pyrogram import raw, errors
import asyncio

API_ID = 26666823
API_HASH = "790b1c91775444bff0d4ab973d4c750d"

USERNAME = "@maga_dager"
MSG_ID = 48043

async def send_gift():
    """Простая функция отправки подарка @Basevme"""
    async with Client(
        "my_account",
        api_id=API_ID,
        api_hash=API_HASH
    ) as app:
        
        try:
            print("🎁 Отправка подарка @Basevme...")
            
            # Получаем пользователя
            user = await app.get_users(USERNAME)
            print(f"👤 Найден: {user.first_name or 'User'} (@{user.username})")
            
            # Передаем подарок
            peer = await app.resolve_peer(USERNAME)
            
            try:
                await app.invoke(raw.functions.payments.TransferStarGift(msg_id=MSG_ID, to_id=peer))
                return f"✅ Подарок отправлен {USERNAME} без оплаты!"
                
            except errors.PaymentRequired:
                invoice = raw.types.InputInvoiceStarGiftTransfer(msg_id=MSG_ID, to_id=peer)
                form = await app.invoke(raw.functions.payments.GetPaymentForm(invoice=invoice))
                await app.invoke(raw.functions.payments.SendStarsForm(form_id=form.form_id, invoice=invoice))
                return f"✅ Подарок отправлен {USERNAME} с оплатой!"
                
        except errors.UsernameNotOccupied:
            return f"❌ Пользователь {USERNAME} не найден"
        except errors.MsgIdInvalid:
            return f"❌ Подарок с ID {MSG_ID} не найден"
        except Exception as e:
            return f"❌ Ошибка: {e}"


if __name__ == "__main__":
    result = asyncio.run(send_gift())
    print(result)