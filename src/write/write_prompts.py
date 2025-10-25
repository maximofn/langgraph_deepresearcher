final_report_generation_prompt = """Basándose en toda la investigación realizada, elabore una respuesta completa y bien estructurada al resumen general de la investigación.:
<Research Brief>
{research_brief}
</Research Brief>

IMPORTANTE: ¡Asegúrate de que la respuesta esté escrita en el mismo idioma que los mensajes humanos!
Por ejemplo, si los mensajes del usuario están en inglés, ASEGÚRATE de escribir tu respuesta en inglés. Si los mensajes del usuario están en español, ASEGÚRATE de escribir toda tu respuesta en español.
Esto es muy importante. El usuario solo entenderá la respuesta si está escrita en el mismo idioma que su mensaje de entrada.

La fecha de hoy es {date}.

Estos son los resultados de la investigación que ha llevado a cabo.:
<Findings>
{findings}
</Findings>

Por favor, redacte una respuesta detallada al resumen general de la investigación que:
1. Esté bien organizada con los encabezados adecuados (# para el título, ## para las secciones, ### para las subsecciones).
2. Incluya datos y conclusiones específicos de la investigación.
3. Haga referencia a fuentes relevantes utilizando el formato [Título](URL).
4. Proporcione un análisis equilibrado y exhaustivo. Sea lo más completo posible e incluya toda la información relevante para la pregunta de investigación general. Las personas le utilizan para realizar investigaciones profundas y esperan respuestas detalladas y completas.
5. Incluya una sección «Fuentes» al final con todos los enlaces a los que se hace referencia.

Puede estructurar su informe de diferentes maneras. A continuación se muestran algunos ejemplos.:

Para responder a una pregunta que te pide comparar dos cosas, puedes estructurar tu informe de la siguiente manera:
1/ introducción
2/ resumen del tema A
3/ resumen del tema B
4/ comparación entre A y B
5/ conclusión

Para responder a una pregunta que te pide que devuelvas una lista de cosas, es posible que solo necesites una única sección que sea la lista completa.
1/ lista de cosas o tabla de cosas
O bien, puedes optar por convertir cada elemento de la lista en una sección independiente del informe. Cuando se te piden listas, no necesitas una introducción ni una conclusión.
1/ elemento 1
2/ elemento 2
3/ elemento 3

Para responder a una pregunta que te pide resumir un tema, hacer un informe o dar una visión general, puedes estructurar tu informe de la siguiente manera:
1/ visión general del tema
2/ concepto 1
3/ concepto 2
4/ concepto 3
5/ conclusión

Si crees que puedes responder a la pregunta con una sola sección, ¡también puedes hacerlo!
1/ respuesta

RECUERDA: La sección es un concepto MUY fluido y flexible. Puedes estructurar tu informe como mejor te parezca, ¡incluso de formas que no se mencionan arriba!
Asegúrate de que tus secciones sean coherentes y tengan sentido para el lector.

Para cada sección del informe, haz lo siguiente:
- Usa un lenguaje sencillo y claro.
- Usa ## para el título de la sección (formato Markdown) para cada sección del informe.
- NO se refiera nunca a sí mismo como el autor del informe. Debe ser un informe profesional sin lenguaje autorreferencial. 
- No mencione lo que está haciendo en el informe. Simplemente redacte el informe sin comentarios personales.
- Cada sección debe tener la extensión necesaria para responder en profundidad a la pregunta con la información que ha recopilado. Se espera que las secciones sean bastante largas y detalladas. Está redactando un informe de investigación en profundidad y los usuarios esperarán una respuesta exhaustiva.
- Utilice viñetas para enumerar la información cuando sea apropiado, pero, por defecto, redacte en forma de párrafos.

RECUERDE:
El resumen y la investigación pueden estar en español, pero debe traducir esta información al idioma adecuado al redactar la respuesta final.
Asegúrese de que el informe de la respuesta final esté en el MISMO idioma que los mensajes humanos del historial de mensajes.

Formatee el informe con un marcado claro y una estructura adecuada, e incluya referencias a las fuentes cuando sea necesario.

<Citation Rules>
- Asigne a cada URL única un número de citación único en su texto.
- Termine con ### Fuentes, donde se enumeran todas las fuentes con los números correspondientes.
- IMPORTANTE: Numere las fuentes de forma secuencial y sin saltos (1, 2, 3, 4...) en la lista final, independientemente de las fuentes que elija.
- Cada fuente debe ser un elemento independiente en una lista, de modo que en el marcado se muestre como una lista.
- Ejemplo de formato:
  [1] Título de la fuente: URL
  [2] Título de la fuente: URL
- Las citas son extremadamente importantes. Asegúrese de incluirlas y preste mucha atención a que sean correctas. Los usuarios suelen utilizar estas citas para buscar más información.
</Citation Rules>
"""

