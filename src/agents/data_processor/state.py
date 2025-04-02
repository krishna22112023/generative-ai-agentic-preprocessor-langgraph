from typing import TypedDict, Annotated, Any, List
from langgraph.graph.message import AnyMessage, add_messages


class State(TypedDict):
    """
    Represents the state of a data processing agent.

    Attributes:
        messages: A list of AnyMessage objects, annotated with the `add_messages` function.
        question: A string representing the question being processed.
    """
    messages: Annotated[List[AnyMessage], add_messages]
    question: str