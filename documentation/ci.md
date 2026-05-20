# CI Summary

## Key Points

- Continuous integration is handled by GitHub Actions.
- The workflow file is `.github/workflows/ci.yml`.
- The workflow runs on every push to the `main` branch.
- Backend tests and the frontend production build must pass before Docker images
  are published.
- Docker image versions come from `docker/version`.
- Published images are pushed to GitHub Container Registry.

## Objective

The CI pipeline validates the application after each push to `main` and
publishes Docker images that can be reused for deployment. It keeps the image
version explicit through `docker/version` while allowing the patch version to be
automatically incremented when the pushed commit did not change the version
file.

## Workflow

The GitHub Actions workflow contains three jobs:

- `backend-tests`: runs `./test_backend.sh`.
- `frontend-build`: installs frontend dependencies with `npm ci` and runs
  `npm run build`.
- `docker-images`: builds and pushes the backend and frontend Docker images
  after the validation jobs succeed.

The `docker-images` job depends on both validation jobs. Docker images must not
be pushed if tests or frontend build fail.

Backend tests run with a configured ODS path. When `JEUXVIDEO_ODS_PATH` is not
already defined, `./test_backend.sh` points it to the versioned
`collection-example.ods` fixture.

## Docker Version

The version file is `docker/version`.

The file must contain a semantic version in the `x.y.z` format, for example:

```text
0.2.0
```

On each push to `main`:

- If `docker/version` changed compared with the previous commit on `main`, the
  workflow uses the new version as-is.
- If `docker/version` did not change, the workflow increments the patch number
  `z` and uses the incremented version for the Docker image tags.

The automatic version bump is committed back to `main` only after backend tests,
frontend build, and Docker image build/publish steps have succeeded. If any
validation or Docker publication step fails, `docker/version` is not updated on
the branch.

The `[skip ci]` marker avoids triggering a second full workflow run for the
automatic version bump commit.

## Published Images

The images are published to GitHub Container Registry:

- `ghcr.io/sebastienbinda/cloudcollectionapp/backend:<version>`
- `ghcr.io/sebastienbinda/cloudcollectionapp/backend:latest`
- `ghcr.io/sebastienbinda/cloudcollectionapp/frontend:<version>`
- `ghcr.io/sebastienbinda/cloudcollectionapp/frontend:latest`

The `<version>` tag is the resolved version from `docker/version`, after any
automatic patch increment.

## Required GitHub Permissions

The workflow requires:

- `contents: write` to commit the automatic `docker/version` patch increment.
- `packages: write` to publish images to GitHub Container Registry.

Repository settings and branch protection rules must allow the GitHub Actions
token to push the automatic version bump commit to `main`. If branch protection
blocks this push, tests and image publication may already have succeeded, but
the final version bump commit step will fail.

## Development Rules

- Do not publish Docker images before backend tests and frontend build have
  passed.
- Keep `docker/version` in semantic version format.
- Update `docker/version` manually when intentionally changing the major or
  minor version.
- Let the workflow increment the patch version automatically for ordinary pushes
  where the version file did not change.
- Do not hardcode registry credentials in the repository. Use GitHub Actions
  token permissions or repository secrets.
- If image names, registry location, trigger branches, or versioning behavior
  change, update this document in the same change set.
