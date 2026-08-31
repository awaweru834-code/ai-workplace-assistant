from slowapi import Limiter
from slowapi.util import get_remote_address

# Single shared limiter — imported by every router that needs rate limiting,
# and registered on the FastAPI app in main.py.
limiter = Limiter(key_func=get_remote_address)
