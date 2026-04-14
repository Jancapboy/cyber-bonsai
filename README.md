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

## Demo

### Sprout Stage (0-10 contributions)
```
┌─────────────────────────────┐
│     🌱 Cyber Bonsai        │
│                             │
│            🌱               │
│            |                │
│           / \               │
│                             │
│  生长阶段: 萌芽期            │
│  贡献积分: 5.0 / 10         │
└─────────────────────────────┘
```

### Growth Stage (11-30 contributions)
```
┌─────────────────────────────┐
│     🌿 Cyber Bonsai        │
│                             │
│           🌿                │
│          /|\                │
│         / | \               │
│        /  |  \              │
│                             │
│  生长阶段: 生长期            │
│  贡献积分: 18.5 / 30        │
└─────────────────────────────┘
```

### Mature Stage (31-60 contributions)
```
┌─────────────────────────────┐
│     🌳 Cyber Bonsai        │
│                             │
│          🌳                 │
│         /|\                 │
│        / | \                │
│       /  |  \               │
│      /___|___\              │
│         |   |               │
│                             │
│  生长阶段: 成熟期            │
│  贡献积分: 45.0 / 60        │
└─────────────────────────────┘
```

### Full Stage (61+ contributions)
```
┌─────────────────────────────┐
│     🌲 Cyber Bonsai        │
│                             │
│            🌲               │
│           /||\              │
│          / || \             │
│         /__||__\            │
│        /   ||   \           │
│       /____||____\          │
│          |    |             │
│          |    |             │
│                             │
│  生长阶段: 完全体            │
│  贡献积分: 85.0 / 85        │
└─────────────────────────────┘
```

## Configuration

Cyber Bonsai can be configured via command line, environment variables, or config file.

### Priority (high to low)
1. Command line arguments
2. Environment variables
3. Config file (`~/.config/cyber-bonsai/config.json`)
4. Default values

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `CYBER_BONSAI_USERNAME` | GitHub username | `Jancapboy` |
| `CYBER_BONSAI_TOKEN` | GitHub Personal Access Token | `ghp_xxx` |
| `CYBER_BONSAI_TIME_WINDOW` | Days to look back | `30` |
| `CYBER_BONSAI_CACHE_DURATION` | Cache validity in seconds | `3600` |

### Config Commands

```bash
# Set username
cyber-bonsai config set username Jancapboy

# Set time window (days)
cyber-bonsai config set time_window 30

# Show current config
cyber-bonsai config show
```

## Growth System

| Stage | Contributions | Icon |
|-------|--------------|------|
| Sprout | 0-10 | 🌱 |
| Growth | 11-30 | 🌿 |
| Mature | 31-60 | 🌳 |
| Full | 61+ | 🌲 |

## Development

See [DEV_SPEC.md](DEV_SPEC.md) for detailed development guidelines.

### Setup

```bash
git clone https://github.com/Jancapboy/cyber-bonsai.git
cd cyber-bonsai
pip install -r requirements-dev.txt
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/test_bonsai.py
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint check
ruff check src/ tests/

# Type check (optional)
mypy src/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and ensure they pass
5. Commit your changes (`git commit -m 'feat: add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) file.
