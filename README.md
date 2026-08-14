# 📚 GUIDE.md — Conceptos de referencia

> **Qué es este documento:** glosario didáctico de los conceptos nuevos que van surgiendo en el proyecto. La bitácora registra *qué se decidió y por qué*; esto explica *qué significan las palabras*. Consulta rápida, sin orden cronológico.

**Índice**

- [1. Arquitectura y despliegue](#1-arquitectura-y-despliegue)
- [2. Seguridad y antispam](#2-seguridad-y-antispam)
- [3. Validación y contrato de datos](#3-validación-y-contrato-de-datos)
- [4. Errores y respuestas HTTP](#4-errores-y-respuestas-http)
- [5. Criterios de diseño transversales](#5-criterios-de-diseño-transversales)

---

## 1. Arquitectura y despliegue

### Stateless (sin estado)

El servidor **no recuerda nada entre una petición y la siguiente**. Cada POST llega huérfano: sin sesión, sin memoria de quién eres ni de qué hiciste hace un minuto.

*Consecuencia práctica:* no existe el "límite por sesión". Si quieres contar peticiones, tienes que elegir un campo por el que agruparlas (típicamente la IP) y guardar ese contador **en algún sitio que sobreviva a la petición**.

### Serverless vs. PaaS

Dos formas distintas de que tu código viva en internet, y **no son intercambiables**.

| | **Serverless** (Vercel, Netlify, Cloudflare Workers) | **PaaS** (Render, Railway) |
|---|---|---|
| Qué es | Una función que se despierta al recibir una petición y muere al terminar | Un proceso que corre 24/7 esperando peticiones |
| Estado en memoria | **No sobrevive** entre invocaciones | Persiste mientras el proceso viva |
| Coste | Por invocación (free tier real para bajo volumen) | Por tiempo de proceso; los free tier duermen tras inactividad |
| Ideal para | Endpoints puntuales y sin estado: formularios, webhooks | Apps completas, tareas de fondo, conexiones persistentes |

**El error clásico:** escribir un rate limiter guardando IPs en un diccionario del proceso. Funciona perfecto en local con Flask y **se rompe en serverless**, porque cada invocación puede ejecutarse en un contenedor nuevo y vacío. Si el destino puede ser serverless, el estado va fuera del proceso (Redis, base de datos, KV store).

### Multi-tenancy

Que **un mismo despliegue sirva a varios clientes distintos**.

Suena eficiente y es la trampa favorita de los proyectos pequeños. En cuanto un solo endpoint atiende a tres webs, tienes que responder tres preguntas que antes eran triviales: *¿quién me llama?*, *¿a qué correo va este email concreto?*, *¿tiene permiso?*. Eso significa identificar al cliente en la petición, guardar configuración por cliente y validar credenciales. En un despliegue por proyecto, todo eso son tres variables de entorno y se acabó.

**Regla:** la multi-tenancy se paga en complejidad. Solo compensa si de verdad vas a operar un servicio.

### Handover vs. servicio mantenido

No es una categoría técnica, es de **modelo de negocio** — y decide la arquitectura antes que cualquier criterio técnico.

- **Handover:** entregas el software y te vas. El cliente debe quedar **autónomo**: cuentas de terceros, dominio e infraestructura **a su nombre**. Si algo queda a tu nombre, sigues siendo el punto de fallo indefinidamente aunque no cobres.
- **Servicio mantenido:** operas tú, cobras recurrente, asumes disponibilidad.

Asumir responsabilidad operativa de un servicio que no genera ingresos es un error de gestión, no de código.

### Desacoplar la lógica del framework

Escribir la lógica de negocio (validar, filtrar, enviar) como **funciones puras** que no sepan nada de Flask, de `request`, ni de handlers serverless.

La capa de entrada queda entonces como un envoltorio de diez líneas: recoge el body, llama a tus funciones, devuelve la respuesta. Cambiar de plataforma pasa a ser reescribir ese envoltorio, no el proyecto.

*Ya lo aplicaste en allergen-manager con `extensions.py`:* aislar lo que depende del entorno para que el resto no lo herede.

---

## 2. Seguridad y antispam

> **La idea de fondo:** el 95% de esto no es hacking, es **desconfiar de todo lo que llega de fuera**. Tu API recibe datos de desconocidos; trata cada campo como hostil hasta demostrar lo contrario.

### CORS no es seguridad

Concepto mal entendido casi universalmente. CORS **solo lo respetan los navegadores**. Un `curl` desde cualquier terminal ignora tu whitelist de orígenes por completo.

**Para qué sirve:** evitar que otra web use tu endpoint desde el navegador de un usuario.
**Para qué NO sirve:** proteger tu endpoint. Si es público, la protección real viene de otro sitio: secreto compartido, rate limiting, honeypot, validación estricta.

### Rate limiting

Limitar **cuántas** peticiones acepta el servidor de un mismo origen en una ventana de tiempo.

- Se agrupa por un campo identificador — normalmente la IP, con la grieta conocida de que varias personas tras el mismo router la comparten.
- **Ventana temporal, no bloqueo permanente:** X peticiones en Y minutos → cerrado un rato. Los bloqueos permanentes causan daño colateral (tras una IP puede haber una oficina entera).
- Contra ataques serios, un bot rota IPs y tu código no gana. Esa defensa corresponde a la capa de red (Cloudflare y similares), que lo hace infinitamente mejor.
- Va **primero** en la cadena de barreras: es la comprobación más barata y la que más descarta.

### Honeypot

Un **campo extra oculto por CSS** que un humano nunca ve ni rellena, pero que los bots — que leen el HTML en crudo y rellenan todo lo que encuentran — completan con entusiasmo. ¿Viene relleno? Es un bot.

Coste cero, sin captchas, sin fricción para el usuario. La técnica antispam con mejor relación beneficio/coste que existe.

**El detalle contraintuitivo:** al detectarlo, **responde `200` como si todo hubiera ido bien** y descarta el mensaje en silencio. Si devuelves un 4xx le confirmas al bot que fue detectado, y quien lo opera puede iterar hasta descubrir qué campo lo delata. *En seguridad, el silencio informa menos al atacante que el error.*

### Backscatter

Convertir tu backend, sin querer, en **un cañón de spam apuntando a terceros**.

*El escenario:* añades un email de confirmación al usuario. Un bot rellena el formulario poniendo `victima@ejemplo.com` como remitente. Tu servidor, obediente, le manda un email a esa víctima. Mil veces.

La factura la paga la **reputación de tu dominio**: acabas en listas negras y los emails legítimos del cliente empiezan a caer en spam. La funcionalidad es valiosa, pero se activa **después** de tener antispam sólido, nunca antes.

### Deliverability

Que tus emails lleguen a la bandeja de entrada y no a spam. Depende de configurar el dominio del remitente con **SPF y DKIM** (registros DNS que acreditan que tienes permiso para enviar en nombre de ese dominio).

Es la ventaja silenciosa de usar una API transaccional con dominio verificado frente a enviar desde una cuenta de Gmail personal.

---

## 3. Validación y contrato de datos

### El front es usabilidad; el back es seguridad

El `maxlength` del HTML lo aplica el navegador — **y el navegador es del atacante**. Un `curl` manda 5 MB en el campo mensaje sin despeinarse.

**Regla sin excepciones:** todo lo que valides en el front, revalídalo en el servidor. La validación del front existe para que el usuario legítimo no pierda el tiempo, no para protegerte.

### Si no haces aritmética con ello, no es un número

Un teléfono guardado como `int` se rompe con prefijos (`+34`), ceros iniciales, espacios y guiones. Igual pasa con códigos postales, DNI o números de factura. **Son strings.**

### Validar emails

Comprobar que hay un `@` no es validar: `a@b` lo cumple y no existe. Usa una librería especializada — escribir tu propia expresión regular para emails es un clásico camino al sufrimiento, porque el formato real es mucho más raro de lo que parece.

### Consentimiento RGPD

Si el cliente es europeo, la casilla de política de privacidad **no es decoración: es requisito legal**. Y debe ser **explícito**: casilla desmarcada por defecto, nunca premarcada.

Por ser requisito legal, se valida en el servidor como cualquier otro campo obligatorio: sin `true`, no hay envío.

---

## 4. Errores y respuestas HTTP

### Códigos usados en este proyecto

| Código | Significado | Cuándo |
|---|---|---|
| `200` | OK | Envío correcto — **y también al detectar el honeypot** (éxito falso) |
| `400` | Bad Request | Validación fallida; indica qué campo |
| `429` | Too Many Requests | Rate limiting. Código específico, mejor que un 4xx genérico |
| `500` | Internal Server Error | Fallo genérico del servidor |
| `502` / `503` | Bad Gateway / Service Unavailable | **Falló un servicio externo** (la API de email). Más preciso que un 500 |

**La distinción que importa:** `4xx` = culpa del cliente, reintentar igual no sirve. `5xx` = culpa del servidor, reintentar tiene sentido. Ese matiz es lo que le dice al front si ofrecer o no un "vuelve a intentarlo".

### Dead letter queue

La "bandeja de lo no entregado": persistir las peticiones que fallaron para poder recuperarlas o reprocesarlas.

Concepto potente en sistemas serios, **descartado aquí conscientemente**: en un handover, una bandeja que nadie va a revisar jamás es peor que no tenerla.

### Nunca uses el canal roto para avisar de que está roto

Si lo que ha fallado es el envío de email, mandar el log del error por email no sirve de nada. Obvio al enunciarlo, sorprendentemente común en el código real.

---

## 5. Criterios de diseño transversales

### Fail fast

**Rechaza lo antes posible, y ordena las comprobaciones de más barata a más cara.**

Rechazar en la puerta cuesta microsegundos; llamar a la API de email cuesta cientos de milisegundos y consume cuota. Es el criterio que ordena toda la cadena de barreras:

```
1. Rate limiting  →  contador, sin tocar el contenido      (baratísimo)
2. Honeypot       →  una comprobación                       (barato)
3. Validación     →  parsear y recorrer todo el body        (medio)
4. Envío email    →  llamada de red a un tercero            (caro)
```

*El portero filtra en la puerta, no cuando el cliente ya se ha sentado en la mesa.*

### Patrón Adapter *(pendiente — para el servidor de notificaciones)*

Cuando el mismo servicio deba enviar por email, WhatsApp, SMS o Telegram, la lógica de negocio no debe saber cuál se está usando. Se define una interfaz común (`enviar(mensaje, destino)`) y cada canal implementa su propia versión detrás.

Es la misma idea de "desacoplar del framework", aplicada a los canales de salida. Se desarrollará cuando llegue ese proyecto.

---

*Documento vivo: cada concepto nuevo que surja se añade en su sección correspondiente.*

---

## 6. Conceptos clave ⭐

> Conceptos que se repiten constantemente en el trabajo diario y conviene tener asentados.

### ⭐ Firma de una función

**El contrato de una función: su nombre, qué parámetros recibe y qué devuelve.** Es la parte que ve quien la usa, ignorando cómo está hecha por dentro.

```python
def send_email(data, config):   # ← la firma
    # ...todo lo de aquí dentro es la implementación
```

De `send_email` se sabe que recibe dos cosas y devuelve un diccionario con `success`, `error` y `status_code`. Con eso basta para usarla sin leer una línea de su cuerpo.

**La utilidad real:** si mañana se cambia Brevo por Resend, la implementación cambia entera y **la firma se mantiene** — quien la llama no se entera. Ese es el mecanismo que hace posible el patrón Adapter.

**Por eso se define la firma antes de escribir el cuerpo:** es decidir el contrato antes que los detalles. Al revés se acaba con funciones que devuelven lo que salió, no lo que hacía falta.

*Sinónimo habitual: **interfaz**.*

> **Regla derivada:** si la firma promete un objeto, **todos** los caminos de la función deben devolver uno — incluido el `catch` o el `except`. Una rama que se va de vacío devuelve `undefined` (JS) o `None` (Python), y convierte un error controlado en un crash en quien la llamó.

### ⭐ "Pintar" en el DOM

**Modificar el DOM: cambiar lo que el usuario ve sin recargar la página.** Ni `alert`, ni consola, ni refresh.

```javascript
document.getElementById("error-email").textContent = "El formato no es válido";
```

En React se hacía con estado: cambiabas `useState` y el framework repintaba solo. **En vanilla el repintado es responsabilidad propia** — nadie observa cambios de estado por ti. Esa es la diferencia de fondo entre ambos mundos, no la sintaxis.

### ⭐ Inyección de dependencias

**Que un módulo reciba lo que necesita como argumento en vez de buscarlo por su cuenta.**

```python
def send_email(data, config):    # recibe la configuración
    ...
```

frente a que `send_email` importe `Config` internamente. La clave no es la seguridad —el valor vive en el mismo proceso en ambos casos— sino el **acoplamiento y la testabilidad**: si el módulo no busca su configuración, no depende de dónde esté. Para probarlo basta pasarle una clase falsa de tres líneas.

Ya estaba aplicado sin nombrarlo en `is_rate_limited(ip)`, que recibe una IP en vez de leer `request`. Es lo que mantiene `services/` libre de Flask.

### ⭐ Fail fast

**Rechazar lo antes posible, ordenando las comprobaciones de más barata a más cara.**

Es el criterio que ordena la cadena de barreras del proyecto, y también el que ordena las *guard clauses* dentro de una función.

⚠️ **Tiene una excepción deliberada:** no aplica cuando el destinatario del error es un humano. La validación **acumula** todos los errores en vez de parar en el primero, porque quien rellena un formulario merece ver sus dos fallos a la vez. *El criterio depende de quién lee la respuesta.*


---

## 7. Frontend sin framework (vanilla JS)

> Sección nacida del salto desde React. Lo que cambia no es la sintaxis: es quién se encarga de las cosas.

### El routing es el sistema de ficheros

En React había **una** página HTML y el router intercambiaba componentes simulando navegación. En una web estática, el navegador pide una URL y el hosting devuelve ese fichero: `index.html`, `contacto.html`. **No hay router que escribir porque el servidor ya es el router.**

### `fetch` no es de React

Es API nativa del navegador; React solo la usaba. Lo que desaparece no es `fetch`, es el envoltorio: sin `useState` ni `useEffect`, solo un `addEventListener` que llama a `fetch` y actualiza el DOM cuando responde.

### `e.preventDefault()`

Un `<form>` tiene comportamiento nativo: al enviarlo, **el navegador recarga la página**. React lo tapaba; en vanilla se cancela a mano, y va **lo primero** dentro del listener. Sin él: la página parpadea, el formulario se vacía y la petición no llega a completarse.

*Síntoma inconfundible de que no se ejecutó: la URL se llena de query string (`?name=&email=`).*

### Módulos ES en el navegador

```html
<script type="module" src="js/main.js"></script>
```

Tres reglas que el bundler tapaba:

1. **`type="module"` es obligatorio** o los `import` lanzan error de sintaxis. Solo se carga el fichero de entrada; el navegador sigue la cadena de imports solo.
2. **La extensión `.js` y el `./` son obligatorios**: `from './api.js'`, no `from './api'`. Sin el `./`, el navegador buscaría un paquete.
3. ⚠️ **No funcionan con doble clic** (protocolo `file://`): hay que servir por HTTP (Live Server).

> **Un error en un módulo lo tumba entero.** No hay ejecución parcial: si el import falla, nada de ese fichero corre. Y el síntoma engaña — la página parece bien, pero "no pasa nada" al pulsar. Primera parada: la consola.

### Separar por responsabilidad, no por componente

```
main.js         # orquesta: escucha eventos
api.js          # habla con el backend
validation.js   # reglas de negocio
ui.js           # toca el DOM
```

`main.js` importa de los demás; **los demás no se importan entre sí**. Es el mismo reparto que en el backend: `api.js` y `validation.js` son el `services/` (datos entran, datos salen, sin tocar pantalla), `ui.js` es la presentación, `main.js` es el `routes.py`.

**Los manejadores de eventos son el final de la cadena, no un eslabón.** Al listener lo llama el navegador, que no hace nada con el valor devuelto: `main.js` no devuelve nada porque nadie lo llama.

### Trampas de JavaScript viniendo de Python

| Python | JavaScript |
|---|---|
| `data.get('x')` lanza `KeyError` con `[]` | `data.x` devuelve `undefined`, no lanza |
| `.strip()` | `.trim()` |
| `if errors:` → dict vacío es **falso** | ⚠️ `{}` es **VERDADERO**: usar `Object.keys(errors).length > 0` |
| `x or 'defecto'` | `x \|\| 'defecto'` (idéntico) — y `??` solo cubre `null`/`undefined` |

**`querySelectorAll` no devuelve un array**, sino una `NodeList`: tiene `forEach`, pero no `map`, `filter` ni `reduce`. Para eso, `Array.from(...)` o `[...]`.

**`form.name` es ambiguo:** los formularios exponen sus campos como propiedades, pero `name` (y `method`, `action`, `target`, `id`) son propiedades nativas del elemento. Usar `form.elements.name` evita la colisión.

### El patrón de nomenclatura que ahorra código

Con `id="<campo>"` en el input e `id="error-<campo>"` en su contenedor de error, pintar todos los errores es un bucle:

```javascript
for (const campo in errors) {
    document.getElementById("error-" + campo).textContent = errors[campo];
    document.getElementById(campo).classList.add("is-invalid");
}
```

Se añade un campo al formulario y **sigue funcionando sin tocar el JS**.

### `alert()` no es una solución de UI

Bloquea la página, no se puede estilar, es distinto en cada navegador y **desaparece al aceptar** — el usuario no puede leerlo mientras corrige. Peor que los globos nativos, no mejor.

### Validación nativa vs. propia

Los atributos `required` bloquean el envío **antes** de que el listener se ejecute. Dejarlos implica: estilo del navegador, **idioma del sistema operativo del usuario** (mensajes en inglés en una web en español) y **solo el primer campo fallido**.

Con `novalidate` en el `<form>` se recupera el control: mensaje, idioma, estilo y todos los fallos a la vez. **Los `required` se dejan puestos igualmente** — siguen documentando el contrato.

⚠️ **La validación en el front es USABILIDAD, no seguridad.** Un `curl` la ignora. Su valor es ahorrarle al usuario legítimo un viaje de ida y vuelta.

### No muevas al usuario de sitio sin que lo pida

Las redirecciones automáticas tras enviar un formulario rompen la sensación de control y suelen inutilizar el botón "atrás". Si el formulario ya se ha limpiado, no hace falta nada más.

---

## 8. Configuración y entornos

### Las variables de entorno siempre son strings

No existen listas, números ni booleanos: **todo lo que devuelve `os.getenv()` es texto**.

*Trampa clásica:* `DEBUG=False` en un `.env` es la cadena `"False"`, que en Python es **verdadera**. Ha roto muchos despliegues.

Para guardar una lista, la convención es un separador y partirla en el código:

```
ALLOWED_ORIGINS=http://127.0.0.1:5500,http://localhost:5500
```
```python
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")
```

**Sin espacios tras las comas** o llegarían dentro de los valores. Y valor por defecto en el `getenv` para no hacer `.split()` sobre `None`.

### En el frontend no hay `.env`

Sin bundler no hay proceso de build que sustituya variables. Y aunque lo hubiera, **todo lo que llega al navegador es público**: un `.env` de front no es un secreto, solo una comodidad.

La configuración que el front necesita (URLs de API, claves públicas) se pone donde cada despliegue ya toca de todos modos: **el HTML**, mediante `data-attributes`.

```html
<body data-api-url="http://localhost:5001/contact">
```
```javascript
const API_URL = document.body.dataset.apiUrl;
```

> **Conversión de nombres:** el prefijo `data-` desaparece y el kebab-case pasa a camelCase. `data-api-url` → `dataset.apiUrl`. Escribir `dataset.apiurl` devuelve `undefined`.

**La ventaja de fondo:** el módulo que consume la configuración queda libre de ella y se puede copiar tal cual entre proyectos.

### El orden en una Application Factory

**Configurar → inicializar extensiones → registrar blueprints.** Cada paso puede depender del anterior: una extensión que lea `app.config` antes del `from_object` recibirá un diccionario vacío, sin dar error, y caerá a su comportamiento por defecto.

---

## 9. CORS, en concreto

### Qué es exactamente

**Una política que aplica el navegador sobre sí mismo.** El servidor solo envía cabeceras diciendo "acepto estos orígenes"; es el navegador quien decide obedecerlas y bloquear la respuesta antes de entregársela al JavaScript de la página.

Consecuencia comprobada en el proyecto: un `curl` con datos válidos atraviesa cualquier whitelist y **envía el correo igualmente**. Ni `curl`, ni Postman, ni Bruno, ni un script, ni un bot tienen concepto de "origen".

**CORS no impide que la petición llegue: solo decide si el navegador puede leer la respuesta.**

### El origen debe coincidir exactamente

Protocolo, host y puerto. Todos estos son orígenes **distintos**:

- `http://localhost:5500`
- `http://127.0.0.1:5500`
- `https://localhost:5500`

En desarrollo conviene incluir las variantes que se usen realmente.

### Cómo verificar que la restricción funciona

Con `curl -i`, comparando dos peticiones:

```bash
curl -i -X POST URL -H "Origin: https://sitio-no-autorizado.com"
curl -i -X POST URL -H "Origin: http://origen-permitido.com"
```

En la primera, la cabecera `Access-Control-Allow-Origin` **debe estar ausente**. En la segunda, presente y acompañada de `Vary: Origin`.

⚠️ **Un `Access-Control-Allow-Origin: *` en la respuesta significa que la whitelist NO se está aplicando.**

### Mixed content

Un navegador **bloquea llamadas HTTP desde una página HTTPS**, y lo hace sin error visible: la petición simplemente no sale. Si el front va por HTTPS, el backend también debe ir por HTTPS.

---

## 10. Método de prueba

### Una prueba que pasaría igual sin el código que prueba no prueba nada

Apareció **dos veces** en este proyecto:

- **Honeypot:** probarlo con todos los campos válidos no demuestra nada — habría dado `200` de todos modos. El caso discriminante es honeypot relleno **junto a campos inválidos**.
- **CORS:** la petición del navegador seguía funcionando con la whitelist mal configurada, porque ese origen estaba permitido en ambos casos. Lo que discriminaba era la cabecera de la respuesta.

**La pregunta a hacerse siempre:** *¿este caso daría un resultado distinto si quito la pieza que quiero comprobar?* Si la respuesta es no, hay que diseñar otro caso.

**Y el corolario:** probar el camino feliz no es probar. Hay que verificar también que **rechaza** lo que debe rechazar.

### Convertir una excepción en un dato

Muchas librerías se comunican lanzando excepciones. Adaptarlas a la forma de trabajar del proyecto es parte del oficio:

```python
try:
    validate_email(email, check_deliverability=False)
except EmailNotValidError:
    errors['email'] = 'El formato del correo no es válido.'
```

El `except` no interrumpe la función: captura, apunta el error y **la ejecución continúa**. La firma no cambia.

> **Capturar siempre lo más específico posible.** Un `except:` a secas atraparía también los errores de programación propios, enmascarados como fallo de validación.

### Nombre del paquete ≠ nombre del módulo

Se instala `email-validator` (guion) y se importa `email_validator` (guion bajo). PyPI admite guiones en los nombres; los módulos de Python no. Provoca un `ModuleNotFoundError` desconcertante al copiar el nombre de la instalación al import.