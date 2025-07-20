async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel operation with drama"""
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    await asyncio.sleep(2)
    
    await update.message.reply_text(
        "🚫 OPERATION CANCELLED 🚫\n\n"
        "⚡ Your verification process has been interrupted\n"
        "💔 No access granted\n"
        "🔄 Send /start to begin again",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def main() -> None:
    """Start the bot with style"""
    print("""
██████╗  ██████╗ ████████╗    ██████╗  ██████╗ ████████╗
██╔══██╗██╔═══██╗╚══██╔══╝    ██╔══██╗██╔═══██╗╚══██╔══╝
██████╔╝██║   ██║   ██║       ██████╔╝██║   ██║   ██║   
██╔══██╗██║   ██║   ██║       ██╔══██╗██║   ██║   ██║   
██████╔╝╚██████╔╝   ██║       ██████╔╝╚██████╔╝   ██║   
╚═════╝  ╚═════╝    ╚═╝       ╚═════╝  ╚═════╝    ╚═╝   
""")
    
    # 🏗️ BUILD APPLICATION �
    application = Application.builder().token(BOT_TOKEN).build()

    # 🎭 CONVERSATION HANDLER 🎭
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^🔓 UNLØCK NØW 🔓$'), unlock_content)],
        states={
            REQUEST_CONTACT: [MessageHandler(filters.CONTACT, handle_contact)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)

    # 🚀 LAUNCH BOT 🚀
    print("\n🔥 BOT ACTIVATED 🔥".center(50))
    print("💎 Premium Content Delivery System".center(50))
    print("⚠️  WARNING: 18+ CONTENT ENABLED".center(50))
    print("="*50)
    application.run_polling()

if name == 'main':
    main()
