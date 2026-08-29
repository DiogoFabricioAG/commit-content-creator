**PROOF OF WORK**

**Prompt Maestro de Desarrollo --- Codex**

GitHub → Story Intelligence → LinkedIn → WhatsApp (Kapso) → Aprobación natural → Publicación

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr>
<th><p><strong>Versión definitiva para comenzar el MVP</strong></p>
<p>Este documento reemplaza la versión anterior. La validación principal ocurre por WhatsApp mediante Kapso. Proof of Work interpreta la respuesta del usuario en lenguaje natural y solo publica en LinkedIn cuando existe aprobación explícita del borrador vigente.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

Arquitectura enfocada en el track Content Machine: crear, validar, publicar y distribuir de forma real.

# PROMPT MAESTRO PARA CODEX

You are the lead engineer responsible for building a functional hackathon MVP called "Proof of Work". Build a real end-to-end application, not a static prototype or fake demo.

# 1. Role and working mode {#role-and-working-mode}

- Work autonomously. Do not ask for confirmation for normal implementation decisions, file creation, dependency installation, migrations, refactors, tests, or development commands.

- Only stop for destructive actions that could lose user data, real external credentials/manual third-party steps you cannot perform, or a genuinely ambiguous product decision that materially changes scope.

- Prefer working vertical slices over premature abstractions.

- After each milestone, run tests, lint/type checks, fix failures, report briefly, and continue.

- When an external API may have changed, verify the current official documentation. Never invent endpoints, headers, scopes, SDK methods, payloads, or API versions.

# 2. Product thesis {#product-thesis}

Proof of Work turns a developer's real work into publishable LinkedIn content without forcing the developer to stop working and manually explain what they did.

CORE LOOP\
\
WORK\
↓\
EVIDENCE\
↓\
UNDERSTANDING\
↓\
STORY MEMORY\
↓\
STORY DETECTION\
↓\
LINKEDIN DRAFT\
↓\
WHATSAPP APPROVAL\
↓\
LINKEDIN PUBLISHING

- A commit is evidence, not automatically a post.

- Multiple commits and pull requests may form one story.

- The system must explain why a story is worth surfacing.

- Generated claims must be grounded in repository evidence.

- Publishing requires explicit human approval.

- The primary approval interface is WhatsApp, not the web dashboard.

- For the MVP, distribution is focused on LinkedIn only.

## Example of a story

Commit 1: feat: add notification polling\
Commit 2: fix: prevent duplicate notification requests\
Commit 3: refactor: replace polling with websocket events\
\
NOT → three separate social posts\
YES → one evolving story:\
"Why we replaced polling with WebSockets."

# 3. Primary hackathon demo {#primary-hackathon-demo}

1\. Developer executes: git push\
\
2. Dashboard reacts automatically:\
Commit received\
↓\
Fetching changes\
↓\
Analyzing files\
↓\
Understanding change\
↓\
Searching related work\
↓\
Story detected\
↓\
LinkedIn draft generated\
\
3. Proof of Work sends the draft to the user on WhatsApp via Kapso.\
\
4. User replies naturally:\
"Ta bueno, publícalo noma"\
"Está muy largo, hazlo más corto"\
"Cambia el inicio"\
"No publiques esto"\
\
5. Approval Agent interprets the intent.\
\
6. If revision is requested:\
regenerate → send new version → ask again\
\
7. Only after explicit approval:\
publish through LinkedIn API\
\
8. WhatsApp confirms:\
"Publicado ✓"

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr>
<th><p><strong>Demo rule</strong></p>
<p>No manual browser refresh. Convex propagates state changes reactively to the dashboard while WhatsApp acts as the human approval layer.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 4. Required technical stack {#required-technical-stack}

| Layer | Technology | Role |
|----|----|----|
| Frontend | Next.js + TypeScript + Tailwind + shadcn/ui | Dashboard, onboarding, history, live activity |
| State / DB / Realtime | Convex | Source of truth, persistence, reactive UI, vector search |
| Python backend | FastAPI + Python 3.12+ | GitHub/Kapso webhooks, OAuth callback, intelligence workers |
| Convex from Python | Convex Python Client | Queries, mutations, actions and documented subscriptions |
| GitHub | GitHub App + REST API + Webhooks | Work ingestion |
| AI | OpenAI Python SDK + Pydantic | Commit analysis, story detection, approval intent, content generation |
| WhatsApp | Kapso REST API | Send drafts and receive approval/revision in natural language |
| LinkedIn | OAuth 2.0 + Share on LinkedIn + Posts API | Connect member account and publish approved posts |
| JS tooling | pnpm | Web + Convex tooling |
| Python tooling | uv preferred + Ruff + Pyright/mypy + pytest | Backend development and quality |

- Do NOT introduce PostgreSQL, Prisma, Supabase, Firebase, Redis, BullMQ, Kafka, or another database for the MVP unless a concrete blocker proves Convex insufficient.

- Do NOT introduce LangChain or LangGraph initially. The pipeline is mostly deterministic.

- Do NOT build custom WebSocket infrastructure for dashboard updates when Convex reactivity already solves it.

# 5. Target architecture {#target-architecture}

GITHUB\
│\
push / PR webhook\
│\
▼\
FASTAPI\
│\
Convex Python Client\
│\
▼\
┌────────────────────────────────────────────────────┐\
│ CONVEX │\
│ repositories commits activityEvents │\
│ githubEvents analyses socialAccounts │\
│ storyClusters stories posts │\
│ approvalRequests approvalMessages postVersions │\
└───────────────┬───────────────────────────────┬────┘\
│ │\
Python Intelligence Next.js\
│ Dashboard\
▼\
GitHub API + OpenAI\
│\
▼\
LinkedIn draft\
│\
▼\
KAPSO\
│\
▼\
WhatsApp\
│\
natural-language reply\
│\
▼\
Kapso webhook → FastAPI\
│\
▼\
Approval Agent\
┌───────┼─────────┬──────────┐\
│ │ │ │\
APPROVE REVISE REJECT CLARIFY/HOLD\
│ │\
│ └→ regenerate → WhatsApp\
▼\
LinkedIn Publisher\
│\
▼\
LINKEDIN

# 6. Repository structure {#repository-structure}

proof-of-work/\
├── apps/\
│ ├── web/\
│ │ ├── app/\
│ │ ├── components/\
│ │ └── lib/\
│ └── backend/\
│ ├── app/\
│ │ ├── api/\
│ │ │ ├── github_webhooks.py\
│ │ │ ├── kapso_webhooks.py\
│ │ │ ├── linkedin_oauth.py\
│ │ │ └── health.py\
│ │ ├── github/\
│ │ ├── linkedin/\
│ │ ├── whatsapp/kapso/\
│ │ ├── intelligence/\
│ │ │ ├── commit_analyzer/\
│ │ │ ├── story_detector/\
│ │ │ ├── content_generator/\
│ │ │ └── approval_agent/\
│ │ ├── schemas/\
│ │ ├── security/\
│ │ └── main.py\
│ └── tests/\
├── convex/\
│ ├── schema.ts\
│ ├── users.ts\
│ ├── repositories.ts\
│ ├── githubInstallations.ts\
│ ├── githubEvents.ts\
│ ├── commits.ts\
│ ├── commitAnalyses.ts\
│ ├── storyClusters.ts\
│ ├── stories.ts\
│ ├── posts.ts\
│ ├── postVersions.ts\
│ ├── socialAccounts.ts\
│ ├── approvalRequests.ts\
│ ├── approvalMessages.ts\
│ └── activity.ts\
├── fixtures/\
├── .env.example\
├── package.json\
├── pnpm-workspace.yaml\
├── pyproject.toml\
└── README.md

# 7. Convex data model {#convex-data-model}

Design a clean Convex schema. Use indexes for idempotency and lookup paths. Do not overuse JSON blobs.

## users

- displayName/email only if needed

- whatsappPhone normalized to E.164

- createdAt / updatedAt

## githubInstallations

- userId

- githubInstallationId

- account metadata

- createdAt

## repositories

- userId

- installationId

- githubRepositoryId

- owner

- name

- fullName

- defaultBranch

- enabled

- createdAt / updatedAt

## githubEvents

- deliveryId unique/idempotent

- eventType

- repositoryId

- status

- receivedAt / processedAt

- error

- normalized metadata

## commits

- repositoryId

- sha

- author

- message

- committedAt

- branch

- additions

- deletions

- changedFiles

- files

- status

- createdAt

## commitAnalyses

- commitId

- type

- summary

- problem

- solution

- impact

- technologies

- importance

- publishability

- potentialStory

- embedding if used

- createdAt

## storyClusters

- repositoryId

- relatedCommitIds

- relationship metadata

- updatedAt

## stories

- userId

- repositoryId

- title

- summary

- storyType

- problem

- attempts

- solution

- learning

- impact

- relatedCommitIds

- confidence

- publishability

- status

- detectedAt

## posts

- userId

- storyId

- platform=linkedin

- format

- status

- currentVersionId

- externalPostUrn

- publishedAt

- createdAt

## postVersions

- postId

- version

- title optional

- body

- generationReason

- createdAt

- approvedAt

## socialAccounts

- userId

- provider=linkedin

- providerMemberId / authorUrn as required

- accessTokenEncrypted

- expiresAt

- scopes

- createdAt / updatedAt

## approvalRequests

- userId

- postId

- channel=whatsapp

- status

- currentPostVersionId

- recipientPhone

- kapsoOutboundMessageId

- createdAt / resolvedAt

## approvalMessages

- approvalRequestId

- direction inbound/outbound

- messageId

- content

- interpretedIntent optional

- confidence optional

- createdAt

## activityEvents

- userId

- repositoryId optional

- type

- label

- status

- metadata

- timestamp

# 8. GitHub integration {#github-integration}

- Use a GitHub App, not permanent Personal Access Tokens.

- Initial webhook events: push and pull_request.

- Validate X-Hub-Signature-256.

- Use X-GitHub-Delivery for idempotency.

- Persist a normalized event in Convex and return quickly.

- Do not perform LLM calls inside the webhook request.

- Fetch commit details/diffs from the GitHub REST API during processing.

- Ignore/deprioritize lockfiles, generated files, build artifacts, minified content, vendor directories, and formatting-only changes.

- Do not blindly send huge raw diffs to the LLM. Normalize, prioritize and chunk.

# 9. Convex Python client usage {#convex-python-client-usage}

Convex must be a genuine architectural dependency. The Python backend should use the official Convex Python client for queries, mutations, actions, and documented query subscriptions where appropriate.

from convex import ConvexClient\
\
client = ConvexClient(CONVEX_URL)\
\
client.query(\"\...\")\
client.mutation(\"\...\")\
client.action(\"\...\")\
\
\# Long-running Python services may use documented query subscriptions:\
for result in client.subscribe(\"\...\"):\
\...

- Verify current SDK signatures from official Convex docs before implementation.

- Convex is the source of truth for processing state. Jobs must remain idempotent after service restarts.

- Use Convex React subscriptions for the live dashboard.

# 10. Commit intelligence {#commit-intelligence}

The CommitAnalyzer answers "What happened technically?" It does not write the social post.

class CommitAnalysis(BaseModel):\
type: Literal\[\
\"feature\", \"bugfix\", \"refactor\", \"architecture_change\",\
\"performance\", \"security\", \"developer_experience\",\
\"docs\", \"maintenance\", \"experiment\", \"unknown\"\
\]\
summary: str\
problem: str \| None\
solution: str \| None\
impact: str \| None\
technologies: list\[str\]\
importance: float\
publishability: float\
potential_story: bool

- Use structured outputs validated with Pydantic.

- All scores must be between 0 and 1.

- Never regex-parse arbitrary model prose.

- Do not fabricate business/performance impact.

# 11. Story memory and relationship detection {#story-memory-and-relationship-detection}

Related work must be grouped semantically and structurally. Never group commits simply because they are the latest N commits.

relation_score =\
semantic_similarity\
+ file_overlap\
+ same_pull_request\
+ branch_relationship\
+ temporal_proximity\
+ shared_technologies\
+ inferred_problem_overlap

- Convex vector search may be used on embeddings of normalized commit analyses, not raw diffs.

- Vector similarity is one signal, not the final decision.

- Never mix data across users or unrelated repositories.

# 12. Story Detector {#story-detector}

{\
\"storyDetected\": true,\
\"confidence\": 0.91,\
\"publishability\": 0.88,\
\"storyType\": \"problem_solution\",\
\"title\": \"Why we replaced polling with WebSockets\",\
\"problem\": \"\...\",\
\"attempts\": \[\"\...\"\],\
\"solution\": \"\...\",\
\"learning\": \"\...\",\
\"impact\": \"\...\"\
}

- Create a Story only when evidence supports a coherent narrative.

- High publishability on one commit is not enough.

- Store why relevant work was linked so the UI can explain it.

# 13. LinkedIn-first content generation {#linkedin-first-content-generation}

For this MVP, generate content for LinkedIn only. Keep a clean publisher abstraction, but do not build other social adapters yet.

- Build Log

- Problem → Solution

- Before / After

- Architecture Breakdown

- Failure Story

- Mini Case Study

- The ContentGenerator recommends the best format and explains why.

- Every claim must be supported by repository evidence or clearly presented as a personal learning/interpretation.

- Do not invent metrics, users, revenue, benchmarks, incidents, costs, or production outcomes.

- Maintain post versions so WhatsApp revisions are auditable.

# 14. LinkedIn authentication and publishing {#linkedin-authentication-and-publishing}

Implement real LinkedIn member authentication and posting. Use current official LinkedIn documentation and supported APIs.

- Use LinkedIn OAuth 2.0 (3-legged member authorization).

- Enable Share on LinkedIn and request w_member_social for member publishing.

- If sign-in/profile data is needed, use the current Sign in with LinkedIn using OpenID Connect flow/scopes.

- Use state for CSRF protection and enforce exact redirect URI handling.

- Never store LinkedIn access tokens in frontend/localStorage.

- Encrypt access tokens server-side before persistence; Convex stores only encrypted token material and metadata.

- Retrieve/derive the current member Person URN according to the current official API documentation before creating a post.

- Use the current LinkedIn Posts API for new publishing work. Do not default to deprecated/legacy posting APIs when Posts API is available.

- For MVP, support text-only organic member posts first.

- Persist the external post URN/ID and publish status.

- Do not build r_member_social analytics in the MVP; reading member social data may require restricted access.

draft\
↓\
awaiting_approval\
↓\
approved\
↓\
publishing\
├─→ published\
└─→ failed

# 15. WhatsApp channel via Kapso {#whatsapp-channel-via-kapso}

Kapso is the transport/channel. Proof of Work owns the intelligence. Do not delegate approval decisions to a third-party agent layer.

- Use Kapso to send WhatsApp messages and receive inbound messages.

- Python should call Kapso REST API through httpx unless the current API requires another supported method.

- Subscribe the Kapso webhook to whatsapp.message.received.

- Verify Kapso HMAC SHA-256 signatures against the raw request body using X-Webhook-Signature.

- Use timing-safe comparison.

- Deduplicate deliveries with X-Idempotency-Key persisted in Convex.

- Return HTTP 200 quickly and perform AI/revision work after the webhook response path.

- Store inbound/outbound WhatsApp message IDs and conversation history.

- Respect WhatsApp customer service window rules. When free-form outbound messaging is not allowed, use an approved WhatsApp template through Kapso to initiate/reopen the conversation.

- Keep template logic isolated from normal free-form review messages.

Example outbound review message:\
\
🔥 Encontré una historia que puede funcionar bien en LinkedIn.\
\
"De polling a WebSockets"\
\
Preparé este borrador:\
\
\[POST BODY\]\
\
¿Qué hacemos con esto?\
\
Puedes responder naturalmente:\
- publícalo\
- no\
- hazlo más corto\
- cambia el inicio\
- suena muy corporativo\
- déjalo para después

# 16. Natural-language Approval Agent {#natural-language-approval-agent}

Do not implement a simple yes/no keyword matcher. The user may approve, reject, revise, defer, or ask for clarification in natural language.

class ApprovalDecision(BaseModel):\
intent: Literal\[\
\"approve\",\
\"reject\",\
\"revise\",\
\"clarify\",\
\"hold\"\
\]\
feedback: str \| None\
confidence: float

| User message                                      | Intent  |
|---------------------------------------------------|---------|
| "Ta bueno, publícalo noma"                        | approve |
| "Sí, ahora sí."                                   | approve |
| "Está muy largo, hazlo más corto."                | revise  |
| "Quita esa parte del final y mándamelo de nuevo." | revise  |
| "No publiques eso."                               | reject  |
| "Déjalo para mañana."                             | hold    |
| "Mmm no sé."                                      | clarify |

## Approval safety rules

- Never publish from an ambiguous message.

- Require explicit approval with sufficiently high confidence.

- If confidence is low, ask for clarification on WhatsApp.

- A revision request invalidates any previous approval for the previous version.

- Only the currently approved post version may be published.

- If more than one approval request is pending for the same user, disambiguate instead of guessing.

- A reaction/emoji may only count as approval when context makes intent unambiguous; otherwise clarify.

- Log the exact inbound message that led to approval.

# 17. Revision loop {#revision-loop}

Draft V1\
↓\
WhatsApp\
↓\
User: "Está bueno pero quita el segundo párrafo"\
↓\
Approval Agent → REVISE\
↓\
Content Generator receives:\
- current draft\
- grounded story\
- user feedback\
↓\
Draft V2 stored as a new postVersion\
↓\
WhatsApp sends V2\
↓\
User: "Sí, ahora sí"\
↓\
APPROVE V2\
↓\
LinkedIn Publisher

- Never overwrite previous versions; store versions.

- Revisions must remain grounded in the underlying Story.

- If the user asks to add unsupported facts, ask for missing information rather than inventing it.

# 18. Web dashboard responsibilities {#web-dashboard-responsibilities}

The dashboard is not the primary approval UI. WhatsApp is. The web app exists for visibility, configuration, debugging, history, and manual fallback.

- Connect GitHub

- Connect LinkedIn

- Configure WhatsApp approval number

- Enable/disable repositories

- Live Activity pipeline

- Recent commits and analyses

- Detected stories

- Post drafts and versions

- Approval status

- Published posts

- Retry failed processing/publishing

## Live Activity event examples

github.event.received\
commit.fetch.started\
commit.fetch.completed\
commit.analysis.started\
commit.analysis.completed\
story.search.started\
story.related_work_found\
story.detected\
post.generation.started\
post.generation.completed\
approval.whatsapp.sent\
approval.whatsapp.received\
approval.intent.detected\
post.revision.started\
post.revision.completed\
linkedin.publish.started\
linkedin.publish.completed\
pipeline.failed

# 19. Identity and channel mapping {#identity-and-channel-mapping}

- A Proof of Work user maps to a GitHub installation, a LinkedIn social account, and an approval WhatsApp number.

- Normalize WhatsApp numbers to E.164.

- Do not accept approval from an unrelated phone number.

- Match Kapso inbound messages to the correct user and pending approval request.

- If no matching approval request exists, never publish anything.

- LinkedIn OAuth state must be bound to the same authenticated Proof of Work user.

# 20. Security {#security}

- Verify GitHub webhook signatures.

- Verify Kapso webhook signatures against raw body.

- Implement idempotency for both webhook providers.

- Never expose GitHub private keys, LinkedIn client secret, Kapso API key, OpenAI key, token encryption key, or privileged Convex secrets to the browser.

- Encrypt LinkedIn access tokens before persistence.

- Use timing-safe signature comparisons.

- Validate all external payloads with Pydantic/Zod.

- Do not log secrets or full access tokens.

- Restrict data access by user/repository.

- Use HTTPS for production callbacks/webhooks.

- Explicit human approval is required before LinkedIn publishing.

# 21. Environment variables {#environment-variables}

\# Convex\
CONVEX_URL=\
NEXT_PUBLIC_CONVEX_URL=\
\
\# Application\
APP_URL=\
BACKEND_URL=\
\
\# GitHub App\
GITHUB_APP_ID=\
GITHUB_PRIVATE_KEY=\
GITHUB_WEBHOOK_SECRET=\
\
\# OpenAI\
OPENAI_API_KEY=\
OPENAI_ANALYSIS_MODEL=\
OPENAI_GENERATION_MODEL=\
OPENAI_EMBEDDING_MODEL=\
\
\# LinkedIn\
LINKEDIN_CLIENT_ID=\
LINKEDIN_CLIENT_SECRET=\
LINKEDIN_REDIRECT_URI=\
LINKEDIN_SCOPES=\"openid profile w_member_social\"\
LINKEDIN_API_VERSION=\
TOKEN_ENCRYPTION_KEY=\
\
\# Kapso / WhatsApp\
KAPSO_API_KEY=\
KAPSO_PHONE_NUMBER_ID=\
KAPSO_BUSINESS_ACCOUNT_ID=\
KAPSO_WEBHOOK_SECRET=\
KAPSO_APPROVAL_TEMPLATE_NAME=\
KAPSO_APPROVAL_TEMPLATE_LANGUAGE=\
\
\# Development\
DEMO_MODE=false

- Only add variables the implementation truly needs.

- If LinkedIn current OAuth requirements differ, use the current official requirements and document the adjustment.

- Keep LinkedIn API version configurable.

# 22. Error handling and retries {#error-handling-and-retries}

- Every pipeline stage exposes a visible status.

- Failed GitHub analysis is retryable without duplicate commits.

- Failed Kapso webhook processing remains idempotent.

- Failed WhatsApp send does not mark approval as sent.

- Failed LinkedIn publishing preserves the approved draft and can be retried.

- Never auto-regenerate and publish a different version after a publishing failure.

- Store concise diagnostic errors and relevant identifiers.

# 23. Testing priorities {#testing-priorities}

- GitHub webhook signature validation

- GitHub delivery idempotency

- duplicate commit handling

- diff normalization / noisy file filtering

- Pydantic CommitAnalysis validation

- story relationship scoring

- StoryDetector structured output

- Kapso raw-body HMAC validation

- Kapso idempotency

- mapping inbound phone → correct approval request

- ApprovalAgent intent classification

- ambiguous approval must NOT publish

- revision invalidates previous approval

- LinkedIn OAuth state validation

- LinkedIn token encryption/decryption

- Publisher executes only for explicitly approved current version

- LinkedIn publish failure / retry behavior

# 24. Demo mode {#demo-mode}

Demo story fixture:\
\
1. feat: add notification polling\
2. fix: prevent duplicate notification requests\
3. refactor: replace polling with websocket events\
\
Expected:\
→ one related story cluster\
→ one Story\
→ one LinkedIn draft\
→ one WhatsApp approval request

- Do not hardcode the final story/post into the frontend.

- Run fixtures through the same internal abstractions wherever possible.

- Support a safe mock LinkedIn publisher for local tests while keeping the real publisher for the final demo.

# 25. Implementation milestones {#implementation-milestones}

## MILESTONE 0 --- Foundation {#milestone-0-foundation}

- Inspect current repository.

- Create monorepo structure.

- Set up Next.js, FastAPI, Convex, pnpm/uv, linting, tests, .env.example.

- Acceptance: frontend, backend, and Convex run successfully.

## MILESTONE 1 --- GitHub → Convex {#milestone-1-github-convex}

- GitHub App webhook endpoint, signature validation, delivery idempotency.

- Store GitHubEvent in Convex.

- Acceptance: a real push appears in Convex.

## MILESTONE 2 --- Commit extraction {#milestone-2-commit-extraction}

- Fetch commit/diff, normalize files, store Commit.

- Acceptance: dashboard shows changed files/additions/deletions.

## MILESTONE 3 --- Live Activity {#milestone-3-live-activity}

- activityEvents in Convex + reactive Next.js UI.

- Acceptance: statuses change without refresh.

## MILESTONE 4 --- Commit intelligence {#milestone-4-commit-intelligence}

- CommitAnalyzer with structured outputs.

- Acceptance: a commit produces a valid CommitAnalysis.

## MILESTONE 5 --- Story memory {#milestone-5-story-memory}

- Embeddings/vector search where useful + relationship scoring + clusters.

- Acceptance: related commits are retrieved correctly.

## MILESTONE 6 --- Story detection {#milestone-6-story-detection}

- StoryDetector.

- Acceptance: polling → WebSockets fixture becomes one coherent Story.

## MILESTONE 7 --- LinkedIn connection {#milestone-7-linkedin-connection}

- OAuth route/callback, secure token storage, member identity/Person URN retrieval.

- Acceptance: user sees LinkedIn account as connected.

## MILESTONE 8 --- LinkedIn content generation {#milestone-8-linkedin-content-generation}

- Generate LinkedIn draft + recommended format + post versions.

- Acceptance: detected Story creates grounded Draft V1.

## MILESTONE 9 --- Kapso outbound/inbound {#milestone-9-kapso-outboundinbound}

- Send draft through Kapso; register/handle whatsapp.message.received webhook.

- Signature validation + idempotency.

- Acceptance: user receives draft and backend receives reply.

## MILESTONE 10 --- Approval Agent + revisions {#milestone-10-approval-agent-revisions}

- approve/reject/revise/clarify/hold intents.

- Revision loop and WhatsApp resend.

- Acceptance: "hazlo más corto" produces V2; "sí, ahora sí" approves V2.

## MILESTONE 11 --- Real LinkedIn publishing {#milestone-11-real-linkedin-publishing}

- Publish only approved current post version through current Posts API.

- Persist post URN/ID and status.

- Acceptance: approved WhatsApp reply results in a real LinkedIn post.

## MILESTONE 12 --- Demo polish {#milestone-12-demo-polish}

- Onboarding, live activity clarity, story explanation, error states, demo fixtures.

- Acceptance: full flow runs reliably in front of judges.

# 26. Hackathon definition of done {#hackathon-definition-of-done}

1.  User connects GitHub.

2.  User connects LinkedIn.

3.  User configures their WhatsApp approval number.

4.  User performs Git activity.

5.  GitHub sends webhook.

6.  FastAPI validates and persists event in Convex.

7.  Python fetches and normalizes the commit.

8.  CommitAnalyzer understands the technical change.

9.  Related prior work is found.

10. StoryDetector identifies a meaningful Story.

11. ContentGenerator creates a LinkedIn draft.

12. Convex updates the dashboard live.

13. Kapso sends the draft to WhatsApp.

14. User replies in natural language.

15. ApprovalAgent detects intent.

16. If revise: a new version is generated and resent.

17. If reject: nothing is published.

18. If ambiguous: the agent asks for clarification.

19. If explicit approve: the approved current version is published to LinkedIn.

20. Proof of Work stores the external post ID/URN.

21. WhatsApp confirms successful publication.

# 27. Non-goals for the MVP {#non-goals-for-the-mvp}

- Other social networks besides LinkedIn

- LinkedIn analytics / r_member_social

- Automatic publishing without human approval

- Enterprise teams / RBAC

- Billing

- Content calendars

- Complex scheduling

- Multiple WhatsApp providers

- General-purpose conversational agent platform

- LangGraph/LangChain orchestration

- Kafka/Redis/microservices

- Full media/video/document publishing unless the core flow is complete

# 28. Non-negotiable product rules {#non-negotiable-product-rules}

**1.** Evidence before content.

**2.** Never one post per commit by default.

**3.** Stories may span multiple commits and PRs.

**4.** Explain why a story was detected.

**5.** Never invent claims.

**6.** LinkedIn is the only publishing target in this MVP.

**7.** WhatsApp via Kapso is the primary validation interface.

**8.** Natural-language revision is a first-class feature.

**9.** No ambiguous message can trigger publishing.

**10.** Every revision creates a new post version.

**11.** Only the explicitly approved current version may be published.

**12.** Convex is the source of truth and powers realtime UI.

**13.** Python + Convex Python client must be genuinely used.

**14.** Kapso is the channel; Proof of Work owns approval intelligence.

**15.** Keep the MVP finishable.

# 29. First task for Codex {#first-task-for-codex}

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr>
<th><p><strong>BEGIN EXECUTION</strong></p>
<p>Inspect the current repository first. Summarize its state, identify blockers, and list the exact files/modules you will create. Then immediately implement Milestone 0 and continue sequentially without waiting for approval unless a real credential/manual third-party step blocks you.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

First major vertical slice:

git push\
↓\
GitHub webhook\
↓\
FastAPI\
↓\
Convex\
↓\
commit fetched\
↓\
dashboard updates live

Then continue toward the complete product loop:

GitHub\
↓\
Story\
↓\
LinkedIn draft\
↓\
Kapso / WhatsApp\
↓\
Natural-language approval or revision\
↓\
LinkedIn publish

# 30. Official documentation to verify during implementation {#official-documentation-to-verify-during-implementation}

**Convex Python client:** https://docs.convex.dev/client/python

**Convex Python quickstart:** https://docs.convex.dev/quickstart/python

**LinkedIn API access / permissions:** https://learn.microsoft.com/en-us/linkedin/shared/authentication/getting-access

**LinkedIn Sign In with OpenID Connect:** https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/sign-in-with-linkedin-v2

**LinkedIn Posts API:** https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api

**Kapso introduction:** https://docs.kapso.ai/docs/introduction

**Kapso send text:** https://docs.kapso.ai/docs/whatsapp/send-messages/text

**Kapso webhooks overview:** https://docs.kapso.ai/docs/platform/webhooks/overview

**Kapso webhook security:** https://docs.kapso.ai/docs/platform/webhooks/security

**Kapso templates:** https://docs.kapso.ai/docs/whatsapp/typescript-sdk/templates

External APIs change. Treat these URLs as starting points and use the current documented endpoints, headers, versions, scopes, and webhook payloads at implementation time.
