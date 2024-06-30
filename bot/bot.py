import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import ollama
import nest_asyncio

nest_asyncio.apply()

# Включаем ведение журнала
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Токен, который вы получили от @BotFather
TOKEN = '1959421074:AAE0Wj4uMSxw_d3b2_DkOl_3Ur5o1GPRcc8'  # Replace with your actual token

# Словарь для хранения данных пользователей
user_ids = {}
context_memory = {}

# Функция для обработки команды /start
async def start(update: Update, context) -> None:
    await update.message.reply_text('Привет! Я чат-бот. Чем могу помочь?')

# Функция для обработки обычных сообщений
async def handle_message(update: Update, context):
    user_id = update.effective_user.id
    if user_id not in user_ids:
        user_ids[user_id] = {'last_message': None, 'preferences': {}}
        context_memory[user_id] = []

    message_text = update.message.text
    context_messages = context_memory[user_id]

    context_messages.append({'role': 'system', 'content': 'please provide only codeblocks, and filepaths. do not explain code, unless asked explicitly otherwise.'})
    # Добавляем новое сообщение в контекст
    context_messages.append({'role': 'user', 'content': message_text})

    # Ограничиваем историю контекста последними 8 сообщениями
    context_memory[user_id] = context_messages[-8:]

    try:
        # Call the ollama.chat function with the context messages
        response = ollama.chat(model='deepseek-coder-v2:16b-lite-instruct-fp16', messages=context_memory[user_id])

        from ollama import Client
        client = Client(host='10.12.1.31:8086')

        prompt=input('your prompt:')
        stream = client.chat(model='deepseek-coder-v2:16b-lite-instruct-fp16', messages=[
            {
                'role': 'user',
                'content': prompt
            },
            ],
            stream=True
        )

        for chunk in stream:
            # print(chunk['message']['content'], end='', flush=True)
            await update.message.reply_text(chunk['message']['content'], parse_mode='MarkdownV2')

        # Отправляем ответ пользователю
        # await update.message.reply_text(response['message']['content'], parse_mode='MarkdownV2')
    except Exception as e:
        logging.error(f"Error while getting response from ollama: {e}")
        await update.message.reply_text('Произошла ошибка, попробуйте позже.')

# Основная функция
async def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
