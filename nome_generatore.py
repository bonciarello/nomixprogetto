"""
Generatore di nomi per progetto da descrizione in italiano.
Tokenizza il testo, estrae parole chiave, le combina con pattern creativi.
"""

import random
import re

# ── Stopwords italiane ─────────────────────────────────────────────
STOPWORDS: set[str] = {
    "il", "lo", "la", "i", "gli", "le", "un", "uno", "una", "dei", "del",
    "della", "degli", "delle", "al", "allo", "alla", "agli", "alle", "dal",
    "dallo", "dalla", "dagli", "dalle", "sul", "sullo", "sulla", "sugli",
    "sulle", "nel", "nello", "nella", "negli", "nelle", "col", "coi",
    "di", "a", "da", "in", "con", "su", "per", "tra", "fra",
    "e", "ed", "o", "ma", "che", "chi", "cui", "non", "si", "mi", "ti",
    "ci", "vi", "li", "ne", "io", "tu", "lui", "lei", "noi", "voi", "loro",
    "mio", "tuo", "suo", "nostro", "vostro", "questo", "quello", "questa",
    "quella", "questi", "quelli", "queste", "quelle", "come", "più", "meno",
    "se", "anche", "ogni", "tutto", "tutti", "tutta", "tutte",
    "molto", "molti", "molta", "molte", "tanto", "tanti", "tanta", "tante",
    "quale", "quali", "dove", "quando", "perché", "cosa", "quanto",
    "quanti", "quanta", "quante", "sono", "sei", "è", "siamo", "siete",
    "ho", "hai", "ha", "abbiamo", "avete", "hanno", "ero", "eri", "era",
    "eravamo", "eravate", "erano", "sarò", "sarai", "sarà", "saremo",
    "sarete", "saranno", "essere", "avere", "fare", "stare", "andare",
    "venire", "potere", "dovere", "volere", "sapere", "dire", "dare",
    "suo", "sua", "suoi", "sue", "nostro", "nostra", "nostri", "nostre",
    "vostro", "vostra", "vostri", "vostre", "quindi", "infatti", "invece",
    "dunque", "cioè", "oppure", "mentre", "durante", "attraverso", "contro",
    "entro", "senza", "dopo", "prima", "sopra", "sotto", "circa", "oltre",
    "devo", "devi", "deve", "dobbiamo", "dovete", "devono",
    "posso", "puoi", "può", "possiamo", "potete", "possono",
    "voglio", "vuoi", "vuole", "vogliamo", "volete", "vogliono",
    "cui", "ossia", "ovvero", "davanti", "fuori", "dentro", "vicino",
    "lontano", "circa", "appena", "ormai", "comunque", "anziché",
    "affinché", "benché", "cosicché", "purché", "quasi", "proprio",
    "insomma", "allora", "cio", "qui", "qua", "lì", "là",
}

# ── Prefissi creativi italiani ─────────────────────────────────────
PREFISSI: list[str] = [
    "Super", "Mega", "Ultra", "Iper", "Neo", "Multi", "Eco", "Micro",
    "Fast", "Smart", "Top", "Prime", "Next", "Max", "Mini",
    "Cyber", "Tech", "Cloud", "Data", "Code", "Web",
]

# ── Suffissi creativi ──────────────────────────────────────────────
SUFFISSI: list[str] = [
    "App", "Lab", "Hub", "Pro", "Go", "Box", "One", "Up", "Now",
    "Plus", "Max", "Zen", "ly", "io", "ia", "ix", "ify", "OS",
]

# ── Parole evocative italiane (creative bank) ──────────────────────
PAROLE_EVOCATIVE: list[str] = [
    "Conquista", "Rivoluzione", "Evoluzione", "Genio", "Magia", "Sogno",
    "Idea", "Mente", "Ingegno", "Impulso", "Slancio", "Apice", "Zenit",
    "Orizzonte", "Onda", "Flusso", "Vortex", "Nucleo", "Cuore", "Anima",
    "Spirito", "Essenza", "Futuro", "Origine", "Forza", "Energia",
    "Luce", "Fuoco", "Terra", "Aria", "Acqua", "Vento", "Fiamma",
    "Sprint", "Turbo", "Flash", "Boost", "Rocket", "Jet",
    "Pixel", "Bit", "Link", "Node", "Grid", "Matrix",
    "Bridge", "Portal", "Gate", "Path", "Route", "Track",
    "Team", "Crew", "Squad", "Tribe", "Flock",
]

# ── Mappa semantica: parola → varianti creative correlate ──────────
MAPPA_SEMANTICA: dict[str, list[str]] = {
    "casa": ["Casa", "Home", "Domus", "Tetto", "Nido", "Rifugio", "Room"],
    "domestico": ["Casa", "Home", "Domus", "Tetto", "Nido"],
    "domestica": ["Casa", "Home", "Domus", "Tetto", "Nido"],
    "domestiche": ["Casa", "Home", "Domus", "Tetto", "Nido"],
    "spesa": ["Spesa", "Budget", "Conto", "Costo", "Fondo", "Cassa", "Cash"],
    "spese": ["Spesa", "Budget", "Conto", "Costo", "Fondo", "Cassa", "Cash"],
    "condividere": ["Dividi", "Condividi", "Split", "Share", "Unisci"],
    "condiviso": ["Dividi", "Condividi", "Split", "Share", "Unisci"],
    "condivisa": ["Dividi", "Condividi", "Split", "Share", "Unisci"],
    "condivise": ["Dividi", "Condividi", "Split", "Share", "Unisci"],
    "coinquilino": ["Coinquilino", "Roomie", "Flat", "Mate", "Socio", "Casa"],
    "coinquilini": ["Coinquilino", "Roomie", "Flat", "Mate", "Socio", "Casa"],
    "gestire": ["Gestisci", "Gestito", "Gest", "Manage", "Control", "Organizza"],
    "app": ["App", "Tool", "Kit", "Suite", "Soft"],
    "applicazione": ["App", "Tool", "Kit", "Suite", "Soft"],
    "software": ["Soft", "Ware", "Code", "App", "Sys", "Dev"],
    "progetto": ["Project", "Plan", "Work", "Task", "Job", "Op"],
    "lavoro": ["Work", "Job", "Task", "Opera", "Biz"],
    "team": ["Team", "Crew", "Squad", "Tribe", "Band"],
    "tempo": ["Time", "Tempo", "Clock", "Ora", "Now"],
    "soldi": ["Money", "Cash", "Coin", "Fin", "Bank"],
    "denaro": ["Money", "Cash", "Coin", "Fin", "Bank"],
    "finanza": ["Fin", "Money", "Cash", "Bank", "Fund"],
    "studio": ["Study", "Learn", "Edu", "School", "Mind"],
    "scuola": ["School", "Edu", "Learn", "Class", "Aula"],
    "salute": ["Health", "Med", "Care", "Vita", "Well"],
    "cibo": ["Food", "Eat", "Cibo", "Mangi", "Chef"],
    "viaggio": ["Travel", "Trip", "Go", "Way", "Tour"],
    "musica": ["Music", "Sound", "Beat", "Tune", "Play"],
    "gioco": ["Game", "Play", "Fun", "Joy", "Ludo"],
    "sport": ["Sport", "Fit", "Train", "Move", "Athletic"],
    "social": ["Social", "Chat", "Talk", "Meet", "Connect"],
    "network": ["Net", "Web", "Link", "Mesh", "Graph"],
    "rete": ["Net", "Web", "Link", "Mesh", "Graph"],
    "foto": ["Photo", "Pic", "Shot", "Image", "Cam"],
    "video": ["Video", "Clip", "Film", "Movie", "Stream"],
    "chat": ["Chat", "Talk", "Mess", "Ping", "Text"],
    "cloud": ["Cloud", "Nube", "Sky", "Store", "Sync"],
    "dati": ["Data", "Info", "Stats", "Base", "Store"],
    "mobile": ["Mobile", "App", "Pocket", "Go", "Move"],
    "design": ["Design", "Art", "Craft", "Shape", "Form"],
    "web": ["Web", "Site", "Page", "Net", "Online"],
}


def tokenizza(testo: str) -> list[str]:
    """Estrae parole significative (>=2 lettere) rimuovendo punteggiatura e stopwords."""
    testo = testo.lower().strip()
    # Estrai sequenze alfabetiche (incluse lettere accentate) di almeno 2 caratteri
    parole = re.findall(r"[a-zA-ZàèéìòóùÀÈÉÌÒÓÙ]{2,}", testo)
    return [p for p in parole if p not in STOPWORDS]


def categorizza_parola(parola: str) -> list[str]:
    """
    Restituisce le categorie probabili di una parola italiana
    in base ai suffissi: 'nome', 'verbo', 'aggettivo'.
    """
    p = parola.lower()
    cat: list[str] = []

    # Verbi all'infinito
    if p.endswith(("are", "ere", "ire")):
        cat.append("verbo")

    # Nomi: suffissi tipici
    if p.endswith((
        "zione", "mento", "tore", "trice", "ista", "eria",
        "ezza", "ità", "tà", "tù", "logo", "loga", "nza",
        "enza", "anza", "ismo", "tudine",
    )):
        cat.append("nome")

    # Aggettivi: suffissi tipici
    if p.endswith((
        "bile", "evole", "oso", "osa", "istico", "istica",
        "esco", "esca", "ale", "ile", "evole", "evoli",
        "ante", "ente",
    )):
        cat.append("aggettivo")

    # Default: probabile nome
    if not cat:
        cat.append("nome")

    return cat


def trasforma_in_singolare(parola: str) -> str:
    """Tenta di ricondurre una parola italiana plurale al singolare."""
    p = parola.lower()
    if len(p) <= 3:
        return p

    # Plurali femminili in -che → -ca, -ghe → -ga
    if p.endswith("che") and len(p) > 4:
        return p[:-3] + "ca"
    if p.endswith("ghe") and len(p) > 4:
        return p[:-3] + "ga"
    # Plurali in -se (spese → spesa): togli solo la -e finale e aggiungi -a
    if p.endswith("se") and len(p) > 4:
        return p[:-1] + "a"
    # Plurali in -ni, -li, -ri → -no, -lo, -ro
    for term, sing in [("ni", "no"), ("li", "lo"), ("ri", "ro")]:
        if p.endswith(term) and len(p) > 4:
            return p[:-2] + sing
    # Generico -i → -o
    if p.endswith("i") and len(p) > 3:
        return p[:-1] + "o"
    # Generico -e → -a
    if p.endswith("e") and len(p) > 3:
        return p[:-1] + "a"

    return p


def estrai_forma_imperativa(verbo: str) -> str | None:
    """Da un verbo all'infinito estrae una forma imperativa usabile nei nomi."""
    v = verbo.lower()
    if v.endswith("are"):
        radice = v[:-3]
        if len(radice) >= 2:
            return radice + "a"
    elif v.endswith("ere"):
        radice = v[:-3]
        if len(radice) >= 2:
            return radice + "i"
    elif v.endswith("ire"):
        radice = v[:-3]
        if len(radice) >= 2:
            # Alcuni verbi in -ire prendono -isci, ma per semplicità usiamo -i
            return radice + "i"
    return None


def capitalizza(parola: str) -> str:
    """Capitalizza la prima lettera di una parola."""
    if not parola:
        return parola
    return parola[0].upper() + parola[1:]


def _raccogli_parole_base(parole: list[str]) -> list[str]:
    """
    Data una lista di parole tokenizzate, restituisce una lista di
    «parole base» capitalizzate (singolari, varianti semantiche) per i pattern.
    """
    base: list[str] = []
    for p in parole:
        base.append(capitalizza(trasforma_in_singolare(p)))
        base.append(capitalizza(p))
        if p in MAPPA_SEMANTICA:
            for v in MAPPA_SEMANTICA[p]:
                base.append(capitalizza(v))
    return list(dict.fromkeys(base))  # deduplica mantenendo ordine


def _raccogli_radici_verbali(parole: list[str]) -> list[str]:
    """Estrae forme imperative dai verbi trovati tra le parole tokenizzate."""
    radici: list[str] = []
    for p in parole:
        if p.endswith(("are", "ere", "ire")):
            imp = estrai_forma_imperativa(p)
            if imp and len(imp) >= 3:
                radici.append(capitalizza(imp))
    return list(dict.fromkeys(radici))


def _applica_pattern(base: list[str], verbi: list[str], rng: random.Random) -> set[str]:
    """Applica i pattern combinatori e restituisce un set di candidati."""
    candidati: set[str] = set()

    # Pattern 1: [nome] + [nome]
    for _ in range(25):
        if len(base) >= 2:
            a, b = rng.sample(base, 2)
            candidati.add(a + b)

    # Pattern 2: [radice verbale] + [nome]
    for _ in range(20):
        if verbi and base:
            candidati.add(rng.choice(verbi) + rng.choice(base))

    # Pattern 3: [nome] + [radice verbale]
    for _ in range(15):
        if base and verbi:
            candidati.add(rng.choice(base) + rng.choice(verbi))

    # Pattern 4: [prefisso] + [nome]
    for _ in range(18):
        if base:
            candidati.add(rng.choice(PREFISSI) + rng.choice(base))

    # Pattern 5: [nome] + [suffisso]
    for _ in range(12):
        if base:
            candidati.add(rng.choice(base) + rng.choice(SUFFISSI))

    # Pattern 6: [parola evocativa] + [nome]
    for _ in range(12):
        if base:
            candidati.add(rng.choice(PAROLE_EVOCATIVE) + rng.choice(base))

    # Pattern 7: [nome] + [parola evocativa]
    for _ in range(12):
        if base:
            candidati.add(rng.choice(base) + rng.choice(PAROLE_EVOCATIVE))

    # Pattern 8: [prefisso] + [parola evocativa]
    for _ in range(8):
        candidati.add(rng.choice(PREFISSI) + rng.choice(PAROLE_EVOCATIVE))

    # Pattern 9: [radice verbale] + [parola evocativa]
    for _ in range(8):
        if verbi:
            candidati.add(rng.choice(verbi) + rng.choice(PAROLE_EVOCATIVE))

    return candidati


def genera_nomi(
    descrizione: str,
    nomi_esistenti: set[str] | None = None,
    count: int = 8,
) -> list[str]:
    """
    Genera una lista di nomi creativi per un progetto.

    Args:
        descrizione: Testo in italiano (max 500 caratteri).
        nomi_esistenti: Nomi già generati nella sessione, da non ripetere.
        count: Numero di nomi da generare (default 8).

    Returns:
        Lista di nomi generati.

    Raises:
        ValueError: Se la descrizione è vuota o ha meno di 3 parole significative.
    """
    if nomi_esistenti is None:
        nomi_esistenti = set()

    descrizione = descrizione.strip()
    if not descrizione:
        raise ValueError("Inserisci una descrizione.")

    if len(descrizione) > 500:
        descrizione = descrizione[:500]

    parole = tokenizza(descrizione)

    if len(parole) < 3:
        raise ValueError(
            "Inserisci almeno 3 parole significative nella descrizione "
            f"(trovate: {len(parole)})."
        )

    # Raccogli parole base e radici verbali
    parole_base = _raccogli_parole_base(parole)
    radici_verbali = _raccogli_radici_verbali(parole)

    # Se poche parole base, arricchisci con evocative
    if len(parole_base) < 4:
        parole_base.extend(PAROLE_EVOCATIVE[:10])
        parole_base = list(dict.fromkeys(parole_base))

    # Generatore riproducibile per la stessa descrizione (seed dal suo hash)
    rng = random.Random(hash(descrizione) % (2**31))

    candidati = _applica_pattern(parole_base, radici_verbali, rng)

    # Filtra per lunghezza 4–30
    candidati = {c for c in candidati if 4 <= len(c) <= 30}

    # Rimuovi duplicati rispetto ai già generati
    candidati -= nomi_esistenti

    # Ordina per qualità: preferisci lunghezza media 8–20, poi random
    def score(nome: str) -> float:
        lungh = len(nome)
        centro = 14
        penalty = abs(lungh - centro) * 0.5
        return -penalty + rng.random() * 3

    ordinati = sorted(candidati, key=score, reverse=True)

    risultato = ordinati[:count]

    # Fallback: se non bastano, genera extra forzati
    tentativi = 0
    while len(risultato) < count and tentativi < 200:
        tentativi += 1
        a = rng.choice(parole_base) if parole_base else "Pro"
        b = rng.choice(PAROLE_EVOCATIVE)
        nuovo = a + b
        if 4 <= len(nuovo) <= 30 and nuovo not in nomi_esistenti and nuovo not in risultato:
            risultato.append(nuovo)

    rng.shuffle(risultato)
    return risultato[:count]
