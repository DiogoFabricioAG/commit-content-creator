import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

const githubEventType = v.union(v.literal("push"), v.literal("pull_request"));

export const record = mutation({
  args: {
    deliveryId: v.string(),
    eventType: githubEventType,
    repositoryFullName: v.string(),
    branch: v.optional(v.string()),
    commitShas: v.array(v.string()),
    action: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const existing = await ctx.db
      .query("githubEvents")
      .withIndex("by_delivery_id", (q) => q.eq("deliveryId", args.deliveryId))
      .unique();

    if (existing) {
      return { eventId: existing._id, duplicate: true };
    }

    const eventId = await ctx.db.insert("githubEvents", {
      deliveryId: args.deliveryId,
      eventType: args.eventType,
      status: "received",
      receivedAt: Date.now(),
      metadata: {
        repositoryFullName: args.repositoryFullName,
        commitShas: args.commitShas,
        ...(args.branch ? { branch: args.branch } : {}),
        ...(args.action ? { action: args.action } : {}),
      },
    });

    return { eventId, duplicate: false };
  },
});

export const getByDeliveryId = query({
  args: { deliveryId: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("githubEvents")
      .withIndex("by_delivery_id", (q) => q.eq("deliveryId", args.deliveryId))
      .unique();
  },
});
