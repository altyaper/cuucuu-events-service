import json
import logging
from datetime import date, datetime, time

from openai import OpenAI

from app.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
Eres un extractor de eventos. A partir del texto de un artículo de noticias, extrae los detalles del evento mencionado.

Responde ÚNICAMENTE con un objeto JSON con estos campos:
- "event_name": nombre limpio y conciso del evento (no el titular del artículo)
- "description": resumen de 1-2 oraciones para mostrar en una tarjeta
- "dates": lista de fechas ISO (YYYY-MM-DD) en las que ocurre el evento
- "start_time": hora de inicio en formato HH:MM (24h) o null
- "end_time": hora de fin en formato HH:MM (24h) o null
- "city": nombre de la ciudad
- "venue": lugar específico (teatro, parque, centro de convenciones, etc.)
- "event_type": una de: expo, festival, feria, concierto, taller, conferencia, presentación, función, carrera, desfile, inauguración, torneo, muestra, jornada, bazar, maratón, otro

Reglas para fechas:
- Si el artículo dice "hoy", "esta noche", etc., usa la fecha de publicación proporcionada.
- Si dice "mañana", suma un día a la fecha de publicación.
- Si dice "este sábado", calcula la fecha del próximo sábado desde la fecha de publicación.
- Si es un rango (ej. "del 8 al 10 de agosto"), incluye TODAS las fechas individuales.
- Si no hay fecha mencionada, devuelve una lista vacía.

Si algún campo no se puede determinar, usa null (o lista vacía para dates).\
"""


def _build_user_prompt(title: str, content: str, published_at: datetime | None) -> str:
    pub_date = ""
    if published_at:
        pub_date = f"\nFecha de publicación del artículo: {published_at.strftime('%Y-%m-%d')}"

    return f"Título del artículo: {title}\n{pub_date}\n\nContenido:\n{content[:3000]}"


def refine(title: str, content: str, published_at: datetime | None = None) -> dict | None:
    if not settings.openai_api_key:
        logger.warning("OpenAI API key not configured, skipping refinement")
        return None

    client = OpenAI(api_key=settings.openai_api_key)

    try:
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": _build_user_prompt(title, content, published_at)},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=800,
            timeout=30,
        )

        raw = response.choices[0].message.content
        data = json.loads(raw)

        return {
            "event_name": data.get("event_name"),
            "description": data.get("description"),
            "dates": _parse_dates(data.get("dates", [])),
            "start_date": None,
            "end_date": None,
            "start_time": _parse_time(data.get("start_time")),
            "end_time": _parse_time(data.get("end_time")),
            "city": data.get("city"),
            "venue": data.get("venue"),
            "event_type": data.get("event_type"),
            "admission": None,
            "organizer": None,
            "evidence": None,
        }

    except Exception as e:
        logger.error(f"OpenAI refinement failed: {e}")
        return None


def _parse_dates(dates_raw: list) -> list[date]:
    parsed = []
    for d in dates_raw or []:
        try:
            parsed.append(date.fromisoformat(d))
        except (ValueError, TypeError):
            continue
    return sorted(parsed)


def _parse_time(time_str: str | None) -> time | None:
    if not time_str:
        return None
    try:
        parts = time_str.split(":")
        return time(int(parts[0]), int(parts[1]))
    except (ValueError, IndexError):
        return None
