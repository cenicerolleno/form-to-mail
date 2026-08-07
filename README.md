# form-to-mail

Backend mínimo para formularios de contacto: recibe una petición POST, valida los datos, aplica barreras antispam y envía el contenido por correo electrónico mediante una API transaccional.

Pensado para desplegarse de forma independiente y ser consumido por cualquier frontend (HTML plano, Bootstrap, React…) desde otro origen.

> ⚠️ **Estado:** en desarrollo. Las tres barreras antispam y la validación están operativas; **el envío de correo todavía no está implementado** (el endpoint devuelve `200` sin enviar nada).

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
│   │   ├── validation.py   # validación de campos y consentimiento
│   │   ├── antispam.py     # honeypot y rate limiting
│   │   └── mailer.py       # envío de correo (pendiente)
│   └── requirements.txt
└── frontend/
```

**Principio de diseño:** `services/` no importa nada de Flask. Recibe y devuelve estructuras de datos de Python, lo que permite testear la lógica sin levantar el servidor y migrar a otra plataforma reescribiendo solo `routes.py`.

`services/` responde preguntas; `routes.py` traduce esas respuestas a códigos HTTP.

---

## Instalación y arranque

Todos los comandos se ejecutan desde el directorio `backend/`.

```bash
cd backend
python -m venv venv
source venv/bin/activate        # macOS / Linux
source venv/Scripts/activate    # Windows (Git Bash)
pip install -r requirements.txt
```

### Levantar el servidor

```bash
flask --app app:create_app run --debug --port 5001
```

Requiere tener el entorno virtual activado (ver paso anterior). Disponible en `http://localhost:5001`.

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
| `website` | string | — | **campo trampa (honeypot)** |

> ⚠️ **`website` es el honeypot.** En el frontend debe existir como input **oculto por CSS** y vacío. El backend descarta silenciosamente cualquier petición que lo traiga relleno. **El `name` del input y la clave que comprueba `antispam.py` deben coincidir exactamente**: si no, la trampa deja de funcionar sin dar ningún error.

**Respuestas:**

| Código | Significado |
|---|---|
| `200` | Recibido correctamente *(también se devuelve al detectar el honeypot, de forma deliberada)* |
| `400` | Body ausente o inválido, o errores de validación (se devuelve el detalle por campo) |
| `429` | Límite de peticiones superado |

**Orden de las barreras** (criterio *fail-fast*, de más barata a más cara):

1. Rate limiting → `429`
2. Body ausente o malformado → `400`
3. Honeypot → `200` (éxito falso, deliberado)
4. Validación de campos y consentimiento → `400`
5. Envío de correo → `200` / `502` *(pendiente)*

**Política de rate limiting actual:** 5 peticiones por IP cada 60 segundos. Configurable en las constantes `MAX_ATTEMPTS` y `WINDOW_SECONDS` de `services/antispam.py`.

---

## Deuda técnica

> Limitaciones conocidas y asumidas conscientemente en la versión de laboratorio. **Deben revisarse antes de desplegar en cualquier proyecto real.**

### 🔴 Prioritarias antes de producción

**1. Fuga de memoria en el rate limiter.**
El diccionario `_attempts` de `services/antispam.py` acumula una entrada por cada IP que haya contactado alguna vez y **nunca las elimina**. Las listas de timestamps se filtran, pero las claves permanecen indefinidamente. En un despliegue de larga duración el consumo de memoria crece sin techo.

*Opciones de solución:*
- Purgar las IPs sin intentos vigentes en cada llamada (rápido de implementar, coste creciente con el número de claves).
- Purga periódica cada N peticiones (mejor equilibrio, sigue siendo casero).
- **Migrar el contador a Redis**, que expira las claves automáticamente. Es la solución estándar de la industria y elimina de paso los puntos 2 y 3.

**2. El estado en memoria no sobrevive a un reinicio ni a múltiples procesos.**
El contador se pierde al reiniciar el servidor y no se comparte entre workers. Con varios procesos, el límite efectivo se multiplica por el número de workers.

**3. ⚠️ El rate limiting NO funciona detrás de un proxy o CDN.**
`request.remote_addr` devuelve la IP del proxy, no la del visitante: **todos los usuarios compartirían un único contador y se bloquearían entre sí**. Debe leerse la cabecera `X-Forwarded-For` — pero solo confiando en el proxy concreto del despliegue, ya que un cliente puede falsificarla para saltarse el límite. Es configuración específica de la plataforma de despliegue.

### 🟡 Incompatibilidad con serverless

Si el destino final fuera una plataforma serverless (Vercel, Netlify, Cloudflare Workers), **el rate limiting dejaría de funcionar por completo**: cada invocación puede ejecutarse en un contenedor nuevo sin memoria compartida. En ese escenario el contador debe vivir fuera del proceso (Redis, KV store) de forma obligatoria, no opcional.

### 🟢 Mejoras opcionales

- **Validación de email:** la comprobación actual es provisional (presencia de `@` y posición). Sustituir por una librería especializada.
- **Persistencia de envíos fallidos:** descartada conscientemente (ver `BITACORA.md`). Si el proyecto pasara a mantenerse activamente, replantear.
- **Email de confirmación al usuario:** descartado por riesgo de *backscatter*. Solo considerar con la capa antispam consolidada.

---

## Pruebas de API

La colección de Bruno está versionada en el repositorio. Abrir Bruno, importar la colección y configurar la URL base como `http://localhost:5001`.

**Casos de prueba relevantes:**
- Body válido → `200`
- Body con JSON malformado → `400`
- Honeypot relleno **junto a campos inválidos** → debe devolver `200`, no `400` (verifica que el orden de barreras es correcto)
- 6 peticiones seguidas → la sexta debe devolver `429`

---

## Ramas

- `main` — estados estables y presentables
- `develop` — integración del trabajo en curso