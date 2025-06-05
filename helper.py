from models import CallDetails
from livekit.plugins import anthropic, deepgram, cartesia
import os
from anthropic import Anthropic
import aiohttp
from dotenv import load_dotenv
import time
import logging

load_dotenv()

BASE_URL = os.getenv("CARE_MANAGEMENT_BASE_URL", "https://consoledev.allyzent.com/")
HEADERS = {
    "Authorization": f"Bearer {os.getenv('CARE_MANAGEMENT_AUTH_TOKEN')}",
    "Content-Type": "application/json",
}
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
logger = logging.getLogger(__name__)


def get_current_epoch():
    return int(time.time())


async def get_call_details(room_name: str):
    """Get the call details for the given room name. #phone_to_+16292767002_template_1_from_16292767002"""

    call_details = CallDetails(
        room_name=room_name,
        phone_to=room_name.split("_")[2],
        phone_from=room_name.split("_")[6],
        template_id=room_name.split("_")[4],
        stt_provider="deepgram",
        stt_model="nova-2-general",
        stt_language="en-US",
        stt_api_key=os.getenv("DEEPGRAM_API_KEY"),
        tts_provider="cartesia",
        tts_model="sonic-2",
        tts_voice="Bella",
        tts_api_key=os.getenv("CARTESIA_API_KEY"),
        llm_provider="anthropic",
        llm_model="claude-3-5-sonnet-20240620",
        llm_api_key=os.getenv("ANTHROPIC_API_KEY"),
        system_prompt="You are a helpful assistant that can answer questions and help with tasks.",
        rag_content="",
        first_message="Hello, how can I help you today?",
        last_message="",
        call_transcript=[],
        call_summary="",
        call_start_time=get_current_epoch(),
        call_end_time=None,
    )

    async def get_file_content(file_url: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(file_url, headers=HEADERS) as resp:
                if resp.status == 200:
                    return await resp.text()
                return ""

    async def get_template_details(template_id: str):
        URL = f"{BASE_URL}/api/PAuthQOnBoardingTemplate/{template_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(URL, headers=HEADERS) as resp:
                if resp.status == 200:
                    response = await resp.json()
                    return response
                return None

    template_details = await get_template_details(call_details.template_id)
    if template_details:

        call_details.first_message = (
            template_details["FirstMessage"] or call_details.first_message
        )
        call_details.last_message = (
            template_details["LastMessage"] or call_details.last_message
        )
        call_details.system_prompt = (
            await get_file_content(template_details["PromptFileUrl"])
            or call_details.system_prompt
        )
        call_details.rag_content = (
            await get_file_content(template_details["RAGFileUrl"])
            or call_details.rag_content
        )
        call_details.tts_model = (
            template_details["SelectedVoiceModal"] or call_details.tts_model
        )
        call_details.tts_voice = (
            template_details["SelectedVoice"] or call_details.tts_voice
        )
        call_details.tts_api_key = (
            template_details["API_Keys"] or call_details.tts_api_key
        )
    return call_details


def setup_stt(call_details: CallDetails):
    """Setup the STT provider."""
    if call_details.stt_provider == "deepgram":
        return deepgram.STT(
            model=call_details.stt_model,
            language=call_details.stt_language,
            api_key=call_details.stt_api_key,
        )


def setup_tts(call_details: CallDetails):
    """Setup the TTS provider."""
    if call_details.tts_provider == "cartesia":
        return cartesia.TTS(
            model=call_details.tts_model, api_key=call_details.tts_api_key
        )


def setup_llm(call_details: CallDetails):
    """Setup the LLM provider."""
    if call_details.llm_provider == "anthropic":
        return anthropic.LLM(
            model=call_details.llm_model, api_key=call_details.llm_api_key
        )


def get_call_summary(call_details: CallDetails):
    """Get the call summary from the transcript."""
    response = anthropic_client.messages.create(
        model="claude-3-5-sonnet-laters",
        messages=[
            {
                "role": "user",
                "content": "Summarize the following transcript of a phone call: "
                + call_details.call_transcript,
            },
        ],
        max_tokens=1000,
    )
    call_details.call_summary = response.content[0].text
    return call_details


async def update_inbound_call(room_name: str, call_details: CallDetails):
    """Update the inbound call with the call details."""
    payload = {
        "fromPatient": call_details.phone_from,
        "to": call_details.phone_to,
        "transcript": call_details.call_transcript,
        "summary": call_details.call_summary,
        "status": "completed",
    }
    async with aiohttp.ClientSession() as session:
        async with session.put(
            f"{BASE_URL}/api/InboundCall/",
            json=payload,
            timeout=100,
        ) as resp:
            if resp.status == 200:
                logger.info("Inbound call for %s updated successfully", room_name)
                return await resp.json()
            return None
