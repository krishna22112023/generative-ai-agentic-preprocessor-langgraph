import json
from langchain_core.load import dumps, loads
from langchain_community.storage import RedisStore
from langchain_community.utilities.redis import get_client

from src.agents.data_processor.graph import DataProcessorGraph
from src.schemas.chat import ChatRequest
from loguru import logger

from config import settings

client = get_client(settings.REDIS_URL)
memory_store = RedisStore(client=client)

graphs = {}
graphs['coach'] = DataProcessorGraph.get_workflow_mcp(stream=True).compile()
graphs['coach_sync'] = DataProcessorGraph.get_workflow_mcp(stream=False).compile()


class ChatService:
    def __init__(self, request: ChatRequest):
        self.messages = request.input.messages

        self.config_info = request.config
        self.thread_id = self.config_info.configurable.thread_id
        self.agent_id = self.config_info.configurable.agent_id
        self.reset_history = self.config_info.configurable.reset_history

    def check_history(self):
        if self.reset_history is True:
            memory_store.mdelete([f"{self.agent_id}_{self.thread_id}"])

    def load_history(self):
        memory = memory_store.mget([f"{self.agent_id}_{self.thread_id}"])[0]

        #save the last 10 conversation turns in memory
        if memory is not None:
            memory = loads(memory.decode())
            history = memory[-10:]
            messages = history + self.messages
 
        else:
            messages = self.messages

        return messages

    def save_history(self, messages):
        if messages is not None:
            bytes_messages = dumps(messages, ensure_ascii=False).encode()
            memory_store.mset([(f"{self.agent_id}_{self.thread_id}", bytes_messages)])

async def stream_chat_event(body: ChatRequest):
    cs = ChatService(body)
    cs.check_history()
    messages = cs.load_history()

    result = None
    first = True
    last_len = 0
    async for stream_mode, chunk in graphs[cs.agent_id].astream(
            input={'messages': messages},
            config=cs.config_info.model_dump(),
            stream_mode=["custom", 'values']
    ):
        if stream_mode == 'custom':
            if 'text' in chunk:
                if first is True:
                    first = False
                    last_len = len(chunk['text'])
                else:
                    tmp_text = chunk['text'][last_len:]
                    last_len = len(chunk['text'])
                    chunk['text'] = tmp_text
            json_result = json.dumps(chunk)
            yield f"event: messages/partial\ndata: {json_result}\n\n"

        elif stream_mode == 'values':
            result = chunk['messages']

    cs.save_history(result)


def invoke_chat_event(body: ChatRequest):
    body.config.configurable.agent_id = body.config.configurable.agent_id + '_sync'

    cs = ChatService(body)
    cs.check_history()

    messages = cs.load_history()

    reply = graphs[cs.config_info.configurable.agent_id].invoke(
        input={'messages': messages},
        config=cs.config_info.model_dump()
    )

    result = reply['messages']

    cs.save_history(result)

    try:
        text = reply['messages'][-1].content
        res = {'text': text}
    except:
        print('error in getting reply message')
        res = {'text': ""}
    return res


def demo_invoke():
    payload = {
        "input": {
            "messages": [
                {
                    "type": "human",
                    "content": "Why are WSQ courses eligible?"
                }
            ]
        },
        "config": {
            "configurable": {
                "thread_id": "S0002",
                "agent_id": "coach",
                "reset_history": False,
                "stream": False
            }
        }
    }

    body = ChatRequest(**payload)
    res = invoke_chat_event(body)
    print(res)


async def demo_stream():
    payload = {
        "input": {
            "messages": [
                {
                    "type": "human",
                    "content": "Hi"
                }
            ]
        },
        "config": {
            "configurable": {
                "thread_id": "S0001",
                "agent_id": "coach",
                "reset_history": False,
                "stream": False
            }
        }
    }

    body = ChatRequest(**payload)
    async for chunk in stream_chat_event(body):
        print(chunk)


def main():
    # import asyncio
    # asyncio.run(demo_stream())
    demo_invoke()


if __name__ == '__main__':
    main()