import logging  # Standard Python module for logging debug/info messages
logger = logging.getLogger(__name__)

import asyncio

# 🔁 Import the shared in-memory task manager from the server
from server.task_manager import InMemoryTaskManager

# 🤖 Import the actual agent we're using (Gemini-powered TellTimeAgent)
from agents.google_adk.agent import TellTimeAgent

# 📦 Import data models used to structure and return tasks
from models.request import SendTaskRequest, SendTaskResponse, GetTaskRequest, GetTaskResponse
from models.task import Message, Task, TextPart, TaskStatus, TaskState

class AgentTaskManager(InMemoryTaskManager):

    def __init__(self, agent: TellTimeAgent):
        super().__init__()
        self.agent = agent
    
    def _get_user_query(self, request: GetTaskRequest) -> str:
        """Get the user query from the request"""
        return request.params.message.parts[0].text
    
    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        """Handle a request to send a task"""

        logger.info(f"Sending task: {request.params.id}")

        task = await self.upsert_task(request.params)
        query = self._get_user_query(request)

        result_text = await self.agent.invoke(query, request.params.sessionId)
        agent_Message = Message(
            role="agent",
            parts=[TextPart(text=result_text)],
        )
        task.history.append(agent_Message)

        async with self.lock:
            task.status = TaskStatus(
                state=TaskState.COMPLETED,
            )
            task.history.append(agent_Message)
        
        return SendTaskResponse(
            id=task.id,
            result=task,
        )

