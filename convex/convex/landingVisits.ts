import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

const LANDING_METRIC_KEY = "landing";
const INITIAL_UNIQUE_VISITORS = 100;

export const getVisitorCount = query({
  args: {},
  handler: async (ctx) => {
    const metric = await ctx.db
      .query("landingMetrics")
      .withIndex("by_key", (q) => q.eq("key", LANDING_METRIC_KEY))
      .unique();

    return metric?.uniqueVisitors ?? INITIAL_UNIQUE_VISITORS;
  },
});

export const registerVisitor = mutation({
  args: {
    visitorId: v.string(),
  },
  handler: async (ctx, args) => {
    const visitorId = args.visitorId.trim();
    if (!visitorId) {
      return INITIAL_UNIQUE_VISITORS;
    }

    const now = Date.now();
    const existingVisitor = await ctx.db
      .query("landingVisitors")
      .withIndex("by_visitor_id", (q) => q.eq("visitorId", visitorId))
      .unique();

    const metric = await ctx.db
      .query("landingMetrics")
      .withIndex("by_key", (q) => q.eq("key", LANDING_METRIC_KEY))
      .unique();
    const currentCount = metric?.uniqueVisitors ?? INITIAL_UNIQUE_VISITORS;

    if (existingVisitor) {
      await ctx.db.patch(existingVisitor._id, { lastVisitedAt: now });
      if (metric) {
        await ctx.db.patch(metric._id, { updatedAt: now });
      }
      return currentCount;
    }

    await ctx.db.insert("landingVisitors", {
      visitorId,
      firstVisitedAt: now,
      lastVisitedAt: now,
    });

    const nextCount = currentCount + 1;
    if (metric) {
      await ctx.db.patch(metric._id, {
        uniqueVisitors: nextCount,
        updatedAt: now,
      });
    } else {
      await ctx.db.insert("landingMetrics", {
        key: LANDING_METRIC_KEY,
        uniqueVisitors: nextCount,
        updatedAt: now,
      });
    }

    return nextCount;
  },
});
