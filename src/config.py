import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

BOT_TOKEN = os.getenv('BOT_TOKEN')