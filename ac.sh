#!/bin/bash

# Prompt for commit message
echo "Enter your commit message:"
read commit_message

# Add all changes
git add .

# Commit with the provided message
git commit -m "$commit_message"

# Push to remote repository
git push

echo "Changes have been committed and pushed successfully!"
