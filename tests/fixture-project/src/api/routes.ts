/**
 * Auth route definitions
 */

import { Router, Request, Response, NextFunction } from 'express';
import { authenticateUser, hashPassword, generateTokenPair, verifyRefreshToken } from '../auth/jwt';
import { authRateLimit } from '../auth/middleware';
import { logger } from '../utils/logger';
import { ValidationError } from '../utils/errors';
import { validateEmail, validatePassword } from '../utils/validation';

export const authRoutes = Router();

// Apply rate limiting to auth routes
authRoutes.use(authRateLimit(5, 15 * 60 * 1000));

/**
 * POST /auth/login
 * Authenticate user and return tokens
 */
authRoutes.post('/login', async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      throw new ValidationError('Email and password required');
    }

    if (!validateEmail(email)) {
      throw new ValidationError('Invalid email format');
    }

    // Mock: In real app, fetch from database
    const mockStoredHash = await hashPassword('password123');

    const tokens = await authenticateUser(email, password === 'password123' ? password : 'wrong', mockStoredHash);

    logger.info(`User logged in: ${email}`);

    res.json({
      success: true,
      ...tokens,
    });
  } catch (error) {
    next(error);
  }
});

/**
 * POST /auth/register
 * Register new user
 */
authRoutes.post('/register', async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { email, password, name } = req.body;

    if (!email || !password || !name) {
      throw new ValidationError('Email, password, and name required');
    }

    if (!validateEmail(email)) {
      throw new ValidationError('Invalid email format');
    }

    if (!validatePassword(password)) {
      throw new ValidationError('Password must be at least 8 characters');
    }

    // Hash password
    const hashedPassword = await hashPassword(password);

    // Mock: In real app, save to database
    const newUser = {
      id: `user_${Date.now()}`,
      email,
      name,
      createdAt: new Date(),
    };

    logger.info(`User registered: ${email}`);

    // Generate tokens for new user
    const tokens = generateTokenPair({
      userId: newUser.id,
      email: newUser.email,
      roles: ['user'],
      sessionId: `sess_${Date.now()}`,
    });

    res.status(201).json({
      success: true,
      user: newUser,
      ...tokens,
    });
  } catch (error) {
    next(error);
  }
});

/**
 * POST /auth/refresh
 * Refresh access token
 */
authRoutes.post('/refresh', async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { refreshToken } = req.body;

    if (!refreshToken) {
      throw new ValidationError('Refresh token required');
    }

    const { userId, sessionId } = verifyRefreshToken(refreshToken);

    // Mock: In real app, verify session is still valid
    const tokens = generateTokenPair({
      userId,
      email: 'user@example.com', // Would fetch from DB
      roles: ['user'],
      sessionId,
    });

    logger.info(`Token refreshed for user: ${userId}`);

    res.json({
      success: true,
      ...tokens,
    });
  } catch (error) {
    next(error);
  }
});

/**
 * POST /auth/logout
 * Invalidate session
 */
authRoutes.post('/logout', async (req: Request, res: Response, next: NextFunction) => {
  try {
    // Mock: In real app, invalidate session in database/cache
    logger.info('User logged out');

    res.json({ success: true, message: 'Logged out successfully' });
  } catch (error) {
    next(error);
  }
});
