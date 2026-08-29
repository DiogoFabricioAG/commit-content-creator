import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

export const record = mutation({
  args: {
    repositoryId: v.id("repositories"),
    relatedCommitIds: v.array(v.id("commits")),
    relationshipMetadata: v.optional(
      v.object({
        reason: v.optional(v.string()),
        score: v.optional(v.number()),
      }),
    ),
  },
  handler: async (ctx, args) => {
    const clusterId = await ctx.db.insert("storyClusters", {
      repositoryId: args.repositoryId,
      relatedCommitIds: args.relatedCommitIds,
      relationshipMetadata: args.relationshipMetadata,
      updatedAt: Date.now(),
    });
    return clusterId;
  },
});

export const listForRepository = query({
  args: { repositoryId: v.id("repositories") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("storyClusters")
      .withIndex("by_repository", (q) => q.eq("repositoryId", args.repositoryId))
      .collect();
  },
});
