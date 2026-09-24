# Course Docker environment

All labs use one student environment: `docker/Dockerfile` builds the
`modern-cryptography-2026` image, and `docker/compose.yml` runs it as `course`.
Keep the programming tools and Python dependencies for the labs in that
Dockerfile. A Part that needs a separate server adds a target Dockerfile in
its own subdirectory and a service in the same Compose file.

```text
docker/
├── Dockerfile                    # Shared environment for every lab
├── compose.yml                   # Course container and optional targets
├── lab01-ssh-target/
│   ├── Dockerfile                # Lab01 Part 2 SSH server
│   ├── README.md
│   └── sshd_config
└── lab02-target/
    ├── Dockerfile                # Lab02 Parts 4–6 server; staff build
    └── README.md
```

## Build once and use for any lab

Run Docker commands in the host terminal from the repository root:

```console
docker compose -f docker/compose.yml build course
docker compose -f docker/compose.yml up -d course
docker compose -f docker/compose.yml exec course bash
```

Inside the shell, choose a lab, for example `cd /workspace/labs/lab02`.
The repository is mounted at `/workspace`, so edits are saved on the host.
Run `exit` to leave the shell; `course` continues running for the next session.
Rebuild the common image when its Dockerfile changes, then run `up -d course`
again to apply the updated image.

## Start an extra service only when needed

The targets use Compose profiles and do not start with the plain course
command. Run these commands on the host, using the same Compose file.

For Lab01 Part 2, build and start the supplied SSH server:

```console
docker compose -f docker/compose.yml --profile lab01-ssh up -d --build --wait lab01-ssh-target
```

See [lab01-ssh-target/README.md](lab01-ssh-target/README.md) for the target's
build files, course-shell entry, and shutdown command.

For Lab02 Parts 4–6, start the common course container and the prebuilt target:

```console
docker compose -f docker/compose.yml --profile lab02 up -d --wait course lab02-target
docker compose -f docker/compose.yml --profile lab02 ps
```

Compose automatically pulls the public GHCR image
`ghcr.io/wonsuk-emsec/modern-cryptography-2026-lab02-target:2026-lab02-v1`
when needed. The first `up` may take longer while it downloads the image;
no manual image download or registry login is needed. Students do not build
this target locally. Use the Lab02 files and image from the same
**`2026-lab02-v1`** release: Part 5's ciphertext must match the target image.
The target should appear as `healthy` in `ps`.

Use the same `course` shell to run both labs. It can reach each target by its
service name. Each target is on its own internal network, and neither target
publishes a host port. Server runtime data lives in its target container.

The Lab02 target's build recipe is public; its Python server and secret data
are excluded from the student source release. The image contains the private
implementation and secrets needed at runtime and can be inspected by anyone
with local access to it. Solve the exercises through the supplied clients.
See [lab02-target/README.md](lab02-target/README.md) for the staff image
publication workflow.

To stop just the Lab02 target while keeping the course shell and Lab01 server:

```console
docker compose -f docker/compose.yml --profile lab02 stop lab02-target
```

To finish a Lab02 session and remove its target, the course container, and
their networks:

```console
docker compose -f docker/compose.yml --profile lab02 down
```

Use the target-only `stop` command above if you want to keep the course
container available for other labs.

When finished with **all** labs, remove the course container, both targets,
and their networks:

```console
docker compose -f docker/compose.yml --profile lab01-ssh --profile lab02 down
```

## Adding a future lab

1. Add any student tools or libraries to the common `Dockerfile`.
2. If a Part needs a server, add `labXX-target/Dockerfile` and the required
   non-secret build files. Keep private source and values under `instructor/`.
3. Add an optional target service and its internal network to `compose.yml`,
   and attach `course` to that network. Use `build:` for student-buildable
   targets or `image:` for targets supplied as prebuilt images.
4. Document target startup and shutdown in the Part README. Check the new lab
   and the existing labs in the common image.
