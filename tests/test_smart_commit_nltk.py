import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PyQt6.QtWidgets import QApplication

from smart_commit_nltk import NLPCommitGenerator


APP = QApplication.instance() or QApplication([])


class SmartCommitGeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generator = NLPCommitGenerator()

    def render_command(self, text):
        self.generator.input_text.setPlainText(text)
        self.generator.generate_commit()
        return self.generator.output_text.toPlainText()

    def test_strip_markdown_noise_removes_embedded_commits(self):
        text = """Resumen útil.

```bash
git commit -m "docs(repo): bad embedded subject" \\
  -m "- Bad embedded body"
python3 -m py_compile smart_commit_nltk.py
```

Ahora detecta idioma y genera commits mejores.
"""
        cleaned = self.generator.strip_markdown_noise(text)

        self.assertNotIn('git commit -m', cleaned)
        self.assertNotIn('-m "- Bad embedded body"', cleaned)
        self.assertIn('Verifiqué con python3 -m py_compile smart_commit_nltk.py.', cleaned)

    def test_detect_language_spanish_and_english(self):
        spanish = 'He creado soporte bilingüe para detectar español e inglés.'
        english = 'Created bilingual support to detect Spanish and English input.'

        self.assertEqual(self.generator.detect_language(spanish), 'es')
        self.assertEqual(self.generator.detect_language(english), 'en')

    def test_spanish_bilingual_summary_generates_feat_nlp(self):
        text = """Listo, le metí una mejora fuerte a [smart_commit_nltk.py](/tmp/smart_commit_nltk.py).
Ahora detecta si el texto está en español o inglés, usa tokenización por idioma,
entiende verbos españoles como `he creado`, `actualizado`, `incluye`, `resume`,
y genera el subject/body en el mismo idioma del texto de entrada.

```bash
git commit -m "docs(repo): agrega roadmap con seguimiento de progreso" \\
  -m "- Documenta funcionalidades completadas"
python3 -m py_compile smart_commit_nltk.py
```

También corregí el bug que hacía que saliera `ci(docs)` por encontrar las letras
`ci` dentro de palabras como “funcionalidades” o “secciones”.
"""
        command = self.render_command(text)

        self.assertIn('git commit -m "feat(nlp): agrega soporte bilingüe y corrige tipo ci"', command)
        self.assertIn('-m "- Detecta el idioma de entrada para tokenización localizada"', command)
        self.assertIn('-m "- Corrige falsos positivos de ci dentro de palabras comunes"', command)
        self.assertIn('-m "- Valida la sintaxis con py_compile"', command)
        self.assertNotIn('docs(repo): agrega roadmap', command)

    def test_english_bilingual_summary_generates_feat_nlp(self):
        text = """Updated smart_commit_nltk.py with bilingual support.
It detects Spanish or English language input, uses localized tokenization,
supports Spanish verbs, and fixes false-positive ci type detection.
Validated with py_compile.
"""
        command = self.render_command(text)

        self.assertIn('git commit -m "feat(nlp): add bilingual support and fix type detection"', command)
        self.assertIn('-m "- Detect input language for localized tokenization"', command)
        self.assertIn('-m "- Fix false-positive ci detection inside common words"', command)

    def test_roadmap_creation_in_spanish_generates_docs_repo(self):
        text = """He creado el archivo Roadmap.md en la raíz del proyecto.
Este documento resume el progreso realizado, marca funcionalidades completadas
y deja pendientes las mejoras futuras para Git, ML, UI, testing y multilenguaje.
"""
        command = self.render_command(text)

        self.assertIn('git commit -m "docs(repo): agrega roadmap con seguimiento de progreso"', command)
        self.assertIn('-m "- Documenta funcionalidades completadas y progreso del proyecto"', command)

    def test_ci_detection_uses_whole_word_matching(self):
        text = 'He creado funcionalidades y secciones nuevas en Roadmap.md.'
        verb, obj, _language = self.generator.analyze_with_nltk(text)

        self.assertEqual(self.generator.select_commit_type(text, verb, obj), 'docs')

    def test_clear_input_button_resets_input_output_and_copy_state(self):
        self.generator.input_text.setPlainText('He creado Roadmap.md.')
        self.generator.output_text.setPlainText('git commit -m "docs(repo): test"')
        self.generator.copy_btn.setEnabled(True)
        self.generator.language_status_label.setText('Idioma detectado: Español')

        self.generator.clear_input_text()

        self.assertEqual(self.generator.input_text.toPlainText(), '')
        self.assertEqual(self.generator.output_text.toPlainText(), '')
        self.assertFalse(self.generator.copy_btn.isEnabled())
        self.assertEqual(self.generator.language_status_label.text(), 'Idioma detectado: pendiente')

    def test_language_status_updates_after_generating_commit(self):
        self.render_command('He creado Roadmap.md con tareas completadas.')
        self.assertEqual(self.generator.language_status_label.text(), 'Idioma detectado: Español')

        self.render_command('Created Roadmap.md with completed tasks.')
        self.assertEqual(self.generator.language_status_label.text(), 'Idioma detectado: Inglés')

    def test_clear_input_summary_takes_priority_over_tests_and_roadmap(self):
        text = """Listo, implementé el botón **“Limpiar entrada”** en [smart_commit_nltk.py](/tmp/smart_commit_nltk.py).

Al pulsarlo:

- borra el texto de entrada
- borra el commit generado anterior
- desactiva el botón de copiar
- devuelve el foco al cuadro de entrada

También añadí un test en [tests/test_smart_commit_nltk.py](/tmp/tests/test_smart_commit_nltk.py)
y actualicé [Roadmap.md](/tmp/Roadmap.md) marcando la mejora como completada.

Resultado: **8 tests OK**.
"""
        command = self.render_command(text)

        self.assertIn('git commit -m "feat(ui): agrega botón Limpiar entrada en la interfaz"', command)
        self.assertIn('-m "- Implementa lógica para limpiar entrada y commit generado"', command)
        self.assertIn('-m "- Desactiva el botón de copiar al limpiar la entrada"', command)
        self.assertIn('-m "- Validación: 8 tests pass en entorno offscreen"', command)
        self.assertNotIn('test(repo): agrega suite', command)

    def test_language_status_summary_takes_priority_over_roadmap(self):
        text = """Hecho. Quité el enfoque de “integración con Git” del Roadmap.
También continué con una mejora del programa: añadí en la interfaz una etiqueta de estado
que muestra el idioma detectado:

- `Idioma detectado: pendiente`
- `Idioma detectado: Español`
- `Idioma detectado: Inglés`

Al generar el commit se actualiza automáticamente, y al usar **Limpiar entrada** vuelve a `pendiente`.
Actualicé [Roadmap.md](/tmp/Roadmap.md) marcando como hecho el idioma detectado.
También añadí test de regresión.
Resultado: **10 tests OK**.
"""
        command = self.render_command(text)

        self.assertIn('git commit -m "feat(ui): agrega indicador de idioma detectado"', command)
        self.assertIn('-m "- Presenta estados Pendiente, Español e Inglés"', command)
        self.assertIn('-m "- Enfoca el roadmap en calidad semántica sin integración Git"', command)
        self.assertIn('-m "- Validación: 10 tests pass en entorno offscreen"', command)
        self.assertNotIn('actualiza roadmap del proyecto', command)

    def test_testing_evaluation_summary_takes_priority_over_bilingual_terms(self):
        text = """Continué con las mejoras del Roadmap y dejé una primera base de testing/evaluación.

- Añadí [tests/test_smart_commit_nltk.py](/tmp/tests/test_smart_commit_nltk.py) con 6 regresiones.
- Actualicé [commit_examples_data/compare_generator.py](/tmp/compare_generator.py) para la nueva firma bilingüe.
- Recalculé [comparison_report.json](/tmp/comparison_report.json).
- Añadí [.gitignore](/tmp/.gitignore) para `__pycache__/`.
- Actualicé [README.md](/tmp/README.md) con comandos de testing/evaluación.
- Actualicé [Roadmap.md](/tmp/Roadmap.md) marcando estas tareas completadas.
- Afiné `clean_input()` para no perder frases en inglés con `detects`, `supports`, `fixes`, `validated`.

La línea base actual quedó: 45 ejemplos, subject similarity `0.446`, body ratio `0.000`.
"""
        command = self.render_command(text)

        self.assertIn('git commit -m "test(repo): agrega suite de regresión y baseline de evaluación"', command)
        self.assertIn('-m "- Añade test_smart_commit_nltk.py con 6 regresiones principales"', command)
        self.assertIn('-m "- Actualiza compare_generator.py para la firma bilingüe"', command)
        self.assertIn('-m "- Establece baseline: 0.446 de similitud de subject"', command)
        self.assertNotIn('feat(nlp): agrega', command)


if __name__ == '__main__':
    unittest.main()
