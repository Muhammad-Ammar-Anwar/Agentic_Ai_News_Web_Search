<<<<<<< HEAD
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
    filename: NotRequired[str]
=======
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
    filename: NotRequired[str]
>>>>>>> 1c6fc7870aa3a19e2c2fc4efe88feabd82aa7f78
