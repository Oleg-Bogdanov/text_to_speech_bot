MAX_USERS = 3  # максимальное кол-во пользователей
MAX_GPT_TOKENS = 120  # максимальное кол-во токенов в ответе GPT
COUNT_LAST_MSG = 4  # кол-во последних сообщений из диалога

# лимиты для пользователя
MAX_USER_STT_BLOCKS = 10  # 10 аудиоблоков
MAX_USER_TTS_SYMBOLS = 5000  # 5 000 символов
MAX_USER_GPT_TOKENS = 2000  # 2 000 токенов
MAX_TTS_PROJECT = 15000
MAX_TTS_SYMBOLS = 400

HOME_DIR = '/home/student/voice-assistant-tg'   # путь к папке с проектом
LOGS = f'{HOME_DIR}/logs.txt'  # файл для логов
DB_FILE = f'{HOME_DIR}/messages.db'  # файл для базы данных
SYSTEM_PROMPT = [{'role': 'system', 'text': 'Я - полезный помощник, основанный на '
                                            'ИИ yandex GPT. Ты всегда готов помочь. Предпочитаешь'
                                            ' давать подробные ответы на вопросы, чтобы '
                                            'максимально удовлетворить вашу потребность в '
                                            'информации.'}]  # список с системным промтом


IAM_TOKEN_PATH = f'{HOME_DIR}/creds/iam_token.txt'  # файл для хранения iam_token
FOLDER_ID_PATH = f'{HOME_DIR}/creds/folder_id.txt'  # файл для хранения folder_id
BOT_TOKEN_PATH = f'{HOME_DIR}/creds/bot_token.txt'  # файл для хранения bot_token
# HOME_DIR = 'C:/Users/olegb/PycharmProjects/pythonProject42/creds'
# BOT_TOKEN_PATH = f'{HOME_DIR}/bot_token.txt'
# FOLDER_ID_PATH = f'{HOME_DIR}/folder_id.txt'
# IAM_TOKEN_PATH = f'{HOME_DIR}/iam_token.txt'
# LOGS = f'{HOME_DIR}/logs.txt'
# DB_FILE = f'{HOME_DIR}/messages.db'

BOT_TOKEN = f'7077602673:AAGQ04U8RejmxjSBvlxJHlb1fm4Kg8AWBZI'
FOLDER_ID = f'b1gv7tv6tfmd502i7fif'
IAM_TOKEN = "t1.9euelZqVm5WZns_PkM-Pjo6SyMnPx-3rnpWai8iLlprInZCPzJKQk4-Rl5bl9Pd1RBlO-e9CACvD3fT3NXMWTvnvQgArw83n9euelZqakI7Izs3HkIrPk52az5iTmO_8xeuelZqakI7Izs3HkIrPk52az5iTmL3rnpWamcyWy5WQzYvHyZqalZ7MnMm13oac0ZyQko-Ki5rRi5nSnJCSj4qLmtKSmouem56LntKMng.xJYzB8i_WhSVVmCvakCfr5Ftl8fZz7dFVtb-oWm1oRGeP5HwQvoMDVosQyh5IuvWAJBf6-Es7sHQyjWLdzT3AQ"
LOGS = f'logs.txt'
DB_FILE = f'messages.db'
errors_list = 'список возможных ошибок: \n' \
              '400 - сервер не понял, что от него хотят \n' \
              '403 - доступ к странице запрещён \n' \
              '429 - слишком много запросов' \
              '404 - данных по запросу нет на сервере \n' \
              '500 - ошибка сервера, вы не виноваты \n' \
              'если вашей ошибки нет в списке, обратитесь в интернет'
