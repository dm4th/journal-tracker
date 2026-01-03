#!/bin/bash

# Activate the Python virtual environment
if [ -d "$CLAUDE_PROJECT_DIR/journal-venv" ]; then
  source "$CLAUDE_PROJECT_DIR/journal-venv/bin/activate"

  # Load environment variables from .env file if it exists
  if [ -f "$CLAUDE_PROJECT_DIR/.env" ]; then
    set -a  # automatically export all variables
    source "$CLAUDE_PROJECT_DIR/.env"
    set +a
  fi

  # Persist the environment variables for subsequent bash commands
  if [ -n "$CLAUDE_ENV_FILE" ]; then
    # Capture the activated environment
    echo "export VIRTUAL_ENV='$VIRTUAL_ENV'" >> "$CLAUDE_ENV_FILE"
    echo "export PATH='$VIRTUAL_ENV/bin:$PATH'" >> "$CLAUDE_ENV_FILE"

    # Export Notion credentials if they're set
    if [ -n "$NOTION_TOKEN" ]; then
      echo "export NOTION_TOKEN='$NOTION_TOKEN'" >> "$CLAUDE_ENV_FILE"
    fi
    if [ -n "$NOTION_JOURNAL_DATABASE_ID" ]; then
      echo "export NOTION_JOURNAL_DATABASE_ID='$NOTION_JOURNAL_DATABASE_ID'" >> "$CLAUDE_ENV_FILE"
    fi
  fi

  echo "Virtual environment activated: $VIRTUAL_ENV"
fi

exit 0
