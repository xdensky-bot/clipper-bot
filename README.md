# Clipper Bot Full OS v1

Discord control center for a TernakKlip-style clipping workflow.

## Rules
- Manual TikTok posting only. The bot never uploads to TikTok.
- After posting manually, use `/track <TikTok URL>`.
- Never commit Discord tokens, passwords, cookies, or private credentials.
- TernakKlip integration is an adapter: use only an official/permitted mechanism; never guess private endpoints or bypass protections.
- Unknown campaign requirements stay UNKNOWN.

## Included
Campaign Radar, detail, filtering, opportunity scoring, brief/rules parser, content angles/hooks, compliance gate, manual TikTok tracker, analytics, earnings calculator, alerts, JSON import/export, connector status, and Discord buttons/select menus.

## Android/Termux
Install only:
`pip install -U discord.py`
Then set `DISCORD_TOKEN` and run:
`python main.py`

## Commands
`/home` `/campaigns` `/detail` `/filter` `/score` `/brief` `/generate` `/check` `/track` `/analytics` `/earnings` `/connector` `/import_campaigns` `/export_data` `/settings`

Actual AI/FFmpeg rendering and an official TernakKlip connector are deliberately kept as adapters so the bot does not rely on unsafe/private access.
