import re
import yt_dlp
from telebot import TeleBot, types

BOT_TOKEN = "8967970011:AAFX20D_rquBTn-XAuDoJ67I9DQmWwUTKHM" # توکن خودت رو اینجا بذار

bot = TeleBot(BOT_TOKEN)

# تابع استخراج لینک مستقیم مدیا
def get_direct_link(url):
    ydl_opts = {
        'format': 'best',
        'noplaylist': True,
        'quiet': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info.get('url'), info.get('title', 'Media')
    except Exception as e:
        print(f"Error: {e}")
        return None, None

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    text = message.text.strip()
    url_pattern = re.compile(r'https?://(?:www\.)?(?:instagram\.com|tiktok\.com|youtube\.com|youtu\.be|fxinstagram\.com|vt\.tiktok\.com)\S+')
    
    # اگر کاربر لینک فرستاد
    if url_pattern.match(text):
        sent_msg = bot.reply_to(message, "🔍 در حال استخراج لینک دانلود...")
        direct_url, title = get_direct_link(text)
        
        if direct_url:
            markup = types.InlineKeyboardMarkup()
            btn = types.InlineKeyboardButton("📥 دانلود مستقیم فایل", url=direct_url)
            markup.add(btn)
            
            bot.edit_message_text(
                f"✨ **{title}**\n\nبرای دانلود فایل با سرعت بالا روی دکمه زیر بزنید:",
                message.chat.id,
                sent_msg.message_id,
                reply_markup=markup,
                parse_mode="Markdown"
            )
        else:
            bot.edit_message_text("❌ متأسفانه نتوانستم لینک این مدیا را استخراج کنم.", message.chat.id, sent_msg.message_id)
            
    else:
        # جستجوی ساده آهنگ به صورت متنی
        sent_msg = bot.reply_to(message, "🔍 در حال جستجوی آهنگ...")
        ydl_opts = {
            'format': 'bestaudio/best',
            'default_search': 'ytsearch1',
            'noplaylist': True,
            'quiet': True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(text, download=False)
                # برداشتن اولین نتیجه
                if 'entries' in info:
                    info = info['entries'][0]
                audio_url = info.get('url')
                title = info.get('title', 'Audio')
                uploader = info.get('uploader', 'Unknown')
                
                if audio_url:
                    markup = types.InlineKeyboardMarkup()
                    btn = types.InlineKeyboardButton("🎵 دانلود مستقیم آهنگ", url=audio_url)
                    markup.add(btn)
                    
                    bot.edit_message_text(
                        f"🎵 **{title}**\n👤 خواننده/کانال: {uploader}\n\nبرای دانلود موزیک روی دکمه زیر بزنید:",
                        message.chat.id,
                        sent_msg.message_id,
                        reply_markup=markup,
                        parse_mode="Markdown"
                    )
                else:
                    bot.edit_message_text("❌ آهنگی پیدا نشد.", message.chat.id, sent_msg.message_id)
        except Exception as e:
            print(f"Search Error: {e}")
            bot.edit_message_text("❌ خطا در جستجوی آهنگ.", message.chat.id, sent_msg.message_id)

if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()
