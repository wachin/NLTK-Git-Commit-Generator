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
- [x] Botón para limpiar el texto de entrada del usuario.
- [x] Indicador de idioma detectado: pendiente, Español o Inglés.
- [x] Selector manual de idioma: Automático, Español o Inglés.
- [x] Selectores manuales para ajustar type y scope antes de copiar.
- [x] Advertencia no intrusiva cuando el input tiene mucho ruido o bloques de código.
- [x] Área de salida con comando `git commit` multilinea.
- [x] Botón para copiar el comando al portapapeles.
- [x] Confirmación de copiado en el propio botón, sin mensaje modal.

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
- [x] Actualización de `compare_generator.py` para la firma bilingüe actual.
- [x] Recalculo de `comparison_report.json` tras las mejoras bilingües.
- [x] Registro de línea base actual: 45 ejemplos, subject similarity 0.446, body ratio 0.000.

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
- [x] README actualizado con comandos de testing y evaluación.

### [x] Evaluación y Testing Inicial
- [x] Creación de suite `unittest` para regresiones principales.
- [x] Tests para `strip_markdown_noise()`.
- [x] Tests para detección de idioma.
- [x] Tests para generación bilingüe `feat(nlp)` en español e inglés.
- [x] Test para roadmap en español como `docs(repo)`.
- [x] Test para evitar falso positivo de `ci` dentro de palabras comunes.
- [x] Test para priorizar summaries de testing/evaluación sobre términos bilingües.
- [x] Test para limpiar entrada, salida y estado del botón copiar.
- [x] Test para priorizar summaries del botón Limpiar entrada sobre menciones de tests/Roadmap.
- [x] Test para mostrar y reiniciar el idioma detectado en la interfaz.
- [x] Test para priorizar summaries de idioma detectado sobre menciones de Roadmap.
- [x] Test para forzar manualmente el idioma de generación.
- [x] Test para editar manualmente type/scope y regenerar el comando.
- [x] Test para priorizar summaries de type/scope sobre menciones de tests/Roadmap.
- [x] Test para confirmar copiado en el botón sin mensaje modal.
- [x] Test para advertencias de ruido por bloques de código y commits pegados.
- [x] Test para truncar el subject sin cortar palabras.
- [x] Ejecución exitosa de 17 tests de regresión.

### [x] Higiene de Artefactos Generados
- [x] Creación de `.gitignore` para `__pycache__/` y archivos `*.py[cod]`.

## Mejoras Futuras Pendientes

### [ ] Evaluación y Testing
- [ ] Añadir más tests unitarios para extracción de acciones en español.
- [ ] Añadir más tests unitarios para `select_commit_type()` y `detect_scope()`.
- [ ] Añadir casos de regresión para textos mixtos español/inglés.
- [ ] Añadir casos de regresión para resúmenes con varios archivos modificados.
- [ ] Definir nuevas métricas que no penalicen el límite actual de 5 bullets.
- [ ] Mejorar métricas del dataset histórico sin perder los casos bilingües recientes.

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
- [ ] Sacar del índice de Git cualquier `__pycache__` ya trackeado.

### [ ] Interfaz de Usuario
- [x] Permitir cambiar manualmente el idioma detectado.
- [x] Permitir editar type/scope desde la UI antes de copiar.
- [x] Mostrar advertencias cuando el input tenga mucho ruido o muchos bloques de código.

### [ ] Calidad del Commit
- [ ] Mejorar ranking de bullets por importancia.
- [ ] Detectar validaciones y pruebas aunque aparezcan en frases indirectas.
- [ ] Detectar menciones de documentación, tests y código dentro del texto pegado.
- [x] Mejorar truncado de subject para que no corte palabras.
- [ ] Generar alternativas cuando haya varias interpretaciones posibles.

---

**Última actualización:** 11 de mayo de 2026  
**Estado:** Funcional para uso básico e iteración diaria; ya cuenta con regresiones iniciales y evaluación del dataset. La prioridad siguiente es mejorar la calidad semántica desde el texto pegado, sin depender de integración con Git.
