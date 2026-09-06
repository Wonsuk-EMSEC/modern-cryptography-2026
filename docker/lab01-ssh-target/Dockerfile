FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install --no-install-recommends --yes openssh-server \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash \
        --password '$6$lab01ssh$5FtlBc6csb5qgcfDvlcbWJNT.n/3uPTj4rD6uOXaa2ugk1W0Sl1ZSMgG2/8P4eh1Vn0CXgWC4Gluj7FFwqqqH/' \
        labstudent \
    && ssh-keygen -A

COPY docker/lab01-ssh-target/sshd_config /etc/ssh/sshd_config

EXPOSE 22

HEALTHCHECK --interval=2s --timeout=2s --retries=10 \
    CMD ssh-keyscan -T 1 localhost >/dev/null 2>&1 || exit 1

CMD ["/bin/sh", "-c", "mkdir -p /run/sshd && exec /usr/sbin/sshd -D -e"]
