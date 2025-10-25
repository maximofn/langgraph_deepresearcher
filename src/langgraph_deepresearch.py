"""
LangGraph Deep Research
"""

from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import HumanMessage

from write.write_agent import writer_builder

from debug import PRINT_WRITER_GRAPH, SAVE_WRITER_GRAPH

import asyncio

from rich.console import Console
from rich.markdown import Markdown

async def main():
    # Create checkpointer
    checkpointer = InMemorySaver()

    # Compile the deep researcher agent graph
    deep_researcher_agent = writer_builder.compile(checkpointer=checkpointer)
    if PRINT_WRITER_GRAPH: print(deep_researcher_agent.get_graph(xray=True).draw_ascii())
    if SAVE_WRITER_GRAPH: deep_researcher_agent.get_graph(xray=True).draw_mermaid_png(output_file_path="writer_graph_xray.png")
    
    # Create thread
    thread = {"configurable": {"thread_id": "1"}}
    
    # Invoke the deep researcher agent
    # user_message = "Quiero investigar las mejores cafeterías de Madrid."
    print("¿Sobre qué quieres investigar?")
    print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n", end="")  # Print line breaks for video recording
    print("\033[16A", end="")  # Move cursor up 16 lines using ANSI escape code
    user_message = input()
    result = await deep_researcher_agent.ainvoke({"messages": [HumanMessage(content=f"{user_message}.")]}, config=thread)

    # If clarification was needed, provide additional context and continue
    if result.get("research_brief", None) is None:
        # user_message = "Examina la calidad del café para evaluar las mejores cafeterías de Madrid."
        print("Introduce tu aclaración")
        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n", end="")  # Print line breaks for video recording
        print("\033[16A", end="")  # Move cursor up 16 lines using ANSI escape code
        user_message = input()
        result = await deep_researcher_agent.ainvoke({"messages": [HumanMessage(content=user_message)]}, config=thread)
    
    # Print the final report
    console = Console()
    console.print("\n\n\n\n\n")
    console.print(Markdown(result["final_report"]))


if __name__ == "__main__":
    asyncio.run(main())