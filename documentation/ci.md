# CI Summary

## Key Points

- Continuous integration is handled by GitHub Actions.
- The workflow file is `.github/workflows/ci.yml`.
- Backend tests and the frontend production build run on every push to `main`
  and on every pushed Git tag.
- Docker images are published only when a Git tag matching `X.Y.Z` is pushed.
- Docker image versions come from the Git tag.
- Published images are pushed to GitHub Container Registry.

## Objective

The CI pipeline validates the main branch and tagged releases. Docker images are
published only for release tags, and the release version is explicit: it is the
pushed Git tag in `X.Y.Z` format.

## Workflow

The GitHub Actions workflow contains three jobs:

- `backend-tests`: runs `./test_backend.sh`.
- `frontend-build`: installs frontend dependencies with `npm ci` and runs
  `npm run build`.
- `docker-images`: for Git tags only, builds and pushes the backend and frontend
  Docker images after the validation jobs succeed.

The `docker-images` job depends on both validation jobs. Docker images must not
be pushed if tests or frontend build fail. Branch pushes never publish Docker
images.

Backend tests run with a configured ODS path. When `JEUXVIDEO_ODS_PATH` is not
already defined, `./test_backend.sh` points it to the versioned
`collection-example.ods` fixture.

The workflow sets `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true` so GitHub-provided
JavaScript actions run on Node.js 24. This is independent from the frontend
application build, which uses the Node.js version configured in
`actions/setup-node`.

## Docker Version

Docker image versions are resolved from the Git tag that triggered the workflow.

The tag must match the `X.Y.Z` format, for example:

```text
0.2.0
```

Docker images are not published from branch pushes. Tags that do not match
`X.Y.Z` fail before image publication. To publish a release, create and push a
version tag:

```bash
git tag 0.2.1
git push origin 0.2.1
```

## Published Images

The images are published to GitHub Container Registry:

- `ghcr.io/sebastienbinda/cloudcollectionapp/backend:<version>`
- `ghcr.io/sebastienbinda/cloudcollectionapp/backend:latest`
- `ghcr.io/sebastienbinda/cloudcollectionapp/frontend:<version>`
- `ghcr.io/sebastienbinda/cloudcollectionapp/frontend:latest`

The `<version>` tag is the Git tag that triggered the workflow.

## Required GitHub Permissions

The workflow requires:

- `contents: read` to checkout the tagged source.
- `packages: write` to publish images to GitHub Container Registry.

## Development Rules

- Do not publish Docker images before backend tests and frontend build have
  passed.
- Publish Docker images only from Git tags matching `X.Y.Z`.
- Use the release tag as the Docker image version.
- Do not hardcode registry credentials in the repository. Use GitHub Actions
  token permissions or repository secrets.
- If image names, registry location, trigger branches, or versioning behavior
  change, update this document in the same change set.
