from llama_index.llms.ollama import Ollama
from llama_index.core.tools import FunctionTool
from llama_index.core.agent.workflow import AgentWorkflow, AgentStream, ToolCallResult
import asyncio
import yaml
import requests
from config import load_agent_config
from weather import check_weather

async def main():
    agent_config = load_agent_config("agent_config/agent_config.yaml")
    llm = Ollama(
        model=agent_config["llm"]["model"],
        temperature=agent_config["llm"].get("temperature", 0.7),
        request_timeout=agent_config["llm"].get("request_timeout", 60.0)
    )

    # Creating an agent with the check weather tool
    agent = AgentWorkflow.from_tools_or_functions(
        tools_or_functions=[
            FunctionTool.from_defaults(
                name="check_weather",
                description="Checks weather for a specific location.",
                fn=check_weather
            )
        ],
        llm=llm,
        system_prompt=agent_config["prompt"]["system_prompt"]
    )
    handler = agent.run(user_msg="How is the weather in Sobral Ceará, Brazil right now?")
                              
    print("\n--- Agent Reasoning Trace ---")
    async for ev in handler.stream_events():
        if isinstance(ev, ToolCallResult):
            print("")
            print("Called tool: ", ev.tool_name, ev.tool_kwargs, "=>", ev.tool_output)
        elif isinstance(ev, AgentStream): 
            print(ev.delta, end="", flush=True)

    resp = await handler
    print(resp)


if __name__ == "__main__":
    asyncio.run(main())
