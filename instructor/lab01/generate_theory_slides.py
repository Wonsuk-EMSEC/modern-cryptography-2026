#!/usr/bin/env python3
"""Generate the student-facing Lab 01 theory slide deck using only Python."""

from __future__ import annotations

import zipfile
from datetime import UTC, datetime
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "labs" / "lab01" / "LAB01_PASSWORD_AUTHENTICATION_THEORY.pptx"

EMU = 914400
WIDTH = int(13.333 * EMU)
HEIGHT = int(7.5 * EMU)

NAVY = "0B132B"
NAVY_2 = "15213D"
PANEL = "1C2C4C"
WHITE = "F7FAFC"
MUTED = "B7C4D6"
CYAN = "38BDF8"
TEAL = "2DD4BF"
ORANGE = "FB923C"
RED = "F87171"
GREEN = "4ADE80"
YELLOW = "FACC15"


def inch(value: float) -> int:
    return int(value * EMU)


def para(
    text: str,
    size: int = 20,
    color: str = WHITE,
    *,
    bold: bool = False,
    bullet: bool = False,
    align: str = "l",
) -> str:
    bullet_xml = '<a:buChar char="•"/>' if bullet else "<a:buNone/>"
    margin = ' marL="342900" indent="-228600"' if bullet else ""
    return (
        f'<a:p><a:pPr algn="{align}"{margin}>{bullet_xml}</a:pPr>'
        f'<a:r><a:rPr lang="en-US" sz="{size * 100}" b="{1 if bold else 0}">' 
        f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill>'
        '<a:latin typeface="Aptos"/></a:rPr>'
        f'<a:t>{escape(text)}</a:t></a:r>'
        f'<a:endParaRPr lang="en-US" sz="{size * 100}"/></a:p>'
    )


def textbox(
    shape_id: int,
    name: str,
    x: float,
    y: float,
    w: float,
    h: float,
    paragraphs: list[str],
    *,
    fill: str | None = None,
    line: str | None = None,
    radius: bool = False,
    margin: float = 0.12,
) -> str:
    geometry = "roundRect" if radius else "rect"
    fill_xml = (
        f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>' if fill else "<a:noFill/>"
    )
    line_xml = (
        f'<a:ln w="12700"><a:solidFill><a:srgbClr val="{line}"/></a:solidFill></a:ln>'
        if line
        else "<a:ln><a:noFill/></a:ln>"
    )
    return (
        '<p:sp><p:nvSpPr>'
        f'<p:cNvPr id="{shape_id}" name="{escape(name)}"/>'
        '<p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
        '<p:spPr>'
        f'<a:xfrm><a:off x="{inch(x)}" y="{inch(y)}"/>'
        f'<a:ext cx="{inch(w)}" cy="{inch(h)}"/></a:xfrm>'
        f'<a:prstGeom prst="{geometry}"><a:avLst/></a:prstGeom>{fill_xml}{line_xml}'
        '</p:spPr><p:txBody>'
        f'<a:bodyPr lIns="{inch(margin)}" rIns="{inch(margin)}" '
        f'tIns="{inch(margin)}" bIns="{inch(margin)}" wrap="square" anchor="t"/>'
        '<a:lstStyle/>' + "".join(paragraphs) + '</p:txBody></p:sp>'
    )


def solid_shape(
    shape_id: int,
    name: str,
    x: float,
    y: float,
    w: float,
    h: float,
    fill: str,
    *,
    geometry: str = "rect",
) -> str:
    return (
        '<p:sp><p:nvSpPr>'
        f'<p:cNvPr id="{shape_id}" name="{escape(name)}"/>'
        '<p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr>'
        f'<a:xfrm><a:off x="{inch(x)}" y="{inch(y)}"/>'
        f'<a:ext cx="{inch(w)}" cy="{inch(h)}"/></a:xfrm>'
        f'<a:prstGeom prst="{geometry}"><a:avLst/></a:prstGeom>'
        f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>'
        '<a:ln><a:noFill/></a:ln></p:spPr></p:sp>'
    )


def base_slide(title: str, section: str, number: int, elements: list[str]) -> str:
    standard = [
        solid_shape(2, "Background", 0, 0, 13.333, 7.5, NAVY),
        solid_shape(3, "Top accent", 0, 0, 13.333, 0.09, CYAN),
        textbox(4, "Section", 0.55, 0.28, 4.0, 0.3, [para(section.upper(), 10, CYAN, bold=True)]),
        textbox(5, "Title", 0.55, 0.62, 12.1, 0.65, [para(title, 28, WHITE, bold=True)]),
        textbox(6, "Footer", 0.55, 7.14, 10.5, 0.22, [para("Modern Cryptographic Applications · Lab 01", 9, MUTED)]),
        textbox(7, "Slide number", 12.15, 7.10, 0.55, 0.25, [para(str(number), 10, CYAN, bold=True, align="r")]),
    ]
    tree = (
        '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
        '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>'
        '<a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
        + "".join(standard + elements)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
        f'<p:cSld><p:spTree>{tree}</p:spTree></p:cSld>'
        '<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>'
    )


def bullets_slide(title: str, section: str, number: int, bullets: list[str], *, note: str | None = None) -> str:
    items = [para(item, 20, WHITE, bullet=True) for item in bullets]
    elements = [textbox(10, "Bullet panel", 0.7, 1.48, 11.9, 4.85, items, fill=NAVY_2, radius=True, margin=0.3)]
    if note:
        elements.append(textbox(11, "Callout", 0.95, 6.48, 11.4, 0.45, [para(note, 13, YELLOW, bold=True)], fill=PANEL, radius=True, margin=0.1))
    return base_slide(title, section, number, elements)


def cards_slide(title: str, section: str, number: int, cards: list[tuple[str, str, str]]) -> str:
    columns = 2 if len(cards) <= 4 else 3
    rows = (len(cards) + columns - 1) // columns
    card_w = 5.85 if columns == 2 else 3.8
    card_h = 2.12 if rows <= 2 else 1.34
    elements: list[str] = []
    for index, (heading, body, color) in enumerate(cards):
        row, col = divmod(index, columns)
        x = 0.7 + col * (card_w + 0.25)
        y = 1.48 + row * (card_h + 0.22)
        elements.append(textbox(20 + index, heading, x, y, card_w, card_h, [para(heading, 18, color, bold=True), para(body, 14, WHITE)], fill=NAVY_2, line=color, radius=True, margin=0.22))
    return base_slide(title, section, number, elements)


def flow_slide(title: str, section: str, number: int, steps: list[tuple[str, str]], *, footer: str) -> str:
    count = len(steps)
    gap = 0.18
    total_w = 11.9
    box_w = (total_w - gap * (count - 1)) / count
    elements: list[str] = []
    colors = (CYAN, TEAL, ORANGE, GREEN, YELLOW)
    for index, (heading, body) in enumerate(steps):
        x = 0.7 + index * (box_w + gap)
        color = colors[index % len(colors)]
        elements.append(textbox(30 + index, heading, x, 2.05, box_w, 2.45, [para(heading, 17, color, bold=True, align="ctr"), para(body, 13, WHITE, align="ctr")], fill=NAVY_2, line=color, radius=True, margin=0.17))
        if index < count - 1:
            elements.append(solid_shape(60 + index, "Arrow", x + box_w - 0.03, 3.0, gap + 0.06, 0.4, color, geometry="rightArrow"))
    elements.append(textbox(80, "Flow note", 1.0, 5.25, 11.3, 0.72, [para(footer, 16, YELLOW, bold=True, align="ctr")], fill=PANEL, radius=True, margin=0.16))
    return base_slide(title, section, number, elements)


def title_slide(number: int) -> str:
    elements = [
        textbox(10, "Course", 0.75, 1.0, 8.4, 0.4, [para("MODERN CRYPTOGRAPHIC APPLICATIONS · FALL 2026", 13, CYAN, bold=True)]),
        textbox(11, "Main title", 0.75, 1.65, 10.8, 1.6, [para("Password-based", 38, WHITE, bold=True), para("Authentication", 38, TEAL, bold=True)]),
        textbox(12, "Subtitle", 0.78, 3.48, 9.5, 0.8, [para("Theory foundation for Lab 01", 22, MUTED), para("Hash → Salt → Offline Guessing → KDFs → Linux → WPA2", 16, WHITE)]),
        textbox(13, "Ethics", 0.78, 5.35, 11.6, 0.85, [para("AUTHORIZED CLASSROOM USE ONLY", 15, ORANGE, bold=True), para("Use only supplied synthetic records, local files, and the approved course PCAP.", 15, WHITE)], fill=NAVY_2, line=ORANGE, radius=True, margin=0.2),
    ]
    return base_slide("", "LAB 01", number, elements)


def build_slides() -> list[str]:
    slides: list[str] = []
    add = slides.append
    add(title_slide(1))
    add(bullets_slide("Learning outcomes", "Orientation", 2, [
        "Explain why plaintext password storage fails and why hashing is not encryption.",
        "Describe what salts prevent—and why salt alone does not stop guessing.",
        "Compare SHA-256, PBKDF2, bcrypt, scrypt, and Argon2id as verifier mechanisms.",
        "Distinguish online authentication attempts from offline verifier testing.",
        "Interpret a synthetic Linux hash and a supplied WPA2 four-way handshake.",
    ], note="Goal: connect every formula to an observable Lab 01 experiment."))
    add(cards_slide("Authorization is part of the experiment", "Orientation", 3, [
        ("Allowed", "Course wordlists, synthetic hashes, local JSON, and the supplied course PCAP.", GREEN),
        ("Not allowed", "Real credentials, public services, arbitrary systems, or third-party captures.", RED),
        ("Offline only", "No packet capture, deauthentication, wireless interface, or network disruption.", CYAN),
        ("Report safely", "Use fictional inputs and redact recovered candidates from public screenshots.", ORANGE),
    ]))
    add(flow_slide("Password verification lifecycle", "Part 1 · Foundations", 4, [
        ("Register", "User supplies a password through a protected channel."),
        ("Derive", "System combines password, salt, and KDF parameters."),
        ("Store", "Save metadata, salt, parameters, and verifier—not plaintext."),
        ("Verify", "Repeat derivation and compare results safely."),
    ], footer="A database leak exposes verifiers; its design determines the cost of offline guessing."))
    add(cards_slide("Hashing is not encryption", "Part 1 · Foundations", 5, [
        ("Encryption", "Reversible with a decryption key. Used when plaintext must be recovered.", ORANGE),
        ("Hash function", "Deterministic one-way mapping to a fixed-size digest. No decryption key.", CYAN),
        ("Password verifier", "A stored value recomputed during login. Should use a dedicated password KDF.", TEAL),
        ("Comparison", "Correct verification asks whether two derived values match—not how to decrypt one.", GREEN),
    ]))
    add(flow_slide("What raw SHA-256 demonstrates", "Part 1 · Foundations", 6, [
        ("Password", "Python string entered with getpass."),
        ("UTF-8", "Encode text into bytes."),
        ("SHA-256", "Fast deterministic hash."),
        ("Digest", "32 bytes shown as 64 hex characters."),
    ], footer="Useful for learning the data flow; unsafe for production password storage because guesses are cheap."))
    add(cards_slide("Salt: unique, public, and necessary", "Part 1 · Foundations", 7, [
        ("Definition", "A fresh random value generated for every stored password.", CYAN),
        ("Stored openly", "The verifier needs the same salt during login; secrecy is not required.", TEAL),
        ("Prevents reuse", "Equal passwords no longer have equal stored values across accounts.", GREEN),
        ("Does not prevent", "An attacker can still test guesses for each known salt.", ORANGE),
    ]))
    add(flow_slide("How an offline dictionary attack works", "Part 2 · Guessing", 8, [
        ("Target file", "Attacker already has authorized toy verifiers."),
        ("Candidate", "Read one word from the small list."),
        ("Compute", "Apply the same hash or KDF and salt rules."),
        ("Compare", "Digest match identifies a candidate."),
    ], footer="No server request occurs: lockout, latency, and server-side rate limiting do not apply."))
    add(cards_slide("Unsalted vs. salted work", "Part 2 · Guessing", 9, [
        ("Unsalted", "Hash each candidate once; compare it with all account targets.", CYAN),
        ("Approximate work", "D candidates → about D hash operations, plus fast lookups.", MUTED),
        ("Salted", "Recompute each candidate separately for each account's salt.", ORANGE),
        ("Approximate work", "T targets × D candidates → up to T·D hash operations.", YELLOW),
    ]))
    add(cards_slide("Time–memory tradeoff and rainbow tables", "Part 2 · Guessing", 10, [
        ("Precompute", "Spend time before the target is known and store reusable chain endpoints.", CYAN),
        ("Tradeoff", "Less storage requires more chain reconstruction during lookup.", TEAL),
        ("Chain merging", "Many-to-one reductions cause collisions and incomplete coverage.", ORANGE),
        ("Salt effect", "A distinct salt changes the function; tables must be rebuilt per salt.", GREEN),
    ]))
    add(bullets_slide("Why password hashing must be slow", "Part 3 · Password KDFs", 11, [
        "A legitimate login computes one verifier; an attacker may compute millions or billions.",
        "A work factor intentionally increases the cost of every candidate.",
        "Memory-hard designs also make massive parallel hardware more expensive.",
        "Parameters belong in the stored record so they can be tuned and upgraded over time.",
        "Cost does not create password entropy: strong, unique passwords are still required.",
    ], note="Tune for acceptable login latency on deployment hardware—not from a universal benchmark table."))
    add(cards_slide("Password KDF landscape", "Part 3 · Password KDFs", 12, [
        ("PBKDF2", "Iteration-based HMAC construction; widely supported, primarily CPU cost.", CYAN),
        ("bcrypt", "Adaptive logarithmic cost; mature, with password-length considerations.", TEAL),
        ("scrypt", "Configurable N, r, p parameters; designed to consume memory.", ORANGE),
        ("Argon2id", "Modern memory-hard design with time, memory, and parallelism controls.", GREEN),
    ]))
    add(flow_slide("A meaningful benchmark", "Part 3 · Password KDFs", 13, [
        ("Warm up", "Run once before recording measurements."),
        ("Repeat", "Collect multiple trials under the same parameters."),
        ("Median", "Reduce sensitivity to occasional scheduling noise."),
        ("Interpret", "Compare relative cost on this machine only."),
    ], footer="Record algorithm, parameters, trial count, hardware context, and median verification time."))
    add(cards_slide("What a stored verifier record needs", "Part 3 · Password KDFs", 14, [
        ("Identity", "Username or account identifier—not a password.", MUTED),
        ("Algorithm", "For example, PBKDF2-HMAC-SHA-256 or Argon2id.", CYAN),
        ("Parameters", "Iterations, memory, parallelism, version, and output length as applicable.", ORANGE),
        ("Salt + verifier", "Unique salt and derived output; compare recomputed values safely.", GREEN),
    ]))
    add(cards_slide("Reading a Linux shadow-style field", "Part 4 · System hashes", 15, [
        ("Account line", "Colon-separated account and password-aging fields.", MUTED),
        ("$id$", "Selects the password hashing scheme; $6$ denotes SHA-512-crypt.", CYAN),
        ("Salt", "Public input required to recompute the verifier.", TEAL),
        ("Verifier", "Derived value—not encrypted plaintext and not directly reversible.", ORANGE),
    ]))
    add(cards_slide("Online vs. offline guessing", "Part 4 · System hashes", 16, [
        ("Online", "Each guess reaches an authentication service. Rate limits and lockouts can react.", CYAN),
        ("Offline", "Guesses are checked against copied data locally. The service sees nothing.", ORANGE),
        ("System hash lab", "Parsing does no guessing; optional John checks the supplied file offline.", TEAL),
        ("Defensive consequence", "Verifier cost and password entropy matter after a database leak.", GREEN),
    ]))
    add(bullets_slide("WPA2-Personal starting point", "Part 5 · WPA2", 17, [
        "The passphrase is not transmitted in the four-way handshake.",
        "Passphrase + SSID derive a 32-byte PMK using PBKDF2-HMAC-SHA1 with 4096 iterations.",
        "AP and station exchange nonces and prove possession of consistent key material.",
        "MAC addresses and fresh nonces bind the derived PTK to endpoints and session.",
        "Captured values can later validate dictionary candidates entirely offline.",
    ], note="This lab begins with an already supplied, authorized course capture."))
    add(flow_slide("WPA2 four-way handshake", "Part 5 · WPA2", 18, [
        ("M1 · AP→STA", "ANonce and replay counter."),
        ("M2 · STA→AP", "SNonce and KCK-based MIC."),
        ("M3 · AP→STA", "Key install/group data and MIC."),
        ("M4 · STA→AP", "Acknowledgement and MIC."),
    ], footer="MIC verification proves consistent key possession; the passphrase itself never crosses the network."))
    add(flow_slide("From passphrase to traffic keys", "Part 5 · WPA2", 19, [
        ("PMK", "PBKDF2(passphrase, SSID, 4096)."),
        ("Context", "Ordered AP/STA MACs + ANonce/SNonce."),
        ("PTK", "PRF-512(PMK, label, context)."),
        ("KCK / KEK / TK", "Confirm messages / protect keys / protect traffic."),
    ], footer="Both endpoints independently derive the same PTK from shared and captured inputs."))
    add(flow_slide("Offline WPA2 candidate verification", "Part 5 · WPA2", 20, [
        ("Guess", "Candidate passphrase + captured SSID."),
        ("Derive", "Candidate PMK, PTK, then KCK."),
        ("Recompute", "Zero EAPOL MIC field and calculate candidate MIC."),
        ("Compare", "Candidate MIC vs. captured MIC."),
    ], footer="A match validates one candidate; it does not reveal a shortcut for arbitrary strong passphrases."))
    add(cards_slide("Defense in depth", "Synthesis", 21, [
        ("Password choice", "Use long, unique passwords and password managers.", GREEN),
        ("Verifier design", "Unique salts and tuned memory-hard password hashing.", CYAN),
        ("Operations", "Protect databases, monitor authentication, rate-limit online attempts.", ORANGE),
        ("Wireless", "Use strong PSKs; consider architectures with different authentication properties.", TEAL),
    ]))
    add(bullets_slide("Lab map and evidence to collect", "Synthesis", 22, [
        "Part 1: repeated and salted digest observations; explain hash vs. encryption.",
        "Part 2: offline computation counts plus bounded online SSH attempts and server logs.",
        "Part 3: KDF benchmark table and a verifier-only JSON authentication record.",
        "Part 4: parsed modular hash fields and justified online/offline classification.",
        "Part 5: M1–M4 summary, PMK→PTK→KCK→MIC diagram, and redacted offline result.",
    ], note="Success means explaining the security consequence—not merely reproducing command output."))
    return slides


def content_types(slide_count: int) -> str:
    overrides = "".join(
        f'<Override PartName="/ppt/slides/slide{i}.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        for i in range(1, slide_count + 1)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>'
        '<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>'
        '<Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>'
        '<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>'
        '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
        '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>'
        f'{overrides}</Types>'
    )


def theme_xml() -> str:
    """Return a schema-compatible minimal Office theme."""
    solid = '<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
    line = '<a:ln w="12700"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln>'
    effect = '<a:effectStyle><a:effectLst/></a:effectStyle>'
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Lab 01 Theme">'
        '<a:themeElements><a:clrScheme name="Lab 01">'
        '<a:dk1><a:srgbClr val="0B132B"/></a:dk1>'
        '<a:lt1><a:srgbClr val="F7FAFC"/></a:lt1>'
        '<a:dk2><a:srgbClr val="15213D"/></a:dk2>'
        '<a:lt2><a:srgbClr val="B7C4D6"/></a:lt2>'
        '<a:accent1><a:srgbClr val="38BDF8"/></a:accent1>'
        '<a:accent2><a:srgbClr val="2DD4BF"/></a:accent2>'
        '<a:accent3><a:srgbClr val="FB923C"/></a:accent3>'
        '<a:accent4><a:srgbClr val="4ADE80"/></a:accent4>'
        '<a:accent5><a:srgbClr val="FACC15"/></a:accent5>'
        '<a:accent6><a:srgbClr val="F87171"/></a:accent6>'
        '<a:hlink><a:srgbClr val="38BDF8"/></a:hlink>'
        '<a:folHlink><a:srgbClr val="2DD4BF"/></a:folHlink>'
        '</a:clrScheme><a:fontScheme name="Aptos">'
        '<a:majorFont><a:latin typeface="Aptos Display"/><a:ea typeface=""/><a:cs typeface=""/></a:majorFont>'
        '<a:minorFont><a:latin typeface="Aptos"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont>'
        '</a:fontScheme><a:fmtScheme name="Lab 01">'
        f'<a:fillStyleLst>{solid}{solid}{solid}</a:fillStyleLst>'
        f'<a:lnStyleLst>{line}{line}{line}</a:lnStyleLst>'
        f'<a:effectStyleLst>{effect}{effect}{effect}</a:effectStyleLst>'
        f'<a:bgFillStyleLst>{solid}{solid}{solid}</a:bgFillStyleLst>'
        '</a:fmtScheme></a:themeElements><a:objectDefaults/><a:extraClrSchemeLst/></a:theme>'
    )


def package_parts(slides: list[str]) -> dict[str, str]:
    slide_ids = "".join(f'<p:sldId id="{255 + i}" r:id="rId{2 + i}"/>' for i in range(1, len(slides) + 1))
    relationships = [
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>'
    ]
    relationships.extend(
        f'<Relationship Id="rId{2 + i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>'
        for i in range(1, len(slides) + 1)
    )
    now = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    parts = {
        "[Content_Types].xml": content_types(len(slides)),
        "_rels/.rels": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/><Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/></Relationships>',
        "docProps/core.xml": f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:title>Lab 01: Password-based Authentication</dc:title><dc:subject>Theory foundation</dc:subject><dc:creator>Modern Cryptographic Applications course staff</dc:creator><cp:lastModifiedBy>Course staff</cp:lastModifiedBy><dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created><dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified></cp:coreProperties>',
        "docProps/app.xml": f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"><Application>Microsoft Office PowerPoint</Application><PresentationFormat>Widescreen</PresentationFormat><Slides>{len(slides)}</Slides><Notes>0</Notes><HiddenSlides>0</HiddenSlides><Company>Modern Cryptographic Applications</Company><AppVersion>16.0000</AppVersion></Properties>',
        "ppt/presentation.xml": f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst><p:sldIdLst>{slide_ids}</p:sldIdLst><p:sldSz cx="{WIDTH}" cy="{HEIGHT}" type="screen16x9"/><p:notesSz cx="6858000" cy="9144000"/><p:defaultTextStyle/></p:presentation>',
        "ppt/_rels/presentation.xml.rels": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' + "".join(relationships) + '</Relationships>',
        "ppt/slideMasters/slideMaster1.xml": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld><p:clrMap accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" bg1="lt1" bg2="lt2" folHlink="folHlink" hlink="hlink" tx1="dk1" tx2="dk2"/><p:sldLayoutIdLst><p:sldLayoutId id="1" r:id="rId1"/></p:sldLayoutIdLst><p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles></p:sldMaster>',
        "ppt/slideMasters/_rels/slideMaster1.xml.rels": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/></Relationships>',
        "ppt/slideLayouts/slideLayout1.xml": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank" preserve="1"><p:cSld name="Blank"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>',
        "ppt/slideLayouts/_rels/slideLayout1.xml.rels": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/></Relationships>',
        "ppt/theme/theme1.xml": theme_xml(),
    }
    for index, slide in enumerate(slides, 1):
        parts[f"ppt/slides/slide{index}.xml"] = slide
        parts[f"ppt/slides/_rels/slide{index}.xml.rels"] = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/></Relationships>'
    return parts


def main() -> None:
    slides = build_slides()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, value in package_parts(slides).items():
            archive.writestr(name, value.encode("utf-8"))
    print(f"Created {OUTPUT.relative_to(ROOT)} ({len(slides)} slides)")


if __name__ == "__main__":
    main()
