"""
agent.py
Builds and returns the LangChain SQL Agent powered by Groq (Llama 3).
"""

from langchain_groq import ChatGroq
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain.agents import AgentType, create_sql_agent


def get_llm(api_key: str, model: str = "llama-3.1-8b-instant", temperature: float = 0):
    """
    Initialise the Groq LLM.
    Temperature 0 keeps SQL generation deterministic.
    """
    llm = ChatGroq(
        groq_api_key=api_key,
        model_name=model,
        temperature=temperature,
        streaming=True,
    )
    return llm


def get_agent(db: SQLDatabase, api_key: str, model: str = "llama-3.1-8b-instant"):
    """
    Build a LangChain SQL Agent.
    - Uses SQLDatabaseToolkit to expose list/describe/query tools.
    - AgentType.ZERO_SHOT_REACT_DESCRIPTION is stable and works well for SQL tasks.
    - verbose=True lets StreamlitCallbackHandler capture thought steps.
    """
    llm = get_llm(api_key=api_key, model=model)
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    agent = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=10,
    )
    return agent