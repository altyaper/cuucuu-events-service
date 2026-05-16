import math
import re

INVITATION_PHRASES = [
    r"invita\s+a\s+la\s+comunidad",
    r"invita\s+a\s+asistir",
    r"invita\s+al\s+público",
    r"invita\s+a\s+participar",
    r"te\s+invita(mos)?",
    r"están\s+invitados",
    r"convoca\s+a",
]

FUTURE_EVENT_PHRASES = [
    r"se\s+llevará\s+a\s+cabo",
    r"se\s+realizará",
    r"tendrá\s+lugar",
    r"se\s+celebrará",
    r"se\s+efectuará",
    r"se\s+llevará\s+a\s+efecto",
    r"se\s+presenta(rá)?",
    r"dará\s+inicio",
]

DATE_REFERENCES = [
    r"este\s+(lunes|martes|miércoles|jueves|viernes|sábado|domingo)",
    r"próximo\s+(lunes|martes|miércoles|jueves|viernes|sábado|domingo)",
    r"el\s+próximo",
    r"del\s+\d{1,2}\s+(al|y)\s+\d{1,2}\s+de\s+\w+",
    r"(lunes|martes|miércoles|jueves|viernes|sábado|domingo)\s+\d{1,2}\s+de\s+\w+",
    r"\d{1,2}\s+de\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)",
]

TIME_REFERENCES = [
    r"a\s+partir\s+de\s+las",
    r"de\s+las?\s+\d{1,2}[:\.]?\d{0,2}\s*(a|a\s+las)\s+\d{1,2}",
    r"\d{1,2}:\d{2}\s*(hrs|horas|am|pm|de\s+la\s+(mañana|tarde|noche))",
    r"desde\s+las\s+\d{1,2}",
    r"horario\s*:?\s*\d{1,2}",
]

VENUE_KEYWORDS = [
    r"centro\s+de\s+convenciones",
    r"teatro\b",
    r"museo\b",
    r"plaza\b",
    r"parque\b",
    r"auditorio\b",
    r"estadio\b",
    r"salón\b",
    r"foro\b",
    r"galería\b",
    r"explanada\b",
    r"arena\b",
    r"recinto\b",
]

EVENT_TYPE_NOUNS = [
    r"festival\b",
    r"expo(sición)?\b",
    r"feria\b",
    r"concierto\b",
    r"taller(es)?\b",
    r"conferencia\b",
    r"presentación\b",
    r"función\b",
    r"convocatoria\b",
    r"carrera\b",
    r"desfile\b",
    r"inauguración\b",
    r"muestra\b",
    r"jornada\b",
    r"torneo\b",
    r"encuentro\b",
    r"maratón\b",
    r"bazar\b",
    r"kermés\b",
]

ADMISSION_CUES = [
    r"entrada\s+(libre|gratuita|general)",
    r"boletos?\b",
    r"costo\s+de",
    r"admisión",
    r"registro\s+(gratuito|libre|en\s+línea)",
    r"sin\s+costo",
    r"acceso\s+(libre|gratuito)",
]

CRIME_PENALTIES = [
    r"asesinato",
    r"detenido",
    r"homicidio",
    r"accidente\b",
    r"choque\b",
    r"muerto\b",
    r"fallecido",
    r"víctima\b",
    r"balacera",
    r"sicario",
    r"narcotráfico",
    r"decomiso",
    r"robo\b",
    r"asalto\b",
    r"crimen\b",
    r"violencia\b",
    r"feminicidio",
    r"desaparecido",
    r"levantón",
    r"secuestro\b",
    r"extorsión\b",
]

PAST_TENSE_PENALTIES = [
    r"se\s+llevó\s+a\s+cabo",
    r"se\s+realizó",
    r"tuvo\s+lugar",
    r"se\s+celebró",
    r"se\s+efectuó",
    r"se\s+presentó",
    r"el\s+pasado\s+(lunes|martes|miércoles|jueves|viernes|sábado|domingo)",
]

POLITICAL_PENALTIES = [
    r"sentencia\b",
    r"juicio\b",
    r"demanda\b",
    r"elecciones\b",
    r"diputado",
    r"gobernador",
    r"candidato",
]


class ScoringBreakdown:
    def __init__(self):
        self.invitation: int = 0
        self.future_event: int = 0
        self.date_refs: int = 0
        self.time_refs: int = 0
        self.venue: int = 0
        self.event_type: int = 0
        self.admission: int = 0
        self.crime_penalty: int = 0
        self.past_tense_penalty: int = 0
        self.political_penalty: int = 0
        self.matched_signals: list[str] = []

    @property
    def raw_score(self) -> int:
        return (
            self.invitation
            + self.future_event
            + self.date_refs
            + self.time_refs
            + self.venue
            + self.event_type
            + self.admission
            + self.crime_penalty
            + self.past_tense_penalty
            + self.political_penalty
        )


def _count_matches(text: str, patterns: list[str]) -> tuple[int, list[str]]:
    count = 0
    matched = []
    for pattern in patterns:
        found = re.findall(pattern, text, re.IGNORECASE)
        if found:
            count += 1
            matched.append(pattern)
    return count, matched


def _sigmoid(x: float, center: float = 5.0, steepness: float = 0.5) -> float:
    return 1.0 / (1.0 + math.exp(-steepness * (x - center)))


def score_article(text: str) -> tuple[float, ScoringBreakdown]:
    breakdown = ScoringBreakdown()

    n, m = _count_matches(text, INVITATION_PHRASES)
    breakdown.invitation = n * 3
    breakdown.matched_signals.extend(m)

    n, m = _count_matches(text, FUTURE_EVENT_PHRASES)
    breakdown.future_event = n * 3
    breakdown.matched_signals.extend(m)

    n, m = _count_matches(text, DATE_REFERENCES)
    breakdown.date_refs = n * 2
    breakdown.matched_signals.extend(m)

    n, m = _count_matches(text, TIME_REFERENCES)
    breakdown.time_refs = n * 2
    breakdown.matched_signals.extend(m)

    n, m = _count_matches(text, VENUE_KEYWORDS)
    breakdown.venue = n * 2
    breakdown.matched_signals.extend(m)

    n, m = _count_matches(text, EVENT_TYPE_NOUNS)
    breakdown.event_type = n * 2
    breakdown.matched_signals.extend(m)

    n, m = _count_matches(text, ADMISSION_CUES)
    breakdown.admission = n * 1
    breakdown.matched_signals.extend(m)

    n, m = _count_matches(text, CRIME_PENALTIES)
    breakdown.crime_penalty = n * -5
    breakdown.matched_signals.extend(m)

    n, m = _count_matches(text, PAST_TENSE_PENALTIES)
    breakdown.past_tense_penalty = n * -3
    breakdown.matched_signals.extend(m)

    n, m = _count_matches(text, POLITICAL_PENALTIES)
    breakdown.political_penalty = n * -2
    breakdown.matched_signals.extend(m)

    confidence = _sigmoid(breakdown.raw_score)
    confidence = max(0.0, min(1.0, confidence))

    return confidence, breakdown
