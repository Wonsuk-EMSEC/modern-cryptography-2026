# Course Repository Instructions

This repository is used for the 2026 Modern Cryptography Applications course.

## General Principles

- All laboratory exercises must run inside the provided Docker environment.
- Students should not need to manually install additional software.
- Prefer simple and reproducible implementations suitable for teaching.
- Prefer Python 3 for cryptographic experiments.
- Use OpenSSL for practical cryptographic exercises where appropriate.
- Use SageMath when number-theoretic or symbolic computation is appropriate.

## Repository Structure

- `docker/`: Docker environment
- `labs/`: Student-facing laboratory exercises
- `assignments/`: Student assignments
- `common/`: Shared scripts and datasets
- `instructor/`: Instructor-only materials

## Lab Structure

Each lab should normally follow this structure:

labs/labXX/
├── README.md
├── starter/
├── data/
└── tests/

Instructor solutions should be placed under:

instructor/labXX/

## Student Material Rules

- Never place complete solutions in student-facing directories.
- Do not reveal passwords, secret keys, expected answers, or solution code in student materials unless explicitly requested.
- Starter code may contain TODO sections for students to complete.
- README files should explain learning objectives, background, tasks, and expected behavior without revealing the solution.

## Docker Rules

- All required dependencies must be installed by the Dockerfile.
- Do not require students to run pip install or apt install manually.
- Keep the image reasonably small where practical.
- Pin dependency versions when reproducibility would otherwise be affected.
- After changing the Docker environment, verify that existing labs still run.

## Validation

Whenever adding or modifying a lab:

1. Build or use the course Docker image.
2. Run the lab inside the container.
3. Run available tests.
4. Verify that previous labs are not broken.
5. Report any issue that could not be verified.

## Modification Rules

- Do not modify previous labs unless the task requires it.
- Do not delete existing course materials without explicit instruction.
- Prefer minimal changes.
