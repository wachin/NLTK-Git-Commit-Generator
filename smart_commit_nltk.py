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

    def strip_markdown_noise(self, text):
        cleaned_lines = []
        in_fence = False

        for raw_line in text.splitlines():
            line = raw_line.strip()
            if line.startswith('```'):
                in_fence = not in_fence
                continue
            if in_fence:
                if 'py_compile' in line:
                    cleaned_lines.append(f"Verifiqué con {line}.")
                continue
            if re.search(r'^\s*git\s+commit\b', line):
                continue
            if re.search(r'^\s*-m\s+["\']', line):
                continue
            cleaned_lines.append(raw_line)

        text = '\n'.join(cleaned_lines)
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        text = re.sub(r'`([^`]+)`', r'\1', text)
        return text

    def detect_language(self, text):
        text_lower = text.lower()
        spanish_markers = [
            ' el ', ' la ', ' los ', ' las ', ' un ', ' una ', ' este ', ' esta ',
            ' que ', ' para ', ' con ', ' sin ', ' desde ', ' hasta ', ' también ',
            ' he ', ' hemos ', ' creado', ' añad', ' agreg', ' actualiz', ' correg',
            ' mejora', ' incluye', ' resume', ' documento', ' funcionalidades',
            ' completadas', ' pendientes', ' pruebas', ' multilenguaje'
        ]
        english_markers = [
            ' the ', ' a ', ' an ', ' this ', ' that ', ' with ', ' without ',
            ' from ', ' to ', ' also ', ' i ', ' we ', ' created', ' added',
            ' updated', ' fixed', ' improved', ' includes', ' document',
            ' completed', ' pending', ' tests', ' multilingual'
        ]

        padded = f" {text_lower} "
        spanish_score = sum(2 for marker in spanish_markers if marker in padded)
        english_score = sum(2 for marker in english_markers if marker in padded)
        spanish_score += len(re.findall(r'[áéíóúñü¿¡]', text_lower)) * 3

        return 'es' if spanish_score > english_score else 'en'

    def sent_tokenize_by_language(self, text, language):
        nltk_language = 'spanish' if language == 'es' else 'english'
        try:
            return nltk.sent_tokenize(text, language=nltk_language)
        except LookupError:
            return re.split(r'(?<=[.!?])\s+', text)

    def clean_input(self, text):
        text = self.strip_markdown_noise(text)
        # Remove noise patterns: Read commands, terminal commands, file references, conversation notes
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Skip lines that look like file reads, terminal commands, or conversation
            if re.search(r'^(Read|Ran terminal command|Replacing|Made changes|Replacing \d+ lines)', line, re.IGNORECASE):
                continue
            if re.search(r'^(command -v|for f in|echo|----|sed|pdftotext|python3)', line):
                continue
            if re.search(r'^(file:///|lines \d+ to \d+|content\.txt)', line):
                continue
            if re.search(r'^(Replacing \d+ lines with \d+ lines)', line):
                continue
            if re.search(r'^(Voy a|Reviso la|Encuentro que|He encontrado|Verifico si)', line):
                continue
            if re.search(r'^(Y analizo|Sed|Replacing)', line):
                continue
            # Skip very short lines or lines without action verbs
            if len(line) < 10 or not re.search(
                r'\b(we|i|added|created|implemented|updated|changed|fixed|refactored|improved|made|'
                r'he|hemos|creado|creé|creamos|añadido|añadí|agregado|implementado|actualizado|'
                r'cambiado|corregido|arreglado|mejorado|documenta|documentado|incluye|resume|'
                r'detecta|usa|entiende|genera|corrige|corregí|corregi|verifiqué|verifique|validé|valide)\b',
                line,
                re.IGNORECASE
            ):
                continue
            cleaned_lines.append(line)
        return '\n'.join(cleaned_lines)

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
        # Prefer sentences starting with action verbs
        if re.search(r'^\s*(add|implement|create|introduce|build|update|change|modify|fix|resolve|correct|enhance|extend|replace|improve|remove|delete|rename|merge|optimize|document|format|configure)', s):
            score += 20
        if re.search(r'^\s*(agrega|añade|crea|implementa|actualiza|cambia|modifica|corrige|arregla|mejora|documenta|formatea|configura|incluye|resume)', s):
            score += 20
        if re.search(r'\bin \[[^\]]+\].*?\b(i|we)\s+(added|created|implemented|updated|changed|modified|fixed|resolved|corrected|replaced|introduced|moved|landed|carried|kept)\b', s):
            score += 20
        if re.search(r'\b(i|we)\s+(added|created|implemented|updated|changed|modified|fixed|resolved|corrected|replaced|introduced|moved|landed|carried|kept|made)\b', s):
            score += 15
        if re.search(r'\b(he|hemos|yo|nosotros)\s+(creado|añadido|agregado|implementado|actualizado|cambiado|modificado|corregido|arreglado|mejorado|documentado)\b', s):
            score += 15
        if re.search(r'\bwe\s+got\b', s):
            score += 14
        if re.search(r'\b(roadmap|readme|documentación|documentacion|guía|guia|docs)\b', s):
            score += 5
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

        if re.search(r'\broadmap\.md\b|\broadmap\b', sentence_lower):
            if re.search(r'\b(created|added|add|new file)\b', sentence_lower):
                return 'add', 'project roadmap with progress tracking'
            if re.search(r'\b(updated|mark|completed|complete)\b', sentence_lower):
                return 'update', 'project roadmap'

        if (
            re.search(r'\b(spanish|english|bilingual|language|tokenization|spanish verbs)\b', sentence_lower)
            and re.search(r'\b(detect|uses?|understand|generate|support)\b', sentence_lower)
        ):
            if re.search(r'\bci\b|false-positive|type detection', sentence_lower):
                return 'add', 'bilingual support and fix type detection'
            return 'add', 'bilingual commit support'

        if re.search(r'\b(false-positive|false positive)\b.*\bci\b|\bci\b.*\b(false-positive|false positive)\b', sentence_lower):
            return 'fix', 'ci type detection'

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

    def extract_spanish_object_phrase(self, phrase):
        phrase = re.sub(r'\[.*?\]', ' ', phrase)
        phrase = phrase.replace('`', ' ')
        phrase = phrase.replace('->', ' -> ')
        phrase = re.sub(r'([a-záéíóúñ])([A-Z])', r'\1 \2', phrase)
        phrase = re.sub(r'\s+', ' ', phrase).strip()
        if not phrase:
            return ""

        stop_words = {
            'para', 'por', 'con', 'sin', 'desde', 'hasta', 'y', 'e', 'o', 'u',
            'que', 'donde', 'cuando', 'como', 'porque', 'si', 'pero', 'aunque',
            'también', 'tambien', 'además', 'ademas', 'dejando', 'marcando'
        }
        generic_start = {
            'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'este',
            'esta', 'estos', 'estas', 'nuevo', 'nueva', 'nuevos', 'nuevas'
        }

        tokens = re.findall(r'[\wÁÉÍÓÚÜÑáéíóúüñ./_-]+|->', phrase, re.UNICODE)
        obj_words = []
        for token in tokens:
            lower = token.lower().strip('.,;:()[]{}')
            if not lower:
                continue
            if not obj_words and lower in generic_start:
                continue
            if lower in stop_words:
                break
            if re.match(r'^[\wáéíóúüñ./_-]+$', lower) or lower == '->':
                obj_words.append(lower)
            if len(obj_words) >= 8:
                break

        cleaned = " ".join(obj_words).strip().rstrip(',.')
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned

    def extract_action_phrase_es(self, sentence):
        sentence = self.clean_summary_text(sentence)
        if not sentence:
            return None, None

        sentence_lower = sentence.lower().replace("`", "")

        if re.search(r'\broadmap\.md\b|\broadmap\b', sentence_lower):
            if re.search(r'\b(cread[oa]|creé|creamos|he creado|hemos creado|nuevo archivo)\b', sentence_lower):
                return 'add', 'roadmap con seguimiento de progreso'
            if re.search(r'\b(actualizad[oa]|marcar|marcando|completad[oa]s?)\b', sentence_lower):
                return 'update', 'roadmap del proyecto'

        if (
            re.search(r'\b(español|ingles|inglés|biling[uü]e|idioma|tokenizaci[oó]n|verbos españoles)\b', sentence_lower)
            and re.search(r'\b(detecta|usa|entiende|genera|soporte|compatibilidad)\b', sentence_lower)
        ):
            if re.search(r'\bci\b|falso positivo|false-positive|detecci[oó]n de tipo', sentence_lower):
                return 'add', 'soporte bilingüe y corrige detección de tipo'
            return 'add', 'soporte bilingüe para commits'

        if re.search(r'\b(falso positivo|false-positive)\b.*\bci\b|\bci\b.*\b(falso positivo|false-positive)\b', sentence_lower):
            return 'fix', 'detección de tipo ci'

        special_patterns = [
            (r'\b(?:he|hemos)?\s*(?:creado|creé|creamos)\s+(.+?)(?:\s+en|\s+para|\s+con|\s+y|\.|$)', 'add'),
            (r'\b(?:he|hemos)?\s*(?:añadido|añadí|agregado|agregué|incorporado)\s+(.+?)(?:\s+en|\s+para|\s+con|\s+y|\.|$)', 'add'),
            (r'\b(?:he|hemos)?\s*(?:implementado|implementé|implementamos)\s+(.+?)(?:\s+en|\s+para|\s+con|\s+y|\.|$)', 'add'),
            (r'\b(?:he|hemos)?\s*(?:actualizado|actualicé|actualizamos)\s+(.+?)(?:\s+en|\s+para|\s+con|\s+y|\.|$)', 'update'),
            (r'\b(?:he|hemos)?\s*(?:corregido|arreglado|resuelto)\s+(.+?)(?:\s+en|\s+para|\s+con|\s+y|\.|$)', 'fix'),
            (r'\b(?:he|hemos)?\s*(?:mejorado|optimizado)\s+(.+?)(?:\s+en|\s+para|\s+con|\s+y|\.|$)', 'improve'),
            (r'\b(?:he|hemos)?\s*(?:documentado)\s+(.+?)(?:\s+en|\s+para|\s+con|\s+y|\.|$)', 'doc'),
            (r'\b(?:este\s+documento\s+)?(?:incluye|resume|documenta)\s+(.+?)(?:\s+para|\s+con|\s+y|\.|$)', 'doc'),
        ]

        for pattern, action in special_patterns:
            match = re.search(pattern, sentence_lower, re.IGNORECASE)
            if match:
                obj = self.extract_spanish_object_phrase(match.group(1))
                if obj:
                    return action, obj

        return None, None

    def is_commitworthy_sentence(self, sentence):
        normalized = sentence.lower()
        # Must have action verb (with or without subject pronoun)
        action_verbs = [
            'add', 'implement', 'create', 'introduce', 'build', 'land', 'push', 'move', 'refactor', 'clean',
            'update', 'change', 'modify', 'fix', 'resolve', 'correct', 'enhance', 'extend', 'replace', 'improve',
            'make', 'remove', 'delete', 'rename', 'merge', 'optimize', 'document', 'format', 'configure',
            'agrega', 'añade', 'crea', 'creado', 'crear', 'implementa', 'implementado', 'actualiza',
            'actualizado', 'cambia', 'modifica', 'corrige', 'arregla', 'mejora', 'mejorado',
            'documenta', 'documentado', 'incluye', 'resume'
        ]
        has_action = any(re.search(rf"\b{verb}\b", normalized) for verb in action_verbs)
        if not has_action:
            return False
        
        # Avoid sentences that are just descriptions or results
        if re.search(r"\b(it|this|that)\s+(updates|now|shows|supports|uses|sends|displays|provides|includes|contains)\b", normalized):
            return False
        # Avoid test/validation sentences
        if re.search(r"\b(verification|compileall|tests|passed|OK|validation)\b", normalized):
            return False
        # Avoid generic or conversational sentences
        if re.search(r"\b(yo|tu|usted|nosotros|ellos|este|eso|aquí|ahí|allí|como|porque|si|no|pero|sin embargo)\b", normalized):
            return False
        # Avoid very short sentences
        if len(normalized.split()) < 4:
            return False
        return True

    def pick_best_sentence(self, text, language='en'):
        sentences = self.sent_tokenize_by_language(text, language)
        best_score = -999
        best_sentence = text.strip()

        for sentence in sentences:
            content = sentence.strip()
            if len(content) < 10:
                continue
            normalized = content.lower()
            if normalized.startswith((
                'verification', 'current', 'test', 'tests', 'compileall', 'and ', 'but ', 'also ',
                'verificación', 'verificacion', 'pruebas', 'validación', 'validacion', 'y ', 'pero ', 'también ', 'tambien '
            )):
                continue
            score = self.score_sentence_for_subject(content)
            if score > best_score:
                best_score = score
                best_sentence = content

        return best_sentence

    def analyze_with_nltk(self, text):
        language = self.detect_language(text)
        normalized = self.clean_input(text)
        best_sentence = self.pick_best_sentence(normalized, language)

        if language == 'es':
            subject_verb, subject_obj = self.extract_action_phrase_es(best_sentence)
        else:
            subject_verb, subject_obj = self.extract_action_phrase(best_sentence)

        if not subject_verb or not subject_obj:
            if language == 'es':
                subject_verb, subject_obj = self.extract_action_phrase_es(normalized)
            else:
                subject_verb, subject_obj = self.extract_action_phrase(normalized)

        if not subject_verb:
            subject_verb = 'update'
        if not subject_obj:
            subject_obj = 'proyecto' if language == 'es' else 'project'

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

        if language == 'es' and 'soporte bilingüe' in subject_obj and re.search(r'\bci\b|falso positivo|detecci[oó]n de tipo', normalized):
            subject_obj = 'soporte bilingüe y corrige tipo ci'
        elif language == 'en' and 'bilingual' in subject_obj and re.search(r'\bci\b|false-positive|type detection', normalized):
            subject_obj = 'bilingual support and fix type detection'

        if subject_verb == 'got' and subject_obj:
            subject_verb = 'add'
        if subject_verb == 'made':
            subject_verb = 'improve'

        return subject_verb, subject_obj, language

    def format_subject(self, action, obj, language):
        if language == 'es':
            verb_map = {
                'add': 'agrega', 'update': 'actualiza', 'fix': 'corrige',
                'improve': 'mejora', 'refactor': 'refactoriza', 'replace': 'reemplaza',
                'remove': 'elimina', 'doc': 'documenta', 'docs': 'documenta',
                'format': 'formatea', 'configure': 'configura', 'optimize': 'optimiza'
            }
        else:
            verb_map = {
                'add': 'add', 'update': 'update', 'fix': 'fix',
                'improve': 'improve', 'refactor': 'refactor', 'replace': 'replace',
                'remove': 'remove', 'doc': 'document', 'docs': 'document',
                'format': 'format', 'configure': 'configure', 'optimize': 'optimize'
            }

        verb = verb_map.get(action, action)
        return f"{verb} {obj}".strip()

    def detect_scope(self, text):
        text_lower = text.lower()
        if any(k in text_lower for k in ['smart_commit_nltk.py', 'nltk', 'tokenization', 'tokenización', 'idioma', 'bilingüe', 'bilingue', 'spanish verbs', 'verbos españoles']):
            return 'nlp'
        if 'dict' in text_lower or 'dictionary' in text_lower or 'wps' in text_lower or 'libreoffice' in text_lower:
            return 'dict'
        if 'repo' in text_lower or '.gitignore' in text_lower or 'clone' in text_lower or 'repository' in text_lower:
            return 'repo'
        if ('roadmap.md' in text_lower or 'roadmap' in text_lower) and re.search(r'\b(created|creado|creé|creamos|new file|nuevo archivo)\b', text_lower):
            return 'repo'
        if 'converter' in text_lower or ('tool' in text_lower and 'dictionary' in text_lower):
            return 'tools'

        has_docs = any(k in text_lower for k in ['roadmap', 'readme', '.md', 'docs', 'guide', 'help', 'documentation', 'documentación', 'documentacion', 'guía', 'guia'])
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
        docs_keywords = ['readme', 'roadmap', 'docs', 'documentation', 'documentación', 'documentacion', '.md', '.rst', 'guide', 'guía', 'guia', 'help', 'docstring', 'comment']
        test_keywords = ['test', 'tests', 'unittest', 'pytest', 'coverage', 'qa', 'spec', 'mock', 'prueba', 'pruebas']
        ci_keywords = ['ci', 'continuous integration', 'github action', 'workflow', 'pipeline', 'circleci', 'travis', 'jenkins', 'gitlab-ci', 'azure-pipelines']
        build_keywords = ['build', 'docker', 'dockerfile', 'dependency', 'dependencies', 'npm', 'package.json', 'yarn.lock', 'pip', 'requirements', 'maven', 'gradle', 'pom.xml', 'pyproject.toml']
        perf_keywords = ['perf', 'performance', 'speed', 'latency', 'memory', 'optimiz', 'cache', 'caching', 'rendimiento']
        style_keywords = ['style', 'format', 'formatted', 'lint', 'whitespace', 'indent', 'prettier', 'eslint', 'formato']
        refactor_keywords = ['refactor', 'cleanup', 'cleaned', 'restructure', 'rename', 'split', 'extract', 'simplify', 'refactoriza', 'limpia']
        fix_keywords = ['fix', 'fixed', 'correct', 'corrected', 'resolve', 'resolved', 'bug', 'crash', 'error', 'corrige', 'corregido', 'arregla', 'arreglado']

        if any(k in text_lower for k in ['bilingüe', 'bilingue', 'bilingual', 'tokenización', 'tokenization', 'verbos españoles', 'spanish verbs']):
            return 'feat'
        if any(re.search(rf'\b{re.escape(k)}\b', text_lower) for k in ci_keywords):
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
        if subject_verb in ['doc', 'document', 'documentation', 'documenta', 'documentado']:
            return 'docs'
        return 'feat'

    def generate_body_lines(self, text, language='en'):
        text_lower = text.lower()
        bullets = []
        seen = set()

        def add_bullet(line):
            clean_line = re.sub(r'\s+', ' ', line).strip()
            if clean_line and clean_line.lower() not in seen:
                bullets.append(clean_line)
                seen.add(clean_line.lower())

        if language == 'es':
            has_bilingual_nlp = any(k in text_lower for k in ['bilingüe', 'bilingue', 'español', 'inglés', 'ingles', 'tokenización', 'tokenizacion', 'verbos españoles'])
            if has_bilingual_nlp and any(k in text_lower for k in ['smart_commit_nltk.py', 'nltk', 'idioma']):
                add_bullet('- Detecta el idioma de entrada para tokenización localizada')
                add_bullet('- Soporta verbos españoles como creado, actualizado e incluye')
                add_bullet('- Genera subject y body en el idioma del resumen')
                if re.search(r'\bci\b|falso positivo|false-positive|detección de tipo|deteccion de tipo', text_lower):
                    add_bullet('- Corrige falsos positivos de ci dentro de palabras comunes')
                if 'py_compile' in text_lower:
                    add_bullet('- Valida la sintaxis con py_compile')
            if 'roadmap.md' in text_lower or 'roadmap' in text_lower:
                if re.search(r'\b(cread[oa]|creé|creamos|he creado|hemos creado)\b', text_lower):
                    add_bullet('- Documenta funcionalidades completadas y progreso del proyecto')
                    add_bullet('- Resume mejoras futuras para Git, ML, UI, pruebas y multilenguaje')
                    add_bullet('- Organiza el roadmap con secciones claras de estado')
                    add_bullet('- Incluye áreas de documentación, comunidad y testing')
                    add_bullet('- Usa checkboxes para visualizar tareas completadas y pendientes')
                else:
                    add_bullet('- Actualiza Roadmap.md para marcar elementos completados')
            if 'readme' in text_lower or 'documentación' in text_lower or 'documentacion' in text_lower:
                add_bullet('- Actualiza documentación del proyecto')
            if 'guía de usuario' in text_lower or 'guia de usuario' in text_lower or 'help -> user guide' in text_lower:
                add_bullet('- Añade o actualiza guía de usuario y ayuda localizada')
            if 'mute' in text_lower and 'solo' in text_lower:
                add_bullet('- Añade controles Mute/Solo por canal en la vista Channels')
            if 'slider' in text_lower and 'volumen' in text_lower:
                add_bullet('- Añade sliders de volumen por canal con actualizaciones en tiempo real')
            if 'pantalla completa' in text_lower or 'fullscreen' in text_lower:
                add_bullet('- Añade modo de pantalla completa para el diálogo')
            if 'codificación' in text_lower or 'codificacion' in text_lower:
                add_bullet('- Añade selector de codificación para exportaciones')

            test_match_es = re.search(r'(\d+)\s+pruebas\s+(?:ok|pasaron|aprobadas)', text, re.IGNORECASE)
            if test_match_es:
                add_bullet(f'- Validación: compileall OK, {test_match_es.group(1)} pruebas pasan')
            elif 'compileall' in text_lower:
                add_bullet('- Validación: compileall OK')
        else:
            has_bilingual_nlp = any(k in text_lower for k in ['bilingual', 'spanish', 'english', 'tokenization', 'spanish verbs'])
            if has_bilingual_nlp and any(k in text_lower for k in ['smart_commit_nltk.py', 'nltk', 'language']):
                add_bullet('- Detect input language for localized tokenization')
                add_bullet('- Support Spanish verbs like creado, actualizado, and incluye')
                add_bullet('- Generate commit subject and body in the source language')
                if re.search(r'\bci\b|false-positive|false positive|type detection', text_lower):
                    add_bullet('- Fix false-positive ci detection inside common words')
                if 'py_compile' in text_lower:
                    add_bullet('- Validate syntax with py_compile')
            if 'roadmap.md' in text_lower or 'roadmap' in text_lower:
                if re.search(r'\b(created|add|added|new file)\b', text_lower):
                    add_bullet('- Document completed features and project progress')
                    add_bullet('- Outline future work for Git, ML, UI, tests, and multilingual support')
                    add_bullet('- Organize the roadmap with clear status sections')
                    add_bullet('- Include documentation, community, and testing areas')
                    add_bullet('- Use checkbox format for completed and pending tasks')
                else:
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

        if len(bullets) >= 5:
            return bullets[:5]

        for sentence in self.sent_tokenize_by_language(text, language):
            candidate = sentence.strip()
            if len(candidate) < 12:
                continue
            if self.is_commitworthy_sentence(candidate):
                # Clean and format the sentence
                cleaned = candidate.strip()
                # Remove trailing punctuation if it's not part of the sentence
                cleaned = re.sub(r'[.!?]+$', '', cleaned)
                # Capitalize first letter
                cleaned = cleaned[0].upper() + cleaned[1:] if cleaned else cleaned
                # Add as bullet point if not similar to existing
                bullet = f'- {cleaned}'
                if not is_similar_to_existing(cleaned):
                    add_bullet(bullet)
            if len(bullets) >= 5:
                break

        if not bullets:
            if language == 'es':
                add_bullet('- Implementa mejoras y ajustes del proyecto')
            else:
                add_bullet('- Implement feature enhancements and improvements')

        return bullets

    def generate_commit(self):
        text = self.input_text.toPlainText()
        if not text.strip():
            QMessageBox.warning(self, "Advertencia", "Por favor pega el texto primero.")
            return

        try:
            verb, obj, language = self.analyze_with_nltk(text)
            scope = self.detect_scope(text)
            subject = self.format_subject(verb, obj, language)
            if len(subject) > 50:
                subject = subject[:47] + "..."

            commit_type = self.select_commit_type(text, verb, obj)

            body_lines = self.generate_body_lines(self.clean_input(text), language)
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
