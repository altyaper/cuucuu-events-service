from app.schemas import ArticleRequest

SAMPLE_EVENT_ARTICLE = ArticleRequest(
    title="Invitan a Expo Viaja Juárez 2026",
    body=(
        "Ciudad Juárez.- La Secretaría de Turismo invita a la comunidad a asistir "
        "este sábado 16 y domingo 17 de mayo a la quinta edición de la Expo Viaja "
        "Juárez 2026 en el centro de convenciones Injectronic, a partir de las 11:00 "
        "de la mañana a 8:00 de la noche, la entrada es libre."
    ),
    date="2026-05-15",
)

CRIME_ARTICLE = ArticleRequest(
    title="Detienen a presunto homicida en Ciudad Juárez",
    body=(
        "Ciudad Juárez.- Elementos de la Policía Municipal detuvieron a un hombre "
        "de 35 años de edad, presunto responsable del homicidio de un comerciante "
        "en la colonia Centro. El detenido fue puesto a disposición de la Fiscalía "
        "General del Estado para las investigaciones correspondientes."
    ),
    date="2026-05-15",
)

GOVERNMENT_ANNOUNCEMENT = ArticleRequest(
    title="Anuncia Municipio programa de pavimentación",
    body=(
        "Chihuahua.- El Gobierno Municipal anunció un programa de pavimentación "
        "que beneficiará a 15 colonias de la ciudad. El presidente municipal indicó "
        "que la inversión será de 120 millones de pesos y las obras iniciarán la "
        "próxima semana. Se espera que los trabajos concluyan en tres meses."
    ),
    date="2026-05-15",
)

EVENT_WITH_DATE_RANGE = ArticleRequest(
    title="Festival de Cine del Norte",
    body=(
        "Chihuahua.- Se llevará a cabo el Festival de Cine del Norte del 20 al 25 "
        "de junio en el Teatro de la Ciudad. La entrada es libre para todas las "
        "funciones. Se presentarán más de 30 cortometrajes de directores locales."
    ),
    date="2026-05-15",
)

PAST_EVENT_ARTICLE = ArticleRequest(
    title="Éxito en la Feria del Libro 2026",
    body=(
        "Ciudad Juárez.- Se realizó con éxito la Feria del Libro 2026 el pasado "
        "sábado en el centro de convenciones. Más de 5 mil personas asistieron "
        "al evento que se llevó a cabo durante tres días. Los organizadores "
        "calificaron la edición como la más exitosa."
    ),
    date="2026-05-15",
)

CONCERT_ARTICLE = ArticleRequest(
    title="Concierto de la Orquesta Sinfónica",
    body=(
        "Chihuahua.- La Secretaría de Cultura invita al público a asistir al "
        "concierto de la Orquesta Sinfónica de Chihuahua este viernes 23 de mayo "
        "a las 20:00 hrs en el Teatro de los Héroes. Los boletos tienen un costo "
        "de $150 pesos en taquilla."
    ),
    date="2026-05-20",
)
