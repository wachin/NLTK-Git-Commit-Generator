# NLTK Git Commit Generator

A lightweight, desktop application built with **PyQt6** and **NLTK** that automatically generates standardized Git commit messages. Simply paste your change summary, and the tool uses linguistic analysis to produce a perfectly formatted Conventional Commit ready for your terminal.

## Features

- **Linguistic Analysis**: Uses `nltk` (Natural Language Toolkit) to parse grammar, extract the main action verb and target object, and construct precise commit subjects.
- **Conventional Commits Standard**: Automatically enforces the `type(scope): description` format.
- **Git Line Length Compliance**: Strictly adheres to Git best practices (≤50 characters for subjects, ≤72 characters for body lines).
- **Smart Heuristics**: Detects test counts, roadmap updates, documentation changes, and UI modifications to auto-generate structured commit bodies.
- **One-Click Copy**: Outputs a ready-to-paste multiline `git commit` command directly to your clipboard.
- **Zero AI Overhead**: Runs entirely locally with lightweight NLP models. No API keys, no heavy LLMs, no internet dependency after initial setup.

## Installation

### Debian / Ubuntu / Linux Mint
```bash
sudo apt update
sudo apt install python3-pyqt6 python3-nltk
```

### Other Linux Distributions (via pip)
```bash
pip install PyQt6 nltk
```

> 💡 **First-Run Note**: On the very first execution, the application will automatically download the required NLTK datasets (`punkt` and `averaged_perceptron_tagger`) to `~/nltk_data` (~57 MB). The terminal may appear paused for 1–3 minutes during this download. This is a one-time setup step. Subsequent launches will open the GUI instantly.

**Optional Pre-download**: To avoid the initial wait, run this once before first launch, but at the same you will need to wait the same time:

```bash
python3 -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')"
```

## Usage

1. Clone or download this repository.
2. Run the application:
   ```bash
   python3 smart_commit_nltk.py
   ```
3. Paste your change summary into the input text area.
4. Click **"Generate Commit with NLTK"**.
5. Review the formatted command and click **"Copy to Clipboard"**.
6. Paste and execute directly in your terminal.

## How It Works

Unlike AI-based generators that rely on heavy language models, this tool uses **statistical NLP** via `nltk`:
1. **Tokenization & POS Tagging**: Breaks down your input text and tags each word with its grammatical role (verb, noun, preposition, etc.).
2. **Subject Extraction**: Identifies the primary action verb and its direct object to construct a concise, meaningful subject line.
3. **Scope & Type Detection**: Uses keyword matching and grammatical context to assign the correct Conventional Commit `type` (`feat`, `fix`, `docs`) and `scope` (`app`, `ui`, `dict`, `tools`).
4. **Body Generation**: Applies project-aware heuristics to automatically append relevant bullet points (e.g., test validation counts, roadmap updates, documentation syncs).
5. **Formatting Engine**: Enforces Git's strict character limits and outputs a clean, multiline bash command.

## 📖 Example Workflow

The repository includes a comprehensive log of real-world usage demonstrating how raw developer summaries are transformed into production-ready commits. See:
👉 [`COMMIT_GENERATION_EXAMPLES.md`](COMMIT_GENERATION_EXAMPLES.md)

Each entry shows:
- The original developer summary
- The generated `git commit` command
- The linguistic & structural reasoning behind the output

## 📁 Project Structure

```
├── smart_commit_nltk.py          # Main PyQt6 application
├── COMMIT_GENERATION_EXAMPLES.md # Real-world usage examples
└── README.md                     # This file
```

## Contributing

Contributions are welcome! If you'd like to improve the linguistic rules, add new scope/type detection patterns, or enhance the UI, feel free to open an issue or submit a pull request.

## License

This project is open-source and available under the GPL 3

---
*Built for developers who value precision, speed, and clean Git history.* 🐍📦✨
```

