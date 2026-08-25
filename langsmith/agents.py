from langchain_groq import ChatGroq
from langchain_core.tools import tool
import requests
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import create_agent
from dotenv import load_dotenv

load_dotenv()

search_tool = DuckDuckGoSearchRun()


@tool
def get_weather_data(city: str) -> str:
    """
    This function fetches the current weather data for a given city.
    """
    url = f'https://api.weatherstack.com/current?access_key=f07d9636974c4120025fadf60678771b&query={city}'

    response = requests.get(url)

    return response.json()


# Groq LLM
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)


# Create agent using the new API
agent = create_agent(
    model=llm,
    tools=[search_tool, get_weather_data]
)


# Invoke
response = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": "What is the current temp of gurgaon"
        }
    ]
})

print(response)