# Fase 5 — Herramientas / vibe coder

## Resumen

En esta fase se trabaja el uso de herramientas modernas de desarrollo asistido por IA (vibe coding): asistentes de código, flujos de trabajo con IA, prompting efectivo y buenas prácticas al programar con estas herramientas.

## Checklist de conceptos clave

- [ ] (pendiente de definir)

## Conceptos clave

### Control de versiones con Git/GitHub
Ya practicado extensamente: ramas de feature, pull requests, merges, y 
resolución de un problema real de configuración (rama "default" mal 
establecida en el repo, corregida en fase-1-backend). El porqué de fondo — 
por qué no se trabaja directo sobre main en un proyecto real — se vivió de 
primera mano: cada PR dio la oportunidad de revisar un diff antes de 
integrarlo, separando "trabajo en progreso" de "lo que ya funciona y está 
validado".

### Docker
También practicado en profundidad: contenedor ccms-postgres, pgAdmin, y 
resolución de un problema real de red entre contenedores 
(host.docker.internal). El concepto de fondo — "funciona en mi máquina" deja 
de ser un problema — se confirmó al comprobar que el backend habla igual con 
PostgreSQL esté donde esté corriendo (nativo o en Docker), porque el 
contenedor aísla el entorno.

### Variables de entorno y gestión de secretos
Contenido nuevo a resolver en el ejercicio práctico: actualmente database.py 
tiene la contraseña de PostgreSQL escrita directamente en el código 
(hardcodeada) — se corrige moviendo las credenciales a un archivo separado 
que nunca se sube a Git.

### Testing básico
Contenido completamente nuevo. Un test unitario es código que verifica 
automáticamente que otro código hace lo que se espera, sin probarlo a mano 
cada vez (a diferencia de las pruebas manuales hechas hasta ahora vía 
Swagger UI o curl). Un CCMS con lógica de workflow (estados, permisos, 
versionado) los necesita porque un cambio pequeño en un sitio puede romper 
una regla de negocio en otro sin que se note a simple vista.

### CI/CD (nivel conceptual, con práctica ligera)
"Desplegar automáticamente" significa que, al subir código a main, un 
sistema externo (no manualmente) ejecuta pasos predefinidos — típicamente: 
correr los tests, y si pasan, desplegar la nueva versión. Reduce errores 
humanos porque elimina el paso "me acordé de probarlo antes de subirlo" — el 
sistema lo hace siempre, sin excepción.

#### Aclaración: qué significan CI y CD exactamente

**CI = Continuous Integration (Integración Continua).** Cada vez que se sube 
código (vía PR o push), un sistema automático construye e integra ese código 
con el resto del proyecto, y ejecuta comprobaciones (tests, linters) para 
detectar problemas cuanto antes — antes de que ese código se mezcle de 
verdad con el trabajo de los demás. En vez de integrar todo el trabajo de 
golpe tras semanas aisladas (con conflictos masivos), se integra 
constantemente, en piezas pequeñas, detectando roturas al momento.

**CD tiene dos significados distintos:**
- **Continuous Delivery (Entrega Continua)**: el código, tras pasar todos 
  los checks automáticos, queda listo para desplegarse en cualquier 
  momento — pero el despliegue final a producción sigue siendo una decisión 
  humana.
- **Continuous Deployment (Despliegue Continuo)**: un paso más allá — si 
  todo pasa los checks automáticos, se despliega a producción sin 
  intervención humana.

**Alcance de este ejercicio**: se implementa solo la parte de CI (ejecutar 
tests automáticamente en cada push) — la parte de CD no aplica todavía 
porque no existe ningún servidor de producción desplegado, solo el entorno 
local. Es un matiz importante: "CI/CD" se suele decir como una sola cosa, 
pero en este proyecto, por ahora, solo se implementa la mitad (CI).

## Ejercicio

### Variables de entorno: sacar las credenciales de PostgreSQL del código

Primer paso práctico de esta fase: corregir que `api/database.py` tuviera 
las credenciales de PostgreSQL escritas directamente en el código.

**Antes:**
```python
DATABASE_URL = "postgresql+psycopg2://postgres:curso123@localhost:5432/ccms"
```
La contraseña real (`curso123`) quedaba visible en el código fuente, y por 
tanto en el historial de Git en cuanto se hiciera commit — cualquiera con 
acceso al repositorio (o a una copia pública de él) vería la contraseña de 
la base de datos.

**Después:**
```python
load_dotenv()

POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")

DATABASE_URL = (
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)
```
Las credenciales ahora viven en un archivo `.env` (fuera de Git), leído en 
tiempo de ejecución con `python-dotenv`. El código ya no contiene ningún 
valor real — solo los nombres de las variables que necesita.

### Por qué `.env` nunca debe subirse a Git, pero `.env.example` sí

- **`.env`**: contiene las credenciales reales (usuario, contraseña, host, 
  puerto, nombre de la base de datos) del entorno de quien lo creó. Si se 
  sube a Git, esas credenciales quedan expuestas para siempre en el 
  historial del repositorio, aunque después se borre el archivo — un 
  `git log`/`git show` de un commit antiguo las seguiría mostrando. Por eso 
  se añade a `.gitignore`: Git lo ignora por completo, nunca llega a 
  proponerse en un commit.
- **`.env.example`**: contiene los mismos nombres de variable, pero con 
  valores de ejemplo genéricos (`tu_usuario`, `tu_password`...), sin ningún 
  dato real. Este archivo sí se sube a Git, precisamente para que cualquiera 
  que clone el repositorio sepa qué variables de entorno necesita crear en 
  su propio `.env` local, sin exponer las credenciales de nadie.

### Verificación

Se instaló `python-dotenv`, se creó `api/.env` con las credenciales reales, 
se creó `api/.env.example` con valores de ejemplo, y se añadió `api/.gitignore` 
con la entrada `.env`. Se levantó el servidor (`uvicorn main:app`) y se 
comprobó que sigue conectando correctamente a PostgreSQL y sirviendo 
`/topics` con datos reales, exactamente igual que antes del cambio — el 
único comportamiento distinto es de dónde vienen las credenciales, no cómo 
funciona la conexión.
