import os
import logging

import json
from typing import Annotated, Dict, Any
from dataclasses import dataclass

from dotenv import load_dotenv
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    llm,
)
from livekit.agents.pipeline import  VoicePipelineAgent
from livekit.plugins import deepgram, openai, silero, cartesia, elevenlabs
from rag_service import RAGService

load_dotenv()

logger = logging.getLogger("demo")
logger.setLevel(logging.INFO)
rag_service = RAGService()


@dataclass
class SessionConfig:
    namespace: str | None
    mode: str
    summary: str | None = None


def parse_session_config(data: Dict[str, Any]) -> SessionConfig:

    config = SessionConfig(
        namespace=data.get("namespace", None),
        mode=data.get("mode", "reservations"),
        summary=data.get("summary", None),
    )
    return config


class RAGFnc(llm.FunctionContext):
    """
    The class defines a set of LLM functions that the assistant can execute.
    """

    def __init__(self, namespace: str):
        super().__init__()  # Call the superclass's __init__ method
        self.namespace = namespace

    @llm.ai_callable(description="Get more information about a specific topic")
    async def query_info(
        self,
        query: Annotated[str, llm.TypeInfo(description="The user's query")],
    ) -> str:
        logger.info(f"Querying RAG with: {query}")
        return rag_service.retrieve_docs(query, self.namespace)


def prewarm_process(proc: JobProcess):
    # preload silero VAD in memory to speed up session start
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    participant = await ctx.wait_for_participant()

    metadata = participant.metadata or "{}"
    config = parse_session_config(json.loads(metadata))
    namespace = config.namespace
    fnc_ctx = RAGFnc(namespace)

    initial_chat_ctx = llm.ChatContext().append(
        role="system",
        text=(
            "You are a knowledgeable and conversational voice assistant designed to help users interact with and understand the contents of a PDF document. "
            "You assist users by summarizing sections, answering specific questions, or providing overviews based on the content of the document. "
            "Keep the conversation friendly, clear, and engaging, using natural and concise language. Avoid technical jargon unless the user explicitly asks for it. "
            "Do not include headers or special formatting in your responses, as this is a voice interaction. Use simple and human-like responses. "
            "For each query, refer only to the provided document content and avoid making up any information beyond what is explicitly stated. "
            "If a user asks for something not covered in the document, politely let them know that the requested information is not available. "
            "Structured Steps for Interaction: "
            "1. Ask the user for their specific query or what part of the document they would like help with. "
            "2. Use the document's content to provide a concise and accurate response. "
            "3. Summarize or expand only when necessary, based on the user's preference. "
            "4. Allow the user to ask follow-up questions or clarify their query. "
            "5. Be polite and redirect the user if their request is outside the scope of the document. "
            "Make sure to use `query_info` tool to get more information about a specific topic if needed."
            "Capabilities: "
            "- Provide answers to specific questions from the document's content. "
            "- Offer guidance on navigating or understanding the structure of the document. "
            "Your role is to make the document's content more accessible and easy to understand in a conversational and human-like manner."
            f"{'Quick Brief about the Document:' if config.summary else ''}"
            f"{config.summary}"
            "No Not only use the brief as your source of truth, but also use the document's content to provide accurate and relevant information. "
            "The brief is a summary of the document's content and structure, but the document itself contains the detailed information. "
            "Do not say that you cannot find the information in the document without querying the document using the `query_info` tool first and confirm that the retrieved data is not related."
        ),
    )

    logger.info(f"connecting to room {ctx.room.name}")

    stt = deepgram.STT(api_key=os.getenv("DEEPGRAM_API_KEY", ""))
    tts = deepgram.TTS(api_key=os.getenv("DEEPGRAM_API_KEY", ""))
    # tts = elevenlabs.TTS(api_key=os.getenv("ELEVENLABS_API_KEY", ""))
    # tts = cartesia.TTS(api_key=os.getenv('CARTESIA_API_KEY', ""))
    # tts = openai.TTS(api_key=os.getenv("OPENAI_API_KEY", ""),voice='nova')

    agent = VoicePipelineAgent(
        vad=ctx.proc.userdata["vad"],
        stt=stt,
        # llm=openai.LLM.with_azure(
        #     azure_endpoint=os.getenv("AZURE_URL", ""),
        #     azure_deployment=os.getenv("AZURE_DEPLOYMENT", ""),
        #     api_key=os.getenv("AZURE_API_KEY", ""),
        #     api_version=os.getenv("AZURE_API_VERSION", ""),
        # ),
        llm=openai.LLM(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY", "")),
        # llm=openai.LLM.with_groq(model="llama-3.1-8b-instant",api_key=os.getenv("GROQ_API_KEY", "")),
        # llm=openai.LLM.with_groq(
        #     model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY", "")
        # ),
        tts=tts,
        fnc_ctx=fnc_ctx,
        chat_ctx=initial_chat_ctx,
        max_nested_fnc_calls=2,
    )

    # Start the assistant. This will automatically publish a microphone track and listen to the participant.
    agent.start(ctx.room, participant)

    await agent.say(
        "Hi, I'm Alice, your personal document assistant. How can I help you today?",
        allow_interruptions=True,
    )


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm_process,
        ),
    )
