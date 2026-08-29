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

export const loginOrCreate = mutation({
  args: {
    whatsappPhone: v.string(),
    displayName: v.optional(v.string()),
    email: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const phone = args.whatsappPhone.trim();
    const existing = await ctx.db
      .query("users")
      .withIndex("by_whatsapp_phone", (q) => q.eq("whatsappPhone", phone))
      .first();

    if (existing) {
      if (args.displayName && args.displayName !== existing.displayName) {
        await ctx.db.patch(existing._id, {
          displayName: args.displayName,
          updatedAt: Date.now(),
        });
      }
      return existing._id;
    }

    const now = Date.now();
    return await ctx.db.insert("users", {
      displayName: args.displayName ?? "Developer",
      email: args.email ?? `${phone.replace(/\D/g, "")}@proofofwork.local`,
      whatsappPhone: phone,
      createdAt: now,
      updatedAt: now,
    });
  },
});

export const updateProfile = mutation({
  args: {
    userId: v.id("users"),
    displayName: v.optional(v.string()),
    email: v.optional(v.string()),
    whatsappPhone: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const user = await ctx.db.get(args.userId);
    if (!user) throw new Error("User not found");
    const now = Date.now();
    await ctx.db.patch(args.userId, {
      displayName: args.displayName ?? user.displayName,
      email: args.email ?? user.email,
      whatsappPhone: args.whatsappPhone ?? user.whatsappPhone,
      updatedAt: now,
    });
    return args.userId;
  },
});


