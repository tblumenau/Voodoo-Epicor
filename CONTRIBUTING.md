# Contributing to Voodoo Pick-To-Light + Epicor Integration Starter

Thanks for your interest in improving this integration starter! Contributions of any size are welcome—from fixing typos to expanding Epicor/Voodoo coverage. This guide summarizes how to propose changes and what maintainers look for.

## Ways to help
- Report issues with Epicor connectivity or device payloads
- Improve documentation and examples
- Add checks, linting, or automation to make the starter easier to run
- Fix bugs or polish the sample script

If you are unsure whether an idea fits, open an issue to start a quick discussion.

## Getting set up
1. Fork the repository and create a feature branch off `main`.
2. Install Python 3.9+ and any dependencies you need for your changes.
3. If you are adjusting Epicor/Voodoo behavior, configure the environment variables documented in `README.md` so you can exercise the flow locally.

## Making changes
- Keep pull requests focused: smaller, self-contained changes are easier to review and merge.
- Update docs alongside behavior changes so users know how to configure and run new capabilities.
- Add or update tests when applicable. If you cannot add a test, explain why in the PR description.
- Preserve backward compatibility whenever possible. Call out any breaking changes early.

## Commit and PR guidelines
- Write clear commit messages that explain the “what” and “why.”
- Reference related issues in your pull request when relevant.
- Include a short summary in the PR body: what changed, why, and how to verify.
- If your change affects how Epicor data is fetched or how devices are driven, describe the testing you performed (for example, dry-run output or device responses).

## Code of conduct
By participating, you agree to abide by the project’s code of conduct. Be respectful, collaborative, and patient with others.
