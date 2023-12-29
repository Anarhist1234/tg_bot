import os


class DatabaseConfig:
    # DB_NAME = os.getenv('DB_NAME', "call_system")
    # DB_PASSWORD = os.getenv('DB_PASSWORD', "WFpnJMjtPKbwpNaBZQuewNBuCGYQWMyD")
    # DB_HOST = os.getenv('DB_HOST', "65.109.25.177")
    # DB_PORT = os.getenv('DB_PORT', "5432")
    # DB_USER = os.getenv('DB_USER', "uhead")
    # DB_URL = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

    DB_NAME = os.getenv('DB_NAME', "call_system")
    DB_PASSWORD = os.getenv('DB_PASSWORD', "WFpnJMjtPKbwpNaBZQuewNBuCGYQWMyD")
    DB_HOST = os.getenv('DB_HOST', "65.109.25.177")
    DB_PORT = os.getenv('DB_PORT', "5432")
    DB_USER = os.getenv('DB_USER', "uhead")
    DB_URL = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'


class ADatabaseConfig(DatabaseConfig):
    # DB_NAME = os.getenv('DB_NAME', "call_syste3m")
    # DB_PASSWORD = os.getenv('DB_PASSWORD', "WFpnJMjtPKbwpNaBZQuewNBuCGYQWMyD")
    # DB_HOST = os.getenv('DB_HOST', "65.109.25.177")
    # DB_PORT = os.getenv('DB_PORT', "5432")
    # DB_USER = os.getenv('DB_USER', "uhead")

    DB_NAME = os.getenv('DB_NAME', "call_system")
    DB_PASSWORD = os.getenv('DB_PASSWORD', "WFpnJMjtPKbwpNaBZQuewNBuCGYQWMyD")
    DB_HOST = os.getenv('DB_HOST', "65.109.25.177")
    DB_PORT = os.getenv('DB_PORT', "5432")
    DB_USER = os.getenv('DB_USER', "uhead")

    pg_driver = 'asyncpg'
    DB_URL = f'postgresql+{pg_driver}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

class APIConfig:
    API_PREFIX = os.getenv('API_PREFIX', '/api')

    API_HOST = os.getenv('API_HOST', '127.0.0.1')
    API_PORT = os.getenv('API_PORT', 8002)
    API_PORT_RESERVE = os.getenv('API_PORT_RESERVE', 8002)
    RESERVE = os.getenv('RESERVE', False)

    API_DOCS_URL = API_PREFIX + '/docs'
    API_OPENAPI_URL = API_PREFIX + '/openapi.json'


class AsteriskDatabaseConfig:
    DB_NAME = "asterisk_db"
    DB_NAME_PG = "postgres"
    DB_USER = "asterisk"
    DB_PASSWORD = "Qwerty123"
    DB_HOST = "localhost"
    DB_PORT = "5432"
    DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    DB_URL_POSTGRES = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME_PG}"

class API_URLs:
    conversion = 'http://127.0.0.1:8000/conversion'
    average_seconds = 'http://127.0.0.1:8000/avg_sec_in_status_ready_for_each_user'
    lost_calls = 'http://127.0.0.1:8000/count_lost_calls'
    info_phones = 'http://127.0.0.1:8000/info_phones'

class TelegramData:
    access_token = '6948990728:AAGHj30De5DHCroQEXPSpelKjse2K6HURE4'
    access_token_ucall_bot = '6565965691:AAGJnmUfKrBc4FaUhHuBL3FNln9gI1Utk94'
    chat_id = '-4021081261'



