# Fixture Project

A test fixture project for validating the Claude Code Harness.

## Structure

```
src/
├── auth/           # Authentication logic
│   ├── index.ts    # Auth exports
│   ├── jwt.ts      # JWT token handling
│   ├── middleware.ts # Auth middleware
│   └── types.ts    # Auth type definitions
├── api/            # API handlers
│   ├── index.ts    # API router
│   ├── handler.ts  # Request handlers
│   └── routes.ts   # Route definitions
├── components/     # Business logic components
│   ├── user.ts     # User management
│   ├── session.ts  # Session handling
│   └── __tests__/  # Component tests
├── utils/          # Utility functions
│   ├── logger.ts   # Logging utility
│   ├── errors.ts   # Error handling
│   └── validation.ts # Input validation
├── config/         # Configuration
│   ├── index.ts    # Config exports
│   ├── database.ts # Database config
│   └── auth.ts     # Auth config
├── middleware/     # Express middleware
│   └── index.ts    # Middleware exports
└── index.ts        # Application entry point
```

## Quick Start

```bash
npm install
npm run dev
```

## Testing

```bash
npm test
npm run test:coverage
```

## API Endpoints

- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `GET /auth/me` - Get current user
- `POST /auth/refresh` - Refresh token
- `GET /users` - List users (admin)
- `GET /users/:id` - Get user by ID
