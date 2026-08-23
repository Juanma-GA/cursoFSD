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

## Ejercicio

_Pendiente de empezar esta fase._
