# Copyright (c) 2026 Mauro Nolan Fernández. Todos los derechos reservados.
import time
from services.antispam import is_bot, is_rate_limited, _attempts, get_client_ip, _purge_expired, HONEYPOT_FIELD


    
#--------------------------Tests for the is_bot function--------------------
def test_honeypot_vacio_no_es_bot():
    assert is_bot({"website": ""}) is False
        
def test_honeypot_con_contenido_si_es_bot():
    data = {"website": "http://example.com"}
    assert is_bot(data)
    
def test_honeypot_solo_espacios_es_bot_sin_limpieza_previa():
    # clean_contact_data corre antes en routes.py y deja cadena vacía.
    # Este test documenta que is_bot por sí solo NO hace strip.
    assert is_bot({HONEYPOT_FIELD: '   '}) is True
        
def test_honeypot_con_clave_falta_no_es_bot():
    data = {}
    assert not is_bot(data)
    
#--------------------------Tests for the is_rate_limited function--------------------

def test_cinco_peticion_no_es_rechazada():
    for _ in range(5):
        assert is_rate_limited("1.2.3.4") is False

def test_sexta_peticion_es_rechazada():
    for _ in range(5):
        is_rate_limited("1.2.3.4")
    assert is_rate_limited("1.2.3.4") is True
    
def test_peticion_diferente_ip_no_es_rechazada():
    for _ in range(5):
        is_rate_limited("1.2.3.4")
    assert is_rate_limited("5.6.7.8") is False
    
#--------------------------Tests for _attempts --------------------   
def test_intentos_se_reinician_despues_de_60_segundos():
    _attempts["1.2.3.4"] = [time.time() - 120] * 5
    assert is_rate_limited("1.2.3.4") is False  
    


# -------------------- get_client_ip --------------------
def test_sin_proxy_usa_remote_addr():
    assert get_client_ip({'CF-Connecting-IP': '9.9.9.9'}, '1.2.3.4', trust_proxy=False) == '1.2.3.4'

def test_con_proxy_usa_cf_connecting_ip():
    assert get_client_ip({'CF-Connecting-IP': '9.9.9.9'}, '1.2.3.4', trust_proxy=True) == '9.9.9.9'

def test_con_proxy_cae_a_forwarded_for():
    assert get_client_ip({'X-Forwarded-For': '9.9.9.9, 10.0.0.1'}, '1.2.3.4', trust_proxy=True) == '9.9.9.9'

def test_con_proxy_sin_cabeceras_cae_a_remote_addr():
    assert get_client_ip({}, '1.2.3.4', trust_proxy=True) == '1.2.3.4'


# -------------------- _purge_expired --------------------
def test_purga_elimina_ips_caducadas():
    _attempts['1.1.1.1'] = [time.time() - 120]
    _purge_expired(time.time())
    assert '1.1.1.1' not in _attempts

def test_purga_conserva_ips_vigentes():
    _attempts['2.2.2.2'] = [time.time()]
    _purge_expired(time.time())
    assert '2.2.2.2' in _attempts