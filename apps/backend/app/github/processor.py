import logging
from typing import Any, cast

from app.config import Settings
from app.github.client import GitHubClient
from app.github.story_batching import (
    STORY_BATCH_MAX_COMMITS,
    select_narrative_batch,
    should_emit_narrative,
)
from app.integrations.convex_client import ConvexGateway
from app.intelligence.commit_analyzer.analyzer import CommitAnalyzer
from app.intelligence.content_generator.generator import ContentGenerator
from app.intelligence.story_detector.detector import StoryDetector
from app.schemas.commit_analysis import CommitAnalysis
from app.schemas.github import CommitFile, NormalizedCommit, NormalizedGitHubEvent
from app.whatsapp.kapso.client import KapsoClient

logger = logging.getLogger(__name__)


def _commit_from_record(record: dict[str, Any]) -> NormalizedCommit:
    raw_files_value = record.get("files")
    files: list[CommitFile] = []
    if isinstance(raw_files_value, list):
        for raw_file_value in cast(list[Any], raw_files_value):
            if not isinstance(raw_file_value, dict):
                continue
            raw_file = cast(dict[str, Any], raw_file_value)
            files.append(
                CommitFile(
                    path=str(raw_file.get("path") or "unknown file"),
                    status=str(raw_file.get("status") or "modified"),
                    additions=int(raw_file.get("additions") or 0),
                    deletions=int(raw_file.get("deletions") or 0),
                    patch=(
                        str(raw_file.get("patch"))
                        if raw_file.get("patch") is not None
                        else None
                    ),
                )
            )
    return NormalizedCommit(
        sha=str(record.get("sha") or "unknown"),
        author=str(record.get("author") or "unknown author"),
        message=str(record.get("message") or "una mejora técnica"),
        committed_at=int(record.get("committedAt") or 0),
        branch=str(record.get("branch")) if record.get("branch") else None,
        additions=int(record.get("additions") or 0),
        deletions=int(record.get("deletions") or 0),
        changed_files=int(record.get("changedFiles") or len(files)),
        files=files,
        status="fetched",
    )


def _analysis_from_record(record: dict[str, Any]) -> CommitAnalysis:
    raw_technologies = record.get("technologies")
    technologies = (
        [str(item) for item in cast(list[Any], raw_technologies)]
        if isinstance(raw_technologies, list)
        else []
    )
    return CommitAnalysis(
        type=cast(Any, str(record.get("type") or "unknown")),
        summary=str(record.get("summary") or "Cambio técnico"),
        problem=str(record["problem"]) if record.get("problem") else None,
        solution=str(record["solution"]) if record.get("solution") else None,
        impact=str(record["impact"]) if record.get("impact") else None,
        technologies=technologies,
        importance=float(record.get("importance") or 0.5),
        publishability=float(record.get("publishability") or 0.5),
        potential_story=bool(record.get("potentialStory")),
    )


class GitHubEventProcessor:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.convex = ConvexGateway(settings)
        self.github_client = GitHubClient(settings)
        self.analyzer = CommitAnalyzer(settings)
        self.story_detector = StoryDetector(settings)
        self.content_generator = ContentGenerator(settings)
        self.kapso_client = KapsoClient(settings)

    def process_event(
        self,
        event: NormalizedGitHubEvent,
        raw_payload_metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not self.convex.is_configured:
            logger.warning("Convex is not configured. Skipping event processing.")
            return {"status": "skipped", "reason": "Convex not configured"}

        # 1. Record GitHub Event
        event_record = self.convex.record_github_event(event)
        if event_record.get("duplicate"):
            logger.info("Event %s is duplicate, ignoring.", event.delivery_id)
            return {"status": "duplicate", "delivery_id": event.delivery_id}

        # 2. Resolve repository and user identity
        existing_repo = self.convex.get_repository_by_full_name(event.repository_full_name)
        if existing_repo and existing_repo.get("userId"):
            user_id = str(existing_repo["userId"])
            repo_id = str(existing_repo["_id"])
        else:
            if self.settings.app_env != "production":
                user_id = self.convex.get_or_create_default_user()
                repo_id = self.convex.get_or_create_repository(
                    user_id=user_id,
                    full_name=event.repository_full_name,
                    default_branch=event.branch,
                )
            else:
                logger.warning(
                    "Repository %s is not registered by any tenant. Skipping push event.",
                    event.repository_full_name,
                )
                return {
                    "status": "skipped",
                    "reason": f"Repository {event.repository_full_name} is not registered",
                }

        # Resolve user phone for WhatsApp approvals
        user_doc = self.convex.get_user_by_id(user_id)
        user_phone = (
            str(user_doc.get("whatsappPhone"))
            if user_doc and user_doc.get("whatsappPhone")
            else self.settings.default_user_phone
        )

        # 3. Emit initial activity event
        self.convex.record_activity(
            user_id=user_id,
            type_="github.event.received",
            label=f"Push received for {event.repository_full_name} ({len(event.commit_shas)} commits)",
            status="completed",
            repository_id=repo_id,
            metadata={"deliveryId": event.delivery_id, "branch": event.branch or "main"},
        )

        # 4. Fetch and store commits
        normalized_commits: list[NormalizedCommit] = []
        commit_ids: list[str] = []
        analyses: list[CommitAnalysis] = []

        shas = event.commit_shas or ["demo_push_sha_01"]
        for sha in shas:
            self.convex.record_activity(
                user_id=user_id,
                type_="commit.fetch.started",
                label=f"Fetching changes for commit {sha[:7]}",
                status="started",
                repository_id=repo_id,
                metadata={"sha": sha},
            )

            commit = self.github_client.fetch_commit(
                event.repository_full_name,
                sha,
                raw_payload_metadata,
            )
            if event.branch and not commit.branch:
                commit = commit.model_copy(update={"branch": event.branch})
            commit_res = self.convex.record_commit(repo_id, commit)
            commit_id = commit_res.get("commitId")
            if commit_id:
                commit_ids.append(commit_id)
            normalized_commits.append(commit)

            self.convex.record_activity(
                user_id=user_id,
                type_="commit.fetch.completed",
                label=f"Commit {sha[:7]} fetched ({commit.changed_files} files changed)",
                status="completed",
                repository_id=repo_id,
                metadata={"sha": sha},
            )

            # 5. Analyze commit
            self.convex.record_activity(
                user_id=user_id,
                type_="commit.analysis.started",
                label=f"Analyzing technical impact for {sha[:7]}",
                status="started",
                repository_id=repo_id,
                metadata={"sha": sha},
            )

            analysis = self.analyzer.analyze(commit)
            analyses.append(analysis)
            if commit_id:
                self.convex.record_commit_analysis(
                    commit_id=commit_id,
                    repository_id=repo_id,
                    analysis=analysis,
                )

            self.convex.record_activity(
                user_id=user_id,
                type_="commit.analysis.completed",
                label=f"Commit classified as {analysis.type}: {analysis.summary[:40]}...",
                status="completed",
                repository_id=repo_id,
                metadata={"sha": sha, "type": analysis.type},
            )

        # 6. Group recent commits into one narrative. A small commit waits for
        # the next related push; a substantial commit can stand on its own.
        current_commit_ids = set(commit_ids)
        recent_records = self.convex.list_commits_for_repository(
            repo_id,
            limit=STORY_BATCH_MAX_COMMITS * 4,
        )
        clustered_commit_ids = {
            str(commit_id)
            for cluster in self.convex.list_story_clusters_for_repository(repo_id)
            for commit_id in cluster.get("relatedCommitIds", [])
        }
        batch_records = select_narrative_batch(
            recent_records,
            clustered_commit_ids=clustered_commit_ids,
            current_commit_ids=current_commit_ids,
            branch=event.branch,
        )
        batch_commits = [_commit_from_record(record) for record in batch_records]
        batch_commit_ids = [str(record["_id"]) for record in batch_records]

        if not should_emit_narrative(batch_commits):
            queued_shas = [commit.sha for commit in batch_commits]
            self.convex.record_activity(
                user_id=user_id,
                type_="story.batch.queued",
                label=(
                    f"Commit {queued_shas[-1][:7] if queued_shas else 'new'} queued; "
                    "waiting for related work to form a narrative"
                ),
                status="waiting",
                repository_id=repo_id,
                metadata={
                    "pendingCommitCount": len(batch_commits),
                    "pendingCommitShas": queued_shas,
                },
            )
            return {
                "status": "queued",
                "story_detected": False,
                "queued_commit_shas": queued_shas,
            }

        normalized_commits = batch_commits
        commit_ids = batch_commit_ids
        analysis_records = self.convex.list_commit_analyses_for_repository(
            repo_id,
            limit=STORY_BATCH_MAX_COMMITS * 4,
        )
        analyses_by_commit_id = {
            str(record.get("commitId")): _analysis_from_record(record)
            for record in analysis_records
            if record.get("commitId")
        }
        analysis_candidates = [
            analyses_by_commit_id.get(str(record["_id"]))
            for record in batch_records
        ]
        analyses = []
        for analysis, commit in zip(
            analysis_candidates, normalized_commits, strict=True
        ):
            analyses.append(analysis or self.analyzer.analyze(commit))

        # 7. Story Detection
        self.convex.record_activity(
            user_id=user_id,
            type_="story.search.started",
            label="Searching related technical work across commits",
            status="started",
            repository_id=repo_id,
        )

        story_result = self.story_detector.detect_story(normalized_commits, analyses)
        if story_result.story_detected:
            _ = self.convex.record_story_cluster(
                repository_id=repo_id,
                commit_ids=commit_ids,
                reason=story_result.title,
                score=story_result.confidence,
            )

            story_id = self.convex.record_story(
                user_id=user_id,
                repository_id=repo_id,
                story=story_result,
                related_commit_ids=commit_ids,
                status="detected",
            )

            self.convex.record_activity(
                user_id=user_id,
                type_="story.detected",
                label=f'Story detected: "{story_result.title}" (confidence: {int(story_result.confidence * 100)}%)',
                status="completed",
                repository_id=repo_id,
                metadata={"storyId": story_id, "title": story_result.title},
            )

            # 8. Content Generation
            self.convex.record_activity(
                user_id=user_id,
                type_="post.generation.started",
                label="Drafting LinkedIn post from verified story evidence",
                status="started",
                repository_id=repo_id,
            )

            preferences = self.convex.get_user_preferences(user_id)
            draft_result = self.content_generator.generate_draft(
                story_result,
                preferences=preferences,
            )
            post_id = self.convex.record_post(
                user_id=user_id,
                story_id=story_id,
                format_=draft_result.format,
                status="awaiting_approval",
            )

            version_id = self.convex.record_post_version(
                post_id=post_id,
                version=1,
                title=draft_result.title,
                body=draft_result.body,
                generation_reason=draft_result.format_rationale,
            )

            self.convex.record_activity(
                user_id=user_id,
                type_="post.generation.completed",
                label=f"LinkedIn draft V1 generated ({draft_result.format})",
                status="completed",
                repository_id=repo_id,
                metadata={"postId": post_id, "versionId": version_id},
            )

            # 9. Queue approval without sending an outbound message. Kapso free-form
            # messages are sent only after the user opens the 24-hour conversation window.
            approval_req_id = self.convex.record_approval_request(
                user_id=user_id,
                post_id=post_id,
                current_post_version_id=version_id,
                recipient_phone=user_phone,
                status="pending",
            )

            if self.convex.is_whatsapp_window_open(user_phone):
                outbound = self.kapso_client.send_draft_for_approval(
                    to_phone=user_phone,
                    story_title=draft_result.title,
                    post_body=draft_result.body,
                    version=1,
                )
                if outbound.message_id:
                    self.convex.set_approval_outbound_message_id(
                        approval_request_id=approval_req_id,
                        kapso_message_id=outbound.message_id,
                    )
                    self.convex.record_approval_message(
                        approval_request_id=approval_req_id,
                        direction="outbound",
                        message_id=outbound.message_id,
                        content=outbound.body,
                    )
                self.convex.record_activity(
                    user_id=user_id,
                    type_="approval.whatsapp.sent",
                    label=(
                        f"Draft V1 sent to WhatsApp ({user_phone}) inside the active 24h window"
                    ),
                    status="completed",
                    repository_id=repo_id,
                    metadata={
                        "approvalRequestId": approval_req_id,
                        "trigger": "github_push_active_window",
                    },
                )
            else:
                self.convex.record_activity(
                    user_id=user_id,
                    type_="approval.whatsapp.queued",
                    label=(
                        f"Draft V1 queued for WhatsApp ({user_phone}); "
                        "waiting for an inbound message to open the 24h window"
                    ),
                    status="started",
                    repository_id=repo_id,
                    metadata={"approvalRequestId": approval_req_id},
                )

            return {
                "status": "processed",
                "story_id": story_id,
                "post_id": post_id,
                "version_id": version_id,
                "approval_request_id": approval_req_id,
            }

        return {"status": "processed", "story_detected": False}
