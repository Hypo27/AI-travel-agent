import streamlit as st
import os  # NEW: Needed to fix the error
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool

st.set_page_config(page_title="AI Travel Agent", page_icon="✈️")

st.title("✈️ AI Travel Planning Agent")

with st.sidebar:
    st.header("🔑 API Keys")
    google_api_key = st.text_input("Google API Key", type="password")
    tavily_api_key = st.text_input("Tavily API Key", type="password")

def budget_calculator(query):
    try:
        return str(eval(query))
    except:
        return "Error in calculation"

if google_api_key and tavily_api_key:
    # --- THE FIX STARTS HERE ---
    os.environ["TAVILY_API_KEY"] = tavily_api_key
    search_tool = TavilySearchResults()
    # --- THE FIX ENDS HERE ---
    
    calc_tool = Tool(
        name="Calculator",
        func=budget_calculator,
        description="Calculates math."
    )

    tools = [search_tool, calc_tool]

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro", 
        google_api_key=google_api_key
    )

    agent = initialize_agent(
        tools, 
        llm, 
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, 
        verbose=True,
        handle_parsing_errors=True
    )

    destination = st.text_input("Where to?", "Tokyo")
    interest = st.text_input("Interests?", "Food")

    if st.button("Plan Trip"):
        with st.spinner("Planning..."):
            try:
                response = agent.run(f"Plan a trip to {destination} focusing on {interest}. Use search to find hotels and calculator to estimate cost.")
                st.write(response)
            except Exception as e:
                st.error(f"Error: {e}")
else:
    st.warning("Enter keys in the sidebar!")