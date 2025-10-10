"""
LangGraph Deep Research
"""

from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import HumanMessage

from scope.scope_agent import deep_researcher_graph_builder
from research.research_agent import agent_builder
from research_mcp.research_mcp_agent import agent_builder_mcp

from utils.message_utils import format_messages

from debug import PRINT_SCOPE_GRAPH, SAVE_SCOPE_GRAPH, PRINT_RESEARCH_GRAPH, SAVE_RESEARCH_GRAPH

import asyncio

MCP = True

async def main():
    # Create checkpointer and compile the scope graph
    checkpointer = InMemorySaver()
    scope_agent = deep_researcher_graph_builder.compile(checkpointer=checkpointer)
    if PRINT_SCOPE_GRAPH: print(scope_agent.get_graph(xray=True).draw_ascii())
    if SAVE_SCOPE_GRAPH: scope_agent.get_graph(xray=True).draw_mermaid_png(output_file_path="scope_graph_xray.png")

    # Create thread and invoke the scope graph
    thread = {"configurable": {"thread_id": "1"}}
    result = scope_agent.invoke({"messages": [HumanMessage(content="Quiero investigar las mejores cafeterías de Madrid.")]}, config=thread)

    # Create clarification question
    result = scope_agent.invoke({"messages": [HumanMessage(content="Examina la calidad del café para evaluar las mejores cafeterías de Madrid.")]}, config=thread)

    research_brief = result.get("research_brief", None)
    if not research_brief:
        print("No research brief found")
        exit()

    # Create checkpointer and compile the research graph
    if MCP:
        research_agent = agent_builder_mcp.compile(checkpointer=checkpointer)
    else:
        research_agent = agent_builder.compile(checkpointer=checkpointer)
    if PRINT_RESEARCH_GRAPH: print(research_agent.get_graph(xray=True).draw_ascii())
    if SAVE_RESEARCH_GRAPH: research_agent.get_graph(xray=True).draw_mermaid_png(output_file_path="research_graph_xray.png")

    # Create thread configuration for the research agent
    # Use ainvoke when MCP is enabled (async required) because MCP functions are async
    if MCP:
        result = await research_agent.ainvoke({"researcher_messages": [HumanMessage(content=f"{research_brief}.")]}, config=thread)
    else:
        result = research_agent.invoke({"researcher_messages": [HumanMessage(content=f"{research_brief}.")]}, config=thread)


if __name__ == "__main__":
    asyncio.run(main())