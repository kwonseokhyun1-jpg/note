# Apply: allow kings to be Zombified (checkers)

This agent run was attached to `kwonseokhyun1-jpg/note`, but the change belongs in
[`kwonseokhyun1-jpg/checkers`](https://github.com/kwonseokhyun1-jpg/checkers).
The installation token for this run can only push to `note`, so the fix is
delivered here as a ready-to-apply patch.

## Apply on checkers

```bash
git clone https://github.com/kwonseokhyun1-jpg/checkers.git
cd checkers
git checkout -b cursor/allow-king-zombify-168b
git apply path/to/checkers-allow-king-zombify.patch
node scripts/test-zombify.mjs
git add -A && git commit -m "Allow kings to be targeted by Zombify"
git push -u origin cursor/allow-king-zombify-168b
# then open a PR into main
```

Or re-launch the same prompt on the **checkers** repo in Cursor Cloud.

## What changed

Zombify no longer rejects kings in targeting or the effect handler. Card copy
says "pieces" instead of "men". A unit test covers zombifying an existing king.
