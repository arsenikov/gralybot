import logging
from uuid import uuid4
from telegram import Update, InlineQueryResultArticle, ParseMode, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup, ChatAction 
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, CallbackContext, Filters, MessageHandler
from telegram.utils.helpers import escape_markdown
from gingerit.gingerit import GingerIt
from functools import wraps
from config import BOT_TOKEN
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

token = BOT_TOKEN
#  Decorator for chat actions
def send_action(action):
    def decorator(func):
        @wraps(func)
        def command_func(update, context, *args, **kwargs):
            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return func(update, context,  *args, **kwargs)
        return command_func
    return decorator

@send_action(ChatAction.TYPING)
def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [   InlineKeyboardButton("Source code", url= "https://github.com/pascalmaximus/gralybot"),
            InlineKeyboardButton("My Channel", url= "https://telegram.dog/botivity")],   
        [   InlineKeyboardButton("Use Inline", switch_inline_query_current_chat ="")]
    ]
        
        
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text("Hi i can check your English text for all types of mistakes: grammar, spelling, punctuation, and more", reply_markup = reply_markup)

@send_action(ChatAction.TYPING)
def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Just send me any text to check your English text for all types of mistakes: grammar, spelling, punctuation, and more,\nor use me inline in any chat.")

@send_action(ChatAction.TYPING)
def grammar(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    parser = GingerIt()
    json = parser.parse(user_message)
    correct = json["result"]
    update.message.reply_text(correct)

def inlinequery(update: Update, context: CallbackContext) -> None:
    query = update.inline_query.query
    parser = GingerIt()
    json = parser.parse(query)
    correct = json["result"]
    if query == "":
        return
    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title=correct,
            input_message_content=InputTextMessageContent(
                correct
            ),
        ),
    ]

    update.inline_query.answer(results, switch_pm_text="Type something !.",switch_pm_parameter= "start")

def main() -> None:
    updater = Updater(token)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, grammar))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(InlineQueryHandler(inlinequery))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()