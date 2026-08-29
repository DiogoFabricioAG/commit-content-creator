import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

export const record = mutation({
  args: {
    approvalRequestId: v.id("approvalRequests"),
    direction: v.union(v.literal("inbound"), v.literal("outbound")),
    messageId: v.string(),
    content: v.string(),
    interpretedIntent: v.optional(v.string()),
    confidence: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("approvalMessages", {
      ...args,
      createdAt: Date.now(),
    });
  },
});

export const listForRequest = query({
  args: { approvalRequestId: v.id("approvalRequests") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("approvalMessages")
      .withIndex("by_request", (q) => q.eq("approvalRequestId", args.approvalRequestId))
      .order("asc")
      .collect();
  },
});
