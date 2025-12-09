/**
 * API Request Handlers
 */

import { Request, Response, NextFunction } from 'express';
import { AuthenticatedRequest } from '../auth/types';
import { logger } from '../utils/logger';
import { NotFoundError, ValidationError } from '../utils/errors';
import { validateId } from '../utils/validation';

/**
 * Handle generic API requests
 */
export async function handleRequest(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    logger.info(`Handling request: ${req.method} ${req.path}`);

    // Mock user list
    const users = [
      { id: '1', name: 'Alice', email: 'alice@example.com' },
      { id: '2', name: 'Bob', email: 'bob@example.com' },
      { id: '3', name: 'Charlie', email: 'charlie@example.com' },
    ];

    res.json({ users, total: users.length });
  } catch (error) {
    next(error);
  }
}

/**
 * Handle user-specific requests
 */
export async function handleUserRequest(
  req: AuthenticatedRequest,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const { id } = req.params;

    if (!validateId(id)) {
      throw new ValidationError('Invalid user ID format');
    }

    logger.info(`Fetching user: ${id}`);

    // Mock user lookup
    const users: Record<string, { id: string; name: string; email: string }> = {
      '1': { id: '1', name: 'Alice', email: 'alice@example.com' },
      '2': { id: '2', name: 'Bob', email: 'bob@example.com' },
      '3': { id: '3', name: 'Charlie', email: 'charlie@example.com' },
    };

    const user = users[id];

    if (!user) {
      throw new NotFoundError(`User not found: ${id}`);
    }

    res.json({ user });
  } catch (error) {
    next(error);
  }
}

/**
 * Handle search requests
 */
export async function handleSearchRequest(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const { q, limit = 10, offset = 0 } = req.query;

    if (!q || typeof q !== 'string') {
      throw new ValidationError('Search query required');
    }

    logger.info(`Search request: "${q}" (limit: ${limit}, offset: ${offset})`);

    // Mock search results
    const results = [
      { type: 'user', id: '1', title: 'Alice', score: 0.95 },
      { type: 'user', id: '2', title: 'Bob', score: 0.87 },
    ];

    res.json({
      results,
      total: results.length,
      query: q,
      pagination: { limit: Number(limit), offset: Number(offset) },
    });
  } catch (error) {
    next(error);
  }
}
