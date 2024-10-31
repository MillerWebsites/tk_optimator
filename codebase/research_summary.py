from torch import ge
from search_manager import SearchManager, initialize_search_manager
from agents import AgentManager, Agent
from config import GEMINI_API_KEY
from llm_providers import GeminiProvider
from models import ModelManager, ModelFactory
import json
from agents import Agent, ToolManager
from models import ModelManager
from functools import partial
import tools

tool_manager = ToolManager()
# Create an instance of the AgentManager class
agent_manager = AgentManager(tool_manager=ToolManager())

# Load the researcher agent's configuration from the agents.json file
with open('agents.json', encoding='utf-8', errors='ignore') as f:
    agents_config = json.load(f)
    print(agents_config)
researcher_config = agents_config.researcher

# Create an instance of the ModelManager class
model_manager = ModelManager()

# Create an instance of the ToolManager class
gemini_provider = GeminiProvider(api_key=GEMINI_API_KEY)
search_manager = initialize_search_manager()

# Register the web_search tool with the ToolManager
tool_manager.register_tool("web_search", partial(tools.web_search, search_manager))

# Initialize the researcher agent and tool manager
agent_manager = AgentManager(tool_manager=ToolManager())

# Load the researcher agent's configuration from the agents.json file
with open('agents.json', encoding='utf-8', errors='ignore') as f:
    agents_config = json.load(f)
researcher_config = agents_config['researcher']

# Create an instance of the ModelManager class
model_manager = ModelManager()

# Create an instance of the ToolManager class
gemini_provider = GeminiProvider(api_key=GEMINI_API_KEY)
search_manager = initialize_search_manager()

# Register the web_search tool with the ToolManager
tool_manager.register_tool("web_search", partial(tools.web_search, search_manager))

# Create an instance of the Agent class
researcher = Agent(
    model_manager=model_manager,
    tool_manager=tool_manager,
    agent_type="producer",
    instruction=researcher_config['system_prompt'],
    tools=agents_config['researcher']['tools'],
    model_config=researcher_config['generation_config']
)

# Define a function to extract search queries from the researcher's output
def extract_search_queries(text):
    # Implement a simple regular expression to extract phrases that start with "search for" or "explore"
    import re
    queries = re.findall(r"(search for|explore) (.+?)(\.|$)", text, re.IGNORECASE)
    return [query[1] for query in queries]

# Define a function to perform iterative web search and knowledge aggregation
def iterative_web_search(topic, max_iterations, num_results):
    knowledge_graph = ""
    search_queries = [topic]
    for i in range(max_iterations):
        # Perform web search on the current topic
        results = tools.web_search(search_queries[-1], num_results)
        # Update the knowledge graph with the new results
        knowledge_graph += results
        # Ask the researcher agent to summarize the current knowledge graph
        prompt = "Summarize the knowledge graph: "
        summary = researcher.generate_response(prompt, knowledge_graph)
        # Ask the researcher agent to generate additional search queries
        prompt = "What are some related search queries to explore further? "
        additional_queries = researcher.generate_response(prompt, summary)
        # Extract the additional search queries from the researcher's output
        additional_queries = extract_search_queries(additional_queries)
        # Add the additional search queries to the list of search queries
        search_queries.extend(additional_queries)
        # Check if the researcher has determined that it has summarized enough information
        prompt = "Have you summarized enough information to provide a comprehensive report? "
        response = researcher.generate_response(prompt, summary)
        if response.lower() == "yes":
            break
    return knowledge_graph

# Get user input for the topic and number of iterations
topic = input("Enter the topic: ")
max_iterations = int(input("Enter the maximum number of iterations: "))
num_results = int(input("Enter the number of results per iteration: "))

# Perform the iterative web search and knowledge aggregation
knowledge_graph = iterative_web_search(topic, max_iterations, num_results)

# Print the final knowledge graph
print(knowledge_graph)

# Ask the researcher agent to generate a comprehensive report
prompt = "Generate a comprehensive report based on the knowledge graph: "
report = researcher.generate_response(prompt, knowledge_graph)

# Print the comprehensive report
print(report)