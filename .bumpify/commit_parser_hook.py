from typing import Optional
from bumpify.core.semver.hooks import commit_parser_hook
from bumpify.core.semver.objects import ConventionalCommit, ConventionalCommitData
from bumpify.core.vcs.objects import Commit


@commit_parser_hook
def make_conventional_commit(commit: Commit) -> Optional[ConventionalCommit]:
    conventional_commit = ConventionalCommit.from_commit(commit)
    if conventional_commit is not None:
        return conventional_commit
    subject = commit.message.split('\n')[0]
    if subject.startswith('fix'):
        return ConventionalCommit(commit=commit, data=ConventionalCommitData(type="fix", description=subject))
    if subject.startswith('add'):
        return ConventionalCommit(commit=commit, data=ConventionalCommitData(type="feat", description=subject))
    if commit.rev == "edc4cb8a5a189acabde2d676cbf8795ac58918f1":
        return ConventionalCommit(commit=commit, data=ConventionalCommitData(type="fix", description='ABCMock with no expectations set fails on assert_satisfied'))
    if commit.rev == "900b702e937967c0a7d60d3b25eae42846289139":
        return ConventionalCommit(commit=commit, data=ConventionalCommitData(type="fix", description='Fix object matcher'))
    return None
