import express from 'express';
import { config } from './config';
import { logger } from './utils/logger';
import { apiRouter } from './api';
import { authMiddleware } from './auth/middleware';
import { errorHandler } from './middleware';

const app = express();

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes
app.use('/api', apiRouter);

// Error handling
app.use(errorHandler);

// Start server
const PORT = config.port || 3000;

app.listen(PORT, () => {
  logger.info(`Server running on port ${PORT}`);
  logger.info(`Environment: ${config.env}`);
});

export { app };
