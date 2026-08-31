# Tensiones pendientes: decisiones tomadas

Registro de las 5 tensiones detectadas al cruzar el mockup 
(`Mockup CCMS S80 v04.html`), los requisitos (`Requisitos Bloque CCMS v01.docx`) 
y el framework `aacf/`, con la decisión ya confirmada para cada una y sus 
implicaciones técnicas para el diseño de arquitectura. Este documento no 
define arquitectura ni estructura de carpetas — fija el terreno sobre el 
que se diseñará después.

## A. Alcance de gobernanza: deliverable Navantia + uso interno ATEXIS

**Tensión original**: no estaba claro si el proyecto era un deliverable de 
cliente (Navantia, fuera del alcance de la política interna de aacf salvo 
ISO 27001/GDPR + contrato) o una herramienta interna ATEXIS (aacf aplica 
por completo).

**Decisión confirmada**: ambas cosas a la vez. Es un deliverable para 
Navantia, pero la misma plataforma tendrá uso interno de ATEXIS para otros 
proyectos propios — el propio mockup ya lista, además de "S80 — Manuales de 
Mantenimiento" (Navantia), los proyectos "Navantia — Documentación interna", 
"F-110 — Publicaciones técnicas" y "Sandbox migración", que no son 
necesariamente del mismo cliente ni del mismo régimen de gobernanza.

**Implicación técnica (obligatoria, no opcional)**: gobernanza dual por 
proyecto, no un simple filtro de UI.
- Cada proyecto (la entidad ya modelada en el mockup como contenedor 
  autónomo de Nivel 0/1/2) debe llevar asociado explícitamente un 
  **régimen de gobernanza** (p. ej. `cliente_id` / `regimen_governance`: 
  `navantia-contrato` vs `atexis-interno`), no inferido por convención de 
  nombre.
- El aislamiento debe ser **de datos**, no solo de navegación: un usuario 
  con acceso al proyecto interno de ATEXIS no debe poder consultar, buscar, 
  ni indexar (búsqueda, ServiLog, reports) contenido de un proyecto 
  Navantia sin permiso explícito sobre ese proyecto concreto — y viceversa. 
  La búsqueda global y los reports de integridad deben resolverse 
  **por proyecto**, nunca cruzando proyectos de distinto régimen por 
  defecto.
- Las obligaciones de auditoría/DLP/retención que apliquen (ISO 27001 + 
  GDPR de Navantia para su contenido; guardrails aacf para el contenido 
  interno ATEXIS) deben poder aplicarse de forma diferenciada por proyecto, 
  no como una única política global del sistema.
- Esto condiciona el modelo de datos desde el esquema base (no es una 
  capa añadida después): todo objeto de contenido, todo registro de 
  auditoría y todo índice derivado debe ser trazable a un proyecto, y todo 
  proyecto a un régimen de gobernanza.

## B. Autenticación: SSO federado con dos Identity Providers

**Tensión original**: el mockup se contradecía a sí mismo (login decía 
"acceso corporativo (SSO)"; Administración decía "Identidad local, sin SSO 
en el MVP"), frente a aacf (Keycloak OIDC obligatorio) y el docx 
("login corporativo").

**Decisión confirmada**: SSO, aceptando credenciales de sesión tanto de 
Navantia como de ATEXIS.

**Implicación técnica**: esto no es un SSO de un único IdP — es un 
escenario de **dos Identity Providers federados** simultáneos, consistente 
con la gobernanza dual del punto A (un usuario Navantia trabajando en un 
proyecto Navantia; un usuario ATEXIS trabajando en un proyecto interno; 
potencialmente ambos necesitando acceder al mismo CCMS).
- El backend debe aceptar y verificar aserciones SAML/OIDC procedentes de 
  **dos IdP distintos** (el de Navantia y el de ATEXIS/Keycloak), no un 
  único flujo SSO fijo.
- Cada aserción entrante debe mapearse a roles/permisos internos del CCMS 
  **junto con su procedencia** (de qué IdP vino esa identidad) — la 
  procedencia del IdP es, además, la señal natural para saber a qué régimen 
  de gobernanza (punto A) pertenece ese usuario por defecto, aunque el 
  acceso final a un proyecto concreto lo siga decidiendo el RBAC del punto 
  C.
- Hace falta decidir explícitamente (pendiente, no bloqueante para el 
  diseño de la arquitectura, pero sí antes de implementar auth): protocolo 
  de cada IdP (SAML vs OIDC — pueden no coincidir entre Navantia y ATEXIS), 
  y qué pasa con un usuario que en el futuro tuviera identidad válida en 
  ambos IdP a la vez.
- Es más complejo que el flujo SSO de un único IdP ya documentado como 
  patrón estándar en aacf (Keycloak OIDC) — la arquitectura debe prever un 
  punto de federación/selección de IdP en el login, no asumir un único 
  proveedor de identidad.

## C. RBAC: catálogo de datos, no constantes en código

**Tensión original**: tres listas de roles distintas y no coincidentes 
(6 roles en el docx §1.A.7, "5 roles" sin nombrar en el docx §1.B.6, 5 
roles distintos en el mockup incluyendo "Armada | Ministerio de Defensa", 
que no aparece en el docx).

**Decisión confirmada**: la lista definitiva de roles se cerrará más 
adelante — no se fija ahora.

**Implicación técnica (restricción de diseño obligatoria)**: precisamente 
porque la lista no está cerrada, el esquema de roles y permisos debe 
modelarse como **tabla de catálogo** (roles, permisos, y la matriz 
rol→operación como datos en base de datos), nunca como constantes o 
enumeraciones hardcodeadas en el código — mismo patrón de tabla de catálogo 
ya usado para estados de workflow en fases anteriores del curso (tabla 
`estados`, con `orden`, en vez de un enum fijo).
- Añadir, renombrar o eliminar un rol, o cambiar qué operaciones permite 
  (la matriz vista en el panel de Administración del mockup) debe ser una 
  operación de datos vía UI de administración, no un cambio de código ni un 
  despliegue.
- El rol "Armada | Ministerio de Defensa" del mockup (aprobar/rechazar y 
  gestionar SIR, pero sin check-out/check-in ni publicar) debe poder 
  representarse igual que cualquier otro rol dentro de ese catálogo — sin 
  necesitar un caso especial en el modelo de datos ni en el código de 
  autorización.
- Dado el punto A, conviene que la matriz de permisos pueda variar por 
  proyecto (ya lo intuye el propio mockup: "RBAC a nivel de proyecto" en la 
  nota de la pantalla de administración) — el catálogo de roles puede ser 
  global, pero la asignación rol↔usuario↔proyecto y la matriz 
  rol→operación deben poder particularizarse por proyecto.

## D. i18n: capa implementada, un único idioma poblado

**Tensión original**: HR15 de aacf ("todo texto de UI debe ser 
localizable", no negociable) frente a la nota del propio mockup 
("Multiidioma: fuera del alcance de la migración").

**Decisión confirmada**: se implementa la capa i18n (todo texto de UI 
enrutado a través de ella, sin strings hardcodeadas), pero solo se puebla 
el locale es-ES por ahora. Sin trabajo de traducción real a otros idiomas 
en este alcance.

**Implicación técnica**: esto cumple HR15 en la letra, no en la 
funcionalidad — hay que dejarlo explícito para que no se lea como 
"no aplica HR15" ni como "hay que entregar multi-idioma real".
- Ningún texto de UI se escribe literal en el componente; todo pasa por la 
  capa de i18n con clave + valor es-ES.
- No hace falta trabajo de extracción/gestión de traducciones a otros 
  idiomas en este alcance — la capa existe para que añadir un idioma en el 
  futuro sea un cambio de datos (nuevo fichero de locale), no una 
  reescritura de componentes.

## E. Clasificación de seguridad: riesgo abierto de alta prioridad

**Tensión original**: el docx lleva una etiqueta de sensibilidad de 
Microsoft Purview ("Sensitivity: C2-Restricted") y trata contenido de 
mantenimiento de submarinos de la Armada, sin que ni el mockup ni el docx 
mencionen clasificación de datos ni tiering.

**Decisión confirmada**: depende directamente del punto A. Como el proyecto 
sí tiene un componente de uso interno ATEXIS (no es únicamente deliverable 
de cliente), la clasificación de seguridad debe tratarse con el nivel de 
rigor de aacf para la parte de la plataforma bajo gobernanza ATEXIS — pero 
sigue **pendiente de confirmación formal por seguridad/compliance de 
ATEXIS** antes de construir nada sobre esa base.

**Implicación técnica**: no bloquea el diseño de arquitectura, pero debe 
quedar marcado como **riesgo abierto de alta prioridad** en el checklist 
final del proyecto, con estas preguntas concretas sin resolver:
- Qué tier de aacf (T1–T4) corresponde a la parte del sistema bajo 
  gobernanza ATEXIS, dado el contenido "C2-Restricted" y de naturaleza de 
  defensa que puede circular por ella (aunque sea indirectamente, vía 
  usuarios con acceso a ambos regímenes de gobernanza del punto A).
- Qué controles de `governance/guardrails.md` (G1–G12) son exigibles desde 
  el primer despliegue frente a cuáles pueden añadirse en una fase de 
  hardening posterior.
- Si aplican restricciones onshore/offshore (mencionadas en 
  `docs/SECURITY_CONTEXT.md`) al equipo que desarrolla o administra la 
  parte interna ATEXIS de la plataforma.
- Confirmación de que el aislamiento de datos por proyecto del punto A es, 
  por sí solo, control suficiente para que el contenido Navantia 
  C2-Restricted no quede expuesto a la superficie de gobernanza interna 
  ATEXIS (auditoría, guardrails, agentes de IA con acceso al repositorio) 
  sin autorización explícita de Navantia.

No se avanza en la implementación de ningún control de este punto hasta 
que seguridad/compliance de ATEXIS lo confirme formalmente.
