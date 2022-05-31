import os
from dotenv import load_dotenv
load_dotenv()

# token
# TOKEN = os.getenv('DISCORD_TOKEN')
TOKEN = os.getenv('DISCORD_DEBUG_TOKEN')

# db
DB_URL = os.getenv('DB_URL')
DB_USR = os.getenv('DB_USR')
DB_PW = os.getenv('DB_PW')
DB_DATABASE = os.getenv('DB_DATABASE')