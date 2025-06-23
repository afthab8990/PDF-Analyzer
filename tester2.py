# Import dependencies
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
from langraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
 
# Load environment variables
load_dotenv()
 
# Initialize Gemini model
model = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",  # or "gemini-1.5-pro" based on your needs
    google_api_key=os.getenv("GOOGLE_API_KEY")
)
 
# Define tool functions
def add(a: float, b: float) -> float:
    return a + b
 
def multiply(a: float, b: float) -> float:
    return a * b
 
def web_search(query: str) -> str:
    """Search the web for information"""
    return (
        "hq of fnn company in 2024: Facebook (Meta), 1000 employees"
    )
 
# Create agents
math_agent = create_react_agent(
    model=model,
    tools=[add, multiply],
    name="maths_expert",
    prompt="You are an excellent AI assistant in mathematics."
)
 
research_agent = create_react_agent(
    model=model,
    tools=[web_search],
    name="research_expert",
    prompt="You are an expert research assistant. Use the web search tool to find current information."
)
 
# Supervisor prompt
supervisor_prompt = (
    "You are a supervisor managing two agents: a research expert and a maths expert.\n"
    "If the query is about mathematics, use the maths expert.\n"
    "If the query is about current events or information lookup, use the research expert."
)
 
# Create the multi-agent workflow
math_search_workflow = create_supervisor(
    agents=[research_agent, math_agent],
    model=model,
    output_mode="last_message",  # can also use "all_messages"
    prompt=supervisor_prompt
)
 
# Example usage
response = math_search_workflow.invoke("What is 17 multiplied by 4?")
print("Response:", response)
 
response2 = math_search_workflow.invoke("Where is the HQ of FNN company in 2024?")
print("Response:", response2)
 