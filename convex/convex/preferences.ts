import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

export const preferenceValidators = {
  roleTitle: v.optional(v.string()),
  language: v.union(v.literal("es"), v.literal("en"), v.literal("pt")),
  tone: v.union(
    v.literal("humble_builder"),
    v.literal("deep_technical"),
    v.literal("direct_minimal"),
    v.literal("storyteller"),
    v.literal("pragmatic_lead"),
    v.literal("startup_founder"),
  ),
  targetAudience: v.union(
    v.literal("senior_engineers"),
    v.literal("tech_founders"),
    v.literal("recruiters"),
    v.literal("junior_developers"),
    v.literal("general_tech"),
  ),
  technicalLevel: v.union(v.literal("high"), v.literal("medium"), v.literal("accessible")),
  postLength: v.union(v.literal("concise"), v.literal("standard"), v.literal("deep_dive")),
  avoidWords: v.array(v.string()),
  preferredCTA: v.union(
    v.literal("discussion_question"),
    v.literal("github_link"),
    v.literal("lesson_takeaway"),
    v.literal("custom_cta"),
    v.literal("none"),
  ),
  customCTA: v.optional(v.string()),
  customRules: v.optional(v.array(v.string())),
  includeCodeSnippets: v.optional(v.boolean()),
  includeMetrics: v.optional(v.boolean()),
  hashtags: v.array(v.string()),
  allowedFormats: v.array(v.string()),
  autoPublish: v.boolean(),
  onboardingCompleted: v.boolean(),
};

export const getForUser = query({
  args: {
    userId: v.id("users"),
  },
  handler: async (ctx, args) => {
    const user = await ctx.db.get(args.userId);
    if (!user) {
      return null;
    }

    return await ctx.db
      .query("userPreferences")
      .withIndex("by_user", (q) => q.eq("userId", args.userId))
      .first();
  },
});

export const save = mutation({
  args: {
    userId: v.id("users"),
    ...preferenceValidators,
  },
  handler: async (ctx, args) => {
    // Authorize user existence
    const user = await ctx.db.get(args.userId);
    if (!user) {
      throw new Error("Unauthorized: Invalid or non-existent userId");
    }

    const existing = await ctx.db
      .query("userPreferences")
      .withIndex("by_user", (q) => q.eq("userId", args.userId))
      .first();

    const now = Date.now();

    if (existing) {
      await ctx.db.patch(existing._id, {
        roleTitle: args.roleTitle,
        language: args.language,
        tone: args.tone,
        targetAudience: args.targetAudience,
        technicalLevel: args.technicalLevel,
        postLength: args.postLength,
        avoidWords: args.avoidWords,
        preferredCTA: args.preferredCTA,
        customCTA: args.customCTA,
        customRules: args.customRules,
        includeCodeSnippets: args.includeCodeSnippets,
        includeMetrics: args.includeMetrics,
        hashtags: args.hashtags,
        allowedFormats: args.allowedFormats,
        autoPublish: args.autoPublish,
        onboardingCompleted: args.onboardingCompleted,
        updatedAt: now,
      });
      return existing._id;
    }

    return await ctx.db.insert("userPreferences", {
      userId: args.userId,
      roleTitle: args.roleTitle,
      language: args.language,
      tone: args.tone,
      targetAudience: args.targetAudience,
      technicalLevel: args.technicalLevel,
      postLength: args.postLength,
      avoidWords: args.avoidWords,
      preferredCTA: args.preferredCTA,
      customCTA: args.customCTA,
      customRules: args.customRules,
      includeCodeSnippets: args.includeCodeSnippets,
      includeMetrics: args.includeMetrics,
      hashtags: args.hashtags,
      allowedFormats: args.allowedFormats,
      autoPublish: args.autoPublish,
      onboardingCompleted: args.onboardingCompleted,
      createdAt: now,
      updatedAt: now,
    });
  },
});
