"""Conservative language choice for English and Roman Urdu study requests."""
import re

MARKERS = set('kya kaise samjhao samjha samjhaein hai hain mein mujhe batao sawal sawalat jawab hal karo karein chahiye ki ke ka se'.split())
STRONG = {'samjhao', 'samjhaein', 'batao'}
ALIASES = {'garmi': 'heat', 'hararat': 'temperature', 'awaz': 'sound', 'awaaz': 'sound',
           'roshni': 'light', 'bijli': 'electricity', 'zarraat': 'particles', 'tezab': 'acid', 'namak': 'salt'}
RETRIEVAL_STOP = MARKERS | set('mujhay mujhy iska iski iske yeh ye woh wo kyun kyu samjhayen samjhaen samjha do dein bata bataein bataen bare baray baare baat kya kese kesay mujko hum ko aur bhi asaan aasan alfaaz lafzon zara please'.split())


def detect_language(query):
    text = query.lower()
    if re.search(r'\b(?:in\s+english|english\s+(?:mein|me)|(?:answer|explain|reply)\s+(?:in\s+)?english)\b', text):
        return 'english'
    if re.search(r'\broman\s+urdu\b', text):
        return 'roman-urdu'
    words = set(re.findall(r'[a-z]+', text))
    return 'roman-urdu' if words & STRONG or len(words & MARKERS) >= 2 else 'english'


def retrieval_text(query):
    """Remove Roman Urdu question scaffolding, preserving textbook English terms."""
    words = re.findall(r'[a-z0-9]+', query.lower())
    normalized = [ALIASES.get(word, word) for word in words if word not in RETRIEVAL_STOP]
    return ' '.join(normalized) if normalized else query
