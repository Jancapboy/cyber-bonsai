# Cyber Bonsai

[![CI](https://github.com/Jancapboy/cyber-bonsai/actions/workflows/ci.yml/badge.svg)](https://github.com/Jancapboy/cyber-bonsai/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/Jancapboy/cyber-bonsai/branch/main/graph/badge.svg)](https://codecov.io/gh/Jancapboy/cyber-bonsai)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Terminal ASCII bonsai that grows or withers based on your GitHub activity 🌱

## What is this?

Cyber Bonsai is a terminal tool that visualizes your GitHub contribution activity as an ASCII bonsai tree. Every commit, issue, and PR becomes "water" for your bonsai, helping it grow from a 🌱 sprout to a 🌲 mighty tree.

## Features

- 🌱 **4 Growth Stages**: Sprout → Growth → Mature → Full
- 📊 **GitHub Integration**: Fetches your real contribution data
- 🎨 **Beautiful ASCII Art**: Terminal-native visualization with colors
- ⚡ **Fast**: Local caching, < 3s cold start
- 🔧 **Configurable**: Time windows, color schemes, custom usernames

## Installation

```bash
# From PyPI (when published)
pip install cyber-bonsai

# From source
git clone https://github.com/Jancapboy/cyber-bonsai.git
cd cyber-bonsai
pip install -e .
```

## Usage

```bash
# Show your bonsai status
cyber-bonsai

# Show with custom username
cyber-bonsai -u yourusername

# Show historical trend
cyber-bonsai history

# Configure default settings
cyber-bonsai config set username yourusername
```

## Growth System

| Stage | Contributions | Icon |
|-------|--------------|------|
| Sprout | 0-10 | 🌱 |
| Growth | 11-30 | 🌿 |
| Mature | 31-60 | 🌳 |
| Full | 61+ | 🌲 |

## Development

See [DEV_SPEC.md](DEV_SPEC.md) for development guidelines.

## License

MIT License - see [LICENSE](LICENSE) file.
