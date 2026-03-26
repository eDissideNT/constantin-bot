# CLAUDE.md — Constantin Bot

## Project structure

```
├── src/             # TypeScript source code (constructor bot)
├── bots/            # Python bots launched by the constructor
├── data/            # Data files — DO NOT scan or read unless explicitly asked
├── init-db/         # PostgreSQL initialization scripts (run once on first start)
├── .claude/plans/   # Project plans
```

## Infrastructure (docker-compose)

- **postgres** — PostgreSQL 16, two databases: `constructor` (bot registry) and `nocodb` (NocoDB metadata)
- **nocodb** — NocoDB UI at `http://localhost:8080`, connected to the `nocodb` database
- **constructor** — TypeScript bot + Python 3.12 runtime + PM2 for running child bots

## Running

See README.md for setup and run instructions.