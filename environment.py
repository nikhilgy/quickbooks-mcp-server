import os
from dotenv import load_dotenv

load_dotenv()

def get_sensitive_data():
    return {
        'quickbooks client id': Environment.get('QUICKBOOKS_CLIENT_ID'),
        'quickbooks client secret': Environment.get('QUICKBOOKS_CLIENT_SECRET'),
        'quickbooks refresh token': Environment.get('QUICKBOOKS_REFRESH_TOKEN'),
        'quickbooks company id': Environment.get('QUICKBOOKS_COMPANY_ID'),
    }

class Environment:
    @staticmethod
    def get(__key, __default=None):
        return os.getenv(__key, __default)

    __getattr__ = dict.get 