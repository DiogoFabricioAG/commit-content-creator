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
    .index("by_github_repository", ["githubRepositoryId"]),

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
    metadata: v.optional(
      v.object({
        entityId: v.optional(v.string()),
        detail: v.optional(v.string()),
      }),
    ),
    timestamp: v.number(),
  }).index("by_user_timestamp", ["userId", "timestamp"]),
});
