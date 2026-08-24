# Síntesis final del CCMS

Documento de cierre del curso: no añade piezas nuevas a la arquitectura — 
resume lo ya diseñado y defendido en `fase-4-arquitectura-sistemas/
2-ejercicio_arquitectura_ccms.md`, lo convierte en preguntas reutilizables 
para evaluar cualquier propuesta futura (propia o de un proveedor), fija los 
riesgos técnicos reales identificados a lo largo de las fases, y cierra con 
un balance honesto de qué costó más entender.

## Resumen de la arquitectura propuesta

El CCMS se apoya en un **backend FastAPI único, monolito modular** 
(`routers/` → `services/` → `storage/`), no en microservicios — decisión 
tomada en el checkpoint de `fase-1-backend/README.md` y reconfirmada, 
pieza por pieza, en la Fase 4: solo tres piezas viven fuera del monolito 
porque tienen ciclo de despliegue, escalado o naturaleza técnica distinta, 
no porque "sea lo moderno".

**Persistencia**: PostgreSQL es la única base de datos obligatoria — el 
esquema de 9 tablas de `fase-2-bases-de-datos/2-construccion_esquema_bd.md` 
(`objetos_contenido`, `revisiones`, `versiones`, `mapa_topic_refs`...) ya 
resuelve versionado a nivel de componente sin depender de una base XML 
nativa. eXist-db queda dibujado como pieza **opcional, no activa**, con una 
justificación real y concreta (validar keyrefs/referencias cruzadas DITA, 
detectar enlaces rotos, aplicar condicionales de filtering/profiling) — no 
por casos de uso débiles como "editar un título".

**Búsqueda**: Elasticsearch/OpenSearch, siempre como copia derivada — nunca 
fuente de verdad, reconstruible desde PostgreSQL. En producción corre como 
**clúster con réplicas**, no como instancia única, con reindexado 
incremental en operación normal (no reindexado total constante).

**LLM local**: on-premise, en su propio contenedor Docker con acceso a GPU, 
sin salida a internet — así se sostiene el requisito de que ningún 
contenido salga de España. Si falla, degrada solo la función de "mejorar 
con IA", no el resto del sistema.

**Publicación**: pipeline DITA-OT detrás de una cola de trabajo (Celery/RQ), 
un worker separado que no bloquea peticiones web mientras genera PDF/HTML.

**Identidad**: SSO vía Active Directory/Azure AD para empleados internos 
(autores, revisores, publishers), con un segundo flujo de identidad 
separado (IdP externo tipo Auth0/Cognito, o tabla propia con passlib como 
último recurso) para usuarios externos de solo lectura — ambos convergen en 
el mismo JWT con RBAC aplicado en `services/`.

**Integración con editores externos**: los endpoints `checkout`/`checkin` 
ya son agnósticos del editor. Oxygen tiene conexión directa (API Key, 
plugin nativo) y, además, un camino vía agente local; XMetaL, al no tener 
conector nativo propio, solo tiene el camino del agente local — una 
pequeña aplicación instalada en cada máquina que sí puede lanzar procesos 
nativos, algo que el navegador tiene bloqueado por diseño.

El diagrama Mermaid completo, con cada pieza justificada línea por línea y 
citando el archivo exacto de la fase que la sustenta, vive en 
`fase-4-arquitectura-sistemas/2-ejercicio_arquitectura_ccms.md` — este 
resumen no lo repite, lo referencia.

## Preguntas técnicas para un proveedor o el propio equipo

Cada pregunta incómoda que este proyecto tuvo que responder en la ronda de 
"abogado del diablo" de la Fase 4, convertida en la pregunta que le haría a 
cualquiera que proponga algo similar.

1. **(De la Pregunta 1 — Elasticsearch vs PostgreSQL)** ¿Qué garantías 
   transaccionales y de integridad referencial ofrece tu solución de 
   persistencia? Si el motor de búsqueda se corrompe, ¿hay una fuente de 
   verdad separada desde la que reconstruirlo sin pérdida de datos, o es la 
   única copia que existe?

2. **(De la Pregunta 2 — SSO vs login propio, usuarios internos/externos)** 
   ¿Cómo gestionas el ciclo de vida de acceso — alta y, sobre todo, baja — 
   de un usuario? ¿Tu propuesta distingue empleados internos (con identidad 
   corporativa centralizada) de usuarios externos, o mete a ambos en el 
   mismo sistema de credenciales?

3. **(De la Pregunta 3 — justificación real de eXist-db)** ¿Qué necesidad 
   concreta sobre el contenido XML/DITA no resuelve ya una base de datos 
   relacional — validación de keys/keyrefs, detección de enlaces rotos, 
   condicionales de filtering/profiling — y qué volumen real de contenido 
   justifica añadir una base de datos XML nativa aparte, en vez de tratarlo 
   como texto opaco?

4. **(De la Pregunta 4 — alta disponibilidad de Elasticsearch)** ¿Tu motor 
   de búsqueda corre como instancia única o como clúster con réplicas? Si 
   el índice se corrompe, ¿cuánto tiempo y qué grado de degradación de 
   servicio implica reconstruirlo, y existe un plan de búsqueda de 
   emergencia mientras tanto?

5. **(De la Pregunta 5 — monolito modular vs microservicios)** ¿Qué parte 
   de tu propuesta es lógica de negocio separada en servicios, y qué parte 
   es infraestructura de apoyo (bases de datos, motores de búsqueda, 
   hardware especializado) — y por qué se separó cada una? Si no hay una 
   pieza concreta con ciclo de despliegue, escalado o equipo distinto, 
   ¿qué justifica dividirlo en varios servicios en vez de un solo backend 
   modular?

6. **(De la Pregunta 6 — integración con editores externos)** ¿Cómo resuelve 
   tu propuesta lanzar una aplicación de escritorio (el editor XML) desde 
   una interfaz que corre en el navegador, dado que el navegador no puede 
   lanzar ejecutables nativos por diseño de seguridad? ¿Ese mecanismo es 
   agnóstico del editor concreto, o queda atado a uno solo?

## Checklist de riesgos técnicos a vigilar

- [ ] **Residencia de datos**: el LLM local (y cualquier otro servicio 
      externo que procese contenido) no debe tener salida a internet — 
      configurado explícitamente por red/firewall, no asumido por defecto 
      (ver `fase-5-herramientas-vibe-coder/README.md`, checkpoint de 
      despliegue del LLM).
- [ ] **Escalabilidad**: no añadir caché, escalado horizontal ni clústeres 
      sin una razón medida concreta — el mismo criterio del checkpoint de 
      microservicios de la Fase 1 aplica aquí: la complejidad debe 
      justificar la herramienta.
- [ ] **Mantenibilidad (arquitectura por capas)**: vigilar que routers/ 
      services/storage sigan sin mezclarse a medida que crece el proyecto — 
      la migración de memoria a PostgreSQL en la Fase 2 (cero cambios en 
      routers/services) es la prueba de que la separación cumple su 
      propósito; una regresión aquí sería la señal de alarma.
- [ ] **Coste de licencias de bases de datos XML nativas vs relacional**: 
      eXist-db es open source, pero alternativas comerciales de la misma 
      categoría (MarkLogic, TEXTML Server de IXIASoft) no lo son — antes de 
      añadir cualquier base XML nativa, confirmar que la necesidad es real 
      (ver tabla de necesidades XML/DITA en la Fase 4) y no solo "porque el 
      sector la usa".
- [ ] **Bloqueos huérfanos en checkout/checkin con editores externos**: si 
      el agente local o el ordenador del autor se cierran sin hacer 
      check-in, el bloqueo (`objeto_estado`) queda colgado — requiere 
      timeout automático o desbloqueo administrativo (rol publisher), no 
      confiar en que el autor siempre cierre limpiamente.
- [ ] **Dependencia de Active Directory para SSO**: si Active Directory/
      Azure AD cae, nadie puede iniciar sesión en el CCMS — es un punto 
      único de fallo externo al propio proyecto; vale la pena confirmar con 
      IT su SLA de disponibilidad antes de asumir que "siempre está 
      arriba".
- [ ] **Degradación de Elasticsearch**: aunque sea copia derivada y 
      reconstruible, una corrupción de índice sin plan de búsqueda de 
      emergencia (fallback a un `LIKE` simple contra PostgreSQL) deja a los 
      autores sin poder encontrar contenido reutilizable durante la 
      reconstrucción — riesgo de producto, no solo técnico.
- [ ] **Compatibilidad de sistema operativo de XMetaL**: al ser Windows-only 
      (ActiveX), el selector de editor en el dashboard debe ocultarlo 
      automáticamente en Mac/Linux — de lo contrario, un autor no-Windows 
      vería una opción que nunca podría usar.
- [ ] **Secretos fuera del código**: confirmado ya como práctica (`.env` + 
      `.gitignore` + `.env.example` en la Fase 5), pero a vigilar que se 
      mantenga en cualquier pieza nueva (LLM, agente local, futuras 
      integraciones) — nunca credenciales hardcodeadas, y en producción 
      real, un gestor de secretos centralizado en vez de `.env` sueltos por 
      servidor.

## Cierre personal

Lo que más costó entender no fueron los conceptos grandes (arquitectura, 
monolito vs microservicios) sino los pasos pequeños y mecánicos que se dan 
por sabidos en cualquier tutorial: qué hace exactamente `venv` y por qué 
hace falta activarlo antes de instalar nada (Fase 0/1), por qué el 
navegador bloquea una petición a otro puerto si el backend no manda las 
cabeceras CORS correctas (Fase 0, y de nuevo al conectar el dashboard en la 
Fase 3), o que `useState` no "se conecta" mágicamente con `fetch()` — son 
dos pasos distintos (`useState` declara la caja, `setTopics` dentro del 
`.then()` es quien la llena) que parecían el mismo paso hasta desglosarlo 
línea por línea.

Lo más útil no fue que el código funcionara a la primera, sino cuando 
falló de verdad y hubo que entender por qué: el primer despliegue del 
workflow de GitHub Actions en la Fase 5 rompió con 
`invalid literal for int() with base 10: 'None'` porque `.env` no existe 
(a propósito) en el runner de CI — un fallo real, no simulado, que obligó a 
entender la diferencia entre `os.getenv("VAR")` y 
`os.getenv("VAR", "valor_por_defecto")` mucho mejor que si hubiera 
funcionado a la primera.

Y lo que queda más claro ahora que al principio es que una arquitectura no 
se defiende sola. En la Fase 4, dos argumentos que sonaban razonables al 
escribirlos no resistieron la pregunta siguiente: justificar eXist-db con 
"para poder editar un título sin reescribir el documento" era débil (en 
PostgreSQL eso es solo regrabar una columna) y hubo que sustituirlo por el 
motivo real (validar keyrefs, enlaces rotos, condicionales DITA); y 
"monolito modular porque no hay microservicios" no bastaba hasta precisar 
el criterio exacto — no es cuántos procesos corren, es cuánta lógica de 
negocio propia del CCMS queda dividida en servicios independientes. Ambas 
correcciones solo salieron a la luz porque alguien preguntó "¿por qué, 
exactamente?" una vez más de lo que el primer borrador contestaba. Esa es 
la habilidad que se llevó este curso: no memorizar una arquitectura fija, 
sino poder defenderla bajo presión real, y saber corregirla en el momento 
en que un argumento flaquea.
