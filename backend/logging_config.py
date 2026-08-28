import json
import logging

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "time": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "func": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
        }
        return json.dumps(log_data, ensure_ascii=False)

def setup_logging(app):
    #Opcion usando la class JsonFormatter configurada mas arriba
    
    handler = logging.StreamHandler()       # a dónde: salida estándar
    handler.setFormatter(JsonFormatter())   # con qué aspecto
    
    root = logging.getLogger()              # el logger raíz
    root.handlers.clear()                   # unifica los logs de Flask y server
    root.addHandler(handler)                # añade el handler
    root.setLevel(logging.INFO)             # criba el umbral desde el que se reciben los logs
    
    #Opcion de texto plano sin formater. 
    # Se guarda para revisión didáctica
    '''
    logging.basicConfig(
        level=logging.INFO, #Se sube a WARNING en produccion (level=logging.WARNING)
        format= '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    )
    '''
    