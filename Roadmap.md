# Roadmap: NLTK Git Commit Generator

Este roadmap documenta el progreso del generador de commits inteligente basado en NLTK. El objetivo del proyecto es acercarse al estilo de commits que suele producir una IA avanzada, pero manteniendo una implementación local, ligera y explicable.

## Funcionalidades Completadas

### [x] Configuración Inicial del Proyecto
- [x] Creación del repositorio y estructura básica.
- [x] Instalación de dependencias principales: NLTK y PyQt6.
- [x] Verificación inicial de datos NLTK requeridos al arrancar la aplicación.
- [x] Descarga automática de paquetes NLTK faltantes en el primer uso.

### [x] Interfaz de Escritorio
- [x] Ventana principal en PyQt6 para pegar resúmenes de cambios.
- [x] Botón para generar commits con NLTK.
- [x] Área de salida con comando `git commit` multilinea.
- [x] Botón para copiar el comando al portapapeles.

### [x] Generador Base con NLTK
- [x] Tokenización y POS tagging para textos en inglés.
- [x] Extracción inicial de verbo y objeto para construir el subject.
- [x] Scoring de oraciones para elegir la frase más representativa.
- [x] Formato Conventional Commits: `type(scope): subject`.
- [x] Límite de longitud para subject y body lines.

### [x] Dataset de Ejemplos de Commits
- [x] Creación de `COMMIT_GENERATION_EXAMPLES.md` con casos reales.
- [x] Desarrollo de `parse_commit_examples.py` para parsear ejemplos.
- [x] Exportación de ejemplos a JSON y SQLite.
- [x] Validación de 45 entradas procesadas correctamente.

### [x] Sistema de Comparación y Evaluación
- [x] Creación de `compare_generator.py`.
- [x] Comparación entre commits generados y commits esperados.
- [x] Reporte JSON con métricas de similitud.
- [x] Mejora inicial de similitud de 0.453 a 0.528.
- [x] Aumento posterior de similitud del subject a 0.509.

### [x] Filtrado de Ruido
- [x] Eliminación de comandos de terminal y frases conversacionales irrelevantes.
- [x] Limpieza de líneas generadas por herramientas o asistentes.
- [x] Filtrado de bloques Markdown con triple backtick.
- [x] Ignorar comandos `git commit -m` pegados dentro del resumen.
- [x] Ignorar líneas `-m` incrustadas para evitar que contaminen el body.
- [x] Limpieza de enlaces Markdown, conservando el texto visible del enlace.
- [x] Conservación de validaciones útiles como `py_compile` cuando aparecen dentro de bloques de código.

### [x] Soporte Bilingüe Español/Inglés
- [x] Detección simple de idioma de entrada (`es` / `en`).
- [x] Tokenización por idioma usando Punkt en inglés o español.
- [x] Generación del subject y body en el mismo idioma del resumen.
- [x] Soporte para verbos españoles comunes: `creado`, `actualizado`, `incluye`, `resume`, `corrige`, `mejora`.
- [x] Extracción de objetos en español mediante reglas lingüísticas propias.
- [x] Casos específicos para resúmenes de roadmap en español e inglés.
- [x] Casos específicos para mejoras bilingües/NLP.

### [x] Detección de Type y Scope
- [x] Detección automática de tipos: `feat`, `fix`, `docs`, `test`, `build`, `ci`, `style`, `refactor`, `perf`.
- [x] Detección automática de scopes: `app`, `ui`, `docs`, `repo`, `dict`, `tools`, `nlp`.
- [x] Corrección del falso positivo de `ci` dentro de palabras como `funcionalidades` o `secciones`.
- [x] Priorización de cambios NLP/bilingües como `feat(nlp)`.
- [x] Clasificación de roadmaps creados como `docs(repo)`.

### [x] Generación de Body Lines
- [x] Generación de hasta 5 bullets relevantes.
- [x] Bullets localizados en español o inglés según el texto de entrada.
- [x] Bullets específicos para roadmap con seguimiento de progreso.
- [x] Bullets específicos para soporte bilingüe/NLP.
- [x] Bullets de validación para `compileall`, pruebas y `py_compile`.
- [x] Dedupe básico para evitar bullets repetidos.

### [x] Documentación
- [x] README actualizado con capacidades actuales.
- [x] Ejemplos de salida en español e inglés.
- [x] Roadmap actualizado con funcionalidades completadas y pendientes.

## Mejoras Futuras Pendientes

### [ ] Evaluación y Testing
- [ ] Añadir tests unitarios para `strip_markdown_noise()`.
- [ ] Añadir tests unitarios para detección de idioma.
- [ ] Añadir tests unitarios para extracción de acciones en español.
- [ ] Añadir tests unitarios para `select_commit_type()` y `detect_scope()`.
- [ ] Añadir casos de regresión para evitar que commits incrustados contaminen el resultado.
- [ ] Recalcular métricas de similitud tras las mejoras bilingües.

### [ ] Integración con Git
- [ ] Leer `git diff --stat` para detectar archivos modificados.
- [ ] Leer `git diff --name-status` para saber si un archivo fue creado, modificado o eliminado.
- [ ] Usar archivos cambiados para mejorar scopes y body lines.
- [ ] Detectar cambios en `README.md`, `Roadmap.md`, tests, código fuente y datos de ejemplos.
- [ ] Ofrecer una opción para ejecutar el commit directamente después de revisar el comando.

### [ ] Soporte Lingüístico
- [ ] Ampliar verbos y patrones en español.
- [ ] Mejorar detección de idioma para textos mixtos.
- [ ] Separar reglas por idioma en estructuras más mantenibles.
- [ ] Evaluar un etiquetador POS en español si se desea más precisión gramatical.
- [ ] Soportar variantes regionales y frases más coloquiales.

### [ ] Arquitectura y Mantenibilidad
- [ ] Separar la lógica NLP de la interfaz PyQt6.
- [ ] Crear una clase o módulo dedicado para limpieza de input.
- [ ] Crear un módulo dedicado para type/scope detection.
- [ ] Crear fixtures reutilizables con ejemplos reales.
- [ ] Evitar versionar artefactos generados como `__pycache__`.

### [ ] Interfaz de Usuario
- [ ] Mostrar el idioma detectado antes de generar el commit final.
- [ ] Permitir cambiar manualmente el idioma detectado.
- [ ] Permitir editar type/scope desde la UI antes de copiar.
- [ ] Mostrar advertencias cuando el input tenga mucho ruido o muchos bloques de código.
- [ ] Añadir vista previa separada para subject y body.

### [ ] Calidad del Commit
- [ ] Mejorar ranking de bullets por importancia.
- [ ] Detectar validaciones y pruebas aunque aparezcan en frases indirectas.
- [ ] Detectar cambios de documentación, tests y código en un mismo resumen.
- [ ] Mejorar truncado de subject para que no corte palabras.
- [ ] Generar alternativas cuando haya varias interpretaciones posibles.

---

**Última actualización:** 11 de mayo de 2026  
**Estado:** Funcional para uso básico e iteración diaria; en progreso hacia mayor precisión con tests, Git diff y más patrones bilingües.

