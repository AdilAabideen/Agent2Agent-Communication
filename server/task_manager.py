from abc import ABC, abstractmethod
from typing import Dict
import asyncio

from models.task import Task, TaskStatus, TaskState, TaskSendParams
from models.request import SendTaskRequest, SendTaskResponse, GetTaskRequest, GetTaskResponse


class TaskManager(ABC):
    """Abstract base class for task managers"""

    @abstractmethod
    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        """Send a task to the task manager"""
        pass

    @abstractmethod
    async def on_get_task(self, request: GetTaskRequest) -> GetTaskResponse:
        """Handle a request to get a task"""
        pass

class InMemoryTaskManager(TaskManager):
    """In-memory task manager"""

    def __init__(self):
        self._tasks: Dict[str, Task] = {}
        self.lock = asyncio.Lock()

    async def upsert_task(self, params: TaskSendParams) -> Task:

        async with self.lock:
            task = self._tasks.get(params.id)

            if task is None:
                task = Task(
                    id=params.id,
                    status=TaskStatus(
                        state=TaskState.SUBMITTED,
                    ),
                    history=[params.message],
                )
            else :
                task.history.append(params.message)
            
            return task
    
    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        """Handle a request to send a task"""
        raise NotImplementedError("Not implemented")
    
    async def on_get_task(self, request: GetTaskRequest) -> GetTaskResponse:
        """Handle a request to get a task"""
        
        async with self.lock:
            query: TaskQueryParams = request.params
            task = self._tasks.get(query.id)

            if not Task:
                return GetTaskResponse(
                    id=query.id,
                    error=JSONRPCError(
                        code=JSONRPCError.CODE_INVALID_REQUEST,
                        message="Task not found",
                    ),
                )
            
            task_copy = task.model_copy()
            if query.historyLength is not None:
                task_copy.history = task_copy.history[-query.historyLength:]
            
            return GetTaskResponse(
                id=query.id,
                result=task_copy,
            )

