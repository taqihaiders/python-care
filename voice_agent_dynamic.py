"""
This is a voice agent that listens to the user and responds with text.
"""

import logging
import asyncio

from dotenv import load_dotenv
from livekit.agents import JobContext, WorkerOptions, cli, JobProcess
from livekit.agents.voice import Agent, AgentSession
from livekit.plugins import silero
from models import CallDetails
from helper import (
    get_call_details,
    setup_stt,
    setup_tts,
    setup_llm,
    get_call_summary,
    update_inbound_call,
    get_current_epoch,
)


load_dotenv()
# Define format and date format
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Create formatter
formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("voice-agent.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class VoiceAgent(Agent):
    """Voice agent that listens to the user and responds with text."""

    def __init__(
        self,
        call_details: CallDetails,
    ) -> None:
        self.call_details = call_details
        super().__init__(
            instructions=call_details.system_prompt + "\n\n" + call_details.rag_content,
            stt=setup_stt(call_details),
            llm=setup_llm(call_details),
            tts=setup_tts(call_details),
            vad=silero.VAD.load(),
        )

    async def on_enter(self):
        if self.call_details.first_message:
            self.session.generate_reply(
                instructions=f"Say the welcome message {self.call_details.first_message}"
            )

    async def on_exit(self):
        if self.call_details.last_message:
            self.session.generate_reply(
                instructions=f"Say the goodbye message {self.call_details.last_message}"
            )


async def entrypoint(ctx: JobContext):
    """Entrypoint for the voice agent."""

    await ctx.connect()
    print(f"Room name: {ctx.room.name}")
    session = AgentSession()

    call_details: CallDetails = get_call_details(ctx.room.name)

    @session.on("conversation_item_added")
    def on_transcript(event):
        call_details.call_transcript.append(
            {"role": event.item.role, "content": event.item.content}
        )

    await session.start(
        agent=VoiceAgent(call_details),
        room=ctx.room,
    )

    def end_of_call_activities(event):
        print(f"Participant disconnected: {event}")
        get_call_summary(call_details)
        call_details.call_end_time = get_current_epoch()

        asyncio.create_task(
            update_inbound_call(
                ctx.room.name,
                call_details,
            )
        )

    ctx.room.on("participant_disconnected", end_of_call_activities)


def prewarm_process(proc: JobProcess):
    """preload silero VAD in memory to speed up session start"""
    proc.userdata["vad"] = silero.VAD.load()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm_process))
