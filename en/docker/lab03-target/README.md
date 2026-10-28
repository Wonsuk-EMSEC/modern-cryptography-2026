# Lab03 Target Image

[한국어](../../../docker/lab03-target/README.md) | **English**

Parts06/08 share one HTTP target accessed from `course`. The `lab03` profile
connects it only to `lab03-internal` and publishes no host ports. Its release tag is:

```text
ghcr.io/wonsuk-emsec/modern-cryptography-2026-lab03-target:2026-lab03-v1
```

Students do not build the target because its source is excluded from the student
release. Staff must build, validate, and publish it. Adding repository files does
not publish this tag. For `manifest unknown`, check publication with staff or use
the supplied hosted target address.

## Instructor Build and Validation

From a host terminal at the private instructor repository root:

```console
docker compose -f docker/compose.yml build course
docker compose -f docker/compose.yml run --rm course python3 -m instructor.lab03.generators.build_data --check
docker build -f docker/lab03-target/Dockerfile -t ghcr.io/wonsuk-emsec/modern-cryptography-2026-lab03-target:2026-lab03-v1 .
docker compose -f docker/compose.yml --profile lab03 up -d --wait course lab03-target
docker compose -f docker/compose.yml --profile lab03 ps
docker compose -f docker/compose.yml --profile lab03 logs --tail 30 lab03-target
docker compose -f docker/compose.yml exec course python3 -m instructor.lab03.solve_all --url http://lab03-target:8080
```

Require a `healthy` target and `PASS` for all eight Parts. Docker was unavailable
in this implementation environment, so these container checks have not been run.
Executed host checks and remaining items are recorded in the instructor-only
`instructor/lab03/TEST_REPORT.md`.

The image copies server implementation without grading private keys or flags.
Default startup generates independent RSA-2048 practice keys and practice flags
in memory. Restarting the target replaces keys, sessions, and flags. Users
controlling Docker can inspect images and process memory; local practice secrets
are unsuitable as hidden grading secrets.

## Instructor-Hosted Target

On a host students cannot access, generate private configuration and load it with
`--config /PRIVATE/PATH/config.json` or `LAB03_TARGET_CONFIG`. Inspect generator
usage with `python3 -m instructor.lab03.generators.part06_08 --help`. Use a private,
high-entropy seed and two distinct flags for grading. Keep configuration outside
student distributions and images. Retain the private seed for reproducibility.
The two Parts use independent keys, sessions, and completion conditions.

For a container deployment, mount configuration read-only and set
`LAB03_TARGET_CONFIG` to its container path. The container's `student` UID must be
able to read it. Never run the graded service under student-controlled Docker.
For external access, staff must provide HTTPS and course access control through
separate deployment configuration. The default internal Compose network is for
local practice. Students select the hosted service with `LAB03_TARGET_URL`.

## Publication and Shutdown

After completing validation, publish separately using an authorized account:

```console
docker login ghcr.io
docker push ghcr.io/wonsuk-emsec/modern-cryptography-2026-lab03-target:2026-lab03-v1
```

Verify public access and supported CPU platforms separately after publication.
Do not overwrite published tags with changed contents; distribute changes under
a new version. Successful local execution does not verify public registry pulls.

```console
docker compose -f docker/compose.yml --profile lab03 stop lab03-target
docker compose -f docker/compose.yml --profile lab03 down
```

The first command stops only the target; the second cleans up this Compose project.
