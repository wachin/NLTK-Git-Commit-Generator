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
        phrase = phrase.replace('->', ' -> ')
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
        allowed_prefixes = ('NN', 'JJ', 'CD', 'VBG', 'NNP', 'NNS')
        generic_start = {'the', 'a', 'an', 'this', 'that', 'these', 'those', 'new', 'real', 'useful', 'actual', 'existing', 'same', 'shared', 'direct', 'first', 'initial', 'basic', 'small', 'genuine', 'local', 'localized'}

        for word, tag in tagged:
            lower = word.lower()
            if not started:
                if lower in generic_start:
                    continue
                if any(tag.startswith(prefix) for prefix in allowed_prefixes) or lower in {
                    'api', 'ui', 'ux', 'cli', 'db', 'sql', 'html', 'css', 'javascript', 'python', 'java', 'json', 'yaml', 'xml',
                    'service', 'endpoint', 'query', 'schema', 'migration', 'token', 'auth', 'password', 'session', 'cache',
                    'pipeline', 'dashboard', 'widget', 'plugin', 'extension', 'module', 'component', 'router', 'layout', 'dialog',
                    'window', 'view', 'form', 'button', 'menu', 'help', 'guide', 'documentation', 'roadmap', 'readme', 'tests',
                    'coverage', 'validation', 'lyrics', 'channels', 'pianola', 'program', 'volume', 'midi', 'preferences', 'settings',
                    'encoding', 'font', 'copy', 'print', 'fullscreen', 'track', 'tabs', 'color', 'label', 'keyboard', 'action', 'toggle', 'selector', 'dialog', 'spinbox', 'combo', 'combobox', 'panel', 'mode'
                } or lower == '->':
                    obj_words.append(lower)
                    started = True
                continue

            if tag.startswith(stop_tags) or lower in {',', '.', ';', ':', ')', '(', '``', "''"}:
                break
            if any(tag.startswith(prefix) for prefix in allowed_prefixes) or lower in {'and', 'for', 'with', 'to', 'from', 'by', 'of', 'on', 'in', 'as', '->', '>'}:
                obj_words.append(lower)
            else:
                break

        cleaned = " ".join(obj_words).strip().rstrip(',.')
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned

    def score_sentence_for_subject(self, sentence):
        score = 0
        s = sentence.lower()
        if re.search(r'\bin \[[^\]]+\].*?\b(i|we)\s+(added|created|implemented|updated|changed|modified|fixed|resolved|corrected|replaced|introduced|moved|landed|carried|kept)\b', s):
            score += 20
        if re.search(r'\b(i|we)\s+(added|created|implemented|updated|changed|modified|fixed|resolved|corrected|replaced|introduced|moved|landed|carried|kept|made)\b', s):
            score += 15
        if re.search(r'\bwe\s+got\b', s):
            score += 14
        if re.search(r'\bhelp\s*->\s*user guide\b', s):
            score += 12
        if re.search(r'\b(user guide|lyrics window|channels view|piano player|pianola|roadmap|readme|docs)\b', s):
            score += 5
        if re.search(r'\b(test|tests|unittest|pytest|ci|coverage|validation)\b', s):
            score -= 2
        return score

    def extract_action_phrase(self, sentence):
        sentence = self.clean_summary_text(sentence)
        if not sentence:
            return None, None

        sentence_lower = sentence.lower()
        sentence_lower = sentence_lower.replace("’", "'")
        sentence_lower = sentence_lower.replace("`", "")

        special_patterns = [
            (r'\bhelp\s*->\s*user guide\b', 'add'),
            (r'\bview\s*->\s*rhythm\b', 'add'),
            (r'\bview\s*->\s*channels\b', 'add'),
            (r'\bview\s*->\s*lyrics\b', 'add'),
            (r'\bhelp\s*->\s*about\b', 'docs'),
            (r'\bencoding selector\b', 'add'),
            (r'\bsave button\b', 'add'),
            (r'\bfullscreen\b', 'add'),
            (r'\bcopy and font\b', 'add'),
            (r'\btrack-aware\b', 'add'),
            (r'\bprogram\s+(?:spinbox|selector|control)\b', 'add'),
            (r'\b(?:in \[[^\]]+\].*?\b(?:i|we)\s+added\s+real\s+(.+?))(?:\s+to|\s+for|\s+with|\s+in|\s+and|\.|$)', 'add'),
            (r'\b(?:in \[[^\]]+\].*?\b(?:i|we)\s+added\s+(?:a\s+new\s+)?(.+?))(?:\s+to|\s+for|\s+with|\s+in|\s+and|\.|$)', 'add'),
            (r'\b(?:i|we)\s+added\s+real\s+(.+?)(?:\s+to|\s+for|\s+with|\s+in|\s+and|\.|$)', 'add'),
            (r'\b(?:i|we)\s+added\s+(?:a\s+new\s+)?(.+?)(?:\s+to|\s+for|\s+with|\s+in|\s+and|\.|$)', 'add'),
            (r'\b(?:i|we)\s+created\s+(.+?)(?:\s+to|\s+for|\s+with|\s+in|\s+and|\.|$)', 'add'),
            (r'\b(?:i|we)\s+implemented\s+(.+?)(?:\s+to|\s+for|\s+with|\s+in|\s+and|\.|$)', 'add'),
            (r'\b(?:i|we)\s+introduced\s+(.+?)(?:\s+to|\s+for|\s+with|\s+in|\s+and|\.|$)', 'add'),
            (r'\b(?:i|we)\s+updated\s+(.+?)(?:\s+to|\s+for|\s+with|\s+in|\s+and|\.|$)', 'update'),
            (r'\b(?:i|we)\s+changed\s+(.+?)(?:\s+to|\s+for|\s+with|\s+in|\s+and|\.|$)', 'update'),
            (r'\b(?:i|we)\s+modified\s+(.+?)(?:\s+to|\s+for|\s+with|\s+in|\s+and|\.|$)', 'update'),
            (r'\b(?:i|we)\s+replaced\s+(.+?)(?:\s+with|\s+to|\s+for|\s+in|\s+and|\.|$)', 'replace'),
            (r'\b(?:i|we)\s+refactored\s+(.+?)(?:\s+to|\s+for|\s+with|\s+in|\s+and|\.|$)', 'refactor'),
            (r'\b(?:i|we)\s+(?:fixed|corrected|resolved)\s+(.+?)(?:\s+to|\s+for|\s+with|\s+in|\s+and|\.|$)', 'fix'),
            (r'\b(?:i|we)\s+sent\s+(.+?)(?:\s+to|\s+for|\s+with|\s+in|\s+and|\.|$)', 'send'),
            (r'\bwe\s+got\s+(.+?)\s+over the line', 'add'),
            (r'\bwe\s+landed\s+(.+?)(?:\s+with|\s+\.|$)', 'add'),
            (r'\bwe\s+carried\s+(.+?)\s+one step further', 'add'),
            (r'\bwe\s+kept\s+(.+?)\s+moving', 'add'),
            (r'\bwe\s+made\s+(.+?)\s+much nicer to use', 'improve'),
        ]

        for pattern, action in special_patterns:
            match = re.search(pattern, sentence_lower, re.IGNORECASE)
            if match:
                if match.groups():
                    obj_text = match.group(1)
                else:
                    obj_text = match.group(0)
                obj = self.extract_object_phrase(obj_text)
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
        best_score = -999
        best_sentence = text.strip()

        for sentence in sentences:
            content = sentence.strip()
            if len(content) < 10:
                continue
            normalized = content.lower()
            if normalized.startswith(('verification', 'current', 'test', 'tests', 'compileall', 'and ', 'but ', 'also ')):
                continue
            score = self.score_sentence_for_subject(content)
            if score > best_score:
                best_score = score
                best_sentence = content

        return best_sentence

    def analyze_with_nltk(self, text):
        normalized = self.clean_summary_text(text)
        best_sentence = self.pick_best_sentence(normalized)
        subject_verb, subject_obj = self.extract_action_phrase(best_sentence)

        if not subject_verb or not subject_obj:
            subject_verb, subject_obj = self.extract_action_phrase(normalized)

        if not subject_verb:
            subject_verb = 'update'
        if not subject_obj:
            subject_obj = 'project'

        subject_verb = subject_verb.lower()
        subject_obj = subject_obj.lower()

        if subject_obj in ['user', 'help'] and 'user guide' in normalized:
            subject_obj = 'user guide'
        elif subject_obj in ['lyrics', 'window'] and 'lyrics window' in normalized:
            subject_obj = 'lyrics window'
        elif subject_obj in ['channels'] and 'channels view' in normalized:
            subject_obj = 'channels view'
        elif subject_obj in ['pianola', 'piano'] and 'piano player' in normalized:
            subject_obj = 'piano player'

        if subject_verb == 'got' and subject_obj:
            subject_verb = 'add'
        if subject_verb == 'made':
            subject_verb = 'improve'

        return subject_verb, subject_obj

    def detect_scope(self, text):
        text_lower = text.lower()
        if 'dict' in text_lower or 'dictionary' in text_lower or 'wps' in text_lower or 'libreoffice' in text_lower:
            return 'dict'
        if 'repo' in text_lower or '.gitignore' in text_lower or 'clone' in text_lower or 'repository' in text_lower:
            return 'repo'
        if 'converter' in text_lower or ('tool' in text_lower and 'dictionary' in text_lower):
            return 'tools'

        has_docs = any(k in text_lower for k in ['roadmap', 'readme', '.md', 'docs', 'guide', 'help', 'documentation'])
        has_ui = any(k in text_lower for k in ['view', 'dialog', 'window', 'action', 'toolbar', 'button', 'checkbox', 'slider', 'meter', 'combo', 'program', 'lock', 'lyrics', 'channels', 'fullscreen', 'pianola', 'piano player'])
        has_app = any(k in text_lower for k in ['settings.py', 'player.py', 'sequence.py', 'app.py', 'widgets.py', 'settings', 'playback', 'midi', 'validation', 'tests', 'application', 'module', 'service'])
        has_tests = any(k in text_lower for k in ['test_', 'unittest', 'pytest', 'ci', 'coverage', 'validation', 'suite passed'])

        if has_ui and not has_docs:
            return 'ui'
        if has_app and not has_ui and not has_docs:
            return 'app'
        if has_docs and not has_ui and not has_app:
            return 'docs'
        if has_tests and not has_ui and not has_app and not has_docs:
            return 'test'
        if has_ui and has_docs:
            return 'ui'
        if has_app and has_docs:
            return 'app'
        return 'app'

    def select_commit_type(self, text, subject_verb, subject_obj):
        text_lower = text.lower()
        docs_keywords = ['readme', 'roadmap', 'docs', 'documentation', '.md', '.rst', 'guide', 'help', 'docstring', 'comment']
        test_keywords = ['test', 'tests', 'unittest', 'pytest', 'coverage', 'qa', 'spec', 'mock']
        ci_keywords = ['ci', 'continuous integration', 'github action', 'workflow', 'pipeline', 'circleci', 'travis', 'jenkins', 'gitlab-ci', 'azure-pipelines']
        build_keywords = ['build', 'docker', 'dockerfile', 'dependency', 'dependencies', 'npm', 'package.json', 'yarn.lock', 'pip', 'requirements', 'maven', 'gradle', 'pom.xml', 'pyproject.toml']
        perf_keywords = ['perf', 'performance', 'speed', 'latency', 'memory', 'optimiz', 'cache', 'caching']
        style_keywords = ['style', 'format', 'formatted', 'lint', 'whitespace', 'indent', 'prettier', 'eslint']
        refactor_keywords = ['refactor', 'cleanup', 'cleaned', 'restructure', 'rename', 'split', 'extract', 'simplify']
        fix_keywords = ['fix', 'fixed', 'correct', 'corrected', 'resolve', 'resolved', 'bug', 'crash', 'error']

        if any(k in text_lower for k in ci_keywords):
            return 'ci'
        if any(k in text_lower for k in build_keywords):
            return 'build'
        if any(k in text_lower for k in test_keywords) and not any(k in text_lower for k in docs_keywords):
            return 'test'
        if any(k in text_lower for k in perf_keywords) or subject_verb in ['perf', 'optimize', 'optimize', 'improve', 'improved']:
            return 'perf'
        if any(k in text_lower for k in style_keywords) or subject_verb in ['style', 'format', 'formatted', 'lint']:
            return 'style'
        if any(k in text_lower for k in refactor_keywords) or subject_verb in ['refactor', 'cleanup', 'clean', 'rename', 'restructure', 'simplify']:
            return 'refactor'
        if any(k in text_lower for k in docs_keywords) and subject_verb not in ['fix', 'perf', 'refactor', 'test', 'build', 'ci', 'style']:
            return 'docs'
        if any(k in text_lower for k in fix_keywords) or subject_verb in ['fix', 'correct', 'resolve', 'resolve', 'corrected', 'resolved']:
            return 'fix'
        if subject_verb in ['doc', 'document', 'documentation']:
            return 'docs'
        return 'feat'

    def generate_body_lines(self, text):
        text_lower = text.lower()
        bullets = []
        seen = set()

        def add_bullet(line):
            clean_line = re.sub(r'\s+', ' ', line).strip()
            if clean_line and clean_line.lower() not in seen:
                bullets.append(clean_line)
                seen.add(clean_line.lower())

        if 'roadmap.md' in text_lower or 'roadmap' in text_lower:
            add_bullet('- Update Roadmap.md to mark completed items')
        if 'user guide' in text_lower or 'help -> user guide' in text_lower or 'local help' in text_lower or 'localized document lookup' in text_lower:
            add_bullet('- Add or update user guide and localized help content')
        if 'general midi' in text_lower or 'gm name' in text_lower or 'qcombobox' in text_lower:
            add_bullet('- Use GM instrument names for channel program selection')
        if 'mute' in text_lower and 'solo' in text_lower:
            add_bullet('- Add per-channel Mute/Solo controls to the Channels view')
        if 'volume slider' in text_lower or 'volume sliders' in text_lower or 'per-channel volume' in text_lower:
            add_bullet('- Add per-channel volume sliders and real-time CC7 updates')
        if 'program lock' in text_lower or 'patch lock' in text_lower or 'lock checkbox' in text_lower:
            add_bullet('- Add per-channel patch lock to suppress file program changes')
        if 'lyrics' in text_lower and 'text events' in text_lower:
            add_bullet('- Add Lyrics window with text-event filtering')
        if 'rhythm view' in text_lower or 'rhythm panel' in text_lower:
            add_bullet('- Add Rhythm view panel with beat, bar, meter, and bpm display')
        if 'preferences' in text_lower and 'gmos' not in text_lower:
            add_bullet('- Add General preferences and playback behavior settings')
        if 'print' in text_lower and 'dialog' in text_lower:
            add_bullet('- Add Print support for filtered lyrics text')
        if 'fullscreen' in text_lower:
            add_bullet('- Add fullscreen mode for the dialog')
        if 'encoding' in text_lower and 'save' in text_lower:
            add_bullet('- Add encoding selector and save support for exported lyrics')
        if 'track-aware' in text_lower or 'source track' in text_lower:
            add_bullet('- Add track-aware filtering for lyrics events')

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
                if action == 'add' and obj in ['user', 'view', 'window', 'help']:
                    continue
                bullet = f'- {action.capitalize()} {obj}'
                add_bullet(bullet)
            if len(bullets) >= 8:
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

            commit_type = self.select_commit_type(text, verb, obj)

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
