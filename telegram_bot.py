import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from wakeonlan import send_magic_packet
from secrets import SECRETS
from Bouwtje_Vast_Controller import PcController
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackContext,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Your bot token obtained from BotFather
TOKEN = SECRETS['TELEGRAM_TOKEN']

# Define states for conversation
MENU, WOL, CHECK, RESTART, FORTNITE, SLEEP = range(6)

# Set up logging for the bot
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

allowed_ids = SECRETS['ALLOWED_USER_IDS']

pc_controller = PcController()

# Start command handler
async def start(update: Update, context: CallbackContext) -> int:
    
    keyboard = [
        [InlineKeyboardButton("Wake PC and Start Plex", callback_data="wakepc")],
        [InlineKeyboardButton("Check Plex", callback_data="checkplex")],
        [InlineKeyboardButton("Restart Plex", callback_data="restartplex")],
        # [InlineKeyboardButton("Check Fortnite Update", callback_data="epicgames")],  ## TODO: bedenken hoe dit te doen, fortnite starten -> check of hij gaat updaten / klaar is met updaten (HOE?) -> sluit fortnite
        [InlineKeyboardButton("Put PC to Sleep", callback_data="sleeppc")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Welcome! Please choose an option:", reply_markup=reply_markup
    )
    return MENU

# Button click handler
async def button(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == "wakepc":
        
        user_id = query.from_user.id
        
        if (user_id in allowed_ids):
            await query.edit_message_text(text="Sending Magic Packet...")
            send_magic_packet(SECRETS['MAC_ADDRESS'])
           
            await query.edit_message_text(text="Checking Plex Status...")
            result, error = pc_controller.start_plex()
            if (error == ""):
                await query.edit_message_text(text="Computer and Plex Started successfully")
            else:
                await query.edit_message_text(text=error)
            
        else:
            await query.edit_message_text(text="User is not allowed to start the computer. Fuck off")
        
        return WOL
    elif query.data == "checkplex":
        result = pc_controller.check_plex()
        await query.edit_message_text(text=result)
        
        return CHECK
    elif query.data == "restartplex":        
        result, error = pc_controller.restart_plex()
        if error == "":
            await query.edit_message_text(text="Plex Restarted")
        else:
            await query.edit_message_text(text=error)
        
        return RESTART
    #elif query.data == "epicgames":
    #    await query.edit_message_text(text="You selected Option 2.")
        
        
    #    return FORTNITE
    elif query.data == "sleeppc":        
        result, error = pc_controller.sleep_pc()
        if (error == ""):
            await query.edit_message_text(text="Computer put to bed")
        else:
            await query.edit_message_text(text=error)
        
        return SLEEP
    else:
        await query.edit_message_text(text="Unknown option selected.")
        return MENU

# Cancel handler
async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END

# Main function to start the bot
def main():
    application = (
        ApplicationBuilder()
        .token(TOKEN)
        .read_timeout(10)
        .write_timeout(10)
        .concurrent_updates(True)
        .build()
    )

    # ConversationHandler to handle the state machine
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MENU: [CallbackQueryHandler(button)],
            WOL: [MessageHandler(filters.TEXT & ~filters.COMMAND, cancel)],
            CHECK: [MessageHandler(filters.TEXT & ~filters.COMMAND, cancel)],
            RESTART: [MessageHandler(filters.TEXT & ~filters.COMMAND, cancel)],
            FORTNITE: [MessageHandler(filters.TEXT & ~filters.COMMAND, cancel)],
            SLEEP: [MessageHandler(filters.TEXT & ~filters.COMMAND, cancel)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    application.add_handler(conv_handler)
    application.run_polling()

    
if __name__ == "__main__":
    main()
    
