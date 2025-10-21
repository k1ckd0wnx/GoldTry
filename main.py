import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

# Вземаме токена и Channel ID от Environment Variables (Render)
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# Съхранява входните данни на потребителя по ID
user_data = {}

# --- Команда /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Здравей! Изпрати /signal за нов сигнал за злато (XAUUSD)."
    )

# --- Команда /signal ---
async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("📈 BUY", callback_data="BUY"),
            InlineKeyboardButton("📉 SELL", callback_data="SELL")
        ]
    ]
    await update.message.reply_text(
        "Избери посока:", 
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# --- Обработва избора на BUY/SELL ---
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_data[query.from_user.id] = {"type": query.data}
    await query.message.reply_text("Въведи Entry price:")

# --- Обработва текста (Entry, SL, TP, Confidence) ---
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    if uid not in user_data:
        return

    data = user_data[uid]

    if "entry" not in data:
        data["entry"] = update.message.text
        await update.message.reply_text("Въведи Stop Loss:")
    elif "sl" not in data:
        data["sl"] = update.message.text
        await update.message.reply_text("Въведи Take Profit:")
    elif "tp" not in data:
        data["tp"] = update.message.text
        await update.message.reply_text(
            "Въведи Confidence (по желание) или 'skip':"
        )
    elif "confidence" not in data:
        conf = update.message.text
        data["confidence"] = None if conf.lower() == "skip" else conf

        # Форматиране на съобщението за канала
        msg = (
            f"📊 *XAUUSD (Gold)*\n"
            f"Signal: *{data['type']}*\n"
            f"Entry: `{data['entry']}`\n"
            f"SL: `{data['sl']}`\n"
            f"TP: `{data['tp']}`\n"
        )
        if data["confidence"]:
            msg += f"Confidence: *{data['confidence']}%*"

        # Изпращане на сигнала в канала
        await context.bot.send_message(
            chat_id=CHANNEL_ID, text=msg, parse_mode="Markdown"
        )
        await update.message.reply_text("✅ Signal sent to channel.")
        del user_data[uid]

# --- Създаване на приложението ---
app = ApplicationBuilder().token(BOT_TOKEN).build()

# Добавяне на handler-и
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("signal", signal))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

# Стартиране на бота
if __name__ == "__main__":
    print("Bot started...")
    app.run_polling()
