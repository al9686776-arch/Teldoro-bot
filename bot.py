import os
import re
import yt_dlp
from telebot import TeleBot, types

# فقط توکن ربات رو اینجا بین دبل‌کوتیشن بذار
BOT_TOKEN = "8967970011:AAFX20D_rquBTn-XAuDoJ67I9DQmWwUTKHM"

bot = TeleBot(BOT_TOKEN)

# تابع دانلود ویدیو (اینستاگرام، تیک‌تاک، یوتیوب)
def download_media(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
    }
    os.makedirs('downloads', exist_ok=True)
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return filename, info.get('title', 'Media')
    except Exception as e:
        print(f"Error: {e}")
        return None, None

# تابع دانلود صوت آهنگ (جستجو در گوگل/یوتیوب و تبدیل به MP3)
def download_audio(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'default_search': 'ytsearch1',
        'noplaylist': True,
        'quiet': True,
    }
    os.makedirs('downloads', exist_ok=True)
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)
            filename = ydl.prepare_filename(info)
            base, _ = os.path.splitext(filename)
            mp3_file = base + ".mp3"
            title = info.get('title', 'Audio')
            uploader = info.get('uploader', 'Unknown')
            return mp3_file, title, uploader
    except Exception as e:
        print(f"Audio Error: {e}")
        return None, None, None

# مدیریت پیام‌های متنی و لینک‌ها
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    text = message.text.strip()
    url_pattern = re.compile(r'https?://(?:www\.)?(?:instagram\.com|tiktok\.com|youtube\.com|youtu\.be|fxinstagram\.com|vt\.tiktok\.com)\S+')
    
    # اگر کاربر لینک فرستاد
    if url_pattern.match(text):
        sent_msg = bot.reply_to(message, "📥 در حال دانلود مدیا...")
        file_path, title = download_media(text)
        
        if file_path and os.path.exists(file_path):
            markup = types.InlineKeyboardMarkup()
            btn = types.InlineKeyboardButton("🎵 دریافت موزیک این ویدیو", callback_data=f"get_audio|{text}")
            markup.add(btn)
            
            with open(file_path, 'rb') as vid:
                bot.send_video(message.chat.id, vid, caption=f"✨ {title}\n🤖 @TelDorobot", reply_markup=markup)
            
            bot.delete_message(message.chat.id, sent_msg.message_id)
            try: os.remove(file_path)
            except: pass
        else:
            bot.edit_message_text("❌ دانلود مدیا نامعتبر بود.", message.chat.id, sent_msg.message_id)
            
    else:
        # اگر کاربر اسم آهنگ فرستاد (جستجو از گوگل/یوتیوب)
        sent_msg = bot.reply_to(message, "🔍 در حال جستجو و آماده‌سازی آهنگ...")
        mp3_path, title, uploader = download_audio(text)
        
        if mp3_path and os.path.exists(mp3_path):
            with open(mp3_path, 'rb') as audio:
                bot.send_audio(
                    message.chat.id, 
                    audio, 
                    title=title, 
                    performer=uploader,
                    caption=f"🎵 {title}\n👤 {uploader}\n🤖 @TelDorobot"
                )
            bot.delete_message(message.chat.id, sent_msg.message_id)
            try: os.remove(mp3_path)
            except: pass
        else:
            bot.edit_message_text("❌ آهنگی با این مشخصات پیدا نشد.", message.chat.id, sent_msg.message_id)

# مدیریت کلیک روی دکمه «دریافت موزیک این ویدیو»
@bot.callback_query_handler(func=lambda call: call.data.startswith("get_audio"))
def callback_get_audio(call):
    url = call.data.split("|")[1]
    bot.answer_callback_query(call.id, "در حال استخراج موزیک ویدیو...")
    
    sent_msg = bot.send_message(call.message.chat.id, "🎧 در حال تبدیل و ارسال فایل صوتی...")
    mp3_path, title, uploader = download_audio(url)
    
    if mp3_path and os.path.exists(mp3_path):
        with open(mp3_path, 'rb') as audio:
            bot.send_audio(
                call.message.chat.id, 
                audio, 
                title=title, 
                performer=uploader,
                caption=f"🎵 موزیک ویدیو: {title}\n🤖 @TelDorobot"
            )
        bot.delete_message(call.message.chat.id, sent_msg.message_id)
        try: os.remove(mp3_path)
        except: pass
    else:
        bot.edit_message_text("❌ استخراج موزیک از این لینک امکان‌پذیر نبود.", call.message.chat.id, sent_msg.message_id)

if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()
