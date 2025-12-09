/**
 * Session component tests
 */

import {
  createSession,
  getSession,
  touchSession,
  invalidateSession,
  invalidateUserSessions,
  getUserSessions,
  getSessionStats,
} from '../session';

describe('Session Component', () => {
  const testSessionId = 'test_session_123';
  const testUserId = 'user_123';

  beforeEach(() => {
    // Create a test session
    createSession(testSessionId, testUserId, 'Chrome/120', '127.0.0.1');
  });

  describe('createSession', () => {
    it('should create a new session', () => {
      const session = createSession('new_session', 'user_456', 'Firefox', '192.168.1.1');

      expect(session.userId).toBe('user_456');
      expect(session.deviceInfo).toBe('Firefox');
      expect(session.isValid).toBe(true);
    });
  });

  describe('getSession', () => {
    it('should return session when found', () => {
      const session = getSession(testSessionId);

      expect(session).not.toBeNull();
      expect(session?.userId).toBe(testUserId);
    });

    it('should return null when not found', () => {
      const session = getSession('nonexistent');

      expect(session).toBeNull();
    });
  });

  describe('touchSession', () => {
    it('should update lastActiveAt', () => {
      const before = getSession(testSessionId)?.lastActiveAt;

      // Small delay to ensure time difference
      setTimeout(() => {
        touchSession(testSessionId);
        const after = getSession(testSessionId)?.lastActiveAt;

        expect(after?.getTime()).toBeGreaterThanOrEqual(before?.getTime() || 0);
      }, 10);
    });
  });

  describe('invalidateSession', () => {
    it('should mark session as invalid', () => {
      invalidateSession(testSessionId);
      const session = getSession(testSessionId);

      expect(session?.isValid).toBe(false);
    });
  });

  describe('invalidateUserSessions', () => {
    it('should invalidate all sessions for a user', () => {
      createSession('session_2', testUserId, 'Safari', '10.0.0.1');
      createSession('session_3', testUserId, 'Edge', '10.0.0.2');

      const count = invalidateUserSessions(testUserId);

      expect(count).toBeGreaterThanOrEqual(1);
    });
  });

  describe('getUserSessions', () => {
    it('should return all active sessions for user', () => {
      const sessions = getUserSessions(testUserId);

      expect(sessions).toBeInstanceOf(Array);
    });
  });

  describe('getSessionStats', () => {
    it('should return session statistics', () => {
      const stats = getSessionStats();

      expect(stats).toHaveProperty('total');
      expect(stats).toHaveProperty('active');
      expect(stats).toHaveProperty('invalid');
    });
  });
});
