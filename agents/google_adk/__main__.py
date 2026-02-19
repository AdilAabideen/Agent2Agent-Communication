from server.server import A2AServer
from models.agent import AgentCard, AgentCapabilities, AgentSkill

from agents.google_adk.agent import TellTimeAgent
from agents.google_adk.task_manager import AgentTaskManager

import click 
import logging

logger = logging.getLogger(__name__)

@click.command()
@click.option("--host", default="0.0.0.0", help="Host to run the server on")
@click.option("--port", default=5000, help="Port to run the server on")
def main(host, port):
    """Run the server"""
    

    capabilities = AgentCapabilities(
        streaming=False,
        pushNotifications=False,
        stateTransitionHistory=False,
    )

    skill = AgentSkill(
        id="tell_time",
        name="Tell Time",
        description="Replies with the current time",
        examples=[
            "What is the time?",
            "What time is it?",
            "What is the current time?",
            "What time is it in New York?",
        ],
        inputModes=TellTimeAgent.SUPPORTED_CONTENT_TYPES,
        outputModes=TellTimeAgent.SUPPORTED_CONTENT_TYPES,
    )

    agent_card = AgentCard(
        name="Tell Time Agent",
        description="A agent that tells the time",
        url=f"http://{host}:{port}",
        version="1.0.0",
        capabilities=capabilities,
        skills=[skill],
    )

    server = A2AServer(
        host=host,
        port=port,
        agent_card=agent_card,
        task_manager=AgentTaskManager(TellTimeAgent("tell_time_agent")),
    )

    server.start()

if __name__ == "__main__":
    main()