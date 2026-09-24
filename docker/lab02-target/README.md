# Lab02 target image

This directory contains the build recipe for the extra service used in Lab02
Parts 4–6. The common student environment is built from `docker/Dockerfile`.
Both containers are run through `docker/compose.yml`.

Students load the supplied `lab02-target-image.tar.gz` and start the target
using the [Lab02 setup instructions](../../labs/lab02/README.md#setup). They do
not need to build this target. The server source and secret data are kept in
the private instructor checkout, so a student checkout alone cannot build it.

Course staff run these commands from the private repository root:

```console
docker compose -f docker/compose.yml build course
docker build -f docker/lab02-target/Dockerfile -t modern-cryptography-2026-lab02-target .
docker compose -f docker/compose.yml --profile lab02 up -d --wait course lab02-target
```

The Dockerfile copies `instructor/lab02/targets/` into the target image. Keep
that directory private and export an image matching the distributed Lab02
data, as described in the instructor notes. The shared course image can be
built without any instructor files.
