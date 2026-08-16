"""
Seed dataset for ThreatGraph.

Every name, IOC value, and CVE id below is synthetic. Indicators use
IP ranges and domain suffixes reserved for documentation by RFC 5737
and RFC 2606 (198.51.100.0/24, 203.0.113.0/24, 192.0.2.0/24, .example)
so nothing here resolves to real infrastructure. Threat actor origins
are given as broad regions rather than specific countries, since this
is illustrative data, not real attribution.

Techniques use real MITRE ATT&CK technique IDs/names/tactics, since
that's a public, standard taxonomy - this is what makes the Technique
data feel grounded rather than arbitrary.

Relationships are wired deterministically (seed=42) rather than by
hand, so the dataset is reproducible and every node ends up with at
least one connection - a raw random sample without that guarantee
tends to leave orphan nodes that make the UI look broken.
"""
import hashlib
import random

RNG = random.Random(42)

# ---------------------------------------------------------------------------
# ThreatActor
# ---------------------------------------------------------------------------
THREAT_ACTORS = [
    ("GRAYWING SPIDER", "Financial Gain", "Eastern Europe"),
    ("VOLT CIRCUIT", "Espionage", "East Asia"),
    ("EMBER JACKAL", "Hacktivism", "Unknown"),
    ("SILENT ATLAS", "Espionage", "Middle East"),
    ("CINDER WOLF", "Destructive/Sabotage", "Eastern Europe"),
    ("QUARTZ FALCON", "Financial Gain", "Southeast Asia"),
    ("HOLLOW MAGPIE", "Espionage", "East Asia"),
    ("RUST VIPER", "Financial Gain", "South America"),
    ("PALE CONDOR", "Hacktivism", "Western Europe"),
    ("IRON THRUSH", "Espionage", "South Asia"),
    ("DUSK BADGER", "Destructive/Sabotage", "Unknown"),
    ("SLATE HERON", "Financial Gain", "North America"),
]

# ---------------------------------------------------------------------------
# Malware
# ---------------------------------------------------------------------------
MALWARE = [
    ("GraniteLocker", "Ransomware", "Windows"),
    ("Emberloom", "Backdoor", "Windows"),
    ("QuietTide", "Infostealer", "Windows"),
    ("Palisade", "RAT", "Cross-platform"),
    ("Cobblehash", "Loader", "Windows"),
    ("Driftwood", "Trojan", "Windows"),
    ("Ashvale", "Wiper", "Linux"),
    ("Sablewing", "Backdoor", "Linux"),
    ("NimbusTap", "Infostealer", "macOS"),
    ("Ironveil", "Ransomware", "Windows"),
    ("Thornbyte", "RAT", "Windows"),
    ("Glasshollow", "Loader", "Cross-platform"),
    ("Cindermoth", "Trojan", "Windows"),
    ("Vaultbreak", "Infostealer", "Windows"),
    ("Duskrunner", "Backdoor", "Cloud"),
    ("Pyrelatch", "Ransomware", "Linux"),
    ("Coalstream", "Worm", "Windows"),
    ("Marrowbind", "Rootkit", "Windows"),
    ("Slatefox", "RAT", "Windows"),
    ("Hollowreed", "Loader", "Windows"),
]

# ---------------------------------------------------------------------------
# Vulnerability (synthetic CVE-style ids, not real CVEs)
# ---------------------------------------------------------------------------
_PRODUCTS = [
    "Apex Mail Gateway", "Corebridge VPN Appliance", "Ledgerline ERP Suite",
    "Fluxpoint File Server", "Northgate Firewall OS", "Amberdesk CRM Platform",
    "Ridgecast Web Server", "Talonhub Identity Provider", "Cascadeflow ETL Engine",
    "Wrenport Container Runtime", "Brightline Remote Desktop", "Havenlock Backup Suite",
]
_SEVERITIES = ["Critical", "High", "High", "Medium", "Medium", "Low"]
VULNERABILITIES = [
    (f"CVE-2023-{91000 + i}" if i % 2 == 0 else f"CVE-2024-{91000 + i}",
     RNG.choice(_SEVERITIES),
     RNG.choice(_PRODUCTS))
    for i in range(24)
]

# ---------------------------------------------------------------------------
# Technique (real MITRE ATT&CK entries - public taxonomy)
# ---------------------------------------------------------------------------
TECHNIQUES = [
    ("T1566", "Phishing", "Initial Access"),
    ("T1190", "Exploit Public-Facing Application", "Initial Access"),
    ("T1078", "Valid Accounts", "Defense Evasion"),
    ("T1059", "Command and Scripting Interpreter", "Execution"),
    ("T1053", "Scheduled Task/Job", "Execution"),
    ("T1547", "Boot or Logon Autostart Execution", "Persistence"),
    ("T1055", "Process Injection", "Defense Evasion"),
    ("T1003", "OS Credential Dumping", "Credential Access"),
    ("T1082", "System Information Discovery", "Discovery"),
    ("T1021", "Remote Services", "Lateral Movement"),
    ("T1560", "Archive Collected Data", "Collection"),
    ("T1071", "Application Layer Protocol", "Command and Control"),
    ("T1041", "Exfiltration Over C2 Channel", "Exfiltration"),
    ("T1486", "Data Encrypted for Impact", "Impact"),
    ("T1210", "Exploitation of Remote Services", "Lateral Movement"),
    ("T1204", "User Execution", "Execution"),
]

# ---------------------------------------------------------------------------
# Campaign
# ---------------------------------------------------------------------------
CAMPAIGNS = [
    ("Operation Coldharbor", 2023), ("Operation Brackenfall", 2024),
    ("Operation Longshadow", 2022), ("Operation Fernbridge", 2025),
    ("Operation Marlstone", 2023), ("Operation Duskferry", 2024),
    ("Operation Halfmoon", 2021), ("Operation Greywater", 2024),
    ("Operation Ashcroft", 2022), ("Operation Nightloom", 2025),
    ("Operation Redwick", 2023), ("Operation Palefire", 2024),
    ("Operation Ironbrook", 2022), ("Operation Softclay", 2025),
    ("Operation Blackferry", 2023), ("Operation Wrenfield", 2024),
]

# ---------------------------------------------------------------------------
# Organization
# ---------------------------------------------------------------------------
ORGANIZATIONS = [
    ("Meridian Capital Group", "Financial Services", "United States"),
    ("Northwell Regional Health", "Healthcare", "United States"),
    ("Solvane Energy Partners", "Energy", "United Kingdom"),
    ("Kestrel Manufacturing Co.", "Manufacturing", "Germany"),
    ("Bureau of Civic Records", "Government", "Canada"),
    ("Vantage Cloud Systems", "Technology", "United States"),
    ("Harborline Retail Group", "Retail", "Netherlands"),
    ("Continental Telecom", "Telecommunications", "France"),
    ("Ashgrove University", "Education", "United Kingdom"),
    ("Pacific Rail Authority", "Transportation", "Australia"),
    ("Lumen Broadcasting Network", "Media", "United States"),
    ("Aegis Defense Systems", "Defense", "United States"),
    ("Bellcrest Insurance Holdings", "Financial Services", "United States"),
    ("Thornfield Pharmaceuticals", "Healthcare", "Switzerland"),
    ("Ridgeline Power Cooperative", "Energy", "Canada"),
    ("Solworth Automotive", "Manufacturing", "Japan"),
    ("Municipal Water Authority", "Government", "United States"),
    ("Cirrusdata Technologies", "Technology", "Singapore"),
    ("Marketside Retail Holdings", "Retail", "United States"),
    ("Pinehaven School District", "Education", "United States"),
]

# ---------------------------------------------------------------------------
# Indicator (RFC 5737 / RFC 2606 reserved ranges - not real infrastructure)
# ---------------------------------------------------------------------------
_IOC_TYPES = ["ip", "domain", "sha256", "url"]
_CONFIDENCE = ["High", "High", "Medium", "Medium", "Low"]
_DOC_SUBNETS = ["198.51.100", "203.0.113", "192.0.2"]


def _fake_ip(i: int) -> str:
    subnet = _DOC_SUBNETS[i % len(_DOC_SUBNETS)]
    return f"{subnet}.{10 + (i % 240)}"


def _fake_domain(i: int) -> str:
    return f"update-svc-{i:03d}.example"


def _fake_sha256(i: int) -> str:
    return hashlib.sha256(f"threatgraph-seed-{i}".encode()).hexdigest()


def _fake_url(i: int) -> str:
    return f"https://cdn-relay-{i:03d}.example/assets/payload"


def _build_indicators(count: int) -> list[tuple[str, str, str]]:
    indicators = []
    for i in range(count):
        ioc_type = _IOC_TYPES[i % len(_IOC_TYPES)]
        value = {
            "ip": _fake_ip,
            "domain": _fake_domain,
            "sha256": _fake_sha256,
            "url": _fake_url,
        }[ioc_type](i)
        confidence = RNG.choice(_CONFIDENCE)
        indicators.append((ioc_type, value, confidence))
    return indicators


INDICATORS = _build_indicators(30)


# ---------------------------------------------------------------------------
# Description templates (kept short and generic - this is illustrative
# data, not a real intelligence report)
# ---------------------------------------------------------------------------
def actor_description(name: str, motivation: str) -> str:
    return f"{name} is a threat activity cluster tracked for operations consistent with {motivation.lower()} objectives."


def malware_description(name: str, mtype: str, platform: str) -> str:
    return f"{name} is a {mtype.lower()} family observed targeting {platform} environments."


def vulnerability_description(cve: str, product: str, severity: str) -> str:
    return f"{cve} is a {severity.lower()}-severity flaw affecting {product} that permits unauthorized access when unpatched."


def technique_description(name: str, tactic: str) -> str:
    return f"{name} is a MITRE ATT&CK technique associated with the {tactic} tactic."


def campaign_description(name: str, year: int) -> str:
    return f"{name} was an intrusion set first observed in {year}, tracked across multiple targeted sectors."
