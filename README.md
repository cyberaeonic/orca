<p align="center">
  <a href="https://github.com/jumpino27?tab=repositories">
    <img alt="Explore more open-source projects" src="https://img.shields.io/badge/Explore%20more%20open--source%20projects-GitHub-181717?logo=github">
  </a>
  <a href="https://revolut.me/jumpino">
    <img alt="Support the creator" src="https://img.shields.io/badge/Support%20the%20creator-Revolut-0075EB">
  </a>
</p>

<p align="center">
  Browse more Jumpino open-source projects and support ongoing development.
  More tools are coming soon.
</p>

# AI Discord Manager

A Python Discord bridge bot designed for AI coding agents such as Codex,
Claude Code, OpenCode, and similar local agents.

The idea is simple: give an authorized AI agent a safe Discord control surface.
The agent can run or edit `bot.py`, inspect the current server state, and then
use Discord-native commands to create channels, manage roles, post updates,
moderate members, or automate a server setup.

This is useful when you want an agent to manage a Discord server as part of a
larger workflow without giving it direct access to your Discord account.

## How AI Agents Use It

An AI agent can work with this repository in two ways:

1. Run `python bot.py`, then issue prefix commands in Discord such as
   `!list-channels`, `!create-channel`, `!announce`, or `!give-role`.
2. Write focused one-shot Python scripts that import/use `discord.py` and the
   same `.env` token to perform larger setup tasks, then shut down immediately.

If the bot is missing a capability, the agent should edit `bot.py`, add the
needed command, run the checks, and then use the enhanced bot. See
[`ai-agent_instructions.md`](ai-agent_instructions.md) for agent-specific
operating instructions.

## What It Can Do

- Read server state: channels, roles, members, permissions, and snapshots.
- Create, rename, move, lock, unlock, and delete channels.
- Create and manage roles.
- Send messages, announcements, links, DMs, pins, and cleanup actions.
- Run basic moderation commands such as timeout, kick, ban, and unban.
- Act as a reusable foundation for AI-driven Discord server automation.

## Setup for Users and Agents

### 1. Create and invite the bot

1. Go to <https://discord.com/developers/applications> and create an application.
2. Open **Bot**, reset/copy the token, and use it as `DISCORD_TOKEN`.
3. Under **Privileged Gateway Intents**, enable:
   - **Message Content Intent**
   - **Server Members Intent**
4. Open **OAuth2 -> URL Generator**.
   - Scopes: `bot`
   - Recommended permissions for the full command set:
     - View Channels
     - Send Messages
     - Embed Links
     - Read Message History
     - Manage Channels
     - Manage Roles
     - Manage Messages
     - Moderate Members
     - Kick Members
     - Ban Members
5. Invite the bot and put its role high enough in the role list. Discord will
   not let the bot manage roles or members at or above its highest role.

Using Administrator also works for testing, but granular permissions are safer.

### 2. Install and run locally

```bash
pip install -r requirements.txt
copy .env.example .env
python bot.py
```

Edit `.env` before running and paste your real bot token. Keep `.env` local and
private; agents should never print or commit it.

## Environment

## Discord → OpenCode on Render

`!opencode your prompt` (aliases `!oc` and `!ai`) runs OpenCode on the bot
host and returns its text reply in the same Discord channel. Each request starts
a new session. Existing authorization rules apply. Only one OpenCode request
runs at a time; requests time out after 180 seconds by default.

Deploy this repository as a Render Blueprint using `render.yaml`. It creates
a **paid background worker**, with Python and OpenCode installed by the Dockerfile.
Set `DISCORD_TOKEN`, `AUTHORIZED_USER_IDS`, and `OPENCODE_MODEL` (a
`provider/model` identifier). Add your chosen provider's API key to the worker's
environment, for example `ANTHROPIC_API_KEY`. Enable the Discord intents described
above. Then try `!oc say hello` in Discord.

Optional environment settings:

- `OPENCODE_CHANNEL_ID`: limit OpenCode requests to a private channel.
- `OPENCODE_TIMEOUT_SECONDS`: maximum duration, default `180`.
- `OPENCODE_WORKDIR`: project directory, default `/workspace` in Docker.
- `OPENCODE_BIN`: executable path, default `opencode`.

The Docker workspace starts empty. To work on a project, include it in a custom
image or provision it in the worker workspace. Render's local filesystem is
ephemeral; attach a persistent disk and set `OPENCODE_WORKDIR` to a directory on
it if edits must survive deployments. Agent tool permissions come from your
OpenCode configuration; interactive approval prompts cannot be answered through
this bridge. This runs prompts via `opencode run`, not an interactive terminal.
Only give access to trusted users, and use a private channel for project output.
The bot token is omitted from the child environment, but an agent with file
access can still read files in its workspace; keep secrets out of that directory.

See the [OpenCode CLI documentation](https://opencode.ai/docs/cli/) and
[Render background workers](https://render.com/docs/background-workers).

### Core bot variables

| Variable | Required | Purpose |
|---|---|---|
| `DISCORD_TOKEN` | yes | Bot token from the Discord Developer Portal. |
| `AUTHORIZED_USER_IDS` | no | Comma-separated Discord user IDs allowed to run commands. Empty means only the server owner is authorized. |
| `COMMAND_PREFIX` | no | Command prefix. Defaults to `!`. |

To get a Discord user ID, enable **Settings -> Advanced -> Developer Mode**,
right-click the user, then choose **Copy User ID**.

## Discord Commands

Type `!help` in Discord for the live command list. Replace `!` with your
configured `COMMAND_PREFIX` if you changed it.

### Diagnostics and inventory

- `!ping` - check that the bot is online.
- `!server-info` - show server counts and metadata.
- `!bot-permissions` - show important bot permissions missing in the current channel.
- `!list-channels` - list channels grouped by category.
- `!channel-info #channel` - show channel details.
- `!list-roles` - list roles with IDs, positions, colors, and member counts.
- `!role-info RoleName` - show role details and permissions.
- `!list-members [limit] [search]` - list members, default limit 50, max 200.
- `!member-info @user` - show member details.
- `!server-snapshot` - compact snapshot of channels, roles, and member counts.

### Channel and category management

- `!create-channel name [category]` - create a text channel.
- `!create-voice name [category]` - create a voice channel.
- `!create-category name` - create a category.
- `!rename-channel #channel new-name` - rename a channel.
- `!delete-channel #channel` - delete a channel.
- `!move-channel #channel CategoryName` - move a channel to a category.
- `!move-channel #channel none` - remove a channel from its category.
- `!set-topic #channel topic text` - set or clear a text channel topic.
- `!set-slowmode #channel seconds` - set channel slowmode, 0 to 21600 seconds.
- `!lock-channel #channel [role]` - deny Send Messages for a role, default `@everyone`.
- `!unlock-channel #channel [role]` - reset the Send Messages overwrite.

### Messaging

- `!say #channel message` - post a message.
- `!dm @user message` - direct-message a member.
- `!link #channel https://example.com [description]` - post a link embed.
- `!announce #channel message` - post an announcement embed.
- `!purge 25` - delete recent messages in the current channel, max 100.
- `!pin message_id` - pin a message in the current channel.
- `!unpin message_id` - unpin a message in the current channel.

### Role management

- `!create-role RoleName` - create a role.
- `!rename-role RoleName New Name` - rename a role. Quote multi-word role names if needed.
- `!delete-role RoleName` - delete a role.
- `!give-role @user RoleName` - assign a role.
- `!remove-role @user RoleName` - remove a role.
- `!set-role-color RoleName #5865F2` - set a role color.
- `!set-role-mentionable RoleName true` - make a role mentionable or not.

### Member management

- `!set-nick @user New Nick` - set or clear a nickname.
- `!timeout @user 10 reason` - timeout a member for minutes, max 40320.
- `!untimeout @user reason` - remove timeout.
- `!kick @user reason` - kick a member.
- `!ban @user reason` - ban a member.
- `!unban user_id reason` - unban by user ID.

## Security notes

- Never commit `.env`; it contains the bot token.
- Keep `AUTHORIZED_USER_IDS` tight. Authorized users can delete channels, manage
  roles, and moderate members.
- Rotate `DISCORD_TOKEN` immediately if it leaks.
- Discord role hierarchy still applies. If a command fails with a permission
  error, run `!bot-permissions` and check the bot role position.
- Let agents enhance `bot.py` when needed, but make them run syntax/import
  checks before using the changed bot.
