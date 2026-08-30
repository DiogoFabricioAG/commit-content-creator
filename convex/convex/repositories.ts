import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

export const getOrCreateForUser = mutation({
  args: {
    userId: v.id("users"),
    fullName: v.string(),
    defaultBranch: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    // 1. Authorize: verify user exists in tenant storage
    const user = await ctx.db.get(args.userId);
    if (!user) {
      throw new Error("Unauthorized: Invalid or non-existent userId");
    }

    const trimmedFullName = args.fullName.trim();
    if (!trimmedFullName || !trimmedFullName.includes("/")) {
      throw new Error("Invalid repository format: Expected 'owner/repo'");
    }

    // 2. Multi-tenant isolation: check if this repository is already registered for THIS user
    const existingForUser = await ctx.db
      .query("repositories")
      .withIndex("by_user_full_name", (q) =>
        q.eq("userId", args.userId).eq("fullName", trimmedFullName),
      )
      .first();

    if (existingForUser) {
      if (!existingForUser.enabled) {
        await ctx.db.patch(existingForUser._id, {
          enabled: true,
          updatedAt: Date.now(),
        });
      }
      return existingForUser._id;
    }

    // 3. Resolve or create GitHub installation for this user
    const parts = trimmedFullName.split("/");
    const owner = parts[0] || "owner";
    const name = parts[1] || "repo";

    let installation = await ctx.db
      .query("githubInstallations")
      .withIndex("by_user", (q) => q.eq("userId", args.userId))
      .first();

    if (!installation) {
      const installationId = await ctx.db.insert("githubInstallations", {
        userId: args.userId,
        githubInstallationId: `inst_${args.userId.slice(-6)}_${Date.now()}`,
        accountLogin: owner,
        accountType: "User",
        createdAt: Date.now(),
      });
      installation = await ctx.db.get(installationId);
    }

    const now = Date.now();

    return await ctx.db.insert("repositories", {
      userId: args.userId,
      installationId: installation!._id,
      githubRepositoryId: `gh_repo_${owner}_${name}`,
      owner,
      name,
      fullName: trimmedFullName,
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
    const trimmed = args.fullName.trim();
    return await ctx.db
      .query("repositories")
      .withIndex("by_full_name", (q) => q.eq("fullName", trimmed))
      .filter((q) => q.eq(q.field("enabled"), true))
      .first();
  },
});

export const listByFullName = query({
  args: { fullName: v.string() },
  handler: async (ctx, args) => {
    const trimmed = args.fullName.trim();
    return await ctx.db
      .query("repositories")
      .withIndex("by_full_name", (q) => q.eq("fullName", trimmed))
      .collect();
  },
});

export const getById = query({
  args: { repositoryId: v.id("repositories") },
  handler: async (ctx, args) => {
    return await ctx.db.get(args.repositoryId);
  },
});

export const getByIdForUser = query({
  args: {
    repositoryId: v.id("repositories"),
    userId: v.id("users"),
  },
  handler: async (ctx, args) => {
    const repo = await ctx.db.get(args.repositoryId);
    if (!repo || repo.userId !== args.userId) {
      return null;
    }
    return repo;
  },
});

export const listForUser = query({
  args: { userId: v.id("users") },
  handler: async (ctx, args) => {
    const user = await ctx.db.get(args.userId);
    if (!user) {
      return [];
    }

    return await ctx.db
      .query("repositories")
      .withIndex("by_user", (q) => q.eq("userId", args.userId))
      .filter((q) => q.eq(q.field("enabled"), true))
      .collect();
  },
});

export const removeForUser = mutation({
  args: {
    repositoryId: v.id("repositories"),
    userId: v.id("users"),
  },
  handler: async (ctx, args) => {
    const repo = await ctx.db.get(args.repositoryId);
    if (!repo) {
      throw new Error("Repository not found");
    }
    if (repo.userId !== args.userId) {
      throw new Error("Unauthorized: You do not own this repository");
    }

    await ctx.db.patch(args.repositoryId, {
      enabled: false,
      updatedAt: Date.now(),
    });
    return args.repositoryId;
  },
});
