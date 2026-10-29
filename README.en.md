# Miku AstrBot Plugins

**English** | [简体中文](README.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![AstrBot](https://img.shields.io/badge/AstrBot-%3E%3D4.4.0-blue)](https://github.com/AstrBotDevs/AstrBot)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)

Three Hatsune Miku–styled plugins for [AstrBot](https://github.com/AstrBotDevs/AstrBot), plus a ready-to-use persona template.

> **Unofficial fan project.** Hatsune Miku is a character of Crypton Future Media. This project is not affiliated with or endorsed by Crypton, SEGA, or any official party. For personal, non-commercial use only.

![Nine emotion stickers: happy / shy / smug / angry / aggrieved / popcorn / goodnight / love / surprised](demo/sticker_preview.png)

## What's included

| Plugin | What it does |
|---|---|
| `miku_sticker` | Sends a local sticker based on an emotion tag in the reply; optionally auto-collects images from a group and classifies them |
| `miku_image_limit` | Caps the number of images per LLM request to keep context (and cost) under control |
| `miku_greeting` | Daily good-morning / good-night messages and festival easter eggs |
| `persona/miku_persona_template.md` | Hatsune Miku persona prompt — fill in the placeholders and paste it into AstrBot |

## Plugins

### miku_sticker

When the bot's reply contains `[表情:开心]` (an emotion tag), the plugin strips the tag and sends a random image from `stickers/开心/` instead.

- Supported categories: `开心` `害羞` `得意` `生气` `委屈` `吃瓜` `晚安` `爱心` `惊讶`
  (happy / shy / smug / angry / aggrieved / popcorn / goodnight / love / surprised)
- **Sticker images are NOT bundled** — this is a copyright matter. Prepare your own and drop them into the matching folders (`.jpg .png .gif .webp`).
- Empty folder → the tag is silently removed, no error.
- Optional: auto-collect images in specified groups and classify them with a vision model (disabled by default; see `ALLOWED_GROUPS` in the source).

### miku_image_limit

Trims images before the request reaches the model: at most 3 images from the current message, and overflow images in history are replaced with a `[图片]` text placeholder. Useful when people flood a group chat with pictures.

### miku_greeting

| Time window | Action |
|---|---|
| 08:00–09:29 | Good morning |
| after 23:30 | Good night |
| 09:00–20:59 | Festival easter egg (New Year, Valentine's, 3/9, 8/31, Halloween, Christmas Eve, Christmas) |

Each type fires at most once per day; state is stored in `data/state.json`, so restarts don't cause duplicates.

## Installation

1. Copy the three folders under `plugins/` into your AstrBot plugin directory (usually `data/plugins/`)
2. Reload plugins, or enable them in the WebUI
3. Set your own group IDs:
   - `ALLOWED_GROUPS` in `miku_sticker/main.py`
   - `GROUPS` in `miku_greeting/main.py`
4. Put your own stickers into `miku_sticker/stickers/<emotion>/`
5. Persona: open `persona/miku_persona_template.md` and paste everything after the `---` line into the persona's system prompt

## Requirements

- AstrBot >= 4.4.0
- `miku_sticker`'s optional image classification needs a multimodal (vision-capable) model. You can skip it if you don't use auto-collection.

## Cost & safety notes

- **Bring your own API key.** No credentials are included in this repository.
- If you put the bot in a public group, add rate limiting (per-user daily quotas, group allowlists) — otherwise a flood of messages will burn your tokens.
- Never commit `cmd_config.json`, databases, or any token.

## Copyright

- Code: MIT License
- Sticker assets: **not provided.** If you supply your own, please verify you have the right to use them (official stickers and game assets belong to their publishers and should not be redistributed).
- Character: Hatsune Miku © Crypton Future Media. This project follows the principle of non-commercial fan use; it must not be used commercially, nor presented as an official product.

## License

[MIT](LICENSE)
