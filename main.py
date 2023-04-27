from pprint import pprint
from telegram import Update, Bot
from telegram.ext import CommandHandler, ContextTypes, Application, CallbackContext

from services.DatabaseRequests import DatabaseRequests


class TelegramBot:
    
    def __init__(self):
        self.__database = DatabaseRequests()
        self.__bot = Bot("5957878793:AAH391KCu0twpoXkbc7kfTzbsXNnN_Qc-5A")


    async def start(self, update: Update,
                    context: ContextTypes.DEFAULT_TYPE) -> None:

        user = update.effective_user
        await update.message.reply_text(f"Привіт, {user.full_name}! \nЦе бот для управління фінансами. \nДля детальнього опису функціонала бота використовуйте команду /help")

        if context.bot_data.get("chats_id") == None:
            context.bot_data.update({"chats_id": list()})

        chats_id = context.bot_data.get("chats_id")

        if update.message.chat.id not in chats_id:
            chats_id.append(update.message.chat_id)
            context.bot_data.update({"chats_id": chats_id})
        pprint(context.bot_data.get("chats_id"))

        query = "INSERT INTO users (username, chat_id) VALUES (%s, %s)"
        values = (user.username, update.message.chat.id)
        self.__database.insert(query=query, values=values)


    async def help_command(self, update: Update,
                           context: ContextTypes.DEFAULT_TYPE) -> None:
        
        await update.message.reply_text("Основні команди: \nДодати витрати: /add_expense")
        await update.message.reply_text("Приклад створення витрат: /add_expense 100 таксі")


    async def add_expense(self, update: Update, context: CallbackContext):
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        try:
            amount = float(context.args[0])
            category = context.args[1]
        except (IndexError, ValueError):
            await context.bot.send_message(chat_id=chat_id, text="Неправильний формат введення. Спробуйте ще раз.")
            return
        
        query = "INSERT INTO expenses (user_id, amount, category, created_at) VALUES (%s, %s, %s, NOW())"
        values = (user_id, amount, category)
        self.__database.insert(query, values)

        message = f"Додано витрату {amount} грн. в категорії {category}!"
        await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')


    def main(self) -> None:

        application = Application.builder().token(
            "5957878793:AAH391KCu0twpoXkbc7kfTzbsXNnN_Qc-5A").build()
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("add_expense", self.add_expense))
        application.run_polling()


telebot = TelegramBot()
telebot.main()