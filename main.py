import telebot
import logging
from validator import is_gpt_token_limit, is_stt_block_limit, is_tts_symbol_limit, check_number_of_users
from config import COUNT_LAST_MSG, BOT_TOKEN, LOGS, errors_list
from database import create_db, create_table, \
    select_n_last_messages, add_message
from yandex_gpt import speech_to_text, ask_gpt, text_to_speech
from creds import get_bot_token  # модуль для получения bot_token

# bot = telebot.TeleBot(get_bot_token())  # создаём объект бота
bot = telebot.TeleBot(BOT_TOKEN)
logging.basicConfig(filename=LOGS, level=logging.ERROR,
                    format="%(asctime)s FILE: %(filename)s IN: "
                           "%(funcName)s MESSAGE: %(message)s", filemode="w")

# обрабатываем команду /start
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Привет! Отправь мне голосовое сообщение "
                              "или текст, и я тебе отвечу!")
    create_db()    # подготовка базы данных
    create_table()    # создание таблицы


# обрабатываем команду /help
@bot.message_handler(commands=['help'])
def help_func(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Чтобы приступить к общению, отправь мне "
                              "голосовое сообщение или текст")


# обрабатываем команду /debug - отправляем файл с логами
@bot.message_handler(commands=['debug'])
def debug(message):
    with open("logs.txt", "rb") as f:
        bot.send_document(message.chat.id, f)


@bot.message_handler(commands=['stt'])
def check_stt(message):
    user_id = message.from_user.id
    bot.send_message(user_id, 'для проверки режима распознавания речи, '
                              'пришлите голосовое сообщение')
    bot.register_next_step_handler(message, last_stt_step)

def last_stt_step(message):
    user_id = message.from_user.id
    if message.content_type == 'voice':
        transcribe_stt(message, move_on=False)
    else:
        bot.send_message(user_id, 'Пришли голосовое сообщение')
        bot.register_next_step_handler(message, check_stt)


@bot.message_handler(commands=['tts'])
def check_tts(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Пришли мне текст для проверки озвучки текста.")
    bot.register_next_step_handler(message, exam_tts)


def exam_tts(message):
    user_id = message.from_user.id
    try:
        transcribe_tts(message, message.text, 0)
    except Exception as e:
        print(e)
        bot.send_message(user_id, "Не получилось озвучить текст. Попробуйте ещё раз позже")


# вывод списка ошибок с их объяснением
@bot.message_handler(commands=['errors_list'])
def print_list(message):
    user_id = message.from_user.id
    bot.send_message(user_id, errors_list)


@bot.message_handler(content_types=['voice'])
# переводим речь в текст
def transcribe_stt(message: telebot.types.Message, move_on=True):
    user_id = message.chat.id
    try:
        # Проверка на максимальное количество пользователей
        status_check_users, error_message = check_number_of_users(user_id)
        if not status_check_users:
            bot.send_message(user_id, error_message)
            return

        # Проверка на доступность аудиоблоков
        good_status, stt_blocks = is_stt_block_limit(user_id, message.voice.duration)
        if not good_status:
            bot.send_message(user_id, stt_blocks)
            return

        # Обработка голосового сообщения
        file_id = message.voice.file_id
        file_info = bot.get_file(file_id)
        file = bot.download_file(file_info.file_path)
        status_stt, stt_text = speech_to_text(file)
        if not status_stt:
            bot.send_message(user_id, stt_text)
            return

        # Запись в БД
        add_message(user_id=user_id, full_message=[stt_text, 'user', 0, 0, stt_blocks])
        if move_on:
            access_to_gpt(message)
        else:
            bot.send_message(user_id, stt_text, reply_to_message_id=message.id)
    except Exception as e:
        print(e)
        logging.error(e)
        bot.send_message(message.chat.id, "Не получилось ответить. Попробуй записать другое сообщение")


# отправка запроса к gpt и получение ответа
def access_to_gpt(message, move_on=True):
    user_id = message.from_user.id
    try:
        # Проверка на доступность GPT-токенов
        last_messages, total_spent_tokens = select_n_last_messages(user_id, COUNT_LAST_MSG)
        total_gpt_tokens, error_message = is_gpt_token_limit(last_messages, total_spent_tokens)
        if error_message:
            bot.send_message(user_id, error_message)
            return

        # Запрос к GPT и обработка ответа
        status_gpt, answer_gpt, tokens_in_answer = ask_gpt(last_messages)
        if not status_gpt:
            bot.send_message(user_id, answer_gpt)
            return
        total_gpt_tokens += tokens_in_answer

        # Проверка на лимит символов для SpeechKit
        if move_on:
            transcribe_tts(message, answer_gpt, total_gpt_tokens)
        else:
            bot.send_message(user_id, answer_gpt, reply_to_message_id=message.id)

    except Exception as e:
        print(e)
        logging.error(e)
        bot.send_message(message.chat.id, "Не получилось ответить. Попробуй записать другое сообщение")


# озвучка и отправка ответа
def transcribe_tts(message, answer_gpt, total_gpt_tokens):
    user_id = message.chat.id
    try:
        good_status, tts_symbols = is_tts_symbol_limit(user_id, answer_gpt)
        if not good_status:
            bot.send_message(user_id, tts_symbols)
            return
        add_message(user_id=user_id, full_message=[answer_gpt, 'assistant', total_gpt_tokens, tts_symbols, 0])
        # Преобразование ответа в аудио и отправка
        status_tts, voice_response = text_to_speech(answer_gpt)
        if status_tts:
            bot.send_voice(user_id, voice_response, reply_to_message_id=message.id)
        else:
            bot.send_message(user_id, answer_gpt, reply_to_message_id=message.id)
    except Exception as e:
        print(e)
        logging.error(e)
        bot.send_message(message.chat.id, "Не получилось ответить. Попробуй записать другое сообщение")


# обрабатываем текстовые сообщения
@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_id = message.from_user.id

    # ВАЛИДАЦИЯ: проверяем, есть ли место для ещё одного пользователя (если пользователь новый)
    status_check_users, error_message = check_number_of_users(user_id)
    if not status_check_users:
        bot.send_message(user_id, error_message)  # мест нет =(
        return

    # БД: добавляем сообщение пользователя и его роль в базу данных
    full_user_message = [message.text, 'user', 0, 0, 0]
    add_message(user_id=user_id, full_message=full_user_message)
    # у нас уже есть функция с обращением к gpt, поэтому просто
    # используем её и указываем параметр move_on=False, чтобы текст не озвучивался
    access_to_gpt(message, move_on=False)

# обрабатываем все остальные типы сообщений
@bot.message_handler(func=lambda: True)
def handler(message):
    bot.send_message(message.from_user.id, "Отправь мне голосовое или "
                                           "текстовое сообщение, и я тебе отвечу")


bot.infinity_polling(timeout=60, long_polling_timeout=40)
