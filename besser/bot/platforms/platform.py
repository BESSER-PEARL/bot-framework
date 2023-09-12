from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from besser.bot.platforms.payload import Payload

if TYPE_CHECKING:
    from besser.bot.core.session import Session


class Platform(ABC):
    """The platform abstract class.

    A platform defines the methods the bot can use to interact with a particular communication channel
    (e.g. Telegram, Slack...) for instance, sending and receiving messages.

    This class serves as a template to implement platforms.
    """

    @abstractmethod
    def run(self) -> None:
        """Run the platform."""
        pass

    @abstractmethod
    def _send(self, session_id: str, payload: Payload) -> None:
        """Send a payload message to a specific user.

        Args:
            session_id (str): the user to send the response to
            payload (Payload): the payload message to send to the user
        """
        pass

    @abstractmethod
    def reply(self, session: 'Session', message: str) -> None:
        """Send a bot reply, i.e. a text message, to a specific user.

        Args:
            session (Session): the user session
            message (str): the message to send to the user
        """
        pass
