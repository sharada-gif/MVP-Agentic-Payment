# How to Add Collaborators to GitHub Repository

## Method 1: Adding Individual Collaborators (Recommended)

### Steps:

1. **Go to your repository on GitHub:**
   ```
   https://github.com/sharada-gif/MVP-Agentic-Payment
   ```

2. **Click on "Settings" tab** (at the top of the repository page)

3. **In the left sidebar, click "Collaborators"**
   - For newer GitHub interface, it might be under "Access" → "Collaborators"
   - Or "Manage access" → "Add people"

4. **Click "Add people" button** (green button on the right)

5. **Enter collaborator's information:**
   - Type their GitHub username, full name, or email address
   - Select the person from the dropdown

6. **Choose permission level:**
   - **Read**: Can view and clone, but cannot modify
   - **Write** (Recommended): Can push code, create branches, open pull requests
   - **Maintain**: Can manage repository settings (for trusted team members)
   - **Admin**: Full access (use carefully)

7. **Click "Add [username] to this repository"**

8. **The collaborator will receive an email invitation** and must accept it

---

## Method 2: Using GitHub Organizations (For Teams)

If you have a GitHub Organization:

1. Go to your organization: `https://github.com/your-org`
2. Click "People" or "Teams"
3. Add members to the organization
4. Then add teams to the repository with appropriate permissions

---

## Method 3: Using Repository Invitations Link

1. Go to repository Settings → Collaborators
2. Copy the invitation link (if available)
3. Share the link with your team members
4. They can accept the invitation directly

---

## Quick Access Links

### Direct Navigation:
- **Repository Settings**: `https://github.com/sharada-gif/MVP-Agentic-Payment/settings`
- **Collaborators Page**: `https://github.com/sharada-gif/MVP-Agentic-Payment/settings/access`

---

## Permission Levels Explained

### Read (Pull)
- ✅ Can view repository
- ✅ Can clone repository
- ✅ Can download code
- ❌ Cannot push changes
- ❌ Cannot create branches
- ❌ Cannot open issues or pull requests

**Use for:** Viewers, stakeholders, external reviewers

### Write (Push) - **Recommended for Developers**
- ✅ Everything in Read
- ✅ Can push code
- ✅ Can create branches
- ✅ Can create pull requests
- ✅ Can manage issues
- ✅ Can manage pull requests
- ❌ Cannot change repository settings
- ❌ Cannot delete repository

**Use for:** Team developers, contributors

### Maintain
- ✅ Everything in Write
- ✅ Can manage repository settings
- ✅ Can manage webhooks
- ✅ Can manage environments
- ❌ Cannot delete repository
- ❌ Cannot transfer repository

**Use for:** Team leads, senior developers

### Admin
- ✅ Full access to everything
- ✅ Can delete repository
- ✅ Can transfer repository
- ✅ Can manage billing (if applicable)

**Use for:** Repository owners only

---

## Best Practices

1. **Start with Write access** for team members
2. **Use Pull Requests** even for collaborators with Write access
3. **Protect main branch** (Settings → Branches → Add rule)
4. **Require pull request reviews** before merging
5. **Grant Admin access sparingly** - only to trusted team leads

---

## Adding Multiple Collaborators

1. Add collaborators one at a time (GitHub doesn't support bulk add in UI)
2. Or create a GitHub Organization and add team members to teams
3. Then assign teams to repositories

---

## Troubleshooting

### Collaborator not receiving invitation email:
- Check their email spam folder
- Verify their GitHub email settings
- Resend invitation from Collaborators page

### Permission denied errors:
- Make sure collaborator accepted the invitation
- Check their permission level
- Verify they're pushing to correct branch

### Can't find Collaborators option:
- Make sure you have Admin access
- Check if repository belongs to an organization (may be under different settings)

---

## Security Tips

1. **Review collaborators regularly** - Remove inactive members
2. **Use branch protection** - Require PR reviews for main branch
3. **Enable two-factor authentication** for all collaborators
4. **Audit access logs** - Review who accessed what and when
5. **Use minimal permissions** - Give only necessary access

---

## Quick Command Reference

After adding collaborators, they can:

```bash
# Clone the repository
git clone https://github.com/sharada-gif/MVP-Agentic-Payment.git

# Or if already cloned, fetch the feature branch
git fetch origin
git checkout feature/api-connector

# Start working
cd MVP-Agentic-Payment
```

---

## Need Help?

- GitHub Documentation: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/managing-teams-and-people-with-access-to-your-repository
- GitHub Support: https://support.github.com
