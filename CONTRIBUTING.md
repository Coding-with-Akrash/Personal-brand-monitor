# Contributing to Personal Brand Monitor

We welcome contributions! Please read this guide before submitting pull requests.

## How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature-name`)
3. Make your changes
4. Run tests and linting (`pytest` and `ruff check`)
5. Commit your changes (`git commit -m "feat: add your feature"`)
6. Push to your fork (`git push origin feature/your-feature-name`)
7. Open a pull request

## Commit Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` — new feature
- `fix:` — bug fix
- `docs:` — documentation changes
- `style:` — formatting, missing semicolons, etc.
- `refactor:` — code change that neither fixes a bug nor adds a feature
- `test:` — adding missing tests or correcting existing tests
- `chore:` — maintenance tasks

## Code Style

- Follow PEP 8
- Use type hints on all public functions
- Add docstrings to modules, classes, and public functions
- Run `black` and `ruff` before submitting

## Reporting Issues

Use GitHub Issues to report bugs or suggest features. Include:
- Steps to reproduce
- Expected vs. actual behavior
- Your environment (Python version, OS)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
