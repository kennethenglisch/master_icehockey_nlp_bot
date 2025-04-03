import os

from fastapi.security.api_key import APIKeyHeader
from fastapi import Security, HTTPException
from starlette.status import HTTP_403_FORBIDDEN
import openai

api_key_header = APIKeyHeader(name="access_token", auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    api_key = api_key_header
    if api_key_header == "masterarbeit2025abgabe":
        api_key = get_api_key_local()

    result = check_openai_api_key(api_key)
    if result["success"]:
        return api_key
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail=f"Could not validate API KEY. \nError: {result['error_message']}"
        )

def check_openai_api_key(api_key):
    openai.api_key = api_key
    try:
        openai.models.list()
    except openai.APITimeoutError as e:
        return {"success": False, "error_message": "OpenAI API request timed out."}
    except openai.APIConnectionError as e:
        return {"success": False, "error_message": "OpenAI API request failed to connect."}
    except openai.APIError as e:
        return {"success": False, "error_message": "OpenAI API returned an API Error."}
    except openai.AuthenticationError as e:
        return {"success": False, "error_message": "OpenAI API request was not authorized."}
    except openai.PermissionDeniedError as e:
        return {"success": False, "error_message": "OpenAI API request was not permitted."}
    except openai.RateLimitError as e:
        return {"success": False, "error_message": "OpenAI API request exceeded rate limit."}
    except Exception as e:
        return {"success": False, "error_message": "An unknown error occurred."}
    else:
        return {"success": True, "error_message": None}


def get_api_key_local():
    if os.environ.get('OPENAI_API_KEY'):
        return os.environ.get('OPENAI_API_KEY')
    else:
        raise Exception('Could not find Api-Key')