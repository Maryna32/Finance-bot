from pprint import pprint
from telegram import Update, Bot, ForceReply
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, Application

from services.DatabaseRequests import DatabaseRequests


class TelegramBot:
    
    def __init__(self):
        self.__database = DatabaseRequests()
        self.__bot = Bot("5957878793:AAH391KCu0twpoXkbc7kfTzbsXNnN_Qc-5A")


    async def start(self, update: Update,
                    context: ContextTypes.DEFAULT_TYPE) -> None:
  
        user = update.effective_user
        await update.message.reply_html(
            rf"Hi, {user.mention_html()}!",
            reply_markup=ForceReply(selective=True),
        )

        if context.bot_data.get("chats_id") == None:
            context.bot_data.update({"chats_id": list()})

        chats_id = context.bot_data.get("chats_id")

        if update.message.chat.id not in chats_id:
            chats_id.append(update.message.chat_id)
            context.bot_data.update({"chats_id": chats_id})
        pprint(context.bot_data.get("chats_id"))


    async def echo(self, update: Update,
                   context: ContextTypes.DEFAULT_TYPE) -> None:
        
        await update.message.reply_text(update.message.text)


    async def help_command(self, update: Update,
                           context: ContextTypes.DEFAULT_TYPE) -> None:
        
        await update.message.reply_text("Help!")


    def main(self) -> None:

        application = Application.builder().token(
            "5957878793:AAH391KCu0twpoXkbc7kfTzbsXNnN_Qc-5A").build()
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_command))
        application.run_polling()


telebot = TelegramBot()
telebot.main()