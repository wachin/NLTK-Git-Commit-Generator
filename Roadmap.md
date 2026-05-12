# Roadmap: NLTK Git Commit Generator

Este roadmap documenta el progreso del generador de commits inteligente basado en NLTK. El objetivo del proyecto es acercarse al estilo de commits que suele producir una IA avanzada, pero manteniendo una implementación local, ligera y explicable.

## Estado Actual para Retomar

El programa ya es funcional para uso diario: toma texto pegado en español o inglés, limpia ruido de Markdown/comandos, detecta idioma, propone `type(scope)`, genera subject y body localizado, permite corregir manualmente idioma/type/scope y copia el comando sin ventana modal.

La línea de mejora actual no es integrar con Git, sino mejorar la calidad semántica desde el texto pegado, imitando mejor los commits ricos que devuelve una IA.

### Últimos Avances Importantes
- [x] Eliminada la vista previa separada de subject/body porque no aportaba al flujo.
- [x] Añadido truncado inteligente de subject con límites de palabra.
- [x] Corregida la priorización para que cambios semánticos no queden ocultos por menciones secundarias de tests o documentación.
- [x] Añadida detección general de validaciones indirectas como `Resultado: 20 tests OK`, `suite completa pasa`, `py_compile`, `compileall`, `unittest` y `pytest`.
- [x] Añadida detección de menciones de archivos para clasificar código, tests, documentación, reportes y configuración.
- [x] Ampliado el body de 5 a 7 bullets para conservar detalles importantes.
- [x] Añadido ranking de bullets para poner primero cambios principales, luego tests/docs/reportes y dejar validación al final.
- [x] Suite actual: 20 tests de regresión pasando.

### Ejemplo de Calidad Actual

Entrada resumida:

```text
Mejoré la detección de menciones de archivos dentro del texto pegado.
Actualicé smart_commit_nltk.py, tests/test_smart_commit_nltk.py, README.md,
Roadmap.md y commit_examples_data/comparison_report.json.
Resultado: 19 tests OK.
```

Salida esperada actual:

```bash
git commit -m "feat(nlp): mejora detección de menciones de archivos" \
  -m "- Actualiza lógica de código mencionada en el resumen" \
  -m "- Cubre cambios con tests de regresión" \
  -m "- Actualiza documentación mencionada en el resumen" \
  -m "- Actualiza datos o reportes de evaluación" \
  -m "- Validación: 19 tests pass"
```

### Comandos Útiles

```bash
QT_QPA_PLATFORM=offscreen python3 -m unittest discover -s tests -v
```

```bash
QT_QPA_PLATFORM=offscreen python3 commit_examples_data/compare_generator.py
```

Nota: `__pycache__/smart_commit_nltk.cpython-311.pyc` puede aparecer modificado porque ya está trackeado por Git. `.gitignore` evita nuevos artefactos, pero queda pendiente sacarlo del índice.

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
- [x] Generación de hasta 7 bullets relevantes.
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
- [x] Test para priorizar summaries de eliminación de vista previa y truncado sobre menciones de tests.
- [x] Test para detectar validaciones indirectas como `suite completa pasa: 18 tests OK`.
- [x] Test para detectar menciones de código, tests, documentación y reportes.
- [x] Test para ordenar bullets por importancia y podar documentación genérica duplicada.
- [x] Ejecución exitosa de 20 tests de regresión.

### [x] Higiene de Artefactos Generados
- [x] Creación de `.gitignore` para `__pycache__/` y archivos `*.py[cod]`.

## Mejoras Futuras Pendientes

### Siguiente Sesión Recomendada
- [ ] Probar el programa con el texto del último resumen generado por Codex y comparar contra el commit que daría una IA.
- [ ] Si el subject sale demasiado genérico, añadir una regla específica de subject antes de tocar el body.
- [ ] Si el body sale con bullets buenos pero mal ordenados, ajustar `rank_body_lines()`.
- [ ] Si se pierde información útil del texto pegado, revisar primero `clean_input()`.
- [ ] Después de cada mejora, añadir o ajustar un test de regresión en `tests/test_smart_commit_nltk.py`.
- [ ] Ejecutar siempre `QT_QPA_PLATFORM=offscreen python3 -m unittest discover -s tests -v`.

### [ ] Evaluación y Testing
- [ ] Añadir más tests unitarios para extracción de acciones en español.
- [ ] Añadir más tests unitarios para `select_commit_type()` y `detect_scope()`.
- [ ] Añadir casos de regresión para textos mixtos español/inglés.
- [ ] Añadir casos de regresión para resúmenes con varios archivos modificados.
- [ ] Definir nuevas métricas que no penalicen el límite actual de 7 bullets.
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
- [x] Mejorar ranking de bullets por importancia.
- [x] Detectar validaciones y pruebas aunque aparezcan en frases indirectas.
- [x] Detectar menciones de documentación, tests y código dentro del texto pegado.
- [x] Mejorar truncado de subject para que no corte palabras.
- [x] Ampliar el body hasta 7 bullets para conservar cambios relevantes y validación.
- [x] Priorizar mejoras semánticas combinadas sobre menciones secundarias de tests/documentación.
- [ ] Generar alternativas cuando haya varias interpretaciones posibles.

---

**Última actualización:** 11 de mayo de 2026  
**Estado:** Funcional para uso básico e iteración diaria; ya cuenta con regresiones iniciales y evaluación del dataset. La prioridad siguiente es mejorar la calidad semántica desde el texto pegado, sin depender de integración con Git.
