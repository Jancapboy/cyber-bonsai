# Cyber Bonsai - Development Specification

## 1. 项目结构

```
cyber-bonsai/
├── src/
│   ├── __init__.py
│   ├── bonsai.py          # 核心生长逻辑
│   ├── github_api.py      # GitHub 数据获取
│   ├── renderer.py        # ASCII 渲染
│   ├── cli.py             # 命令行接口
│   └── config.py          # 配置管理
├── tests/
│   ├── __init__.py
│   ├── test_bonsai.py     # 生长逻辑测试
│   ├── test_github_api.py # API 测试（mock）
│   ├── test_renderer.py   # 渲染测试
│   └── conftest.py        # pytest 配置
├── .github/
│   └── workflows/
│       └── ci.yml         # CI 配置
├── docs/
│   └── screenshots/       # 截图/GIF
├── PRD.md               # 产品需求文档
├── DEV_SPEC.md          # 开发规范（本文件）
├── README.md            # 项目说明
├── CHANGELOG.md         # 变更日志
├── pyproject.toml       # Python 项目配置
├── requirements.txt     # 依赖列表
├── requirements-dev.txt # 开发依赖
└── .gitignore
```

---

## 2. 开发流程

### 2.1 需求阶段（必须）

**规则**: 任何功能开发前必须完成以下步骤

1. **PRD 条目**: 在 PRD.md 中明确功能描述
2. **技术方案**: 在 Issue 中讨论实现方案
3. **任务拆分**: 大功能拆分为可独立完成的子任务

**禁止**: 直接写代码再补文档

### 2.2 开发阶段

#### 2.2.1 分支管理
```bash
# 从 main 创建 feature 分支
git checkout -b feature/M2-growth-logic

# 分支命名规范
feature/M{数字}-{简短描述}   # 新功能
fix/issue-{数字}-{描述}      # Bug 修复
docs/{描述}                  # 文档更新
```

#### 2.2.2 代码提交规范
```
<type>: <subject>

<body> (可选)

<footer> (可选)

type:
- feat: 新功能 (对应 M 里程碑)
- fix: Bug 修复
- docs: 文档更新
- style: 代码格式调整（不影响功能）
- refactor: 重构（不改变行为）
- test: 测试相关
- chore: 杂项（依赖更新、配置调整等）

示例:
feat: implement growth stage calculation

- Add BonsaiGrowth class
- Implement 4-stage growth logic
- Add unit tests

Closes #4
```

#### 2.2.3 代码质量门禁
**提交前必须检查**:
```bash
# 1. 格式化
black src/ tests/ --line-length=100

# 2. Lint 检查
ruff check src/ tests/

# 3. 类型检查（可选但推荐）
mypy src/

# 4. 测试
pytest tests/ --cov=src --cov-report=term-missing

# 5. 覆盖率必须 > 80%
```

**不通过门禁禁止提交**

### 2.3 代码审查

#### 2.3.1 PR 模板
```markdown
## 描述
简要描述这个 PR 做了什么

## 变更类型
- [ ] Bug 修复
- [ ] 新功能
- [ ] 文档更新
- [ ] 重构

## 检查清单
- [ ] 代码通过 ruff lint
- [ ] 代码通过 black 格式化
- [ ] 单元测试通过
- [ ] 覆盖率 > 80%
- [ ] 相关文档已更新

## 相关 Issue
Closes #{数字}
```

#### 2.3.2 审查标准
- 代码逻辑清晰
- 有适当的注释和 docstring
- 错误处理完善
- 测试覆盖新增代码

### 2.4 发布阶段

#### 2.4.1 版本号规则（SemVer）
```
主版本.次版本.修订号

- 主版本: 不兼容的 API 变更
- 次版本: 向下兼容的功能添加
- 修订号: 向下兼容的问题修复
```

#### 2.4.2 发布流程
1. 更新 CHANGELOG.md
2. 修改版本号（pyproject.toml）
3. 创建 PR 到 main
4. 通过 CI 检查
5. 合并后打 tag: `git tag v0.1.0`
6. 推送 tag 触发 release workflow

---

## 3. 代码规范

### 3.1 格式
- **工具**: black
- **行长度**: 100 字符
- **引号**: 双引号优先

### 3.2 Lint
- **工具**: ruff
- **规则**: E, F, I, N, W, UP, B, C4, SIM
- **配置**（pyproject.toml）:
```toml
[tool.ruff]
line-length = 100
select = ["E", "F", "I", "N", "W", "UP", "B", "C4", "SIM"]
ignore = ["E501"]  # black 处理行长度

[tool.ruff.pydocstyle]
convention = "google"
```

### 3.3 类型注解
- **要求**: 公共 API 必须有类型注解
- **工具**: mypy（可选检查）

```python
# 示例
def calculate_stage(contributions: float) -> GrowthStage:
    """Calculate growth stage based on contribution score.
    
    Args:
        contributions: The contribution score (0-100+)
        
    Returns:
        The corresponding growth stage
        
    Raises:
        ValueError: If contributions is negative
    """
    if contributions < 0:
        raise ValueError("Contributions cannot be negative")
    # ...
```

### 3.4 文档
- **公共 API**: Google 风格 docstring
- **模块**: 文件顶部说明用途
- **复杂逻辑**: 行内注释说明"为什么"

---

## 4. 测试规范

### 4.1 测试结构
```
tests/
├── conftest.py          # 共享 fixture
├── test_bonsai.py       # 核心逻辑测试
├── test_github_api.py   # API 测试（必须 mock）
└── test_renderer.py     # 渲染测试
```

### 4.2 测试要求
- **覆盖率**: > 80%
- **Mock 策略**: GitHub API 必须 mock，不依赖网络
- **Fixture**: 共享数据放在 conftest.py

### 4.3 测试示例
```python
# tests/test_bonsai.py
import pytest
from src.bonsai import BonsaiGrowth, GrowthStage

@pytest.fixture
def growth():
    return BonsaiGrowth()

def test_sprout_stage(growth):
    """Test that 0-10 contributions maps to sprout stage."""
    assert growth.calculate_stage(0) == GrowthStage.SPROUT
    assert growth.calculate_stage(5) == GrowthStage.SPROUT
    assert growth.calculate_stage(10) == GrowthStage.SPROUT

def test_growth_stage(growth):
    """Test that 11-30 contributions maps to growth stage."""
    assert growth.calculate_stage(11) == GrowthStage.GROWTH
    assert growth.calculate_stage(20) == GrowthStage.GROWTH
    assert growth.calculate_stage(30) == GrowthStage.GROWTH

def test_negative_contributions(growth):
    """Test that negative contributions raise ValueError."""
    with pytest.raises(ValueError, match="cannot be negative"):
        growth.calculate_stage(-1)
```

---

## 5. CI/CD

### 5.1 GitHub Actions Workflow
```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements-dev.txt
    
    - name: Lint with ruff
      run: ruff check src/ tests/
    
    - name: Format check with black
      run: black --check src/ tests/
    
    - name: Test with pytest
      run: pytest tests/ --cov=src --cov-report=xml
    
    - name: Check coverage
      run: |
        coverage=$(python -c "import xml.etree.ElementTree as ET; tree = ET.parse('coverage.xml'); root = tree.getroot(); print(root.attrib['line-rate'])")
        if (( $(echo "$coverage < 0.80" | bc -l) )); then
          echo "Coverage $coverage is below 80%"
          exit 1
        fi
```

### 5.2 检查项清单
- [ ] ruff lint 通过
- [ ] black 格式检查通过
- [ ] pytest 全部通过
- [ ] 覆盖率 > 80%
- [ ] Python 3.10/3.11/3.12 全部通过

---

## 6. Issue 规范

### 6.1 标签定义
| 标签 | 颜色 | 用途 |
|------|------|------|
| `growth` | #90EE90 | 生长阶段相关功能 |
| `daily` | #87CEEB | 每日浇水记录 |
| `feature` | #A2EEEF | 新功能开发 |
| `bug` | #D73A4A | 缺陷修复 |
| `enhancement` | #A2EEEF | 功能优化 |
| `docs` | #0075CA | 文档相关 |
| `M2` | #FFD700 | 里程碑 M2 任务 |
| `M3` | #FFD700 | 里程碑 M3 任务 |

### 6.2 Issue 模板
```markdown
## 描述
简要描述这个功能/问题

## 需求/期望行为
详细说明应该做什么

## 验收标准
- [ ] 标准 1
- [ ] 标准 2
- [ ] 标准 3

## 参考
- PRD 章节: X.X
- 相关 Issue: #数字

## 预估工作量
X 小时 / X 天
```

---

## 7. 配置管理

### 7.1 用户配置
```python
# ~/.config/cyber-bonsai/config.json
{
    "username": "Jancapboy",
    "token": null,  # 或从环境变量读取
    "cache_duration": 3600,
    "time_window": 30,
    "color_scheme": "auto"  # auto/always/never
}
```

### 7.2 环境变量
```bash
export CYBER_BONSAI_USERNAME="Jancapboy"
export CYBER_BONSAI_TOKEN="ghp_xxxx"
export CYBER_BONSAI_CACHE_DURATION="3600"
```

**优先级**: 命令行参数 > 环境变量 > 配置文件 > 默认值

---

## 8. 错误处理

### 8.1 错误码定义
| 错误码 | 描述 | 用户提示 |
|--------|------|---------|
| 1 | 网络错误 | "无法连接到 GitHub，请检查网络" |
| 2 | API Rate Limit | "API 调用次数超限，请稍后再试或使用 Token" |
| 3 | 认证失败 | "认证失败，请检查 Token 是否有效" |
| 4 | 用户不存在 | "用户 {username} 不存在" |
| 5 | 配置错误 | "配置文件格式错误: {详情}" |

### 8.2 错误处理原则
- 所有外部调用（API、文件）必须有 try-except
- 错误信息必须对用户友好
- 调试信息用 `-v` 选项显示

---

## 9. 文档维护

### 9.1 文档更新时机
- PRD: 需求变更时立即更新
- DEV_SPEC: 流程/规范调整时更新
- README: 功能变化时更新
- CHANGELOG: 每次发布前更新

### 9.2 文档格式
- Markdown 格式
- 中文为主，代码/术语保留英文
- 表格用于对比/列表
- 代码块标注语言

---

## 10. 开发环境

### 10.1 初始化
```bash
# 1. 克隆仓库
git clone https://github.com/Jancapboy/cyber-bonsai.git
cd cyber-bonsai

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements-dev.txt

# 4. 安装 pre-commit（推荐）
pre-commit install
```

### 10.2 开发命令
```bash
# 运行测试
pytest

# 运行测试并查看覆盖率
pytest --cov=src --cov-report=term-missing

# 格式化代码
black src/ tests/

# Lint 检查
ruff check src/ tests/

# 本地运行
cd src && python -m cli
```
