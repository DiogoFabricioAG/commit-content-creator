import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

export const upsert = mutation({
  args: {
    userId: v.id("users"),
    provider: v.literal("linkedin"),
    providerMemberId: v.optional(v.string()),
    authorUrn: v.optional(v.string()),
    accessTokenEncrypted: v.string(),
    expiresAt: v.optional(v.number()),
    scopes: v.array(v.string()),
  },
  handler: async (ctx, args) => {
    const existing = await ctx.db
      .query("socialAccounts")
      .withIndex("by_user_provider", (q) =>
        q.eq("userId", args.userId).eq("provider", args.provider),
      )
      .first();

    const now = Date.now();
    if (existing) {
      await ctx.db.patch(existing._id, {
        ...args,
        updatedAt: now,
      });
      return existing._id;
    }

    return await ctx.db.insert("socialAccounts", {
      ...args,
      createdAt: now,
      updatedAt: now,
    });
  },
});

export const getByUserAndProvider = query({
  args: {
    userId: v.id("users"),
    provider: v.literal("linkedin"),
  },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("socialAccounts")
      .withIndex("by_user_provider", (q) =>
        q.eq("userId", args.userId).eq("provider", args.provider),
      )
      .first();
  },
});
