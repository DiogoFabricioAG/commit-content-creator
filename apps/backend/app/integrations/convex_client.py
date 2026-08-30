import time
from typing import Any, cast

import httpx
from convex.values import CoercibleToConvexValue

from app.config import Settings
from app.schemas.commit_analysis import CommitAnalysis
from app.schemas.github import NormalizedCommit, NormalizedGitHubEvent
from app.schemas.preferences import EditorialPreferences
from app.schemas.story import StoryDetectionResult
from convex import ConvexClient


class ConvexGateway:
    """Lazily exposes the official Convex Python client to backend services."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._client = ConvexClient(settings.convex_url) if settings.convex_url else None

    @property
    def is_configured(self) -> bool:
        return self._client is not None

    @property
    def client(self) -> ConvexClient:
        if self._client is None:
            raise RuntimeError("CONVEX_URL is required before using the Convex client")
        return self._client

    # Activity & Users
    def record_activity(
        self,
        *,
        user_id: str,
        type_: str,
        label: str,
        status: str,
        repository_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str | None:
        if not self.is_configured:
            return None
        payload: dict[str, CoercibleToConvexValue] = {
            "userId": user_id,
            "type": type_,
            "label": label,
            "status": status,
        }
        if repository_id:
            payload["repositoryId"] = repository_id
        if metadata:
            payload["metadata"] = cast(dict[str, CoercibleToConvexValue], metadata)
        result = self.client.mutation("activity:record", payload)
        return cast(str, result) if result else None

    def get_or_create_default_user(
        self,
        whatsapp_phone: str | None = None,
        display_name: str | None = None,
        email: str | None = None,
    ) -> str:
        phone = whatsapp_phone or self.settings.default_user_phone
        result = self.client.mutation(
            "users:getOrCreateDefault",
            {
                "whatsappPhone": phone,
                "displayName": display_name or "Lead Developer",
                "email": email or "developer@proofofwork.local",
            },
        )
        return cast(str, result)

    def get_or_create_repository(
        self,
        *,
        user_id: str,
        full_name: str,
        default_branch: str | None = None,
    ) -> str:
        payload: dict[str, CoercibleToConvexValue] = {
            "userId": user_id,
            "fullName": full_name,
        }
        if default_branch:
            payload["defaultBranch"] = default_branch
        result = self.client.mutation("repositories:getOrCreateForUser", payload)
        return cast(str, result)

    def get_repository_by_full_name(self, full_name: str) -> dict[str, Any] | None:
        result = self.client.query("repositories:getByFullName", {"fullName": full_name})
        return cast(dict[str, Any], result) if result else None

    def get_repository_by_id_for_user(
        self, *, user_id: str, repository_id: str
    ) -> dict[str, Any] | None:
        result = self.client.query(
            "repositories:getByIdForUser",
            {"userId": user_id, "repositoryId": repository_id},
        )
        return cast(dict[str, Any] | None, result)

    def list_repositories_for_user(self, user_id: str) -> list[dict[str, Any]]:
        result = self.client.query("repositories:listForUser", {"userId": user_id})
        return cast(list[dict[str, Any]], result or [])

    def remove_repository_for_user(self, user_id: str, repository_id: str) -> str:
        result = self.client.mutation(
            "repositories:removeForUser",
            {"userId": user_id, "repositoryId": repository_id},
        )
        return cast(str, result)

    def get_user_by_id(self, user_id: str) -> dict[str, Any] | None:
        result = self.client.query("users:getById", {"userId": user_id})
        return cast(dict[str, Any], result) if result else None

    def update_user_profile(
        self,
        *,
        user_id: str,
        display_name: str | None = None,
        whatsapp_phone: str | None = None,
        email: str | None = None,
    ) -> str:
        payload: dict[str, CoercibleToConvexValue] = {"userId": user_id}
        if display_name is not None:
            payload["displayName"] = display_name
        if whatsapp_phone is not None:
            payload["whatsappPhone"] = whatsapp_phone
        if email is not None:
            payload["email"] = email
        result = self.client.mutation("users:updateProfile", payload)
        return cast(str, result)

    def list_activity_for_user(
        self, user_id: str, limit: int = 50
    ) -> list[dict[str, Any]]:
        result = self.client.query(
            "activity:listRecent",
            {"userId": user_id, "limit": limit},
        )
        return cast(list[dict[str, Any]], result or [])

    def list_posts_for_user(
        self, user_id: str, limit: int = 50
    ) -> list[dict[str, Any]]:
        result = self.client.query(
            "posts:listForUser",
            {"userId": user_id, "limit": limit},
        )
        return cast(list[dict[str, Any]], result or [])

    def list_approval_requests_for_user(
        self, user_id: str
    ) -> list[dict[str, Any]]:
        result = self.client.query(
            "approvalRequests:listForUser",
            {"userId": user_id},
        )
        return cast(list[dict[str, Any]], result or [])

    # GitHub Events & Commits
    def record_github_event(self, event: NormalizedGitHubEvent) -> dict[str, Any]:
        payload: dict[str, CoercibleToConvexValue] = {
            "deliveryId": event.delivery_id,
            "eventType": event.event_type,
            "repositoryFullName": event.repository_full_name,
            "commitShas": event.commit_shas,
        }
        if event.branch:
            payload["branch"] = event.branch
        if event.action:
            payload["action"] = event.action

        result = self.client.mutation("githubEvents:record", payload)
        return cast(dict[str, Any], result)

    def record_commit(self, repository_id: str, commit: NormalizedCommit) -> dict[str, Any]:
        payload: dict[str, CoercibleToConvexValue] = {
            "repositoryId": repository_id,
            "sha": commit.sha,
            "author": commit.author,
            "message": commit.message,
            "committedAt": commit.committed_at,
            "additions": commit.additions,
            "deletions": commit.deletions,
            "changedFiles": commit.changed_files,
            # Convex optional fields omit absent values; sending Python None
            # is different from omitting the field and fails validation.
            "files": [f.model_dump(exclude_none=True) for f in commit.files],
            "status": commit.status,
        }
        if commit.branch:
            payload["branch"] = commit.branch

        result = self.client.mutation("commits:record", payload)
        return cast(dict[str, Any], result)

    def list_commits_for_repository(
        self, repository_id: str, limit: int = 50
    ) -> list[dict[str, Any]]:
        result = self.client.query(
            "commits:listForRepository",
            {"repositoryId": repository_id, "limit": limit},
        )
        return cast(list[dict[str, Any]], result or [])

    def list_commits_by_ids(self, commit_ids: list[str]) -> list[dict[str, Any]]:
        if not commit_ids:
            return []
        result = self.client.query(
            "commits:listByIds",
            {"commitIds": commit_ids},
        )
        return cast(list[dict[str, Any]], result or [])

    def list_commit_analyses_for_repository(
        self, repository_id: str, limit: int = 50
    ) -> list[dict[str, Any]]:
        result = self.client.query(
            "commitAnalyses:listForRepository",
            {"repositoryId": repository_id, "limit": limit},
        )
        return cast(list[dict[str, Any]], result or [])

    # Commit Intelligence
    def record_commit_analysis(
        self,
        *,
        commit_id: str,
        repository_id: str,
        analysis: CommitAnalysis,
    ) -> str:
        payload: dict[str, CoercibleToConvexValue] = {
            "commitId": commit_id,
            "repositoryId": repository_id,
            "type": analysis.type,
            "summary": analysis.summary,
            "technologies": analysis.technologies,
            "importance": analysis.importance,
            "publishability": analysis.publishability,
            "potentialStory": analysis.potential_story,
        }
        if analysis.problem:
            payload["problem"] = analysis.problem
        if analysis.solution:
            payload["solution"] = analysis.solution
        if analysis.impact:
            payload["impact"] = analysis.impact

        result = self.client.mutation("commitAnalyses:record", payload)
        return cast(str, result)

    # Story Clusters & Stories
    def record_story_cluster(
        self,
        *,
        repository_id: str,
        commit_ids: list[str],
        reason: str | None = None,
        score: float | None = None,
    ) -> str:
        payload: dict[str, CoercibleToConvexValue] = {
            "repositoryId": repository_id,
            "relatedCommitIds": commit_ids,
        }
        if reason or score is not None:
            rel_meta: dict[str, CoercibleToConvexValue] = {}
            if reason:
                rel_meta["reason"] = reason
            if score is not None:
                rel_meta["score"] = score
            payload["relationshipMetadata"] = rel_meta

        result = self.client.mutation("storyClusters:record", payload)
        return cast(str, result)

    def list_story_clusters_for_repository(
        self, repository_id: str
    ) -> list[dict[str, Any]]:
        result = self.client.query(
            "storyClusters:listForRepository",
            {"repositoryId": repository_id},
        )
        return cast(list[dict[str, Any]], result or [])

    def record_story(
        self,
        *,
        user_id: str,
        repository_id: str,
        story: StoryDetectionResult,
        related_commit_ids: list[str],
        status: str = "detected",
    ) -> str:
        payload: dict[str, CoercibleToConvexValue] = {
            "userId": user_id,
            "repositoryId": repository_id,
            "title": story.title,
            "summary": story.summary,
            "storyType": story.story_type,
            "relatedCommitIds": related_commit_ids,
            "confidence": story.confidence,
            "publishability": story.publishability,
            "status": status,
        }
        if story.problem:
            payload["problem"] = story.problem
        if story.attempts:
            payload["attempts"] = story.attempts
        if story.solution:
            payload["solution"] = story.solution
        if story.learning:
            payload["learning"] = story.learning
        if story.impact:
            payload["impact"] = story.impact

        result = self.client.mutation("stories:record", payload)
        return cast(str, result)

    # LinkedIn Posts & Versions
    def record_post(
        self,
        *,
        user_id: str,
        story_id: str,
        format_: str,
        status: str = "draft",
    ) -> str:
        result = self.client.mutation(
            "posts:record",
            {
                "userId": user_id,
                "storyId": story_id,
                "platform": "linkedin",
                "format": format_,
                "status": status,
            },
        )
        return cast(str, result)

    def record_post_version(
        self,
        *,
        post_id: str,
        version: int,
        body: str,
        title: str | None = None,
        generation_reason: str | None = None,
    ) -> str:
        payload: dict[str, CoercibleToConvexValue] = {
            "postId": post_id,
            "version": version,
            "body": body,
        }
        if title:
            payload["title"] = title
        if generation_reason:
            payload["generationReason"] = generation_reason

        result = self.client.mutation("postVersions:record", payload)
        return cast(str, result)

    # Historical digest runs
    def reserve_historical_digest(
        self,
        *,
        user_id: str,
        repository_id: str,
        repository_full_name: str,
        branch: str | None,
        fingerprint: str,
    ) -> dict[str, Any]:
        payload: dict[str, CoercibleToConvexValue] = {
            "userId": user_id,
            "repositoryId": repository_id,
            "repositoryFullName": repository_full_name,
            "fingerprint": fingerprint,
        }
        if branch:
            payload["branch"] = branch
        result = self.client.mutation("historicalDigests:reserve", payload)
        return cast(dict[str, Any], result)

    def complete_historical_digest(
        self,
        *,
        digest_id: str,
        included_commit_shas: list[str],
        filtered_commit_shas: list[str],
        story_id: str,
        post_id: str,
        approval_request_id: str,
        title: str,
        summary: str,
        status: str = "awaiting_approval",
    ) -> None:
        self.client.mutation(
            "historicalDigests:complete",
            {
                "digestId": digest_id,
                "includedCommitShas": included_commit_shas,
                "filteredCommitShas": filtered_commit_shas,
                "storyId": story_id,
                "postId": post_id,
                "approvalRequestId": approval_request_id,
                "title": title,
                "summary": summary,
                "status": status,
            },
        )

    def fail_historical_digest(self, *, digest_id: str, error: str) -> None:
        self.client.mutation(
            "historicalDigests:fail",
            {"digestId": digest_id, "error": error[:1000]},
        )

    def upload_media(self, *, content: bytes, mime_type: str) -> dict[str, str]:
        upload_url = cast(str, self.client.mutation("media:generateUploadUrl", {}))
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                upload_url,
                content=content,
                headers={"Content-Type": mime_type},
            )
            response.raise_for_status()
            data = cast(dict[str, Any], response.json())

        storage_id = str(data.get("storageId") or "")
        if not storage_id:
            raise RuntimeError("Convex storage upload returned no storage ID")

        media_url = self.client.query("media:getUrl", {"storageId": storage_id})
        if not isinstance(media_url, str) or not media_url:
            raise RuntimeError("Convex storage returned no public media URL")

        return {"storageId": storage_id, "url": media_url}

    def record_media_asset(
        self,
        *,
        post_version_id: str,
        kind: str,
        storage_id: str,
        mime_type: str,
        url: str,
        alt_text: str,
        source: str = "generated",
        prompt: str | None = None,
    ) -> str:
        payload: dict[str, CoercibleToConvexValue] = {
            "postVersionId": post_version_id,
            "kind": kind,
            "storageId": storage_id,
            "mimeType": mime_type,
            "url": url,
            "altText": alt_text,
            "source": source,
        }
        if prompt:
            payload["prompt"] = prompt
        result = self.client.mutation("media:record", payload)
        return cast(str, result)

    def list_media_for_post_version(self, post_version_id: str) -> list[dict[str, Any]]:
        result = self.client.query(
            "media:listForPostVersion",
            {"postVersionId": post_version_id},
        )
        return cast(list[dict[str, Any]], result or [])

    def approve_post_version(self, version_id: str) -> None:
        self.client.mutation("postVersions:approve", {"versionId": version_id})

    def update_post_status(
        self,
        post_id: str,
        status: str,
        current_version_id: str | None = None,
    ) -> None:
        payload: dict[str, CoercibleToConvexValue] = {
            "postId": post_id,
            "status": status,
        }
        if current_version_id:
            payload["currentVersionId"] = current_version_id
        self.client.mutation("posts:updateStatus", payload)

    def set_post_external_urn(
        self,
        post_id: str,
        external_post_urn: str,
        status: str = "published",
    ) -> None:
        self.client.mutation(
            "posts:setExternalUrn",
            {
                "postId": post_id,
                "externalPostUrn": external_post_urn,
                "status": status,
            },
        )

    # Social Accounts
    def upsert_social_account(
        self,
        *,
        user_id: str,
        provider: str = "linkedin",
        access_token_encrypted: str,
        scopes: list[str],
        provider_member_id: str | None = None,
        author_urn: str | None = None,
        expires_at: int | None = None,
    ) -> str:
        payload: dict[str, CoercibleToConvexValue] = {
            "userId": user_id,
            "provider": provider,
            "accessTokenEncrypted": access_token_encrypted,
            "scopes": scopes,
        }
        if provider_member_id:
            payload["providerMemberId"] = provider_member_id
        if author_urn:
            payload["authorUrn"] = author_urn
        if expires_at:
            payload["expiresAt"] = expires_at

        result = self.client.mutation("socialAccounts:upsert", payload)
        return cast(str, result)

    def get_social_account(self, user_id: str, provider: str = "linkedin") -> dict[str, Any] | None:
        result = self.client.query(
            "socialAccounts:getByUserAndProvider",
            {"userId": user_id, "provider": provider},
        )
        return cast(dict[str, Any] | None, result)

    def get_user_preferences(self, user_id: str) -> EditorialPreferences | None:
        result = self.client.query("preferences:getForUser", {"userId": user_id})
        if not result:
            return None

        raw = cast(dict[str, Any], result)
        defaults = EditorialPreferences()
        try:
            return EditorialPreferences(
                role_title=str(raw.get("roleTitle") or defaults.role_title),
                language=raw.get("language") or defaults.language,
                tone=raw.get("tone") or defaults.tone,
                target_audience=raw.get("targetAudience") or defaults.target_audience,
                technical_level=raw.get("technicalLevel") or defaults.technical_level,
                post_length=raw.get("postLength") or defaults.post_length,
                avoid_words=raw.get("avoidWords") or defaults.avoid_words,
                preferred_cta=raw.get("preferredCTA") or defaults.preferred_cta,
                custom_cta=raw.get("customCTA"),
                custom_rules=raw.get("customRules") or defaults.custom_rules,
                include_code_snippets=bool(
                    raw.get("includeCodeSnippets", defaults.include_code_snippets)
                ),
                include_metrics=bool(
                    raw.get("includeMetrics", defaults.include_metrics)
                ),
                hashtags=raw.get("hashtags") or defaults.hashtags,
                allowed_formats=raw.get("allowedFormats") or defaults.allowed_formats,
                auto_publish=bool(raw.get("autoPublish", defaults.auto_publish)),
                onboarding_completed=bool(
                    raw.get("onboardingCompleted", defaults.onboarding_completed)
                ),
            )
        except (TypeError, ValueError):
            return defaults

    def save_user_preferences(
        self, user_id: str, preferences: EditorialPreferences
    ) -> str:
        payload: dict[str, CoercibleToConvexValue] = {
            "userId": user_id,
            "roleTitle": preferences.role_title,
            "language": preferences.language,
            "tone": preferences.tone,
            "targetAudience": preferences.target_audience,
            "technicalLevel": preferences.technical_level,
            "postLength": preferences.post_length,
            "avoidWords": preferences.avoid_words,
            "preferredCTA": preferences.preferred_cta,
            "hashtags": preferences.hashtags,
            "allowedFormats": preferences.allowed_formats,
            "autoPublish": preferences.auto_publish,
            "onboardingCompleted": preferences.onboarding_completed,
        }
        if preferences.custom_cta is not None:
            payload["customCTA"] = preferences.custom_cta
        if preferences.custom_rules:
            payload["customRules"] = preferences.custom_rules
        payload["includeCodeSnippets"] = preferences.include_code_snippets
        payload["includeMetrics"] = preferences.include_metrics

        result = self.client.mutation("preferences:save", payload)
        return cast(str, result)

    # Approval Requests & Messages
    def record_approval_request(
        self,
        *,
        user_id: str,
        post_id: str,
        current_post_version_id: str,
        recipient_phone: str,
        status: str = "pending",
        kapso_msg_id: str | None = None,
    ) -> str:
        payload: dict[str, CoercibleToConvexValue] = {
            "userId": user_id,
            "postId": post_id,
            "channel": "whatsapp",
            "status": status,
            "currentPostVersionId": current_post_version_id,
            "recipientPhone": recipient_phone,
        }
        if kapso_msg_id:
            payload["kapsoOutboundMessageId"] = kapso_msg_id

        result = self.client.mutation("approvalRequests:record", payload)
        return cast(str, result)

    def get_pending_approval_for_phone(self, recipient_phone: str) -> dict[str, Any] | None:
        result = self.client.query(
            "approvalRequests:getPendingForPhone",
            {"recipientPhone": recipient_phone},
        )
        return cast(dict[str, Any] | None, result)

    def list_pending_approvals_for_phone(self, recipient_phone: str) -> list[dict[str, Any]]:
        result = self.client.query(
            "approvalRequests:listPendingForPhone",
            {"recipientPhone": recipient_phone},
        )
        return cast(list[dict[str, Any]], result or [])

    def open_whatsapp_window(
        self,
        *,
        user_id: str,
        recipient_phone: str,
        inbound_message_id: str,
    ) -> str:
        result = self.client.mutation(
            "whatsappSessions:open",
            {
                "userId": user_id,
                "phone": recipient_phone,
                "inboundMessageId": inbound_message_id,
            },
        )
        return cast(str, result)

    def is_whatsapp_window_open(self, recipient_phone: str) -> bool:
        result = self.client.query(
            "whatsappSessions:getForPhone",
            {"phone": recipient_phone},
        )
        if not result:
            return False
        session = cast(dict[str, Any], result)
        try:
            return int(session.get("expiresAt", 0)) > int(time.time() * 1000)
        except (TypeError, ValueError):
            return False

    def update_approval_request(
        self,
        *,
        approval_request_id: str,
        status: str,
        current_post_version_id: str | None = None,
    ) -> None:
        payload: dict[str, CoercibleToConvexValue] = {
            "approvalRequestId": approval_request_id,
            "status": status,
        }
        if current_post_version_id:
            payload["currentPostVersionId"] = current_post_version_id
        self.client.mutation("approvalRequests:updateStatus", payload)

    def set_approval_outbound_message_id(
        self,
        *,
        approval_request_id: str,
        kapso_message_id: str,
    ) -> None:
        self.client.mutation(
            "approvalRequests:setOutboundMessageId",
            {
                "approvalRequestId": approval_request_id,
                "kapsoOutboundMessageId": kapso_message_id,
            },
        )

    def record_approval_message(
        self,
        *,
        approval_request_id: str,
        direction: str,
        message_id: str,
        content: str,
        interpreted_intent: str | None = None,
        confidence: float | None = None,
    ) -> str:
        payload: dict[str, CoercibleToConvexValue] = {
            "approvalRequestId": approval_request_id,
            "direction": direction,
            "messageId": message_id,
            "content": content,
        }
        if interpreted_intent:
            payload["interpretedIntent"] = interpreted_intent
        if confidence is not None:
            payload["confidence"] = confidence

        result = self.client.mutation("approvalMessages:record", payload)
        return cast(str, result)

    def list_approval_messages_for_request(
        self,
        approval_request_id: str,
    ) -> list[dict[str, Any]]:
        result = self.client.query(
            "approvalMessages:listForRequest",
            {"approvalRequestId": approval_request_id},
        )
        return cast(list[dict[str, Any]], result or [])
