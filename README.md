# NLTK Git Commit Generator

A lightweight desktop app built with **PyQt6** and **NLTK** that turns pasted change summaries into ready-to-run Conventional Commit commands.

The project is intentionally local-first: no API keys, no cloud model, and no network dependency after the initial NLTK data download. It uses language-aware tokenization, practical heuristics, and project-specific patterns to produce useful commit subjects and bullet bodies.

## Features

- **Bilingual input support**: Detects Spanish or English summaries and keeps the generated subject/body in the same language.
- **Language-aware tokenization**: Uses NLTK Punkt tokenizers for English and Spanish sentence splitting.
- **Spanish action extraction**: Understands common Spanish development phrases such as `he creado`, `actualizado`, `incluye`, `resume`, `corrige`, and `mejora`.
- **Conventional Commits format**: Generates `type(scope): subject` commands with scopes such as `nlp`, `repo`, `docs`, `ui`, `app`, `dict`, and `tools`.
- **Markdown noise filtering**: Ignores pasted fenced code blocks, embedded `git commit -m` examples, Markdown links, and quoted command output that would otherwise pollute the result.
- **Smarter type detection**: Avoids false positives such as classifying a commit as `ci` just because the letters `ci` appear inside Spanish words like `funcionalidades` or `secciones`.
- **Structured body generation**: Builds up to five high-signal bullet lines for roadmap work, bilingual NLP changes, UI work, validation, docs, and common project patterns.
- **Clipboard workflow**: Shows a multiline `git commit` command ready to copy and paste into a terminal.

## Installation

### Debian / Ubuntu / Linux Mint

```bash
sudo apt update
sudo apt install python3-pyqt6 python3-nltk
```

### Other Linux Distributions

```bash
pip install PyQt6 nltk
```

On first run, the app checks for required NLTK data and downloads missing packages:

- `punkt`
- `averaged_perceptron_tagger`

The Spanish tokenizer is included in the Punkt data package.

Optional pre-download:

```bash
python3 -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')"
```

## Usage

1. Run the app:

   ```bash
   python3 smart_commit_nltk.py
   ```

2. Paste a summary from your own notes, an assistant response, or a changelog-style paragraph.
3. Leave **Modo de idioma** on **Automático**, or choose **Español** / **Inglés** manually if the text is mixed.
4. Click **Generar Commit con NLTK**.
5. Review the generated command, detected language status, and any non-blocking noise warning.
6. Adjust **Tipo** or **Scope** if the automatic choice needs a manual correction.
7. Copy it to the clipboard and run it in your repository. The copy button confirms the action in-place, without opening a popup.

## Testing and Evaluation

Run the regression tests:

```bash
QT_QPA_PLATFORM=offscreen python3 -m unittest discover -s tests -v
```

Recalculate the example-dataset comparison report:

```bash
QT_QPA_PLATFORM=offscreen python3 commit_examples_data/compare_generator.py
```

The comparison report is written to `commit_examples_data/comparison_report.json`. The current heuristics intentionally cap generated bodies at seven bullets, so body-count metrics are not expected to match older examples that contain longer commit bodies.

## Examples

Spanish input about the bilingual NLP improvements can produce:

```bash
git commit -m "feat(nlp): agrega soporte bilingüe y corrige tipo ci" \
  -m "- Detecta el idioma de entrada para tokenización localizada" \
  -m "- Soporta verbos españoles como creado, actualizado e incluye" \
  -m "- Genera subject y body en el idioma del resumen" \
  -m "- Corrige falsos positivos de ci dentro de palabras comunes" \
  -m "- Valida la sintaxis con py_compile"
```

English input about the same kind of work can produce:

```bash
git commit -m "feat(nlp): add bilingual support and fix type detection" \
  -m "- Detect input language for localized tokenization" \
  -m "- Support Spanish verbs like creado, actualizado, and incluye" \
  -m "- Generate commit subject and body in the source language" \
  -m "- Fix false-positive ci detection inside common words" \
  -m "- Validate syntax with py_compile"
```

Spanish roadmap input can produce:

```bash
git commit -m "docs(repo): agrega roadmap con seguimiento de progreso" \
  -m "- Documenta funcionalidades completadas y progreso del proyecto" \
  -m "- Resume mejoras futuras para Git, ML, UI, pruebas y multilenguaje" \
  -m "- Organiza el roadmap con secciones claras de estado" \
  -m "- Incluye áreas de documentación, comunidad y testing" \
  -m "- Usa checkboxes para visualizar tareas completadas y pendientes"
```

## How It Works

1. **Noise cleanup**: Removes Markdown fences, embedded commit commands, copied `-m` lines, Markdown link targets, and other assistant/terminal noise.
2. **Language detection**: Scores Spanish and English markers to choose `es` or `en`.
3. **Sentence splitting**: Uses NLTK sentence tokenization with the detected language.
4. **Action extraction**: Applies English POS tagging and rule-based Spanish patterns to find the main action and object.
5. **Type/scope selection**: Classifies the change into Conventional Commit type/scope using whole-word matching and project-aware keywords.
6. **Body generation**: Adds concise, localized bullets for detected change categories.
7. **Formatting**: Keeps the subject short and emits a shell-ready multiline `git commit` command.

## Project Structure

```text
├── smart_commit_nltk.py          # Main PyQt6 application
├── Roadmap.md                    # Current progress and planned improvements
├── COMMIT_GENERATION_EXAMPLES.md # Real-world examples and expected outputs
├── commit_examples_data/         # Parsed JSON/SQLite examples and comparison tools
├── tests/                        # Regression tests for NLP heuristics
└── README.md                     # Project documentation
```

## Current Limitations

- Spanish grammar support is rule-based. NLTK Punkt can split Spanish sentences, but this project does not currently use a full Spanish POS tagger.
- The generator is heuristic, not a large language model. It improves through specific patterns, examples, and evaluation data.
- It works best with summaries that describe concrete changes, files, features, validation, and user-visible behavior.

## Contributing

Good contributions include:

- Adding more Spanish and English phrase patterns.
- Expanding `commit_examples_data` with real summaries and expected commits.
- Improving comparison metrics.
- Adding tests for language detection, Markdown cleanup, type/scope selection, and body generation.

## License

This project is open-source and available under GPL 3.
