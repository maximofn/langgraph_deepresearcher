"""
LangGraph Deep Research
"""

from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import HumanMessage

from scope.research_agent_scope import deep_researcher_graph_builder

from utils.message_utils import format_messages

from debug import PRINT_SCOPE_GRAPH, SAVE_SCOPE_GRAPH

# Create checkpointer and compile the scope graph
checkpointer = InMemorySaver()
scope_graph = deep_researcher_graph_builder.compile(checkpointer=checkpointer)
if PRINT_SCOPE_GRAPH: print(scope_graph.get_graph(xray=True).draw_ascii())
if SAVE_SCOPE_GRAPH: scope_graph.get_graph(xray=True).draw_mermaid_png(output_file_path="scope_graph_xray.png")

# Create thread and invoke the scope graph
# thread = {"configurable": {"thread_id": "1"}}
# result = scope_graph.invoke({"messages": [HumanMessage(content="Quiero investigar las mejores cafeterías de Madrid.")]}, config=thread)
# # format_messages(result['messages'])

# result = scope_graph.invoke({"messages": [HumanMessage(content="Examina la calidad del café para evaluar las mejores cafeterías de Madrid.")]}, config=thread)

# format_messages(result['messages'])
# format_messages(result['research_brief'], title="🔍 Research Brief", border_style="purple")