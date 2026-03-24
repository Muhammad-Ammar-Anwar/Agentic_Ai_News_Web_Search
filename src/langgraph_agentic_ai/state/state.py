from typing import Annotated
from typing_extensions import TypedDict, List, NotRequired
from langgraph.graph.message import add_messages

class State(TypedDict):
    """
    Represent the structure of the state used in graph
    
    """

    messages: Annotated[List,add_messages]
    news_data: NotRequired[List]
    summary: NotRequired[str]
    markdown: NotRequired[str]
