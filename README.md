# form-to-mail

Backend y frontend mínimos para formularios de contacto: recibe una petición POST, valida los datos, aplica barreras antispam y envía el contenido por correo electrónico mediante una API transaccional.

Diseñado para desplegarse de forma independiente y ser consumido por cualquier frontend (HTML plano, Bootstrap, React…) desde otro origen.

> **Este repositorio es una plantilla.** Cada proyecto real se crea a partir de él con *Use this template* en GitHub y se adapta a su contrato de datos. Los arreglos que afecten a la plantilla se aplican **primero aquí** y después se propagan a las instancias; al revés, la plantilla se queda atrás y deja de servir como plantilla.

---

## Stack

- **Backend:** Python 3.13 · Flask · Flask-CORS · requests · email-validator
- **Frontend:** HTML + Bootstrap 5 (CDN) + JavaScript vanilla (ES Modules)
- **Email:** API transaccional de [Brevo](https://www.brevo.com/)
- **Tests:** pytest — 61 tests
- **Pruebas de API:** [Bruno](https://www.usebruno.com/)

---

## Estructura

```
form-to-mail/
├── backend/
│   ├── app.py              # Application Factory
│   ├── config.py           # configuración por entornos + validate()
│   ├── routes.py           # capa HTTP
│   ├── logging_config.py   # formateador JSON / texto según entorno
│   ├── conftest.py         # fixtures de pytest
│   ├── services/           # lógica de negocio, sin dependencias de Flask
│   │   ├── validation.py   # limpieza y validación de campos
│   │   ├── antispam.py     # honeypot, rate limiting y resolución de IP
│   │   └── mailer.py       # envío vía API transaccional
│   ├── tests/
│   ├── requirements.txt
│   └── requirements-dev.txt
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

**`services/` responde preguntas; `routes.py` traduce esas respuestas a códigos HTTP.** Un validador devuelve *"falta el email"*, no un `400`. `get_client_ip(headers, remote_addr, trust_proxy)` recibe datos planos, no el objeto `request`.

El frontend replica el mismo reparto: `api.js` y `validation.js` no tocan el DOM, `ui.js` no sabe que existe el backend, y `main.js` orquesta.

> **Señal de alarma en una revisión de código:** un `from flask import ...` dentro de `services/`.

---

## Instalación

Todos los comandos del backend se ejecutan desde el directorio `backend/`.

```bash
cd backend
python -m venv venv
source venv/bin/activate        # macOS / Linux
source venv/Scripts/activate    # Windows (Git Bash)
pip install -r requirements-dev.txt
```

### Variables de entorno

Crear un fichero `.env` dentro de `backend/` a partir de `.env.example` (no se versiona):

```
FLASK_ENV=development
BREVO_API_KEY=tu_clave_de_api
MAIL_FROM=remitente@dominio-autenticado.com
MAIL_TO=destinatario@ejemplo.com
ALLOWED_ORIGINS=http://127.0.0.1:5500,http://localhost:5500
```

| Variable | Obligatoria | Descripción |
|---|:---:|---|
| `BREVO_API_KEY` | ✅ | Clave de API de Brevo (*SMTP & API → API Keys*) |
| `MAIL_FROM` | ✅ | Remitente del dominio autenticado en Brevo. **No** es el email del visitante |
| `MAIL_TO` | ✅ | Buzón que recibirá los mensajes del formulario |
| `ALLOWED_ORIGINS` | ✅ | Orígenes autorizados, separados por comas |
| `FLASK_ENV` | — | `development` (por defecto) · `production` · `testing` |
| `TRUST_PROXY` | — | `true` **solo** detrás de un proxy de confianza. Por defecto `false` |

Las cuatro obligatorias están en `Config.REQUIRED`: si falta alguna, **el proceso falla al arrancar** con un mensaje que las nombra.

> **Por qué falla al arrancar y no en la primera petición.** Los atributos de clase se evalúan al importar el módulo, así que un `os.getenv()` sin valor deja un `None` que se propaga en silencio y revienta tres capas más abajo, en producción, con un error incomprensible. `Config.validate()` se ejecuta en `create_app()` **antes de construir la aplicación**: un fallo ruidoso al arrancar es infinitamente preferible.

> **Sobre `ALLOWED_ORIGINS`:** el origen debe coincidir exactamente, protocolo y puerto incluidos. `http://localhost:5500` y `http://127.0.0.1:5500` son orígenes distintos para el navegador. Y `www.dominio.com` es un origen distinto de `dominio.com`.

> ⚠️ **`MAIL_FROM` debe pertenecer a un dominio autenticado en el proveedor.** Si se usa un `@gmail.com` u otro dominio ajeno, la API devolverá `201` y **el correo no llegará nunca**: el proveedor del destinatario lo trata como suplantación y lo descarta en silencio.

> ⚠️ **`TRUST_PROXY` solo se activa cuando hay proxy delante.** Activado sin proxy, cualquiera puede saltarse el rate limiting enviando una cabecera `X-Forwarded-For` falsa. Desactivado detrás de proxy, todos los visitantes comparten un único contador y se bloquean entre sí.

### Configuración por entornos

`config.py` define una clase base con los valores **seguros por defecto** y tres variantes que la heredan. `create_app()` selecciona una según `FLASK_ENV`, o según el argumento `config_name` si se le pasa.

| Entorno | `DEBUG` | Nivel de log | Formato de log |
|---|---|---|---|
| `development` | `True` | `INFO` | texto |
| `production` | `False` | `WARNING` | JSON |
| `testing` | `False` | `DEBUG` | texto |

**Los valores seguros viven en la clase base y desarrollo los relaja.** Al revés —permisivo por defecto y restrictivo en producción— olvidar configurar el entorno dejaría el depurador expuesto en el servidor.

> ⚠️ **`DEBUG = True` nunca debe llegar a producción.** El depurador de Werkzeug expone una consola interactiva de Python ante cualquier error no capturado: quien provoque una excepción podría ejecutar código en el servidor.

**El entorno `testing`** usa credenciales falsas escritas en el propio `config.py`, de modo que la suite de tests no depende de que exista un `.env`. Se activa automáticamente al ejecutar `pytest`, y los tests pueden forzarlo con `create_app("testing")` sin depender de variables de entorno.

**El formato de log cambia con el entorno:** texto legible en desarrollo y en tests, JSON estructurado en producción, donde lo consumen las plataformas de despliegue y los agregadores de logs.

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
python -m http.server 5500 --bind 127.0.0.1
```

O la extensión *Live Server* de VSCode. El repositorio incluye un `.vscode/settings.json` que fija su raíz en `/frontend` y el puerto en 5500.

> Los módulos ES **no funcionan abriendo `index.html` con doble clic** (protocolo `file://`): el navegador bloquea la carga.

> ⚠️ **El puerto y la interfaz importan.** `ALLOWED_ORIGINS` autoriza orígenes exactos. Live Server salta al siguiente puerto libre si el suyo está ocupado, y `python -m http.server` sin `--bind` puede escuchar en IPv6 y dar origen `http://[::]:5500`, que no coincide con nada de la lista. Ante cualquier error de CORS inesperado, verificar la URL real en la barra de direcciones.

---

## Levantar el proyecto en GitHub Codespaces

Un Codespace es un contenedor Linux remoto: el código se ejecuta allí, pero **el navegador sigue siendo el de tu máquina**. Eso cambia cuatro cosas respecto al arranque en local.

### 1. Recrear lo que no viaja por Git

`venv/` y `.env` están en `.gitignore`, así que **no existen en el Codespace**. Hay que crearlos de nuevo:

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
```

Y recrear el `.env` (ver sección anterior). Las claves no están en el repositorio: hay que copiarlas a mano desde un gestor de contraseñas.

> ⚠️ **Comprobar la versión de Python del contenedor.** `requirements.txt` fija versiones exactas; si el Codespace trae una versión de Python distinta de la del proyecto, la instalación fallará con errores del tipo *"Could not find a version that satisfies the requirement"*. La pista está en el nombre del wheel que intenta descargar (`cp39`, `cp313`…).

### 2. Arrancar el backend escuchando en todas las interfaces

```bash
flask --app app:create_app run --debug --port 5001 --host 0.0.0.0
```

El `--host 0.0.0.0` es necesario para que el reenvío de puertos del Codespace alcance al servidor. Sin él, Flask solo escucha en la interfaz interna del contenedor.

### 3. Hacer público el puerto del backend

Al arrancar, el Codespace reenvía el puerto y genera una URL con el formato `https://NOMBRE-DEL-CODESPACE-PUERTO.app.github.dev`.

Los puertos reenviados son privados por defecto: solo visibles para tu sesión autenticada de GitHub, no para una petición `fetch` lanzada desde otra página — que llegará sin credenciales y recibirá una pantalla de login en lugar de la API.

Por eso hay que **cambiar la visibilidad del puerto 5001 a pública**: pestaña **PORTS** → clic derecho sobre el puerto → *Port Visibility* → *Public*. También desde la terminal:

```bash
gh codespace ports visibility 5001:public
```

> ⚠️ **Un puerto público es accesible por cualquiera que conozca la URL.** Con las credenciales de Brevo cargadas, eso significa que un tercero podría consumir la cuota de envíos. Detener el Codespace al terminar y no compartir esas URLs.

### 4. Levantar el frontend

```bash
cd frontend
python -m http.server 5500
```

**Es la forma recomendada en Codespaces.** No requiere extensiones, siempre sirve desde el directorio en el que se lanza, y el puerto es explícito y predecible.

### 5. Ajustar las dos URLs que apuntan a `localhost`

Este es el punto que más confunde, porque el código funciona en local y falla en Codespaces sin dar un error claro.

**No hace falta copiar las URLs a mano.** Estos dos comandos las construyen:

```bash
echo "https://$CODESPACE_NAME-5001.$GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN/contact"
echo "https://$CODESPACE_NAME-5500.$GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN"
```

**La primera va a `API_URL`** en `frontend/js/config.js`. Desde el navegador de tu máquina, `localhost` es *tu propio ordenador*, no el contenedor.

**La segunda va a `ALLOWED_ORIGINS`** en el `.env`, y después hay que **reiniciar Flask**: el `.env` solo se lee al arrancar.

> ⚠️ **`API_URL` lleva la ruta `/contact`; `ALLOWED_ORIGINS` NO.** Un origen es solo protocolo + host + puerto: sin ruta y sin barra final. Es el error más común al copiar de una a otra.

Ambas son `https`. Un origen con protocolo distinto es un origen distinto, y CORS lo rechazará.

> El dominio que GitHub usa para el reenvío de puertos puede cambiar con el tiempo, así que conviene construir las URLs a partir de las variables de entorno y no fijarlas en el código. Son ajustes de sesión: revertirlos antes de commitear.

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
|---|---|:---:|---|
| `name` | string | ✅ | 60, sin saltos de línea |
| `email` | string | ✅ | 254, formato válido |
| `phone` | string | ❌ | 20, sin saltos, al menos un dígito |
| `message` | string | ✅ | 500, saltos permitidos |
| `consent` | boolean | ✅ | debe ser `true` |
| `website` | string | — | **campo trampa (honeypot)** |

**Respuestas:**

| Código | Significado |
|---|---|
| `200` | Mensaje enviado correctamente — **y también al detectar el honeypot**, de forma deliberada |
| `400` | Body ausente o inválido, errores de validación, o email rechazado por el proveedor |
| `429` | Límite de peticiones superado |
| `502` | Fallo del proveedor de email por causas ajenas al usuario |

Los errores de validación se devuelven agrupados, no de uno en uno:

```json
{
  "errors": {
    "email": "El formato del correo no es válido.",
    "consent": "El consentimiento es obligatorio."
  }
}
```

**Cascada de barreras** (criterio *fail-fast*, de más barata a más cara):

```
1. Rate limiting        → 429
2. Body ausente/roto    → 400
3. Limpieza (strip)
4. Honeypot             → 200 (éxito falso, deliberado)
5. Validación de campos → 400 con detalle por campo
6. Envío al proveedor   → 200 / 400 / 502
```

**Política de rate limiting:** 5 peticiones por IP cada 60 segundos. Configurable en `services/antispam.py`.

---

## Decisiones de diseño

### El honeypot responde `200`

Un `4xx` le confirma al bot que fue detectado, y quien lo opera puede iterar hasta descubrir qué campo lo delata. Respondiendo `200` y descartando el mensaje en silencio, el bot cree que funcionó.

⚠️ **El mensaje de éxito real y el del honeypot deben ser idénticos byte a byte** — por eso viven en la constante `SUCCESS_MESSAGE`. Hay un test que lo verifica.

⚠️ **El campo trampa está oculto con `position: absolute; left: -9999px`, no con `display: none`.** Algunos bots comprueban `display:none` y saltan esos campos; sacarlo del viewport es más difícil de detectar. Como consecuencia, **el contenedor necesita `aria-hidden="true"`**: sin él, un lector de pantalla anunciaría el campo y un usuario ciego podría rellenarlo, provocando que su mensaje se descartara en silencio.

⚠️ **El nombre del campo (`HONEYPOT_FIELD` en `services/antispam.py`) debe coincidir exactamente** con el `name` del input del HTML. Si no coinciden, la trampa deja de funcionar sin dar ningún error.

### No confiar en cabeceras de IP salvo tras un proxy conocido

`X-Forwarded-For` **la puede falsificar el cliente**. Confiar en ella sin más permite saltarse el rate limiting enviando una IP distinta en cada petición. Por eso `get_client_ip` solo la lee cuando `TRUST_PROXY` está activo, y prioriza `CF-Connecting-IP` — que Cloudflare sobrescribe siempre y el cliente no puede falsear.

### Validación: acumula errores, no para en el primero

El *fail-fast* ordena las **barreras** (rechazar rápido al atacante). Dentro de la validación el destinatario es un humano, que merece ver sus dos fallos a la vez en lugar de descubrirlos por reenvíos sucesivos. Dos criterios opuestos conviviendo en el mismo endpoint, cada uno donde corresponde.

### Los campos de una línea rechazan saltos de línea

Un `<input type="text">` no puede producir un salto de línea: si llega uno, quien envía no está usando el formulario. **No se limpia, se rechaza** — no hay a quién ayudar.

Mitiga además que alguien falsifique la estructura del correo imitando las líneas `Etiqueta: valor`. `message` sí los permite (es un `<textarea>`), y por eso **el mensaje va al final del email, tras un separador**: al no haber campos propios después del contenido libre, no hay nada que imitar.

### La limpieza ocurre una sola vez, antes de todo

`clean_contact_data()` hace `strip()` a los valores de texto y se llama desde `routes.py` justo después de comprobar el body. A partir de ahí todos los consumidores trabajan con datos limpios: desaparecen los `strip()` repartidos por la validación, se valida exactamente el valor que acaba en el correo, y se cierra el hueco de *"95 espacios + 5 letras"* que pasaba el límite de longitud.

⚠️ *Consecuencia:* `is_bot` ya no hace `strip()` por su cuenta. Las dos cosas van juntas — hay un test que lo documenta para que nadie lo "arregle" por error.

### Rescate mínimo de solicitudes no entregadas

Si el proveedor de correo falla, la solicitud se registra en el log con el prefijo `SOLICITUD NO ENTREGADA` y sus datos en JSON, recuperable desde el panel de la plataforma de despliegue.

No es una *dead letter queue*: no hay reintento automático ni bandeja de fallidos. En un despliegue sin mantenimiento activo, una bandeja que nadie vacía es peor que no tenerla.

⚠️ *Consecuencia:* los datos del solicitante quedan en el log en caso de fallo. Es una excepción rara y deliberada, no un descuido.

### Correo en texto plano

No hay lenguaje que inyectar, así que el problema del contenido hostil desaparece de raíz. Es a la vez la opción más segura y la más simple.

### Origen y destino no se deciden desde el formulario

| Campo | Valor | Origen |
|---|---|---|
| `from` | remitente verificado | `MAIL_FROM` (fijo) |
| `to` | quien lee los mensajes | `MAIL_TO` (fijo) |
| `replyTo` | el visitante | formulario (variable) |

Si el destinatario dependiera del body, esto sería un **relay abierto**: cualquiera podría enviar correo a quien quisiera desde este backend.

---

## Tests

La suite cubre las tres capas del backend: lógica de negocio, adaptador de correo e integración del endpoint. **61 tests**, en menos de un segundo, sin salir a internet.

### Instalación

Las dependencias de desarrollo están separadas de las de producción. Desde `backend/`, con el entorno virtual activado:

```bash
pip install -r requirements-dev.txt
```

Ese fichero incluye `requirements.txt` mediante la directiva `-r`, así que instala todo lo necesario en un solo comando.

> ⚠️ **`pip freeze > requirements.txt` no debe usarse** en este proyecto: volcaría las dependencias de desarrollo al manifiesto de producción. Ambos ficheros se editan a mano.
>
> Y si alguna vez se usa: **comprobar antes que el prompt muestra `(venv)`**. Sin entorno virtual activo, `pip freeze` vuelca los paquetes globales de la máquina — un manifiesto con JupyterLab y sin Flask es el síntoma.

### Ejecución

```bash
pytest                          # ejecución normal
pytest --log-cli-level=INFO     # mostrando los logs en directo
pytest -v                       # nombre de cada test, uno por línea
pytest tests/test_routes.py     # un solo fichero
```

Todos los comandos se lanzan desde `backend/`.

**Sobre `--log-cli-level`:** por defecto pytest captura los logs y solo los muestra cuando un test falla. Esa opción los saca en directo, lo que resulta útil al depurar un test concreto y molesto como comportamiento por defecto.

### Estructura

```
backend/
├── conftest.py             # fixtures compartidas por todos los ficheros de test
└── tests/
    ├── test_validation.py  # campos, límites, saltos de línea, limpieza y contrato completo
    ├── test_antispam.py    # honeypot, rate limiting, purga y resolución de IP
    ├── test_mailer.py      # caminos de salida y payload (API externa mockeada)
    └── test_routes.py      # integración: la cascada de barreras traducida a códigos HTTP
```

**Los tests no salen a internet.** Las llamadas a la API de correo están mockeadas, así que la suite se ejecuta sin conexión, sin consumir cuota del proveedor y en menos de un segundo.

**`conftest.py`** aloja una fixture de limpieza que se aplica automáticamente a todos los tests. Es necesaria porque el rate limiter mantiene estado a nivel de módulo: sin ella, los tests se contaminarían entre sí y fallarían de forma dependiente del orden.

> **Principio aplicado en toda la suite:** una prueba que pasaría igual sin el código que prueba no prueba nada. Ante cada test, preguntarse *qué tendría que romperse para que fallara*.
>
> El caso que discrimina de verdad en este proyecto es **honeypot relleno junto a campos inválidos**: si devuelve `200`, el orden de barreras es correcto; si devuelve `400`, están intercambiadas.

---

## Integración con otro frontend

El backend es agnóstico del cliente. Para consumirlo desde otro proyecto:

1. Añadir el origen del nuevo frontend a `ALLOWED_ORIGINS`.
2. Enviar un `POST` a `/contact` con `Content-Type: application/json` y los campos de la tabla anterior.
3. **Incluir el campo trampa antispam.** El formulario debe contener un input adicional oculto por CSS y vacío, con `aria-hidden="true"` en su contenedor. El nombre exacto está en `HONEYPOT_FIELD` (`services/antispam.py`) y debe coincidir **exactamente** con el atributo `name` del input.
4. **Apuntar el frontend al backend.** Copiar `config.example.js` a `config.js` y ajustar `API_URL`.

`frontend/js/api.js` es reutilizable tal cual entre proyectos: no contiene configuración, solo la lógica de la petición.

> ⚠️ **Al adaptar el contrato de datos, recordar que se escribe dos veces:** en `services/validation.py` y en `frontend/js/validation.js`. Si divergen, el frontend aceptará algo que el backend rechaza, o al revés. Es deuda conocida, no un descuido.

---

## Notas de despliegue

> ⚠️ Revisar estos puntos antes de desplegar cualquier instancia en un proyecto real.

**Servidor de producción.** El servidor de desarrollo de Flask es de un solo hilo y no está pensado para producción. Usar **Gunicorn**:

```bash
gunicorn --workers 1 "app:create_app()"
```

Los paréntesis importan: indican que hay que **llamar** a la factory. Sin ellos, Gunicorn busca una variable llamada `create_app` y falla.

⚠️ **`--workers 1` no es arbitrario.** Cada worker es un proceso independiente con su propia memoria, y el contador del rate limiter vive en memoria: con N workers, el límite efectivo se multiplica por N.

**`FLASK_ENV=production`.** Sin él, la aplicación arranca en modo desarrollo con el depurador expuesto.

**Autenticación del dominio en el proveedor de email.** Sin DKIM configurado, los correos tienen alta probabilidad de acabar en spam o de no llegar en absoluto. **Es un requisito de entrega, no una mejora opcional.**

Con Brevo **no hace falta registro SPF**: el dominio del *Envelope From* lo gestionan sus servidores y nunca se alineará con el *From* visible. DMARC exige que DKIM **o** SPF estén autenticados y alineados — con DKIM correcto, DMARC pasa. Añadir el `include` de Brevo consumiría uno de los diez lookups DNS que permite el estándar sin aportar nada. *(Salvedad: si el dominio tiene además un servicio de correo, ahí sí habrá SPF y hay que no pisarlo.)*

**Detección de IP tras proxy.** Activar `TRUST_PROXY=true` **solo** si hay un proxy de confianza delante (Cloudflare con la nube naranja, por ejemplo). Ver *Decisiones de diseño*.

**Rate limiting.** El estado vive en memoria del proceso: no sobrevive a reinicios, no se comparte entre workers y **no es compatible con plataformas serverless**. Para despliegues con varios procesos, migrar el contador a Redis.

**CORS.** `ALLOWED_ORIGINS` debe restringirse al dominio del proyecto. CORS solo lo aplican los navegadores: no protege el endpoint frente a peticiones directas. La protección real la aportan el rate limiting, el filtro antispam y la validación en servidor.

**HTTPS en ambos extremos.** Si el frontend se sirve por HTTPS, el navegador **bloqueará las llamadas a un backend por HTTP** (*mixed content*), y lo hará sin error visible: la petición simplemente no sale.

**Titularidad de las cuentas.** En un modelo de entrega sin mantenimiento, la cuenta del proveedor de email y el dominio verificado deben estar a nombre del cliente. Si quedan a nombre del desarrollador, este sigue siendo el punto de fallo indefinidamente aunque no cobre.

---

## Pruebas manuales

La colección de Bruno está versionada en el repositorio. Configurar la URL base como `http://localhost:5001`.

| Caso | Esperado |
|---|---|
| Body válido | `200` + correo recibido |
| JSON malformado o ausente | `400` |
| Campos inválidos | `400` con detalle por campo |
| Salto de línea en `name` (vía `curl`) | `400` |
| Campo trampa relleno **junto a campos inválidos** | `200` (verifica el orden de las barreras) |
| 6 peticiones seguidas | La sexta devuelve `429` |
| `Origin` no autorizado | Respuesta sin cabecera `Access-Control-Allow-Origin` |

---

## Deuda técnica

### 🟡 Requieren atención si el proyecto crece

**1. El estado del rate limiter no se comparte ni sobrevive a reinicios.**
Mitigado con `--workers 1` y con la purga periódica de IPs caducadas. La solución estándar es **Redis**, que además expira las claves automáticamente y resuelve de paso el problema de los workers.

**2. Incompatible con serverless.**
En Vercel, Netlify o Cloudflare Workers el rate limiting dejaría de funcionar por completo: cada invocación puede ejecutarse en un contenedor nuevo sin memoria compartida. En ese escenario el contador **debe** vivir fuera del proceso.

**3. El contrato de datos está escrito dos veces.**
`services/validation.py` y `frontend/js/validation.js`. **Divergirá.** No tiene solución limpia sin un paso de build compartido.

**4. `_attempts` no es thread-safe.**
Con workers que usen hilos, dos peticiones simultáneas de la misma IP podrían leer y escribir el contador a la vez. Con `--workers 1` y worker síncrono no aplica.

**5. `routes.py` importa `Config` directamente** en vez de leer `current_app.config`. En tests eso significa la clase base, no `TestingConfig`. Hoy inofensivo; conviene limpiarlo antes de que algún test necesite configuración propia.

**6. `getElementById(campo)` sin comprobar existencia en `ui.js`.**
Devuelve `null` si el id no existe, y `null.textContent` revienta. Null-safety pendiente en el acceso al DOM.

### 🟢 Descartado conscientemente

**Dead letter queue completa.** Ver *Decisiones de diseño*.

**Email de confirmación al usuario.** Descartado por riesgo de *backscatter*: un bot que ponga la dirección de una víctima como remitente convertiría el backend en un cañón de spam contra terceros, y la factura la pagaría la reputación del dominio. Solo considerarlo con la capa antispam consolidada.

**Defensa contra la falsificación de estructura del correo.** Mitigada colocando el contenido libre al final del mensaje. Una solución completa (delimitadores infalsificables o cambio de formato) sería sobre-ingeniería mientras el destinatario sea un lector humano. **Revisar si el correo pasa a alimentar un CRM, un panel web o cualquier sistema que lo parsee.**

---

## Ramas

- `main` — estados estables y presentables
- `develop` — integración del trabajo en curso

---

## 🔵 Plan formativo (Módulo 3)

Ciclo completo pendiente de cerrar por primera vez:
tests → logging → config por entornos → **Docker** → **despliegue** → **CI**

- [x] `DEBUG = True` fijo en `config.py` → configuración por entorno
- [x] `CORS(app)` sin restringir orígenes → acotado a ruta, método y cabecera
- [x] `print(result["error"])` en `routes.py` → `logging`
- [x] Validación de email provisional → `email-validator`
- [x] Fuga de memoria en el rate limiter → purga periódica
- [x] `request.remote_addr` tras proxy → `get_client_ip` + `TRUST_PROXY`
- [x] Validación de la configuración al arrancar → `Config.validate()`
- [ ] `_attempts` no es thread-safe (workers con hilos)
- [ ] Contrato duplicado y divergente: `validation.js` ↔ `validation.py`
- [ ] `getElementById(campo)` sin comprobar existencia en `ui.js`
- [ ] Docker
- [ ] Despliegue
- [ ] CI