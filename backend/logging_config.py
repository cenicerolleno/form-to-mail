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
    
    level = app.config["LOG_LEVEL"]
    log_format = app.config["LOG_FORMAT"]
    
    if log_format == "json":
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )
    handler = logging.StreamHandler()       # a dónde: salida estándar
    handler.setFormatter(formatter)         # con qué aspecto
    
    root = logging.getLogger()              # el logger raíz
    root.handlers.clear()                   # unifica los logs de Flask y server
    root.addHandler(handler)                # añade el handler
    root.setLevel(level)                    # criba el umbral desde el que se reciben los logs
    
    