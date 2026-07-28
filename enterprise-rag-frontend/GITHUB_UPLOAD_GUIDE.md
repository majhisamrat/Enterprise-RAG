# GitHub Upload Guide - Enterprise RAG Frontend

This guide will walk you through uploading your Enterprise RAG Frontend to GitHub.

## Step 1: Configure Git (First Time Only)

Run these commands to set up your Git configuration:

```powershell
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

Example:
```powershell
git config --global user.name "Samrat Majhi"
git config --global user.email "samrat@example.com"
```

To verify:
```powershell
git config --global --list
```

## Step 2: Initialize the Repository (Already Done ✓)

The repository has already been initialized with `.gitignore` configured.

```powershell
cd "c:\Users\Samratmajhi\Downloads\enterprise-rag\enterprise-rag-frontend"
```

## Step 3: Stage and Commit Changes

### Stage all files
```powershell
git add .
```

### Create initial commit
```powershell
git commit -m "Initial commit: Production-grade Enterprise RAG Frontend with Napkin.ai-inspired design"
```

## Step 4: Create Repository on GitHub

1. Go to [GitHub.com](https://github.com)
2. Click the **+** icon in the top-right corner
3. Select **New repository**
4. Enter repository details:
   - **Repository name**: `enterprise-rag-frontend`
   - **Description**: `Production-grade frontend for Enterprise RAG system with Napkin.ai-inspired design`
   - **Visibility**: Choose **Public** or **Private**
   - **Initialize repository**: Leave unchecked (we already have files)
5. Click **Create repository**

## Step 5: Connect Local Repository to GitHub

After creating the repository on GitHub, you'll see instructions. Copy the HTTPS URL (it looks like `https://github.com/yourusername/enterprise-rag-frontend.git`)

Then run:

```powershell
cd "c:\Users\Samratmajhi\Downloads\enterprise-rag\enterprise-rag-frontend"

# Add the remote repository
git remote add origin https://github.com/yourusername/enterprise-rag-frontend.git

# Rename the default branch to main (recommended)
git branch -M main

# Push to GitHub
git push -u origin main
```

## Step 6: Verify Upload

1. Go to your GitHub repository URL: `https://github.com/yourusername/enterprise-rag-frontend`
2. Verify all files are there
3. Check that the README.md displays correctly

## Optional: Set Up SSH (Recommended for Future Commits)

SSH is more secure than HTTPS. To set up:

### 1. Generate SSH key
```powershell
ssh-keygen -t ed25519 -C "your.email@example.com"
```

When prompted, press Enter to accept default file location, then create a passphrase.

### 2. Add SSH key to GitHub
- Go to GitHub Settings → SSH and GPG keys
- Click "New SSH key"
- Paste the content of `~/.ssh/id_ed25519.pub`
- Click "Add SSH key"

### 3. Update remote URL (optional)
```powershell
# If you want to switch from HTTPS to SSH
git remote set-url origin git@github.com:yourusername/enterprise-rag-frontend.git
```

## Useful Git Commands

```powershell
# Check status
git status

# View commit history
git log --oneline

# Create a new branch
git checkout -b feature/your-feature-name

# Push branch to GitHub
git push -u origin feature/your-feature-name

# View remote URLs
git remote -v

# Undo uncommitted changes
git checkout -- filename

# Amend last commit (before pushing)
git commit --amend
```

## .gitignore Breakdown

Your `.gitignore` file excludes:

- **Dependencies**: `node_modules/`, lock files
- **Build files**: `dist/`, `.vite/`
- **Environment variables**: `.env`, `.env.local`
- **IDE files**: `.vscode/`, `.idea/`
- **OS files**: `.DS_Store`, `Thumbs.db`
- **Logs**: `*.log` files
- **Python files**: If used for backend

## GitHub Repository Best Practices

### 1. Add Topics (Tags)
On your repository page:
- Click "About" (gear icon)
- Add topics like: `react`, `rag`, `typescript`, `tailwind`, `ai`

### 2. Add Branch Protection Rules
- Go to Settings → Branches
- Add rule for `main` branch:
  - Require pull request reviews
  - Require status checks to pass

### 3. Enable GitHub Pages (Optional)
- Go to Settings → Pages
- Source: Deploy from a branch
- Branch: `main` or `gh-pages`
- Folder: `/docs` or `/dist`

### 4. Create GitHub Actions (Optional)
Create `.github/workflows/deploy.yml` for CI/CD:

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Build
        run: npm run build
      
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
```

### 5. Create a .github/CONTRIBUTING.md
Guide for contributors:

```markdown
# Contributing to Enterprise RAG Frontend

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/enterprise-rag-frontend.git`
3. Create a branch: `git checkout -b feature/amazing-feature`
4. Install dependencies: `npm install`
5. Start dev server: `npm run dev`

## Before Submitting PR

- Run `npm run build` to ensure build passes
- Test your changes locally
- Write clear commit messages
- Update README if needed

## PR Guidelines

- Link related issues
- Provide screenshots if UI changes
- Update tests if applicable
```

## Troubleshooting

### Authentication Failed
```powershell
# Clear git credentials and retry
git config --global --unset user.password
git push -u origin main
```

### File too large
Add to `.gitignore`:
```
dist/
node_modules/
*.log
```

### Want to remove accidentally committed files
```powershell
# Remove from Git but keep locally
git rm --cached filename
git commit -m "Remove cached filename"

# Add to .gitignore for future
echo "filename" >> .gitignore
git add .gitignore
git commit -m "Add filename to gitignore"
git push
```

## Common Git Workflow

```powershell
# 1. Create new feature branch
git checkout -b feature/new-feature

# 2. Make changes and commit
git add .
git commit -m "Add new feature"

# 3. Push to GitHub
git push -u origin feature/new-feature

# 4. Create Pull Request on GitHub
# (GitHub will show a prompt after pushing)

# 5. After PR is merged, clean up
git checkout main
git pull origin main
git branch -d feature/new-feature
```

## Next Steps

1. ✅ Create GitHub account if you don't have one
2. ✅ Configure Git with your name and email
3. ✅ Create repository on GitHub
4. ✅ Push your code: `git push -u origin main`
5. ✅ Add description and topics
6. ✅ Enable GitHub Pages (optional)
7. ✅ Set up GitHub Actions (optional)

## Support

For more help:
- [GitHub Docs](https://docs.github.com)
- [Git Book](https://git-scm.com/book)
- [GitHub Desktop](https://desktop.github.com) - GUI alternative to command line

---

Good luck with your Enterprise RAG Frontend! 🚀
