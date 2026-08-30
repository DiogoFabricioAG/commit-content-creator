import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

const storyStatus = v.union(
  v.literal("detected"),
  v.literal("drafted"),
  v.literal("approved"),
  v.literal("published"),
  v.literal("rejected"),
  v.literal("archived"),
);

export const record = mutation({
  args: {
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
    status: storyStatus,
  },
  handler: async (ctx, args) => {
    const user = await ctx.db.get(args.userId);
    if (!user) {
      throw new Error("Unauthorized: Invalid or non-existent userId");
    }

    return await ctx.db.insert("stories", {
      ...args,
      detectedAt: Date.now(),
    });
  },
});

export const getById = query({
  args: { storyId: v.id("stories") },
  handler: async (ctx, args) => {
    return await ctx.db.get(args.storyId);
  },
});

export const getByIdForUser = query({
  args: {
    storyId: v.id("stories"),
    userId: v.id("users"),
  },
  handler: async (ctx, args) => {
    const story = await ctx.db.get(args.storyId);
    if (!story || story.userId !== args.userId) {
      return null;
    }
    return story;
  },
});

export const listForUser = query({
  args: {
    userId: v.id("users"),
    limit: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    const user = await ctx.db.get(args.userId);
    if (!user) {
      return [];
    }

    return await ctx.db
      .query("stories")
      .withIndex("by_user", (q) => q.eq("userId", args.userId))
      .order("desc")
      .take(args.limit ?? 50);
  },
});

export const updateStatus = mutation({
  args: {
    storyId: v.id("stories"),
    status: storyStatus,
  },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.storyId, { status: args.status });
  },
});
