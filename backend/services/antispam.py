import time

_attempts = {} 
WINDOW_SECONDS = 60
MAX_ATTEMPTS = 5

def is_bot(data):
    trap = data.get('website')
    return bool(trap and trap.strip())

def is_rate_limited(ip):
    
    now = time.time()
    if ip not in _attempts:
        _attempts[ip] = []
    _attempts[ip] = [t for t in _attempts[ip] if (now - t) < WINDOW_SECONDS]
    if len(_attempts[ip]) >= MAX_ATTEMPTS:
        return True
    _attempts[ip].append(now)
    return False