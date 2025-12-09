/**
 * Authentication middleware for Express
 */

import { Request, Response, NextFunction } from 'express';
import { verifyAccessToken } from './jwt';
import { AuthPayload, AuthenticatedRequest } from './types';
import { logger } from '../utils/logger';
import { AuthenticationError, ForbiddenError } from '../utils/errors';

/**
 * Main authentication middleware
 * Extracts and validates JWT from Authorization header
 */
export function authMiddleware(
  req: AuthenticatedRequest,
  res: Response,
  next: NextFunction
): void {
  const authHeader = req.headers.authorization;

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return next(new AuthenticationError('No token provided'));
  }

  const token = authHeader.substring(7);

  try {
    const payload = verifyAccessToken(token);
    req.user = payload;
    req.token = token;
    logger.debug(`Authenticated user: ${payload.userId}`);
    next();
  } catch (error) {
    next(error);
  }
}

/**
 * Require authentication - fail if not authenticated
 */
export function requireAuth(
  req: AuthenticatedRequest,
  res: Response,
  next: NextFunction
): void {
  if (!req.user) {
    return next(new AuthenticationError('Authentication required'));
  }
  next();
}

/**
 * Optional authentication - continue even if not authenticated
 */
export function optionalAuth(
  req: AuthenticatedRequest,
  res: Response,
  next: NextFunction
): void {
  const authHeader = req.headers.authorization;

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return next();
  }

  const token = authHeader.substring(7);

  try {
    const payload = verifyAccessToken(token);
    req.user = payload;
    req.token = token;
  } catch (error) {
    // Ignore auth errors for optional auth
    logger.debug('Optional auth failed, continuing without user');
  }

  next();
}

/**
 * Require specific roles
 */
export function requireRoles(...roles: string[]) {
  return (req: AuthenticatedRequest, res: Response, next: NextFunction): void => {
    if (!req.user) {
      return next(new AuthenticationError('Authentication required'));
    }

    const hasRole = roles.some(role => req.user!.roles.includes(role));

    if (!hasRole) {
      return next(new ForbiddenError(`Required roles: ${roles.join(', ')}`));
    }

    next();
  };
}

/**
 * Rate limiting for auth endpoints
 */
const authAttempts = new Map<string, { count: number; resetAt: number }>();

export function authRateLimit(maxAttempts = 5, windowMs = 15 * 60 * 1000) {
  return (req: Request, res: Response, next: NextFunction): void => {
    const key = req.ip || 'unknown';
    const now = Date.now();

    const record = authAttempts.get(key);

    if (record && record.resetAt > now) {
      if (record.count >= maxAttempts) {
        res.status(429).json({
          error: 'Too many authentication attempts',
          retryAfter: Math.ceil((record.resetAt - now) / 1000),
        });
        return;
      }
      record.count++;
    } else {
      authAttempts.set(key, { count: 1, resetAt: now + windowMs });
    }

    next();
  };
}
