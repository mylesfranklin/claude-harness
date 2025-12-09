/**
 * Authentication module exports
 * Provides JWT-based authentication for the API
 */

export { authenticateUser, validateCredentials } from './jwt';
export { authMiddleware, requireAuth, optionalAuth } from './middleware';
export type { AuthPayload, TokenPair, AuthConfig } from './types';
