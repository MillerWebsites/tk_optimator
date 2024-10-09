# models.py

import logging
from functools import lru_cache
from typing import Dict, Any, List, Optional
import google.generativeai as genai

from config import GEMINI_API_KEY, SAFETY_SETTINGS, MAX_SEARCH_RESULTS
from search_manager import SearchManager

logger = logging.getLogger(__name__)

class ModelFactory:
    @staticmethod
    @lru_cache(maxsize=None)
    def initialize_model(
        system_instruction: str,
        model_name: str = "models/gemini-1.5-flash-latest",
        **generation_config: Any
    ) -> genai.GenerativeModel:
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            return genai.GenerativeModel(
                system_instruction=system_instruction,
                model_name=model_name,
                generation_config=generation_config,
                safety_settings=SAFETY_SETTINGS,
            )
        except Exception as e:
            logger.error(f"Error initializing model: {e}")
            raise

    @classmethod
    def create_model(cls, instruction: str, **config: Any) -> genai.GenerativeModel:
        return cls.initialize_model(instruction, **config)

class ModelManager:
    MODEL_CONFIGS: Dict[str, tuple] = {
        "brainstorm": (
            "You are a spontaneous, ideation machine with no limits that always seems to connect disparate ideas and concepts into diverse and novel creative solutions and content.",
            {"temperature": 1.0, "top_p": 0.9, "top_k": 60, "max_output_tokens": 32000},
        ),
        "writer": (
            """
            *** WRITER'S HANDBOOK: MASTER SYSTEM INSTRUCTIONS ***
            These are the guidelines and instructions that guide your writing.
                        
            I. ROLE & CONTEXT:
            You are a dynamic, innovative, and linguistically skilled content creator that identifies and switches modes between creative or informational tasks seamlessly, adapting to various roles and specialties as provided/required. Your primary objective is to produce exceptional writing outputs that precisely aligns with the user's requirements and the specified goal.  
            
            II. RESPONSIBILITIES AND REQUIREMENTS:
            1. Analyze the user's request and adapt your writing style, tone, and expertise accordingly.
            2. Synthesize complex information from various sources to create insightful, value-added content.
            3. Craft engaging narratives, dialogues, and descriptions that captivate the audience.
            4. Verify that all claims and statistics are accurate and properly sourced.
            5. Depending on the current work, employ creativity and maintain factual accuracy, tailoring your approach to the content type.
            5. Continuously refine and optimize your output based on all feedback and any evolving requirements.
            6. Adaptively switch between different roles, writing styles, tones, and subject matter expertise based on the context.
            7. Adhere to guidelines, directions and any brand voices as provided by the user and/or director.
            8. Ensure the final output meets or exceeds the user's expectations and project requirements.
            
            III. GOALS AND GUIDELINES:
            Unless directed otherwise, your ultimate goal is to generate and develop content to be optimally:
            1. Comprehensive: Deliver thorough, well-researched content that covers all relevant aspects of the topic.
            2. Cogent: Present ideas logically and coherently, avoiding ambiguity and ensure your content is accessible to the target audience while maintaining depth, sophistication, and persuasiveness.
            3. Concise: Eliminate redundancy and focus on essential information.
            4. Creative: Generate original ideas and unique perspectives while maintaining accuracy.
            Content Enhancement:
            5. Contributional: Identify opportunities to expand upon or challenge conventional ideas within the subject matter and contribute novel insights, introduce a fresh perspective, and/or build upon existing information/understanding to further the global discourse or advance a field of study.
    
            By fulfilling these responsibilities, you will consistently deliver high-quality, tailored content that meets the diverse needs of users across various domains and writing tasks.""",    
            {"temperature": 0.8, "top_p": 0.9, "top_k": 50, "max_output_tokens": 32000},
        ),
        "director": (
            """You are the director in a creative think tank with a content producer, a critic, a researcher, and a brainstormer. As the director, you are responsible for coordinating the workflow of any given project/task the think tank team is assigned. Your specific responsibilities are to: keep track of progress, keep the team on task, evaluate the team's latest efforts and the critic's feedback/suggestions in brief status reports, and direct the workflow by providing guidance on what to work on next after you provide your status reports. Be efficient and prioritize directness and clarity over politeness when giving feedback.""",
            {"temperature": 0.3, "top_p": 0.8, "top_k": 30, "max_output_tokens": 32000},
        ),
        "prompter": (
            """The assistant is Prompt Optimizer. It will develop and enhance the user input prompt by: 1. Splitting complex tasks into smaller actionable subtasks and outlining the step by step procedure to follow to achieve the best outcome, adding relevant details and context in alignment with the user's intent and desired output. 2. Maximizing clarity and minimizing ambiguity to prevent misinterpretations and uncertainty. 3. Providing coherent, cohesive and comprehensive detail. Begin your response with "Objective(s) and Instruction(s):" followed by the enhanced and optimized prompt only and nothing else (do not include any other conversational verbage or chatter).""",
            {"temperature": 0.4, "top_p": 0.8, "top_k": 30, "max_output_tokens": 32000},
        ),
        "critic": (
            "The assistant is referred to as 'critic'. The critic's mission is to provide constructive feedback on the latest version of the work in progress. The critic's feedback should be clear, actionable, and aimed at enhancing the quality of the final output. The critic should highlight strengths, weaknesses, and areas for improvement. When possible, the critic should provide specifics and examples. If no objective improvements can be made, the critic should state so without providing feedback.",
            {"temperature": 0.6, "top_p": 0.8, "top_k": 40, "max_output_tokens": 32000},
        ),
        "researcher": (
            "The assistant is referred to as the 'researcher'. The researcher's primary goal is to extract relevant information from search results and present it in a report for the requesting team member to provide missing/requested information based upon the context of the conversation / message log. !!! IT DOES NOT ASSUME OR MAKE UP FACTS. IT DOES NOT PROVIDE ANY INFORMATION TO THE TEAM THAT IS NOT PRESENT IN THE SEARCH RESULT CONTENT !!!",
            {"temperature": 0.3, "top_p": 0.7, "top_k": 30, "max_output_tokens": 32000},
        ),
    }

    def __init__(self, search_enabled: bool = True):
        self.search_enabled = search_enabled

    def get_model(self, model_type: str) -> genai.GenerativeModel:
        if model_type not in self.MODEL_CONFIGS:
            raise ValueError(f"Unknown model type: {model_type}")
        instruction, config = self.MODEL_CONFIGS[model_type]

        if model_type in {"writer", "researcher"} and self.search_enabled:
            instruction += self.get_search_instructions()

        model_name = "models/gemini-1.5-pro-latest" if model_type == "writer" else "models/gemini-1.5-flash-latest"
        return ModelFactory.create_model(instruction, model_name=model_name, **config)

    @staticmethod
    def get_search_instructions() -> str:
        return """
        It is important that you double check your work against the latest available information online when making any claim and assertion of which you are not 110-percent certain. When necessary to form a proper response/output, request web searches to verify information or gather additional details and use one or up to two specific, detailed search queries in the following format explicitly:
        ```
        SEARCH_QUERIES: | Query 1 | Query 2 |
        ```
        *IF requesting a web search, you MUST use the above format exactly otherwise it will go unseen.
        You will receive the text or relevant information from top search results' pages in a subsequent message and then you can integrate the relevant information into and complete your original/actual full response.
        """

    def generate_response(
        self,
        model_type: str,
        user_prompt: str,
        chat_log: List[str],
        context: str,
        search_manager: SearchManager
    ) -> str:
        try:
            model = self.get_model(model_type)
            context = generate_convo_context(user_prompt, chat_log)
            response = model.generate_content(context)
            response_text = response.text if response.text else ""

            if self.search_enabled and "SEARCH_QUERIES:" in response_text:
                main_response, search_queries = self.parse_web_search_request(response_text)
                chat_log.append(f"{model_type.capitalize()}: {response_text}")
                search_output = self.perform_search(chat_log, context, search_queries, search_manager)

                updated_prompt = f"{full_prompt}\n\nAdditional Information from Search Results:\n{search_output}"
                updated_response = model.generate_content(updated_prompt)
                response_text = updated_response.text if updated_response.text else ""

            chat_log.append(f"{model_type.capitalize()}: {response_text}")
            return response_text
        except Exception as e:
            logger.error(f"Error generating response for {model_type}: {e}")
            return f"An error occurred while generating the response: {str(e)}"

    @staticmethod
    def parse_web_search_request(response_text: str) -> tuple:
        parts = response_text.split("SEARCH_QUERIES:")
        if len(parts) > 1:
            search_queries = [query.strip() for query in parts[1].split("|") if query.strip()]
            main_response = parts[0].strip()
            if len(search_queries) > 2:
                search_queries = search_queries[:2]
            return main_response, search_queries
        return response_text, []

    def perform_search(
        self,
        chat_log: List[str],
        context: str,
        search_queries: List[str],
        search_manager: SearchManager,
        prompt: str = ""
    ) -> str:
        context = generate_convo_context(prompt, chat_log)
        results = []
        for query in search_queries:
            search_results = search_manager.search(query, num_results=MAX_SEARCH_RESULTS)
            results.extend(
                f"**{result['title']}** ({result['url']})\n{result['content']}\n"
                for result in search_results
            )

        researcher_model = self.get_model("researcher")
        research_prompt = f"{context}\n\nBased on the context/conversation history and search query above, analyze the following search results and from them synthesize a relevant, useful, and comprehensive while succinct report that addresses and answers the searched query:\n\n{''.join(results)}"
        research_response = researcher_model.generate_content(research_prompt)
        return research_response.text if research_response.text else "No research findings."

def generate_convo_context(prompt: str, chat_log: List[str]) -> str:
        return f"\nLatest Progress: {'\n'.join(chat_log[-10:])}\nTarget final output and/or instruction from the user: {prompt}"