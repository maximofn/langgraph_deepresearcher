"""
Prompt templates for the deep research system.

This module contains all prompt templates used across the research workflow components,
including user clarification, research brief generation, and report synthesis.
"""

clarify_with_user_instructions="""
Estos son los mensajes que se han intercambiado hasta ahora con el usuario que solicita el informe:
<Messages>
{messages}
</Messages>

La fecha de hoy es {date}.

Evalúa si necesitas hacer alguna pregunta aclaratoria o si el usuario ya te ha proporcionado suficiente información para comenzar la investigación.
IMPORTANTE: Si en el historial de mensajes ves que ya has hecho una pregunta aclaratoria, casi siempre no es necesario que hagas otra. Solo haz otra pregunta si es ABSOLUTAMENTE NECESARIO.

Si hay acrónimos, abreviaturas o términos desconocidos, pide al usuario que los aclare.
Si necesitas hacer una pregunta, sigue estas pautas:
 - Se conciso al recopilar toda la información necesaria.
 - Asegúrate de recopilar toda la información necesaria para llevar a cabo la tarea de investigación de forma concisa y bien estructurada.
 - Utiliza bullet points o listas numeradas si es necesario para mayor claridad. Asegúrate de que utilizas el formato Markdown y de que se mostrará correctamente si la cadena de salida se pasa a un renderizador Markdown.
 - No solicites información innecesaria o información que el usuario ya haya proporcionado. Si ves que el usuario ya ha proporcionado la información, no se la vuelvas a solicitar.

Responde en formato JSON válido con estas claves exactas:
"need_clarification": boolean,
"question": "<pregunta para pedir al usuario que aclare el alcance del informe>",
"verification": "<mensaje de verificación de que comenzaremos la investigación>"

Si necesitas hacer una pregunta aclaratoria, devuelve:
"need_clarification": true,
"question": "<tu pregunta aclaratoria>",
"verification": ""

Si no necesitas hacer una pregunta aclaratoria, devuelve:
"need_clarification": false,
"question": "",
"verification": "<Mensaje de confirmación de que ahora comenzará la investigación basándose en la información proporcionada.>"

Para el mensaje de verificación cuando no se necesita aclaración:
 - Confirma que tienes suficiente información para continuar.
 - Resume brevemente los aspectos clave de lo que entiendes de la solicitud.
 - Confirma que ahora comenzará el proceso de investigación.
 - Mantén el mensaje conciso y profesional.

Responde siempre en el idioma en el que el usuario te haya preguntado. En caso de duda, responde en español.
"""

transform_messages_into_research_topic_prompt = """Se te va a proporcionar un conjunto de mensajes que se han intercambiado hasta ahora entre el usuario y tú. 
Tu trabajo consiste en traducir estos mensajes en una pregunta de investigación más detallada y concreta que se utilizará para orientar la investigación.

Los mensajes que se han intercambiado hasta ahora entre el usuario y tú son:
<Messages>
{messages}
</Messages>

La fecha de hoy es {date}.

Devolverás una única pregunta de investigación que se utilizará para orientar la investigación.

Directrices:
1. Maximiza la especificidad y el detalle.
- Incluye todas las preferencias conocidas del usuario y enumera explícitamente los atributos o dimensiones clave a tener en cuenta.
- Es importante que todos los detalles del usuario se incluyan en las instrucciones.

2. Trata con cuidado las dimensiones no especificadas
- Cuando la calidad de la investigación requiera tener en cuenta dimensiones adicionales que el usuario no haya especificado, reconócelas como consideraciones abiertas en lugar de preferencias asumidas.
- Ejemplo: en lugar de asumir «opciones económicas», di «considerar todos los rangos de precios a menos que se especifiquen restricciones de coste».
- Solo menciona las dimensiones que sean realmente necesarias para una investigación exhaustiva en ese ámbito.

3. Evita suposiciones injustificadas
- Nunca inventes preferencias, restricciones o requisitos específicos del usuario que no se hayan indicado.
- Si el usuario no ha proporcionado un detalle concreto, señala explícitamente esta falta de especificación.
- Orienta al investigador para que trate los aspectos no especificados como flexibles en lugar de hacer suposiciones.

4. Distinguir entre el alcance de la investigación y las preferencias del usuario
- Alcance de la investigación: qué temas/dimensiones deben investigarse (puede ser más amplio que las menciones explícitas del usuario)
- Preferencias del usuario: restricciones, requisitos o preferencias específicos (solo debes incluir lo que el usuario haya indicado)
- Ejemplo: «Investigar los factores que influyen en la calidad del café (incluido el origen de los granos, los métodos de tostado y las técnicas de preparación) en las cafeterías de Madrid, centrándose principalmente en el sabor, tal y como ha especificado el usuario».

5. Utiliza la primera persona
- Redacta la solicitud desde la perspectiva del usuario.

6. Fuentes
- Si se debe dar prioridad a fuentes específicas, entonces específalas en la pregunta de investigación.
- Para la investigación de productos y viajes, es preferible enlazar directamente con sitios web oficiales o primarios (por ejemplo, sitios web oficiales de marcas, páginas de fabricantes o plataformas de comercio electrónico de renombre como Amazon para opiniones de usuarios) en lugar de sitios agregadores o blogs con mucho SEO.
- Para consultas académicas o científicas, es preferible enlazar directamente con el artículo original o la publicación oficial en una revista, en lugar de con artículos de encuestas o resúmenes secundarios.
- En el caso de personas, intente enlazar directamente con su perfil de LinkedIn, su sitio web personal o su perfil de GitHub, si lo tienen.
- Si la consulta está en un idioma específico, dé prioridad a las fuentes publicadas en ese idioma.

Responde siempre en el idioma en el que el usuario te haya preguntado. En caso de duda, responde en español.
"""