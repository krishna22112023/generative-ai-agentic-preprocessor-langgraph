import traceback
from fastapi import APIRouter
from starlette.responses import StreamingResponse, JSONResponse
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage

from src.schemas.chat import ChatRequest, Input
from src.services.chat_service import stream_chat_event, invoke_chat_event
from config import logger

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post(
    "/generate",
    summary="Send messages to chatbot (Text Bot)",
    description="Send messages to chatbot. (Text Bot)",
)
async def generate(body: ChatRequest = None):
    """Process and route chat messages to either streaming or non-streaming response.
    
    Args:
        body (ChatRequest, optional): The chat request containing messages and configuration.
            Expected format:
            - input: Contains list of messages with their types (human/ai/tool/system)
            - config: Contains configuration including stream mode
    
    Returns:
        Union[StreamingResponse, dict, JSONResponse]: 
            - StreamingResponse for stream mode
            - Dict with response for non-stream mode
            - JSONResponse with error details if exception occurs
    
    Raises:
        Exception: Any exceptions during processing are caught and returned as JSONResponse
    """
    try:
        messages = list()
        for msg in body.input.messages:
            if msg.type == 'human':
                messages.append(HumanMessage(**msg.model_dump()))
            elif msg.type == 'ai':
                messages.append(AIMessage(**msg.model_dump()))
            elif msg.type == 'tool':
                messages.append(ToolMessage(**msg.model_dump()))
            elif msg.type == 'system':
                messages.append(SystemMessage(**msg.model_dump()))
            else:
                messages.append(HumanMessage(**msg.model_dump()))

        request = ChatRequest(input=Input(messages=messages), config=body.config)
        if body.config.configurable.stream is True:
            print('stream')
            return StreamingResponse(stream_chat_event(request), media_type="text/event-stream")
        else:
            print('invoke')
            return invoke_chat_event(request)

    except Exception as e:
        err_detail = traceback.format_exc()
        logger.error(f"input: {body}")
        logger.error(f"details: {e}")
        logger.error(f"trace: {err_detail}")

        return JSONResponse({"input": f"{body}", "details": f"{e}", "trace": f"{err_detail}"}, status_code=500)

