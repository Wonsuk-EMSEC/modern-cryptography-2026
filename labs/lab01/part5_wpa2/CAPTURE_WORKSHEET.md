# Part 5 capture worksheet

Name:
Date:

Use only `../data/wpa2/lab01-handshake.pcap`. Complete this worksheet by reading
the Wireshark or TShark decoded packet tree. Do not use a Python parser or an
automated field-export command. Do not record the recovered passphrase.

## Network identification

| Observation | Your result | Frame number and protocol-tree location |
| --- | --- | --- |
| SSID |  |  |
| BSSID / AP MAC |  |  |
| Station/client MAC |  |  |

How did you distinguish the AP address from the station address?


## Four-way handshake

Enter `0` or `1` for each flag. Record only a shortened nonce or MIC prefix in
this worksheet; keep any full values out of public screenshots and reports.

| Label | Frame | Transmitter -> Receiver | Replay counter | ACK | MIC | Secure | Nonce/MIC observation |
| --- | ---: | --- | ---: | ---: | ---: | ---: | --- |
| M1 |  |  |  |  |  |  |  |
| M2 |  |  |  |  |  |  |  |
| M3 |  |  |  |  |  |  |  |
| M4 |  |  |  |  |  |  |  |

What evidence supports each label rather than simply assuming capture order?


How do the replay counters relate the messages?


Why is the M1 MIC behavior different from M2-M4?


## Offline verification

Which observed fields would an offline checker need for PMK -> PTK -> KCK ->
MIC candidate verification?


Why can this verification proceed without sending a guess to the AP?


## Authorization statement

Explain why this particular activity is authorized and what actions remain out
of scope.
