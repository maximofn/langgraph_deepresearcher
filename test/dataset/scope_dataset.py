"""
Dataset for the scope deep research test.
"""

from langchain_core.messages import AIMessage, HumanMessage

# ===== DATASET =====
# Create the conversation
conversation_1 = [
    HumanMessage(content="¿Cuál es la mejor manera de invertir 50.000 € para la jubilación?"),
    AIMessage(content="Puedes proporcionarme información adicional para adaptar el asesoramiento de inversión a tu objetivo de jubilación de $50.000 €? En concreto:\n * Tu edad actual o la edad a la que deseas jubilarte\n * Tu tolerancia al riesgo (baja, media, alta)\n * Cualquier preferencia en cuanto a tipos de inversión (por ejemplo, acciones, bonos, fondos de inversión, bienes inmuebles)\n * Si inviertes a través de una cuenta con ventajas fiscales (por ejemplo, IRA, 401(k)) o una cuenta de corretaje normal\nEsto me ayudará a ofrecerle sugerencias más personalizadas y relevantes."),
    HumanMessage(content="Tengo 25 años y quiero jubilarme a los 45. Ahora mismo tengo una alta tolerancia al riesgo, pero creo que irá disminuyendo con el tiempo. He oído que las acciones y los ETF son una buena opción, pero estoy abierto a cualquier posibilidad. Ya tengo un plan 401k, pero esto sería solo a través de una cuenta de corretaje normal."),
]

conversation_2 = [
    HumanMessage(content="Estoy buscando un piso en Madrid, ¿me puedes ayudar?"),
    AIMessage(content="¿Podrías especificar tus preferencias en cuanto al piso? Por ejemplo:\n * Barrios o distritos deseados\n * Número de dormitorios/baños\n * Rango de presupuesto (alquiler mensual)\n * Cualquier comodidad o característica imprescindible\n * Fecha de mudanza preferida\nEsta información me ayudará a ofrecerte las opciones de apartamentos más relevantes en Madrid."),
    HumanMessage(content="Prefiero vivir en Lavapies, Chueca o Salamanca. Busco un piso de dos dormitorios y dos baños, con un alquiler mensual inferior a 1000 €. Me gustaría que fuera un edificio con portero, pero no pasa nada si no lo tiene. Sería un plus que cerca hubiera un gimnasio. Y me gustaría mudarme en diciembre de 2025."),
]

criteria_1 = [
    "La edad actual es 25",
    "La edad de jubilación deseada es 45",
    "La tolerancia al riesgo es alta",
    "Está interesado en invertir en acciones y ETFs",
    "Está abierto a formas de inversión más allá de acciones y ETFs"
    "La cuenta de inversión es una cuenta de corretaje regular",
]

criteria_2 = [
    "Buscando un piso de dos dormitorios y dos baños en Lavapies, Chueca o Salamanca",
    "El alquiler mensual es inferior a 1000 €",
    "Debe estar en un edificio con portero, pero no estrictamente necesario",
    "Idealmente cerca haya un gimnasio, pero no estrictamente necesario",
    "La fecha de mudanza es diciembre de 2025"
]