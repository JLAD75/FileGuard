# Contributing to FileGuard

First off, thank you for considering contributing to FileGuard! It's people like you that make FileGuard such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps to reproduce the problem**
* **Provide specific examples to demonstrate the steps**
* **Describe the behavior you observed after following the steps**
* **Explain which behavior you expected to see instead and why**
* **Include screenshots if possible**
* **Include your environment details** (OS, browser, versions)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* **Use a clear and descriptive title**
* **Provide a step-by-step description of the suggested enhancement**
* **Provide specific examples to demonstrate the steps**
* **Describe the current behavior** and **explain which behavior you expected to see instead**
* **Explain why this enhancement would be useful**

### Pull Requests

1. **Fork the repo** and create your branch from `main`
2. **Follow the code style** of the project
3. **Add tests** for any new functionality
4. **Ensure the test suite passes**
5. **Update documentation** for user-facing changes
6. **Write a clear commit message**

## Development Process

### Setting Up Development Environment

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/FileGuard.git
cd FileGuard

# Add upstream remote
git remote add upstream https://github.com/JLAD75/FileGuard.git

# Create a branch
git checkout -b feature/my-new-feature

# Setup development environment
cp .env.example .env
docker-compose up -d

# Install pre-commit hooks
pip install pre-commit
pre-commit install
```

### Code Style Guidelines

#### Python (Backend)

We follow **PEP 8** with these specifics:

* Line length: 100 characters
* Use type hints for all functions
* Use docstrings for all public functions (Google style)
* Import order: stdlib, third-party, local

```python
from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from core.models import User


def get_user_files(
    user_id: uuid.UUID,
    db: Session,
    limit: int = 10
) -> List[FileMetadata]:
    """
    Retrieve files for a user.

    Args:
        user_id: UUID of the user
        db: Database session
        limit: Maximum number of files to return

    Returns:
        List of FileMetadata objects
    """
    return db.query(FileMetadata).filter(
        FileMetadata.owner_id == user_id
    ).limit(limit).all()
```

#### TypeScript (Frontend)

We follow standard TypeScript conventions:

* Use **ESLint** configuration in the project
* Prefer functional components with hooks
* Use TypeScript interfaces over types when possible
* Use async/await over promises

```typescript
import { useState, useEffect } from 'react';
import { FileMetadata } from '@/types';
import { api } from '@/lib/api';

interface FileListProps {
  userId: string;
  limit?: number;
}

export const FileList: React.FC<FileListProps> = ({ userId, limit = 10 }) => {
  const [files, setFiles] = useState<FileMetadata[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchFiles = async () => {
      try {
        const response = await api.get('/files/', { params: { limit } });
        setFiles(response.data);
      } catch (error) {
        console.error('Failed to fetch files:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchFiles();
  }, [userId, limit]);

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      {files.map(file => (
        <FileCard key={file.id} file={file} />
      ))}
    </div>
  );
};
```

### Testing

#### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_files.py

# Run specific test
pytest tests/test_files.py::test_upload_file
```

Write tests for:
* All new endpoints
* Edge cases and error conditions
* Database operations
* Business logic functions

#### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test
npm test FileUpload.test.tsx

# Run in watch mode
npm test -- --watch
```

Write tests for:
* Component rendering
* User interactions
* API calls (mocked)
* State management

### Commit Messages

We use **Conventional Commits** for clear commit history:

```
type(scope): brief description

Longer explanation if needed

Closes #123
```

**Types:**
* `feat`: New feature
* `fix`: Bug fix
* `docs`: Documentation changes
* `style`: Code style changes (formatting)
* `refactor`: Code refactoring
* `perf`: Performance improvements
* `test`: Adding or updating tests
* `chore`: Maintenance tasks
* `ci`: CI/CD changes

**Examples:**

```
feat(files): add file versioning support

Implement full file versioning with rollback capability.
Users can now view and restore previous versions.

Closes #145
```

```
fix(auth): resolve JWT token expiration issue

Tokens were expiring too early due to timezone mismatch.
Now using UTC consistently across the application.

Fixes #234
```

### Branch Naming

* Feature: `feature/description-here`
* Bug fix: `fix/issue-description`
* Documentation: `docs/what-you-are-documenting`
* Refactoring: `refactor/what-you-are-refactoring`

### Pull Request Process

1. **Update documentation** if you're adding/changing features
2. **Add tests** for new functionality
3. **Ensure all tests pass** locally before submitting
4. **Update the CHANGELOG.md** with your changes
5. **Link related issues** in the PR description
6. **Wait for review** from maintainers

**PR Title Format:**

```
type: Brief description of changes
```

**PR Description Template:**

```markdown
## Description
Brief description of what this PR does.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe how you tested your changes.

## Checklist
- [ ] My code follows the style guidelines
- [ ] I have performed a self-review
- [ ] I have commented my code where necessary
- [ ] I have updated the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix/feature works
- [ ] New and existing unit tests pass locally
- [ ] Any dependent changes have been merged

## Related Issues
Closes #123
Related to #456
```

### Code Review

All submissions require review. We use GitHub pull requests for this purpose.

**What we look for:**

* **Correctness**: Does the code do what it's supposed to?
* **Testing**: Are there adequate tests?
* **Style**: Does it follow our coding standards?
* **Documentation**: Is it well documented?
* **Performance**: Are there any obvious performance issues?
* **Security**: Are there any security concerns?

**Review timeline:**

* We aim to review PRs within **2-3 business days**
* Complex PRs may take longer
* If your PR hasn't been reviewed after 5 days, feel free to ping us

### Database Migrations

When adding/modifying database models:

```bash
cd backend

# Create migration
alembic revision --autogenerate -m "Add file_versions table"

# Review the generated migration file
# Edit if necessary

# Test the migration
alembic upgrade head

# Test rollback
alembic downgrade -1

# Commit both the model changes and migration file
git add alembic/versions/xxx_add_file_versions.py
git add core/models.py
git commit -m "feat(db): add file versions table"
```

### Documentation

Documentation is just as important as code:

* **Code comments**: Explain *why*, not *what*
* **Docstrings**: All public functions need docstrings
* **README**: Update if you change setup/installation
* **API docs**: OpenAPI/Swagger updates automatically
* **User guides**: Add to `/docs` if needed

### Performance Considerations

* **Database queries**: Use proper indexes, avoid N+1 queries
* **Async operations**: Use async/await for I/O operations
* **Caching**: Cache expensive operations when appropriate
* **File handling**: Stream large files, don't load into memory
* **Frontend**: Lazy load components, optimize images

## Project Structure

```
FileGuard/
├── backend/
│   ├── alembic/              # Database migrations
│   ├── auth/                 # Authentication module
│   ├── core/                 # Core models & config
│   ├── files/                # File management
│   ├── storage/              # Storage backends
│   ├── tasks/                # Celery tasks
│   ├── tests/                # Test files
│   └── main.py               # FastAPI app
│
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js pages
│   │   ├── components/       # React components
│   │   ├── lib/              # Utilities
│   │   ├── store/            # State management
│   │   └── types/            # TypeScript types
│   └── tests/                # Test files
│
├── docs/                     # Documentation
└── .github/                  # GitHub config
```

## Getting Help

* 💬 **Discord**: [Join our Discord](https://discord.gg/fileguard)
* 📧 **Email**: dev@fileguard.example.com
* 📖 **Docs**: [Documentation](https://docs.fileguard.example.com)

## Recognition

Contributors who make significant contributions will be:

* Added to the CONTRIBUTORS file
* Mentioned in release notes
* Given recognition in our Discord community

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to FileGuard! 🎉
