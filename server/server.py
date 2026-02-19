import json
import logging
logger = logging.getLogger(__name__)
from datetime import datetime

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse

from models.request import A2ARequest, SendTaskRequest
from models.json_rpc import JSONRPCResponse, InternalError
from models.agent import AgentCard
from agents.google_adk import task_manager


from fastapi.encoders import jsonable_encoder
class A2AServer:
    """A2A Server"""

    def __init__(self, host="0.0.0.0", port=5000, agent_card: AgentCard=None, task_manager: task_manager = None):

        self.host = host
        self.port = port
        self.agent_card = agent_card
        self.task_manager = task_manager

        self.app = Starlette()
        self.app.add_route("/", self.handle_request, methods=["POST"])
        self.app.add_route("/.well-known/agent.json", self._get_agent_card, methods=["GET"])

    def start(self):

        if not self.agent_card or not self.task_manager:
            raise ValueError("Agent card and task manager are required")
        
        import uvicorn
        uvicorn.run(self.app, host=self.host, port=self.port)
    
    def _get_agent_card(self, request: Request):
        """Get the agent card"""
        return JSONResponse(self.agent_card.model_dump(exclude_none=True))
    
    async def handle_request(self, request: Request):
        """Handle a request"""
        
        try: 
            
            body = await request.json()
            print(f"Incoming request: {json.dumps(body, indent=4)}")
            
            json_rpc = A2ARequest.validate_python(body)

            if isinstance(json_rpc, SendTaskRequest):
                result = await self.task_manager.on_send_task(json_rpc)
            else:
                raise ValueError(f"Invalid request: {json_rpc}")
            
            return self._create_response(result)
        
        except Exception as e:

            logger.error(f"Error handling request: {e}")

            return JSONResponse(
                JSONRPCResponse(
                    id=None,
                    error=InternalError(
                        message=str(e),
                    )
                ).model_dump(),
                status_code=400
            )
    
    def _create_response(self, result):
        """Create a response"""

        if isinstance(result, JSONRPCResponse):
            return JSONResponse(content=jsonable_encoder(result.model_dump(exclude_none=True)))
        else :
            raise ValueError(f"Invalid result: {result}")



        