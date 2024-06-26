import math  # математический модуль для округления
from config import *
from database import *
from yandex_gpt import count_gpt_tokens

# настраиваем запись логов в файл
logging.basicConfig(filename=LOGS, level=logging.ERROR,
                    format="%(asctime)s FILE: %(filename)s IN: "
                           "%(funcName)s MESSAGE: %(message)s", filemode="w")

# получаем количество уникальных пользователей, кроме самого пользователя
def check_number_of_users(user_id):
    count = count_users(user_id)
    if count is None:
        return None, "Ошибка при работе с БД"
    if count > MAX_USERS:
        return None, "Превышено максимальное количество пользователей"
    return True, ""

# проверяем, не превысил ли пользователь лимиты на общение с GPT
def is_gpt_token_limit(messages, total_spent_tokens):
    all_tokens = count_gpt_tokens(messages) + total_spent_tokens
    if all_tokens > MAX_USER_GPT_TOKENS:
        return None, f"Превышен общий лимит GPT-токенов {MAX_USER_GPT_TOKENS}"
    return all_tokens, ""


# проверяем, не превысил ли пользователь лимиты на преобразование аудио в текст
def is_stt_block_limit(user_id, duration):

    # Переводим секунды в аудиоблоки
    audio_blocks = math.ceil(duration / 15) # округляем в большую сторону
    # Функция из БД для подсчёта всех потраченных пользователем аудиоблоков
    all_blocks = count_all_blocks(user_id) + audio_blocks
    if all_blocks is not None:
        all_blocks += audio_blocks
    else:
        all_blocks = audio_blocks

    # Проверяем, что аудио длится меньше 30 секунд
    if duration >= 30:
        msg = "SpeechKit STT работает с голосовыми сообщениями меньше 30 секунд"
        return None, msg

    # Сравниваем all_blocks с количеством доступных пользователю аудиоблоков
    elif all_blocks >= MAX_USER_STT_BLOCKS:
        msg = f"Превышен общий лимит SpeechKit STT {MAX_USER_STT_BLOCKS}. Использовано {all_blocks} блоков. " \
              f"Доступно: {MAX_USER_STT_BLOCKS - all_blocks}"
        return None, msg
    else:
        return True, audio_blocks


# проверяем, не превысил ли пользователь лимиты на преобразование текста в аудио
def is_tts_symbol_limit(user_id, text):
    text_symbols = len(text)

    # Функция из БД для подсчёта всех потраченных пользователем символов
    all_symbols = count_all_limits(user_id, 'tts_symbols') + text_symbols

    # Сравниваем all_symbols с количеством доступных пользователю символов
    if project_symbol() >= MAX_TTS_PROJECT:
        msg = f'Превышен общий лимит SpeechKit TTS на проект {MAX_TTS_PROJECT}. Использовано: " \
              f"{all_symbols} символов.'
        return None, msg
    elif all_symbols >= MAX_USER_TTS_SYMBOLS:
        msg = f"Превышен общий лимит SpeechKit TTS {MAX_USER_TTS_SYMBOLS}. Использовано: " \
              f"{all_symbols} символов. Доступно: {MAX_USER_TTS_SYMBOLS - all_symbols}"
        return None, msg
    # Сравниваем количество символов в тексте с максимальным количеством символов в тексте
    elif text_symbols >= MAX_TTS_SYMBOLS:
        msg = f"Превышен лимит SpeechKit TTS на запрос {MAX_TTS_SYMBOLS}, в сообщении {text_symbols} символов"
        return None, msg
    else:
        return True, len(text)
