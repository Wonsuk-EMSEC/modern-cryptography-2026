#!/usr/bin/env python3
"""Summarize 802.11 and EAPOL-Key records in the supplied course PCAP."""

from __future__ import annotations

import argparse
import struct
from pathlib import Path


def mac(raw: bytes) -> str:
    return ":".join(f"{value:02x}" for value in raw)


def pcap_packets(path: Path):
    data = path.read_bytes()
    if data[:4] != b"\xd4\xc3\xb2\xa1":
        raise ValueError("expected a little-endian microsecond PCAP file")
    offset = 24
    while offset + 16 <= len(data):
        _, _, captured_length, _ = struct.unpack_from("<IIII", data, offset)
        offset += 16
        packet = data[offset : offset + captured_length]
        offset += captured_length
        if len(packet) != captured_length:
            raise ValueError("truncated PCAP packet")
        yield packet


def summarize(path: Path) -> dict[str, object]:
    networks: dict[str, str] = {}
    messages: list[dict[str, object]] = []
    packet_count = 0
    for packet in pcap_packets(path):
        packet_count += 1
        if len(packet) < 4:
            continue
        radiotap_length = int.from_bytes(packet[2:4], "little")
        frame = packet[radiotap_length:]
        if len(frame) < 24:
            continue
        control = int.from_bytes(frame[:2], "little")
        frame_type = (control >> 2) & 3
        subtype = (control >> 4) & 15

        if frame_type == 0 and subtype in (5, 8):
            ies = frame[36:]
            index = 0
            while index + 2 <= len(ies):
                tag, size = ies[index], ies[index + 1]
                value = ies[index + 2 : index + 2 + size]
                index += 2 + size
                if tag == 0 and value:
                    networks[mac(frame[16:22])] = value.decode("utf-8", "replace")
                    break

        if frame_type != 2:
            continue
        to_ds, from_ds = (control >> 8) & 1, (control >> 9) & 1
        header_length = 24 + (6 if to_ds and from_ds else 0) + (2 if subtype & 8 else 0)
        if frame[header_length : header_length + 8] != bytes.fromhex("aaaa03000000888e"):
            continue
        eapol = frame[header_length + 8 :]
        if len(eapol) < 99 or eapol[1] != 3:
            continue
        key_info = int.from_bytes(eapol[5:7], "big")
        ack, mic_set = bool(key_info & 0x80), bool(key_info & 0x100)
        secure = bool(key_info & 0x200)
        if ack and not mic_set:
            label = "M1"
        elif mic_set and not ack and not secure:
            label = "M2"
        elif ack and mic_set:
            label = "M3"
        elif mic_set and not ack and secure:
            label = "M4"
        else:
            label = "other"
        messages.append(
            {
                "message": label,
                "receiver": mac(frame[4:10]),
                "transmitter": mac(frame[10:16]),
                "bssid": mac(frame[16:22]),
                "replay_counter": int.from_bytes(eapol[9:17], "big"),
            }
        )
    return {"packet_count": packet_count, "networks": networks, "messages": messages}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pcap", type=Path, help="instructor-provided local PCAP")
    args = parser.parse_args()
    summary = summarize(args.pcap)
    print(f"Packets: {summary['packet_count']}")
    for bssid, ssid in summary["networks"].items():
        print(f"Network: SSID={ssid} BSSID={bssid}")
    print(f"EAPOL-Key frames: {len(summary['messages'])}")
    for message in summary["messages"]:
        print(
            f"{message['message']}: {message['transmitter']} -> {message['receiver']} "
            f"(replay={message['replay_counter']})"
        )


if __name__ == "__main__":
    main()
