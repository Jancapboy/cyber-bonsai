# Cyber Bonsai - Product Requirements Document

## 1. 产品概述

### 1.1 产品定义
赛博盆栽是一个将 GitHub 贡献活动可视化为 ASCII 盆栽生长的终端工具。用户的每一次 Issue、Commit、PR 都会成为"浇水"行为，让盆栽从 🌱 萌芽成长为 🌲 参天大树。

### 1.2 目标用户
- 想要可视化自己 GitHub 活跃度的开发者
- 喜欢终端工具和 ASCII 艺术的技术爱好者
- 需要 gamification 激励自己保持贡献习惯的人

### 1.3 核心价值
- **可视化**: 把抽象的贡献数据变成具象的盆栽生长
- **激励**: 通过 gamification 鼓励持续贡献
- **轻量**: 终端运行，无需 GUI

---

## 2. 核心功能

### 2.1 生长系统（核心算法）

#### 2.1.1 生长阶段定义
| 阶段 | 贡献数范围 | 图标 | ASCII 复杂度 |
|------|-----------|------|-------------|
| 萌芽期 | 0-10 | 🌱 | 简单（<50字符） |
| 生长期 | 11-30 | 🌿 | 中等（50-150字符） |
| 成熟期 | 31-60 | 🌳 | 复杂（150-300字符） |
| 完全体 | 61+ | 🌲 | 极复杂（>300字符） |

#### 2.1.2 贡献计算规则
```python
# 伪代码
contributions = (
    commits_count * 1.0 +      # 每次提交算 1 分
    issues_count * 1.5 +       # 每个 Issue 算 1.5 分
    pr_count * 2.0 +           # 每个 PR 算 2 分
    review_count * 0.5         # 每次 Review 算 0.5 分
)
```

#### 2.1.3 时间窗口
- **默认**: 最近 30 天
- **可配置**: 7天/30天/90天/365天
- **衰减机制**: 超过 30 天的贡献权重递减（每天衰减 5%）

### 2.2 数据来源

#### 2.2.1 GitHub API 端点
```
GET /users/{username}/events/public
GET /users/{username}/repos
```

#### 2.2.2 认证方式
- **方式1**: Personal Access Token (推荐)
- **方式2**: GitHub CLI (gh auth status)
- **方式3**: 无认证（公开数据，有 rate limit）

#### 2.2.3 Rate Limit 处理
- 无认证: 60 requests/hour
- 有认证: 5000 requests/hour
- **缓存策略**: 本地缓存 1 小时，避免频繁调用

### 2.3 展示形式

#### 2.3.1 ASCII 艺术规格
```
萌芽期示例:
    🌱
    |
   / \

生长期示例:
    🌿
   /|\
  / | \
 /  |  \

成熟期示例（详细图案见实现）
完全体示例（详细图案见实现）
```

#### 2.3.2 终端输出格式
```
┌─────────────────────────────┐
│     🌱 Cyber Bonsai        │
│                             │
│      [ASCII 图案]           │
│                             │
│  生长阶段: 萌芽期            │
│  贡献积分: 8.5 / 10         │
│  距离下一级: 1.5 分         │
│                             │
│  最近活动:                  │
│  - 2 commits (今天)         │
│  - 1 issue (昨天)           │
└─────────────────────────────┘
```

#### 2.3.3 颜色方案
- 萌芽期: 浅绿色 (#90EE90)
- 生长期: 绿色 (#32CD32)
- 成熟期: 深绿色 (#228B22)
- 完全体: 森林绿 (#006400)

---

## 3. 用户场景

### 3.1 场景一: 日常查看状态
**用户**: 开发者小王
**行为**: 每天早上打开终端，运行 `cyber-bonsai`
**期望**: 看到盆栽当前状态，了解自己的贡献进度
**输出**: 显示 ASCII 盆栽 + 贡献统计

### 3.2 场景二: 贡献后查看变化
**用户**: 开发者小王
**行为**: 提交了一个 PR，然后运行工具
**期望**: 看到盆栽有变化（或提示即将升级）
**输出**: 显示更新后的状态，如果有阶段变化显示动画

### 3.3 场景三: 对比历史
**用户**: 开发者小王
**行为**: 运行 `cyber-bonsai --history`
**期望**: 看到过去 30 天的生长曲线
**输出**: 简单的文本图表显示贡献趋势

---

## 4. 技术方案

### 4.1 技术栈
- **语言**: Python 3.10+
- **依赖**:
  - `requests` (API 调用)
  - `rich` (终端美化，表格/颜色)
  - `click` (CLI 参数解析)
  - `pydantic` (配置验证)
- **API**: GitHub REST API v3

### 4.2 模块设计

```python
# 核心模块
class BonsaiGrowth:
    """生长逻辑核心"""
    def calculate_stage(self, contributions: float) -> GrowthStage
    def get_progress(self) -> tuple[int, int]  # (current, next_level)

class GitHubAPI:
    """GitHub 数据获取"""
    def fetch_contributions(self, username: str, days: int) -> ContributionData
    def _handle_rate_limit(self, response: Response) -> None

class ASCIIRenderer:
    """ASCII 渲染"""
    def render(self, stage: GrowthStage, width: int = 40) -> str
    def render_with_stats(self, data: BonsaiData) -> Panel

class Config:
    """配置管理"""
    username: str
    token: Optional[str]
    cache_duration: int = 3600  # seconds
    time_window: int = 30  # days
```

### 4.3 数据流
```
用户输入 → CLI 解析 → 读取配置 → 检查缓存
                                    ↓
终端输出 ← 渲染 ASCII ← 计算生长 ← 获取贡献数据 ← GitHub API
```

### 4.4 缓存策略
- **位置**: `~/.cache/cyber-bonsai/`
- **格式**: JSON
- **有效期**: 1 小时（可配置）
- **键值**: `{username}_{time_window}_{date}`

---

## 5. CLI 设计

### 5.1 命令结构
```bash
cyber-bonsai [OPTIONS] [COMMAND]

Commands:
  show        显示当前状态（默认）
  history     显示历史趋势
  config      配置管理
  version     显示版本

Options:
  -u, --username TEXT    GitHub 用户名
  -t, --token TEXT       GitHub Token
  -w, --window INTEGER   时间窗口（天）
  --no-cache             禁用缓存
  --no-color             禁用颜色
  -v, --verbose          详细输出
  --help                 显示帮助
```

### 5.2 配置管理
```bash
cyber-bonsai config set username Jancapboy
cyber-bonsai config set token ghp_xxxx
cyber-bonsai config show
```

---

## 6. 里程碑

### M1: 项目初始化 ✅
- [x] 创建仓库
- [x] 编写 PRD
- [x] 编写开发规范

### M2: 核心生长逻辑
- [ ] 实现生长阶段计算
- [ ] 实现贡献积分算法
- [ ] 单元测试 > 80%

### M3: GitHub API 集成
- [ ] 实现 API 客户端
- [ ] 实现认证机制
- [ ] 实现缓存机制
- [ ] Rate Limit 处理

### M4: ASCII 渲染器
- [ ] 设计 4 个阶段的 ASCII 图案
- [ ] 实现渲染引擎
- [ ] 集成 rich 库美化输出

### M5: CLI 接口
- [ ] 实现命令解析
- [ ] 实现配置管理
- [ ] 实现所有命令

### M6: CI/CD 配置
- [ ] GitHub Actions workflow
- [ ] 自动测试
- [ ] 自动发布到 PyPI

### M7: 文档完善
- [ ] README 完善
- [ ] 使用示例
- [ ] 截图/GIF 展示

---

## 7. 非功能需求

### 7.1 性能
- 冷启动时间 < 3 秒（含 API 调用）
- 热启动时间 < 0.5 秒（使用缓存）
- 内存占用 < 50MB

### 7.2 可靠性
- API 失败时有降级方案（使用缓存或显示错误信息）
- 网络超时处理（5 秒超时）
- 优雅的错误提示

### 7.3 兼容性
- Python 3.10, 3.11, 3.12
- Linux, macOS, Windows
- 支持主流终端（xterm, iTerm2, Windows Terminal）

### 7.4 安全
- Token 存储使用 keyring 或环境变量
- 不记录敏感信息到日志
- 缓存文件权限 600

---

## 8. 风险与假设

### 8.1 风险
| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| GitHub API 变更 | 高 | 封装 API 层，便于修改 |
| Rate Limit 限制 | 中 | 实现缓存和退避机制 |
| 终端兼容性问题 | 低 | 测试主流终端，提供 --no-color 选项 |

### 8.2 假设
- 用户有基本的终端使用经验
- 用户有 GitHub 账号
- 网络可以访问 GitHub API
