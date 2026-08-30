import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

const eventStatus = v.union(
  v.literal("received"),
  v.literal("processing"),
  v.literal("processed"),
  v.literal("failed"),
);

const commitStatus = v.union(
  v.literal("fetched"),
  v.literal("analyzing"),
  v.literal("analyzed"),
  v.literal("ignored"),
  v.literal("failed"),
);

export default defineSchema({
  users: defineTable({
    displayName: v.optional(v.string()),
    email: v.optional(v.string()),
    whatsappPhone: v.optional(v.string()),
    createdAt: v.number(),
    updatedAt: v.number(),
  }).index("by_whatsapp_phone", ["whatsappPhone"]),

  githubInstallations: defineTable({
    userId: v.id("users"),
    githubInstallationId: v.string(),
    accountLogin: v.string(),
    accountType: v.union(v.literal("User"), v.literal("Organization")),
    createdAt: v.number(),
  }).index("by_user", ["userId"]),

  repositories: defineTable({
    userId: v.id("users"),
    installationId: v.id("githubInstallations"),
    githubRepositoryId: v.string(),
    owner: v.string(),
    name: v.string(),
    fullName: v.string(),
    defaultBranch: v.string(),
    enabled: v.boolean(),
    createdAt: v.number(),
    updatedAt: v.number(),
  })
    .index("by_user", ["userId"])
    .index("by_user_full_name", ["userId", "fullName"])
    .index("by_github_repository", ["githubRepositoryId"])
    .index("by_full_name", ["fullName"]),

  githubEvents: defineTable({
    deliveryId: v.string(),
    eventType: v.union(v.literal("push"), v.literal("pull_request")),
    repositoryId: v.optional(v.id("repositories")),
    status: eventStatus,
    receivedAt: v.number(),
    processedAt: v.optional(v.number()),
    error: v.optional(v.string()),
    metadata: v.object({
      repositoryFullName: v.optional(v.string()),
      branch: v.optional(v.string()),
      commitShas: v.optional(v.array(v.string())),
      action: v.optional(v.string()),
    }),
  })
    .index("by_delivery_id", ["deliveryId"])
    .index("by_repository", ["repositoryId"]),

  commits: defineTable({
    repositoryId: v.id("repositories"),
    sha: v.string(),
    author: v.string(),
    message: v.string(),
    committedAt: v.number(),
    branch: v.optional(v.string()),
    additions: v.number(),
    deletions: v.number(),
    changedFiles: v.number(),
    files: v.array(
      v.object({
        path: v.string(),
        status: v.string(),
        additions: v.number(),
        deletions: v.number(),
        patch: v.optional(v.string()),
      }),
    ),
    status: commitStatus,
    createdAt: v.number(),
  })
    .index("by_repository_sha", ["repositoryId", "sha"])
    .index("by_repository_created_at", ["repositoryId", "createdAt"]),

  commitAnalyses: defineTable({
    commitId: v.id("commits"),
    repositoryId: v.id("repositories"),
    type: v.string(),
    summary: v.string(),
    problem: v.optional(v.string()),
    solution: v.optional(v.string()),
    impact: v.optional(v.string()),
    technologies: v.array(v.string()),
    importance: v.number(),
    publishability: v.number(),
    potentialStory: v.boolean(),
    createdAt: v.number(),
  })
    .index("by_commit", ["commitId"])
    .index("by_repository", ["repositoryId"]),

  storyClusters: defineTable({
    repositoryId: v.id("repositories"),
    relatedCommitIds: v.array(v.id("commits")),
    relationshipMetadata: v.optional(
      v.object({
        reason: v.optional(v.string()),
        score: v.optional(v.number()),
      }),
    ),
    updatedAt: v.number(),
  }).index("by_repository", ["repositoryId"]),

  stories: defineTable({
    userId: v.id("users"),
    repositoryId: v.id("repositories"),
    title: v.string(),
    summary: v.string(),
    storyType: v.string(),
    problem: v.optional(v.string()),
    attempts: v.optional(v.array(v.string())),
    solution: v.optional(v.string()),
    learning: v.optional(v.string()),
    impact: v.optional(v.string()),
    relatedCommitIds: v.array(v.id("commits")),
    confidence: v.number(),
    publishability: v.number(),
    status: v.union(
      v.literal("detected"),
      v.literal("drafted"),
      v.literal("approved"),
      v.literal("published"),
      v.literal("rejected"),
      v.literal("archived"),
    ),
    detectedAt: v.number(),
  })
    .index("by_user", ["userId"])
    .index("by_repository", ["repositoryId"]),

  posts: defineTable({
    userId: v.id("users"),
    storyId: v.id("stories"),
    platform: v.literal("linkedin"),
    format: v.string(),
    status: v.union(
      v.literal("draft"),
      v.literal("awaiting_approval"),
      v.literal("approved"),
      v.literal("publishing"),
      v.literal("published"),
      v.literal("failed"),
      v.literal("rejected"),
    ),
    currentVersionId: v.optional(v.id("postVersions")),
    externalPostUrn: v.optional(v.string()),
    publishedAt: v.optional(v.number()),
    createdAt: v.number(),
  })
    .index("by_user", ["userId"])
    .index("by_story", ["storyId"]),

  postVersions: defineTable({
    postId: v.id("posts"),
    version: v.number(),
    title: v.optional(v.string()),
    body: v.string(),
    generationReason: v.optional(v.string()),
    createdAt: v.number(),
    approvedAt: v.optional(v.number()),
  })
    .index("by_post", ["postId"])
    .index("by_post_version", ["postId", "version"]),

  mediaAssets: defineTable({
    postVersionId: v.id("postVersions"),
    kind: v.union(v.literal("image"), v.literal("video"), v.literal("architecture")),
    storageId: v.id("_storage"),
    mimeType: v.string(),
    url: v.optional(v.string()),
    altText: v.string(),
    source: v.string(),
    prompt: v.optional(v.string()),
    createdAt: v.number(),
  }).index("by_post_version", ["postVersionId"]),

  socialAccounts: defineTable({
    userId: v.id("users"),
    provider: v.literal("linkedin"),
    providerMemberId: v.optional(v.string()),
    authorUrn: v.optional(v.string()),
    accessTokenEncrypted: v.string(),
    expiresAt: v.optional(v.number()),
    scopes: v.array(v.string()),
    createdAt: v.number(),
    updatedAt: v.number(),
  }).index("by_user_provider", ["userId", "provider"]),

  approvalRequests: defineTable({
    userId: v.id("users"),
    postId: v.id("posts"),
    channel: v.literal("whatsapp"),
    status: v.union(
      v.literal("pending"),
      v.literal("approved"),
      v.literal("revised"),
      v.literal("rejected"),
      v.literal("clarify"),
      v.literal("hold"),
    ),
    currentPostVersionId: v.id("postVersions"),
    recipientPhone: v.string(),
    kapsoOutboundMessageId: v.optional(v.string()),
    createdAt: v.number(),
    resolvedAt: v.optional(v.number()),
  })
    .index("by_user", ["userId"])
    .index("by_phone_status", ["recipientPhone", "status"])
    .index("by_post", ["postId"]),

  whatsappSessions: defineTable({
    userId: v.id("users"),
    phone: v.string(),
    openedAt: v.number(),
    lastInboundAt: v.number(),
    lastInboundMessageId: v.string(),
    expiresAt: v.number(),
  })
    .index("by_phone", ["phone"])
    .index("by_user", ["userId"]),

  approvalMessages: defineTable({
    approvalRequestId: v.id("approvalRequests"),
    direction: v.union(v.literal("inbound"), v.literal("outbound")),
    messageId: v.string(),
    content: v.string(),
    interpretedIntent: v.optional(v.string()),
    confidence: v.optional(v.number()),
    createdAt: v.number(),
  })
    .index("by_request", ["approvalRequestId"])
    .index("by_message_id", ["messageId"]),

  activityEvents: defineTable({
    userId: v.id("users"),
    repositoryId: v.optional(v.id("repositories")),
    type: v.string(),
    label: v.string(),
    status: v.union(
      v.literal("started"),
      v.literal("completed"),
      v.literal("failed"),
      v.literal("waiting"),
    ),
    metadata: v.optional(v.any()),
    timestamp: v.number(),
  }).index("by_user_timestamp", ["userId", "timestamp"]),

  userPreferences: defineTable({
    userId: v.id("users"),
    roleTitle: v.optional(v.string()),
    language: v.union(v.literal("es"), v.literal("en"), v.literal("pt")),
    tone: v.union(
      v.literal("humble_builder"),
      v.literal("deep_technical"),
      v.literal("direct_minimal"),
      v.literal("storyteller"),
    ),
    targetAudience: v.union(
      v.literal("senior_engineers"),
      v.literal("tech_founders"),
      v.literal("recruiters"),
      v.literal("general_tech"),
    ),
    technicalLevel: v.union(v.literal("high"), v.literal("medium"), v.literal("accessible")),
    postLength: v.union(v.literal("concise"), v.literal("standard"), v.literal("deep_dive")),
    avoidWords: v.array(v.string()),
    preferredCTA: v.union(
      v.literal("discussion_question"),
      v.literal("github_link"),
      v.literal("lesson_takeaway"),
      v.literal("none"),
    ),
    hashtags: v.array(v.string()),
    allowedFormats: v.array(v.string()),
    autoPublish: v.boolean(),
    onboardingCompleted: v.boolean(),
    createdAt: v.number(),
    updatedAt: v.number(),
  }).index("by_user", ["userId"]),
});
