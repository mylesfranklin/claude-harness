/**
 * JWT token handling for authentication
 */

import jwt from 'jsonwebtoken';
import bcrypt from 'bcrypt';
import { authConfig } from '../config/auth';
import { AuthPayload, TokenPair } from './types';
import { logger } from '../utils/logger';
import { AuthenticationError } from '../utils/errors';

/**
 * Authenticate a user with email and password
 * Returns token pair on success
 */
export async function authenticateUser(
  email: string,
  password: string,
  storedHash: string
): Promise<TokenPair> {
  logger.debug(`Authenticating user: ${email}`);

  const isValid = await bcrypt.compare(password, storedHash);

  if (!isValid) {
    logger.warn(`Failed authentication attempt for: ${email}`);
    throw new AuthenticationError('Invalid credentials');
  }

  // In real implementation, fetch user from database
  const payload: Omit<AuthPayload, 'iat' | 'exp'> = {
    userId: 'user-123', // Would come from DB
    email,
    roles: ['user'],
    sessionId: generateSessionId(),
  };

  return generateTokenPair(payload);
}

/**
 * Validate user credentials without generating tokens
 */
export async function validateCredentials(
  password: string,
  storedHash: string
): Promise<boolean> {
  return bcrypt.compare(password, storedHash);
}

/**
 * Generate a new token pair (access + refresh)
 */
export function generateTokenPair(
  payload: Omit<AuthPayload, 'iat' | 'exp'>
): TokenPair {
  const accessToken = jwt.sign(payload, authConfig.jwtSecret, {
    expiresIn: authConfig.jwtExpiresIn,
  });

  const refreshToken = jwt.sign(
    { userId: payload.userId, sessionId: payload.sessionId },
    authConfig.refreshSecret,
    { expiresIn: authConfig.refreshExpiresIn }
  );

  // Parse expiry for response
  const decoded = jwt.decode(accessToken) as AuthPayload;
  const expiresIn = decoded.exp - Math.floor(Date.now() / 1000);

  return { accessToken, refreshToken, expiresIn };
}

/**
 * Verify and decode an access token
 */
export function verifyAccessToken(token: string): AuthPayload {
  try {
    return jwt.verify(token, authConfig.jwtSecret) as AuthPayload;
  } catch (error) {
    if (error instanceof jwt.TokenExpiredError) {
      throw new AuthenticationError('Token expired');
    }
    if (error instanceof jwt.JsonWebTokenError) {
      throw new AuthenticationError('Invalid token');
    }
    throw error;
  }
}

/**
 * Verify a refresh token
 */
export function verifyRefreshToken(token: string): { userId: string; sessionId: string } {
  try {
    return jwt.verify(token, authConfig.refreshSecret) as { userId: string; sessionId: string };
  } catch (error) {
    throw new AuthenticationError('Invalid refresh token');
  }
}

/**
 * Hash a password for storage
 */
export async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, authConfig.bcryptRounds);
}

/**
 * Generate a unique session ID
 */
function generateSessionId(): string {
  return `sess_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}
