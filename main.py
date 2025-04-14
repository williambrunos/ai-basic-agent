from llama_index.llms.ollama import Ollama
from llama_index.core.tools import FunctionTool
from llama_index.core.agent.workflow import AgentWorkflow
import asyncio

def check_weather(location: str) -> str:
    """Useful for checking the weather in a specific location"""
    # location = params.location
    message = f"The weather in {location} is Cloudly!"
    return message


async def main():
    # Defining the LLM
    llm = Ollama(model="llama3.2", temperature=0.15, request_timeout=120.0)

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
        system_prompt="You are a helpful assistant that can check the weather. You only use the check weather tool to check the weather in a specific location."
    )
    response = await agent.run(user_msg="What is the weather in new york right now?")
    print(response)


if __name__ == "__main__":
    # Run the main function asynchronously
    asyncio.run(main())
