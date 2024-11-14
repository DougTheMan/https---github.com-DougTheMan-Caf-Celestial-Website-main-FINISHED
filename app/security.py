from cryptography.fernet import Fernet  #negocio para encriptar cartões

from dotenv import load_dotenv
import os
load_dotenv('.env') #tem no init para ver

# key = Fernet.generate_key()
# print(key)
key = os.getenv('key')  #para pegar do env


f = Fernet(key)
