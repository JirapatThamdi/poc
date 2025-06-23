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

CHATBOT_URL = os.environ.get('CHATBOT_URL', '')
CHATBOT_API_KEY = os.environ.get('CHATBOT_API_KEY', '')

CHANNEL_ACCESS_TOKEN = os.environ.get('CHANNEL_ACCESS_TOKEN', '')
CHANNEL_SECRET = os.environ.get('CHANNEL_SECRET', '')

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

def print_config(logger):   
    """
    Print the configuration
    """
    logger.info(f'HOST: {HOST}')
    logger.info(f'PORT: {PORT}')