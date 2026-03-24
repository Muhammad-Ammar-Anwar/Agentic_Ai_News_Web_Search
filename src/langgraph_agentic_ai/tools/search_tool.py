<<<<<<< HEAD
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import ToolNode

def get_tools():
    """
    Return the list of tools to be used in the chatbot
    """
    tools=[TavilySearchResults(max_results=2)]
    return tools


def create_tool_node(tools):
    """
    create and returns a tool node for the graph
    """
=======
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import ToolNode

def get_tools():
    """
    Return the list of tools to be used in the chatbot
    """
    tools=[TavilySearchResults(max_results=2)]
    return tools


def create_tool_node(tools):
    """
    create and returns a tool node for the graph
    """
>>>>>>> 1c6fc7870aa3a19e2c2fc4efe88feabd82aa7f78
    return ToolNode(tools=tools)