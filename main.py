from llama_index.llms.ollama import Ollama
from llama_index.core.tools import FunctionTool
from llama_index.core.agent.workflow import AgentWorkflow
import asyncio
import yaml


def check_weather(location: str) -> str:
    """Useful for checking the weather in a specific location"""
    # location = params.location
    message = f"The weather in {location} is Cloudly!"
    return message

def load_agent_config(yaml_path: str):
    """Load agent configuration from a YAML file."""
    with open(yaml_path, 'r') as file:
        config = yaml.safe_load(file)
    return config


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
    response = await agent.run(user_msg="How is the weather in new york right now?")
    print(response)


if __name__ == "__main__":
    # Run the main function asynchronously
    asyncio.run(main())
