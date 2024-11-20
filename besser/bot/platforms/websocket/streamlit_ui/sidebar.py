import base64
import json
import queue
import threading
from datetime import datetime

import streamlit as st
from streamlit.runtime.scriptrunner_utils.script_run_context import add_script_run_ctx

from besser.bot.core.file import File
from besser.bot.core.message import MessageType, Message
from besser.bot.platforms.payload import PayloadEncoder, PayloadAction, Payload
from besser.bot.platforms.websocket.streamlit_ui.vars import WEBSOCKET, HISTORY, QUEUE, SUBMIT_AUDIO, SUBMIT_FILE, IMG, \
    VIDEO_INPUT_ENABLED, VIDEO_INPUT, VIDEO_INPUT_INTERVAL
from besser.bot.platforms.websocket.streamlit_ui.video_input import video_input


def sidebar():
    ws = st.session_state[WEBSOCKET]

    with st.sidebar:
        st.session_state[VIDEO_INPUT_ENABLED] = st.toggle(label='Enable video input')
        if st.session_state[VIDEO_INPUT_ENABLED]:
            st.session_state[VIDEO_INPUT_INTERVAL] = st.number_input(label='Video input interval', min_value=0.01, max_value=60.0, step=0.01, value=0.2)
            if VIDEO_INPUT not in st.session_state:
                video_input_thread = threading.Thread(target=video_input)
                add_script_run_ctx(video_input_thread)
                video_input_thread.start()
                st.session_state[VIDEO_INPUT] = video_input_thread

        if IMG in st.session_state:
            st.subheader('Video Input')
            st.image(st.session_state[IMG], channels='BGR')

        if reset_button := st.button(label="Reset bot"):
            st.session_state[HISTORY] = []
            st.session_state[QUEUE] = queue.Queue()
            payload = Payload(action=PayloadAction.RESET)
            ws.send(json.dumps(payload, cls=PayloadEncoder))

        def submit_audio():
            # Necessary callback due to buf after 1.27.0 (https://github.com/streamlit/streamlit/issues/7629)
            # It was fixed for rerun but with _handle_rerun_script_request it doesn't work
            st.session_state[SUBMIT_AUDIO] = True

        voice_bytes_io = st.audio_input(label='Say something', on_change=submit_audio)
        if st.session_state[SUBMIT_AUDIO]:
            st.session_state[SUBMIT_AUDIO] = False
            voice_bytes = voice_bytes_io.read()
            # Encode the audio bytes to a base64 string
            voice_message = Message(t=MessageType.AUDIO, content=voice_bytes, is_user=True, timestamp=datetime.now())
            st.session_state.history.append(voice_message)
            voice_base64 = base64.b64encode(voice_bytes).decode('utf-8')
            payload = Payload(action=PayloadAction.USER_VOICE, message=voice_base64)
            try:
                ws.send(json.dumps(payload, cls=PayloadEncoder))
            except Exception as e:
                st.error('Your message could not be sent. The connection is already closed')

        def submit_file():
            # Necessary callback due to buf after 1.27.0 (https://github.com/streamlit/streamlit/issues/7629)
            # It was fixed for rerun but with _handle_rerun_script_request it doesn't work
            st.session_state[SUBMIT_FILE] = True

        uploaded_file = st.file_uploader("Choose a file", accept_multiple_files=False, on_change=submit_file)
        if st.session_state[SUBMIT_FILE]:
            st.session_state[SUBMIT_FILE] = False
            bytes_data = uploaded_file.read()
            file_object = File(file_base64=base64.b64encode(bytes_data).decode('utf-8'), file_name=uploaded_file.name,
                               file_type=uploaded_file.type)
            payload = Payload(action=PayloadAction.USER_FILE, message=file_object.get_json_string())
            file_message = Message(t=MessageType.FILE, content=file_object.to_dict(), is_user=True,
                                   timestamp=datetime.now())
            st.session_state.history.append(file_message)
            try:
                ws.send(json.dumps(payload, cls=PayloadEncoder))
            except Exception as e:
                st.error('Your message could not be sent. The connection is already closed')