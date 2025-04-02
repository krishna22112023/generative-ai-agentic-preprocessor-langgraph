import gradio
from termcolor import colored
import pyfiglet
from langchain_core.messages import HumanMessage


from langgraph.store.memory import InMemoryStore
from langchain_community.storage import RedisStore
from langchain_community.utilities.redis import get_client

import sys
import pyprojroot
root = pyprojroot.find_root(pyprojroot.has_dir("config"))
sys.path.append(str(root))

from src.agents.data_processor.graph import DataProcessorGraph
from config import settings,agent_config

client = get_client(settings.REDIS_URL)
memory_store = RedisStore(client=client)
# memory_store = InMemoryStore()

async def stream_response(message, history):
    print(colored(pyfiglet.figlet_format('chat'), 'magenta'))

    print(colored('history', 'blue', attrs=['bold']), colored(len(history), 'blue'))

    print(colored('message', 'blue', attrs=['bold']), colored(message, 'cyan'))

    messages = history + [HumanMessage(content=message)]

    init_state = {'messages': messages}

    if agent_config.ENABLE_MCP_TOOLS:
        workflow = await DataProcessorGraph.get_workflow_mcp(stream=True)
    else:
        workflow = DataProcessorGraph.get_workflow(stream=True)
    compiled_workflow = workflow.compile()    
    async for cat, chunk in compiled_workflow.astream(init_state, stream_mode=['custom', 'values']):
        if cat == 'custom':
            if 'text' in chunk:
                yield chunk['text']
            elif 'status' in chunk:
                yield "Status: " + chunk['status']
            else:
                pass

demo_interface = gradio.ChatInterface(
    stream_response,
    type="messages",
    title="Data Processor Agent",
    multimodal=False
)

print(colored(pyfiglet.figlet_format('Agentic CV Data Processor'), 'cyan'))
demo_interface.launch(share=False, debug=False, server_name='0.0.0.0', server_port=8081, ssl_verify=False)