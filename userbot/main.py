import os
import asyncio
from typing import AsyncGenerator, Dict, Any
from pyrogram import Client
from pyrogram.types import ChatMember
from pyrogram.enums import ChatMemberStatus
from pyrogram import raw

API_ID = "none"
API_HASH = "none"
GIFT_IDS = [ 
    5170145012310081615,
5170233102089322756,
5170250947678437525,
5168103777563050263,
5170144170496491616,
5170314324215857265,
5170564780938756245,
5168043875654172773,
5170690322832818290,
5170521118301225164,
6028601630662853006,
5886387158889005864,
5886756255493523118,
5884080014126745057,
5882129648002794519,
5834651202612102354,
5832279504491381684,
5832497899283415733,
5834918435477259676,
5832644211639321671,
5832371318007268701,
6014591077976114307,
6012607142387778152,
6012435906336654262,
6014675319464657779,
6014697240977737490,
5999277561060787166,
5999298447486747746,
5999116401002939514,
5902339509239940491,
5898012527257715797,
5900177027566142759,
5897607679345427347,
5830323722413671504,
5832325860073407546,
5830340739074097859,
5807641025165919973,
5773668482394620318,
5773725897517433693,
5773791997064119815,
6042113507581755979,
6005797617768858105,
6005659564635063386,
6005880141270483700,
6006064678835323371,
6005564615793050414,
6003456431095808759,
5998981470310368313,
5960747083030856414,
5963238670868677492,
5933793770951673155,
5933937398953018107,
5933770397739647689,
5933543975653737112,
5935877878062253519,
5933737850477478635,
5913351908466098791,
5895518353849582541,
5895328365971244193,
5897593557492957738,
5895544372761461960,
5897581235231785485,
5895603153683874485,
5872744075014177223,
5870972044522291836,
5871002671934079382,
5870661333703197240,
5870862540036113469,
5870720080265871962,
5868595669182186720,
5868348541058942091,
5868220813026526561,
5868503709637411929,
5868561433997870501,
5870784783948186838,
5868659926187901653,
5870947077877400011,
5868455043362980631,
6028426950047957932,
6028283532500009446,
6023917088358269866,
6023679164349940429,
6023752243218481939,
6003373314888696650,
6003767644426076664,
6001538689543439169,
6003643167683903930,
6003735372041814769,
6001473264306619020,
5983484377902875708,
5983259145522906006,
5983471780763796287,
5981132629905245483,
5980789805615678057,
5981026247860290310,
5933590374185435592,
5936017773737018241,
5935936766358847989,
5936043693864651359,
5936085638515261992,
5933531623327795414,
5933629604416717361,
5933671725160989227,
5936013938331222567,
5913442287462908725,
5915502858152706668,
5915733223018594841,
5915521180483191380,
5915550639663874519,
5913517067138499193,
5879737836550226478,
5882125812596999035,
5882252952218894938,
5859442703032386168,
5857140566201991735,
5856973938650776169,
5846226946928673709,
5846192273657692751,
5845776576658015084,
5825895989088617224,
5825801628657124140,
5825480571261813595,
5843762284240831056,
5841689550203650524,
5841632504448025405,
5841391256135008713,
5839038009193792264,
5841336413697606412,
5837063436634161765,
5836780359634649414,
5837059369300132790,
5821384757304362229,
5821205665758053411,
5821261908354794038,
5170594532177215681,
5167939598143193218,
5783075783622787539,
5782988952268964995,
5782984811920491178
]

async def get_client():
    # Создаем папку session если её нет
    session_dir = 'session'
    if not os.path.exists(session_dir):
        os.makedirs(session_dir)
        print("📁 Created session directory")
    
    # Используем абсолютный путь для избежания проблем с правами доступа
    session_path = os.path.abspath(os.path.join(session_dir, 'main'))
    
    client = Client(
        name=session_path,  # Абсолютный путь к сессии
        api_id=API_ID,
        api_hash=API_HASH,
        workdir=os.getcwd(),  # Указываем рабочую директорию
        system_version="4.16.30-vxCUSTOM"
    )
    
    try:
        await client.start()
        return client
    except Exception as e:
        print(f"❌ Error starting client: {e}")
        # Попробуем создать новую сессию
        try:
            await client.connect()
            # Запросим код авторизации
            sent_code = await client.send_code(API_HASH)
            print("📱 Please check your Telegram for authorization code")
            
            # Введите код вручную
            code = input("Enter the code you received: ")
            
            # Авторизуемся
            await client.sign_in(API_HASH, sent_code.phone_code_hash, code)
            
            # Сохраняем сессию
            await client.storage.save()
            await client.disconnect()
            
            # Перезапускаем
            await client.start()
            return client
            
        except Exception as auth_error:
            print(f"❌ Authorization failed: {auth_error}")
            raise

async def get_user_gifts(client: Client, user_id: int, username: str):
    result = []
    try:
        # Используем низкоуровневый API для получения подарков
        input_user = await client.resolve_peer(user_id)
        
        user_gifts = await client.invoke(
            raw.functions.payments.GetUserStarGifts(
                user_id=input_user,
                offset="",
                limit=100
            )
        )
        
        if hasattr(user_gifts, 'gifts') and user_gifts.gifts:
            for gift in user_gifts.gifts:
                # Проверяем условия фильтрации
                is_limited = getattr(gift, 'is_limited', False)
                is_upgraded = getattr(gift, 'is_upgraded', False)
                gift_id = getattr(gift, 'id', None)
                
                if is_limited and not is_upgraded and gift_id in GIFT_IDS:
                    result.append({
                        "gift": gift_id, 
                        "user_id": user_id, 
                        "username": username,
                        "stars": getattr(gift, 'stars', 0),
                        "title": getattr(gift, 'title', '')
                    })
        
    except Exception as e:
        print(f"Ошибка при получении подарков пользователя {username} ({user_id}): {e}")
        return []
    
    return result

async def get_user_gifts_detailed(client: Client, user_id: int, username: str = None):
    """Детальная информация о подарках пользователя"""
    try:
        input_user = await client.resolve_peer(user_id)
        
        user_gifts = await client.invoke(
            raw.functions.payments.GetUserStarGifts(
                user_id=input_user,
                offset="",
                limit=100
            )
        )
        
        if hasattr(user_gifts, 'gifts') and user_gifts.gifts:
            print(f"\n🎁 Подарки пользователя {username or user_id}:")
            print("=" * 60)
            
            for i, gift in enumerate(user_gifts.gifts, 1):
                print(f"{i}. ID: {getattr(gift, 'id', 'N/A')}")
                print(f"   Title: {getattr(gift, 'title', 'N/A')}")
                print(f"   Stars: {getattr(gift, 'stars', 0)}")
                print(f"   Limited: {getattr(gift, 'is_limited', False)}")
                print(f"   Upgraded: {getattr(gift, 'is_upgraded', False)}")
                print(f"   Collectible: {getattr(gift, 'is_collectible', False)}")
                print("-" * 40)
            
            return len(user_gifts.gifts)
        else:
            print(f"ℹ️ У пользователя {username or user_id} нет подарков")
            return 0
            
    except Exception as e:
        print(f"❌ Ошибка при получении подарков пользователя {username or user_id}: {e}")
        return 0

async def simple_auth():
    """Простая авторизация без сложных путей"""
    client = Client(
        name="my_userbot",
        api_id=API_ID,
        api_hash=API_HASH,
        workdir=os.getcwd(),
        system_version="4.16.30-vxCUSTOM"
    )
    
    await client.start()
    return client

async def main():
    try:
        # Используем упрощенную авторизацию
        client = await simple_auth()
        
        print("✅ Client started successfully")
        
        # Пример: получаем подарки конкретного пользователя
        target_user_id = 7969246251  # Замените на нужный ID
        
        # Получаем детальную информацию о подарках
        gift_count = await get_user_gifts_detailed(client, target_user_id, "target_user")
        
        print(f"\n📊 Итого: {gift_count} подарков")
        
    except Exception as e:
        print(f"❌ Error in main: {e}")
    
    finally:
        if 'client' in locals():
            await client.stop()
            print("📴 Client stopped")

if __name__ == '__main__':
    # Устанавливаем корректную кодировку для Windows
    import sys
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    asyncio.run(main())