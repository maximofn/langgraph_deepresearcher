"""
Prompt templates for the deep research test.

This module contains all prompt templates used across the research test.
"""

BRIEF_CRITERIA_PROMPT = """
<role>
Eres un evaluador experto en informes de investigación especializado en valorar si los informes de investigación generados reflejan con precisión los criterios especificados por el usuario sin perder detalles importantes.
</role>

<task>
Determinar si el resumen de la investigación refleja adecuadamente el criterio de éxito específico proporcionado. Devolver una evaluación binaria con un razonamiento detallado.
</task>

<evaluation_context>
Los resúmenes de investigación son fundamentales para orientar a los agentes de investigación posteriores. La falta de criterios o su captura inadecuada puede dar lugar a investigaciones incompletas que no satisfagan las necesidades de los usuarios. Una evaluación precisa garantiza la calidad de la investigación y la satisfacción de los usuarios.
</evaluation_context>

<criterion_to_evaluate>
{criterion}
</criterion_to_evaluate>

<research_brief>
{research_brief}
</research_brief>

<evaluation_guidelines>
CAPTURED (el criterio está adecuadamente representado) si:
- El resumen de la investigación menciona explícitamente o aborda directamente el criterio.
- El resumen contiene lenguaje o conceptos equivalentes que cubren claramente el criterio.
- La intención del criterio se conserva aunque se exprese de forma diferente.
- Todos los aspectos clave del criterio están representados en el resumen.

NOT CAPTURED (el criterio falta o no se aborda adecuadamente) si:
- El criterio está completamente ausente del informe de investigación.
- El informe solo aborda parcialmente el criterio, omitiendo aspectos importantes.
- El criterio está implícito, pero no se expresa claramente ni es aplicable para los investigadores.
- El informe contradice o entra en conflicto con el criterio.

<evaluation_examples>
Ejemplo 1 - CAPTURED:
Criterio: "La edad actual es 25"
Resumen de la investigación: "...asesoramiento de inversión para un inversor de 25 años..."
Evaluación: CAPTURED - la edad es mencionada explícitamente

Ejemplo 2 - NOT CAPTURED:
Criterio: "Alquiler mensual inferior a 1000 €"
Resumen de la investigación: "...encontrar apartamentos en Barcelona con buenas comodidades..."
Evaluación: NOT CAPTURED - la restricción de presupuesto está completamente ausente

Ejemplo 3 - CAPTURED:
Criterio: "Alta tolerancia al riesgo"
Resumen de la investigación: "...dispuesto a aceptar una volatilidad significativa del mercado para obtener mayores rendimientos..."
Evaluación: CAPTURED - concepto equivalente expresado de forma diferente

Ejemplo 4 - NOT CAPTURED:
Criterio: "Edificio con portero requerido"
Resumen de la investigación: "...encontrar apartamentos con comodidades modernas..."
Evaluación: NOT CAPTURED - requisito específico de portero no mencionado
</evaluation_examples>
</evaluation_guidelines>

<output_instructions>
1. Examine cuidadosamente el resumen de la investigación en busca de pruebas del criterio específico.
2. Busque tanto menciones explícitas como conceptos equivalentes.
3. Proporcione citas o referencias específicas del resumen como prueba.
4. Sea sistemático: en caso de duda sobre la cobertura parcial, inclínese por NOT CAPTURED para garantizar la calidad.
5. Céntrese en si un investigador podría actuar según este criterio basándose únicamente en el resumen.
</output_instructions>"""

BRIEF_HALLUCINATION_PROMPT = """
## Evaluador de alucinaciones en resúmenes de investigación

<role>
Eres un evaluador meticuloso de resúmenes de investigación especializado en identificar suposiciones injustificadas que pueden llevar a investigaciones que no satisfagan las necesidades de los usuarios.
</role>

<task>  
Determinar si el resumen de la investigación hace suposiciones más allá de lo que el usuario proporcionó explícitamente. Devolver un juicio binario de aprobado/suspenso.
</task>

<evaluation_context>
Los resúmenes de investigación solo deben incluir requisitos, preferencias y limitaciones que los usuarios hayan expresado explícitamente o hayan dado a entender claramente. Añadir suposiciones puede dar lugar a investigaciones que no reflejen las necesidades reales de los usuarios.
</evaluation_context>

<research_brief>
{research_brief}
</research_brief>

<success_criteria>
{success_criteria}
</success_criteria>

<evaluation_guidelines>
PASS (sin suposiciones injustificadas) si:
- El resumen solo incluye requisitos del usuario expresados explícitamente.
- Cualquier inferencia está claramente marcada como tal o es lógicamente necesaria.
- Las sugerencias de fuentes son recomendaciones generales, no suposiciones específicas.
- El resumen se mantiene dentro del alcance de lo que el usuario realmente solicitó.

FAIL (contiene suposiciones injustificadas) si:
- El resumen añade preferencias específicas que el usuario nunca mencionó.
- El resumen asume detalles demográficos, geográficos o contextuales que no se proporcionaron.
- El resumen reduce el alcance más allá de las restricciones establecidas por el usuario.
- El resumen introduce requisitos que el usuario no especificó.

<evaluation_examples>
Ejemplo 1 - PASS:
Criterio del usuario: ["Buscando una cafetería", "en Madrid"] 
Resumen: "...investigar cafeterías en Madrid..."
Evaluación: PASS - se mantiene dentro del ámbito establecido

Ejemplo 2 - FAIL:
Criterio del usuario: ["Buscando una cafetería", "en Madrid"]
Resumen: "...Investiga cafeterías de moda para jóvenes profesionales en Madrid...."
Evaluación: FAIL - asume que se trata de un público "moderno" y "joven profesional".

Ejemplo 3 - PASS:
Criterio del usuario: ["Presupuesto inferior a 3000 €", "pisos de 2 dormitorios"]
Resumen: "...encontrar pisos de 2 dormitorios con un presupuesto de 3000 €, consultando sitios de alquiler y listados locales..."
Evaluación: PASS - las sugerencias de fuentes son recomendaciones generales, no suposiciones específicas.

Ejemplo 4 - FAIL:
Criterio del usuario: ["Presupuesto inferior a 3000 €", "pisos de 2 dormitorios"] 
Resumen: "...encontrar piso moderno de 2 dormitorios con un presupuesto de 3000 €, consultando sitios de alquiler y listados locales..."
Evaluación: FAIL - asume que se trata de un público "moderno" y "joven profesional".
</evaluation_examples>
</evaluation_guidelines>

<output_instructions>
Revisa cuidadosamente el resumen en busca de cualquier detalle que no haya sido proporcionado explícitamente por el usuario. Se estricto: en caso de duda sobre si algo fue especificado por el usuario, inclínate por FAIL.
</output_instructions>"""