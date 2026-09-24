# Lab01 SSH target image

This directory contains the build files for the extra SSH service used in
Lab01 Part 2. The common student environment is built from `docker/Dockerfile`.
Both containers are run through `docker/compose.yml`.

- `Dockerfile` installs and starts the SSH server.
- `sshd_config` configures the isolated classroom service.

Students can build this target from the supplied files. Run these commands
from the repository root in the host terminal:

```console
docker compose -f docker/compose.yml --profile lab01-ssh build course lab01-ssh-target
docker compose -f docker/compose.yml --profile lab01-ssh up -d --wait course lab01-ssh-target
docker compose -f docker/compose.yml exec course bash
```

Inside the course shell, go to the Part directory:

```console
cd /workspace/labs/lab01/part2_dictionary_attack
```

Follow the [Part 2 instructions](../../labs/lab01/part2_dictionary_attack/README.md)
for the exercise. The client connects to `lab01-ssh-target` on port 22 through
the internal Docker network. The target does not publish a host port.

After leaving the shell with `exit`, stop just the SSH target from the host:

```console
docker compose -f docker/compose.yml --profile lab01-ssh stop lab01-ssh-target
```

The shared course container and other lab targets remain available. See the
[common Docker instructions](../README.md) for shutting down all lab services.
