import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

const WINDOW_MS = 24 * 60 * 60 * 1000;

export const open = mutation({
  args: {
    userId: v.id("users"),
    phone: v.string(),
    inboundMessageId: v.string(),
  },
  handler: async (ctx, args) => {
    const now = Date.now();
    const existing = await ctx.db
      .query("whatsappSessions")
      .withIndex("by_phone", (q) => q.eq("phone", args.phone))
      .first();

    if (existing) {
      await ctx.db.patch(existing._id, {
        userId: args.userId,
        lastInboundAt: now,
        lastInboundMessageId: args.inboundMessageId,
        expiresAt: now + WINDOW_MS,
      });
      return existing._id;
    }

    return await ctx.db.insert("whatsappSessions", {
      userId: args.userId,
      phone: args.phone,
      openedAt: now,
      lastInboundAt: now,
      lastInboundMessageId: args.inboundMessageId,
      expiresAt: now + WINDOW_MS,
    });
  },
});

export const getForPhone = query({
  args: { phone: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("whatsappSessions")
      .withIndex("by_phone", (q) => q.eq("phone", args.phone))
      .first();
  },
});
