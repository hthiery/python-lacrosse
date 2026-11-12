import os
import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

POLICY = Path(__file__).resolve().parents[1] / ".github/scripts/release-policy.sh"
PolicyRunner = Callable[..., subprocess.CompletedProcess[str]]


def git(repository: Path, *arguments: str) -> str:
    return subprocess.run(
        [
            "git",
            "-C",
            str(repository),
            "-c",
            "user.name=Release Test",
            "-c",
            "user.email=release-test@example.invalid",
            "-c",
            "commit.gpgsign=false",
            "-c",
            "tag.gpgsign=false",
            *arguments,
        ],
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"},
    ).stdout.strip()


@pytest.fixture
def release_repository(tmp_path: Path) -> Path:
    origin = tmp_path / "origin"
    origin.mkdir()
    git(origin, "init", "--initial-branch=main")
    git(origin, "commit", "--allow-empty", "-m", "Initial release commit")
    repository = tmp_path / "checkout"
    git(tmp_path, "clone", "--no-hardlinks", str(origin), str(repository))
    return repository


@pytest.fixture
def run_policy(release_repository: Path, tmp_path: Path) -> PolicyRunner:
    def run(**changes: str) -> subprocess.CompletedProcess[str]:
        environment = {
            **os.environ,
            "GITHUB_EVENT_NAME": "push",
            "GITHUB_REPOSITORY": "vipwolf/python-lacrosse",
            "GITHUB_REF_TYPE": "branch",
            "GITHUB_REF_NAME": "develop",
            "GITHUB_SHA": git(release_repository, "rev-parse", "HEAD"),
            "GITHUB_RUN_ID": "123",
            "GITHUB_RUN_ATTEMPT": "2",
            "GITHUB_OUTPUT": str(tmp_path / "output"),
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_NOSYSTEM": "1",
            **changes,
        }
        return subprocess.run(
            ["bash", str(POLICY)],
            cwd=release_repository,
            env=environment,
            capture_output=True,
            text=True,
        )

    return run


@pytest.mark.parametrize("branch", ["main", "develop"])
def test_branch_versions_are_public_and_unique(
    run_policy: PolicyRunner, tmp_path: Path, branch: str
) -> None:
    result = run_policy(GITHUB_REF_NAME=branch)
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "output").read_text() == "version=0.0.123.dev2\n"
    result = run_policy(GITHUB_REF_NAME=branch, GITHUB_RUN_ATTEMPT="3")
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "output").read_text().endswith("version=0.0.123.dev3\n")


@pytest.mark.parametrize(
    "changes",
    [
        {"GITHUB_EVENT_NAME": "pull_request"},
        {"GITHUB_EVENT_NAME": "pull_request_target"},
        {"GITHUB_EVENT_NAME": "workflow_run"},
        {"GITHUB_EVENT_NAME": "workflow_dispatch"},
        {"GITHUB_REPOSITORY": "attacker/python-lacrosse"},
        {"GITHUB_REF_NAME": "master"},
        {"GITHUB_REF_NAME": "feature"},
        {"GITHUB_REF_NAME": "main$(touch INJECTED)"},
        {"GITHUB_SHA": "0" * 40},
        {"GITHUB_RUN_ID": "0"},
        {"GITHUB_RUN_ATTEMPT": "invalid"},
    ],
)
def test_disallowed_contexts_fail_closed(
    run_policy: PolicyRunner, release_repository: Path, changes: dict[str, str]
) -> None:
    assert run_policy(**changes).returncode != 0
    assert not (release_repository / "INJECTED").exists()


@pytest.mark.parametrize("annotated", [False, True])
def test_release_tags_on_main_are_accepted(
    release_repository: Path,
    run_policy: PolicyRunner,
    tmp_path: Path,
    annotated: bool,
) -> None:
    arguments = ["tag", "1.2.3"]
    if annotated:
        arguments.extend(["--annotate", "--message", "Release 1.2.3"])
    git(release_repository, *arguments)
    result = run_policy(GITHUB_REF_TYPE="tag", GITHUB_REF_NAME="1.2.3")
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "output").read_text() == "version=1.2.3\n"


@pytest.mark.parametrize("tag", ["v1.2.3", "1.2.3rc1", "01.2.3", "1.2", "1.2.3.4"])
def test_noncanonical_tags_are_rejected(run_policy: PolicyRunner, tag: str) -> None:
    assert run_policy(GITHUB_REF_TYPE="tag", GITHUB_REF_NAME=tag).returncode != 0


def test_release_commit_must_be_on_main(
    release_repository: Path, run_policy: PolicyRunner
) -> None:
    git(release_repository, "checkout", "-b", "develop")
    git(release_repository, "commit", "--allow-empty", "-m", "Unmerged change")
    git(release_repository, "tag", "1.2.3")
    result = run_policy(GITHUB_REF_TYPE="tag", GITHUB_REF_NAME="1.2.3")
    assert result.returncode != 0
    assert "not in main history" in result.stderr


def test_missing_main_fails_closed(
    release_repository: Path, run_policy: PolicyRunner
) -> None:
    git(release_repository, "tag", "1.2.3")
    git(
        release_repository, "remote", "set-url", "origin", "/nonexistent-release-origin"
    )
    assert run_policy(GITHUB_REF_TYPE="tag", GITHUB_REF_NAME="1.2.3").returncode != 0


def test_tag_must_point_at_triggering_commit(
    release_repository: Path, run_policy: PolicyRunner
) -> None:
    git(release_repository, "tag", "1.2.3")
    git(release_repository, "commit", "--allow-empty", "-m", "Different commit")
    assert run_policy(GITHUB_REF_TYPE="tag", GITHUB_REF_NAME="1.2.3").returncode != 0


def test_modified_checkout_is_rejected(
    release_repository: Path, run_policy: PolicyRunner
) -> None:
    tracked = release_repository / "tracked"
    tracked.write_text("original\n")
    git(release_repository, "add", "tracked")
    git(release_repository, "commit", "-m", "Track a file")
    tracked.write_text("modified\n")
    assert run_policy().returncode != 0
