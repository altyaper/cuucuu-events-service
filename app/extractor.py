from __future__ import annotations

import re
from datetime import datetime, time, date

import dateparser

EVENT_TYPES_MAP = {
    "expo": r"expo(sición)?",
    "festival": r"festival",
    "feria": r"feria",
    "concierto": r"concierto",
    "taller": r"taller",
    "conferencia": r"conferencia",
    "presentación": r"presentación",
    "función": r"función",
    "carrera": r"carrera",
    "desfile": r"desfile",
    "inauguración": r"inauguración",
    "torneo": r"torneo",
    "muestra": r"muestra",
    "jornada": r"jornada",
    "bazar": r"bazar",
    "maratón": r"maratón",
}

VENUE_ANCHORS = [
    "centro de convenciones",
    "teatro",
    "museo",
    "plaza",
    "parque",
    "auditorio",
    "estadio",
    "salón",
    "foro",
    "galería",
    "explanada",
    "arena",
    "recinto",
    "gimnasio",
    "coliseo",
]

MONTHS_ES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
    "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
    "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12,
}


def extract_city(text: str, article_city: str | None = None) -> str | None:
    if article_city:
        return article_city

    m = re.search(r"(Ciudad\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)\s*[.\-–—:]", text)
    if m:
        return m.group(1).strip()

    m = re.search(r"(?:^|\s)((?:[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+\s+){0,2}[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)\s*\.\-", text)
    if m:
        return m.group(1).strip()

    m = re.search(r"([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)*),\s*(?:Chih|Son|Coah|Dgo|NL|Jal|CDMX|Gto|Mex)\b", text)
    if m:
        return m.group(1).strip()

    return None


def extract_venue(text: str) -> str | None:
    for anchor in VENUE_ANCHORS:
        pattern = rf"(?:en\s+(?:el|la|los|las)\s+)?({re.escape(anchor)}\s+[A-ZÁÉÍÓÚÑa-záéíóúñ\s]+?)(?:[,.]|\s+a\s+partir|\s+donde|\s+el\s+día|\s+los\s+días|\s+este|\s+del|\s+desde)"
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            venue = m.group(1).strip()
            venue = re.sub(r"\s+", " ", venue)
            return venue

    pattern = r"en\s+(?:el|la|los|las)\s+([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑa-záéíóúñ\s]{3,50}?)(?:[,.]|\s+a\s+partir|\s+donde|\s+ubicad)"
    m = re.search(pattern, text)
    if m:
        return m.group(1).strip()

    return None


def extract_event_type(text: str) -> str | None:
    lower = text.lower()
    for event_type, pattern in EVENT_TYPES_MAP.items():
        if re.search(pattern, lower):
            return event_type
    return None


def extract_event_name(text: str) -> str | None:
    patterns = [
        r"(?:edición\s+(?:de\s+)?(?:la|el|del)\s+)((?:[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑa-záéíóúñ0-9]*\s*){2,8})",
        r"[«\"\"]((?:[A-ZÁÉÍÓÚÑa-záéíóúñ0-9]+\s*){2,8})[»\"\"]",
        r"(?:Expo|Festival|Feria|Concierto|Taller|Conferencia|Torneo|Carrera|Maratón)\s+((?:[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑa-záéíóúñ0-9]*\s*){1,6})",
    ]

    for pattern in patterns:
        m = re.search(pattern, text)
        if m:
            name = m.group(1).strip()
            if len(name) > 5:
                return name

    for event_type, type_pattern in EVENT_TYPES_MAP.items():
        m = re.search(rf"({type_pattern}\s+(?:[A-ZÁÉÍÓÚÑa-záéíóúñ0-9]+\s*){{1,5}})", text, re.IGNORECASE)
        if m:
            name = m.group(1).strip()
            if len(name) > 5:
                return name

    return None


def extract_organizer(text: str) -> str | None:
    patterns = [
        r"(?:La|El)\s+((?:Secretaría|Instituto|Municipio|Gobierno|Dirección|Coordinación|Departamento|Universidad|Comité|Consejo)\s+(?:de\s+)?(?:[A-ZÁÉÍÓÚÑa-záéíóúñ]+\s*){1,6})",
        r"((?:Secretaría|Instituto|Municipio|Gobierno|Dirección|Coordinación|Universidad|Comité|Consejo)\s+(?:de\s+)?(?:[A-ZÁÉÍÓÚÑa-záéíóúñ]+\s*){1,6})\s+(?:invita|convoca|organiza|presenta)",
        r"(?:organizad[oa]s?\s+por\s+(?:la|el)\s+)((?:[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑa-záéíóúñ]+\s*){2,6})",
    ]

    for pattern in patterns:
        m = re.search(pattern, text)
        if m:
            org = m.group(1).strip()
            org = re.sub(r"\s+(invita|convoca|organiza|presenta).*$", "", org)
            return org

    return None


def extract_admission(text: str) -> str | None:
    patterns = [
        (r"entrada\s+(libre|gratuita|general)", lambda m: m.group(1)),
        (r"la\s+entrada\s+es\s+(libre|gratuita|general)", lambda m: m.group(1)),
        (r"acceso\s+(libre|gratuito)", lambda m: m.group(1)),
        (r"sin\s+costo", lambda _: "gratuita"),
        (r"(?:costo|precio|boletos?)\s*(?:de\s*)?\$\s*([\d,]+(?:\.\d{2})?)", lambda m: f"${m.group(1)}"),
        (r"boletos\s+(?:desde|a\s+partir\s+de)\s+\$\s*([\d,]+)", lambda m: f"desde ${m.group(1)}"),
    ]

    for pattern, extractor in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            return extractor(m)

    return None


def _parse_spanish_date(text: str, reference_date: datetime | None = None) -> date | None:
    settings = {"PREFER_DATES_FROM": "future", "PREFER_DAY_OF_MONTH": "first"}
    if reference_date:
        settings["RELATIVE_BASE"] = reference_date

    parsed = dateparser.parse(text, languages=["es"], settings=settings)
    if parsed:
        return parsed.date()
    return None


def extract_dates(text: str, reference_date: datetime | None = None) -> tuple[date | None, date | None]:
    m = re.search(
        r"(?:sábado|domingo|lunes|martes|miércoles|jueves|viernes)\s+(\d{1,2})\s+y\s+"
        r"(?:sábado|domingo|lunes|martes|miércoles|jueves|viernes)\s+(\d{1,2})\s+de\s+"
        r"(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)",
        text,
        re.IGNORECASE,
    )
    if m:
        day1, day2 = int(m.group(1)), int(m.group(2))
        month = MONTHS_ES.get(m.group(3).lower())
        if month:
            year = reference_date.year if reference_date else datetime.now().year
            try:
                return date(year, month, day1), date(year, month, day2)
            except ValueError:
                pass

    m = re.search(
        r"del\s+(\d{1,2})\s+al\s+(\d{1,2})\s+de\s+"
        r"(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)",
        text,
        re.IGNORECASE,
    )
    if m:
        day1, day2 = int(m.group(1)), int(m.group(2))
        month = MONTHS_ES.get(m.group(3).lower())
        if month:
            year = reference_date.year if reference_date else datetime.now().year
            try:
                return date(year, month, day1), date(year, month, day2)
            except ValueError:
                pass

    m = re.search(
        r"(\d{1,2})\s+(?:y|al)\s+(\d{1,2})\s+de\s+"
        r"(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)",
        text,
        re.IGNORECASE,
    )
    if m:
        day1, day2 = int(m.group(1)), int(m.group(2))
        month = MONTHS_ES.get(m.group(3).lower())
        if month:
            year = reference_date.year if reference_date else datetime.now().year
            try:
                return date(year, month, day1), date(year, month, day2)
            except ValueError:
                pass

    single_patterns = [
        r"(?:este|próximo|el)\s+(?:lunes|martes|miércoles|jueves|viernes|sábado|domingo)\s+\d{1,2}\s+de\s+\w+",
        r"\d{1,2}\s+de\s+(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)(?:\s+de\s+\d{4})?",
        r"(?:este|próximo)\s+(?:lunes|martes|miércoles|jueves|viernes|sábado|domingo)",
    ]

    for pattern in single_patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            d = _parse_spanish_date(m.group(0), reference_date)
            if d:
                return d, None

    return None, None


def extract_times(text: str) -> tuple[time | None, time | None]:
    m = re.search(
        r"de\s+las?\s+(\d{1,2})[:\.]?(\d{2})?\s*"
        r"(?:de\s+la\s+(mañana|tarde|noche)|hrs|horas|am|pm)?\s*"
        r"(?:a|a\s+las?)\s+(\d{1,2})[:\.]?(\d{2})?\s*"
        r"(?:de\s+la\s+(mañana|tarde|noche)|hrs|horas|am|pm)?",
        text,
        re.IGNORECASE,
    )
    if m:
        start_h = int(m.group(1))
        start_m = int(m.group(2)) if m.group(2) else 0
        start_period = m.group(3)
        end_h = int(m.group(4))
        end_m = int(m.group(5)) if m.group(5) else 0
        end_period = m.group(6)

        start_h = _adjust_hour(start_h, start_period)
        end_h = _adjust_hour(end_h, end_period)

        try:
            return time(start_h, start_m), time(end_h, end_m)
        except ValueError:
            pass

    m = re.search(
        r"(?:a\s+partir\s+de\s+las?|desde\s+las?)\s+(\d{1,2})[:\.]?(\d{2})?\s*"
        r"(?:de\s+la\s+(mañana|tarde|noche)|hrs|horas|am|pm)?",
        text,
        re.IGNORECASE,
    )
    if m:
        h = int(m.group(1))
        mins = int(m.group(2)) if m.group(2) else 0
        period = m.group(3)
        h = _adjust_hour(h, period)
        try:
            return time(h, mins), None
        except ValueError:
            pass

    m = re.search(r"(\d{1,2}):(\d{2})\s*(am|pm|hrs|horas)", text, re.IGNORECASE)
    if m:
        h = int(m.group(1))
        mins = int(m.group(2))
        suffix = m.group(3).lower()
        if suffix == "pm" and h < 12:
            h += 12
        elif suffix == "am" and h == 12:
            h = 0
        try:
            return time(h, mins), None
        except ValueError:
            pass

    return None, None


def _adjust_hour(hour: int, period: str | None) -> int:
    if not period:
        return hour
    period = period.lower()
    if period in ("tarde", "noche", "pm") and hour < 12:
        return hour + 12
    if period in ("mañana", "am") and hour == 12:
        return 0
    return hour


def extract_evidence(text: str) -> str | None:
    patterns = [
        r"(invita\s+(?:a\s+)?(?:la\s+comunidad|al\s+público|a\s+asistir|a\s+participar).{0,150})",
        r"(se\s+(?:llevará\s+a\s+cabo|realizará|celebrará|efectuará).{0,150})",
        r"(tendrá\s+lugar.{0,150})",
    ]

    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            evidence = m.group(1).strip()
            if len(evidence) > 200:
                evidence = evidence[:200] + "..."
            return evidence

    return None


def extract_all(text: str, article_city: str | None = None, reference_date: datetime | None = None) -> dict:
    start_date, end_date = extract_dates(text, reference_date)
    start_time, end_time = extract_times(text)

    return {
        "event_name": extract_event_name(text),
        "city": extract_city(text, article_city),
        "venue": extract_venue(text),
        "start_date": start_date,
        "end_date": end_date,
        "start_time": start_time,
        "end_time": end_time,
        "admission": extract_admission(text),
        "organizer": extract_organizer(text),
        "event_type": extract_event_type(text),
        "evidence": extract_evidence(text),
    }
