import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

const activityStatus = v.union(
  v.literal("started"),
  v.literal("completed"),
  v.literal("failed"),
  v.literal("waiting"),
);

export const record = mutation({
  args: {
    userId: v.id("users"),
    repositoryId: v.optional(v.id("repositories")),
    type: v.string(),
    label: v.string(),
    status: activityStatus,
    metadata: v.optional(v.any()),
  },
  handler: async (ctx, args) => {
    const user = await ctx.db.get(args.userId);
    if (!user) {
      throw new Error("Unauthorized: Invalid or non-existent userId");
    }

    return await ctx.db.insert("activityEvents", {
      ...args,
      timestamp: Date.now(),
    });
  },
});

export const listRecent = query({
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
      .query("activityEvents")
      .withIndex("by_user_timestamp", (q) => q.eq("userId", args.userId))
      .order("desc")
      .take(args.limit ?? 50);
  },
});
