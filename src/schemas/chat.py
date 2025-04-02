from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage, ChatMessage


class Configurable(BaseModel):
    thread_id: Optional[str] = Field('S0001', description="The thread ID")
    agent_id: Optional[str] = Field('coach', description="The agent ID")
    reset_history: Optional[bool] = Field(False, description="Whether to clear the history of the chat or not")
    stream: Optional[bool] = Field(True, description="Whether to use stream mode or not")


class Config(BaseModel):
    configurable: Configurable = Field(..., description="The configuration")


class Input(BaseModel):
    messages: List[AnyMessage] = Field(..., description="The message list")


class ChatRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "input": {
                        "messages": [
                            {
                                "type": "human",
                                "content": "prepocess and annotate my data stored in minio bucket named traffic"
                            }
                        ]
                    },
                    "config": {
                        "configurable": {
                            "thread_id": "S0001",
                            "agent_id": "DataProcessor",
                            "reset_history": False
                        }
                    }
                }
            ]
        }
    )
    input: Input = Field(..., description="The input data structure")
    config: Config = Field(..., description="The configuration data structure")