/**
 * Authentication type definitions
 */

export interface AuthPayload {
  userId: string;
  email: string;
  roles: string[];
  sessionId: string;
  iat: number;
  exp: number;
}

export interface TokenPair {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}

export interface AuthConfig {
  jwtSecret: string;
  jwtExpiresIn: string;
  refreshSecret: string;
  refreshExpiresIn: string;
  bcryptRounds: number;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
}

export interface AuthenticatedRequest extends Request {
  user?: AuthPayload;
  token?: string;
}

export interface SessionData {
  userId: string;
  deviceInfo: string;
  ipAddress: string;
  createdAt: Date;
  lastActiveAt: Date;
  isValid: boolean;
}
