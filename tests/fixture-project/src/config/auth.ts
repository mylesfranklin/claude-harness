/**
 * Authentication configuration
 */

import { AuthConfig } from '../auth/types';

export const authConfig: AuthConfig = {
  jwtSecret: process.env.JWT_SECRET || 'dev-jwt-secret-change-in-production',
  jwtExpiresIn: process.env.JWT_EXPIRES_IN || '15m',
  refreshSecret: process.env.REFRESH_SECRET || 'dev-refresh-secret-change-in-production',
  refreshExpiresIn: process.env.REFRESH_EXPIRES_IN || '7d',
  bcryptRounds: parseInt(process.env.BCRYPT_ROUNDS || '10', 10),
};

export default authConfig;
