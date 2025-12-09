/**
 * API Router
 * Main entry point for all API routes
 */

import { Router } from 'express';
import { authRoutes } from './routes';
import { handleRequest, handleUserRequest } from './handler';
import { authMiddleware, requireRoles } from '../auth/middleware';

export const apiRouter = Router();

// Auth routes (public)
apiRouter.use('/auth', authRoutes);

// User routes (protected)
apiRouter.get('/users', authMiddleware, requireRoles('admin'), handleRequest);
apiRouter.get('/users/:id', authMiddleware, handleUserRequest);

// Health check
apiRouter.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});
