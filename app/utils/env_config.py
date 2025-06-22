import os

PROJECT_NAME = os.environ.get('PROJECT_NAME', 'TRD_adaptor')
PROJECT_VERSION = os.environ.get('PROJECT_VERSION', '0.1.0')

HOST = os.environ.get('HOST', '0.0.0.0')
PORT = int(os.environ.get('PORT', 8000))

INPUT_PATH = os.environ.get('INPUT_PATH', 'input/')

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')
LOG_FILE = os.environ.get('LOG_FILE', None)

SSL_KEYFILE = os.environ.get('SSL_KEYFILE', f'{INPUT_PATH}keys/self_ssl/key.pem')
SSL_CERTFILE = os.environ.get('SSL_CERTFILE', f'{INPUT_PATH}keys/self_ssl/cert.pem')

CHATBOT_URL = os.environ.get('CHATBOT_URL', 'aichatbot-agent.clicknext.com')
CHATBOT_API_KEY = os.environ.get('CHATBOT_API_KEY', 'CN_CB_API_KEY:158f7ac1-8f18-42a5-ac68-fd16d1a604ef')

CHANNEL_ACCESS_TOKEN = os.environ.get('CHANNEL_ACCESS_TOKEN', 'q5iS+Dt3PUc2MZ3HEjs7F8VA28qepXUQLzhl4boNtJirVon52Ye+UeXbJ8Ijk4Op4gZTvPkQnJzJfQwBuS7kFt6dymGYK1Buz7icZ/kyIcd16NBPU9QqleMTV9uaZE0uxIJOhqVUbOma66jvghwD9QdB04t89/1O/w1cDnyilFU=')
CHANNEL_SECRET = os.environ.get('CHANNEL_SECRET', '8e93b4591d8b15d8f4e1de5c2be892a7')

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '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')

def print_config(logger):   
    """
    Print the configuration
    """
    logger.info(f'HOST: {HOST}')
    logger.info(f'PORT: {PORT}')