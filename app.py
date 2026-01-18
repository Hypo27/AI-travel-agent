import streamlit as st
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool

st.set_page_config(page_title="AI Travel Agent", page_icon="🌎", layout="wide")

st.title("🌎 AI Travel Planning Agent")

with st.sidebar:
    st.header("🔑 API Keys")
    google_api_key = st.text_input("Google API Key", type="password")
    tavily_api_key = st.text_input("Tavily API Key", type="password")
    
    st.divider()
    st.header("⚙️ Trip Settings")
    days = st.slider("Trip Duration (Days)", 1, 14, 5)
    budget_style = st.select_slider("Budget Style", options=["Backpacker", "Moderate", "Luxury"])

def budget_calculator(query):
    try:
        return str(eval(query))
    except:
        return "Error in calculation"

if google_api_key and tavily_api_key:
    os.environ["TAVILY_API_KEY"] = tavily_api_key
    
    search_tool = TavilySearchResults()
    calc_tool = Tool(
        name="Calculator",
        func=budget_calculator,
        description="Useful for calculating total travel budgets."
    )
    tools = [search_tool, calc_tool]

    # --- THIS LINE IS THE FIX ---
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=google_api_key)
    
    agent = initialize_agent(
        tools, 
        llm, 
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, 
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=3,
        early_stopping_method="generate"
    )

    col1, col2 = st.columns(2)
    with col1:
        destination = st.text_input("Where do you want to go?", "Tokyo, Japan")
    with col2:
        interests = st.text_input("Primary Interests?", "Food, History, Anime")

    if st.button("🚀 Generate Itinerary"):
        with st.spinner(f"Planning a {days}-day {budget_style} trip to {destination}..."):
            try:
                prompt = (
                    f"Plan a {days}-day trip to {destination} for a traveler with a '{budget_style}' budget. "
                    f"Interests: {interests}. "
                    "1. Search for 3 hotels and flight costs. "
                    "2. Create a daily itinerary. "
                    "3. Calculate total cost. "
                    "STOP searching after you have basic info."
                )
                response = agent.run(prompt)
                st.success("Trip Planned Successfully!")
                st.markdown(response)
            except Exception as e:
                st.error(f"An error occurred: {e}")
else:
    st.warning("👈 Please enter your API Keys in the sidebar to start!")
