import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

const postStatus = v.union(
  v.literal("draft"),
  v.literal("awaiting_approval"),
  v.literal("approved"),
  v.literal("publishing"),
  v.literal("published"),
  v.literal("failed"),
  v.literal("rejected"),
);

export const record = mutation({
  args: {
    userId: v.id("users"),
    storyId: v.id("stories"),
    platform: v.literal("linkedin"),
    format: v.string(),
    status: postStatus,
  },
  handler: async (ctx, args) => {
    const user = await ctx.db.get(args.userId);
    if (!user) {
      throw new Error("Unauthorized: Invalid or non-existent userId");
    }

    return await ctx.db.insert("posts", {
      ...args,
      createdAt: Date.now(),
    });
  },
});

export const getById = query({
  args: { postId: v.id("posts") },
  handler: async (ctx, args) => {
    return await ctx.db.get(args.postId);
  },
});

export const getByIdForUser = query({
  args: {
    postId: v.id("posts"),
    userId: v.id("users"),
  },
  handler: async (ctx, args) => {
    const post = await ctx.db.get(args.postId);
    if (!post || post.userId !== args.userId) {
      return null;
    }
    return post;
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
      .query("posts")
      .withIndex("by_user", (q) => q.eq("userId", args.userId))
      .order("desc")
      .take(args.limit ?? 50);
  },
});

export const updateStatus = mutation({
  args: {
    postId: v.id("posts"),
    status: postStatus,
    currentVersionId: v.optional(v.id("postVersions")),
  },
  handler: async (ctx, args) => {
    const patch: {
      status: typeof args.status;
      currentVersionId?: typeof args.currentVersionId;
    } = { status: args.status };
    if (args.currentVersionId) {
      patch.currentVersionId = args.currentVersionId;
    }
    await ctx.db.patch(args.postId, patch);
  },
});

export const setExternalUrn = mutation({
  args: {
    postId: v.id("posts"),
    externalPostUrn: v.string(),
    status: postStatus,
  },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.postId, {
      externalPostUrn: args.externalPostUrn,
      status: args.status,
      publishedAt: Date.now(),
    });
  },
});
