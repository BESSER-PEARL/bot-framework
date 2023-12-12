import base64
import inspect
import json
import logging
import os
import plotly
import subprocess
import threading
from typing import TYPE_CHECKING

from pandas import DataFrame
from websockets.exceptions import ConnectionClosedError
from websockets.sync.server import ServerConnection, WebSocketServer, serve

from besser.bot.core.session import Session
from besser.bot.exceptions.exceptions import PlatformMismatchError
from besser.bot.platforms import websocket
from besser.bot.platforms.payload import Payload, PayloadAction, PayloadEncoder
from besser.bot.platforms.platform import Platform
from besser.bot.platforms.websocket import streamlit_ui
from besser.bot.core.file import File

if TYPE_CHECKING:
    from besser.bot.core.bot import Bot


class WebSocketPlatform(Platform):
    """The WebSocket Platform allows a bot to communicate with the users using the
    `WebSocket <https://en.wikipedia.org/wiki/WebSocket>`_ bidirectional communications protocol.

    This platform implements the WebSocket server, and it can establish connection with a client, allowing the
    bidirectional communication between server and client (i.e. sending and receiving messages).

    Note:
        We provide a UI (:doc:`streamlit_ui`) implementing a WebSocket client to communicate with the bot, though you
        can use or create your own UI as long as it has a WebSocket client that connects to the bot's WebSocket server.

    Args:
        bot (Bot): the bot the platform belongs to
        use_ui (bool): weather to use the built-in UI or not

    Attributes:
        _bot (Bot): The bot the platform belongs to
        _host (str): The WebSocket host address (e.g. `localhost`)
        _port (int): The WebSocket port (e.g. `8765`)
        _use_ui (bool): Weather to use the built-in UI or not
        _connections (dict[str, ServerConnection]): The list of active connections (i.e. users connected to the bot)
        _websocket_server (WebSocketServer or None): The WebSocket server instance
        _message_handler (Callable[[ServerConnection], None]): The function that handles the user connections
            (sessions) and incoming messages
    """

    def __init__(self, bot: 'Bot', use_ui: bool = True):
        super().__init__()
        self._bot: 'Bot' = bot
        self._host: str = None
        self._port: int = None
        self._use_ui: bool = use_ui
        self._connections: dict[str, ServerConnection] = {}
        self._websocket_server: WebSocketServer = None

        def message_handler(conn: ServerConnection) -> None:
            """This method is run on each user connection to handle incoming messages and the bot sessions.

            Args:
                conn (ServerConnection): the user connection
            """
            self._connections[str(conn.id)] = conn
            session = self._bot.new_session(str(conn.id), self)
            try:
                for payload_str in conn:
                    if not self.running:
                        raise ConnectionClosedError(None, None)
                    payload: Payload = Payload.decode(payload_str)
                    if payload.action == PayloadAction.USER_MESSAGE.value:
                        self._bot.receive_message(session.id, payload.message)
                    elif payload.action == PayloadAction.USER_VOICE.value:
                        # Decode the base64 string to get audio bytes
                        audio_bytes = base64.b64decode(payload.message.encode('utf-8'))
                        message = self._bot.nlp_engine.speech2text(audio_bytes)
                        self._bot.receive_message(session.id, message)
                    elif payload.action == PayloadAction.USER_FILE.value:
                        self._bot.receive_file(session.id, File.decode(payload.message))
                    elif payload.action == PayloadAction.RESET.value:
                        self._bot.reset(session.id)
            except ConnectionClosedError:
                logging.error(f'The client closed unexpectedly')
            except Exception as e:
                logging.error("Server Error:", e)
            finally:
                logging.info(f'Session finished')
                self._bot.delete_session(session.id)
        self._message_handler = message_handler

    def initialize(self) -> None:
        self._host = self._bot.get_property(websocket.WEBSOCKET_HOST)
        self._port = self._bot.get_property(websocket.WEBSOCKET_PORT)
        self._websocket_server = serve(
            handler=self._message_handler,
            host=self._host,
            port=self._port,
            max_size=self._bot.get_property(websocket.WEBSOCKET_MAX_SIZE)
        )

    def start(self) -> None:
        if self._use_ui:
            def run_streamlit() -> None:
                """Run the Streamlit UI in a dedicated thread."""
                subprocess.run(["streamlit", "run", os.path.abspath(inspect.getfile(streamlit_ui)),
                                "--server.address", self._bot.get_property(websocket.STREAMLIT_HOST),
                                "--server.port", str(self._bot.get_property(websocket.STREAMLIT_PORT))])

            thread = threading.Thread(target=run_streamlit)
            logging.info(f'Running Streamlit UI in another thread')
            thread.start()
            #
            self._use_ui = False
        logging.info(f'{self._bot.name}\'s WebSocketPlatform starting at ws://{self._host}:{self._port}')
        self.running = True
        self._websocket_server.serve_forever()

    def stop(self):
        self._websocket_server.shutdown()
        self.running = False
        logging.info(f'{self._bot.name}\'s WebSocketPlatform stopped')

    def _send(self, session_id, payload: Payload) -> None:
        conn = self._connections[session_id]
        conn.send(json.dumps(payload, cls=PayloadEncoder))

    def reply(self, session: Session, message: str) -> None:
        if session.platform is not self:
            raise PlatformMismatchError(self, session)
        session.chat_history.append((message, 0))
        payload = Payload(action=PayloadAction.BOT_REPLY_STR,
                          message=message)
        self._send(session.id, payload)
        
    def reply_file(self, session: Session, file: File) -> None:
        """Send a file reply to a specific user

        Args:
            session (Session): the user session
            file (File): the file to send
        """
        session.chat_history.append((file.get_json_string(), 0))
        payload = Payload(action=PayloadAction.BOT_REPLY_FILE,
                          message=file.to_dict())
        self._send(session.id, payload)

    def reply_dataframe(self, session: Session, df: DataFrame) -> None:
        """Send a DataFrame bot reply, i.e. a table, to a specific user.

        Args:
            session (Session): the user session
            df (pandas.DataFrame): the message to send to the user
        """
        message = df.to_json()
        session.chat_history.append((message, 0))
        payload = Payload(action=PayloadAction.BOT_REPLY_DF,
                          message=message)
        self._send(session.id, payload)

    def reply_options(self, session: Session, options: list[str]):
        """Send a list of options as a reply. They can be used to let the user choose one of them

        Args:
            session (Session): the user session
            options (list[str]): the list of options to send to the user
        """
        d = {}
        for i, button in enumerate(options):
            d[i] = button
        message = json.dumps(d)
        session.chat_history.append((message, 0))
        payload = Payload(action=PayloadAction.BOT_REPLY_OPTIONS,
                          message=message)
        self._send(session.id, payload)

    def reply_plotly(self, session: Session, plot: plotly.graph_objs.Figure) -> None:
        """Send a Plotly figure as a bot reply, to a specific user.

        Args:
            session (Session): the user session
            plot (plotly.graph_objs.Figure): the message to send to the user
        """
        message = plotly.io.to_json(plot)
        session.chat_history.append((message, 0))
        payload = Payload(action=PayloadAction.BOT_REPLY_PLOTLY,
                          message=message)
        self._send(session.id, payload)
