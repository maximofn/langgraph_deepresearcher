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
thread = {"configurable": {"thread_id": "1"}}
result = scope_agent.invoke({"messages": [HumanMessage(content="Quiero investigar las mejores cafeterías de Madrid.")]}, config=thread)
# format_messages(result['messages'])

result = scope_agent.invoke({"messages": [HumanMessage(content="Examina la calidad del café para evaluar las mejores cafeterías de Madrid.")]}, config=thread)

research_brief = result.get("research_brief", None)
if not research_brief:
    print("No research brief found")
    exit()

# format_messages(result['messages'])
# format_messages(result['research_brief'], title="🔍 Research Brief", border_style="purple")

# Create checkpointer and compile the research graph
research_agent = agent_builder.compile(checkpointer=checkpointer)
if PRINT_RESEARCH_GRAPH: print(research_agent.get_graph(xray=True).draw_ascii())
if SAVE_RESEARCH_GRAPH: research_agent.get_graph(xray=True).draw_mermaid_png(output_file_path="research_graph_xray.png")

research_brief = result["research_brief"]

# Create thread configuration for the research agent
result = research_agent.invoke({"researcher_messages": [HumanMessage(content=f"{research_brief}.")]}, config=thread)
# format_messages(result['researcher_messages'])