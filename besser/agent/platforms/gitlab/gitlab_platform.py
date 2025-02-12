from __future__ import annotations

import asyncio
import json
import threading
from asyncio import AbstractEventLoop
from datetime import datetime
from typing import TYPE_CHECKING

from aiohttp import web, ClientSession
from gidgetlab import routing, sansio
from gidgetlab.aiohttp import GitLabAPI

from besser.agent.core.message import Message, MessageType
from besser.agent.core.session import Session
from besser.agent.exceptions.exceptions import PlatformMismatchError
from besser.agent.exceptions.logger import logger
from besser.agent.platforms import gitlab
from besser.agent.platforms.gitlab.actions import *
from besser.agent.platforms.gitlab.gitlab_objects import Issue
from besser.agent.platforms.gitlab.webooks_events import GitlabEvent
from besser.agent.platforms.payload import Payload, PayloadAction, PayloadEncoder
from besser.agent.platforms.platform import Platform

if TYPE_CHECKING:
    from besser.agent.core.agent import Agent


def sync_coro_call(coro):
    def start_event_loop(coro, returnee):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        returnee['result'] = loop.run_until_complete(coro)

    returnee = {'result': None}
    thread = threading.Thread(target=start_event_loop, args=[coro, returnee])
    thread.start()
    thread.join()
    return returnee['result']


class GitLabPlatform(Platform):
    """The GitLab Platform allows an agent to receive events from GitLab webhooks and make calls to its REST API

    This platform implements a webserver exposing an endpoint to receive webhooks events from GitLab.
    In addition, the platform provides abstractions for interacting with issues (e.g., open, get, comment).

    Args:
        agent (Agent): the agent the platform belongs to

    Attributes:
        _agent (Agent): The agent the platform belongs to
        _secret (str): The secret webhook token
        _oauth_token (str): Personal token for GitLab API requests
        _agent_name (str): Name of the agent
        _port (int): Port of the webhook endpoint
        _app (web.Application): Web application routing webhooks to our entrypoint
        _session (Session): The session of the GitLabPlatform
        _post_entrypoint (Request -> web.Response): The method handling the webhooks events
    """

    def __init__(self, agent: 'Agent'):
        super().__init__()
        self._agent: 'Agent' = agent
        self._secret: str = self._agent.get_property(gitlab.GITLAB_WEBHOOK_TOKEN)
        self._oauth_token: str = self._agent.get_property(gitlab.GITLAB_PERSONAL_TOKEN)
        self._agent_name: str = self._agent.name
        self._port: int = self._agent.get_property(gitlab.GITLAB_PORT)
        self._event_loop: AbstractEventLoop = None
        self._router = routing.Router()
        self._app = web.Application()
        self._session: Session = None

        async def post_entrypoint(request) -> None:
            body = await request.read()

            event = sansio.Event.from_http(request.headers, body, secret=self._secret)
            if event.event == "Note Hook":
                agent.receive_event(
                    GitlabEvent(event.data['object_attributes']['noteable_type'] + event.event,
                                event.data['object_attributes']['action'] or '', event.data))
            else:
                agent.receive_event(
                    GitlabEvent(event.event, event.data['object_attributes']['action'] or '', event.data))
            return web.Response(status=200)

        self._post_entrypoint = post_entrypoint

    def initialize(self) -> None:
        self._app.router.add_post("/", self._post_entrypoint)
        if self._port is not None:
            self._port = int(self._port)

        self._event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._event_loop)

    def start(self) -> None:
        logger.info(f'{self._agent.name}\'s GitLabPlatform starting')
        self._agent.get_or_create_session("GitLab_Session_" + str(self._event_loop.__hash__()), self)
        self.running = True
        web.run_app(self._app, port=self._port)

    def stop(self):
        self.running = False
        logger.info(f'{self._agent.name}\'s GitLabPlatform stopped')

    def __getattr__(self, name: str):
        """All methods in :class:`aiohttp.GitLabAPI` can be used from the GitLabPlatform.

        Args:
            name (str): the name of the function to call
        """

        async def api_call(*args, **kwargs):
            async with ClientSession() as session:
                gl_api = GitLabAPI(session, self._agent_name, access_token=self._oauth_token)
                # Forward the method call to the gitlab api
                method = getattr(gl_api, name, None)
                if method:
                    return await method(*args, **kwargs)
                else:
                    raise AttributeError(f"'{gl_api.__class__}' object has no attribute '{name}'")

        def method_proxy(*args, **kwargs):
            return sync_coro_call(api_call(*args, **kwargs))

        return method_proxy

    def _send(self, session_id, payload: Payload) -> None:
        session = self._agent.get_or_create_session(session_id=session_id, platform=self)
        payload.message = self._agent.process(session=session, message=payload.message, is_user_message=False)
        if session_id in self._connections:
            conn = self._connections[session_id]
            conn.send(json.dumps(payload, cls=PayloadEncoder))

    def reply(self, session: Session, message: str) -> None:
        if session.platform is not self:
            raise PlatformMismatchError(self, session)
        session.save_message(Message(t=MessageType.STR, content=message, is_user=False, timestamp=datetime.now()))
        payload = Payload(action=PayloadAction.AGENT_REPLY_STR,
                          message=message)
        self._send(session.id, payload)

    def open_issue(self, user: str, repository: str, title: str, body: str) -> Issue:
        return Issue(sync_coro_call(open_issue(self._agent_name, self._oauth_token, user, repository, title, body)))

    def get_issue(self, user: str, repository: str, issue_number: int) -> Issue:
        return Issue(sync_coro_call(get_issue(self._agent_name, self._oauth_token, user, repository, issue_number)))

    def comment_issue(self, issue: Issue, content: str):
        return sync_coro_call(comment_issue(self._agent_name, self._oauth_token, issue, content))

    def set_label(self, issue: Issue, label: str):
        return sync_coro_call(set_label(self._agent_name, self._oauth_token, issue, label))

    def assign_user(self, issue: Issue, assignee: int):
        return sync_coro_call(assign_user(self._agent_name, self._oauth_token, issue, assignee))
