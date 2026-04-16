"""
Full Multi-Agent Research System

This module integrates all components of the research system:
- User clarification and scoping
- Research brief generation
- Multi-agent research coordination
- Final report generation

The system orchestrates the complete research workflow from initial user
input through final report delivery.
"""

from typing_extensions import Literal

from langchain_core.messages import HumanMessage, get_buffer_string
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command

from utils.today import get_today_str
from write.write_prompts import final_report_generation_prompt, chat_with_writer_prompt
from scope.scope_state import AgentState, AgentInputState, ClarifyWithUser, ResearchQuestion
from scope.scope_agent import clarify_with_user, write_research_brief
from supervisor.supervisor_agent import supervisor_agent
from utils.progress_bar import safe_progress_bar

from LLM_models.model_catalog import get_role_model
from langchain_core.runnables import RunnableConfig

from utils.message_utils import format_messages

# ===== REQUEST ROUTER =====

def route_request(state: AgentState) -> Command[Literal["clarify_with_user", "chat_with_writer"]]:
    """
    Entry point router. Decides whether this is a new research request or a
    follow-up chat after research has already been completed.
    """
    if state.get("final_report"):
        return Command(goto="chat_with_writer")
    return Command(goto="clarify_with_user")

# ===== FINAL REPORT GENERATION =====

async def final_report_generation(state: AgentState, config: RunnableConfig):
    """
    Final report generation node.

    Synthesizes all research findings into a comprehensive final report
    """

    notes = state.get("notes", [])

    # Build the per-session writer model from RunnableConfig
    writer_model = get_role_model("writer", config)

    findings = "\n".join(notes)

    final_report_prompt = final_report_generation_prompt.format(
        research_brief=state.get("research_brief", ""),
        findings=findings,
        date=get_today_str()
    )

    print("⏳ Writer agent - Final report generation:")
    with safe_progress_bar(monitor=False, stats=False, title="", spinner='dots_waves', bar='blocks') as bar:
        final_report = await writer_model.ainvoke([HumanMessage(content=final_report_prompt)])
        bar()

    format_messages([final_report], title="Writer Agent - Final Report")

    return {
        "final_report": final_report.content,
        "messages": ["Here is the final report: " + final_report.content],
    }

# ===== POST-RESEARCH CHAT =====

async def chat_with_writer(state: AgentState, config: RunnableConfig):
    """
    Post-research chat node.

    Answers follow-up questions from the user using the completed research state
    (notes, research_brief, final_report). Supports multi-turn conversation.
    """
    writer_model = get_role_model("writer", config)

    findings = "\n".join(state.get("notes", []))

    prompt = chat_with_writer_prompt.format(
        research_brief=state.get("research_brief", ""),
        findings=findings,
        final_report=state.get("final_report", ""),
        date=get_today_str(),
    )

    print("⏳ Writer agent - Chat mode:")
    with safe_progress_bar(monitor=False, stats=False, title="", spinner='dots_waves', bar='blocks') as bar:
        response = await writer_model.ainvoke([
            HumanMessage(content=prompt),
            *list(state.get("messages", [])),
        ])
        bar()

    format_messages([response], title="Writer Agent - Chat Response")
    return {"messages": [response]}

# ===== GRAPH CONSTRUCTION =====
# Build the overall workflow
writer_builder = StateGraph(AgentState, input_schema=AgentInputState)

# Add workflow nodes
writer_builder.add_node("route_request", route_request)
writer_builder.add_node("clarify_with_user", clarify_with_user)
writer_builder.add_node("write_research_brief", write_research_brief)
writer_builder.add_node("supervisor_subgraph", supervisor_agent)
writer_builder.add_node("final_report_generation", final_report_generation)
writer_builder.add_node("chat_with_writer", chat_with_writer)

# Add workflow edges
writer_builder.add_edge(START, "route_request")
writer_builder.add_edge("write_research_brief", "supervisor_subgraph")
writer_builder.add_edge("supervisor_subgraph", "final_report_generation")
writer_builder.add_edge("final_report_generation", END)
writer_builder.add_edge("chat_with_writer", END)

# Compile the full workflow
agent = writer_builder.compile()
