<<<<<<< HEAD
from src.langgraph_agentic_ai.state.state import State


class BasicChatbotNode:
    """
    Basic ChatBot login implementation
    """
    def __init__(self,model):
        self.llm=model

    def process(self,state:State)->dict:
        """
        Processes the input state and generates a chatbot response.
        """
        return {"messages":self.llm.invoke(state['messages'])}
=======
from src.langgraph_agentic_ai.state.state import State


class BasicChatbotNode:
    """
    Basic ChatBot login implementation
    """
    def __init__(self,model):
        self.llm=model

    def process(self,state:State)->dict:
        """
        Processes the input state and generates a chatbot response.
        """
        return {"messages":self.llm.invoke(state['messages'])}
>>>>>>> 1c6fc7870aa3a19e2c2fc4efe88feabd82aa7f78
