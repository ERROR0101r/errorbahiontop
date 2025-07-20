import os
import zipfile
import asyncio
import time
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Developer credit
DEVELOPER_CREDIT = "@ERROR0101r"

# Your Telegram Bot Token
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

user_sessions = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"👋 Welcome to ZIP Password Cracker Bot!\n\n"
        f"📦 Send me a ZIP file to begin cracking.\n\n"
        f"🤖 Developed by {DEVELOPER_CREDIT}"
    )
    user_sessions[update.message.chat_id] = {"state": "awaiting_zip"}

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    session = user_sessions.get(chat_id, {"state": None})

    if session["state"] == "awaiting_zip":
        zip_file = await update.message.document.get_file()
        zip_path = f"zip_{chat_id}.zip"
        await zip_file.download_to_drive(zip_path)
        session["zip_path"] = zip_path
        session["state"] = "awaiting_passwords"
        user_sessions[chat_id] = session

        await update.message.reply_text("📂 ZIP file received!\n\n📄 Now, send me a PASSWORD file (.txt) with passwords (one per line).")

    elif session["state"] == "awaiting_passwords":
        pass_file = await update.message.document.get_file()
        pass_path = f"pass_{chat_id}.txt"
        await pass_file.download_to_drive(pass_path)
        session["pass_path"] = pass_path
        session["state"] = "cracking"
        user_sessions[chat_id] = session

        await update.message.reply_text("🚀 Cracking started... 🔐 Please wait.")

        asyncio.create_task(crack_password(update, context, chat_id))

    else:
        await update.message.reply_text("❌ Use /start first to begin.")

async def crack_password(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id):
    session = user_sessions.get(chat_id)
    zip_path = session["zip_path"]
    pass_path = session["pass_path"]

    extract_folder = f"extracted_{chat_id}"
    os.makedirs(extract_folder, exist_ok=True)

    message = await context.bot.send_message(chat_id=chat_id, text="⏳ Tried 0 passwords... 🔄")
    tried_count = 0
    last_update_time = time.time()

    with open(pass_path, 'r', errors='ignore') as pf:
        passwords = pf.readlines()

    with zipfile.ZipFile(zip_path) as zf:
        for password in passwords:
            password = password.strip()
            tried_count += 1

            try:
                zf.extractall(path=extract_folder, pwd=password.encode('utf-8'))
                await message.edit_text(
                    f"✅ Password FOUND: `{password}` 🎉\n\n"
                    f"🔓 ZIP file cracked successfully!\n\n"
                    f"📤 Sending extracted files...\n\n"
                    f"🤖 Developed by {DEVELOPER_CREDIT}"
                )

                for root, _, files in os.walk(extract_folder):
                    for filename in files:
                        file_path = os.path.join(root, filename)
                        try:
                            await context.bot.send_document(chat_id=chat_id, document=InputFile(file_path))
                        except:
                            await context.bot.send_message(chat_id=chat_id, text=f"⚠️ Failed to send {filename}.")

                cleanup_files(zip_path, pass_path, extract_folder)
                session["state"] = "done"
                return

            except RuntimeError:
                pass

            except Exception:
                pass

            if time.time() - last_update_time > 10:
                try:
                    await message.edit_text(f"⏳ Tried {tried_count} passwords... 🔄")
                except:
                    pass
                last_update_time = time.time()

    await message.edit_text(
        f"❌ Failed to crack ZIP after {tried_count} passwords. 😞\n\n"
        f"🤖 Developed by {DEVELOPER_CREDIT}"
    )

    cleanup_files(zip_path, pass_path, extract_folder)
    session["state"] = "done"

def cleanup_files(zip_path, pass_path, extract_folder):
    try:
        if os.path.exists(zip_path):
            os.remove(zip_path)
        if os.path.exists(pass_path):
            os.remove(pass_path)
        if os.path.exists(extract_folder):
            for root, dirs, files in os.walk(extract_folder, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(extract_folder)
    except:
        pass

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    app.run_polling()

if __name__ == "__main__":
    main()
