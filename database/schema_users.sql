-- Database schema for the users table

CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; -- For uuid_generate_v4()

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL, -- Store hashed passwords, not plain text
    full_name VARCHAR(120),
    role VARCHAR(50) DEFAULT 'user' NOT NULL, -- e.g., 'user', 'admin'
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster username and email lookups
CREATE INDEX IF NOT EXISTS idx_users_username ON users (username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);

-- Trigger to update the updated_at timestamp on every update
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_users_updated_at ON users;
CREATE TRIGGER trigger_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Optional: Add some initial thoughts on roles or permissions if needed later
-- COMMENT ON COLUMN users.role IS 'User role, e.g., ''user'' for standard access, ''admin'' for administrative privileges.';

-- Note on password hashing:
-- The application backend (e.g., Flask service) will be responsible for:
-- 1. Hashing passwords using a strong algorithm (e.g., bcrypt, Argon2) before storing them in password_hash.
-- 2. Verifying passwords by hashing the provided login password and comparing it to the stored hash.
-- DO NOT STORE PLAIN TEXT PASSWORDS.

