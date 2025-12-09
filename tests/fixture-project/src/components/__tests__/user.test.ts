/**
 * User component tests
 */

import {
  createUser,
  findUserById,
  findUserByEmail,
  updateUser,
  deleteUser,
  listUsers,
} from '../user';

describe('User Component', () => {
  describe('createUser', () => {
    it('should create a new user with valid input', async () => {
      const input = {
        email: 'test@example.com',
        password: 'password123',
        name: 'Test User',
      };

      const user = await createUser(input);

      expect(user.email).toBe(input.email);
      expect(user.name).toBe(input.name);
      expect(user.roles).toContain('user');
      expect(user).not.toHaveProperty('passwordHash');
    });

    it('should throw ValidationError for invalid email', async () => {
      const input = {
        email: 'invalid-email',
        password: 'password123',
        name: 'Test User',
      };

      await expect(createUser(input)).rejects.toThrow('Invalid email format');
    });
  });

  describe('findUserById', () => {
    it('should return user when found', async () => {
      const user = await findUserById('user_1');

      expect(user).not.toBeNull();
      expect(user?.id).toBe('user_1');
    });

    it('should return null when not found', async () => {
      const user = await findUserById('nonexistent');

      expect(user).toBeNull();
    });
  });

  describe('findUserByEmail', () => {
    it('should return user when found', async () => {
      const user = await findUserByEmail('alice@example.com');

      expect(user).not.toBeNull();
      expect(user?.email).toBe('alice@example.com');
    });

    it('should return null when not found', async () => {
      const user = await findUserByEmail('nonexistent@example.com');

      expect(user).toBeNull();
    });
  });

  describe('updateUser', () => {
    it('should update user name', async () => {
      const updated = await updateUser('user_1', { name: 'New Name' });

      expect(updated.name).toBe('New Name');
    });

    it('should throw NotFoundError for nonexistent user', async () => {
      await expect(updateUser('nonexistent', { name: 'New' })).rejects.toThrow(
        'User not found'
      );
    });
  });

  describe('listUsers', () => {
    it('should return paginated users', async () => {
      const result = await listUsers(10, 0);

      expect(result.users).toBeInstanceOf(Array);
      expect(result.total).toBeGreaterThan(0);
    });

    it('should respect limit parameter', async () => {
      const result = await listUsers(1, 0);

      expect(result.users.length).toBeLessThanOrEqual(1);
    });
  });
});
