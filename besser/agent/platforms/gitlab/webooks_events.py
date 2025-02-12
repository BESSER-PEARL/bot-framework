class GitlabEvent:

    def __init__(self, name, action, payload):
        self._name: str = name
        self._action: str = action
        self._payload: str = payload

    @property
    def name(self):
        """str: The name of the event"""
        return self._name

    @property
    def action(self):
        """str: The action of the event"""
        return self._action

    @property
    def payload(self):
        """str: The payload of the event"""
        return self._payload


class IssuesClosed(GitlabEvent):
    def __init__(self, payload=None):
        super().__init__('Issue Hook', 'close', payload)

class IssuesUpdated(GitlabEvent):
    def __init__(self, payload=None):
        super().__init__('Issue Hook', 'update', payload)

class IssuesOpened(GitlabEvent):
    def __init__(self, payload=None):
        super().__init__('Issue Hook', 'open', payload)

class IssuesReopened(GitlabEvent):
    def __init__(self, payload=None):
        super().__init__('Issue Hook', 'reopen', payload)

class IssueCommentCreated(GitlabEvent):
    def __init__(self, payload=None):
        super().__init__('IssueNote Hook', 'create', payload)

class IssueCommentUpdated(GitlabEvent):
    def __init__(self, payload=None):
        super().__init__('IssueNote Hook', 'update', payload)

class MergeRequestClosed(GitlabEvent):
    def __init__(self, payload=None):
        super().__init__('Merge Request Hook', 'close', payload)

class MergeRequestUpdated(GitlabEvent):
    def __init__(self, payload=None):
        super().__init__('Merge Request Hook', 'update', payload)

class MergeRequestOpened(GitlabEvent):
    def __init__(self, payload=None):
        super().__init__('Merge Request Hook', 'open', payload)

class MergeRequestReopened(GitlabEvent):
    def __init__(self, payload=None):
        super().__init__('Merge Request Hook', 'reopen', payload)

class MergeRequestApproved(GitlabEvent):
    def __init__(self, payload=None):
        super().__init__('Merge Request Hook', 'approved', payload)

class MergeRequestUnapproved(GitlabEvent):
    def __init__(self, payload=None):
        super().__init__('Merge Request Hook', 'unapproved', payload)

class MergeRequestApproval(GitlabEvent):
    def __init__(self, payload=None):
        super().__init__('Merge Request Hook', 'approval', payload)

class MergeRequestUnapproval(GitlabEvent):
    def __init__(self, payload=None):
        super().__init__('Merge Request Hook', 'unapproval', payload)

class MergeRequestMerge(GitlabEvent):
    def __init__(self, payload=None):
        super().__init__('Merge Request Hook', 'merge', payload)

class MergeRequestCommentCreated(GitlabEvent):
    def __init__(self, payload=None):
        super().__init__('MergeRequestNote Hook', 'create', payload)

class MergeRequestCommentUpdated(GitlabEvent):
    def __init__(self, payload=None):
        super().__init__('MergeRequestNote Hook', 'update', payload)

class WikiPageCreated(GitlabEvent):
    def __init__(self, payload=None):
        super().__init__('Wiki Page Hook', 'create', payload)

class WikiPageUpdated(GitlabEvent):
    def __init__(self, payload=None):
        super().__init__('Wiki Page Hook', 'update', payload)

class WikiPageDeleted(GitlabEvent):
    def __init__(self, payload=None):
        super().__init__('Wiki Page Hook', 'delete', payload)

class Push(GitlabEvent):
    def __init__(self, payload=None):
        super().__init__('Push Hook', '', payload)
