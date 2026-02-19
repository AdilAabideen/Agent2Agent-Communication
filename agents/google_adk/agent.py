from dotenv import load_dotenv
from datetime import datetime
import traceback

from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner

from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.sessions import InMemorySessionService

from google.genai import types

load_dotenv()


class TellTimeAgent:

    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self, name: str):
        self._agent = self._build_agent()
        self._user_id = 'tell_time_agent'

        self._runner = Runner(
            app_name=self._agent.name,
            agent=self._agent,
            artifact_service=InMemoryArtifactService(),
            memory_service=InMemoryMemoryService(),
            session_service=InMemorySessionService(),
        )
    
    

    def _build_agent(self):
        """Build the agent"""

        return LlmAgent(
            model= "gemini-3-flash-preview",
            name="tell_time_agent",
            description="A agent that tells the time",
            instruction="Reply with the current time in the format 'HH:MM:SS'",
        )
    
    async def invoke(self, input: str, session_id: str):

        try: 

            session = await self._runner.session_service.get_session(
                app_name=self._agent.name,
                user_id=self._user_id,
                session_id=session_id,
            )
            
            if session is None:
                session = await self._runner.session_service.create_session(
                    app_name=self._agent.name,
                    user_id=self._user_id,
                    session_id=session_id,
                )
            
            content = types.Content(
                role='user',
                parts=[types.Part.from_text(text=input)]
            )

            last_event = None
            async for event in self._runner.run_async(
                user_id=self._user_id,
                session_id=session_id,
                new_message=content,
            ):
                last_event = event

            
            if not last_event or not last_event.content or not last_event.content.parts:
                return ""
            
            return "\n".join(part.text for part in last_event.content.parts if part.text)
        
        except Exception as e:

            print(f"Error running agent: {e}")
            traceback.print_exc()
            return "Sorry, I encountered an error while processing your request. Please try again."