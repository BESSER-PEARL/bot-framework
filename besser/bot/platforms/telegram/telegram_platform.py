import asyncio
import base64
import logging
from typing import TYPE_CHECKING

from telegram import Update
from telegram.ext import Application, ApplicationBuilder, BaseHandler, CommandHandler, ContextTypes, MessageHandler, \
    filters

from besser.bot.core.session import Session
from besser.bot.exceptions.exceptions import PlatformMismatchError
from besser.bot.platforms import telegram
from besser.bot.platforms.payload import Payload, PayloadAction
from besser.bot.platforms.platform import Platform

if TYPE_CHECKING:
    from besser.bot.core.bot import Bot


class TelegramPlatform(Platform):
    """The Telegram Platform allows a bot to interact via Telegram.

    It includes a `message handler` to handle all text inputs except commands (i.e. messages starting with '/')
    and a `reset handler`, triggered by the `/reset` command, to reset the bot session.

    Args:
        bot (Bot): the bot the platform belongs to

    Attributes:
        _bot (Bot): The bot the platform belongs to
        _telegram_app (Application): The Telegram Application
        _event_loop (asyncio.AbstractEventLoop): The event loop that runs the asynchronous tasks of the Telegram
            Application
    """
    def __init__(self, bot: 'Bot'):
        super().__init__()
        self._bot: 'Bot' = bot
        self._telegram_app: Application = None
        self._event_loop: asyncio.AbstractEventLoop = None
        self._handlers: list[BaseHandler] = []

        async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):
            session_id = str(update.effective_chat.id)
            session = self._bot.get_or_create_session(session_id, self)
            text = update.message.text
            self._bot.receive_message(session.id, text)

        message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), message)
        self._handlers.append(message_handler)

        # Handler for reset command
        async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
            session_id = str(update.effective_chat.id)
            self._bot.reset(session_id)

        reset_handler = CommandHandler('reset', reset)
        self._handlers.append(reset_handler)

        # Handler for voice messages
        async def voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
            session_id = str(update.effective_chat.id)
            session = self._bot.get_or_create_session(session_id, self)
            voice_file = await context.bot.get_file(update.message.voice.file_id)
            voice_data = await voice_file.download_as_bytearray()
            text = self._bot.nlp_engine.speech2text(bytes(voice_data))
            self._bot.receive_message(session.id, text)

        voice_handler = MessageHandler(filters.VOICE, voice)
        self._handlers.append(voice_handler)
        
        # Handler for voice messages
        async def file(update: Update, context: ContextTypes.DEFAULT_TYPE):
            session_id = str(update.effective_chat.id)
            session = self._bot.get_or_create_session(session_id, self)
            file_object = await context.bot.get_file(update.message.document.file_id)
            file_data = await file_object.download_as_bytearray()
            base64_data = base64.b64encode(file_data).decode()
            json_object = {
                "base64": base64_data,
                "name": update.message.document.file_name,
                "type": update.message.document.mime_type
            }
            self._bot.receive_file(session.id, json_file=json_object)

        file_handler = MessageHandler(filters.ATTACHMENT & (~filters.PHOTO), file)
        self._handlers.append(file_handler)
        
        async def image(update: Update, context: ContextTypes.DEFAULT_TYPE):
            session_id = str(update.effective_chat.id)
            session = self._bot.get_or_create_session(session_id, self)
            image_object = await context.bot.get_file(update.message.photo[-1].file_id)
            image_data = await image_object.download_as_bytearray()
            base64_data = base64.b64encode(image_data).decode()
            # im not sure if it actually is png tbh
            json_object = {
                "base64": base64_data,
                "name": update.message.photo[-1].file_id + ".jpg",
                "type": "image/jpeg"
            }
            self._bot.receive_file(session.id, json_file=json_object)

        image_handler = MessageHandler(filters.PHOTO, image)
        self._handlers.append(image_handler)

    @property
    def telegram_app(self):
        """telegram.ext._application.Application: The Telegram app."""
        return self._telegram_app

    def initialize(self) -> None: # Hide Info logging messages
        logging.getLogger("httpx").setLevel(logging.WARNING)
        self._telegram_app = ApplicationBuilder().token(
            self._bot.get_property(telegram.TELEGRAM_TOKEN)).build()
        self._telegram_app.add_handlers(self._handlers)
        self._event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._event_loop)

    def start(self) -> None:
        logging.info(f'{self._bot.name}\'s TelegramPlatform starting')
        self.running = True
        self._telegram_app.run_polling(stop_signals=None)

    def stop(self):
        self._event_loop.stop()
        self.running = False
        logging.info(f'{self._bot.name}\'s TelegramPlatform stopped')

    def _send(self, session_id: str, payload: Payload) -> None:
        loop = asyncio.get_event_loop()
        if payload.action == PayloadAction.BOT_REPLY_STR.value:
            asyncio.run_coroutine_threadsafe(self._telegram_app.bot.send_message(chat_id=session_id, text=payload.message),
                                            loop)
        elif payload.action == PayloadAction.BOT_REPLY_FILE.value:
            asyncio.run_coroutine_threadsafe(self._telegram_app.bot.send_document(chat_id=session_id, document=payload.message["data"],
                                                                        filename=payload.message["name"]), loop)

    def reply(self, session: Session, message: str) -> None:
        if session.platform is not self:
            raise PlatformMismatchError(self, session)
        session.chat_history.append((message, 0))
        payload = Payload(action=PayloadAction.BOT_REPLY_STR,
                          message=message)
        self._send(session.id, payload)
        
    def reply_file(self, session: Session, file_path: str = None, file_data: bytes = None, file_name: str = None, file_type: str = None, 
                   file_base64: dict = None) -> None:
        """A bot file message (usually a reply to a user message) is sent to the session platform to show it to the user.

        Note that at least one of file_path, file_data or file_base64 need to be set. 
        Args:
            file_path (str, optional): Path to the file.
            file_data (bytes, optional): Raw file data.
            file_info (dict, optional): JSON object containing file data, filename, and file type.
        """
        if file_path:
            with open(file_path, 'rb') as file:
                file_data = file.read()
                file_name = file_path.split('/')[-1]
                file_type = file_path.split('.')[-1]
        elif file_base64:
            file_data = base64.b64decode(file_base64)
        elif not file_data:
            raise ValueError("Invalid input parameters")
        if not file_name:
            file_name = 'default_filename'
        if not file_type:
            file_type = 'file'
        file_object = {
            'data': file_data,
            'name': file_name,
            'type': file_type
        }
        if session.platform is not self:
            raise PlatformMismatchError(self, session)
        session.chat_history.append((file_object, 0))
        payload = Payload(action=PayloadAction.BOT_REPLY_FILE,
                          message=file_object)
        self._send(session.id, payload)

    def add_handler(self, handler: BaseHandler) -> None:
        """
        Add a custom Telegram handler for the bot.

        Args:
            handler (telegram.ext.BaseHandler): the handler to add
        """
        self._handlers.append(handler)
