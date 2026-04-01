# check-secrets

Scan staged files (or the full working tree) for hardcoded secrets before committing.

## What to do

1. Run the following grep patterns against every **staged** file (`git diff --cached --name-only`).
   If no files are staged, fall back to all tracked files.

2. Flag any line that matches these patterns (case-insensitive):

   | Pattern | Why it's risky |
   |---|---|
   | `password\s*[:=]\s*\S+` (not a `${…}` reference or placeholder) | Hardcoded DB / service password |
   | `secret\s*[:=]\s*\S+` | Hardcoded secret key |
   | `api_key\s*[:=]\s*\S+` | Hardcoded API key |
   | `token\s*[:=]\s*\S+` | Hardcoded token |
   | `PRIVATE KEY` | PEM private key block |
   | Long base64-like strings (40+ chars of `[A-Za-z0-9+/=]`) inside quotes | Possible encoded secret |

3. **Ignore** safe patterns:
   - Values that are entirely a `${VAR}` or `${VAR:-default}` reference
   - Lines inside `*.env.example` files (they are intentionally placeholder values)
   - Lines that are comments (`#`)
   - Values equal to common placeholders: `your_*`, `change_me*`, `<…>`, `todo`, `xxxxx`

4. For each finding, report:
   - File path + line number
   - The matched line (redact the secret value itself with `***`)
   - Which pattern triggered

5. If **no findings**: confirm "No hardcoded secrets detected."

6. If **findings exist**: list them, then recommend:
   - Move the value to `.env` (gitignored) and reference it as `${VAR_NAME}`
   - Add the variable to `.env.example` with a placeholder value
   - Rotate the exposed secret if it was already committed

## Usage

Run manually before committing:
```
/check-secrets
```

Or wire it as a pre-commit reminder by adding to your workflow:
```bash
# In .git/hooks/pre-commit (chmod +x)
claude /check-secrets
```
