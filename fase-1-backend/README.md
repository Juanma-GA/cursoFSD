# Fase 1 — Backend

## Resumen

En esta fase se trabaja el desarrollo del lado servidor: cómo construir una API, gestionar rutas, peticiones y respuestas, lógica de negocio, autenticación y buenas prácticas de backend.

## Checklist de conceptos clave

- [ ] (pendiente de definir)

## Conceptos clave

### Lenguaje/framework: FastAPI
Se usa FastAPI en vez de Django (más pesado, pensado para apps con mucha UI 
server-side) o Node.js (otro ecosistema entero). FastAPI es moderno, tipado, y 
genera documentación de API automática — útil para explicar la arquitectura a 
terceros.

### Arquitectura por capas
- **Rutas/controladores**: reciben la petición HTTP, no deciden nada.
- **Lógica de negocio/servicios**: aquí vive el "qué hacer" — validar permisos, 
  aplicar reglas del workflow.
- **Acceso a datos/repositorios**: hablan con la base de datos, nada más.

Se separa así por mantenibilidad (cambiar de base de datos solo afecta a la capa 
de repositorios) y testeo (se puede probar la lógica de negocio sin BD real).

### Autenticación vs autorización
- **Autenticación** = "¿quién eres?" (login, verificar contraseña o token)
- **Autorización** = "¿qué puedes hacer, ya que sé quién eres?" (rol de autor, 
  revisor o publisher; permisos sobre un proyecto concreto)

Crítico en un CCMS: un autor no debería poder publicar directamente, un revisor 
no debería poder borrar topics de otro proyecto, etc.

### API Keys vs OAuth vs JWT
- **API Key**: clave fija que identifica a una aplicación cliente, sin usuario 
  individual detrás (así se conecta Oxygen al LLM).
- **OAuth**: protocolo para delegar acceso sin compartir contraseñas (ej. "iniciar 
  sesión con Google").
- **JWT** (JSON Web Token): token firmado que el backend entrega tras el login, 
  reenviado por el cliente en cada petición para demostrar quién es sin volver 
  a autenticarse cada vez.

Para el CCMS: probablemente API Key para la integración con Oxygen (aplicación-a-
aplicación), y JWT para sesiones de usuarios humanos en el panel de administración.

### Procesamiento asíncrono / colas de trabajo (Celery, RQ)
Una llamada al LLM o una generación de PDF puede tardar segundos o minutos. Si el 
backend espera bloqueado a que termine, la interfaz se congela y otros usuarios no 
pueden ser atendidos. Con una cola de trabajo, el backend responde de inmediato 
("tarea en proceso") y un worker separado hace el trabajo pesado en segundo plano, 
avisando cuando termina.

### Monolito vs microservicios vs "monolito modular"
Un microservicio es un sistema completo (backend propio, a veces BD propia) 
dedicado a una sola responsabilidad, comunicándose con otros por red — añade 
complejidad real (más piezas, más comunicación que puede fallar, más monitorización). 
Para un CCMS de tamaño medio, un **monolito bien modularizado** (un solo backend 
organizado internamente en módulos: autoría, workflow, publicación, búsqueda) 
casi siempre es la opción correcta. Desconfiar de quien proponga microservicios 
"porque es lo moderno" sin una razón concreta de escala o equipo.

## Ejercicio

_Pendiente de empezar esta fase._
