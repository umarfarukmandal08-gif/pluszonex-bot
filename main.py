from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import uuid
import asyncio

# ========= CONFIG =========
BOT_TOKEN = "8525233229:AAG8dgtgVgH_KqbHjnSb7unKmla-fotp0Tc"
ADMIN_ID = 1096992356
BOT_USERNAME = "PlusZoneX_bot"
STORAGE_CHANNEL_ID = -1003570732474  # Private Storage Channel
# ==========================

# Temporary in-memory video database
video_db = {}       # key -> file_id
user_sessions = {}  # chat_id -> key (active session)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    chat_id = update.effective_chat.id

    if args:
        key = args[0]
        if key in video_db:
            # Step 1: Send processing message
            processing_msg = await update.message.reply_text("⏳ Processing video…")

            # Step 2: Send video
            video_msg = await context.bot.send_video(
                chat_id=chat_id,
                video=video_db[key]
            )

            # Step 3: Delete processing message immediately after video sent
            await processing_msg.delete()

            # Step 4: Send info message
            info_msg = await update.message.reply_text(
                "💾 Save the videos if you want to watch them again — "
                "they will be deleted automatically after 2 minutes. ⏳"
            )

            # Step 5: Track session
            user_sessions[chat_id] = key

            # Step 6: Wait 2 minutes, then delete video + info message + session
            await asyncio.sleep(120)
            user_sessions.pop(chat_id, None)
            await video_msg.delete()
            await info_msg.delete()
            return

    # Welcome message if no args
    await update.message.reply_text(
        f"Hello welcome to our Bot ❤️\n@{BOT_USERNAME}"
    )

# Video upload handler (ADMIN only)
async def save_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user:
        return
    if update.effective_user.id != ADMIN_ID:
        return
    if not update.message.video:
        return

    # Upload to Private Storage Channel
    msg = await context.bot.send_video(
        chat_id=STORAGE_CHANNEL_ID,
        video=update.message.video.file_id
    )

    # Generate unique key
    key = uuid.uuid4().hex[:8]
    video_db[key] = msg.video.file_id

    # Generate Telegram link
    link = f"https://t.me/{BOT_USERNAME}?start={key}"

    # Reply to admin
    await update.message.reply_text(
        f"✅ Video Added Successfully\n🔗 {link}"
    )

# Main function
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO, save_video))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()