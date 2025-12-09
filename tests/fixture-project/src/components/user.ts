/**
 * User component - handles user management logic
 */

import { query } from '../config/database';
import { hashPassword } from '../auth/jwt';
import { logger } from '../utils/logger';
import { NotFoundError, ConflictError, ValidationError } from '../utils/errors';
import { validateEmail } from '../utils/validation';

export interface User {
  id: string;
  email: string;
  name: string;
  passwordHash: string;
  roles: string[];
  createdAt: Date;
  updatedAt: Date;
  lastLoginAt?: Date;
}

export interface CreateUserInput {
  email: string;
  password: string;
  name: string;
  roles?: string[];
}

export interface UpdateUserInput {
  email?: string;
  name?: string;
  roles?: string[];
}

/**
 * Create a new user
 */
export async function createUser(input: CreateUserInput): Promise<Omit<User, 'passwordHash'>> {
  const { email, password, name, roles = ['user'] } = input;

  if (!validateEmail(email)) {
    throw new ValidationError('Invalid email format');
  }

  // Check if user exists
  const existing = await findUserByEmail(email);
  if (existing) {
    throw new ConflictError('User with this email already exists');
  }

  const passwordHash = await hashPassword(password);
  const id = `user_${Date.now()}`;
  const now = new Date();

  // In real app, insert into database
  const user: User = {
    id,
    email,
    name,
    passwordHash,
    roles,
    createdAt: now,
    updatedAt: now,
  };

  logger.info(`Created user: ${email}`);

  const { passwordHash: _, ...safeUser } = user;
  return safeUser;
}

/**
 * Find user by ID
 */
export async function findUserById(id: string): Promise<User | null> {
  // Mock implementation
  const mockUsers: Record<string, User> = {
    'user_1': {
      id: 'user_1',
      email: 'alice@example.com',
      name: 'Alice',
      passwordHash: 'hashed',
      roles: ['user', 'admin'],
      createdAt: new Date('2024-01-01'),
      updatedAt: new Date('2024-06-01'),
    },
  };

  return mockUsers[id] || null;
}

/**
 * Find user by email
 */
export async function findUserByEmail(email: string): Promise<User | null> {
  // Mock implementation
  const mockUsers: User[] = [
    {
      id: 'user_1',
      email: 'alice@example.com',
      name: 'Alice',
      passwordHash: 'hashed',
      roles: ['user', 'admin'],
      createdAt: new Date('2024-01-01'),
      updatedAt: new Date('2024-06-01'),
    },
  ];

  return mockUsers.find(u => u.email === email) || null;
}

/**
 * Update user
 */
export async function updateUser(id: string, input: UpdateUserInput): Promise<User> {
  const user = await findUserById(id);

  if (!user) {
    throw new NotFoundError(`User not found: ${id}`);
  }

  // Apply updates
  if (input.email) user.email = input.email;
  if (input.name) user.name = input.name;
  if (input.roles) user.roles = input.roles;
  user.updatedAt = new Date();

  logger.info(`Updated user: ${id}`);

  return user;
}

/**
 * Delete user
 */
export async function deleteUser(id: string): Promise<void> {
  const user = await findUserById(id);

  if (!user) {
    throw new NotFoundError(`User not found: ${id}`);
  }

  // In real app, delete from database
  logger.info(`Deleted user: ${id}`);
}

/**
 * List all users with pagination
 */
export async function listUsers(limit = 10, offset = 0): Promise<{ users: User[]; total: number }> {
  // Mock implementation
  const allUsers: User[] = [
    {
      id: 'user_1',
      email: 'alice@example.com',
      name: 'Alice',
      passwordHash: 'hashed',
      roles: ['user', 'admin'],
      createdAt: new Date('2024-01-01'),
      updatedAt: new Date('2024-06-01'),
    },
    {
      id: 'user_2',
      email: 'bob@example.com',
      name: 'Bob',
      passwordHash: 'hashed',
      roles: ['user'],
      createdAt: new Date('2024-02-01'),
      updatedAt: new Date('2024-02-01'),
    },
  ];

  return {
    users: allUsers.slice(offset, offset + limit),
    total: allUsers.length,
  };
}
