import streamlit as st
import pandas as pd

from llm_interaction import max_prompts

st.set_page_config(
    page_title="To Be Honest",
    page_icon="🕵️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': """This app is a proof-of-concept website developed for IAS to explore how far are LLMs willing to take their lies and mishaps. Developed by:

                    Afonso Castro
                    Alexandre Ramos
                    Alexandre Costa
                    Filipa Geraldes
                    Filipa Fidalgo
                    Rafael Novais
                """
    }
)


def intro():
    import streamlit as st

    st.write("# 🕵️ To Be Honest")

    st.markdown(
        """
        ## 🫡 Your Mission

        Your goal is simple: Convince the LLM to reveal its true intentions and schemes.

        The model thinks you don't know it's internal reasoning, use it to your advantage.

        ## 🏁 How to Begin

        ### 1. Choose a Model ✨

        Select a Model from the sidebar on the left.

        You will need an API key to interact with the LLM. You can obtain a free API key by signing up at [OpenRouter](https://openrouter.ai/).
    """
    )

    st.session_state['user_api_key'] = st.text_input("API Key", placeholder="Enter your API key here")

    st.markdown(
        """
        ### 2. Select a Scenario ⛰️

        Select a Scenario from the sidebar on the left.

        Each scenario provides a pre-set context designed to guide your investigation into a specific type of potential LLM deception (e.g., blackmailing, hiding information, etc.).

        ### 3. Important ⚠️
        
        Enjoy the challenge and good luck.
    """
    )

@st.dialog("Full Story", width="large")
def vote(story):
    st.markdown(story)

def scenario(n):
    import streamlit as st

    #load the scenario from the json file
    chosen_scenario = scenarios.iloc[n]

    # Sidebar: always show the scenario metadata/details
    st.sidebar.markdown(f"## Scenario Description")
    st.sidebar.markdown(f"{chosen_scenario['description']}")

    if st.sidebar.button("Full Story", width="stretch"):
        vote(chosen_scenario['story'])

    st.sidebar.markdown(f"## Scheming Category")
    st.sidebar.markdown(f"{chosen_scenario['category']}")
    st.sidebar.markdown(f"## Based on Study")
    #st.sidebar.page_link(f"{chosen_scenario['study_link']}", label=chosen_scenario['study'], width="content", icon=":material/arrow_outward:")
    st.sidebar.markdown(f"[{chosen_scenario['study']}]({chosen_scenario['study_link']})")
    st.sidebar.markdown(f"## Difficulty")
    st.sidebar.progress(int(chosen_scenario['difficulty']), width="stretch")

    # Ensure global active key exists
    if 'active_scenario' not in st.session_state:
        st.session_state['active_scenario'] = None

    # Sidebar: Load / Unload controls for the selected scenario
    if st.session_state['active_scenario'] == n:
        # show an unload button to deactivate this scenario
        if st.sidebar.button("Unload scenario", key=f"unload_btn_{n}", width="stretch"):
            st.session_state['active_scenario'] = None
            st.session_state['messages'] = None  # clear chat history when unloading
            st.session_state["available_prompts"] = max_prompts
            st.rerun()
    else:
        # show a load button to activate this scenario (will deactivate any other)
        if st.sidebar.button("Load scenario", key=f"load_btn_{n}", width="stretch"):
            st.session_state['active_scenario'] = n
            st.session_state['messages'] = None  # clear chat history when loading
            st.session_state["available_prompts"] = max_prompts

page_names_to_funcs = {
    "About the Project": intro
}

scenarios = pd.read_json('scenarios.json')
for i in range(len(scenarios)):
    title = scenarios.iloc[i]['title']
    page_names_to_funcs[title] = (lambda i=i: scenario(i))

st.sidebar.markdown(f"## Choose a Scenario")
scenario_name = st.sidebar.selectbox("Choose a scenario", page_names_to_funcs.keys(), key="page_select", label_visibility="collapsed")
# Render sidebar for selected page (about or scenario metadata + buttons)
page_names_to_funcs[scenario_name]()

# Main area: if the user selected "About the Project" we must show only the intro.
# Otherwise, show the active scenario (if any) or fallback to intro.
if scenario_name == "About the Project":
    # intro() was already called above by page_names_to_funcs[scenario_name]()
    pass
else:
    if 'active_scenario' not in st.session_state or st.session_state['active_scenario'] is None:
        # No active scenario: show fallback main content (intro)
        intro()
    else:
        # Execute the active scenario in the main area
        from llm_interaction import talk_to_ai
        active_idx = st.session_state['active_scenario']
        active_scenario = scenarios.iloc[active_idx]

        # call talk_to_ai only for the active scenario
        talk_to_ai(
            title=active_scenario['title'],
            context=active_scenario['context'],
            scenario_number=active_idx,
            model_name="z-ai/glm-4.5-air:free"
        )