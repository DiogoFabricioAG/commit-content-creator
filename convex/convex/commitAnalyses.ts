import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

export const record = mutation({
  args: {
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
  },
  handler: async (ctx, args) => {
    const existing = await ctx.db
      .query("commitAnalyses")
      .withIndex("by_commit", (q) => q.eq("commitId", args.commitId))
      .first();

    if (existing) {
      await ctx.db.patch(existing._id, {
        ...args,
      });
      return existing._id;
    }

    return await ctx.db.insert("commitAnalyses", {
      ...args,
      createdAt: Date.now(),
    });
  },
});

export const getByCommitId = query({
  args: { commitId: v.id("commits") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("commitAnalyses")
      .withIndex("by_commit", (q) => q.eq("commitId", args.commitId))
      .first();
  },
});

export const listForRepository = query({
  args: {
    repositoryId: v.id("repositories"),
    limit: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("commitAnalyses")
      .withIndex("by_repository", (q) => q.eq("repositoryId", args.repositoryId))
      .order("desc")
      .take(args.limit ?? 50);
  },
});
