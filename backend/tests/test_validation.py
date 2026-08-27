from services.validation import validate_contact_data


# ----------Tests for the name field--------------------
def test_nombre_valido_no_da_error():
    data = {"name": "Mauro"}                    # 1. preparar
    errors = validate_contact_data(data)        # 2. ejecutar
    assert "name" not in errors                 # 3. comprobar
    
def test_nombre_de_61_caracteres_da_error():
    data = {"name": "a" * 61}                   
    errors = validate_contact_data(data)        
    assert "name" in errors                     
    
def test_nombre_ausente_da_error():
    data = {}                                   
    errors = validate_contact_data(data)        
    assert "name" in errors                     
    
def test_nombre_con_solo_espacios_da_error():
    data = {"name": "   "}                      
    errors = validate_contact_data(data)        
    assert "name" in errors
    
def test_nombre_con_exactamente_60_caracteres_no_da_error():
    data = {"name": "a" * 60}                   
    errors = validate_contact_data(data)        
    assert "name" not in errors
    
# Tests for the email field

def test_email_valido_no_da_error():
    data = {"email": "user@example.com"}
    errors = validate_contact_data(data)
    assert "email" not in errors

def test_email_invalido_da_error():
    data = {"email": "invalid-email"}
    errors = validate_contact_data(data)
    assert "email" in errors
    
def test_email_con_dominio_vacio_da_error():
    data = {"email": "user@.com"}
    errors = validate_contact_data(data)
    assert "email" in errors
  
def test_email_sin_punto_en_dominio_da_error():
    data = {"email": "user@examplecom"}
    errors = validate_contact_data(data)
    assert "email" in errors
    
def test_email_con_acentos_no_da_error():
    data = {"email": "josé@ejemplo.com"}
    errors = validate_contact_data(data)
    assert "email" not in errors
  
def test_email_ausente_da_error():
    data = {}
    errors = validate_contact_data(data)
    assert "email" in errors

def test_email_con_solo_espacios_da_error():
    data = {"email": "   "}
    errors = validate_contact_data(data)
    assert "email" in errors
    
#--------------------------Tests for the phone field--------------------
def test_telefono_valido_no_da_error():
    data = {"phone": "1234567890"}
    errors = validate_contact_data(data)
    assert "phone" not in errors

def test_telefono_invalido_da_error():
    data = {"phone": "abcd"}
    errors = validate_contact_data(data)
    assert "phone" in errors

def test_telefono_con_mas_de_20_caracteres_da_error():
    data = {"phone": "1" * 21}
    errors = validate_contact_data(data)
    assert "phone" in errors
    
def test_telefonono_con_exactamente_20_caracteres_no_da_error():
    data = {"phone": "1" * 20}
    errors = validate_contact_data(data)
    assert "phone" not in errors
    
def test_telefono_con_espacios_y_guiones_no_da_error():
    data = {"phone": "+1 234-567-890"}
    errors = validate_contact_data(data)
    assert "phone" not in errors
    
def test_telefono_con_parentesis_no_da_error():
    data = {"phone": "(123) 456-7890"}
    errors = validate_contact_data(data)
    assert "phone" not in errors
    
#--------------------------Tests for the message field--------------------
def test_mensaje_valido_no_da_error():
    data = {"message": "Este es un mensaje válido."}
    errors = validate_contact_data(data)
    assert "message" not in errors  

def test_mensaje_con_mas_de_500_caracteres_da_error():
    data = {"message": "a" * 501}
    errors = validate_contact_data(data)
    assert "message" in errors


def test_mensaje_ausente_da_error():
    data = {}
    errors = validate_contact_data(data)
    assert "message" in errors
    
def test_mensaje_con_solo_espacios_da_error():
    data = {"message": "   "}
    errors = validate_contact_data(data)
    assert "message" in errors
    
def test_mensaje_con_exactamente_500_caracteres_no_da_error():
    data = {"message": "a" * 500}
    errors = validate_contact_data(data)
    assert "message" not in errors
    
#--------------------------Tests for the consent field--------------------
def test_consentimiento_verdadero_no_da_error():
    data = {"consent": True}
    errors = validate_contact_data(data)
    assert "consent" not in errors  
    
def test_consentimiento_falso_da_error():
    data = {"consent": False}
    errors = validate_contact_data(data)
    assert "consent" in errors
    
def test_consentimiento_ausente_da_error():
    data = {}
    errors = validate_contact_data(data)
    assert "consent" in errors
    
def test_consentimiento_nulo_da_error():
    data = {"consent": None}
    errors = validate_contact_data(data)
    assert "consent" in errors  
    
def test_consentimiento_con_valor_no_booleano_da_error():
    data = {"consent": "yes"}
    errors = validate_contact_data(data)
    assert "consent" in errors  
    
def test_consentimiento_con_valor_numerico_da_error():
    data = {"consent": 1}
    errors = validate_contact_data(data)
    assert "consent" in errors
    

def test_datos_completos_y_validos_no_dan_errores():
    data = {
        "name": "Mauro",
        "email": "mauro@example.com",
        "phone": "1234567890",
        "message": "Este es un mensaje válido.",
        "consent": True
    }
    assert validate_contact_data(data) == {}
