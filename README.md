# CICD Tool

A **Python CLI tool** that automatically generates GitHub Actions CI/CD workflows from simple YAML configuration files. Standardize your CI/CD practices across projects and save 30-60 minutes per project setup.

---

## 🎯 What It Does

Instead of manually writing 50+ line GitHub Actions workflow files for each project, define your configuration once in a simple YAML file and let CICD Tool generate everything automatically.

### Problem & Solution

**Without CICD Tool:**
- Manual workflow creation (50+ lines of YAML)
- Duplicate code across projects
- Inconsistent CI/CD practices
- Hard to maintain & update

**With CICD Tool:**
- Simple 5-line config file
- Auto-generated, consistent workflows
- Update template once = update all projects
- Version control your CI/CD configuration

---

## ✨ Features

- **Generate Workflows** – Create GitHub Actions workflows from YAML config in seconds
- **Preview Changes** – See diffs before applying with the `plan` command
- **GitHub Integration** – Auto-commit, push, and open PRs for workflow updates
- **Manual Triggers** – Trigger workflows manually and monitor status in real-time
- **Notifications** – Optional Slack integration for workflow completions
- **Configuration-Driven** – Template-based generation with Jinja2
- **Fully Tested** – 4 comprehensive test cases with 100% coverage of core logic

---

## 📋 Quick Example

**Input (`project.yaml`):**
```yaml
service: my-app
provider: github
repository: my-org/my-repo
branches:
  - main
  - develop
```

**Command:**
```bash
python cli.py init --config project.yaml
```

**Output (`.github/workflows/ci.yml`):**
```yaml
name: CI

on:
  push:
    branches: ["main", "develop"]
  workflow_dispatch:

jobs:
  build-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install deps
        run: |
          python -m pip install --upgrade pip
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
      - name: Run tests
        run: |
          if [ -d tests ]; then pytest -q; else echo "No tests/ directory found"; fi
```

---

## 🛠️ CLI Commands

| Command | Description |
|---------|-------------|
| `init` | Generate workflow locally (no git changes) |
| `plan` | Show diff between current and rendered workflow |
| `push` | Commit workflow to branch and open PR |
| `run` | Manually trigger workflow and watch status |
| `status` | List recent workflow runs with status |

---

## 📦 Tech Stack

- **Language:** Python 3.11+
- **CLI Framework:** Click
- **Template Engine:** Jinja2
- **Config Parsing:** PyYAML
- **HTTP Client:** Requests
- **Logging:** Loguru
- **Testing:** Pytest
- **CI/CD Platform:** GitHub Actions

---

## 🚀 Installation & Usage

### Prerequisites
- Python 3.11+
- pip or pip3
- GitHub token (optional, for push/run/status commands)

### Setup

```bash
# Clone repository
git clone https://github.com/amanverma-wsu/cicd-tool.git
cd cicd-tool

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```bash
# 1. Create your project configuration
cat > project.yaml << 'EOF'
service: my-service
provider: github
repository: username/repo-name
branches:
  - main
  - develop
EOF

# 2. Generate workflow locally
python cli.py init --config project.yaml

# 3. Preview changes
python cli.py plan --config project.yaml

# 4. Push to GitHub with PR (requires GITHUB_TOKEN)
export GITHUB_TOKEN=your_token_here
python cli.py push --config project.yaml

# 5. Trigger workflow manually
python cli.py run --config project.yaml --watch

# 6. Check workflow status
python cli.py status --config project.yaml
```

---

## 📊 Project Structure

```
cicd-tool/
├── cli.py                      # Main CLI application
├── action.yml                  # GitHub Action configuration
├── pyproject.toml              # Python package config
├── requirements.txt            # Dependencies
├── README.md                   # This file
├── .github/
│   └── workflows/
│       └── test-cicd-tool.yml # Auto-test workflow
├── templates/
│   └── github/
│       ├── ci.yml.j2          # Jinja2 template
│       └── requirements.txt    # Frozen dependencies
└── tests/
    ├── test_cli.py            # Unit tests
    └── golden.yml             # Test fixture
```

---

## 🤖 Use as GitHub Action

Use CICD Tool in your GitHub workflows:

```yaml
- uses: amanverma-wsu/cicd-tool@main
  with:
    config: 'project.yaml'
    command: 'init'
```

**Inputs:**
- `config` – Path to project config YAML (default: `project.yaml`)
- `command` – CLI command: `init`, `plan`, `push`, `run`, `status` (default: `init`)
- `template-dir` – Optional custom template directory

---

## 🧪 Testing

All tests pass:

```bash
pytest tests/ -v
```

**Test Coverage:**
- ✅ Config loading and validation
- ✅ Workflow generation and rendering
- ✅ Diff detection (plan command)
- ✅ Real workflow files against golden test fixture

---

## 📚 Configuration Schema

**Required fields in `project.yaml`:**

```yaml
service: <string>           # Service name (e.g., my-app)
provider: <string>          # CI provider (currently: github)
repository: <string>        # Repo path (e.g., org/repo)
branches: <list>            # Branches to trigger on (e.g., [main, develop])
```

**Optional fields:**

```yaml
notifications:
  slack_webhook: <url>      # Slack webhook for notifications
```

---

## 🌟 Use Cases

- **Standardize** CI/CD across multiple projects
- **Reduce** setup time per project (30-60 min saved)
- **Ensure** consistent quality gates and testing
- **Version Control** your CI/CD configuration
- **Scale** easily to 10+ projects with single template updates

---

## 🔄 Workflow

1. Create `project.yaml` with your service config
2. Run `python cli.py init` to generate workflow locally
3. Review with `python cli.py plan` to see changes
4. Push to GitHub with `python cli.py push` (creates PR automatically)
5. GitHub Actions runs your generated workflow automatically

---

## 🎓 Complexity Level

**MEDIUM** (5.5/10)

- Not too simple: Uses APIs, templates, CLI framework
- Not too complex: No databases, distributed systems, or advanced algorithms
- Perfect for: Learning DevOps + Python, portfolio projects, production use

**Learn:**
- Python CLI development
- GitHub API integration
- Jinja2 templating
- Test-driven development
- CI/CD principles

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

Contributions welcome! To contribute:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -m 'Add my feature'`
4. Push to branch: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 🗺️ Roadmap

- [ ] Support for Jenkins and GitLab CI
- [ ] Database for tracking workflow metadata
- [ ] Web dashboard for workflow management
- [ ] Kubernetes deployment automation
- [ ] Secrets management (HashiCorp Vault, SOPS)
- [ ] Audit logging and compliance features

---

## 💡 Tips & Tricks

**Generate without git changes:**
```bash
python cli.py init --config project.yaml
```

**See what would change:**
```bash
python cli.py plan --config project.yaml
```

**Customize templates:**
```bash
python cli.py init --config project.yaml --template-dir ./custom-templates
```

**Use custom GitHub token:**
```bash
GITHUB_TOKEN=ghp_xxxx python cli.py push --config project.yaml
```

---

## 🐛 Troubleshooting

**`FileNotFoundError: project.yaml`**
- Ensure config file exists in current directory
- Use absolute path: `python cli.py init --config /full/path/project.yaml`

**`Set GITHUB_TOKEN`**
- Required for `push`, `run`, `status` commands
- Get token at: https://github.com/settings/tokens
- Set: `export GITHUB_TOKEN=your_token_here`

**Workflow not triggering**
- Ensure branches in config match your actual branches
- Check GitHub Actions is enabled in repo settings
- Verify workflow file in `.github/workflows/ci.yml`

---

## 📧 Support

For issues, questions, or suggestions:
- Open a GitHub Issue
- Check existing documentation
- Review test cases for usage examples

---

## ⭐ Show Your Support

If you find CICD Tool helpful, please star the repository!

```
$ git clone https://github.com/amanverma-wsu/cicd-tool.git
$ cd cicd-tool
$ python cli.py init --config project.yaml
```

---

**Happy CI/CD-ing! 🚀**
