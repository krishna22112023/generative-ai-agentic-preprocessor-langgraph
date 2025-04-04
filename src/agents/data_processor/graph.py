from langgraph.graph import StateGraph, END
#from langgraph.prebuilt import ToolNode

from src.agents.data_processor.state import State
from src.agents.data_processor.chain import DataProcessorChain
from src.agents.data_processor.node import DataProcessorNode


class DataProcessorGraph:
    @classmethod
    def get_workflow(cls, **kwargs):
        stream = kwargs.get('stream', False)
        data_process_generator = DataProcessorChain.get_generator_chain()
        data_process_node = DataProcessorNode(data_process_generator)

        workflow = StateGraph(State)

        if stream is False:
            workflow.add_node('generator', data_process_node.generator_node)
        else:
            workflow.add_node('generator', data_process_node.agenerator_node)
        
        workflow.add_node('tools', data_process_node.tool_node)

        workflow.set_entry_point('generator')
        
        workflow.add_conditional_edges(
            'generator',
            data_process_node.should_continue,
            {
                "continue": "tools",
                "end": END,
            },
        )
        workflow.add_edge('tools', 'generator')

        return workflow
    
    @classmethod
    async def get_workflow_mcp(self, **kwargs):
        stream = kwargs.get('stream', False)
        data_process_generator = await DataProcessorChain.get_generator_chain_mcp()
        data_process_node = DataProcessorNode(data_process_generator)

        workflow = StateGraph(State)

        if stream is False:
            workflow.add_node('generator', data_process_node.generator_node)
        else:
            workflow.add_node('generator', data_process_node.agenerator_node)
        
        workflow.add_node('tools', data_process_node.tool_node_mcp)

        workflow.set_entry_point('generator')
        
        workflow.add_conditional_edges(
            'generator',
            data_process_node.should_continue,
            {
                "continue": "tools",
                "end": END,
            },
        )
        workflow.add_edge('tools', 'generator')

        return workflow