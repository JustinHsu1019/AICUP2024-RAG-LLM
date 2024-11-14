# Contribution Guide
這個資料夾主要處理 CI Pipeline, 目前僅有檢測程式碼規範 (pre-commit), 且在發 PR & merge to main 才會觸發

We follow GitHub Flow for contributing. The steps are as follows:

1. **Claim an issue**: Start by picking an issue from GitHub.
2. **Create a branch**: Open a new branch with a clear name related to the issue (e.g., `feat/xxxxx-feature`).
3. **Development**: After completing the feature, ensure you run pre-commit hooks:
   ```
   pre-commit run --all-files
   ```
4. **Create PR Request (PR)**:
   - Ensure your PR is small and easily reviewable.
   - Add the GitHub issue number to the PR title in the format `feat(#123): xxxxxx` for easy reference.
   - Write a clear description including the reason for the change and what was modified (`Reason & Changes`).
5. **Review & Approval**:
   - Assign the PR to all members of the team for review.
   - Wait for at least one approval.
   - Ensure all CI checks pass.
6. **Merge**: Once approved and CI passes, merge the branch into `main` yourself.

## Additional Notes
- Keep your commits focused and ensure meaningful commit messages.
- Always rebase your branch on top of `main` before merging.
- Avoid large, multi-purpose PRs. Smaller changes are easier to review and help prevent issues.
