import asyncio
import aiohttp
import aiogram
import instaloader
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from pytube import YouTube

# Telegram bot uchun API tokeni
bot_token = '6327620999:AAEnLQkULdcoW4_CZRjlSFeThn42ZBLCpw8'

# AIogram kutubxonasini ishlatish
bot = Bot(token=bot_token)
dp = Dispatcher(bot)

# Async HTTP klienti yaratish
async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

# TikTok uchun video yuklash funktsiyasi
async def download_media_from_tiktok(url):
    if "tiktok" in url and url.startswith("https://"):
        try:
            # Initialize TikTokScraper with the video URL
           
            # Get video metadata
            tiktok_metadata
            if tiktok_metadata:
                video_url = tiktok_metadata['video_url']
                async with aiohttp.ClientSession() as session:
                    async with session.get(video_url) as resp:
                        if resp.status == 200:
                            filename = f'downloads/{tiktok_metadata["author"]}_{tiktok_metadata["title"]}.mp4'
                            with open(filename, 'wb') as f:
                                f.write(await resp.read())
                            return {
                                'type': 'tiktok',
                                'title': tiktok_metadata['author'],
                                'file': filename,
                                'audio_file': None  # TikTok dan musiqa topolmaydi
                            }
                        else:
                            print(f"TikTok video yuklab olishda xatolik: Status code {resp.status}")
        except Exception as e:
            print(f"TikTok video yuklab olishda xatolik: {e}")
    
    return None

# /start buyrug'i uchun javob berish
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Assalomu alaykum! Men botman, TikTok URL yuboring va video yuklab olishni kuting.\n\n"
                        "Misol:\n"
                        "TikTok: https://www.tiktok.com/@therock/video/6980571946972903173")

# Video yuklab olish va yuborish
@dp.message_handler()
async def send_media(message: types.Message):
    url = message.text
    try:
        # Async tezroq yuklash uchun asyncio.gather() ishlatamiz
        media_data = await download_media_from_tiktok(url)
        
        if media_data:
            if media_data['file'].endswith('.mp4'):
                caption = f"<b>{media_data['title']}</b>\nTikTok video"
                caption += "\nMusiqa topilmadi: ❌"
                
                # Inline keyboard yaratish
                keyboard = types.InlineKeyboardMarkup()
                keyboard.add(
                    types.InlineKeyboardButton("📤 Do'stlarga ulashish", switch_inline_query=media_data['file']),
                )
                
                # Video faylini yuborish
                with open(media_data['file'], 'rb') as video:
                    await bot.send_video(message.chat.id, video, caption=caption, parse_mode='HTML', reply_markup=keyboard)
            else:
                await message.reply("Video yuklab olishda xatolik yuzaga keldi.")
        else:
            await message.reply("URL noto'g'ri formatda yuborilgan yoki videoni yuklab olish imkoniyati yo'q.")
    except Exception as e:
        print(f"Xatolik: {e}")
        await message.reply("Video yuklab olishda xatolik yuzaga keldi.")

# Botni ishga tushirish
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
