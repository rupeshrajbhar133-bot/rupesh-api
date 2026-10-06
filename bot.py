import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Aapka Bot Token
TOKEN = "8633668362:AAFXRkYYL2By6cntmWX1vTI9Eu_WLp_uvd4"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hello! Mujhe koi bhi:\n"
        "• **10-digit Mobile Number**\n"
        "• **12-digit Aadhaar Number**\n"
        "bhejiye, main database mein search karke details nikal dunga.\n\n"
        "👨‍💻 **Developer:** @RD3B4T",
        parse_mode="Markdown"
    )

async def search_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    
    # Check karein ki sirf numbers hain ya nahi
    if not query.isdigit():
        await update.message.reply_text("❌ Kripya sirf numbers (digits) bhejiye.")
        return
        
    # Length check for 10-digit (Mobile) or 12-digit (Aadhaar)
    if len(query) == 10:
        search_type = "Mobile Number"
    elif len(query) == 12:
        search_type = "Aadhaar Number"
    else:
        await update.message.reply_text(
            "❌ Galat length! Kripya ya toh valid **10-digit Mobile Number** ya **12-digit Aadhaar Number** bhejiye.",
            parse_mode="Markdown"
        )
        return

    await update.message.reply_text(f"🔍 Searching {search_type} `{query}`...", parse_mode="Markdown")
    
    api_url = f"https://kzropx-icmr-data.hf.space/search?q={query}"
    
    try:
        response = requests.get(api_url, timeout=15)
        if response.status_code == 200:
            res_json = response.json()
            
            # API response data structure handle karna
            data = res_json.get('data', res_json) if isinstance(res_json, dict) else res_json
            
            if data:
                item = data[0] if isinstance(data, list) else data
                
                mobile = item.get('mobile', 'N/A')
                name = item.get('name', 'N/A')
                fname = item.get('fname', 'N/A')
                address = item.get('address', 'N/A')
                alt = item.get('alt', 'N/A')
                circle = item.get('circle', 'N/A')
                user_id = item.get('id', 'N/A')
                email = item.get('email')
                email_str = email if email else 'N/A'
                
                # Formatted output with Developer credit
                result_text = (
                    f"📋 **Record Found ({search_type}):**\n\n"
                    f"📱 **Mobile:** {mobile}\n"
                    f"👤 **Name:** {name}\n"
                    f"👨 **Father's Name:** {fname}\n"
                    f"📞 **Alt Number:** {alt}\n"
                    f"🌐 **Circle:** {circle}\n"
                    f"🏠 **Address:** {address}\n"
                    f"🆔 **ID:** {user_id}\n"
                    f"📧 **Email:** {email_str}\n\n"
                    f"👨‍💻 **Developer:** @RD3B4T"
                )
                
                await update.message.reply_text(result_text, parse_mode="Markdown")
            else:
                await update.message.reply_text("❌ Koi record nahi mila.")
        else:
            await update.message.reply_text(f"⚠️ API Error: {response.status_code}")
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("⚠️ Server se data fetch karne mein error aayi.")

def main():
    if not TOKEN:
        logger.error("BOT_TOKEN set nahi hai!")
        return

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_data))

    logger.info("Bot polling start ho gayi hai...")
    application.run_polling()

if __name__ == '__main__':
    main()
