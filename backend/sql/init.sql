-- Movie Recap Service Database Initialization
-- Simple initialization script for PostgreSQL

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create schema for multi-tenancy
CREATE SCHEMA IF NOT EXISTS tenant_data;

-- Basic setup will be handled by Alembic migrations
-- This file ensures database is ready for the application