import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

export const getOrCreateDefault = mutation({
  args: {
    whatsappPhone: v.optional(v.string()),
    displayName: v.optional(v.string()),
    email: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const phone = args.whatsappPhone ?? "+51999888777";
    const existing = await ctx.db
      .query("users")
      .withIndex("by_whatsapp_phone", (q) => q.eq("whatsappPhone", phone))
      .first();

    if (existing) {
      return existing._id;
    }

    const now = Date.now();
    return await ctx.db.insert("users", {
      displayName: args.displayName ?? "Lead Developer",
      email: args.email ?? "developer@proofofwork.local",
      whatsappPhone: phone,
      createdAt: now,
      updatedAt: now,
    });
  },
});

export const getByWhatsappPhone = query({
  args: { whatsappPhone: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("users")
      .withIndex("by_whatsapp_phone", (q) => q.eq("whatsappPhone", args.whatsappPhone))
      .first();
  },
});

export const getById = query({
  args: { userId: v.id("users") },
  handler: async (ctx, args) => {
    return await ctx.db.get(args.userId);
  },
});
