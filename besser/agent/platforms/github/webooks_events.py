class GithubEvent:

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

class StarCreated(GithubEvent):
    def __init__(self,payload=None):
        super().__init__('star', 'created',payload)

class StarDeleted(GithubEvent):
    def __init__(self,payload=None):
        super().__init__('star', 'deleted',payload)

class IssuesAssigned(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('issues', 'assigned', payload)

class IssuesClosed(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('issues', 'closed', payload)

class IssuesDeleted(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('issues', 'deleted', payload)

class IssuesDemilestoned(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('issues', 'demilestoned', payload)

class IssuesEdited(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('issues', 'edited', payload)

class IssuesLabeled(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('issues', 'labeled', payload)

class IssuesLocked(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('issues', 'locked', payload)

class IssuesMilestoned(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('issues', 'milestoned', payload)

class IssuesOpened(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('issues', 'opened', payload)

class IssuesPinned(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('issues', 'pinned', payload)

class IssuesReopened(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('issues', 'reopened', payload)

class IssuesTransferred(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('issues', 'transferred', payload)

class IssuesUnassigned(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('issues', 'unassigned', payload)

class IssuesUnlabeled(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('issues', 'unlabeled', payload)

class IssuesUnlocked(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('issues', 'unlocked', payload)

class IssuesUnpinned(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('issues', 'unpinned', payload)

class IssueCommentCreated(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('issue_comment', 'created', payload)

class IssueCommentDeleted(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('issue_comment', 'deleted', payload)

class IssueCommentEdited(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('issue_comment', 'edited', payload)

class PullRequestAssigned(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('pull_request', 'assigned', payload)

class PullRequestAutoMergeDisabled(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('pull_request', 'auto_merge_disabled', payload)

class PullRequestAutoMergeEnabled(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('pull_request', 'auto_merge_enabled', payload)

class PullRequestClosed(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('pull_request', 'closed', payload)

class PullRequestConvertedToDraft(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('pull_request', 'converted_to_draft', payload)

class PullRequestDemilestoned(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('pull_request', 'demilestoned', payload)

class PullRequestDequeued(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('pull_request', 'dequeued', payload)

class PullRequestEdited(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('pull_request', 'edited', payload)

class PullRequestEnqueued(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('pull_request', 'enqueued', payload)

class PullRequestLabeled(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('pull_request', 'labeled', payload)

class PullRequestLocked(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('pull_request', 'locked', payload)

class PullRequestMilestoned(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('pull_request', 'milestoned', payload)

class PullRequestOpened(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('pull_request', 'opened', payload)

class PullRequestReadyForReview(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('pull_request', 'ready_for_review', payload)

class PullRequestReopened(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('pull_request', 'reopened', payload)

class PullRequestReviewRequestRemoved(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('pull_request', 'review_request_removed', payload)

class PullRequestReviewRequested(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('pull_request', 'review_requested', payload)

class PullRequestSynchronize(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('pull_request', 'synchronize', payload)

class PullRequestUnassigned(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('pull_request', 'unassigned', payload)

class PullRequestUnlabeled(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('pull_request', 'unlabeled', payload)

class PullRequestUnlocked(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('pull_request', 'unlocked', payload)

class PullRequestReviewCommentCreated(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('pull_request_review_comment', 'created', payload)

class PullRequestReviewCommentDeleted(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('pull_request_review_comment', 'deleted', payload)

class PullRequestReviewCommentEdited(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('pull_request_review_comment', 'edited', payload)

class WikiPageCreated(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('gollum', 'created', payload)

class WikiPageEdited(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('gollum', 'edited', payload)

class LabelCreated(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('label', 'created', payload)

class LabelDeleted(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('label', 'deleted', payload)

class LabelEdited(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('label', 'edited', payload)

class Push(GithubEvent):
    def __init__(self, payload=None):
        super().__init__('push', '', payload)
