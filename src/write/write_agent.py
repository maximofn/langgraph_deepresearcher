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

from langchain_core.messages import HumanMessage
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END

from utils.today import get_today_str
from utils.initialize_model import initialize_model
from write.write_prompts import final_report_generation_prompt
from scope.scope_state import AgentState, AgentInputState, ClarifyWithUser, ResearchQuestion
from scope.scope_agent import clarify_with_user, write_research_brief
from supervisor.supervisor_agent import supervisor_agent
from utils.progress_bar import safe_progress_bar

from LLM_models.LLM_models import WRITER_MODEL_NAME, WRITER_MODEL_PROVIDER, WRITER_MODEL_TEMPERATURE, WRITER_MODEL_BASE_URL, WRITER_MODEL_PROVIDER_API_KEY, WRITER_MODEL_MAX_TOKENS

from utils.message_utils import format_messages

# ===== Config =====

writer_model = initialize_model(
    model_name=WRITER_MODEL_NAME,
    model_provider=WRITER_MODEL_PROVIDER,
    base_url=WRITER_MODEL_BASE_URL,
    temperature=WRITER_MODEL_TEMPERATURE,
    api_key=WRITER_MODEL_PROVIDER_API_KEY,
    max_tokens=WRITER_MODEL_MAX_TOKENS
)

# ===== FINAL REPORT GENERATION =====

async def final_report_generation(state: AgentState):
    """
    Final report generation node.
    
    Synthesizes all research findings into a comprehensive final report
    """
    
    notes = state.get("notes", [])
    
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

# ===== GRAPH CONSTRUCTION =====
# Build the overall workflow
writer_builder = StateGraph(AgentState, input_schema=AgentInputState)

# Add workflow nodes
writer_builder.add_node("clarify_with_user", clarify_with_user)
writer_builder.add_node("write_research_brief", write_research_brief)
writer_builder.add_node("supervisor_subgraph", supervisor_agent)
writer_builder.add_node("final_report_generation", final_report_generation)

# Add workflow edges
writer_builder.add_edge(START, "clarify_with_user")
writer_builder.add_edge("write_research_brief", "supervisor_subgraph")
writer_builder.add_edge("supervisor_subgraph", "final_report_generation")
writer_builder.add_edge("final_report_generation", END)

# Compile the full workflow
agent = writer_builder.compile()