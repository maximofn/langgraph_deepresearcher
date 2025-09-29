"""
Test the research agent scope
"""

import os
from langsmith import Client
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage

from test_prompts.prompts import BRIEF_CRITERIA_PROMPT, BRIEF_HALLUCINATION_PROMPT

from pydantic import BaseModel, Field
from langchain.chat_models import init_chat_model

# Add ../src to the path
import sys
sys.path.append("../src")

from LLM_models.LLM_models import TEST_SCOPE_MODEL_NAME, TEST_SCOPE_MODEL_PROVIDER, TEST_SCOPE_MODEL_TEMPERATURE, TEST_SCOPE_MODEL_BASE_URL, TEST_SCOPE_MODEL_PROVIDER_API_KEY
from dataset.dataset import conversation_1, conversation_2, criteria_1, criteria_2
from langgraph_deepresearch import scope_graph

import uuid

# ===== CONFIGURATION =====
# Initialize the LangSmith client
load_dotenv()
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT")

os.environ["LANGSMITH_TRACING_V2"] = "true"
os.environ["LANGSMITH_API_KEY"] = LANGSMITH_API_KEY
os.environ["LANGSMITH_ENDPOINT"] = LANGSMITH_ENDPOINT
os.environ["LANGSMITH_PROJECT"] = LANGSMITH_PROJECT

print("Creating LangSmith client...")
langsmith_client = Client()

# Create the dataset
dataset_name = "deep_research_scoping"
if not langsmith_client.has_dataset(dataset_name=dataset_name):
    
    # Create the dataset
    print("Creating dataset...")
    dataset = langsmith_client.create_dataset(
        dataset_name=dataset_name,
        description="A dataset that measures the quality of research briefs generated from an input conversation",
    )

    # Add the examples to the dataset
    print("Adding examples to the dataset...")
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
    is_criterion_captured: bool = Field(
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
    print("\n"+"*"*100)
    print(f"Evaluating success criteria...")

    research_brief = outputs["research_brief"]
    success_criteria = reference_outputs["criteria"]

    print(f"\tResearch Brief: {research_brief}")

    model = init_chat_model(
        model=TEST_SCOPE_MODEL_NAME, 
        model_provider=TEST_SCOPE_MODEL_PROVIDER, 
        api_key=TEST_SCOPE_MODEL_PROVIDER_API_KEY,
        base_url=TEST_SCOPE_MODEL_BASE_URL, 
        temperature=TEST_SCOPE_MODEL_TEMPERATURE
    )
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

    for criterion, response in zip(success_criteria, responses):
        print(f"\tCriterion: {criterion}, reasoning: {response.reasoning}, is criterion captured: {response.is_criterion_captured}")
        print(f"\t\treasoning: {response.reasoning}")
        print(f"\t\tis criterion captured: {response.is_criterion_captured}")
    
    # Ensure the criteria_text field is populated correctly
    individual_evaluations = [
        Criteria(
            reasoning=response.reasoning,
            criteria_text=criterion,
            is_criterion_captured=response.is_criterion_captured
        )
        for criterion, response in zip(success_criteria, responses)
    ]
    
    # Calculate overall score as percentage of captured criteria
    captured_count = sum(1 for eval_result in individual_evaluations if eval_result.is_criterion_captured)
    total_count = len(individual_evaluations)
    score = captured_count / total_count if total_count > 0 else 0.0
    print(f"\tSuccess Criteria score: {score} (captured {captured_count} out of {total_count} criteria)")
    
    return {
        "key": "success_criteria_score", 
        "score": score,
        "individual_evaluations": [
            {
                "criteria": eval_result.criteria_text,
                "captured": eval_result.is_criterion_captured,
                "reasoning": eval_result.reasoning
            }
            for eval_result in individual_evaluations
        ]
    }

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
    print("\n"+"*"*100)
    print(f"Evaluating no assumptions...")

    research_brief = outputs["research_brief"]
    success_criteria = reference_outputs["criteria"]

    print(f"\tResearch Brief: {research_brief}")

    model = init_chat_model(
        model=TEST_SCOPE_MODEL_NAME, 
        model_provider=TEST_SCOPE_MODEL_PROVIDER, 
        api_key=TEST_SCOPE_MODEL_PROVIDER_API_KEY,
        base_url=TEST_SCOPE_MODEL_BASE_URL, 
        temperature=TEST_SCOPE_MODEL_TEMPERATURE
    )
    structured_output_model = model.with_structured_output(NoAssumptions)
    
    response = structured_output_model.invoke([
        HumanMessage(content=BRIEF_HALLUCINATION_PROMPT.format(
            research_brief=research_brief, 
            success_criteria=str(success_criteria)
        ))
    ])

    print(f"\tNo Assumptions reasoning: {response.reasoning}")
    print(f"\tNo Assumptions score: {response.no_assumptions}")
    
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