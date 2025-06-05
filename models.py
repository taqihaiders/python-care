from dataclasses import dataclass


@dataclass
class CallDetails:
    """Details of the call."""

    room_name: str
    phone_to: str
    phone_from: str
    template_id: str  # PAuthQOnBoardingTemplate
    stt_provider: str
    stt_model: str
    stt_language: str
    stt_api_key: str
    tts_provider: str
    tts_model: str
    tts_voice: str
    tts_api_key: str
    llm_provider: str
    llm_model: str
    llm_api_key: str
    system_prompt: str
    rag_content: str
    first_message: str
    last_message: str
    call_start_time: int
    call_end_time: int
    call_transcript: list[dict]
    call_summary: str
