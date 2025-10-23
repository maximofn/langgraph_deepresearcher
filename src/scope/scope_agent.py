"""
User Clarification and Research Brief Generation.

This module implements the scoping phase of the research workflow, where we:
 1. Assess if the user's request needs clarification
 2. Generate a detailed research brief from the conversation to starts the investigation

The workflow uses structured output to make deterministic decisions about
whether sufficient context exists to proceed with research.

The hole deep researcher workflow is composed by the following steps:

 User prompt -> Scope -> Research -> Write Report
"""

from datetime import datetime
from typing_extensions import Literal
from alive_progress import alive_bar
import traceback
import sys

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, get_buffer_string
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command

from scope.scope_prompts import clarify_with_user_instructions, transform_messages_into_research_topic_prompt
from scope.scope_state import AgentState, AgentInputState, ClarifyWithUser, ResearchQuestion

from utils.today import get_today_str
from LLM_models.LLM_models import SCOPE_MODEL_NAME, SCOPE_MODEL_PROVIDER, SCOPE_MODEL_TEMPERATURE, SCOPE_MODEL_BASE_URL, SCOPE_MODEL_PROVIDER_API_KEY

from utils.message_utils import format_messages

# ===== CONFIGURATION =====

# Initialize model
model = init_chat_model(
    model=SCOPE_MODEL_NAME, 
    model_provider=SCOPE_MODEL_PROVIDER, 
    api_key=SCOPE_MODEL_PROVIDER_API_KEY,
    base_url=SCOPE_MODEL_BASE_URL, 
    temperature=SCOPE_MODEL_TEMPERATURE
)

# ===== WORKFLOW NODES =====

def clarify_with_user(state: AgentState) -> Command[Literal["write_research_brief", "__end__"]]:
    """
    Determine if the user's request contains sufficient information to proceed with research.
    
    Uses structured output to make deterministic decisions and avoid hallucination.
    Routes to either research brief generation or ends with a clarification question.
    """

    try:
        print("⏳ Scope agent:")
        format_messages([state.get("messages", [])[-1]], title="Real Human Message", msg_subtype='RealHumanMessage')

        # Set up structured output model
        structured_output_model = model.with_structured_output(ClarifyWithUser)

        # Invoke the model with clarification instructions
        with alive_bar(monitor=False, stats=False, title="", spinner='dots_waves', bar='blocks') as bar:
            response = structured_output_model.invoke([
                HumanMessage(content=clarify_with_user_instructions.format(
                    messages=get_buffer_string(messages=state["messages"]), 
                    date=get_today_str()
                ))
            ])
            bar()
        
        # Format and display the research messages
        format_messages([response], title="Scope Assistant - need clarification?")
        
        # Route based on clarification need
        if response.need_clarification:
            # Create a System message to show the decision
            routing_message = SystemMessage(
                content="Necesita aclaración por parte del usuario. Enviando pregunta aclaratoria..."
            )
            format_messages([routing_message], title="Scope System Message")
            return Command(
                goto=END, 
                update={"messages": [AIMessage(content=response.question)]}
            )
        else:
            # Create a System message to show the decision
            routing_message = SystemMessage(
                content="No necesita aclaración por parte del usuario. Enviando mensaje de verificación..."
            )
            format_messages([routing_message], title="Scope System Message")
            return Command(
                goto="write_research_brief", 
                update={"messages": [AIMessage(content=response.verification)]}
            )
    
    except Exception as e:
        # Get the traceback information
        exc_type, exc_obj, exc_tb = sys.exc_info()
        line_number = exc_tb.tb_lineno
        
        # Print detailed error information
        print(f"\n❌ Error in clarify_with_user function:")
        print(f"   Line number: {line_number}")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        print(f"\n   Full traceback:")
        traceback.print_exc()
        
        # Re-raise the exception to let the caller handle it
        raise

def write_research_brief(state: AgentState):
    """
    Transform the conversation history into a comprehensive research brief.
    
    Uses structured output to ensure the brief follows the required format
    and contains all necessary details for effective research.
    """
    
    try:
        # Set up structured output model
        structured_output_model = model.with_structured_output(ResearchQuestion)

        print("⏳ Scope agent - Write research brief:")
        format_messages([state.get("messages", [])[-1]], title="Scope Assistant - Write research brief")
        
        # Generate research brief from conversation history
        with alive_bar(monitor=False, stats=False, title="", spinner='dots_waves', bar='blocks') as bar:
            response = structured_output_model.invoke([
                HumanMessage(content=transform_messages_into_research_topic_prompt.format(
                    messages=get_buffer_string(state.get("messages", [])),
                    date=get_today_str()
                ))
            ])
            bar()
        
        # Format and display the research brief
        format_messages([response], title="Scope Assistant - Research brief generated")
        
        # Update state with generated research brief and pass it to the supervisor
        return {
            "research_brief": response.research_brief,
            "supervisor_messages": [HumanMessage(content=f"{response.research_brief}.")]
        }
    
    except Exception as e:
        # Get the traceback information
        exc_type, exc_obj, exc_tb = sys.exc_info()
        line_number = exc_tb.tb_lineno
        
        # Print detailed error information
        print(f"\n❌ Error in write_research_brief function:")
        print(f"   Line number: {line_number}")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        print(f"\n   Full traceback:")
        traceback.print_exc()
        
        # Re-raise the exception to let the caller handle it
        raise

# ===== GRAPH CONSTRUCTION =====

# Build the scoping workflow
deep_researcher_graph_builder = StateGraph(AgentState, input_schema=AgentInputState)

# Add workflow nodes
deep_researcher_graph_builder.add_node("clarify_with_user", clarify_with_user)
deep_researcher_graph_builder.add_node("write_research_brief", write_research_brief)

# Add workflow edges
deep_researcher_graph_builder.add_edge(START, "clarify_with_user")
deep_researcher_graph_builder.add_edge("write_research_brief", END)

# Compile the workflow
scope_research = deep_researcher_graph_builder.compile()