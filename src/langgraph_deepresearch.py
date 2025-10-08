"""
LangGraph Deep Research
"""

from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import HumanMessage

from scope.scope_agent import deep_researcher_graph_builder
from research.research_agent import agent_builder

from utils.message_utils import format_messages

from debug import PRINT_SCOPE_GRAPH, SAVE_SCOPE_GRAPH, PRINT_RESEARCH_GRAPH, SAVE_RESEARCH_GRAPH

# Create checkpointer and compile the scope graph
checkpointer = InMemorySaver()
scope_agent = deep_researcher_graph_builder.compile(checkpointer=checkpointer)
if PRINT_SCOPE_GRAPH: print(scope_agent.get_graph(xray=True).draw_ascii())
if SAVE_SCOPE_GRAPH: scope_agent.get_graph(xray=True).draw_mermaid_png(output_file_path="scope_graph_xray.png")

# Create thread and invoke the scope graph
# thread = {"configurable": {"thread_id": "1"}}
# result = scope_agent.invoke({"messages": [HumanMessage(content="Quiero investigar las mejores cafeterías de Madrid.")]}, config=thread)
# # format_messages(result['messages'])

# result = scope_agent.invoke({"messages": [HumanMessage(content="Examina la calidad del café para evaluar las mejores cafeterías de Madrid.")]}, config=thread)

# format_messages(result['messages'])
# format_messages(result['research_brief'], title="🔍 Research Brief", border_style="purple")


# Create checkpointer and compile the research graph
checkpointer = InMemorySaver()
research_agent = agent_builder.compile(checkpointer=checkpointer)
if PRINT_RESEARCH_GRAPH: print(research_agent.get_graph(xray=True).draw_ascii())
if SAVE_RESEARCH_GRAPH: research_agent.get_graph(xray=True).draw_mermaid_png(output_file_path="research_graph_xray.png")

research_brief = """Quiero identificar y evaluar las cafeterías de Madrid que se consideran las mejores basándome específicamente en la calidad del café. Mi investigación debe centrarse en analizar y comparar las cafeterías de la zona de Madrid, utilizando la calidad del café como criterio principal. Estoy abierto a métodos de evaluación de la calidad del café (por ejemplo, reseñas de expertos, valoraciones de clientes, certificaciones de café especial), y no hay restricciones en cuanto al ambiente, la ubicación, el wifi o las opciones de comida, a menos que afecten directamente a la calidad percibida del café. Por favor, da prioridad a las fuentes primarias, como los sitios web oficiales de las cafeterías, organizaciones de reseñas de café de terceros de renombre (como Coffee Review o Specialty Coffee Association) y agregadores de reseñas destacados como Google o Yelp, donde se pueden encontrar comentarios directos de los clientes sobre la calidad del café. El estudio debe dar como resultado una lista o clasificación bien fundamentada de las mejores cafeterías de Madrid, haciendo hincapié en la calidad de su café según los últimos datos disponibles en julio de 2025."""

# Create thread configuration for the research agent
thread = {"configurable": {"thread_id": "1"}}
result = research_agent.invoke({"researcher_messages": [HumanMessage(content=f"{research_brief}.")]}, config=thread)
# format_messages(result['researcher_messages'])