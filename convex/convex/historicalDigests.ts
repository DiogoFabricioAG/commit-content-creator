import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

const digestStatus = v.union(
  v.literal("building"),
  v.literal("awaiting_approval"),
  v.literal("completed"),
  v.literal("failed"),
);

export const reserve = mutation({
  args: {
    userId: v.id("users"),
    repositoryId: v.id("repositories"),
    repositoryFullName: v.string(),
    branch: v.optional(v.string()),
    fingerprint: v.string(),
  },
  handler: async (ctx, args) => {
    const user = await ctx.db.get(args.userId);
    const repository = await ctx.db.get(args.repositoryId);
    if (!user || !repository || repository.userId !== args.userId) {
      throw new Error("Unauthorized: digest does not belong to this user");
    }

    const existing = await ctx.db
      .query("historicalDigests")
      .withIndex("by_user_fingerprint", (q) =>
        q.eq("userId", args.userId).eq("fingerprint", args.fingerprint),
      )
      .first();

    if (existing && existing.status !== "failed") {
      return {
        digestId: existing._id,
        existing: true,
        status: existing.status,
      };
    }

    const now = Date.now();
    if (existing) {
      await ctx.db.patch(existing._id, {
        repositoryFullName: args.repositoryFullName,
        branch: args.branch,
        status: "building",
        includedCommitShas: [],
        filteredCommitShas: [],
        storyId: undefined,
        postId: undefined,
        approvalRequestId: undefined,
        title: undefined,
        summary: undefined,
        error: undefined,
        updatedAt: now,
      });
      return { digestId: existing._id, existing: false, status: "building" };
    }

    const digestId = await ctx.db.insert("historicalDigests", {
      ...args,
      status: "building",
      includedCommitShas: [],
      filteredCommitShas: [],
      createdAt: now,
      updatedAt: now,
    });
    return { digestId, existing: false, status: "building" };
  },
});

export const complete = mutation({
  args: {
    digestId: v.id("historicalDigests"),
    includedCommitShas: v.array(v.string()),
    filteredCommitShas: v.array(v.string()),
    storyId: v.id("stories"),
    postId: v.id("posts"),
    approvalRequestId: v.id("approvalRequests"),
    title: v.string(),
    summary: v.string(),
    status: digestStatus,
  },
  handler: async (ctx, args) => {
    const digest = await ctx.db.get(args.digestId);
    if (!digest) throw new Error("Digest not found");
    await ctx.db.patch(args.digestId, {
      includedCommitShas: args.includedCommitShas,
      filteredCommitShas: args.filteredCommitShas,
      storyId: args.storyId,
      postId: args.postId,
      approvalRequestId: args.approvalRequestId,
      title: args.title,
      summary: args.summary,
      status: args.status,
      updatedAt: Date.now(),
    });
  },
});

export const fail = mutation({
  args: {
    digestId: v.id("historicalDigests"),
    error: v.string(),
  },
  handler: async (ctx, args) => {
    const digest = await ctx.db.get(args.digestId);
    if (!digest) throw new Error("Digest not found");
    await ctx.db.patch(args.digestId, {
      status: "failed",
      error: args.error.slice(0, 1000),
      updatedAt: Date.now(),
    });
  },
});

export const getByIdForUser = query({
  args: {
    digestId: v.id("historicalDigests"),
    userId: v.id("users"),
  },
  handler: async (ctx, args) => {
    const digest = await ctx.db.get(args.digestId);
    if (!digest || digest.userId !== args.userId) return null;
    return digest;
  },
});

export const listForUser = query({
  args: {
    userId: v.id("users"),
    limit: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("historicalDigests")
      .withIndex("by_user_updated_at", (q) => q.eq("userId", args.userId))
      .order("desc")
      .take(args.limit ?? 10);
  },
});
