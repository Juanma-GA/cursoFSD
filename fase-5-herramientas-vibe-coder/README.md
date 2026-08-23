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

_Pendiente de empezar esta fase._
