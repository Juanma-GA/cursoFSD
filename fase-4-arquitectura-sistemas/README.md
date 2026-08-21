# Fase 4 — Arquitectura de sistemas

## Resumen

En esta fase se trabaja el diseño de sistemas a mayor escala: patrones de arquitectura, escalabilidad, despliegue, infraestructura y buenas prácticas de sistemas distribuidos.

## Checklist de conceptos clave

- [ ] (pendiente de definir)

## Conceptos clave

### Arquitectura de 3 capas
Presentación (frontend React) / lógica de negocio (backend FastAPI) / datos 
(PostgreSQL, y potencialmente eXist-db). Mantenerlas separadas permite 
cambiar una pieza sin romper las demás — ya demostrado en la Fase 2, cuando 
la migración de memoria a PostgreSQL no requirió tocar routers ni services.

### REST vs GraphQL vs gRPC
Ya visto en el checkpoint de microservicios de la Fase 1. Para un CCMS, REST 
casi siempre es suficiente y más fácil de mantener. GraphQL aportaría valor 
solo si el frontend necesitara combinar datos de muchas fuentes distintas en 
una sola pantalla. gRPC solo tendría sentido para comunicación interna entre 
microservicios de alta frecuencia — ya descartados como innecesarios para 
esta escala.

### Ampliación: REST vs GraphQL vs gRPC, con ejemplos

Los tres son estilos de arquitectura para diseñar cómo cliente y servidor se 
comunican:

**REST** (usado en este proyecto): recursos identificados por URLs, verbos 
HTTP con significado, cada endpoint devuelve una estructura fija. `GET /topics` 
siempre devuelve todos los campos de cada topic, aunque el frontend solo 
necesite el título.

**GraphQL**: un único endpoint; el cliente especifica exactamente qué campos 
quiere:
```graphql
query {
  topics {
    titulo
  }
}
```
Ventaja: cuando una pantalla necesita combinar datos de varias fuentes a la 
vez (topic + autor + última revisión + estado), REST necesitaría 3-4 llamadas 
distintas; GraphQL, una sola consulta anidada.

**gRPC**: formato binario (Protocol Buffers) sobre HTTP/2, pensado para 
comunicación entre servicios backend, no para que un navegador lo consuma 
directamente. Mucho más rápido y compacto, pero requiere contratos estrictos 
definidos de antemano (.proto) y no se prueba con curl/navegador como REST.

Por qué REST basta en este proyecto: no hay el problema que GraphQL resuelve 
(combinar muchas fuentes en una pantalla compleja), y no hay microservicios 
internos hablando entre sí a alta frecuencia que justifiquen gRPC — misma 
lógica que el checkpoint de microservicios de la Fase 1: la complejidad debe 
justificar la herramienta.

### Diseño de arquitectura para CCMS: piezas ya construidas o exploradas
- Repositorio de contenido (BD XML nativa o relacional + almacenamiento de 
  ficheros): diseñado y comparado en la Fase 2 (construccion_esquema_bd.md, 
  4-ejercicio_xmlBD.md).
- Capa de integración con herramientas de autoría (Oxygen, vía API): patrón 
  de API Key ya conocido del proyecto previo.
- Capa de integración con el LLM (local, on-premise): el mock construido en 
  la Fase 1 (POST /topics/{id}/mejorar), ahora a pensar en su versión real.
- Motor de workflow (borrador → revisión → aprobado → publicado): tabla 
  `estados` diseñada en la Fase 2.
- Pipeline de publicación (DITA-OT, generación de PDF/HTML/help): nuevo en 
  esta fase.
- Motor de búsqueda y reutilización: Elasticsearch/OpenSearch, ya comparado 
  conceptualmente en 5-ejercicio_busquedas.md de la Fase 2.

### Seguridad y residencia de datos
Cómo se traduce en arquitectura un requisito como "los datos no pueden salir 
de España" — ya aplicado de facto con el LLM local en el proyecto de Oxygen; 
en esta fase se entiende el porqué técnico: dónde vive físicamente cada 
servidor, qué tráfico sale a internet y cuál no.

### Ampliación: Seguridad, temas concretos a explorar

- **HTTPS/TLS en producción**: cómo se obtiene y renueva un certificado real 
  (Let's Encrypt, certificados corporativos), y por qué Nginx suele 
  gestionarlo (rol de "portero" visto en la Fase 0).
- **Gestión de secretos**: contraseñas y API keys no deben ir hardcodeadas en 
  el código (como curso123 en database.py ahora mismo) — en producción se 
  mueven a variables de entorno o a un gestor de secretos dedicado (Vault, 
  AWS Secrets Manager). Tema retomado en la Fase 5.
- **OWASP Top 10**: lista de referencia de las vulnerabilidades web más 
  comunes (inyección SQL, autenticación rota, exposición de datos sensibles). 
  No requiere memorizarse, pero es la checklist de referencia del sector.
- **Auditoría y logs**: quién hizo qué y cuándo. La tabla `revisiones` (con 
  autor y fecha, Fase 2) ya es una forma de auditoría de contenido; la 
  seguridad añade auditoría de accesos (quién entró, desde dónde, qué 
  intentó hacer).
- **Rate limiting**: limitar peticiones por segundo por IP/usuario, para 
  evitar abuso o fuerza bruta — normalmente configurado en Nginx o en 
  middleware del backend.

### Escalabilidad y caché (nivel conceptual)
No es prioridad en un CCMS interno de tamaño medio, pero es necesario saber 
reconocer cuándo un proveedor vende complejidad innecesaria — mismo criterio 
aplicado en el checkpoint de microservicios de la Fase 1.

### Ampliación: Escalabilidad y caché, temas concretos

- **Caché aplicada al CCMS**: guardar temporalmente el resultado de algo 
  costoso (lista de topics más buscados, resultado de una búsqueda en 
  Elasticsearch) para no recalcularlo en cada petición. Herramienta típica: 
  Redis (base de datos en memoria, muy rápida, pensada para esto).
- **Escalado vertical vs horizontal**: vertical = más recursos (CPU/RAM) a 
  la misma máquina; horizontal = más máquinas corriendo el mismo backend, 
  repartiendo carga (requiere un balanceador de carga, otra vez el rol de 
  Nginx).
- **Por qué probablemente no es necesario aún**: un CCMS interno de tamaño 
  medio, con decenas de usuarios simultáneos, no tiene el volumen que 
  justifica escalado horizontal ni caché agresiva — misma pregunta que con 
  microservicios: ¿qué problema de carga concreto y medido existe?
- **Índices de base de datos**: ya mencionados en la Fase 2 sin profundizar. 
  Aceleran búsquedas en PostgreSQL sobre columnas muy consultadas (ej. 
  buscar revisiones por objeto_id), a cambio de un pequeño coste al escribir. 
  La optimización de rendimiento más barata y de mayor impacto antes de 
  pensar en nada más sofisticado.

### Gestión de usuarios corporativos: RBAC y autenticación centralizada

**RBAC (Role-Based Access Control)**: un usuario tiene un rol (autor, 
revisor, publisher), y ese rol determina qué acciones puede hacer. Vive en 
la capa de lógica de negocio (backend, en services/) — donde se comprueba 
"¿este usuario, con este rol, puede mover este topic a estado publicado?" 
antes de ejecutar la acción.

Gestionar usuarios corporativos añade una pieza previa al RBAC: la 
autenticación centralizada.

- **LDAP / Active Directory**: sistema donde una empresa ya tiene 
  registrados a sus empleados con sus contraseñas corporativas. En vez de 
  que el CCMS tenga su propia tabla de usuarios con contraseñas propias, se 
  conecta a ese directorio existente para verificar identidad.
- **SSO (Single Sign-On)**: el usuario inicia sesión una vez (ej. al entrar 
  en su ordenador de empresa) y accede a todas las aplicaciones internas sin 
  volver a teclear contraseña. Se implementa con protocolos como SAML o 
  OAuth2/OIDC (evolución moderna de OAuth, ya visto en la Fase 1).
- **Dónde vive cada pieza**: la autenticación (verificar identidad contra 
  LDAP/SSO) vive en una capa específica del backend (a veces delegada a un 
  servicio externo dedicado), que entrega un JWT (Fase 1) con identidad y 
  rol. Cada endpoint de routers comprueba ese JWT; services aplica el RBAC 
  correspondiente.

**Flujo completo aplicado al CCMS:**
1. El autor abre el dashboard, es redirigido a login (posiblemente contra 
   Active Directory vía SSO).
2. Tras autenticarse, recibe un JWT: "soy [usuario], mi rol es autor".
3. El dashboard adjunta ese JWT en cada petición al backend.
4. El backend verifica el JWT en routers, y aplica el RBAC en services: 
   "¿un autor puede hacer esto? Sí/No".

### Cómo funciona SSO con Active Directory, paso a paso

**El problema que resuelve**: sin SSO, cada aplicación (CCMS, correo, 
intranet) tendría su propia base de usuarios y contraseñas — un empleado 
recordaría N contraseñas, e IT daría de alta/baja en N sistemas por 
separado. SSO centraliza esto en un único punto de verdad.

**Los actores, con nombres reales del sector:**
- **Identity Provider (IdP)**: sistema que verifica identidad — Active 
  Directory (on-premise) o Azure AD/Microsoft Entra ID (nube). Fuente de 
  verdad de quién trabaja en la empresa y con qué permisos generales.
- **Service Provider (SP)**: la aplicación que quiere que el usuario inicie 
  sesión — en este proyecto, el backend del CCMS.
- **Protocolo que conecta ambos**: SAML (más veterano, típico con Active 
  Directory clásico/ADFS) u OAuth2/OIDC (más moderno, típico con Azure 
  AD/Entra ID en la nube).

**El flujo real, con SAML como ejemplo:**
1. El autor abre el dashboard y pulsa "Iniciar sesión".
2. El backend redirige el navegador hacia el Identity Provider (no pide 
   usuario/contraseña directamente).
3. Si el usuario ya tiene sesión de Windows activa, el IdP no vuelve a pedir 
   nada — reconoce que ya está autenticado.
4. El IdP construye una "aserción SAML": XML firmado digitalmente que 
   certifica la identidad del usuario, sus grupos de Active Directory, y la 
   validez temporal.
5. El navegador vuelve al CCMS llevando esa aserción.
6. El backend verifica la firma digital (con un certificado público 
   intercambiado de antemano con el IdP), confirmando que viene realmente 
   del Active Directory real, no de una falsificación.
7. Con la identidad confirmada, el backend genera su propio JWT, mapeando 
   grupos de Active Directory a roles internos (ej. grupo AD 
   "CCMS-Autores" → rol interno "autor").
8. A partir de aquí, flujo normal: JWT en cada petición, RBAC en services/.

**Punto clave**: el backend nunca ve ni gestiona la contraseña real del 
usuario — solo confía en la aserción firmada del IdP. Esto hace SSO más 
seguro que si cada aplicación gestionara sus propias contraseñas.

**Diferencia con OAuth2/OIDC**: flujo conceptualmente similar, pero el IdP 
entrega directamente un token JWT ya construido ("ID token"), sin necesidad 
de construirlo a partir de una aserción SAML — más simple de implementar en 
un stack moderno como FastAPI.

#### La URL de redirección: qué es y de dónde sale

Es una URL real, pero con información codificada dentro, no un enlace fijo. 
Requiere una configuración previa (una sola vez):

1. **Registro previo de la aplicación en el IdP** (lo gestiona IT), que 
   entrega:
   - Un **Entity ID** (SAML) o **Client ID** (OAuth2): identificador único 
     de la aplicación CCMS ante el IdP.
   - La **URL base del IdP** (ej. `https://sts.atexis.com/adfs/ls/` para 
     ADFS/SAML, o `https://login.microsoftonline.com/{tenant-id}/` para 
     Azure AD/OIDC).
   - Un certificado o secreto compartido, para verificar después que las 
     respuestas vienen realmente de ese IdP.

2. **En el momento del login, el backend construye la URL dinámicamente.** 
   Ejemplo simplificado con SAML:

```
https://sts.atexis.com/adfs/ls/?SAMLRequest=<XML_codificado>&RelayState=https://ccms.atexis.com/dashboard
```

   - `SAMLRequest`: XML codificado en base64 pidiendo autenticar a alguien 
     para esta aplicación.
   - `RelayState`: URL de vuelta tras completar el login.

   Ejemplo simplificado con OAuth2/OIDC:

```
https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/authorize?client_id=TU_CLIENT_ID&redirect_uri=https://ccms.atexis.com/callback&response_type=code&scope=openid
```

3. **Esta URL no se construye a mano con concatenación de texto** — se usa 
   una librería (`python3-saml` para SAML, `Authlib` para OIDC) que genera 
   correctamente el `SAMLRequest` o los parámetros OAuth2 siguiendo el 
   estándar exacto, sin necesidad de conocer cada detalle criptográfico.

**Secuencia práctica necesaria, en orden:**
1. Pedir a IT: URL base del IdP, Entity ID/Client ID asignado, certificado 
   o secreto de confianza.
2. Instalar la librería correspondiente (SAML u OIDC) en el backend FastAPI.
3. La librería, con esos datos de configuración, construye automáticamente 
   la URL de redirección correcta en el momento del login.

## Ejercicio

_Pendiente de empezar esta fase._
