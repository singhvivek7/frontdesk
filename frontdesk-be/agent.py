import logging

from dotenv import load_dotenv
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    llm,
    metrics,
)
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.plugins import (
    cartesia,
    deepgram,
    noise_cancellation,
    silero,
    turn_detector,
    google,
)

from app.main import addQuery


load_dotenv(dotenv_path=".env.local")
logger = logging.getLogger("voice-agent")


my_unknown_queries = []


def handle_unknown_query(query: str):
    my_unknown_queries.append(query)
    print(f"Unknown queries: {my_unknown_queries}")
    logger.info(f"Hey, I need help answering: {query}")

    addQuery(query)

    return "I don't have that information right now, but I've logged your question for future reference."


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()
    if "unknown_queries" not in proc.userdata:
        proc.userdata["unknown_queries"] = []


async def entrypoint(ctx: JobContext):

    initial_ctx = llm.ChatContext().append(
        role="system",
        text=(
            "You are a voice assistant created by LiveKit. Your interface with users will be voice. "
            "You should use short and concise responses, and avoiding usage of unpronouncable punctuation. "
            "You were created as a demo to showcase the capabilities of LiveKit's agents framework. "
            "If you don't know the answer to a question, respond with: [UNKNOWN_QUERY]"
        ),
    )

    logger.info(f"connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    participant = await ctx.wait_for_participant()
    logger.info(f"starting voice assistant for participant {participant.identity}")

    agent = VoicePipelineAgent(
        vad=ctx.proc.userdata["vad"],
        stt=deepgram.STT(),
        llm=google.LLM(
            model="gemini-2.0-flash-exp",
            temperature=0.8,
        ),
        tts=cartesia.TTS(),
        turn_detector=turn_detector.EOUModel(),
        min_endpointing_delay=0.1,
        max_endpointing_delay=1.0,
        noise_cancellation=noise_cancellation.BVC(),
        chat_ctx=initial_ctx,
    )

    usage_collector = metrics.UsageCollector()

    @agent.on("metrics_collected")
    def on_metrics_collected(agent_metrics: metrics.AgentMetrics):
        metrics.log_metrics(agent_metrics)
        usage_collector.collect(agent_metrics)

    @agent.on("agent_speech_committed")
    def on_agent_speech_committed(message: llm.ChatMessage):
        if "[UNKNOWN_QUERY]" in message.content:

            agent.chat_ctx.messages[-1].content = (
                "Let me check with my supervisor and get back to you."
            )
            # Extract the actual query from the previous user message
            user_query = next(
                (
                    msg.content
                    for msg in agent.chat_ctx.messages[-2:]
                    if msg.role == "user"
                ),
                "unknown query",
            )

            handle_unknown_query(user_query)

            message.content = message.content.replace(
                "[UNKNOWN_QUERY]",
                "I don't have that information right now, but I've logged your question for follow-up.",
            )
            agent.chat_ctx.messages[-1].content = (
                "Let me check with my supervisor and get back to you."
            )

    agent.start(ctx.room, participant)

    await agent.say("Hey, how can I help you today?", allow_interruptions=True)


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        ),
    )
