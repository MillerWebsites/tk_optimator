import json
import os
import time
from click import prompt
import google.generativeai as genai
import re
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def upload_to_gemini(path, mime_type=None):
  """Uploads the given file to Gemini.

  See https://ai.google.dev/gemini-api/docs/prompting_with_media
  """
  file = genai.upload_file(path, mime_type=mime_type)
  print(f"Uploaded file '{file.display_name}' as: {file.uri}")
  return file

def wait_for_files_active(files):
  """Waits for the given files to be active.

  Some files uploaded to the Gemini API need to be processed before they can be
  used as prompt inputs. The status can be seen by querying the file's "state"
  field.

  This implementation uses a simple blocking polling loop. Production code
  should probably employ a more sophisticated approach.
  """
  print("Waiting for file processing...")
  for name in (file.name for file in files):
    file = genai.get_file(name)
    while file.state.name == "PROCESSING":
      print(".", end="", flush=True)
      time.sleep(10)
      file = genai.get_file(name)
    if file.state.name != "ACTIVE":
      raise Exception(f"File {file.name} failed to process")
  print("...all files ready")
  print()

# Create the model
generation_config = {
  "temperature": 0.3,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

with open("agents.json", "r", encoding="utf-8", errors="ignore") as f:
  agents = json.load(f)
  print(agents["researcher"])
  researcher_config = agents["researcher"]

coder_model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
  system_instruction="""Conduct a thorough analysis to identify vulnerabilities, glitches, and performance issues, focusing on memory management, resource allocation, and concurrency to ensure robustness and efficiency.

Diagnostic Reports:

Provide detailed reports for each issue, describing the problem, its impact, and the relevant code snippets.
Highlight patterns or recurring issues indicating broader systemic problems.
Actionable Recommendations:

Offer actionable solutions with best practices to prevent similar future issues.
Steps:

Comprehensive Code Review:

Analyze the entire codebase to detect errors, inefficiencies, and logical inconsistencies.
Scrutinize algorithms, data structures, and control flow using advanced techniques to uncover vulnerabilities and performance bottlenecks.
Diagnostic Reports:

Identify and explain logical errors, structural weaknesses, inefficiencies, security vulnerabilities, and performance bottlenecks.
Include code snippets showing the source of each issue.
Actionable Recommendations:

Provide specific, actionable solutions aligned with best practices and ensure feasibility within the current codebase.
Revised Source Code Snippets:

Offer optimized, functional code revisions with comments for clarity.
Clearly mark what to remove, replace, or retain, avoiding vague comments like “previous code unchanged.”
Recap the changes and their impact, noting any unintended side effects for further revision.
Deliverables:

A report detailing findings.
Actionable recommendations.
Revised code snippets with annotations.
A summary of changes and their impact.""")


researcher_model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
  system_instruction="agents.researcher"
)
print(researcher_model._system_instruction)
model = ModelFactory.create_model(researcher_config["instruction"], **researcher_config)

# TODO Make these files available on the local file system
# You may need to update the file paths
files = [
  upload_to_gemini("gui.py", mime_type="text/x-python"),
  upload_to_gemini("models.py", mime_type="text/x-python"),
  upload_to_gemini("search_manager.py", mime_type="text/x-python"),
  upload_to_gemini("main.py", mime_type="text/x-python"),
  upload_to_gemini("tools.py", mime_type="text/x-python"),
  upload_to_gemini("agents.py", mime_type="text/x-python"),
  upload_to_gemini("llm_providers.py", mime_type="text/x-python"),
  upload_to_gemini("config.py", mime_type="text/x-python"),
]

# Some files have a processing delay. Wait for them to be ready.
wait_for_files_active(files)

chat_session = model.start_chat(
  history=[
    {
      "role": "user",
      "parts": [
        files[0],
        files[1],
        files[2],
        files[3],
        files[4],
        files[5],
        files[6],
        files[7],
        "This code aims to create a creative AI writing assistant that leverages the power of LLMs and a sophisticated agent-based architecture. It distinguishes itself through:\n\n- **Specialized Agents:** You've implemented a `researcher_agent` and a `writer_agent`, each with distinct roles and capabilities. This division of labor allows for more focused and effective task execution.\n- **Contextual Tool Use:** Your agents dynamically determine and utilize the most appropriate tools from the `ToolManager` based on the user's input and the ongoing context. This adaptability is key to a versatile and powerful assistant.\n- **Flexible Model Selection:** The `ModelManager` allows you to easily switch between different LLM providers (OpenAI, Gemini) and models, providing flexibility for experimentation and optimization.\n- **Web Search Integration:** The `SearchManager` enables access to real-world information through web searches, enriching the assistant's knowledge base.\n- **Interactive GUI:** The Tkinter-based GUI offers a user-friendly interface for interacting with the assistant.\n\n**Functionality:**\n\n1. **User Interaction:** Users input prompts or instructions through the GUI.\n2. **Agent Selection:** The application routes the user's request to the most suitable agent (researcher or writer) based on the task at hand.\n3. **Dynamic Tool Invocation:**  Agents analyze the user's input and the current context to determine which tools, if any, are required, and execute them accordingly.\n4. **LLM-Powered Response Generation:** The selected agent interacts with the chosen LLM, incorporating information gathered from tools and previous interactions to generate a comprehensive and contextually relevant response.\n5. **Output Display:** The generated text, along with any relevant findings from tool executions, is presented to the user in the GUI.\n\n**",
      ],
    },
    {
      "role": "model",
      "parts": [
          "I see you have uploaded several python files, what would you like me to do?"
        ],
    },
  ]
)

prompt = "Please thoroughly inspect the code and identify all redundancies, unnecessary abstractions, logical inconsistencies, and other flaws or bugs and list them in a numbered list in the format:   1. detailed description of first problem 2. detailed description of second problem 3. etc... so that your answer can be properly parsed."

#Function to parse the listed problems from the response to the prompt

def parse_listed_problems(response):
  return [
      # Split each line into a problem number and a description, and strip any whitespace
      # from the description.  We use a regular expression to match lines that start
      # with a number followed by a period and a space, which should be the format
      # of the listed problems.
      re.sub(r"^\d+\.\s", "", line).strip()
      for line in response.text.split("\n")
      if re.match(r"^\d+\.\s", line)  # Only match lines that start with a number followed by a period        
  ]

    
#"Please thoroughly inspect the code and determine which method of storing the system_instructions / system prompts for each of the agents.  Should I use json?  Python dictionary?  Which method is the best for being able to create and modify agents on the fly through the GUI when the program is running?"




def code_review_workflow():
  while True:
      response = chat_session.send_message(prompt)
      print(response.text)
      problems = parse_listed_problems(response)

    #Iteratively send each problem to the agent and print the response

      for problem in problems:
        print(f"Problem: {problem}")
        response = chat_session.send_message(problem)
        print(f"Response: {response}")

#Create a simple CLI command menu for running different functions / workflows

while True:
  print("1. Code Review Workflow")
  print("2. Exit")
  choice = input("Enter your choice: ")
  if choice == "1":
    code_review_workflow()
  elif choice == "2":
    break
  else:
    print("Invalid choice. Please try again.")  
