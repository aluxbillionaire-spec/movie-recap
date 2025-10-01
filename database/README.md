# Database Migrations

## Migration System

This directory contains SQL migration files for the Movie Recap Pipeline database.

### Migration Files

- `001_initial_schema.sql` - Initial database schema
- `002_add_embeddings.sql` - Add vector embeddings support
- `003_add_indexes.sql` - Performance optimizations
- `004_add_rls_policies.sql` - Row Level Security policies

### Running Migrations

```bash
# Using Alembic (recommended)
alembic upgrade head

# Using psql directly
psql -d movierecap -f database/migrations/001_initial_schema.sql
```

### Migration Guidelines

1. Always test migrations on a copy of production data
2. Include rollback scripts for each migration
3. Document breaking changes
4. Use transactions for atomic operations
5. Consider performance impact on large tables