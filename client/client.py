from typing import Dict, Any
from uuid import uuid4
from httpx_sse import connect_sse
import httpx
import json

from models.agent import AgentCard
from models.request import SendTaskRequest, GetTaskRequest
from models.task import Task, TaskSendParams
from models.json_rpc import JSONRPCRequest
from models.agent import AgentCard

class A2AClientHTTPError(Exception):
    """Raised when an HTTP request fails (e.g., bad server response)"""
    pass

class A2AClientJSONError(Exception):
    """Raised when the response is not valid JSON"""
    pass

class A2AClient:
    """A2A Client"""

    def __init__(self, url: str, agent_card: AgentCard=None):
        """Initialize the client"""
    
        if agent_card :
            self.url=agent_card.url
        elif url : 
            self.url=url
        else :
            raise ValueError("Either agent_card or base_url must be provided")


    async def send_task(self, payload: Dict[str, Any]) -> Task:
        """Send a task to the agent"""
        
        request = SendTaskRequest(
            id=uuid4().hex,
            params=TaskSendParams(
                **payload,
            ),
        )

        print(f"Sending request: {request.model_dump_json(indent=4)}")

        response = await self.send_request(request)
        return Task(**response["result"])
    
    async def get_task(self, payload: Dict[str, Any]) -> Task:
        """Get a task from the agent"""

        request = GetTaskRequest(params=payload)
        response = await self.send_request(request)
        return Task(**response["result"])
    
    async def send_request(self, request: JSONRPCRequest) -> Dict[str, Any]:
        """Send a request to the agent"""

        async with httpx.AsyncClient() as client:
            try : 
                response = await client.post(self.url, json=request.model_dump(), timeout=30)
                response.raise_for_status()
                return response.json()
            
            except httpx.HTTPStatusError as e:
                raise A2AClientHTTPError(f"HTTP request failed: {e}")
            except json.JSONDecodeError as e:
                raise A2AClientJSONError(f"Invalid JSON response: {e}")