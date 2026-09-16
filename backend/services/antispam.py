# Copyright (c) 2026 Mauro Nolan Fernández. Todos los derechos reservados.
import time

_attempts = {}
WINDOW_SECONDS = 60
MAX_ATTEMPTS = 5

# Nombre del campo trampa. Debe coincidir EXACTAMENTE con el `name` del input
# oculto en el HTML: si no coinciden, la trampa deja de funcionar en silencio.
HONEYPOT_FIELD = 'website'

# Cada cuántas llamadas se hace la limpieza completa del diccionario.
PURGE_EVERY = 100
_calls_since_purge = 0


def get_client_ip(headers, remote_addr, trust_proxy=False):
    """Devuelve la IP del visitante.

    Con trust_proxy=False usa remote_addr: sin proxy delante, las cabeceras
    vienen del cliente y son falsificables.

    Con trust_proxy=True lee CF-Connecting-IP, que Cloudflare sobrescribe
    siempre y el cliente no puede falsear. Si no está, cae a la primera
    entrada de X-Forwarded-For (el cliente original) y por último a remote_addr.
    """
    if not trust_proxy:
        return remote_addr

    cf_ip = headers.get('CF-Connecting-IP')
    if cf_ip:
        return cf_ip.strip()

    forwarded = headers.get('X-Forwarded-For')
    if forwarded:
        return forwarded.split(',')[0].strip()

    return remote_addr


def is_bot(data):
    return bool(data.get(HONEYPOT_FIELD))


def _purge_expired(now):
    """Elimina las IPs sin intentos vigentes.

    El filtrado por IP de is_rate_limited vacía las listas pero deja las
    claves, así que el diccionario crece sin techo. Esta purga recorre todo
    el diccionario, y por eso no se hace en cada llamada: sería O(n) por
    petición, más caro cuantas más IPs haya.
    """
    expired = [
        ip for ip, timestamps in _attempts.items()
        if not any((now - t) < WINDOW_SECONDS for t in timestamps)
    ]
    for ip in expired:
        del _attempts[ip]


def is_rate_limited(ip):
    global _calls_since_purge

    now = time.time()

    _calls_since_purge += 1
    if _calls_since_purge >= PURGE_EVERY:
        _calls_since_purge = 0
        _purge_expired(now)

    if ip not in _attempts:
        _attempts[ip] = []
    _attempts[ip] = [t for t in _attempts[ip] if (now - t) < WINDOW_SECONDS]

    if len(_attempts[ip]) >= MAX_ATTEMPTS:
        return True

    _attempts[ip].append(now)
    return False