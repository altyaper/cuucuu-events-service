from datetime import datetime

import pytest

from app.schemas import ArticleInput

SAMPLE_EVENT_ARTICLE = ArticleInput(
    id=1,
    title="Invitan a Expo Viaja Juárez 2026",
    content=(
        "Ciudad Juárez.- La Secretaría de Turismo invita a la comunidad a asistir "
        "este sábado 16 y domingo 17 de mayo a la quinta edición de la Expo Viaja "
        "Juárez 2026 en el centro de convenciones Injectronic, a partir de las 11:00 "
        "de la mañana a 8:00 de la noche, la entrada es libre."
    ),
    published_at=datetime(2026, 5, 15),
)

CRIME_ARTICLE = ArticleInput(
    id=2,
    title="Detienen a presunto homicida en Ciudad Juárez",
    content=(
        "Ciudad Juárez.- Elementos de la Policía Municipal detuvieron a un hombre "
        "de 35 años de edad, presunto responsable del homicidio de un comerciante "
        "en la colonia Centro. El detenido fue puesto a disposición de la Fiscalía "
        "General del Estado para las investigaciones correspondientes."
    ),
    published_at=datetime(2026, 5, 15),
)

GOVERNMENT_ANNOUNCEMENT = ArticleInput(
    id=3,
    title="Anuncia Municipio programa de pavimentación",
    content=(
        "Chihuahua.- El Gobierno Municipal anunció un programa de pavimentación "
        "que beneficiará a 15 colonias de la ciudad. El presidente municipal indicó "
        "que la inversión será de 120 millones de pesos y las obras iniciarán la "
        "próxima semana. Se espera que los trabajos concluyan en tres meses."
    ),
    published_at=datetime(2026, 5, 15),
)

EVENT_WITH_DATE_RANGE = ArticleInput(
    id=4,
    title="Festival de Cine del Norte",
    content=(
        "Chihuahua.- Se llevará a cabo el Festival de Cine del Norte del 20 al 25 "
        "de junio en el Teatro de la Ciudad. La entrada es libre para todas las "
        "funciones. Se presentarán más de 30 cortometrajes de directores locales."
    ),
    published_at=datetime(2026, 5, 15),
)

PAST_EVENT_ARTICLE = ArticleInput(
    id=5,
    title="Éxito en la Feria del Libro 2026",
    content=(
        "Ciudad Juárez.- Se realizó con éxito la Feria del Libro 2026 el pasado "
        "sábado en el centro de convenciones. Más de 5 mil personas asistieron "
        "al evento que se llevó a cabo durante tres días. Los organizadores "
        "calificaron la edición como la más exitosa."
    ),
    published_at=datetime(2026, 5, 15),
)

CONCERT_ARTICLE = ArticleInput(
    id=6,
    title="Concierto de la Orquesta Sinfónica",
    content=(
        "Chihuahua.- La Secretaría de Cultura invita al público a asistir al "
        "concierto de la Orquesta Sinfónica de Chihuahua este viernes 23 de mayo "
        "a las 20:00 hrs en el Teatro de los Héroes. Los boletos tienen un costo "
        "de $150 pesos en taquilla."
    ),
    published_at=datetime(2026, 5, 20),
)
