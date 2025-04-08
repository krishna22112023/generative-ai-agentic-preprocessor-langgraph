import json

from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.store.base import BaseStore
from langgraph.types import StreamWriter
from src.services.mcp.create_client import get_client

import random

import sys
import pyprojroot
root = pyprojroot.find_root(pyprojroot.has_dir("config"))
sys.path.append(str(root))

from src.agents.data_processor.state import State
from src.services.tool.minIO import minio_tools
from src.services.tool.IQA import iqa_tools
from src.services.tool.IR import ir_tools

tools = minio_tools + iqa_tools + ir_tools
tools_by_name = {tool.name: tool for tool in tools}

class DataProcessorNode:
    def __init__(self, generator):
        self.generator = generator

    def gen_waiting_reply(self):
        reply_waiting = [
            "Please hold on for a moment while we review your inquiry.",
            "Kindly wait while we look into your question.",
            "One moment, please, as we analyze your request.",
            "We appreciate your patience while we process your query.",
            "Please bear with us as we check your inquiry.",
            "We're working on your question—please hold on.",
            "Hang on a moment while we examine your query.",
            "Your request is being processed—please wait.",
            "We're investigating your question; one moment, please.",
            "Thank you for waiting as we verify your query.",
            "Just a moment while we address your request.",
            "We are currently looking into your question—please stand by.",
            "We’re reviewing your inquiry; kindly hold on.",
            "Your query is under review; please wait.",
            "We're taking a closer look at your request—kindly wait.",
            "We're verifying the details of your question; thank you for your patience.",
            "Hang tight while we check your inquiry.",
            "We’re double-checking your query—one moment, please.",
            "Just a second, we’re making sure we have the right information for you.",
            "Your query is being examined—please hang on."
        ]

        random_response = random.choice(reply_waiting)
        return random_response

    def tool_node(self, state: State, writer: StreamWriter):
        writer({'status': self.gen_waiting_reply()})
        outputs = []
        for tool_call in state["messages"][-1].tool_calls:
            tool_result = tools_by_name[tool_call["name"]].invoke(tool_call["args"])
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": outputs}
    
    async def tool_node_mcp(self, state: State, writer: StreamWriter):
        tools = await get_client()
        tools_by_name = {tool.name: tool for tool in tools}
        outputs = []
        for tool_call in state["messages"][-1].tool_calls:
            args = tool_call["args"]
            tool = tools_by_name[tool_call["name"]]
            observation = await tool.ainvoke(args)
            outputs.append(
                ToolMessage(
                    content=json.dumps(observation),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": outputs}
    

    def generator_node(self, state: State, config: RunnableConfig, writer: StreamWriter, store: BaseStore):
        inputs = {
            'messages': state['messages']
        }

        result = self.generator.invoke(inputs)

        return {"messages": result}

    async def agenerator_node(self, state: State, config: RunnableConfig, writer: StreamWriter, store: BaseStore):
        inputs = {
            'messages': state['messages']
        }

        first = True
        async for chunk in self.generator.astream(inputs):
            if first:
                gathered = chunk
                first = False
            else:
                gathered = gathered + chunk

            writer({'text': gathered.content})

        return {"messages": gathered}
    
    # Define the conditional edge that determines whether to continue or not
    def should_continue(self,state: State):
        messages = state["messages"]
        last_message = messages[-1]
        # If there is no function call, then we finish
        if not last_message.tool_calls:
            return "end"
        # Otherwise if there is, we continue
        else:
            return "continue"