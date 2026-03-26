# PRD: Constantin Bot — Telegram Bot Constructor (MVP)

## Introduction

Constantin Bot is a Telegram bot constructor that allows a marketing team to create and manage notification bots without writing code. The admin interacts with a single Telegram bot (constructor) to spin up child bots, each running an automated message funnel defined in a NocoDB table. The system solves two problems: (1) launching new notification bots in minutes instead of hours of development, and (2) managing all bots from a single control point.

## Goals

- Enable a marketing team member to create a new Telegram notification bot in under 5 minutes via Telegram chat
- Provide full lifecycle management of child bots: create, start, stop, delete
- Allow non-technical users to edit message funnels through a spreadsheet-like NocoDB interface
- Run multiple independent child bots simultaneously on a single server

## User Stories

### US-001: Create a new bot via /add command
**Description:** As a marketing team member, I want to create a new notification bot by providing a Telegram token and name, so that I can quickly launch a new funnel without developer involvement.

**Acceptance Criteria:**
- [ ] `/add` command starts a step-by-step dialog (FSM)
- [ ] Bot asks for Telegram bot name
- [ ] Bot asks for Telegram token (from BotFather)
- [ ] Bot validates the token by calling Telegram API (`getMe`)
- [ ] Bot creates a new table in NocoDB with the correct schema (columns A-O as defined in the plan)
- [ ] Bot registers the new bot in PostgreSQL `bots` table
- [ ] Bot launches the child Python process via PM2 and updates its status in PostgreSQL
- [ ] Bot replies with: NocoDB table URL + child bot's Telegram link
- [ ] If token is invalid, bot reports the error and lets the user retry

### US-002: List all bots via /list command
**Description:** As a marketing team member, I want to see all created bots with their statuses and NocoDB table URL, so I can monitor and control which bots are running.

**Acceptance Criteria:**
- [ ] `/list` shows all bots from PostgreSQL registry
- [ ] Each entry displays: name, status (`running` / `stopped`), table URL, creation date
- [ ] If no bots exist, shows an informative message

### US-003: Stop a running bot via /stop
**Description:** As a marketing team member, I want to stop a bot temporarily without deleting it, so I can pause a campaign.

**Acceptance Criteria:**
- [ ] `/stop` shows a paginated list of running bots to choose from (inline keyboard) one to stop
- [ ] Stopping a bot kills its PM2 process and updates status to `stopped` in PostgreSQL
- [ ] Confirmation message is sent to the admin

### US-004: Start a stopped bot via /run
**Description:** As a marketing team member, I want to restart a previously stopped bot, so I can resume a campaign.

**Acceptance Criteria:**
- [ ] `/run` shows a paginated list of running bots to choose from (inline keyboard) one to restart
- [ ] Starting a bot launches the Python process via PM2 and updates status to `running` in PostgreSQL
- [ ] Confirmation message is sent to the admin

### US-005: Delete a bot via /delete
**Description:** As a marketing team member, I want to permanently remove a bot I no longer need, so the system stays clean.

**Acceptance Criteria:**
- [ ] `/delete` shows a paginated list of running bots to choose from (inline keyboard) one to remove from the bot registry
- [ ] Bot asks for confirmation before deletion
- [ ] Deletion stops the PM2 process (if running), removes the NocoDB table, and removes the record from PostgreSQL
- [ ] Confirmation message is sent to the admin

## Functional Requirements

- FR-1: Constructor bot runs as a TypeScript application using the Grammy framework
- FR-2: Constructor bot authenticates via a single Telegram token from environment variable
- FR-3: Constructor bot uses Grammy's `Conversations` plugin for multi-step dialogs (`/add`)
- FR-4: Constructor bot manages child processes via PM2 Node.js API (`pm2` package)
- FR-5: Constructor bot stores bot registry in PostgreSQL table `bots` (id, name, token, messages_table_url, status, created_at)
- FR-6: Constructor bot creates NocoDB tables via NocoDB REST API with the predefined funnel schema
- FR-7: Child bots are Python scripts (`bots/notification_bot.py`) launched with environment variables: `BOT_TOKEN`, `MESSAGES_TABLE_URL`
- FR-12: All services run inside Docker Compose (PostgreSQL, NocoDB, constructor container with Node.js + Python + PM2)

## Non-Goals (Out of Scope for MVP)

- No analytics or statistics on subscribers / funnel completion (planned for v2, see Future section)
- No multi-admin support or role-based access control
- No bot editing after creation (edit the NocoDB table directly)
- No automatic restart of child bots after container restart
- No webhook mode — child bots use long polling
- No deeplink support (single funnel per bot)
- No scheduled/timed funnel starts
- No A/B testing of funnels
- No payment integration

## Technical Considerations

- **Existing infrastructure:** Docker Compose with PostgreSQL 16, NocoDB, and a Node.js/Python container is already deployed
- **Database:** PostgreSQL `constructor` database with `bots` table schema already created in `init-db/`
- **NocoDB API:** Requires API token (stored in env) for table creation and data access
- **PM2:** Used as process manager to launch/stop/monitor child Python bots inside the same container
- **Grammy Conversations:** Use `@grammyjs/conversations` for the `/add` multi-step dialog — avoids manual FSM
- **Child bot rewrite:** Current `bots/notification_bot.py` contains constructor FSM logic that must be removed, keeping only child bot funnel execution logic
- **Environment variables:** `CONSTRUCTOR_BOT_TOKEN`, `NOCODB_API_TOKEN`, `NOCODB_BASE_URL`, `DATABASE_URL`

## Success Metrics

- A marketing team member can create a new bot and have it responding to `/start` within 5 minutes
- Child bot correctly executes a 10+ step funnel with mixed message types, delays, and buttons
- Constructor can manage 10+ bots simultaneously without performance issues
- Zero manual code changes required to create or manage bots

## Future: Analytics (v2)

Planned for the next iteration after MVP:
- Track number of subscribers per bot
- Track funnel completion rate (how far users progress through the scenario)
- Track button click statistics
- `/stats <bot>` command in constructor to view analytics
- Dashboard in NocoDB or a separate table for analytics data

## Open Questions

- Should child bots reload the NocoDB scenario periodically (hot-reload) or only on startup?
- How to handle Telegram API rate limits when a child bot has many subscribers?
- Should the constructor restrict access to a whitelist of Telegram user IDs?
