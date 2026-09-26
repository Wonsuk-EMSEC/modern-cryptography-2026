#!/usr/bin/env python3
"""Part 6 starter: compare two authenticated-encryption orderings."""

from __future__ import annotations

import argparse

from client import ServiceClient


def probe(service: ServiceClient, packet: bytes) -> tuple[str, str]:
    """Submit both controlled changes through the provided service client."""
    modified_iv = bytearray(packet)
    modified_iv[0] ^= 1
    modified_ciphertext = bytearray(packet)
    modified_ciphertext[20] ^= 1
    return (service.query(bytes(modified_iv)),
            service.query(bytes(modified_ciphertext)))


def recover_vulnerable_message(packet: bytes, padding_query) -> bytes:
    """Recover the encrypted message from the service that leaks padding.

    `padding_query` must return True for a valid padding response. Reuse or
    adapt the block-recovery technique from Part 5, then remove the final
    encrypted HMAC-SHA-256 tag from the recovered plaintext.
    """
    # TODO: recover the CBC plaintext with the padding oracle and separate the
    # final 32-byte MAC from the message.
    raise NotImplementedError


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recover-service", choices=("A", "B"),
                        help="service letter selected from your probe results")
    args = parser.parse_args()

    for name in ("A", "B"):
        with ServiceClient(name) as service:
            packet = service.item()
            print(f"Service {name}: original={service.query(packet)}, modified={probe(service, packet)}")

    if args.recover_service is None:
        print("After interpreting the probes, rerun with --recover-service A or B.")
        return

    # TODO: complete recover_vulnerable_message() before using the selected
    # service's padding-validity interface to recover its protected message.
    with ServiceClient(args.recover_service) as service:
        message = recover_vulnerable_message(service.item(), service.padding_valid)
        print(message.decode("ascii"))
        print(f"oracle queries: {service.queries}")


if __name__ == "__main__":
    main()
