# Fase 3 — Frontend

## Resumen

En esta fase se trabaja el desarrollo del lado cliente: HTML, CSS, JavaScript avanzado, frameworks/librerías de UI, gestión de estado y consumo de APIs.

## Checklist de conceptos clave

- [ ] (pendiente de definir)

## Conceptos clave

### HTML/CSS/JS: lo mínimo para leer, no para escribir de cero
La Fase 0 ya cubrió lo esencial (fetch(), el navegador ejecutando JS de forma 
nativa). El objetivo de esta fase es dirigir a Claude Code con criterio, no 
competir escribiendo líneas de JS a mano.

### Frameworks: React vs Vue vs Angular
Los tres resuelven el mismo problema (interfaces dinámicas) con filosofías 
distintas:
- **React**: el más usado, ecosistema enorme, mucha demanda de mercado.
- **Vue**: curva de aprendizaje más suave, sintaxis más cercana a 
  HTML/CSS tradicional.
- **Angular**: más "empresarial" y rígido, con más estructura impuesta de 
  fábrica — habitual en grandes corporaciones con equipos grandes que 
  necesitan convenciones estrictas.

Para un panel de administración interno de tamaño medio, React o Vue son las 
opciones razonables — Angular añadiría rigidez innecesaria para este tamaño 
de proyecto.

### Arquitectura por componentes
La interfaz se construye como piezas reutilizables e independientes (un 
botón, una tarjeta de topic, una tabla de resultados), cada una con su propio 
estado y lógica. Misma filosofía que la reutilización de topics en DITA — un 
componente de UI, como un topic, se escribe una vez y se usa en muchos 
sitios.

### Gestión de estado
"Estado" es cualquier dato que cambia y que la interfaz necesita reflejar 
(¿está el formulario abierto? ¿qué topics se han cargado? ¿hay un error?). 
Para casos simples, `useState` de React basta. Cuando ese estado necesita 
compartirse entre componentes lejanos entre sí (ej. "qué usuario está 
logueado" necesitándose en el header, el formulario y el pie de página a la 
vez), aparecen herramientas más avanzadas de gestión de estado — no 
necesario en la primera versión de este dashboard.

### SPA vs renderizado tradicional
Una SPA (Single Page Application) carga una sola vez y luego actualiza solo 
las partes que cambian, usando fetch() para traer datos nuevos sin recargar 
toda la página — el mismo patrón visto en la Fase 0. El modelo tradicional 
(páginas PHP clásicas, por ejemplo) recarga la página completa en cada clic. 
React construye SPAs por defecto.

## Ejercicio

_Pendiente de empezar esta fase._
