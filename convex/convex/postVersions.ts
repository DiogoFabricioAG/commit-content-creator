import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

export const record = mutation({
  args: {
    postId: v.id("posts"),
    version: v.number(),
    title: v.optional(v.string()),
    body: v.string(),
    generationReason: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const versionId = await ctx.db.insert("postVersions", {
      ...args,
      createdAt: Date.now(),
    });

    // Update parent post with current version
    await ctx.db.patch(args.postId, {
      currentVersionId: versionId,
    });

    return versionId;
  },
});

export const getLatestForPost = query({
  args: { postId: v.id("posts") },
  handler: async (ctx, args) => {
    const versions = await ctx.db
      .query("postVersions")
      .withIndex("by_post", (q) => q.eq("postId", args.postId))
      .order("desc")
      .first();
    return versions;
  },
});

export const listForPost = query({
  args: { postId: v.id("posts") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("postVersions")
      .withIndex("by_post", (q) => q.eq("postId", args.postId))
      .order("asc")
      .collect();
  },
});

export const approve = mutation({
  args: {
    versionId: v.id("postVersions"),
  },
  handler: async (ctx, args) => {
    const now = Date.now();
    await ctx.db.patch(args.versionId, {
      approvedAt: now,
    });
  },
});
