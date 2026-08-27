# form-to-mail

Backend y frontend mínimos para formularios de contacto: recibe una petición POST, valida los datos, aplica barreras antispam y envía el contenido por correo electrónico mediante una API transaccional.

Diseñado para desplegarse de forma independiente y ser consumido por cualquier frontend (HTML plano, Bootstrap, React…) desde otro origen.

---

## Stack

- **Backend:** Python 3.13 · Flask · Flask-CORS · requests · email-validator
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
        ├── main.js             # orquesta: listener del submit
        ├── api.js              # comunicación con el backend
        ├── validation.js       # validación en cliente
        ├── ui.js               # manipulación del DOM
        └── config.example.js   # plantilla de configuración
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

### Configuración del frontend

La URL del backend vive en `frontend/js/config.js`, que **está ignorado por Git**: cada máquina tiene el suyo. Hay que crearlo a partir de la plantilla versionada:

```bash
cp frontend/js/config.example.js frontend/js/config.js
```

Y ajustar `API_URL` al entorno correspondiente.

> ⚠️ **Este paso no es opcional.** Sin `config.js`, el import de `api.js` falla y **`main.js` no llega a ejecutarse**: el formulario recarga la página al enviar en lugar de dar un error visible.

### Arranque

**Backend** (con el entorno virtual activado):

```bash
flask --app app:create_app run --debug --port 5001
```

Disponible en `http://localhost:5001`. Se usa el puerto 5001 porque en macOS el 5000 suele estar ocupado por AirPlay.

**Frontend:** servir `frontend/` por HTTP. Dos opciones:

```bash
cd frontend
python -m http.server 5500
```

O la extensión *Live Server* de VSCode. El repositorio incluye un `.vscode/settings.json` que fija su raíz en `/frontend` y el puerto en 5500.

> Los módulos ES **no funcionan abriendo `index.html` con doble clic** (protocolo `file://`): el navegador bloquea la carga.

> ⚠️ **El puerto importa.** `ALLOWED_ORIGINS` autoriza orígenes exactos: si el servidor de estáticos arranca en 5501 en lugar de 5500, CORS rechazará las peticiones. Live Server salta al siguiente puerto libre si el suyo está ocupado, así que conviene verificar la URL real en la barra de direcciones ante cualquier error de CORS inesperado.

---

## Levantar el proyecto en GitHub Codespaces

Un Codespace es un contenedor Linux remoto: el código se ejecuta allí, pero **el navegador sigue siendo el de tu máquina**. Eso cambia cuatro cosas respecto al arranque en local.

### 1. Recrear lo que no viaja por Git

`venv/` y `.env` están en `.gitignore`, así que **no existen en el Codespace**. Hay que crearlos de nuevo:

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Y recrear el `.env` con las cuatro variables (ver sección anterior). Las claves no están en el repositorio: hay que copiarlas a mano.

### 2. Arrancar el backend escuchando en todas las interfaces

```bash
flask --app app:create_app run --debug --port 5001 --host 0.0.0.0
```

El `--host 0.0.0.0` es necesario para que el reenvío de puertos del Codespace alcance al servidor. Sin él, Flask solo escucha en la interfaz interna del contenedor.

### 3. Hacer público el puerto del backend

Al arrancar, el Codespace reenvía el puerto y genera una URL con el formato <cite index="25-1">`https://NOMBRE-DEL-CODESPACE-PUERTO.app.github.dev`</cite>.

<cite index="25-1">Los puertos reenviados son privados por defecto: solo visibles para ti</cite>. Y "para ti" significa *para tu sesión autenticada de GitHub*, no para una petición `fetch` lanzada desde otra página — que llegará sin credenciales y recibirá una pantalla de login en lugar de tu API.

Por eso hay que **cambiar la visibilidad del puerto 5001 a pública**: pestaña **PORTS** → clic derecho sobre el puerto → *Port Visibility* → *Public*. También desde la terminal:

```bash
gh codespace ports visibility 5001:public
```

> ⚠️ **Un puerto público es accesible por cualquiera que conozca la URL.** Con las credenciales de Brevo cargadas, eso significa que un tercero podría consumir tu cuota de envíos. Detén el Codespace al terminar y no compartas esas URLs.

### 4. Levantar el frontend

Desde el directorio `frontend/`:

```bash
cd frontend
python -m http.server 5500
```

**Es la forma recomendada en Codespaces.** No requiere extensiones, siempre sirve desde el directorio en el que se lanza, y el puerto es explícito y predecible — a diferencia de Live Server, que puede arrancar en otro puerto y romper la coincidencia con `ALLOWED_ORIGINS`.

Codespaces detectará el puerto 5500 y lo reenviará automáticamente.

### 5. Ajustar las dos URLs que apuntan a `localhost`

Este es el punto que más confunde, porque el código funciona en local y falla en Codespaces sin dar un error claro.

**No hace falta copiar las URLs a mano.** El Codespace las expone en variables de entorno; estos dos comandos las construyen:

```bash
echo "https://$CODESPACE_NAME-5001.$GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN/contact"
echo "https://$CODESPACE_NAME-5500.$GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN"
```

**La primera va a `API_URL`** en `frontend/js/config.js`. Desde el navegador de tu máquina, `localhost` es *tu propio ordenador*, no el contenedor.

**La segunda va a `ALLOWED_ORIGINS`** en el `.env`, y después hay que **reiniciar Flask**: el `.env` solo se lee al arrancar.

> ⚠️ **`API_URL` lleva la ruta `/contact`; `ALLOWED_ORIGINS` NO.** Un origen es solo protocolo + host + puerto: sin ruta y sin barra final. Es el error más común al copiar de una a otra.

Fíjate en que ambas son `https`. Un origen con protocolo distinto es un origen distinto, y CORS lo rechazará.

> **Ventaja de usar las variables de entorno:** <cite index="32-1">el dominio que GitHub usa para el reenvío de puertos puede cambiar con el tiempo</cite>, así que construir la URL a partir de `$GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN` devuelve siempre la correcta.

Como `config.js` está ignorado por Git, **no hay riesgo de commitear por accidente una URL de Codespace**: cada entorno mantiene la suya.

> <cite index="32-1">El dominio que GitHub usa para el reenvío de puertos puede cambiar con el tiempo, así que conviene no fijar estas URLs en el código de forma permanente</cite>. Son ajustes de sesión: revertirlos antes de commitear.

### Resumen de diferencias

| | Local | Codespaces |
|---|---|---|
| `venv`, `.env` y `config.js` | Ya existen | Hay que recrearlos |
| Arranque de Flask | `--port 5001` | `--port 5001 --host 0.0.0.0` |
| Servir el frontend | Live Server o `http.server` | `python -m http.server 5500` |
| Visibilidad del puerto 5001 | N/A | Debe ser **pública** |
| `API_URL` en `config.js` | `http://localhost:5001/contact` | URL reenviada del 5001 (`https`) |
| `ALLOWED_ORIGINS` | `http://127.0.0.1:5500` | URL reenviada del 5500 (`https`) |

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

4. **Apuntar el frontend al backend.** Copiar `config.example.js` a `config.js` y ajustar `API_URL`. Como `config.js` está ignorado por Git, cada entorno mantiene su propia URL sin riesgo de pisarse ni de subirla al repositorio.

`frontend/js/api.js` es reutilizable tal cual entre proyectos: no contiene configuración, solo la lógica de la petición.

---

## Notas de despliegue

> ⚠️ Este repositorio está en fase de laboratorio. Antes de desplegarlo en un proyecto real hay que revisar los siguientes puntos.

**Autenticación del dominio en el proveedor de email.** Sin registros DKIM y SPF configurados, los correos se envían desde un dominio genérico del proveedor y tienen alta probabilidad de acabar en spam. **Es un requisito de entrega, no una mejora opcional.**

**Rate limiting.** La implementación actual guarda el estado en memoria del proceso. Esto implica que no sobrevive a reinicios, no se comparte entre workers y **no es compatible con plataformas serverless**. Para cualquier despliegue con varios procesos o de larga duración, el contador debe migrarse a un almacén externo (Redis o similar).

**Detección de IP.** El rate limiting usa la IP de la conexión directa. Detrás de un proxy o CDN debe configurarse la lectura de la cabecera correspondiente, confiando únicamente en el proxy del despliegue concreto.

**CORS.** `ALLOWED_ORIGINS` debe restringirse al dominio del proyecto. Conviene recordar que CORS solo lo aplican los navegadores: no protege el endpoint frente a peticiones directas. La protección real la aportan el rate limiting, el filtro antispam y la validación en servidor.

**HTTPS en ambos extremos.** Si el frontend se sirve por HTTPS, el navegador **bloqueará las llamadas a un backend por HTTP** (*mixed content*), y lo hará sin error visible: la petición simplemente no sale. El backend debe estar tras HTTPS. Recuerda que el protocolo forma parte del origen: `http://` y `https://` son orígenes distintos a efectos de `ALLOWED_ORIGINS`.

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

### 🔵 Plan formativo (Módulo 3 · form-to-mail)

Ciclo completo pendiente de cerrar por primera vez:
tests → logging → config por entornos → Docker → despliegue → CI

- [ ] `DEBUG = True` fijo en `config.py` → configuración por entorno
- [ ] `CORS(app)` sin restringir orígenes
- [ ] `print(result["error"])` en `routes.py` → `logging`
- [ ] `_attempts` no es thread-safe (workers con hilos)
- [ ] Contrato duplicado y divergente: `validation.js` ↔ `validation.py`
- [ ] `getElementById(campo)` sin comprobar existencia en `ui.js`