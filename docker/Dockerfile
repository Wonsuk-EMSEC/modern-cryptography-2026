FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive
ARG STUDENT_UID=1000
ARG STUDENT_GID=1000

RUN apt-get update \
    && apt-get install --no-install-recommends --yes \
        build-essential \
        ca-certificates \
        curl \
        g++ \
        gcc \
        gdb \
        git \
        aircrack-ng \
        john \
        libssl-dev \
        make \
        openssl \
        python3 \
        python3-pip \
        python3-venv \
        tshark \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/course-venv \
    && /opt/course-venv/bin/pip install --no-cache-dir \
        cryptography==45.0.6 \
        argon2-cffi==25.1.0 \
        bcrypt==4.3.0 \
        jupyterlab==4.4.6 \
        lark==1.2.2 \
        paramiko==5.0.0 \
        pycryptodome==3.23.0 \
        pytest==8.4.1

RUN if getent group "${STUDENT_GID}" >/dev/null; then \
        existing_group="$(getent group "${STUDENT_GID}" | cut -d: -f1)"; \
        groupmod --new-name student "${existing_group}"; \
    else \
        groupadd --gid "${STUDENT_GID}" student; \
    fi \
    && if getent passwd "${STUDENT_UID}" >/dev/null; then \
        existing_user="$(getent passwd "${STUDENT_UID}" | cut -d: -f1)"; \
        usermod --login student --home /home/student --move-home \
            --gid "${STUDENT_GID}" --groups '' --shell /bin/bash "${existing_user}"; \
    else \
        useradd --create-home --uid "${STUDENT_UID}" --gid "${STUDENT_GID}" \
            --shell /bin/bash student; \
    fi

ENV PATH="/opt/course-venv/bin:${PATH}"

WORKDIR /workspace
USER student

EXPOSE 8888

CMD ["bash"]
