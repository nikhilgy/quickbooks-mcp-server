import os
from dotenv import load_dotenv

load_dotenv()

class Environment:
    @staticmethod
    def get(__key, __default=None):
        return os.getenv(__key, __default) 