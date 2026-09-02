# Modern Cryptography Applications 2026

Course repository for hands-on exercises and assignments.

## Ethical and Authorized Use

Course security exercises may be performed only on supplied synthetic data,
local containers, and instructor-controlled systems for which explicit
authorization has been granted. Do not test real credentials, public services,
or third-party networks. Lab-specific restrictions appear in each lab README.

## Repository Structure

- `docker/`: Docker-based course environment
- `labs/`: Hands-on laboratory exercises
- `assignments/`: Assignments
- `common/`: Shared scripts and datasets
- `instructor/`: Instructor materials

## Environment

All exercises are intended to run inside the provided Docker environment.

## Docker Environment

The course Docker image provides the software and libraries used by the labs.
Students should use Docker as the execution environment while keeping their
work in this Git repository.

### 1. Prerequisites

Install the following software before starting:

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Git](https://git-scm.com/)
- WSL2 is recommended for Windows users.
- [Visual Studio Code](https://code.visualstudio.com/) is optional and can be
  used to edit the repository files.

Open a terminal in the root directory of this repository before running the
commands below.

The same `docker compose` commands work in Windows PowerShell and macOS/Linux
terminals. In VS Code, you may edit on the host and use its **Attach to Running
Container** command after starting a long-running course container; a Dev
Container configuration is not required.

### 2. Build the course Docker image

```console
docker compose -f docker/compose.yml build
```

This builds the `modern-cryptography-2026` image and installs the software and
libraries required for the course. The initial build may take several minutes.

### 3. Start an interactive course container

```console
docker compose -f docker/compose.yml run --rm course bash
```

Here, `course` is the Docker Compose service name. The `--rm` option removes the
temporary container after it exits. The Git repository is mounted inside the
container at `/workspace`, so files created or modified under `/workspace`
modify the repository on the host computer as well.

### 4. Verify the environment

After the container starts, run:

```console
whoami
pwd
python3 --version
gcc --version
openssl version
```

The expected user is `student`, and the expected working directory is
`/workspace`. Version numbers may vary when the course image is updated.

### 5. Run a lab

For example, to open Lab 01:

```console
cd /workspace/labs/lab01
ls
```

Each lab may provide additional setup, task, and test instructions in its own
`README.md`.

For Lab 01:

```console
cd /workspace/labs/lab01
pytest -q
```

### 6. Exit the container

```console
exit
```

The temporary container is removed, but files under `/workspace` remain because
they are stored in the host Git repository.

### 7. Rebuild the environment

If `docker/Dockerfile` changes, rebuild the image:

```console
docker compose -f docker/compose.yml build
```

For troubleshooting, you can force Docker to rebuild every layer:

```console
docker compose -f docker/compose.yml build --no-cache
```

The `--no-cache` option is normally unnecessary and makes the build slower.

### 8. Run JupyterLab (optional)

JupyterLab is included in the course image. Start it from the repository root:

```console
docker compose -f docker/compose.yml run --rm --service-ports course \
  jupyter lab --ip=0.0.0.0 --no-browser
```

The `--service-ports` option publishes port 8888 as configured in
`docker/compose.yml`. Open the URL printed by JupyterLab in a browser, including
its access token. Press `Ctrl+C` in the terminal to stop JupyterLab.

### 9. Important notes

- Do not install course dependencies manually with `apt` or `pip` unless a lab
  or instructor explicitly tells you to do so. Required dependencies should be
  provided by the Docker image.
- Do not create important course files outside `/workspace` inside the
  temporary container; those files may disappear when the container exits.
- Normally, edit files in the host Git repository and use Docker to run and
  test them.

### Direct local Python setup (alternative)

Docker is the supported and reproducible course environment. If Docker cannot
be used, Python 3.12 users may create a virtual environment and install the
Lab 01 Python requirements locally:

```console
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r labs/lab01/requirements.txt
cd labs/lab01
pytest -q
```

In PowerShell, activate with `.venv\Scripts\Activate.ps1`. This alternative
does not install optional system tools such as John the Ripper or aircrack-ng;
do not install them unless the instructor explicitly requires those optional
exercises.
