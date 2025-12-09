/**
 * Session component - handles user session management
 */

import { SessionData } from '../auth/types';
import { logger } from '../utils/logger';
import { NotFoundError } from '../utils/errors';

// In-memory session store (use Redis in production)
const sessions = new Map<string, SessionData>();

/**
 * Create a new session
 */
export function createSession(
  sessionId: string,
  userId: string,
  deviceInfo: string,
  ipAddress: string
): SessionData {
  const session: SessionData = {
    userId,
    deviceInfo,
    ipAddress,
    createdAt: new Date(),
    lastActiveAt: new Date(),
    isValid: true,
  };

  sessions.set(sessionId, session);
  logger.debug(`Created session: ${sessionId} for user: ${userId}`);

  return session;
}

/**
 * Get session by ID
 */
export function getSession(sessionId: string): SessionData | null {
  return sessions.get(sessionId) || null;
}

/**
 * Update session activity
 */
export function touchSession(sessionId: string): void {
  const session = sessions.get(sessionId);

  if (session && session.isValid) {
    session.lastActiveAt = new Date();
    sessions.set(sessionId, session);
  }
}

/**
 * Invalidate a session
 */
export function invalidateSession(sessionId: string): void {
  const session = sessions.get(sessionId);

  if (session) {
    session.isValid = false;
    sessions.set(sessionId, session);
    logger.debug(`Invalidated session: ${sessionId}`);
  }
}

/**
 * Invalidate all sessions for a user
 */
export function invalidateUserSessions(userId: string): number {
  let count = 0;

  for (const [sessionId, session] of sessions.entries()) {
    if (session.userId === userId && session.isValid) {
      session.isValid = false;
      sessions.set(sessionId, session);
      count++;
    }
  }

  logger.debug(`Invalidated ${count} sessions for user: ${userId}`);
  return count;
}

/**
 * Get all active sessions for a user
 */
export function getUserSessions(userId: string): SessionData[] {
  const userSessions: SessionData[] = [];

  for (const session of sessions.values()) {
    if (session.userId === userId && session.isValid) {
      userSessions.push(session);
    }
  }

  return userSessions;
}

/**
 * Clean up expired sessions
 */
export function cleanupExpiredSessions(maxAgeMs: number = 7 * 24 * 60 * 60 * 1000): number {
  const now = Date.now();
  let cleaned = 0;

  for (const [sessionId, session] of sessions.entries()) {
    if (now - session.lastActiveAt.getTime() > maxAgeMs) {
      sessions.delete(sessionId);
      cleaned++;
    }
  }

  if (cleaned > 0) {
    logger.info(`Cleaned up ${cleaned} expired sessions`);
  }

  return cleaned;
}

/**
 * Get session statistics
 */
export function getSessionStats(): {
  total: number;
  active: number;
  invalid: number;
} {
  let active = 0;
  let invalid = 0;

  for (const session of sessions.values()) {
    if (session.isValid) {
      active++;
    } else {
      invalid++;
    }
  }

  return {
    total: sessions.size,
    active,
    invalid,
  };
}
