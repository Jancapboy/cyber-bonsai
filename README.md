# 🌳 Cyber Bonsai

Terminal ASCII bonsai that grows or withers based on your GitHub activity.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🎮 How it works

Your bonsai's health depends on your GitHub activity over the last 30 days:

| Activity Score | State | Appearance |
|---------------|-------|------------|
| < 5 | ☠️ DEAD | Bare trunk |
| 5-14 | 🍂 WITHERED | Sparse leaves |
| 15-29 | 🌱 STRUGGLING | Growing |
| 30-49 | 🌿 HEALTHY | Lush |
| 50-79 | 🌳 THRIVING | Full canopy |
| 80+ | ✨ LEGENDARY | Epic tree |

Activity score is calculated from:
- Push events: +2 points
- PRs/Create events: +3 points  
- Issues: +1 point
- Other: +0.5 point

## 🚀 Usage

```bash
# Install
pip install -r requirements.txt

# Run with GitHub username
python bonsai.py your_github_username

# Or set env variable
export GITHUB_USERNAME=yourname
python bonsai.py
```

## 🔧 Optional: GitHub Token

For private repos or higher API limits:
```bash
export GITHUB_TOKEN=your_token_here
```

## 📦 Install as CLI tool

```bash
chmod +x bonsai.py
sudo ln -s $(pwd)/bonsai.py /usr/local/bin/cyber-bonsai
cyber-bonsai yourname
```

## 🎯 Project Status

Part of the [10 creative projects challenge](https://github.com/Jancapboy/cyber-bonsai).

## 📄 License

MIT - Do whatever you want.
