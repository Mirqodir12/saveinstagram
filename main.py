import instaloader
import os
import shutil
from uuid import uuid4
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import InputFile, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor
from pytube import YouTube
import youtube_dl

L = instaloader.Instaloader()

bot = Bot(token="6971921827:AAHL1W72f9vGB3JxmeTAbusFu_WdcwSSIdI ")

dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

MAX_FILE_SIZE_MB = 10
MAX_VIDEO_DURATION = 60 

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Instagram yoki YouTube video URL manzilini yuboring:")

@dp.message_handler(lambda message: 'instagram.com' in message.text)
async def handle_instagram_url(message: types.Message):
    chat_id = message.chat.id
    url = message.text
    shortcode = url.split("/")[-2]
    try:
        target_directory = str(uuid4())
        L.context.username = "YOUR_INSTAGRAM_USERNAME"
        L.context.password = "YOUR_INSTAGRAM_PASSWORD"
        loading_message = await message.answer('🔎 Video Yuklanmoqda...')
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        L.download_post(post, target=target_directory)
        video_file = next(os.path.join(target_directory, f) for f in os.listdir(target_directory) if f.endswith('.mp4'))
        
        with open(video_file, 'rb') as video:
            keyboard = [
                [InlineKeyboardButton("📤 Do'stlarga ulashish", switch_inline_query=video_file)],
                [InlineKeyboardButton("📥 Qo'shiqni yuklab olish", callback_data=f"download_audio:{video_file}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await bot.send_video(chat_id, video, caption='😀 Ushbu video juda ajoyib uni do\'stlaringiz bilan ulashing!\n\n🤖 @Mix_Save_robot orqali yuklab olindi.', reply_markup=reply_markup)

        await bot.delete_message(chat_id, loading_message.message_id)
        
        shutil.rmtree(target_directory)
    except Exception as e:
        await message.answer(f'Xatolik yuz berdi: {e}')

@dp.message_handler(lambda message: 'youtube.com' in message.text or 'youtu.be' in message.text)
async def handle_youtube_url(message: types.Message):
    chat_id = message.chat.id
    url = message.text
    try:
        yt = YouTube(url)
        video_stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()

        if not video_stream:
            await message.answer('Xatolik yuz berdi: 720p formatida video topilmadi.')
            return

        if yt.length > MAX_VIDEO_DURATION:
            await message.answer(f'Xatolik yuz berdi: Faqat shorts videolar (60 sekunddan kam) qabul qilinadi.')
            return

        target_directory = str(uuid4())
        video_file = video_stream.download(output_path=target_directory)

        if os.path.getsize(video_file) > MAX_FILE_SIZE_MB * 1024 * 1024:
            await message.answer('Xatolik yuz berdi: Video hajmi 10 MB dan oshmasligi kerak.')
            shutil.rmtree(target_directory)
            return
        
        loading_message = await message.answer('🔎 Video Yuklanmoqda...')
        
        with open(video_file, 'rb') as video:
            keyboard = [
                [InlineKeyboardButton("📤 Do'stlarga ulashish", switch_inline_query=video_file)],
                [InlineKeyboardButton("📥 Qo'shiqni yuklab olish", callback_data=f"download_audio:{video_file}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await bot.send_video(chat_id, video, caption='😀 Ushbu video juda ajoyib uni do\'stlaringiz bilan ulashing!\n\n🤖 @Mix_Save_robot orqali yuklab olindi.', reply_markup=reply_markup)

        await bot.delete_message(chat_id, loading_message.message_id)
        
        shutil.rmtree(target_directory)
    except Exception as e:
        await message.answer(f'Xatolik yuz berdi: {e}')

@dp.callback_query_handler(lambda query: query.data.startswith('download_audio'))
async def handle_inline_query(query: types.CallbackQuery):
    callback_data = query.data
    video_file = callback_data.split(":", 1)[1]
    target_directory = os.path.dirname(video_file)
    
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(target_directory, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_file, download=False)
            audio_file = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')

            if os.path.exists(audio_file):
                await bot.send_audio(query.message.chat.id, InputFile(audio_file), title='Extracted Music')
            else:
                await query.message.reply_text("Xatolik yuz berdi: Audio fayl topilmadi.")

    except Exception as e:
        await query.message.reply_text(f'Xatolik yuz berdi: {e}')
    finally:
        shutil.rmtree(target_directory)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
