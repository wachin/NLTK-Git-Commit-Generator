# Roadmap: NLTK Git Commit Generator

Este roadmap documenta el desarrollo del generador de commits inteligente basado en NLTK, que analiza texto de cambios y genera commits convencionales de alta calidad. El proyecto busca imitar el estilo de commits de una IA avanzada, evitando ruido y enfocándose en cambios relevantes.

## Funcionalidades Completadas

### [x] Configuración Inicial del Proyecto
- [x] Creación del repositorio y estructura básica.
- [x] Instalación de dependencias (NLTK, PyQt6 para GUI).
- [x] Configuración de entorno Python (venv o similar).

### [x] Dataset de Ejemplos de Commits
- [x] Creación de `COMMIT_GENERATION_EXAMPLES.md` con ejemplos de commits buenos y malos.
- [x] Desarrollo de `parse_commit_examples.py` para parsear ejemplos en JSON/SQLite.
- [x] Validación del dataset con 45 entradas procesadas correctamente.

### [x] Implementación del Generador Base
- [x] Desarrollo de `smart_commit_nltk.py` con análisis NLP usando NLTK.
- [x] Implementación de tokenización, POS tagging y extracción de frases.
- [x] Heurísticas iniciales para extraer verbos/objetos y scoring de frases.

### [x] Sistema de Comparación y Evaluación
- [x] Creación de `compare_generator.py` para comparar commits generados vs. esperados.
- [x] Métricas de similitud (subject y body) con reporte JSON.
- [x] Mejora inicial de similitud de 0.453 a 0.528.

### [x] Mejoras en Filtrado de Ruido
- [x] Implementación de `clean_input()` para eliminar comandos de terminal, frases conversacionales y contenido irrelevante.
- [x] Aplicación del filtro en análisis de subject y generación de body.

### [x] Refinamiento de Clasificación de Frases
- [x] Mejora de `is_commitworthy_sentence()` para detectar frases con verbos de acción sin requerir pronombres.
- [x] Filtros para evitar frases descriptivas, de validación o cortas.

### [x] Optimización de Subject y Scope
- [x] Refinamiento de `pick_best_sentence()` y `score_sentence_for_subject()` para favorecer frases con verbos al inicio.
- [x] Mejora en `detect_scope()` para clasificar scopes (ui, app, docs, etc.) más precisamente.
- [x] Aumento de similitud del subject a 0.509.

### [x] Generación de Body Lines Mejorada
- [x] Modificación de `generate_body_lines()` para usar frases commit-worthy formateadas.
- [x] Limitación a 5 bullets máximo, con capitalización y limpieza.
- [x] Integración con bullets hardcoded específicos para casos comunes.

### [x] Integración con Conventional Commits
- [x] Soporte para tipos (feat, fix, docs) y scopes automáticos.
- [x] Formato de comandos Git listos para ejecutar.

## Mejoras Futuras Pendientes

### [ ] Integración con Git
- [ ] Análisis automático de `git diff` para extraer cambios relevantes.
- [ ] Generación de commits basada en diffs en lugar de texto manual.
- [ ] Validación de commits generados contra el estado del repo.

### [ ] Mejora en Inteligencia Artificial
- [ ] Uso de modelos de ML (e.g., BERT) para mejor comprensión semántica.
- [ ] Entrenamiento con dataset más grande para predicción de tipos/scopes.
- [ ] Detección de intenciones más precisa (e.g., refactor vs. feature).

### [ ] Soporte Multilenguaje
- [ ] Extensión a otros lenguajes de programación (JavaScript, Java, etc.).
- [ ] Adaptación de heurísticas para diferentes convenciones de commits.
- [ ] Internacionalización de mensajes (soporte para español, etc.).

### [ ] Interfaz de Usuario Avanzada
- [ ] Mejora de la GUI con PyQt6 para previsualización de commits.
- [ ] Integración con editores (VS Code extension).
- [ ] Modo batch para procesar múltiples cambios.

### [ ] Validación y Testing
- [ ] Suite de tests unitarios para funciones clave.
- [ ] Validación automática de formato de conventional commits.
- [ ] Benchmarking contra otros generadores de commits.

### [ ] Características Avanzadas
- [ ] Detección de breaking changes.
- [ ] Sugerencias de co-autores basadas en cambios.
- [ ] Integración con CI/CD para commits automáticos.
- [ ] Modo interactivo para edición manual de commits generados.

### [ ] Documentación y Comunidad
- [ ] Documentación completa en README.md con ejemplos.
- [ ] Tutoriales y guías de uso.
- [ ] Contribución abierta y issues en GitHub.

---

**Última actualización:** 11 de mayo de 2026  
**Similitud actual:** Subject 0.509, Body ratio 0.039  
**Estado:** Funcional para uso básico, con mejoras iterativas en progreso.</content>
<filePath>README.md