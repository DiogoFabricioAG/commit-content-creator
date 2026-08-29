import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

export const getOrCreateForUser = mutation({
  args: {
    userId: v.id("users"),
    fullName: v.string(),
    defaultBranch: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const existing = await ctx.db
      .query("repositories")
      .withIndex("by_full_name", (q) => q.eq("fullName", args.fullName))
      .first();

    if (existing) {
      return existing._id;
    }

    // Get or create dummy installation
    let installation = await ctx.db
      .query("githubInstallations")
      .withIndex("by_user", (q) => q.eq("userId", args.userId))
      .first();

    if (!installation) {
      const parts = args.fullName.split("/");
      const owner = parts[0] || "owner";
      const installationId = await ctx.db.insert("githubInstallations", {
        userId: args.userId,
        githubInstallationId: "inst_default_01",
        accountLogin: owner,
        accountType: "User",
        createdAt: Date.now(),
      });
      installation = await ctx.db.get(installationId);
    }

    const parts = args.fullName.split("/");
    const owner = parts[0] || "owner";
    const name = parts[1] || "repo";
    const now = Date.now();

    return await ctx.db.insert("repositories", {
      userId: args.userId,
      installationId: installation!._id,
      githubRepositoryId: `gh_repo_${owner}_${name}`,
      owner,
      name,
      fullName: args.fullName,
      defaultBranch: args.defaultBranch ?? "main",
      enabled: true,
      createdAt: now,
      updatedAt: now,
    });
  },
});

export const getByFullName = query({
  args: { fullName: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("repositories")
      .withIndex("by_full_name", (q) => q.eq("fullName", args.fullName))
      .first();
  },
});

export const getById = query({
  args: { repositoryId: v.id("repositories") },
  handler: async (ctx, args) => {
    return await ctx.db.get(args.repositoryId);
  },
});

export const listForUser = query({
  args: { userId: v.id("users") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("repositories")
      .withIndex("by_user", (q) => q.eq("userId", args.userId))
      .collect();
  },
});
