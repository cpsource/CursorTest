Here's how to create a pull request using PyGithub:

## Basic Pull Request Creation

```python
from github import Github

# Initialize with your personal access token
g = Github("your_personal_access_token")
repo = g.get_repo("owner/repository-name")

# Create a pull request
pr = repo.create_pull(
    title="Add new feature",
    body="This PR adds a new feature that does X, Y, and Z.",
    head="feature-branch",  # Your branch with changes
    base="main"            # Target branch (usually main/master)
)

print(f"Pull request created: {pr.html_url}")
```

## More Complete Example

```python
from github import Github

def create_pull_request():
    # Initialize GitHub client
    g = Github("your_token")
    repo = g.get_repo("username/my-project")
    
    # Pull request details
    pr_title = "Fix authentication bug"
    pr_body = """
    ## Changes Made
    - Fixed token validation logic
    - Added error handling for expired tokens
    - Updated tests
    
    ## Testing
    - All existing tests pass
    - Added new test cases for edge cases
    
    Fixes #123
    """
    
    try:
        # Create the pull request
        pr = repo.create_pull(
            title=pr_title,
            body=pr_body,
            head="bugfix/auth-validation",  # Your feature branch
            base="main",                    # Target branch
            draft=False                     # Set to True for draft PR
        )
        
        print(f"✅ Pull request created successfully!")
        print(f"URL: {pr.html_url}")
        print(f"Number: #{pr.number}")
        
        return pr
        
    except Exception as e:
        print(f"❌ Error creating pull request: {e}")
        return None

# Usage
pr = create_pull_request()
```

## Adding Labels and Reviewers

```python
# After creating the PR, you can add labels and reviewers
if pr:
    # Add labels
    pr.add_to_labels("bug", "priority-high")
    
    # Request reviewers
    pr.create_review_request(reviewers=["teammate1", "teammate2"])
    
    # Add assignees
    pr.add_to_assignees("project-lead")
```

Think of it like sending a formal letter - you need the recipient (base branch), your return address (head branch), a subject line (title), and the message content (body). PyGithub handles the "postal service" part of actually delivering your pull request to GitHub.

**Important notes:**
- Your `head` branch must exist and have commits that differ from the `base` branch
- You need appropriate permissions on the repository
- The personal access token needs `repo` scope for private repos, or `public_repo` for public ones

Would you like to see how to handle any specific scenarios, like creating draft PRs or handling merge conflicts?

