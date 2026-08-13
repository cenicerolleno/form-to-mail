# form-to-mail

Backend y frontend mínimos para formularios de contacto: recibe una petición POST, valida los datos, aplica barreras antispam y envía el contenido por correo electrónico mediante una API transaccional.

Diseñado para desplegarse de forma independiente y ser consumido por cualquier frontend (HTML plano, Bootstrap, React…) desde otro origen.

---

## Stack

- **Backend:** Python 3.13 · Flask · Flask-CORS · requests
- **Frontend:** HTML + Bootstrap 5 (CDN) + JavaScript vanilla (ES Modules)
- **Email:** API transaccional de [Brevo](https://www.brevo.com/)
- **Pruebas de API:** [Bruno](https://www.usebruno.com/)

---

## Estructura

```
form-to-mail/
├── backend/
│   ├── app.py              # Application Factory
│   ├── config.py           # configuración desde variables de entorno
│   ├── routes.py           # capa HTTP
│   ├── services/           # lógica de negocio, sin dependencias de Flask
│   │   ├── validation.py   # validación de campos y consentimiento
│   │   ├── antispam.py     # honeypot y rate limiting
│   │   └── mailer.py       # envío vía API transaccional
│   └── requirements.txt
└── frontend/
    ├── index.html
    ├── css/styles.css
    └── js/
        ├── main.js         # orquesta: listener del submit
        ├── api.js          # comunicación con el backend
        ├── validation.js   # validación en cliente
        └── ui.js           # manipulación del DOM
```

### Principios de diseño

**`services/` no importa nada de Flask.** Recibe y devuelve estructuras de datos de Python, lo que permite testear la lógica sin levantar el servidor y migrar a otra plataforma reescribiendo solo `routes.py`.

**`services/` responde preguntas; `routes.py` traduce esas respuestas a códigos HTTP.** Un validador devuelve *"falta el email"*, no un `400`.

El frontend replica el mismo reparto: `api.js` y `validation.js` no tocan el DOM, `ui.js` no sabe que existe el backend, y `main.js` orquesta.

---

## Instalación

Todos los comandos del backend se ejecutan desde el directorio `backend/`.

```bash
cd backend
python -m venv venv
source venv/bin/activate        # macOS / Linux
source venv/Scripts/activate    # Windows (Git Bash)
pip install -r requirements.txt
```

### Variables de entorno

Crear un fichero `.env` dentro de `backend/` (no se versiona):

```
BREVO_API_KEY=tu_clave_de_api
MAIL_FROM=remitente@verificado.com
MAIL_TO=destinatario@ejemplo.com
ALLOWED_ORIGINS=http://127.0.0.1:5500,http://localhost:5500
```

| Variable | Descripción |
|---|---|
| `BREVO_API_KEY` | Clave de API de Brevo (*SMTP & API → API Keys*) |
| `MAIL_FROM` | Remitente verificado en Brevo. **No** es el email del visitante |
| `MAIL_TO` | Buzón que recibirá los mensajes del formulario |
| `ALLOWED_ORIGINS` | Orígenes autorizados, separados por comas y **sin espacios** |

> **Sobre `ALLOWED_ORIGINS`:** el origen debe coincidir exactamente, protocolo y puerto incluidos. `http://localhost:5500` y `http://127.0.0.1:5500` son orígenes distintos para el navegador.

### Arranque

**Backend** (con el entorno virtual activado):

```bash
flask --app app:create_app run --debug --port 5001
```

Disponible en `http://localhost:5001`. Se usa el puerto 5001 porque en macOS el 5000 suele estar ocupado por AirPlay.

**Frontend:** servir `frontend/` por HTTP (por ejemplo, con la extensión *Live Server* de VSCode).

> Los módulos ES **no funcionan abriendo `index.html` con doble clic** (protocolo `file://`): el navegador bloquea la carga.

---

## API

### `POST /contact`

Recibe los datos del formulario en formato JSON.

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
| `200` | Mensaje enviado correctamente |
| `400` | Body ausente o inválido, o errores de validación (se devuelve el detalle por campo) |
| `429` | Límite de peticiones superado |
| `502` | Fallo del proveedor de email |

Los errores de validación se devuelven agrupados, no de uno en uno:

```json
{
  "errors": {
    "email": "El formato del correo no es válido.",
    "consent": "El consentimiento es obligatorio."
  }
}
```

**Política de rate limiting:** 5 peticiones por IP cada 60 segundos. Configurable en `services/antispam.py`.

---

## Integración con otro frontend

El backend es agnóstico del cliente. Para consumirlo desde otro proyecto:

1. Añadir el origen del nuevo frontend a `ALLOWED_ORIGINS`.
2. Enviar un `POST` a `/contact` con `Content-Type: application/json` y los campos de la tabla anterior.
3. **Incluir el campo trampa antispam.** El formulario debe contener un input adicional oculto por CSS y vacío; el backend descarta silenciosamente cualquier petición que lo traiga relleno. El nombre exacto del campo está en `services/antispam.py` y debe coincidir **exactamente** con el atributo `name` del input: si no coinciden, la protección deja de funcionar sin dar ningún error.

`frontend/js/api.js` es reutilizable tal cual: no depende del DOM ni del resto de ficheros.

---

## Notas de despliegue

> ⚠️ Este repositorio está en fase de laboratorio. Antes de desplegarlo en un proyecto real hay que revisar los siguientes puntos.

**Autenticación del dominio en el proveedor de email.** Sin registros DKIM y SPF configurados, los correos se envían desde un dominio genérico del proveedor y tienen alta probabilidad de acabar en spam. **Es un requisito de entrega, no una mejora opcional.**

**Rate limiting.** La implementación actual guarda el estado en memoria del proceso. Esto implica que no sobrevive a reinicios, no se comparte entre workers y **no es compatible con plataformas serverless**. Para cualquier despliegue con varios procesos o de larga duración, el contador debe migrarse a un almacén externo (Redis o similar).

**Detección de IP.** El rate limiting usa la IP de la conexión directa. Detrás de un proxy o CDN debe configurarse la lectura de la cabecera correspondiente, confiando únicamente en el proxy del despliegue concreto.

**CORS.** `ALLOWED_ORIGINS` debe restringirse al dominio del proyecto. Conviene recordar que CORS solo lo aplican los navegadores: no protege el endpoint frente a peticiones directas. La protección real la aportan el rate limiting, el filtro antispam y la validación en servidor.

**Validación de email.** La comprobación del backend es provisional. Sustituir por una librería especializada.

**Titularidad de las cuentas.** En un modelo de entrega sin mantenimiento, la cuenta del proveedor de email y el dominio verificado deben estar a nombre del cliente.

---

## Pruebas

La colección de Bruno está versionada en el repositorio. Configurar la URL base como `http://localhost:5001`.

**Casos relevantes:**

| Caso | Esperado |
|---|---|
| Body válido | `200` + correo recibido |
| JSON malformado o ausente | `400` |
| Campos inválidos | `400` con detalle por campo |
| Campo trampa relleno **junto a campos inválidos** | `200` (verifica el orden de las barreras) |
| 6 peticiones seguidas | La sexta devuelve `429` |
| `Origin` no autorizado | Respuesta sin cabecera `Access-Control-Allow-Origin` |

---

## Ramas

- `main` — estados estables y presentables
- `develop` — integración del trabajo en curso