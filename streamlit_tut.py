import datetime
import streamlit as st
from crewai import Crew, Task

from agents.query_parser_agent import query_parser_agent
from agents.flight_search_agent import flight_search_agent
from agents.summarization_agent import summarization_agent

from tools.kayak_tool import generate_kayak_url_tool
from tools.browser_tool import search_flights


# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="FlightFinder Pro",
    layout="wide",
)


# -------------------------------------------------
# LIGHT UI POLISH (NO COLOR OVERRIDES)
# -------------------------------------------------
st.markdown("""
<style>

/* Main container spacing */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Cards */
.card {
    background: white;
    padding: 28px;
    border-radius: 999px; /* overridden below for content */
    margin-bottom: 24px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.08);
}

/* Rectangular cards */
.card-rect {
    border-radius: 20px;
}

/* Headings */
h1, h2, h3 {
    font-weight: 600;
}

/* Buttons */
.stButton button {
    padding: 0.6rem 1.6rem;
    font-weight: 500;
    border-radius: 999px;
}

/* Inputs */
.stTextInput input {
    border-radius: 999px !important;
    padding-left: 14px;
}

</style>
""", unsafe_allow_html=True)


# -------------------------------------------------
# SIDEBAR
with st.sidebar:
    st.markdown("### 🧰 Tech Stack")

    st.markdown("""
    **🧠 AI & Agents**
    - CrewAI (Multi-Agent Framework)
    - Ollama (DeepSeek – Local LLM)

    **🛠 Tools**
    - Kayak URL Generator
    - Flight Search Browser Tool


    """)




# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.markdown("""
<div class="card card-rect">
    <h1>✈️ FlightFinder Pro</h1>
    <p>AI-powered flight search using CrewAI</p>
</div>
""", unsafe_allow_html=True)



user_query = st.text_input(
    "Flight Query",
    placeholder="Los Angeles to Boston on 22 January 2026"
)

search_clicked = st.button("Search Flights")


# -------------------------------------------------
# AI FLOW
# -------------------------------------------------
if search_clicked and user_query:

    with st.spinner("Finding best flight options..."):

        parse_task = Task(
            description=f"Parse this query: {user_query}",
            expected_output="origin, destination, date",
            agent=query_parser_agent,
        )

        generate_url_task = Task(
            description="Generate a Kayak URL for the flight search",
            expected_output="url",
            agent=flight_search_agent,
            tools=[generate_kayak_url_tool],
            input_variables=lambda output: {
                "origin": output["origin"],
                "destination": output["destination"],
                "date": output["date"],
            },
        )

        search_task = Task(
            description="Search flights on Kayak using the URL",
            expected_output="5 flight options with airline, price, duration, stops",
            agent=flight_search_agent,
            tools=[search_flights],
            input_variables=lambda output: {
                "url": f"{output['url']}?uid={datetime.datetime.now().timestamp()}"
            },
        )

        summary_task = Task(
            description="Summarize the flight options clearly",
            expected_output="Concise comparison of flights",
            agent=summarization_agent,
        )

        crew = Crew(
            agents=[
                query_parser_agent,
                flight_search_agent,
                summarization_agent,
            ],
            tasks=[
                parse_task,
                generate_url_task,
                search_task,
                summary_task,
            ],
            verbose=True,
        )

        result = crew.kickoff()

    st.markdown("""
    <div class="card card-rect">
        <h3>Best Flight Options</h3>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        f"<div class='card card-rect'>{result}</div>",
        unsafe_allow_html=True
    )


# -------------------------------------------------


