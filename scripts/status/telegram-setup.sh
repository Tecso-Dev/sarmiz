#!/usr/bin/env bash
# Connects the status workflow to a Telegram group. Run it yourself, as a repository admin:
#
#   bash scripts/status/telegram-setup.sh
#
# What it does:
#   1. asks for the bot token WITHOUT showing it (it never appears on screen, in history or in the process list);
#   2. finds your group's chat id from the messages the bot has seen;
#   3. creates the "status" environment and lets only the main branch use it, so a student's branch
#      cannot read the secrets;
#   4. stores TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID as secrets of that environment;
#   5. sends a test message to the group.
#
# Before you run it: in Telegram open @BotFather, send /newbot and copy the token; add the bot to your group
# and send any message in the group.

set -euo pipefail

REPO="${REPO:-Tecso-Dev/sarmiz}"
ENV_NAME="status"

for tool in gh curl python3; do
  command -v "$tool" >/dev/null || { echo "$tool is not installed"; exit 1; }
done
gh auth status >/dev/null 2>&1 || { echo "gh is not logged in: run 'gh auth login'"; exit 1; }
[ "$(gh api "repos/$REPO" --jq '.permissions.admin')" = "true" ] || { echo "You need admin rights on $REPO."; exit 1; }

printf "Paste the bot token (nothing is shown while you type): "
read -rs TOKEN
echo
[ -n "$TOKEN" ] || { echo "No token given."; exit 1; }

# Call the Telegram API with the token inside a curl config read from stdin, so it is never on a command line.
tg() { # tg <method> [curl config lines for data...]
  local method="$1"; shift
  { printf 'url = "https://api.telegram.org/bot%s/%s"\n' "$TOKEN" "$method"; printf '%s\n' "$@"; } | curl -s -K -
}

me=$(tg getMe)
python3 -c 'import json,sys; sys.exit(0 if json.load(sys.stdin).get("ok") else 1)' <<<"$me" || { echo "Telegram did not accept that token."; exit 1; }
echo "Bot: $(python3 -c 'import json,sys; print(json.load(sys.stdin)["result"]["username"])' <<<"$me")"

updates=$(tg getUpdates)
groups=$(python3 -c '
import json, sys
seen = {}
for u in json.load(sys.stdin).get("result", []):
    m = u.get("message") or u.get("channel_post") or u.get("my_chat_member") or {}
    c = m.get("chat") or {}
    if c.get("type") in ("group", "supergroup"):
        seen[c["id"]] = c.get("title", "")
for k, v in seen.items():
    print(f"{k}\t{v}")
' <<<"$updates")

if [ -z "$groups" ]; then
  echo "The bot has not seen any group message yet. Add it to the group, send a message there, then run this again."
  exit 1
fi
echo "Groups the bot can see (chat id, title):"
echo "$groups"
if [ "$(printf '%s\n' "$groups" | wc -l | tr -d ' ')" = "1" ]; then
  CHAT="$(printf '%s' "$groups" | cut -f1)"
else
  printf "Type the chat id of the group to use: "
  read -r CHAT
fi
[ -n "$CHAT" ] || { echo "No chat id."; exit 1; }
printf "Use chat %s? [y/N] " "$CHAT"
read -r answer
[ "$answer" = "y" ] || { echo "Stopped. Nothing was changed."; exit 1; }

echo "Creating the '$ENV_NAME' environment (main branch only)..."
gh api -X PUT "repos/$REPO/environments/$ENV_NAME" --input - >/dev/null <<'JSON'
{"deployment_branch_policy": {"protected_branches": false, "custom_branch_policies": true}}
JSON
if ! gh api "repos/$REPO/environments/$ENV_NAME/deployment-branch-policies" --jq '.branch_policies[].name' | grep -qx "main"; then
  gh api -X POST "repos/$REPO/environments/$ENV_NAME/deployment-branch-policies" -f name=main -f type=branch >/dev/null
fi
gh api "repos/$REPO/environments/$ENV_NAME/deployment-branch-policies" --jq '"Allowed branches: " + ([.branch_policies[].name] | join(", "))'

printf '%s' "$TOKEN" | gh secret set TELEGRAM_BOT_TOKEN --env "$ENV_NAME" --repo "$REPO"
printf '%s' "$CHAT" | gh secret set TELEGRAM_CHAT_ID --env "$ENV_NAME" --repo "$REPO"

result=$(tg sendMessage "data = \"chat_id=$CHAT\"" 'data-urlencode = "text=✅ ربات وضعیت سرمیز وصل شد. از حالا بازبینی‌ها و PRها این‌جا خبر می‌شوند."')
python3 -c 'import json,sys; sys.exit(0 if json.load(sys.stdin).get("ok") else 1)' <<<"$result" \
  && echo "Test message sent. Check the group." || echo "The secrets are stored, but the test message failed."
unset TOKEN
echo "Done. Next: gh workflow run status.yml --ref main -R $REPO"
