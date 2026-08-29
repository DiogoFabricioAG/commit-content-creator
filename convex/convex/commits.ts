import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

const commitStatus = v.union(
  v.literal("fetched"),
  v.literal("analyzing"),
  v.literal("analyzed"),
  v.literal("ignored"),
  v.literal("failed"),
);

const commitFile = v.object({
  path: v.string(),
  status: v.string(),
  additions: v.number(),
  deletions: v.number(),
  patch: v.optional(v.string()),
});

export const record = mutation({
  args: {
    repositoryId: v.id("repositories"),
    sha: v.string(),
    author: v.string(),
    message: v.string(),
    committedAt: v.number(),
    branch: v.optional(v.string()),
    additions: v.number(),
    deletions: v.number(),
    changedFiles: v.number(),
    files: v.array(commitFile),
    status: commitStatus,
  },
  handler: async (ctx, args) => {
    const existing = await ctx.db
      .query("commits")
      .withIndex("by_repository_sha", (q) =>
        q.eq("repositoryId", args.repositoryId).eq("sha", args.sha),
      )
      .unique();

    if (existing) {
      return { commitId: existing._id, duplicate: true };
    }

    const commitId = await ctx.db.insert("commits", {
      ...args,
      createdAt: Date.now(),
    });

    return { commitId, duplicate: false };
  },
});

export const listForRepository = query({
  args: {
    repositoryId: v.id("repositories"),
    limit: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("commits")
      .withIndex("by_repository_created_at", (q) => q.eq("repositoryId", args.repositoryId))
      .order("desc")
      .take(args.limit ?? 50);
  },
});

export const listByIds = query({
  args: {
    commitIds: v.array(v.id("commits")),
  },
  handler: async (ctx, args) => {
    const commits = [];
    for (const commitId of args.commitIds) {
      const commit = await ctx.db.get(commitId);
      if (commit) commits.push(commit);
    }
    return commits;
  },
});
