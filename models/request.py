from typing import Annotated, Union, Literal
from pydantic import Field
from pydantic.type_adapter import TypeAdapter
from models.json_rpc import JSONRPCRequest, JSONRPCResponse
from models.task import Task, TaskSendParams
from models.task import TaskQueryParams


# Used to send a new task to an agent
class SendTaskRequest(JSONRPCRequest):
    method: Literal["tasks/send"] = "tasks/send"
    params: TaskSendParams


# Used to retrieve a task's status or history
class GetTaskRequest(JSONRPCRequest):
    method: Literal["tasks/get"] = "tasks/get"
    params: TaskQueryParams


# Discriminated union of supported request types that automatically identifies and parses requests based on the method field
A2ARequest = TypeAdapter(
    Annotated[
        Union[
            SendTaskRequest,
            GetTaskRequest,
        ],
        Field(discriminator="method")
    ]
)


# Response model for a successful "tasks/send" request
class SendTaskResponse(JSONRPCResponse):
    result: Task | None = None


# Response model for a "tasks/get" request
class GetTaskResponse(JSONRPCResponse):
    result: Task | None = None
