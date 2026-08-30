from typing import Any, cast

import pytest


class FakeConvexClient:
    """Mock Convex Client to verify multi-tenant isolation and negative access checks."""

    def __init__(self) -> None:
        self.users: dict[str, dict[str, Any]] = {
            "user_alice_01": {"displayName": "Alice", "whatsappPhone": "+51999111222"},
            "user_bob_02": {"displayName": "Bob", "whatsappPhone": "+51999333444"},
        }
        self.repositories: dict[str, dict[str, Any]] = {
            "repo_alice_01": {
                "_id": "repo_alice_01",
                "userId": "user_alice_01",
                "fullName": "growthrockstar/platform",
                "enabled": True,
            },
            "repo_bob_02": {
                "_id": "repo_bob_02",
                "userId": "user_bob_02",
                "fullName": "growthrockstar/platform",
                "enabled": True,
            },
        }
        self.posts: dict[str, dict[str, Any]] = {
            "post_alice_01": {
                "_id": "post_alice_01",
                "userId": "user_alice_01",
                "title": "Alice Post",
            }
        }
        self.recorded_events: list[dict[str, Any]] = []

    def query(self, function_name: str, args: dict[str, Any]) -> Any:
        if function_name == "users:getById":
            user_id = args.get("userId")
            return self.users.get(str(user_id)) if user_id else None

        if function_name == "repositories:getByFullName":
            full_name = args.get("fullName")
            for repo in self.repositories.values():
                if repo.get("fullName") == full_name and repo.get("enabled"):
                    return repo
            return None

        if function_name == "repositories:getByIdForUser":
            repo_id = str(args.get("repositoryId"))
            user_id = str(args.get("userId"))
            repo = self.repositories.get(repo_id)
            if repo and repo.get("userId") == user_id:
                return repo
            return None

        if function_name == "posts:getByIdForUser":
            post_id = str(args.get("postId"))
            user_id = str(args.get("userId"))
            post = self.posts.get(post_id)
            if post and post.get("userId") == user_id:
                return post
            return None

        return None

    def mutation(self, function_name: str, args: dict[str, Any]) -> str:
        if function_name == "repositories:removeForUser":
            repo_id = str(args.get("repositoryId"))
            user_id = str(args.get("userId"))
            repo = self.repositories.get(repo_id)
            if not repo:
                raise ValueError("Repository not found")
            if repo.get("userId") != user_id:
                raise PermissionError("Unauthorized: You do not own this repository")
            repo["enabled"] = False
            return repo_id

        if function_name == "repositories:getOrCreateForUser":
            user_id = str(args.get("userId"))
            if user_id not in self.users:
                raise PermissionError("Unauthorized: Invalid or non-existent userId")
            return f"repo_{user_id}"

        return "ok"


def test_cross_tenant_repository_isolation_negative_checks() -> None:
    fake_convex = FakeConvexClient()

    # Alice queries her own repository -> OK
    alice_repo = cast(dict[str, Any] | None, fake_convex.query(
        "repositories:getByIdForUser",
        {"repositoryId": "repo_alice_01", "userId": "user_alice_01"},
    ))
    assert alice_repo is not None
    assert alice_repo["userId"] == "user_alice_01"

    # Bob tries to query Alice's repository -> Negative Check: Returns None (Forbidden)
    cross_repo = fake_convex.query(
        "repositories:getByIdForUser",
        {"repositoryId": "repo_alice_01", "userId": "user_bob_02"},
    )
    assert cross_repo is None

    # Bob tries to delete/disable Alice's repository -> Negative Check: PermissionError
    with pytest.raises(PermissionError, match="Unauthorized: You do not own this repository"):
        fake_convex.mutation(
            "repositories:removeForUser",
            {"repositoryId": "repo_alice_01", "userId": "user_bob_02"},
        )


def test_cross_tenant_post_isolation_negative_checks() -> None:
    fake_convex = FakeConvexClient()

    # Alice queries her own post -> OK
    alice_post = cast(dict[str, Any] | None, fake_convex.query(
        "posts:getByIdForUser",
        {"postId": "post_alice_01", "userId": "user_alice_01"},
    ))
    assert alice_post is not None
    assert alice_post["userId"] == "user_alice_01"

    # Bob tries to read Alice's post via cross-tenant ID -> Negative Check: Returns None
    cross_post = fake_convex.query(
        "posts:getByIdForUser",
        {"postId": "post_alice_01", "userId": "user_bob_02"},
    )
    assert cross_post is None


def test_unknown_user_id_rejected_on_repository_registration() -> None:
    fake_convex = FakeConvexClient()

    with pytest.raises(PermissionError, match="Unauthorized: Invalid or non-existent userId"):
        fake_convex.mutation(
            "repositories:getOrCreateForUser",
            {"userId": "attacker_fake_user_id", "fullName": "victim/repo"},
        )
