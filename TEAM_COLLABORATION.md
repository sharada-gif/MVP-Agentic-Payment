# Team Collaboration Guide

This guide explains how to share the API connector feature branch with team members.

## Current Branch

The API connector code is on branch: `feature/api-connector`

## Setting Up Remote Repository

If you haven't set up a remote repository yet:

### Option 1: GitHub

1. **Create a new repository on GitHub** (or use existing):
   ```bash
   # On GitHub: Create new repository (e.g., MVP-Agentic-Payment)
   ```

2. **Add remote and push**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/MVP-Agentic-Payment.git
   git push -u origin feature/api-connector
   ```

### Option 2: GitLab

1. **Create a new project on GitLab**

2. **Add remote and push**:
   ```bash
   git remote add origin https://gitlab.com/YOUR_USERNAME/MVP-Agentic-Payment.git
   git push -u origin feature/api-connector
   ```

### Option 3: Bitbucket

1. **Create a new repository on Bitbucket**

2. **Add remote and push**:
   ```bash
   git remote add origin https://bitbucket.org/YOUR_USERNAME/MVP-Agentic-Payment.git
   git push -u origin feature/api-connector
   ```

## Sharing with Team Members

### Step 1: Push Your Branch

```bash
# Make sure you're on the feature branch
git checkout feature/api-connector

# Push to remote
git push -u origin feature/api-connector
```

### Step 2: Grant Access

#### For GitHub:
1. Go to repository settings
2. Click "Collaborators" or "Manage access"
3. Add team members by username or email
4. Set permission level (Read, Write, or Admin)

#### For GitLab:
1. Go to project settings → Members
2. Add team members by username or email
3. Set role (Guest, Reporter, Developer, Maintainer, Owner)

#### For Bitbucket:
1. Go to repository settings → User and group access
2. Add users or groups
3. Set permission (Read, Write, or Admin)

### Step 3: Team Members Clone and Checkout

Team members should run:

```bash
# Clone the repository (first time only)
git clone <repository-url>
cd MVP-Agentic-Payment-main

# Or if already cloned, fetch the new branch
git fetch origin
git checkout feature/api-connector

# Install dependencies
cd api-connector
pip install -r requirements.txt
```

## Working Together

### Daily Workflow

1. **Pull latest changes**:
   ```bash
   git checkout feature/api-connector
   git pull origin feature/api-connector
   ```

2. **Create feature branch for your work**:
   ```bash
   git checkout -b feature/api-connector-<your-feature>
   # Make changes...
   git add .
   git commit -m "Description of changes"
   git push origin feature/api-connector-<your-feature>
   ```

3. **Create Pull/Merge Request**:
   - Push your feature branch
   - Create a Pull Request (GitHub) or Merge Request (GitLab) to `feature/api-connector`
   - Request review from team members
   - Merge after approval

### Branch Protection (Recommended)

Set up branch protection rules:
- Require pull request reviews
- Require status checks to pass
- Prevent force pushes
- Require branches to be up to date

## Project Structure

```
MVP-Agentic-Payment-main/
├── api-connector/          # API Extraction Connector (NEW)
│   ├── __main__.py        # CLI interface
│   ├── extractor.py       # LLM-based API extractor
│   ├── terraform_parser.py # Terraform parser
│   ├── schema.py          # Normalized schemas
│   ├── unifier.py         # Unified output generator
│   ├── visualizer.py      # HTML dashboard
│   ├── prompts.py         # LLM prompts
│   ├── requirements.txt   # Dependencies
│   ├── README.md          # Overview
│   ├── ARCHITECTURE.md    # Architecture docs
│   ├── EXTENSIBILITY.md   # Extension guide
│   ├── EXAMPLE.md         # Usage examples
│   └── dashboard.html     # Generated dashboard
├── apps/                  # Application services
├── terraform/             # Infrastructure as code
└── ...                    # Other project files
```

## Team Member Onboarding

### Prerequisites

1. **Python 3.9+**
   ```bash
   python3 --version
   ```

2. **Git**
   ```bash
   git --version
   ```

3. **OpenAI API Key** (for LLM extraction):
   ```bash
   export OPENAI_API_KEY=sk-your-key-here
   ```

### Setup Steps

1. **Clone repository**:
   ```bash
   git clone <repository-url>
   cd MVP-Agentic-Payment-main
   ```

2. **Checkout feature branch**:
   ```bash
   git checkout feature/api-connector
   ```

3. **Install dependencies**:
   ```bash
   cd api-connector
   pip install -r requirements.txt
   ```

4. **Test the connector**:
   ```bash
   # Extract APIs (requires OpenAI API key)
   python3 api-connector/__main__.py extract \
       --source-dir ../apps \
       --output apis.json

   # Parse Terraform
   python3 api-connector/__main__.py terraform \
       --terraform-dir ../terraform \
       --output infrastructure.json

   # Generate dashboard
   python3 api-connector/__main__.py unify \
       --apis apis.json \
       --terraform infrastructure.json \
       --output unified.json \
       --html dashboard.html
   ```

## Collaboration Best Practices

1. **Communication**:
   - Use GitHub/GitLab Issues for bugs and features
   - Use Pull/Merge Requests for code reviews
   - Keep commits atomic and well-documented

2. **Code Standards**:
   - Follow PEP 8 for Python code
   - Write docstrings for functions/classes
   - Add comments for complex logic

3. **Testing**:
   - Test your changes locally before pushing
   - Add tests for new features
   - Update documentation as needed

4. **Branch Naming**:
   - `feature/` - New features
   - `fix/` - Bug fixes
   - `docs/` - Documentation updates
   - `refactor/` - Code refactoring

## Common Commands

```bash
# Check current branch
git branch

# Switch branch
git checkout feature/api-connector

# Pull latest changes
git pull origin feature/api-connector

# Create and switch to new branch
git checkout -b feature/your-feature

# Stage changes
git add .

# Commit changes
git commit -m "Your commit message"

# Push to remote
git push origin feature/your-feature

# View commit history
git log --oneline

# View changes
git diff

# View status
git status
```

## Questions or Issues?

- Check `api-connector/README.md` for overview
- Check `api-connector/ARCHITECTURE.md` for architecture details
- Check `api-connector/EXAMPLE.md` for usage examples
- Create an Issue in the repository for bugs or questions
