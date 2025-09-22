"""
Test the research agent scope
"""

import os
from langsmith import Client
from dotenv import load_dotenv

from langchain_core.messages import AIMessage, HumanMessage

from test_prompts.prompts import BRIEF_CRITERIA_PROMPT, BRIEF_HALLUCINATION_PROMPT

from typing_extensions import cast
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.chat_models import init_chat_model

# Add ../src to the path
import sys
sys.path.append("../src")

from LLM_models.LLM_models import TEST_SCOPE_MODEL_NAME, TEST_SCOPE_MODEL_PROVIDER, TEST_SCOPE_MODEL_TEMPERATURE, GITHUB_BASE_URL
from langgraph_deepresearch import scope_graph

import uuid

# ===== CONFIGURATION =====
# Initialize the LangSmith client
load_dotenv()
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT")
GITHUB_API_KEY = os.getenv("GITHUB_API_KEY")
GITHUB_BASE_URL = os.getenv("GITHUB_BASE_URL")

os.environ["LANGSMITH_TRACING_V2"] = "true"
os.environ["LANGSMITH_API_KEY"] = LANGSMITH_API_KEY
os.environ["LANGSMITH_ENDPOINT"] = LANGSMITH_ENDPOINT
os.environ["LANGSMITH_PROJECT"] = LANGSMITH_PROJECT

langsmith_client = Client(api_key=LANGSMITH_API_KEY)

# ===== DATASET =====
# Create the conversation
conversation_1 = [
    HumanMessage(content="¿Cuál es la mejor manera de invertir 50.000 € para la jubilación?"),
    AIMessage(content="Puedes proporcionarme información adicional para adaptar el asesoramiento de inversión a tu objetivo de jubilación de $50.000 €? En concreto:\n * Tu edad actual o la edad a la que deseas jubilarte\n * Tu tolerancia al riesgo (baja, media, alta)\n * Cualquier preferencia en cuanto a tipos de inversión (por ejemplo, acciones, bonos, fondos de inversión, bienes inmuebles)\n * Si inviertes a través de una cuenta con ventajas fiscales (por ejemplo, IRA, 401(k)) o una cuenta de corretaje normal\nEsto me ayudará a ofrecerle sugerencias más personalizadas y relevantes."),
    HumanMessage(content="Tengo 25 años y quiero jubilarme a los 45. Ahora mismo tengo una alta tolerancia al riesgo, pero creo que irá disminuyendo con el tiempo. He oído que las acciones y los ETF son una buena opción, pero estoy abierto a cualquier posibilidad. Ya tengo un plan 401k, pero esto sería solo a través de una cuenta de corretaje normal."),
]

conversation_2 = [
    HumanMessage(content="Estoy buscando un piso en Madrid, ¿me puedes ayudar?"),
    AIMessage(content="¿Podrías especificar tus preferencias en cuanto al piso? Por ejemplo:\n * Barrios o distritos deseados\n * Número de dormitorios/baños\n * Rango de presupuesto (alquiler mensual)\n * Cualquier comodidad o característica imprescindible\n * Fecha de mudanza preferida\nEsta información me ayudará a ofrecerte las opciones de apartamentos más relevantes en Madrid."),
    HumanMessage(content="Prefiero vivir en Lavapies, Chueca o Salamanca. Busco un piso de dos dormitorios y dos baños, con un alquiler mensual inferior a 1000 €. Me gustaría que fuera un edificio con portero, pero no pasa nada si no lo tiene. Sería un plus que cerca hubiera un gimnasio. Y me gustaría mudarme en diciembre de 2025."),
]

criteria_1 = [
    "Current age is 25 años",
    "Desired retirement age is 45",
    "Current risk tolerance is high",
    "Interested in investing in stocks and ETFs",
    "Open to forms of investment beyond stocks and ETFs"
    "Investment account is a regular brokerage account",
]

criteria_2 = [
    "Looking for a 2 bed 2 bath apartment in Lavapies, Chueca, or Salamanca",
    "Monthly rent below 1000 €",
    "Should be in a doorman building, but not strict",
    "Ideally have a near by gym but not strict",
    "Move in date is December 2025"
]

# Create the dataset
dataset_name = "deep_research_scoping"
if not langsmith_client.has_dataset(dataset_name=dataset_name):
    
    # Create the dataset
    dataset = langsmith_client.create_dataset(
        dataset_name=dataset_name,
        description="A dataset that measures the quality of research briefs generated from an input conversation",
    )

    # Add the examples to the dataset
    langsmith_client.create_examples(
        dataset_id=dataset.id,
        examples=[
            {
                "inputs": {"messages": conversation_1},
                "outputs": {"criteria": criteria_1},
            },
            {
                "inputs": {"messages": conversation_2},
                "outputs": {"criteria": criteria_2},
            },
        ],
    )

# ===== EVALUATION FUNCTIONS =====
# Improved Criteria class with reasoning field and enhanced descriptions
class Criteria(BaseModel):
    """
    Individual success criteria evaluation result.
    
    This model represents a single evaluation criteria that should be present
    in the research brief, along with a detailed assessment of whether it was
    successfully captured and the reasoning behind that assessment.
    """
    criteria_text: str = Field(
        description="The specific success criteria being evaluated (e.g., 'Current age is 25', 'Monthly rent below 7k')"
    )
    reasoning: str = Field(
        description="Detailed explanation of why this criteria is or isn't captured in the research brief, including specific evidence from the brief"
    )
    is_captured: bool = Field(
        description="Whether this specific criteria is adequately captured in the research brief (True) or missing/inadequately addressed (False)"
    )

def evaluate_success_criteria(outputs: dict, reference_outputs: dict):
    """
    Evaluate whether the research brief captures all required success criteria.
    
    This function evaluates each criterion individually to provide focused assessment
    and detailed reasoning for each evaluation decision.
    
    Args:
        outputs: Dictionary containing the research brief to evaluate
        reference_outputs: Dictionary containing the list of success criteria
        
    Returns:
        Dict with evaluation results including score (0.0 to 1.0)
    """
    research_brief = outputs["research_brief"]
    success_criteria = reference_outputs["criteria"]

    model = ChatOpenAI(
        model=TEST_SCOPE_MODEL_NAME,
        temperature=TEST_SCOPE_MODEL_TEMPERATURE
    )
    # model = init_chat_model(
    #     model=TEST_SCOPE_MODEL_NAME, 
    #     model_provider=TEST_SCOPE_MODEL_PROVIDER, 
    #     api_key=GITHUB_API_KEY,
    #     base_url=GITHUB_BASE_URL, 
    #     temperature=TEST_SCOPE_MODEL_TEMPERATURE
    # )
    structured_output_model = model.with_structured_output(Criteria)
    
    # Run evals
    responses = structured_output_model.batch([
    [
        HumanMessage(
            content=BRIEF_CRITERIA_PROMPT.format(
                research_brief=research_brief,
                criterion=criterion
            )
        )
    ] 
    for criterion in success_criteria])
    
    # Ensure the criteria_text field is populated correctly
    individual_evaluations = [
        Criteria(
            reasoning=response.reasoning,
            criteria_text=criterion,
            is_captured=response.is_captured
        )
        for criterion, response in zip(success_criteria, responses)
    ]
    
    # Calculate overall score as percentage of captured criteria
    captured_count = sum(1 for eval_result in individual_evaluations if eval_result.is_captured)
    total_count = len(individual_evaluations)
    
    return {
        "key": "success_criteria_score", 
        "score": captured_count / total_count if total_count > 0 else 0.0,
        "individual_evaluations": [
            {
                "criteria": eval_result.criteria_text,
                "captured": eval_result.is_captured,
                "reasoning": eval_result.reasoning
            }
            for eval_result in individual_evaluations
        ]
    }

# ===== EVALUATION FUNCTIONS =====
# Improved NoAssumptions class with reasoning field and enhanced descriptions
class NoAssumptions(BaseModel):
    """
    Evaluation model for checking if research brief makes unwarranted assumptions.
    
    This model evaluates whether the research brief contains any assumptions,
    inferences, or additions that were not explicitly stated by the user in their
    original conversation. It provides detailed reasoning for the evaluation decision.
    """
    no_assumptions: bool = Field(
        description="Whether the research brief avoids making unwarranted assumptions. True if the brief only includes information explicitly provided by the user, False if it makes assumptions beyond what was stated."
    )
    reasoning: str = Field(
        description="Detailed explanation of the evaluation decision, including specific examples of any assumptions found or confirmation that no assumptions were made beyond the user's explicit statements."
    )

def evaluate_no_assumptions(outputs: dict, reference_outputs: dict):
    """
    Evaluate whether the research brief avoids making unwarranted assumptions.
    
    This evaluator checks that the research brief only includes information
    and requirements that were explicitly provided by the user, without
    making assumptions about unstated preferences or requirements.
    
    Args:
        outputs: Dictionary containing the research brief to evaluate
        reference_outputs: Dictionary containing the success criteria for reference
        
    Returns:
        Dict with evaluation results including boolean score and detailed reasoning
    """
    research_brief = outputs["research_brief"]
    success_criteria = reference_outputs["criteria"]

    model = ChatOpenAI(
        model=TEST_SCOPE_MODEL_NAME,
        temperature=TEST_SCOPE_MODEL_TEMPERATURE
    )
    # model = init_chat_model(
    #     model=TEST_SCOPE_MODEL_NAME, 
    #     model_provider=TEST_SCOPE_MODEL_PROVIDER, 
    #     api_key=GITHUB_API_KEY,
    #     base_url=GITHUB_BASE_URL, 
    #     temperature=TEST_SCOPE_MODEL_TEMPERATURE
    # )
    structured_output_model = model.with_structured_output(NoAssumptions)
    
    response = structured_output_model.invoke([
        HumanMessage(content=BRIEF_HALLUCINATION_PROMPT.format(
            research_brief=research_brief, 
            success_criteria=str(success_criteria)
        ))
    ])
    
    return {
        "key": "no_assumptions_score", 
        "score": response.no_assumptions,
        "reasoning": response.reasoning
    }

# ===== EVALUATION FUNCTIONS =====
def target_func(inputs: dict):
    config = {"configurable": {"thread_id": uuid.uuid4()}}
    return scope_graph.invoke(inputs, config=config)

langsmith_client.evaluate(
    target_func,
    data=dataset_name,
    evaluators=[evaluate_success_criteria, evaluate_no_assumptions],
    experiment_prefix="Deep Research Scoping",
)