# GitHub Actions Automation Documentation

This document describes the GitHub Actions workflows configured for this repository and their requirements.

## Workflows

### 1. Generate Snake Animation (`snake.yml`)

**Purpose**: Generates a snake animation from GitHub contribution graph  
**Schedule**: Daily at midnight UTC  
**Manual Trigger**: Available via workflow_dispatch  

**What it does**:
- Generates SVG animations showing contributions being eaten by a snake
- Creates both light and dark theme versions
- Pushes results to the `output` branch

**Optimizations**:
- Uses latest v3 of Platane/snk action
- Includes proper permissions for contents:write
- Has concurrency control to prevent duplicate runs
- Includes 10-minute timeout for job safety

**Required Secrets**: 
- `GITHUB_TOKEN` (automatically provided by GitHub)

**Required Permissions**:
- `contents: write` - to push generated files to output branch

---

### 2. Daily Contribution (`daily-contribution.yml`)

**Purpose**: Makes daily automated commits to maintain contribution activity  
**Schedule**: Daily at midnight UTC  
**Manual Trigger**: Available via workflow_dispatch  

**What it does**:
- Updates a timestamp file (`.github/daily-update.txt`)
- Commits the change with a timestamped message
- Ensures consistent daily activity on GitHub profile

**Optimizations**:
- Shallow clone with `fetch-depth: 1` for faster checkout
- Timezone-aware UTC timestamps
- Concurrency control prevents overlapping runs
- 5-minute timeout for safety
- Better error messages and logging

**Required Secrets**: 
- `GITHUB_TOKEN` (automatically provided by GitHub)

**Required Permissions**:
- `contents: write` - to commit and push changes

---

### 3. Advanced Profile Automations (`profile-advanced.yml`)

**Purpose**: Automatically updates dynamic sections of the README  
**Schedule**: Daily at 18:15 IST (12:45 UTC)  
**Manual Trigger**: Available via workflow_dispatch  

**What it does**:
- Updates "Last Updated" timestamp in README
- Rotates motivational quotes
- Fetches latest blog posts from Medium feed
- Fetches top GitHub repositories (if PROJECTS tag exists)
- Commits changes back to the repository

**Optimizations**:
- Explicit Python 3.11 setup for consistency
- Shallow clone with `fetch-depth: 1`
- Comprehensive error handling for network failures
- Better logging with emoji indicators
- Graceful fallback when external APIs fail
- Uses timezone-aware datetime (no deprecation warnings)
- 10-minute timeout for external API calls

**Required Secrets**: 
- `GITHUB_TOKEN` (automatically provided by GitHub)

**Required Permissions**:
- `contents: write` - to update and commit README changes

**External Dependencies**:
- Medium RSS feed: `https://medium.com/feed/@jayanththomas2004`
- GitHub API: `https://api.github.com/users/JET609/repos`

**Note**: The workflow will continue to work even if external APIs are unavailable - it will simply skip those sections and update what it can.

---

## Configuration Requirements

### Secrets
All workflows use `GITHUB_TOKEN` which is automatically provided by GitHub Actions. No additional secrets need to be configured.

### Permissions
All workflows require `contents: write` permission which is granted in the workflow files. Ensure the repository settings allow GitHub Actions to create pull requests and write to the repository:

1. Go to Settings → Actions → General
2. Under "Workflow permissions", ensure "Read and write permissions" is selected
3. Check "Allow GitHub Actions to create and approve pull requests" if needed

### Branch Protection
If using branch protection rules on `main`:
- Allow the GitHub Actions bot to push directly, OR
- Configure the workflows to create pull requests instead

### Output Branch (for snake.yml)
The snake animation workflow pushes to an `output` branch. This branch will be created automatically on first run if it doesn't exist.

---

## Testing Workflows

You can manually trigger any workflow:

1. Go to the "Actions" tab in GitHub
2. Select the workflow you want to run
3. Click "Run workflow"
4. Select the branch and click the green "Run workflow" button

---

## Monitoring

Check workflow runs in the Actions tab. Each workflow includes:
- Clear success/failure indicators
- Detailed logs with emoji markers for easy scanning
- Timeout protection to prevent hung jobs
- Concurrency controls to prevent resource waste

---

## Troubleshooting

### Snake animation not appearing
- Check if the `output` branch was created
- Verify the workflow ran successfully in Actions tab
- Check permissions are set correctly

### Daily contribution not committing
- Verify `contents: write` permission is enabled
- Check if there are branch protection rules blocking the push
- Look for error messages in workflow logs

### Profile automation not updating README
- Verify README has the correct comment tags (`<!--LAST_UPDATED-->`, `<!--RANDOM_QUOTE-->`, `<!--BLOG_START-->`)
- Check network connectivity issues in workflow logs
- Medium/GitHub API may be temporarily unavailable (workflow will still update what it can)

### Rate Limiting
GitHub API has rate limits:
- Authenticated: 5,000 requests/hour (using GITHUB_TOKEN)
- These workflows make minimal API calls and should never hit limits

If Medium RSS feed is rate-limited, the workflow will gracefully skip that section.

---

## Maintenance

### Updating Dependencies
Workflows use pinned major versions:
- `actions/checkout@v4`
- `actions/setup-python@v5`
- `Platane/snk/svg-only@v3`
- `crazy-max/ghaction-github-pages@v4`

Check for updates periodically by reviewing Dependabot alerts or checking action repositories.

### Modifying Schedules
Edit the `cron` expressions in each workflow file:
- Use [crontab.guru](https://crontab.guru/) to understand/create cron schedules
- Remember schedules use UTC timezone

### Adding New Dynamic Sections
To add new auto-updating sections to README:
1. Add comment tags in README: `<!--TAG_START-->content<!--TAG_END-->`
2. Update the Python script in `profile-advanced.yml` to populate that section
3. Test locally before pushing

---

## Performance Metrics

Average workflow execution times:
- **snake.yml**: 30-60 seconds
- **daily-contribution.yml**: 10-20 seconds  
- **profile-advanced.yml**: 30-60 seconds (depends on API response times)

All workflows include timeouts to prevent hanging:
- snake.yml: 10 minutes
- daily-contribution.yml: 5 minutes
- profile-advanced.yml: 10 minutes
