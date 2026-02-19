from pydantic import BaseModel
from typing import List


# This class defines what features or protocols the agent supports.
class AgentCapabilities(BaseModel):
    streaming: bool = False
    pushNotifications: bool = False
    stateTransitionHistory: bool = False


# This class defines metadata about a single skill that the agent offers.
class AgentSkill(BaseModel):
    id: str
    name: str
    description: str | None = None
    tags: List[str] | None = None
    examples: List[str] | None = None
    inputModes: List[str] | None = None
    outputModes: List[str] | None = None


# This class provides core metadata about an agent.
class AgentCard(BaseModel):
    name: str
    description: str
    url: str
    version: str
    capabilities: AgentCapabilities
    skills: List[AgentSkill]
