from pprint import pprint
import datetime
import asyncio
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, Application, CallbackContext
from services.DatabaseRequests import DatabaseRequests


class TelegramBot:
    
    def __init__(self):
        self.__database = DatabaseRequests()
        # self.__bot = Bot("5957878793:AAH391KCu0twpoXkbc7kfTzbsXNnN_Qc-5A")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.__database.connect())


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
    
        await self.__database.insert(query=query, values=values)


    async def help_command(self, update: Update,
                           context: ContextTypes.DEFAULT_TYPE) -> None:
        
        await update.message.reply_text("Основні команди: \nДодати витрати: /add_expense \nСтатистика за сьогоднішній день: /daily_expenses \nСтатистика за місяць: /view_monthly_statistics \nОстанні витрати: /view_last_expenses")
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
        await self.__database.insert(query, values)

        message = f"Додано витрату {amount} грн. в категорії {category}!"
        await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')



    async def daily_expenses(self, update: Update, context: CallbackContext) -> None:
        
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        today = datetime.date.today()

        query = "SELECT SUM(amount) FROM expenses WHERE user_id = %s AND DATE(created_at) = %s"
        values = (user_id, today)
        result = await self.__database.select_one(query, values)

        if result and result[0]:
            message = f"Витрати за сьогодні: {result[0]} грн."
        else:
            message = "За сьогодні витрат не було."

        await context.bot.send_message(chat_id=chat_id, text=message)


    async def view_last_expenses(self, update: Update, context: CallbackContext):

        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        limit = 10 
        query = f"SELECT amount, category, created_at FROM expenses WHERE user_id={user_id} ORDER BY created_at DESC LIMIT {limit}"
        rows = await self.__database.select(query)
        if not rows:
            await context.bot.send_message(chat_id=chat_id, text="У вас поки що немає витрат")
            return
        message = "Останні витрати:\n"
        for row in rows:
            amount, category = row[:2]
            created_at = row[2]
            if created_at is not None:
                created_at_str = created_at.strftime('%d.%m.%Y %H:%M:%S')
            else:
                created_at_str = 'N/A'
            message += f"- {amount:.2f} грн. ({category}) - {created_at_str}\n"

        await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')


    async def view_monthly_statistics(self, update: Update, context: CallbackContext):
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        today = datetime.date.today()
        first_day_of_month = today.replace(day=1)
        last_day_of_month = today.replace(day=28) + datetime.timedelta(days=4)
        last_day_of_month = last_day_of_month.replace(day=1) - datetime.timedelta(days=1)
        query = f"SELECT category, SUM(amount) FROM expenses WHERE user_id={user_id} AND created_at BETWEEN '{first_day_of_month}' AND '{last_day_of_month}' GROUP BY category"
        rows = await self.__database.select(query)
        if not rows:
            await context.bot.send_message(chat_id=chat_id, text="За поточний місяць у вас поки що немає витрат")
            return
        total_amount = sum(row[1] for row in rows)
        message = f"Статистика витрат за {today.strftime('%B %Y')}:\n"
        for row in rows:
            category, amount = row
            message += f"- {amount:.2f} грн. ({category})\n"
        message += f"\nУсього витрачено: {total_amount:.2f} грн."
        await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')


    def main(self) -> None:

        application = Application.builder().token(
            "5957878793:AAH391KCu0twpoXkbc7kfTzbsXNnN_Qc-5A").build()
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("add_expense", self.add_expense))
        application.add_handler(CommandHandler("daily_expenses", self.daily_expenses))
        application.add_handler(CommandHandler("view_last_expenses", self.view_last_expenses))
        application.add_handler(CommandHandler("view_monthly_statistics", self.view_monthly_statistics))

        application.run_polling()


telebot = TelegramBot()
telebot.main()