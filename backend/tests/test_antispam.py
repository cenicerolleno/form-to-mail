import time
from services.antispam import is_bot, is_rate_limited, _attempts

    
#--------------------------Tests for the is_bot function--------------------
def test_honeypot_vacio_no_es_bot():
    assert is_bot({"website": ""}) is False
        
def test_honeypot_con_contenido_si_es_bot():
    data = {"website": "http://example.com"}
    assert is_bot(data)
    
def test_honeypot_solo_espacios_no_es_bot():
    data = {'website': '   '}
    assert not is_bot(data)
    
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