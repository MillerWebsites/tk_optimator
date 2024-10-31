import tkinter as tk
from tkinter import ttk, scrolledtext, Menu, filedialog, simpledialog, messagebox
import logging
from typing import List, Optional, Tuple, Dict
from functools import partial
import re
import tools
from models import ModelManager, ModelFactory, generate_convo_context
from agents import AgentManager, ToolManager
from search_manager import SearchManager, SearchAPI, DuckDuckGoSearchProvider
from config import MAX_SEARCH_RESULTS
import json
from functools import partial

logger = logging.getLogger(__name__)


class ModifierTreeView(ttk.Treeview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.selected_modifiers = []
        self.bind("<<TreeviewSelect>>", self.on_select)

    def on_select(self, event):
        self.selected_modifiers = []
        for item in self.selection():
            item_text = self.item(item, "text")
            if item_values := self.item(item, "values"):
                self.selected_modifiers.append((item_text, item_values[0]))


class App(tk.Tk):
    modifier_groups: Dict[str, Dict[str, str]] = {
        "SONG WRITING": {
            "Brainstorm Concepts": "Based on the above context and using it as inspiration, generate a list of potential concepts that could be developed into compelling lyrics for a song",
            "Narrow Down and Select Concept": "Evaluate each concept from the above list and determine which one(s) are the best quality by playing around with some potential verses, hooks, wordplay, you could use for each one and optionally mixing and matching concepts to form complex combinations of concepts, and at the end of your experimentation, decide the best one you choose for developing into a full fledged song"
        },
        "JOKE WRITING": {
            "Comedy Technique": "Analyze the current content and suggest three different comedy techniques that could be applied to enhance its humor. Provide brief examples for each technique.",
            "Punch-up": "Review the existing content and punch-up the dialogue or descriptions to make them snappier, funnier, and more engaging. Focus on adding unexpected twists, wordplay, or exaggeration where appropriate."
        },
        "REASONING": {
            "Analyze for error": "Analyze the above response. What are the potential errors, flaws, or missteps in the reasoning?",
            "Identify Assumptions": "Identify any unstated assumptions in the previous answer. How might these assumptions impact the conclusion?",
            "Consider Counterarguments": "What counterarguments or alternative perspectives have not been considered?",
            "Logical Fallacies": "Are there any logical fallacies present in the reasoning? If so, how can they be addressed?",
            "Additional Context": "What additional context or information would make this response more comprehensive?",
            "Organize for Clarity": "How can the structure or organization of the answer be improved for clarity?",
            "Clarify Ambiguities": "Are there any ambiguities or vague statements that need clarification?",
            "Enhance with examples": "What specific examples or evidence could strengthen the argument?",
            "Mitigate Bias": "Are there any potential biases in the response? How can they be mitigated?",
            "Address Limitations": "What are the limitations of this answer? How can they be acknowledged or addressed?",
            "Lossless Conciseness": "How can the response be made more concise without losing important information?",
            "Broaden Usefulness": "How can the answer be improved to address a wider range of scenarios or use cases?",
            "Explore and Elaborate Implications": "What are the potential implications or consequences of this answer that haven't been explored?",
            "Enhance Applicability": "How can the response be made more actionable or practical for the user?",
            "Enrich with Interdisciplinary Connections": "What interdisciplinary connections or insights could enrich this answer?",
            "Refine certainty/uncertainty": "How can the certainty or uncertainty of various claims in the response be more accurately conveyed?",
            "Is anything missing?": "What may be missing from the response that, if included, would provide an even more accurate and comprehensive answer?",
            "Enhance engagement potential": "How can the answer be improved to be more engaging or memorable for the reader?",
            "Recap and synthesize all of the above in a final draft": "Synthesize the improvements identified in the previous iterations. How can they be integrated to create a more robust and refined response?"
        }
    }

    def __init__(
        self,
        search_manager: SearchManager,
        tool_manager: ToolManager,
        model_manager: ModelManager,
        agent_manager: AgentManager,
        llm_provider,
        researcher_agent,  # Receive the researcher_agent
        writer_agent,      # Receive the writer_agent
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.title("Creative AI writer")
        self.geometry("800x600")

        self.search_manager = search_manager
        self.tool_manager = tool_manager
        self.model_manager = model_manager
        self.agent_manager = agent_manager
        self.llm_provider = llm_provider
        self.researcher_agent = researcher_agent
        self.writer_agent = writer_agent

        self.chat_log: List[str] = []
        self.context = ""
        self.current_prompt = ""
        self.last_output = ""

        # Register tools from the tools module
        self.tool_manager.register_tool("foia_search", tools.foia_search)
        self.tool_manager.register_tool("search", partial(tools.web_search, self.search_manager))  # Use partial to pass search_manager

        self.setup_ui()

    def setup_ui(self):
        self.setup_main_frame()
        self.setup_sidebar()
        self.setup_menu()

    def setup_main_frame(self):
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(side="left", fill="both", expand=True)

        self.chat_history = scrolledtext.ScrolledText(self.main_frame, wrap="word")
        self.chat_history.pack(fill="both", expand=True)

        self.user_prompt = ttk.Entry(self.main_frame)
        self.user_prompt.pack(fill="x")
        self.user_prompt.bind("<Return>", self.run_workflow)

    def setup_sidebar(self):
        self.sidebar_frame = ttk.Frame(self)
        self.sidebar_frame.pack(side="right", fill="y")

        self.model_label = ttk.Label(self.sidebar_frame, text="Model:")
        self.model_label.pack()

        self.model_var = tk.StringVar(value="writer")
        self.model_dropdown = ttk.Combobox(self.sidebar_frame, textvariable=self.model_var)
        self.model_dropdown['values'] = list(self.modifier_groups.keys())
        self.model_dropdown.pack()

        self.modifier_tree = ModifierTreeView(self.sidebar_frame)
        self.modifier_tree.pack(fill="both", expand=True)

    def setup_menu(self):
        self.menu_bar = Menu(self)
        self.config(menu=self.menu_bar)

        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Open", command=self.open_file)
        self.file_menu.add_command(label="Save", command=self.save_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.quit)

        self.edit_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(label="Undo", command=self.undo)
        self.edit_menu.add_command(label="Redo", command=self.redo)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Cut", command=self.cut)
        self.edit_menu.add_command(label="Copy", command=self.copy)
        self.edit_menu.add_command(label="Paste", command=self.paste)

    def run_workflow(self, event):
            """
            Run a workflow based on user input from a prompt.

            This method processes user input to either execute a specified tool with arguments or interact with an AI model. It captures the result or error message and updates the chat history display accordingly.

            Args:
                self: 
                event: The event that triggered the workflow execution.

            Returns:
                None

            Raises:
                Exception: If an error occurs during tool execution.

            Examples:
                To execute a tool, the user might input: "tool_name(arg1, arg2)".
                For regular AI interaction, the user can simply input a question or statement.
            """
            user_input = self.user_prompt.get()
            self.user_prompt.delete(0, tk.END)

            if match := re.match(r"(\w+)\((.*)\)", user_input):
                tool_name = match[1]
                arguments = [arg.strip() for arg in match[2].split(",")]
                try:
                    result = self.tool_manager.execute_tool(tool_name, *arguments)
                    message = f"Tool '{tool_name}' Result: {result}\n"
                except Exception as e:
                    message = f"Error: {e}\n"
                    print(f"Error: {e}")  
            else:
                # ... regular LLM interaction
                full_prompt = self.generate_prompt(user_input)
                response = self.llm_provider.generate_response(full_prompt)
                message = f"AI: {response}\n"

            # Display the message (tool result or AI response)
            self.chat_history.config(state="normal")
            self.chat_history.insert(tk.END, message)
            self.chat_history.config(state="disabled")
            self.update()

    def generate_prompt(self, user_input):
        return f"""Previous conversation:
{self.chat_history.get("1.0", tk.END)}

User: {user_input}
AI:"""

    def open_file(self):
        # Implementation of open file
        pass

    def save_file(self):
        # Implementation of save file
        pass

    def undo(self):
        # Implementation of undo
        pass

    def redo(self):
        # Implementation of redo
        pass

    def cut(self):
        # Implementation of cut
        pass

    def copy(self):
        # Implementation of copy
        pass

    def paste(self):
        # Implementation of paste
        pass