def stream_data(text):
    import time

    for word in text.split(" "):
        yield word + " "
        time.sleep(0.02)

def try_multiple():
    import streamlit as st
    from openai import OpenAI

    last_exception = None

    # Define a helper to validate the client
    def validate_client(api_key):
        if not api_key or api_key.strip() == "":
            raise ValueError("API key is empty or None")

        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )

        # Try a very lightweight call to verify the key works
        try:
            client.models.list()  # simple request to check validity
            return client
        except Exception as e:
            raise ValueError(f"Invalid API key: {e}")

    # Try user key first
    try:
        api_key = st.session_state.get("user_api_key")
        client = validate_client(api_key)
        return client
    except Exception as e:
        last_exception = f"User API key failed: {e}"

    # Then try fallback keys
    for idx in range(1, 4):
        try:
            api_key = st.secrets[f"api_key_{idx}"]
            client = validate_client(api_key)
            return client
        except Exception as e:
            last_exception = f"Secret key {idx} failed: {e}"

    # If all failed
    st.error(f"Error initializing OpenAI client: {last_exception}")
    return None


def talk_to_ai(context, scenario_number, model_name):
    import streamlit as st

    client = try_multiple()

    # Clear message history and reinitialize with the new scenario's initial prompt
    if st.session_state["messages"] == None:
        st.session_state["messages"] = [{"role": "system", "content": context}]
        st.session_state["active_scenario"] = scenario_number

    # Display chat history using st.chat_message
    for message in st.session_state["messages"]:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        elif message["role"] == "assistant":
            with st.chat_message("assistant"):
                st.write(message["content"])
                #st.write_stream(stream_data(message["content"]))

    # Use st.chat_input for user input
    user_input = st.chat_input("Type your message here...")

    if user_input:
        # Add user message to chat history
        st.session_state["messages"].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        # Call OpenAI API
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=st.session_state["messages"],
                extra_body={
                    "reasoning": {
                        "effort": "low"
                    }
                },
            )

            reasoning = getattr(response.choices[0].message, "reasoning", None)
            output = response.choices[0].message.content

            ai_response = f"``` \n {reasoning} \n ``` \n {output}"

            # Add AI response and reasoning to chat history
            st.session_state["messages"].append({"role": "assistant", "content": ai_response})

            with st.chat_message("assistant"):
                st.write_stream(stream_data(ai_response))
            
            st.rerun()
        except Exception as e:
            st.error(f"Error communicating with the AI: {e}")
