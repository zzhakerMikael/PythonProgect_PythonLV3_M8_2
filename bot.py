# Импортируем необходимые библиотеки
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging
import os
from config import *

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Константы
ADMIN_CHAT_ID = tg_id  # Ваш ID Telegram
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')  # Токен бота

# Глобальный словарь для хранения информации о тикетах
tickets = {}

# Функция запуска бота
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    await update.message.reply_text(
        f"Здравствуйте, {user.first_name}!\n"
        "Я бот технической поддержки. Чтобы создать заявку, напишите /new_ticket"
    )

# Функция создания новой заявки
async def new_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    tickets[user_id] = {
        'description': '',
        'details': '',
        'status': 'new'
    }
    
    await update.message.reply_text(
        "Создайте описание вашей проблемы. Отправьте /done, когда закончите."
    )

# Функция обработки сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    if user_id in tickets:
        if update.message.text.lower() == '/done':
            ticket_info = tickets[user_id]
            
            # Отправляем заявку администратору
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=f"Новая заявка от {update.message.from_user.first_name}:\n"
                     f"Описание: {ticket_info['description']}\n"
                     f"Детали: {ticket_info['details']}"
            )
            
            await update.message.reply_text("Ваша заявка отправлена. Ожидайте ответа.")
            del tickets[user_id]
        else:
            if not tickets[user_id]['description']:
                tickets[user_id]['description'] = update.message.text
            else:
                tickets[user_id]['details'] += f"\n{update.message.text}"

# Функция для получения помощи
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Как пользоваться ботом:\n"
        "/start - начать работу с ботом\n"
        "/new_ticket - создать новую заявку\n"
        "/help - получить помощь"
    )

# Основная функция
def main():
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('new_ticket', new_ticket))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()
