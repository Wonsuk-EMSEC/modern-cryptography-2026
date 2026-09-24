# Modern Cryptography Applications 2026

Course repository for hands-on cryptography exercises.

## Ethical and Authorized Use

Course security exercises may be performed only on supplied synthetic data,
local containers, and instructor-controlled systems for which explicit
authorization has been granted. Do not test real credentials, public services,
or third-party networks. Lab-specific restrictions appear in each lab README.

## Repository Structure

- `docker/`: Docker-based course environment
- `labs/`: Hands-on laboratory exercises
- `instructor/`: Instructor materials

## Environment

All exercises are intended to run inside the provided Docker environment.

## Docker Environment

The course Docker image provides the software and libraries used by the labs.
Students should use Docker as the execution environment while keeping their
work in this Git repository.

Every lab uses the same `docker/Dockerfile` and the `course` service in
`docker/compose.yml`. Parts that need an extra server use a target Dockerfile
under `docker/`, such as `lab01-ssh-target/` or `lab02-target/`. Start those
services only when the Part requires them. See [the Docker layout and service
commands](docker/README.md) for details; Lab02 uses an instructor-supplied
target image that Compose automatically pulls from public GHCR; its server
implementation and secrets are excluded from the student source release but
are present in the locally inspectable runtime image.

### 0. Prerequisites

Install the following software before starting:

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Git](https://git-scm.com/)
- WSL2 with Ubuntu is required for Windows users.
- [Visual Studio Code](https://code.visualstudio.com/) is optional and can be
  used to edit the repository files.

On Windows, open PowerShell and enter Ubuntu before cloning the repository:

```powershell
wsl -d Ubuntu
```

Run the remaining Git and Docker commands inside Ubuntu. Make sure Docker
Desktop's WSL integration is enabled for Ubuntu. On macOS and Linux, run the
commands directly in a terminal.

### 1. Clone the course repository

Open a terminal in the directory where you want to keep the course files, then
clone the repository and enter its root directory:

```console
git clone https://github.com/Wonsuk-EMSEC/modern-cryptography-2026.git
cd modern-cryptography-2026
```

Run the remaining commands from this repository root directory.

### 2. Build the course Docker image

```console
docker compose -f docker/compose.yml build course
```

This builds the `modern-cryptography-2026` image and installs the software and
libraries required for the course. The initial build may take several minutes.

### 3. Start the course container in the background

Start the `course` service in detached mode:

```console
docker compose -f docker/compose.yml up -d course
```

Here, `course` is the Docker Compose service name, and the `-d` option runs the
container in the background.

You can check whether the container is running with:

```console
docker compose -f docker/compose.yml ps
```

To open an interactive shell inside the running course container, use:

```console
docker compose -f docker/compose.yml exec course bash
```

The Git repository is mounted inside the container at `/workspace`, so files
created or modified under `/workspace` modify the repository on the host
computer as well.

You can leave the interactive shell by running:

```console
exit
```

Exiting the shell does not stop the course container because it continues to run
in the background. You can enter the container again at any time with:

```console
docker compose -f docker/compose.yml exec course bash
```

When you are finished with all labs, stop and remove the course container,
optional targets, and their networks with:

```console
docker compose -f docker/compose.yml --profile lab01-ssh --profile lab02 down
```


### 4. Verify the environment

After entering the course container, run the following commands:

```console
whoami
pwd
python3 --version
gcc --version
openssl version
```

Example output:

```text
student
/workspace
Python 3.12.3
gcc (Ubuntu 13.3.0-6ubuntu2~24.04) 13.3.0
OpenSSL 3.0.13 30 Jan 2024
```

The expected user is `student`, and the expected working directory is
`/workspace`.

The version numbers shown above are examples and may vary when the course image
is updated. The important point is that each command executes successfully and
reports the installed software version.


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

This closes the shell. The course container continues running, and files under
`/workspace` remain in the host Git repository. Use the shutdown command in
step 3 when you are finished with all containers.

### 7. Rebuild the environment

If `docker/Dockerfile` changes, rebuild the image:

```console
docker compose -f docker/compose.yml build course
```

For troubleshooting, you can force Docker to rebuild every layer:

```console
docker compose -f docker/compose.yml build --no-cache course
```

The `--no-cache` option is normally unnecessary and makes the build slower.
After rebuilding, run `docker compose -f docker/compose.yml up -d course`
to recreate the course container with the updated image.

### 8. Run JupyterLab (optional)

JupyterLab is included in the course image. Start it in the shared course
container from the repository root:

```console
docker compose -f docker/compose.yml up -d course
docker compose -f docker/compose.yml exec course \
  jupyter lab --ip=0.0.0.0 --no-browser
```

The course container publishes port 8888 as configured in `docker/compose.yml`.
Open the URL printed by JupyterLab in a browser, including its access token.
Press `Ctrl+C` in the terminal to stop JupyterLab; the course container remains
running.

### 9. Important notes

- Do not install course dependencies manually with `apt` or `pip` unless a lab
  or instructor explicitly tells you to do so. Required dependencies should be
  provided by the Docker image.
- Keep important course files under `/workspace`; files elsewhere in the
  container are lost when it is removed or recreated.
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
