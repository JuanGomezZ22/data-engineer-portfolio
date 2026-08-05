# Docker — Referencia rápida para un Data Engineer

Guía de estructura y comandos que deberías poder reproducir de memoria (o casi) al trabajar con Docker en pipelines de datos.

---

## 1. Dockerfile — instrucciones esenciales

### Estructura base que casi siempre vas a repetir

```dockerfile
FROM python:3.12-slim          # 1. Imagen base
WORKDIR /app                    # 2. Carpeta de trabajo dentro del contenedor

COPY requirements.txt .         # 3. Copiar SOLO dependencias primero
RUN pip install --no-cache-dir -r requirements.txt   # 4. Instalar

COPY . .                        # 5. Copiar el resto del código

ENV PYTHONUNBUFFERED=1          # 6. Variables de entorno
EXPOSE 8080                     # 7. Puerto que el contenedor escuchara (documental)

CMD ["python", "main.py"]       # 8. Comando por defecto al arrancar
```

### Tabla de instrucciones que debes conocer de memoria

| Instrucción | Para qué sirve | Notas |
|---|---|---|
| `FROM` | Define la imagen base | Siempre la primera línea (o la primera de cada etapa en multi-stage) |
| `WORKDIR` | Crea y entra a una carpeta dentro del contenedor | Evita usar `cd` (no persiste entre instrucciones `RUN`) |
| `COPY` | Copia archivos de tu máquina a la imagen | Preferido sobre `ADD` salvo que necesites extraer `.tar` o descargar URLs |
| `ADD` | Como `COPY`, pero además extrae comprimidos y soporta URLs | Evítalo salvo esos casos específicos — su "magia" oculta genera confusión |
| `RUN` | Ejecuta un comando **durante el build** (una sola vez, se guarda en la imagen) | Cada `RUN` es una capa nueva |
| `CMD` | Comando por defecto al iniciar el contenedor | Se puede sobreescribir al hacer `docker run <imagen> otro-comando` |
| `ENTRYPOINT` | Como `CMD`, pero **no** se sobreescribe fácil — se le añaden argumentos en vez de reemplazarlo | Útil cuando el contenedor siempre debe ejecutar lo mismo (ej. una CLI) |
| `ENV` | Define variables de entorno visibles dentro del contenedor | No uses esto para secretos — se quedan visibles en `docker history` |
| `ARG` | Variable disponible **solo durante el build**, no en tiempo de ejecución | Útil para parametrizar versiones: `ARG PYTHON_VERSION=3.12` |
| `EXPOSE` | Documenta qué puerto usa la app | No abre el puerto por sí solo — eso lo hace `-p` en `docker run` |
| `USER` | Cambia el usuario que ejecuta el resto de instrucciones | Buena práctica: no correr como `root` en producción |
| `LABEL` | Metadata (versión, mantenedor, etc.) | Opcional, útil para organización en equipos grandes |
| `HEALTHCHECK` | Le dice a Docker cómo verificar si el contenedor sigue "sano" | Útil en Compose/Kubernetes para reinicios automáticos |

### Reglas de oro (por qué el orden importa)

1. **Lo que cambia menos, va primero.** `requirements.txt` cambia poco; tu código cambia todo el tiempo. Si inviertes el orden, invalidas el cache de `pip install` en cada build.
2. **Usa imágenes `-slim` o `-alpine`** salvo que necesites herramientas de compilación — reduce tamaño y superficie de ataque.
3. **Un `RUN` con `&&` en vez de varios `RUN`** cuando instalas paquetes del sistema, para no dejar capas intermedias pesadas:
   ```dockerfile
   RUN apt-get update && apt-get install -y --no-install-recommends \
       curl \
       && rm -rf /var/lib/apt/lists/*
   ```
4. **`--no-cache-dir` en `pip install`** — evita que pip guarde su propio caché dentro de la imagen (peso extra innecesario).

---

## 2. `.dockerignore` — estructura base

```
# Entornos virtuales y cachés de Python
venv/
venv-spark/
__pycache__/
*.pyc

# Control de versiones
.git/
.gitignore

# Datos (normalmente se montan como volumen, no se copian a la imagen)
data/

# Configuración local / secretos
.env
*.key
*-key.json

# Documentación y SQL (si no los necesita el runtime)
*.md
sql/

# Notebooks
*.ipynb
.ipynb_checkpoints/
```

**Regla mental:** todo lo que no necesite el programa para *ejecutarse* (no para desarrollarse) no debería entrar a la imagen.

---

## 3. Comandos de build y ejecución

### Construir una imagen

```bash
docker build -t nombre-imagen:tag .
# -t = tag (nombre:version). Si omites ":tag", Docker asume ":latest"

docker build -f Dockerfile.spark -t clima-spark:latest .
# -f = usar un Dockerfile con nombre distinto al default
```

### Ejecutar un contenedor

```bash
docker run --rm -v "$(pwd)/data:/app/data" nombre-imagen:tag
```

| Flag | Qué hace |
|---|---|
| `--rm` | Elimina el contenedor automáticamente al terminar |
| `-d` | Modo *detached* (segundo plano) |
| `-it` | Interactivo + terminal (para entrar a una shell dentro del contenedor) |
| `-v origen:destino` | Monta un volumen (bind mount o nombrado) |
| `-p host:contenedor` | Publica un puerto (ej. `-p 8080:8080`) |
| `-e VAR=valor` | Define una variable de entorno para esa ejecución |
| `--name algo` | Le da un nombre fijo al contenedor (en vez de uno aleatorio) |
| `--network red` | Conecta el contenedor a una red específica |

### Comandos de inspección y limpieza (los vas a usar seguido)

```bash
docker ps                    # Contenedores corriendo
docker ps -a                 # Todos los contenedores, incluidos detenidos
docker images                # Imágenes locales
docker logs <nombre>         # Ver logs de un contenedor
docker exec -it <nombre> bash  # Entrar a una shell dentro de un contenedor corriendo
docker stop <nombre>         # Detener
docker rm <nombre>           # Eliminar contenedor detenido
docker rmi <imagen>          # Eliminar imagen
docker system df             # Cuanto espacio ocupa Docker en tu disco
docker system prune -a       # Limpieza agresiva: elimina TODO lo no usado (cuidado)
```

---

## 4. `docker-compose.yml` — estructura base (sin base de datos real)

```yaml
version: "3.9"

services:
  mi-servicio:
    build: .                        # Construir desde Dockerfile local...
    # image: alguna-imagen:tag      # ...O usar una imagen ya publicada (uno u otro, no ambos)
    container_name: mi-contenedor
    volumes:
      - ./data:/app/data            # Bind mount: carpeta tuya <-> carpeta del contenedor
    environment:
      - VARIABLE_1=valor1
    env_file:
      - .env                        # Alternativa: cargar variables desde un archivo
    ports:
      - "8080:8080"
    depends_on:
      - otro-servicio
    networks:
      - mi-red
    restart: unless-stopped         # Reinicia solo si no lo detuviste tú manualmente

  otro-servicio:
    image: redis:7-alpine
    networks:
      - mi-red

networks:
  mi-red:
    driver: bridge

volumes:
  mi-volumen-nombrado:
```

### Comandos de Compose

```bash
docker compose up              # Levanta todo (sigue mostrando logs en la terminal)
docker compose up -d           # Levanta todo en segundo plano
docker compose up --build      # Fuerza reconstruir imágenes antes de levantar
docker compose down            # Detiene y elimina contenedores + red (NO volúmenes nombrados)
docker compose down -v         # Igual, pero también elimina volúmenes nombrados
docker compose ps              # Estado de los servicios
docker compose logs -f mi-servicio   # Logs en vivo de un servicio especifico
docker compose exec mi-servicio bash # Entrar a una shell de un servicio corriendo
```

---

## 5. Multi-stage builds — cuándo usarlos y más ejemplos

### La pregunta que te debes hacer siempre

> ¿Necesito herramientas pesadas (compiladores, SDKs, dependencias de build) **solo para construir/compilar algo**, pero **no para ejecutarlo** después?

Si la respuesta es sí → multi-stage build. El patrón general siempre es:

```dockerfile
FROM <imagen-pesada-con-herramientas> AS builder
# ... instalar herramientas, compilar, construir ...

FROM <imagen-liviana-de-runtime>
COPY --from=builder <solo-lo-que-necesitas> <destino>
# ... comando final ...
```

### Ejemplo A — el que ya hicimos: PySpark (Python + JVM)

- **Problema:** necesitas `build-essential` para compilar algunas dependencias Python, y necesitas Java, pero no necesitas el compilador de Java (`javac`).
- **Builder:** `python:3.11-slim` + `build-essential` + crea un `venv` con `pip install`.
- **Runtime:** `python:3.11-slim` + `default-jre-headless` (NO el JDK completo) + copia solo el `venv` ya armado.

### Ejemplo B — una librería con extensión en C: `psycopg2` (driver de PostgreSQL)

`psycopg2` (no la versión `-binary`) necesita compilarse contra `libpq-dev` (las cabeceras de desarrollo de PostgreSQL). Pero en producción, tu script solo necesita la **librería en tiempo de ejecución** (`libpq5`), no las cabeceras de desarrollo completas.

```dockerfile
# ---------- Builder ----------
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt   # aqui se compila psycopg2

# ---------- Runtime ----------
FROM python:3.12-slim

# Solo la libreria de runtime, NO libpq-dev (that trae headers/compilador de mas)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app
COPY . .
CMD ["python", "main.py"]
```

### Ejemplo C — un proyecto dbt (muy relevante para Data Engineering)

`dbt-core` + adaptadores (ej. `dbt-bigquery`) traen bastantes dependencias transitivas. El patrón es el mismo: compilas/instalas todo en una etapa, y en runtime solo necesitas el intérprete de Python con el entorno ya armado — no necesitas herramientas de compilación para *ejecutar* `dbt run`.

```dockerfile
FROM python:3.12-slim AS builder
RUN apt-get update && apt-get install -y --no-install-recommends git build-essential \
    && rm -rf /var/lib/apt/lists/*
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir dbt-core dbt-bigquery

FROM python:3.12-slim
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /app
COPY . .
CMD ["dbt", "run"]
```

### Ejemplo D — fuera del mundo Python: frontend (React/Vue) servido por Nginx

Este es el ejemplo clásico que verás en cualquier equipo con frontend, y ayuda a ver que el patrón **no es exclusivo de Python**:

```dockerfile
# ---------- Builder: necesita Node.js completo para compilar ----------
FROM node:20-slim AS builder
WORKDIR /app
COPY package*.json .
RUN npm install
COPY . .
RUN npm run build          # genera archivos estaticos en /app/dist

# ---------- Runtime: solo un servidor web liviano, sin Node.js ----------
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Node.js (pesado, con todo el tooling de build) **desaparece por completo** de la imagen final — la imagen de producción es solo Nginx sirviendo archivos estáticos.

### Regla general para decidir el número de etapas

| Situación | ¿Multi-stage? |
|---|---|
| Solo instalas paquetes puros de Python (`pandas`, `requests`) vía `pip` | No hace falta, no hay nada que "compilar y descartar" |
| Instalas algo que requiere `build-essential`, `gcc`, `libpq-dev`, etc. | Sí — la etapa de compilación no debe llegar a producción |
| Compilas código (Go, Rust, Node, Java con Maven/Gradle) | Sí — casi siempre el compilador no se necesita en runtime |
| Necesitas Java/JVM para ejecutar algo (Spark, Kafka clients) | Considera si necesitas JDK completo o solo JRE headless |

---

## Resumen mental de una línea por sección

- **Dockerfile:** copia dependencias antes que código, usa imágenes slim, evita `root` en producción.
- **`.dockerignore`:** todo lo que no necesita el runtime, fuera.
- **Comandos:** `build` → `run` → `ps`/`logs` para verificar → `stop`/`rm` para limpiar.
- **Compose:** un archivo `.yml` reemplaza comandos `docker run` largos y coordina varios contenedores con una red compartida.
- **Multi-stage:** compila/instala en una etapa pesada, copia solo el resultado a una etapa liviana final.
