"""Definition of the agent properties within the ``gitlab_platform`` section:"""

from besser.agent.core.property import Property

SECTION_GITLAB = 'gitlab_platform'

GITLAB_PERSONAL_TOKEN = Property(SECTION_GITLAB, 'gitlab.personal_token', str, "")
"""
The Personal Access Token used to connect to the GitLab API

type: ``str``

default value: ``None``
"""

GITLAB_WEBHOOK_TOKEN = Property(SECTION_GITLAB, 'gitlab.webhook_token', str, "")
"""
The secret token defined at the webhook creation

type: ``str``

default value: ``None``
"""

GITLAB_PORT = Property(SECTION_GITLAB, 'webhooks.port', int, 8901)
"""
The server local port. This port should be exposed of proxied to make it visible by GitLab

type: ``int``

default value: ``8901``
"""