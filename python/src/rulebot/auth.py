import os

def get_api_key():
    if os.environ.get('OPENAI_API_KEY'):
        return os.environ.get('OPENAI_API_KEY')
    else:
        raise Exception('Could not find Api-Key')