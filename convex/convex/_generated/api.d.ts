/* eslint-disable */
/**
 * Generated `api` utility.
 *
 * THIS CODE IS AUTOMATICALLY GENERATED.
 *
 * To regenerate, run `npx convex dev`.
 * @module
 */

import type * as activity from "../activity.js";
import type * as approvalMessages from "../approvalMessages.js";
import type * as approvalRequests from "../approvalRequests.js";
import type * as commitAnalyses from "../commitAnalyses.js";
import type * as commits from "../commits.js";
import type * as diagnostics from "../diagnostics.js";
import type * as githubEvents from "../githubEvents.js";
import type * as historicalDigests from "../historicalDigests.js";
import type * as landingVisits from "../landingVisits.js";
import type * as media from "../media.js";
import type * as postVersions from "../postVersions.js";
import type * as posts from "../posts.js";
import type * as preferences from "../preferences.js";
import type * as repositories from "../repositories.js";
import type * as retention from "../retention.js";
import type * as socialAccounts from "../socialAccounts.js";
import type * as stories from "../stories.js";
import type * as storyClusters from "../storyClusters.js";
import type * as users from "../users.js";
import type * as whatsappSessions from "../whatsappSessions.js";

import type {
  ApiFromModules,
  FilterApi,
  FunctionReference,
} from "convex/server";

declare const fullApi: ApiFromModules<{
  activity: typeof activity;
  approvalMessages: typeof approvalMessages;
  approvalRequests: typeof approvalRequests;
  commitAnalyses: typeof commitAnalyses;
  commits: typeof commits;
  diagnostics: typeof diagnostics;
  githubEvents: typeof githubEvents;
  historicalDigests: typeof historicalDigests;
  landingVisits: typeof landingVisits;
  media: typeof media;
  postVersions: typeof postVersions;
  posts: typeof posts;
  preferences: typeof preferences;
  repositories: typeof repositories;
  retention: typeof retention;
  socialAccounts: typeof socialAccounts;
  stories: typeof stories;
  storyClusters: typeof storyClusters;
  users: typeof users;
  whatsappSessions: typeof whatsappSessions;
}>;

/**
 * A utility for referencing Convex functions in your app's public API.
 *
 * Usage:
 * ```js
 * const myFunctionReference = api.myModule.myFunction;
 * ```
 */
export declare const api: FilterApi<
  typeof fullApi,
  FunctionReference<any, "public">
>;

/**
 * A utility for referencing Convex functions in your app's internal API.
 *
 * Usage:
 * ```js
 * const myFunctionReference = internal.myModule.myFunction;
 * ```
 */
export declare const internal: FilterApi<
  typeof fullApi,
  FunctionReference<any, "internal">
>;

export declare const components: {};
