# Lab 01 at a Glance

Read this guide before starting Lab 01 to understand the **directory structure**,
**Docker environment**, and **purpose of each part**. Refer to the README in each
part for commands, implementation requirements, checkpoint questions, and report
requirements.

## 1. Learning Flow

Lab 01 explores how passwords and authentication data are stored and verified.

```mermaid
flowchart LR
    P1["Part 1<br/><b>Hashes and Salts</b><br/>Starting point for password storage"]
    P2["Part 2<br/><b>Online SSH Guessing</b><br/>Send candidates directly to a server"]
    P3["Part 3<br/><b>Offline Guessing and KDFs</b><br/>Check acquired verifiers locally"]
    P4["Part 4<br/><b>Table Attacks</b><br/>Reuse precomputed results"]
    P5["Part 5<br/><b>WPA2 Capture and Verification</b><br/>Inspect packets and implement an offline check"]

    P1 -->|Storage basics| P2
    P2 -->|Compare online and offline| P3
    P3 -->|Extend to precomputation| P4
    P4 -->|Apply to network authentication| P5

    classDef base fill:#e8f4ff,stroke:#337ab7,stroke-width:2px,color:#172b4d
    classDef online fill:#fff4d6,stroke:#d89b00,stroke-width:2px,color:#4a3400
    classDef offline fill:#f3e8ff,stroke:#845ec2,stroke-width:2px,color:#2f1b4d
    class P1 base
    class P2 online
    class P3,P4,P5 offline
```

- **Online guessing:** Each candidate is sent to a live authentication server. The
  server can observe, record, or limit the attempts.
- **Offline guessing:** Candidates are checked locally against an acquired verifier
  or capture file. No requests are sent to the authentication server.

## 2. Directories and Execution Environment

The lab materials are stored in one Git repository, while the programs run inside
Docker containers.

| Component | Role |
| --- | --- |
| Git repository on the host | Stores the README files, code, and data |
| `course` container | Provides the shared environment for Python and lab tools |
| `lab01-ssh-target` container | Provides the isolated SSH server used only in Part 2 |

The host repository is mounted at `/workspace` in the `course` container. A file
saved on the host is therefore immediately visible inside the container.

```mermaid
flowchart LR
    subgraph HOST["Your computer · Host"]
        REPO["Git repository<br/>README · code · data"]
        EDITOR["Editor<br/>Read and modify files"]
        LOG["Second terminal<br/>Observe Part 2 logs"]
    end

    subgraph DOCKER["Inside Docker"]
        COURSE["course container<br/>/workspace<br/>Run lab programs"]
        SSH["SSH target container<br/>Part 2 authentication server"]
    end

    EDITOR -->|Save| REPO
    REPO -. "Mounted at /workspace" .-> COURSE
    COURSE -->|Authentication requests<br/>in Part 2 only| SSH
    LOG -->|Check status and logs| SSH

    classDef host fill:#e8f4ff,stroke:#337ab7,stroke-width:2px,color:#172b4d
    classDef container fill:#eaf8e6,stroke:#4c9a2a,stroke-width:2px,color:#173b0b
    class REPO,EDITOR,LOG host
    class COURSE,SSH container
```

```text
labs/lab01/
├── README.md                       Official overview of Lab 01
├── STUDENT_WORKFLOW_GUIDE.md       This structural guide
├── data/                           Lab data shared by the parts
├── part1_hashing/                  Hashes and salts
├── part2_dictionary_attack/        Online SSH guessing
├── part3_password_kdfs/            Offline guessing and KDFs
├── part4_system_hashes/            System verifiers and table attacks
├── part5_wpa2/                     WPA2 capture verification
└── report/                         Report materials
```

The README in each `part.../` directory gives the instructions and submission
criteria for that part.

## 3. Part 1: Hashes and Salts

Part 1 introduces the basic idea of transforming a password into a verifier instead
of storing the password itself.

```mermaid
flowchart LR
    P1[Same password] --> H1[SHA-256]
    P1 --> H2[SHA-256]
    H1 --> D1[Same digest]
    H2 --> D1

    P2[Same password] --> S1[Combine with random salt A]
    P2 --> S2[Combine with random salt B]
    S1 --> V1[Different verifier A]
    S2 --> V2[Different verifier B]

    classDef input fill:#e8f1ff,stroke:#4676b8,color:#172b4d
    classDef process fill:#fff3cd,stroke:#c69500,color:#4d3b00
    classDef result fill:#e7f7ed,stroke:#3a8f5c,color:#153d26
    class P1,P2 input
    class H1,H2,S1,S2 process
    class D1,V1,V2 result
```

Without a salt, the same password produces the same digest. With a random salt,
the same password produces different verifiers.

## 4. Part 2: Online SSH Guessing in an Isolated Environment

Part 2 demonstrates that **online guessing requires communication with a server for
every candidate**. This is the only part that uses both the `course` container and
the SSH target container.

```mermaid
sequenceDiagram
    autonumber
    participant P as course container<br/>Python program
    participant S as SSH target<br/>Authentication server
    participant L as Host terminal<br/>Server logs

    loop Check each candidate in the wordlist
        P->>S: SSH authentication request
        S-->>P: Success or failure
        S-->>L: Authentication-attempt log
    end
    P->>P: Review the attempt count and elapsed time
```

The Python program initiates the experiment, and the SSH target receives its
requests. The log terminal is an observation window for the existing target, not a
second server.

## 5. Part 3: Offline Guessing and Password KDFs

Part 3 examines how salts affect an attacker's workload and why a password KDF
slows candidate testing.

```mermaid
flowchart TB
    W[Select one candidate]

    subgraph U[Unsalted: reuse is possible]
        UH[Hash the candidate once]
        UA[Compare with account A]
        UB[Compare with account B]
        UC[Compare with account C]
        UH --> UA
        UH --> UB
        UH --> UC
    end

    subgraph S[Salted: per-account work is required]
        SA[Candidate + account A salt → hash]
        SB[Candidate + account B salt → hash]
        SC[Candidate + account C salt → hash]
    end

    W --> UH
    W --> SA
    W --> SB
    W --> SC
    SA --> K[A slow password KDF also raises<br/>the cost of each computation]
    SB --> K
    SC --> K

    classDef source fill:#e8f1ff,stroke:#4676b8,color:#172b4d
    classDef compute fill:#fff3cd,stroke:#c69500,color:#4d3b00
    classDef compare fill:#e7f7ed,stroke:#3a8f5c,color:#153d26
    class W source
    class UH,SA,SB,SC,K compute
    class UA,UB,UC compare
```

A salt requires separate computation for each account. A password KDF also makes
each computation slower, increasing the cost of testing many candidates.

## 6. Part 4: System Verifiers and Table Attacks

Part 4 has two goals:

- Identify the algorithm, parameters, salt, and verifier in a system hash string.
- Compare storage and lookup costs when an attacker saves precomputed results.

```mermaid
flowchart TB
    C[Same candidate set]

    subgraph F[Full precomputation table]
        F1[Hash every candidate]
        F2[Store every digest and candidate]
        F3[Look up a digest directly]
        F1 --> F2 --> F3
    end

    subgraph R[Rainbow table]
        R1[Repeat hash → reduction]
        R2[Store only chain starts and ends]
        R3[Recompute chains during lookup]
        R1 --> R2 --> R3
    end

    C --> F1
    C --> R1
    F3 --> FT[More storage<br/>Less lookup computation]
    R3 --> RT[Less storage<br/>More lookup work and possible misses]

    classDef source fill:#e8f1ff,stroke:#4676b8,color:#172b4d
    classDef full fill:#e7f7ed,stroke:#3a8f5c,color:#153d26
    classDef rainbow fill:#f2e9ff,stroke:#7952b3,color:#352050
    class C source
    class F1,F2,F3,FT full
    class R1,R2,R3,RT rainbow
```

A full precomputation table stores more results to reduce lookup work. A rainbow
table stores only the start and end of each chain, saving space at the cost of
recomputing chains during lookup. A reduction function is not the inverse of a
hash; it maps a digest back into the candidate space.

## 7. Part 5: WPA2 Capture and Offline Verification

Part 5 begins with manual packet inspection and then connects the observed WPA2
fields to a candidate-verification implementation.

| Material | Purpose |
| --- | --- |
| PCAP | Manually locate the network and M1-M4 fields with Wireshark or TShark |
| `CAPTURE_WORKSHEET.md` | Record packet evidence without an automated parser |
| Synthetic JSON | Provide a separate, reproducible calculation fixture |
| Python starter and tests | Implement and verify the PMK-to-MIC pipeline |

```mermaid
flowchart LR
    A["Exercise A<br/><b>Inspect the PCAP manually</b><br/>Locate fields and identify M1-M4"]
    B["Exercise B<br/><b>Implement candidate verification</b><br/>PMK → PTK → KCK → MIC"]
    C["Exercise C<br/><b>Run a bounded comparison</b><br/>Use the supplied PCAP and wordlist"]
    A -->|Record worksheet evidence| B
    B -->|Run implementation tests| C

    classDef observe fill:#e8f4ff,stroke:#337ab7,stroke-width:2px,color:#172b4d
    classDef implement fill:#fff4d6,stroke:#d89b00,stroke-width:2px,color:#4a3400
    classDef compare fill:#f3e8ff,stroke:#845ec2,stroke-width:2px,color:#2f1b4d
    class A observe
    class B implement
    class C compare
```

```mermaid
flowchart LR
    A[Candidate + SSID] -->|PBKDF2| B[32-byte PMK]
    B -->|Ordered MACs and nonces| C[64-byte PTK]
    C -->|First 16 bytes| D[KCK]
    E[Normalized EAPOL] --> F[HMAC-SHA1]
    D --> F
    F -->|First 16 bytes| G[Candidate MIC]
    H[Captured MIC] --> I{Constant-time match?}
    G --> I
```

```mermaid
sequenceDiagram
    participant AP as Access point
    participant STA as Station
    AP->>STA: M1 · Send ANonce
    STA->>AP: M2 · Send SNonce and MIC
    AP->>STA: M3 · Instruct key installation
    STA->>AP: M4 · Confirm installation
```

The PCAP and synthetic JSON are separate classroom datasets. Candidate
verification uses local values and sends no new authentication request to the
access point.

## 8. Where to Go Next

After you understand the overall structure, read `labs/lab01/README.md` for the lab
sequence and then open the README for the part you are working on. Follow that
README for commands, code requirements, tests, checkpoints, and report criteria.
