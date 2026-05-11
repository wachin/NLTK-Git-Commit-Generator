import sys
import re
import time
import threading
import contextlib
import io
import nltk
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QTextEdit, QPushButton, QLabel, QMessageBox,
                             QHBoxLayout, QGroupBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QClipboard

# ==========================================
# 🔄 MEJORA: Descarga con Spinner y Feedback
# ==========================================
def ensure_nltk_data():
    required_packages = [
        ('punkt', 'tokenizers/punkt'),
        ('averaged_perceptron_tagger', 'taggers/averaged_perceptron_tagger')
    ]

    missing = []
    for pkg, path in required_packages:
        try:
            nltk.data.find(path)
        except LookupError:
            missing.append(pkg)

    if not missing:
        return

    print("\n📦 First-time setup: Downloading NLTK language models (~57 MB)...")
    print("⏳ This is a one-time process. Depending on your connection, it may take 2-10 minutes.")
    print("🔄 The terminal may appear idle, but the download is running in the background...\n")

    # Spinner animation thread
    stop_spinner = threading.Event()
    def spinner():
        symbols = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        idx = 0
        while not stop_spinner.is_set():
            sys.stdout.write(f"\r  {symbols[idx % len(symbols)]} Downloading and extracting data...")
            sys.stdout.flush()
            time.sleep(0.15)
            idx += 1
        sys.stdout.write("\r  ✅ Download complete! Launching application...\n")
        sys.stdout.flush()

    spinner_thread = threading.Thread(target=spinner)
    spinner_thread.start()

    # Download thread (suppresses NLTK's own print statements)
    download_done = threading.Event()
    def download_task():
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                for pkg in missing:
                    nltk.download(pkg, quiet=True)
        except Exception as e:
            print(f"\n❌ Error downloading NLTK data: {e}")
            sys.exit(1)
        download_done.set()

    download_thread = threading.Thread(target=download_task)
    download_thread.start()
    download_thread.join()

    stop_spinner.set()
    spinner_thread.join()

# Ejecutar verificación antes de iniciar la GUI
ensure_nltk_data()

class NLPCommitGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Generador de Commits - NLTK Enhanced")
        self.setGeometry(100, 100, 900, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        instr_label = QLabel("Pega aquí el resumen. El sistema usará NLTK para analizar la gramática:")
        instr_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(instr_label)

        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Ejemplo: We pushed the Pianola work into real interaction...")
        self.input_text.setFont(QFont("Courier New", 9))
        layout.addWidget(self.input_text)

        self.generate_btn = QPushButton("Generar Commit con NLTK")
        self.generate_btn.clicked.connect(self.generate_commit)
        self.generate_btn.setStyleSheet(
            "QPushButton { background-color: #673AB7; color: white; padding: 12px; font-weight: bold; font-size: 14px; }"
            "QPushButton:hover { background-color: #512DA8; }"
        )
        layout.addWidget(self.generate_btn)

        output_group = QGroupBox("Comando Git Generado:")
        output_layout = QVBoxLayout()

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Courier New", 10))
        self.output_text.setStyleSheet("background-color: #2b2b2b; color: #f8f8f2;")
        output_layout.addWidget(self.output_text)

        btn_layout = QHBoxLayout()
        self.copy_btn = QPushButton("Copiar al Portapapeles")
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        self.copy_btn.setEnabled(False)
        self.copy_btn.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; padding: 8px; font-weight: bold; }"
        )
        btn_layout.addWidget(self.copy_btn)

        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        layout.addLayout(btn_layout)

    def clean_summary_text(self, text):
        text = re.sub(r'\[.*?\]', ' ', text)
        text = text.replace('..', '.')
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def extract_object_phrase(self, phrase):
        phrase = re.sub(r'\[.*?\]', ' ', phrase)
        phrase = phrase.replace('-', ' ')
        phrase = phrase.replace('_', ' ')
        phrase = re.sub(r'([a-z])([A-Z])', r'\1 \2', phrase)
        phrase = re.sub(r'\s+', ' ', phrase).strip()
        if not phrase:
            return ""

        words = nltk.word_tokenize(phrase)
        tagged = nltk.pos_tag(words)

        obj_words = []
        started = False
        stop_tags = ('IN', 'CC', 'TO', 'PRP', 'PRP$', 'WDT', 'WP', 'WP$', 'WRB', 'DT')
        allowed_prefixes = ('NN', 'JJ', 'CD', 'VBG')

        for word, tag in tagged:
            lower = word.lower()
            if not started:
                if any(tag.startswith(prefix) for prefix in allowed_prefixes) or lower in {
                    'api', 'ui', 'ux', 'cli', 'db', 'sql', 'html', 'css', 'javascript', 'python', 'java', 'json', 'yaml', 'xml',
                    'service', 'endpoint', 'query', 'schema', 'migration', 'token', 'auth', 'password', 'session', 'cache',
                    'pipeline', 'dashboard', 'widget', 'plugin', 'extension', 'module', 'component', 'router', 'layout', 'dialog',
                    'window', 'view', 'form', 'button', 'menu', 'help', 'guide', 'documentation', 'roadmap', 'readme', 'tests',
                    'coverage', 'validation'
                }:
                    obj_words.append(lower)
                    started = True
                continue

            if tag.startswith(stop_tags) or lower in {',', '.', ';', ':', ')', '('}:
                break
            if any(tag.startswith(prefix) for prefix in allowed_prefixes) or lower in {
                'and', 'for', 'with', 'to', 'from', 'by', 'of', 'on', 'in', 'as'
            }:
                obj_words.append(lower)
            else:
                break

        cleaned = " ".join(obj_words).strip().rstrip(',.')
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned

    def extract_action_phrase(self, sentence):
        sentence = self.clean_summary_text(sentence)
        if not sentence:
            return None, None

        sentence_lower = sentence.lower()
        sentence_lower = sentence_lower.replace("’", "'")

        special_patterns = [
            (r'\bwe\s+got\s+(.+?)\s+over the line', 'add'),
            (r'\bwe\s+landed\s+(.+?)\s+with', 'add'),
            (r'\bwe\s+landed\s+(.+?)$', 'add'),
            (r'\bwe\s+pushed\s+(.+?)\s+from', 'update'),
            (r'\bwe\s+pushed\s+(.+?)$', 'update'),
            (r'\bwe\s+carried\s+(.+?)\s+one step further', 'add'),
            (r'\bwe\s+kept\s+(.+?)\s+moving', 'add'),
            (r'\bwe\s+made\s+(.+?)\s+much nicer to use', 'improve'),
            (r'\bwe\s+added\s+real\s+(.+?)(?:\s+for|\s+in|\s+with|\s+and|\.|$)', 'add'),
        ]

        for pattern, action in special_patterns:
            match = re.search(pattern, sentence_lower, re.IGNORECASE)
            if match:
                obj = self.extract_object_phrase(match.group(1))
                if obj:
                    return action, obj

        verb_map = {
            'added': 'add', 'create': 'add', 'created': 'add', 'implement': 'add', 'implemented': 'add', 'introduced': 'add',
            'built': 'add', 'landed': 'add', 'pushed': 'update', 'moved': 'move', 'refactored': 'refactor',
            'cleaned': 'refactor', 'updated': 'update', 'changed': 'update', 'modified': 'update',
            'fixed': 'fix', 'corrected': 'fix', 'resolved': 'fix', 'improved': 'improve', 'made': 'improve',
            'replaced': 'replace', 'sent': 'send', 'applied': 'apply', 'removed': 'remove', 'deleted': 'remove',
            'restored': 'restore', 'renamed': 'rename', 'merged': 'merge', 'optimized': 'optimize',
            'documented': 'doc', 'formatted': 'format', 'configured': 'configure'
        }

        found = re.search(r"\b(added|created|implemented|introduced|built|landed|pushed|moved|refactored|cleaned|updated|changed|modified|fixed|resolved|corrected|improved|made|replaced|sent|applied|removed|deleted|restored|renamed|merged|optimized|documented|formatted|configured)\b", sentence_lower)
        if found:
            verb = found.group(1)
            action = verb_map.get(verb, verb)
            tail = sentence[found.end():]
            obj = self.extract_object_phrase(tail)
            if obj:
                return action, obj

        words = nltk.word_tokenize(sentence)
        tagged = nltk.pos_tag(words)
        auxiliaries = {'be', 'have', 'do', 'let', 'get', 'got', 'make', 'makes', 'made', 'is', 'are', 'was', 'were', 'will', 'would', 'can', 'could', 'should', 'may', 'might'}
        for index, (word, tag) in enumerate(tagged):
            if tag.startswith('VB') and word.lower() not in auxiliaries:
                verb = word.lower()
                noun_phrase = self.extract_object_phrase(' '.join(w for w, _ in tagged[index + 1:]))
                if noun_phrase:
                    return verb_map.get(verb, verb), noun_phrase

        return None, None

    def is_commitworthy_sentence(self, sentence):
        normalized = sentence.lower()
        if re.search(r"\b(we|i)\s+(added|implemented|created|introduced|built|landed|pushed|moved|refactored|cleaned|updated|changed|modified|fixed|resolved|corrected|enhanced|extended|replaced|improved|made)\b", normalized):
            return True
        if re.search(r"\b(it|this|that)\s+(updates|now|shows|supports|uses|sends)\b", normalized):
            return False
        return False

    def pick_best_sentence(self, text):
        sentences = nltk.sent_tokenize(text)
        candidates = []
        for sentence in sentences:
            content = sentence.strip()
            if len(content) < 10:
                continue
            normalized = content.lower()
            if normalized.startswith(('in [', 'verification', 'current', 'test', 'tests', 'compileall', 'and ', 'but ', 'also ')):
                continue
            candidates.append(content)

        for sentence in candidates:
            action, obj = self.extract_action_phrase(sentence)
            if action and obj:
                return sentence

        return candidates[0] if candidates else text.strip()

    def analyze_with_nltk(self, text):
        normalized = self.clean_summary_text(text)
        subject_verb, subject_obj = self.extract_action_phrase(normalized)

        if not subject_verb or not subject_obj:
            best_sentence = self.pick_best_sentence(normalized)
            subject_verb, subject_obj = self.extract_action_phrase(best_sentence)

        if not subject_verb:
            subject_verb = 'update'
        if not subject_obj:
            subject_obj = 'project'

        subject_verb = subject_verb.lower()
        subject_obj = subject_obj.lower()

        if subject_verb == 'got' and subject_obj:
            subject_verb = 'add'
        if subject_verb == 'made':
            subject_verb = 'improve'

        return subject_verb, subject_obj

    def detect_scope(self, text):
        text_lower = text.lower()
        if any(k in text_lower for k in ['readme', 'roadmap', 'docs', 'documentation', '.md', '.rst', 'changelog', 'guide', 'help']):
            return 'docs'
        if any(k in text_lower for k in ['test', 'tests', 'unittest', 'pytest', 'ci', 'coverage', 'validation', 'spec', 'mock']):
            return 'test'
        if any(k in text_lower for k in ['ui', 'ux', 'dialog', 'window', 'button', 'menu', 'layout', 'style', 'css', 'html', 'frontend', 'screen', 'panel', 'view', 'toolbar']):
            return 'ui'
        if any(k in text_lower for k in ['settings', 'playback', 'midi', 'database', 'db', 'api', 'endpoint', 'server', 'client', 'application', 'module', 'service', 'backend', 'frontend', '.py', '.js', '.ts', '.java', '.go', '.rs', '.cpp', '.c', '.cs', '.swift']):
            return 'app'
        return 'app'

    def generate_body_lines(self, text):
        text_lower = text.lower()
        bullets = []
        seen = set()

        def add_bullet(line):
            clean_line = re.sub(r'\s+', ' ', line).strip()
            if clean_line.lower() not in seen:
                bullets.append(clean_line)
                seen.add(clean_line.lower())

        if any(k in text_lower for k in ['roadmap', 'readme', 'docs', 'documentation', '.md', '.rst', 'changelog', 'guide', 'help']):
            add_bullet('- Update documentation and project notes')
        if any(k in text_lower for k in ['test', 'tests', 'unittest', 'pytest', 'coverage', 'ci', 'validation', 'spec', 'mock']):
            add_bullet('- Add or update test coverage and validation checks')
        if any(k in text_lower for k in ['refactor', 'cleanup', 'cleaned', 'formatted']):
            add_bullet('- Refactor code for readability and maintainability')
        if any(k in text_lower for k in ['perf', 'optimiz', 'speed', 'latency', 'memory']):
            add_bullet('- Improve performance and resource usage')
        if any(k in text_lower for k in ['auth', 'login', 'session', 'token', 'security', 'encrypt', 'password']):
            add_bullet('- Improve authentication and security handling')
        if re.search(r'\b(fix|fixed|resolve|resolved|correct|corrected|bug|issue|patch)\b', text_lower):
            add_bullet('- Fix bugs and edge cases')

        test_match = re.search(r'(?:full\s+unittest\s+suite\s+passed[:\s]+)?(\d+)\s+tests\s+(?:OK|passed)', text, re.IGNORECASE)
        if test_match:
            add_bullet(f'- Validation: compileall OK, {test_match.group(1)} tests pass')
        elif 'compileall' in text_lower:
            add_bullet('- Validation: compileall OK')

        def is_similar_to_existing(obj_text):
            obj_words = [w for w in re.sub(r'[^a-z0-9 ]', ' ', obj_text.lower()).split() if len(w) > 2]
            if not obj_words:
                return False
            for existing in bullets:
                existing_lower = existing.lower()
                match_count = sum(1 for w in obj_words if w in existing_lower)
                if match_count >= max(2, len(obj_words) // 2):
                    return True
            return False

        for sentence in nltk.sent_tokenize(text):
            candidate = sentence.strip()
            if len(candidate) < 12:
                continue
            action, obj = self.extract_action_phrase(candidate)
            if action and obj and not is_similar_to_existing(obj):
                action_word = action if action != 'add' else 'Add'
                bullet = f'- {action_word.capitalize()} {obj}'
                add_bullet(bullet)
            if len(bullets) >= 5:
                break

        if not bullets:
            add_bullet('- Implement feature enhancements and improvements')

        return bullets

    def generate_commit(self):
        text = self.input_text.toPlainText()
        if not text.strip():
            QMessageBox.warning(self, "Advertencia", "Por favor pega el texto primero.")
            return

        try:
            verb, obj = self.analyze_with_nltk(text)
            scope = self.detect_scope(text)
            subject = f"{verb} {obj}"
            if len(subject) > 50:
                subject = subject[:47] + "..."

            commit_type = "feat"
            if verb == "fix": commit_type = "fix"
            elif verb in ["update", "doc"]: commit_type = "docs"

            body_lines = self.generate_body_lines(text)
            cmd_parts = [f'git commit -m "{commit_type}({scope}): {subject}"']
            for line in body_lines:
                if len(line) > 72: line = line[:69] + "..."
                cmd_parts.append(f'  -m "{line}"')

            final_command = " \\\n".join(cmd_parts)
            self.output_text.setText(final_command)
            self.copy_btn.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error analizando con NLTK: {str(e)}")

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.output_text.toPlainText())
        QMessageBox.information(self, "Copiado", "Comando copiado al portapapeles.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NLPCommitGenerator()
    window.show()
    sys.exit(app.exec())
