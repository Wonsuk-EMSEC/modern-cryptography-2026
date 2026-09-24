# Lab02 target image

This directory contains the build recipe for the extra service used in Lab02
Parts 4–6. The common student environment is built from `docker/Dockerfile`.
Both containers are run through `docker/compose.yml`.

Students start the target using the [Lab02 setup
instructions](../../labs/lab02/README.md#setup). Compose pulls this pinned
release from GitHub Container Registry (GHCR) when it is missing locally:

```text
ghcr.io/wonsuk-emsec/modern-cryptography-2026-lab02-target:2026-lab02-v1
```

Students do not build this target. The server source and private target data
remain in the instructor checkout, so a student checkout alone cannot build
it. The course image builds without any instructor files.

## Instructor build and publication

From the private repository root, build the course base from
`docker/Dockerfile`, verify the existing matching Lab02 data, and build the
target from `docker/lab02-target/Dockerfile`:

```console
docker compose -f docker/compose.yml build course
docker compose -f docker/compose.yml run --rm course \
  python3 -m instructor.lab02.generators.build_data --check
docker build -f docker/lab02-target/Dockerfile -t ghcr.io/wonsuk-emsec/modern-cryptography-2026-lab02-target:2026-lab02-v1 .
docker compose -f docker/compose.yml --profile lab02 up -d --wait course lab02-target
docker compose -f docker/compose.yml --profile lab02 ps
```

The Dockerfile copies the existing `instructor/lab02/targets/` directory into
the image. Keep that directory out of the public repository and student
source archive. Do not regenerate data for a routine build. Pair the Lab02
student files for `2026-lab02-v1` with the image bearing that same release tag:
Part 5's ciphertext depends on the target's matching data. After any data
change, choose a new release tag and update Compose and the student files
together. Never overwrite a published versioned tag with changed data, and
never use `latest` for the Lab02 target.

After local validation, authenticate with a GitHub account allowed to publish
under `wonsuk-emsec`, using a personal access token (classic) with
`write:packages` at the password prompt:

```console
docker login ghcr.io
docker push ghcr.io/wonsuk-emsec/modern-cryptography-2026-lab02-target:2026-lab02-v1
```

Prefer a **Public** package so students can pull anonymously. The first push
normally creates a private package. In GitHub's package page, open **Package
settings → Change visibility → Public** after that push; this usually requires
a manual change even if the repository is already public. See [GitHub's
package visibility instructions](https://docs.github.com/en/packages/learn-github-packages/configuring-a-packages-access-control-and-visibility).

For a private package, grant students read access and have them run
`docker login ghcr.io` with their own personal access token (classic) carrying
`read:packages`. A token also needs the account's package permission. See
[GitHub's Container registry authentication instructions](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry#authenticating-with-a-personal-access-token-classic).

Validate anonymous access with an explicit pull from a clean Docker client
without GHCR credentials:

```console
docker pull ghcr.io/wonsuk-emsec/modern-cryptography-2026-lab02-target:2026-lab02-v1
```

Starting a cached local build verifies container behavior only; it does not
verify publication or public pull access. A single-platform build also does
not establish compatibility with every student CPU architecture. Test each
intended platform before releasing; a multi-platform release needs a matching
course base for each platform and one release manifest.

The instructor's `scripts/build_student_release.sh OUTPUT_DIRECTORY` creates
the source archive only. GHCR supplies the matching target image. When local
validation is finished, clean up from the host terminal:

```console
docker compose -f docker/compose.yml --profile lab02 down
```
