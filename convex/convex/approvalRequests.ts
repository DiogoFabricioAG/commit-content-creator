import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

const approvalStatus = v.union(
  v.literal("pending"),
  v.literal("approved"),
  v.literal("revised"),
  v.literal("rejected"),
  v.literal("clarify"),
  v.literal("hold"),
);

export const record = mutation({
  args: {
    userId: v.id("users"),
    postId: v.id("posts"),
    channel: v.literal("whatsapp"),
    status: approvalStatus,
    currentPostVersionId: v.id("postVersions"),
    recipientPhone: v.string(),
    kapsoOutboundMessageId: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("approvalRequests", {
      ...args,
      createdAt: Date.now(),
    });
  },
});

export const getPendingForPhone = query({
  args: { recipientPhone: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("approvalRequests")
      .withIndex("by_phone_status", (q) =>
        q.eq("recipientPhone", args.recipientPhone).eq("status", "pending"),
      )
      .order("desc")
      .first();
  },
});

export const getById = query({
  args: { approvalRequestId: v.id("approvalRequests") },
  handler: async (ctx, args) => {
    return await ctx.db.get(args.approvalRequestId);
  },
});

export const getForPost = query({
  args: { postId: v.id("posts") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("approvalRequests")
      .withIndex("by_post", (q) => q.eq("postId", args.postId))
      .order("desc")
      .first();
  },
});

export const updateStatus = mutation({
  args: {
    approvalRequestId: v.id("approvalRequests"),
    status: approvalStatus,
    currentPostVersionId: v.optional(v.id("postVersions")),
  },
  handler: async (ctx, args) => {
    const patch: {
      status: typeof args.status;
      currentPostVersionId?: typeof args.currentPostVersionId;
      resolvedAt?: number;
    } = { status: args.status };

    if (args.currentPostVersionId) {
      patch.currentPostVersionId = args.currentPostVersionId;
    }

    if (args.status === "approved" || args.status === "rejected") {
      patch.resolvedAt = Date.now();
    }

    await ctx.db.patch(args.approvalRequestId, patch);
  },
});
