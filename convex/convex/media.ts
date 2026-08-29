import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

export const generateUploadUrl = mutation({
  args: {},
  handler: async (ctx) => {
    return await ctx.storage.generateUploadUrl();
  },
});

export const getUrl = query({
  args: { storageId: v.id("_storage") },
  handler: async (ctx, args) => {
    return await ctx.storage.getUrl(args.storageId);
  },
});

export const record = mutation({
  args: {
    postVersionId: v.id("postVersions"),
    kind: v.union(v.literal("image"), v.literal("video"), v.literal("architecture")),
    storageId: v.id("_storage"),
    mimeType: v.string(),
    url: v.optional(v.string()),
    altText: v.string(),
    source: v.string(),
    prompt: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("mediaAssets", {
      ...args,
      createdAt: Date.now(),
    });
  },
});

export const listForPostVersion = query({
  args: { postVersionId: v.id("postVersions") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("mediaAssets")
      .withIndex("by_post_version", (q) => q.eq("postVersionId", args.postVersionId))
      .order("asc")
      .collect();
  },
});
