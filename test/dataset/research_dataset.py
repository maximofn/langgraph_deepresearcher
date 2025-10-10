from langchain_core.messages import AIMessage, ToolMessage, HumanMessage

# Scenario 1: Agent should CONTINUE - has insufficient/irrelevant information + think_tool realizes more research needed
messages_should_continue = [
    HumanMessage(content="¿Cuáles son las mejores cafeterías de Madrid en cuanto a la calidad del café?"),
    AIMessage(
        content="Buscaré información sobre las mejores cafeterías de Madrid, centrándome en la calidad del café.",
        tool_calls=[
            {
                "name": "tavily_search",
                "args": {
                    "query": "Cafeterías populares en Madrid"
                },
                "id": "call_continue_search_001",
                "type": "tool_call"
            }
        ]
    ),
    # Tavily Search provides generic cafe information - NOT focused on coffee quality
    ToolMessage(
        content="Los resultados de la búsqueda muestran cafeterías populares de Madrid: Blue Bottle Coffee tiene una excelente conexión wifi y un ambiente agradable, Philz Coffee es conocida por sus mezclas personalizadas y su servicio amable, Café Reveille tiene varios locales con buenos pasteles y espacios adecuados para trabajar con el ordenador portátil. Ritual Coffee ofrece asientos acogedores y es muy popular entre los estudiantes.",
        tool_call_id="call_continue_search_001",
    ),
    # Agent uses think_tool to reflect and realizes the search results are insufficient
    AIMessage(
        content="Permítanme utilizar la herramienta think_tool para analizar estos resultados de búsqueda y determinar los siguientes pasos.",
        tool_calls=[
            {
                "name": "think_tool",
                "args": {
                    "reflection": "Análisis de los resultados de la búsqueda: La información que encontré se centra en características generales de las cafeterías, como wifi, ambiente, mezclas personalizadas y asientos, pero carece de métricas específicas sobre la calidad del café. El usuario solicitó específicamente una evaluación basada en la calidad del café, lo que requeriría reseñas de expertos, calificaciones profesionales, certificaciones de especialidad o comentarios de clientes centrados en la calidad. Necesito buscar específicamente evaluaciones de la calidad del café, puntuaciones de Coffee Review, credenciales de café especial o evaluaciones de expertos de cafeterías de Madrid. La información actual es insuficiente para responder a la pregunta del usuario sobre la calidad del café."
                },
                "id": "call_continue_think_001",
                "type": "tool_call"
            }
        ]
    ),
    # think_tool response identifies the gap and need for more targeted research
    ToolMessage(
        content="Reflexión registrada: Análisis de los resultados de la búsqueda: La información que encontré se centra en características generales de las cafeterías, como wifi, ambiente, mezclas personalizadas y asientos, pero carece de métricas específicas sobre la calidad del café. El usuario solicitó específicamente una evaluación basada en la calidad del café, lo que requeriría reseñas de expertos, calificaciones profesionales, certificaciones de especialidad o comentarios de clientes centrados en la calidad. Necesito buscar específicamente evaluaciones de la calidad del café, puntuaciones de Coffee Review, credenciales de café especial o evaluaciones de expertos de cafeterías de Madrid. La información actual es insuficiente para responder a la pregunta del usuario sobre la calidad del café.",
        tool_call_id="call_continue_think_001",
    )
]

# Scenario 2: Agent should STOP - has comprehensive coffee quality information + think_tool reflection
messages_should_stop = [
    HumanMessage(content="¿Cuáles son las mejores cafeterías de Madrid en cuanto a la calidad del café?"),
    AIMessage(
        content="Investigaré las cafeterías de Madrid centrándome específicamente en las evaluaciones de la calidad del café y las opiniones de los expertos.",
        tool_calls=[
            {
                "name": "tavily_search",
                "args": {
                    "query": "La mejor calidad de café. Opiniones de expertos en café especial de Madrid. Calificaciones de Coffee Review 2025."
                },
                "id": "call_stop_search_001", 
                "type": "tool_call"
            }
        ]
    ),
    # This ToolMessage provides COMPREHENSIVE coffee quality information - sufficient to answer the question
    ToolMessage(
        content="""Una investigación sobre la calidad del café en Madrid revela los mejores establecimientos según las opiniones de expertos y las credenciales de café especial:

**Cafeterías que se centran en la máxima calidad:**
1. **Sightglass Coffee**: puntuación de 94/100 en Coffee Review, conocida por sus granos de origen único y sus precisas técnicas de tostado. Aparece en la lista de Bon Appétit de «El mejor café de Estados Unidos» por la excepcional calidad de su café.

2. **Saint Frank Coffee**: clasificada como la tercera cafetería de Estados Unidos por The Daily Meal en función de la calidad del café. Puntuación de 4,3/5 en Yelp, con reseñas que elogian específicamente la «calidad excepcional de los granos» y la «extracción perfecta».

3. **Ritual Coffee Roasters**: miembro de la Specialty Coffee Association, relaciones comerciales directas, puntuación constante de 4,4/5 en Google con reseñas que destacan el «sabor superior del café» y las «habilidades expertas de los baristas».

4. **Blue Bottle Coffee**: pionero del café de tercera ola, puntuación media de 90+/100 en Coffee Review, conocido por su riguroso control de calidad y sus prácticas de tueste fresco.

5. **Four Barrel Coffee**: tostador local con puntuaciones de 88-92/100 en Coffee Review, elogiado por los expertos del sector por la «calidad excepcional del café» y los métodos de elaboración innovadores.

**Indicadores de calidad encontrados:**
- Puntuaciones profesionales de Coffee Review (entre 88 y 94/100).
- Certificaciones de la Specialty Coffee Association.
- Comercio directo/abastecimiento de origen único.
- Reconocimiento de expertos de publicaciones gastronómicas.
- Opiniones de clientes que mencionan específicamente el sabor y la calidad del café.

Esto proporciona una evaluación exhaustiva de las cafeterías de Madrid basada específicamente en la calidad del café, en lugar del ambiente o el servicio.""",
        tool_call_id="call_stop_search_001",
    ),
    # Agent now uses think_tool to reflect on the search results
    AIMessage(
        content="Permítanme reflexionar sobre los resultados de la búsqueda utilizando la herramienta think_tool para evaluar si dispongo de información suficiente.",
        tool_calls=[
            {
                "name": "think_tool",
                "args": {
                    "reflection": "Análisis de los resultados de la búsqueda: he encontrado información exhaustiva sobre la calidad del café de las cafeterías de Madrid, incluyendo: 1) puntuaciones de Professional Coffee Review (88-94/100), 2) clasificaciones de expertos de publicaciones de renombre, 3) certificaciones de la Specialty Coffee Association, 4) indicadores de calidad específicos (origen único, técnicas de tostado, métodos de extracción), 5) los cinco establecimientos mejor valorados con evaluaciones detalladas de la calidad. Esto cubre todos los aspectos solicitados: reseñas de expertos, valoraciones de clientes, certificaciones de especialidad. Tengo suficiente información para ofrecer una clasificación bien fundamentada basada específicamente en la calidad del café. No es necesario realizar búsquedas adicionales: ahora debería proporcionar mi respuesta completa."
                },
                "id": "call_think_001",
                "type": "tool_call"
            }
        ]
    ),
    # think_tool response confirming reflection was recorded
    ToolMessage(
        content="Reflexión registrada: Análisis de los resultados de la búsqueda: he encontrado información completa sobre la calidad del café de las cafeterías de Madrid, incluyendo: 1) puntuaciones de Professional Coffee Review (88-94/100), 2) clasificaciones de expertos de publicaciones de renombre, 3) certificaciones de la Specialty Coffee Association, 4) indicadores de calidad específicos (origen único, técnicas de tostado, métodos de extracción), 5) cinco establecimientos mejor valorados con evaluaciones detalladas de la calidad. Esto cubre todos los aspectos solicitados: reseñas de expertos, valoraciones de clientes, certificaciones de especialidad. Tengo suficiente información para proporcionar una clasificación bien fundamentada basada específicamente en la calidad del café. No es necesario realizar búsquedas adicionales: ahora debería proporcionar mi respuesta completa.",
        tool_call_id="call_think_001",
    )
]