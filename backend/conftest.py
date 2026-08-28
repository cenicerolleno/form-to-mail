import os
os.environ["FLASK_ENV"] = "testing"   
import pytest
from services.antispam import _attempts

@pytest.fixture(autouse=True)
def limpiar_intentos():
    _attempts.clear()