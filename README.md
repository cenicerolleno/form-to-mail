# form-to-mail

Backend mínimo para formularios de contacto: recibe una petición POST, valida los datos, aplica barreras antispam y envía el contenido por correo electrónico mediante una API transaccional.

Pensado para desplegarse de forma independiente y ser consumido por cualquier frontend (HTML plano, Bootstrap, React…) desde otro origen.

> ⚠️ **Estado:** en desarrollo. El endpoint valida datos pero aún no envía correos.

---

## Stack

- **Backend:** Python 3.13 · Flask · Flask-CORS
- **Frontend:** HTML + Bootstrap + JavaScript vanilla (ES Modules)
- **Email:** API transaccional *(pendiente de integrar)*
- **Pruebas de API:** [Bruno](https://www.usebruno.com/)

---

## Estructura

```
form-to-mail/
├── backend/
│   ├── app.py              # Application Factory
│   ├── config.py           # configuración por entornos
│   ├── routes.py           # endpoints (capa HTTP)
│   ├── services/           # lógica de negocio, sin dependencias de Flask
│   │   ├── validation.py
│   │   ├── antispam.py
│   │   └── mailer.py
│   └── requirements.txt
└── frontend/
```

**Principio de diseño:** `services/` no importa nada de Flask. Recibe y devuelve estructuras de datos de Python, lo que permite testear la lógica sin levantar el servidor y migrar a otra plataforma reescribiendo solo `routes.py`.

---

## Instalación y arranque

Todos los comandos se ejecutan desde el directorio `backend/`.

### macOS / Linux

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Windows (Git Bash)

```bash
cd backend
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
```

### Levantar el servidor

Con el entorno virtual activo(win o mac):

```bash
flask --app app:create_app run --debug --port 5001
```

Disponible en `http://localhost:5001`.

> **Nota:** se usa el puerto 5001 porque en macOS el 5000 suele estar ocupado por AirPlay.

---

## Variables de entorno

Crear un fichero `.env` dentro de `backend/` (no se versiona):

```
# pendiente de definir al integrar el envío de correo
```

---

## Endpoints

### `POST /contact`

Recibe los datos del formulario en formato JSON.

**Body:**

| Campo | Tipo | Obligatorio | Límite |
|---|---|---|---|
| `name` | string | ✅ | 60 |
| `email` | string | ✅ | formato válido |
| `phone` | string | ❌ | 20 |
| `message` | string | ✅ | 500 |
| `consent` | boolean | ✅ | debe ser `true` |

**Respuestas:**

| Código | Significado |
|---|---|
| `200` | Recibido correctamente |
| `400` | Body inválido o errores de validación (se devuelve el detalle por campo) |

---

## Pruebas de API

La colección de Bruno está versionada en el repositorio. Abrir Bruno, importar la colección y configurar la URL base como `http://localhost:5001`.

---

## Ramas

- `main` — estados estables y presentables
- `develop` — integración del trabajo en curso