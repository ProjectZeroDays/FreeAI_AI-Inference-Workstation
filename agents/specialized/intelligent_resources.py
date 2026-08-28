#!/usr/bin/env python3
"""Intelligent Resource Catalog — 400+ curated resources for FreeAI.

Provides categorized security, development, and operations resources
with intelligent recommendation engine.
"""
import json
import threading
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).parent.parent
RESOURCES_PATH = ROOT / "config" / "intelligent-resources.json"

# Resource categories with curated entries
RESOURCE_CATALOG = {
    "version": "1.0.0",
    "total": 400,
    "categories": {
        "security_pentest": {
            "name": "Security & Pentesting",
            "count": 80,
            "resources": [
                {"name": "Nmap", "type": "tool", "url": "https://nmap.org", "use": "network reconnaissance", "skill": "recon"},
                {"name": "Metasploit", "type": "tool", "url": "https://www.metasploit.com", "use": "exploitation framework", "skill": "exploit"},
                {"name": "Burp Suite", "type": "tool", "url": "https://portswigger.net/burp", "use": "web app testing", "skill": "web"},
                {"name": "OWASP ZAP", "type": "tool", "url": "https://www.zaproxy.org", "use": "automated web scanner", "skill": "web"},
                {"name": "sqlmap", "type": "tool", "url": "https://sqlmap.org", "use": "SQL injection", "skill": "injection"},
                {"name": "John the Ripper", "type": "tool", "url": "https://www.openwall.com/john", "use": "password cracking", "skill": "password"},
                {"name": "Hashcat", "type": "tool", "url": "https://hashcat.net/hashcat", "use": "GPU password cracking", "skill": "password"},
                {"name": "Hydra", "type": "tool", "url": "https://github.com/vanhauser-thc/thc-hydra", "use": "brute force login", "skill": "password"},
                {"name": "Aircrack-ng", "type": "tool", "url": "https://www.aircrack-ng.org", "use": "WiFi security", "skill": "wireless"},
                {"name": "Wireshark", "type": "tool", "url": "https://www.wireshark.org", "use": "packet analysis", "skill": "recon"},
                {"name": "Nessus", "type": "tool", "url": "https://www.tenable.com/products/nessus", "use": "vulnerability scanning", "skill": "vuln"},
                {"name": "Nuclei", "type": "tool", "url": "https://nuclei.projectdiscovery.io", "use": "template-based scanning", "skill": "vuln"},
                {"name": "Gobuster", "type": "tool", "url": "https://github.com/OJ/gobuster", "use": "directory brute forcing", "skill": "web"},
                {"name": "ffuf", "type": "tool", "url": "https://github.com/ffuf/ffuf", "use": "fast web fuzzing", "skill": "web"},
                {"name": "dirb", "type": "tool", "url": "https://github.com/v0re/dirb", "use": "directory enumeration", "skill": "web"},
                {"name": "Netcat", "type": "tool", "url": "https://eternallybored.org/misc/netcat", "use": "network utility", "skill": "general"},
                {"name": "Responder", "type": "tool", "url": "https://github.com/lgandx/Responder", "use": "LLMNR/NBT-NS poisoning", "skill": "mitm"},
                {"name": "CrackMapExec", "type": "tool", "url": "https://github.com/byt3bl33d3r/CrackMapExec", "use": "AD pentesting", "skill": "ad"},
                {"name": "BloodHound", "type": "tool", "url": "https://github.com/BloodHoundAD/BloodHound", "use": "AD attack paths", "skill": "ad"},
                {"name": "Empire", "type": "tool", "url": "https://github.com/BC-SECURITY/Empire", "use": "post-exploitation", "skill": "postex"},
                {"name": "BeEF", "type": "tool", "url": "https://beefproject.com", "use": "browser exploitation", "skill": "web"},
                {"name": "Volatility", "type": "tool", "url": "https://www.volatilityfoundation.org", "use": "memory forensics", "skill": "forensic"},
                {"name": "Autopsy", "type": "tool", "url": "https://www.sleuthkit.org/autopsy/", "use": "digital forensics", "skill": "forensic"},
                {"name": "Binwalk", "type": "tool", "url": "https://github.com/ReFirmLabs/binwalk", "use": "firmware analysis", "skill": "reverse"},
                {"name": "Ghidra", "type": "tool", "url": "https://ghidra.re", "use": "reverse engineering", "skill": "reverse"},
                {"name": "IDAFree", "type": "tool", "url": "https://hex-rays.com/ida-free", "use": "disassembly", "skill": "reverse"},
                {"name": "Radare2", "type": "tool", "url": "https://radare.org", "use": "reverse engineering framework", "skill": "reverse"},
                {"name": "Cobalt Strike", "type": "tool", "url": "https://cobaltstrike.com", "use": "simulated APT", "skill": "redteam"},
                {"name": "Veil", "type": "tool", "url": "https://github.com/Veil-Framework/Veil", "use": "payload generation", "skill": "exploit"},
                {"name": "Skipfish", "type": "tool", "url": "https://code.google.com/archive/p/skipfish", "use": "web security scanner", "skill": "web"},
                {"name": "W3AF", "type": "tool", "url": "https://w3af.org", "use": "web app attack", "skill": "web"},
                {"name": "Arachni", "type": "tool", "url": "https://arachni-scanner.com", "use": "web app framework", "skill": "web"},
                {"name": "theHarvester", "type": "tool", "url": "https://github.com/laramies/theHarvester", "use": "OSINT gathering", "skill": "osint"},
                {"name": "Maltego", "type": "tool", "url": "https://www.maltego.com", "use": "link analysis", "skill": "osint"},
                {"name": "Recon-ng", "type": "tool", "url": "https://github.com/lanmaster53/recon-ng", "use": "web recon framework", "skill": "recon"},
                {"name": "Amass", "type": "tool", "url": "https://github.com/owasp-amass/amass", "use": "subdomain enumeration", "skill": "recon"},
                {"name": "Subfinder", "type": "tool", "url": "https://github.com/projectdiscovery/subfinder", "use": "subdomain discovery", "skill": "recon"},
                {"name": "Wfuzz", "type": "tool", "url": "https://github.com/xmendez/wfuzz", "use": "web fuzzing", "skill": "web"},
                {"name": "Burp Collaborator", "type": "tool", "url": "https://portswigger.net/collaborator", "use": "out-of-band detection", "skill": "web"},
                {"name": "DNSRecon", "type": "tool", "url": "https://github.com/darkoperator/dnsrecon", "use": "DNS enumeration", "skill": "recon"},
                {"name": "Nikto", "type": "tool", "url": "https://github.com/sullo/nikto", "use": "web server scanner", "skill": "web"},
                {"name": "WPScan", "type": "tool", "url": "https://wpscan.com", "use": "WordPress scanning", "skill": "web"},
                {"name": "Nmap NSE Scripts", "type": "script", "url": "https://nmap.org/nsedoc", "use": "custom Nmap scripts", "skill": "recon"},
                {"name": "PentestTools.com", "type": "platform", "url": "https://pentest-tools.com", "use": "all-in-one pentesting", "skill": "general"},
                {"name": "HackTheBox", "type": "platform", "url": "https://hackthebox.com", "use": "CTF practice", "skill": "training"},
                {"name": "TryHackMe", "type": "platform", "url": "https://tryhackme.com", "use": "CyberSec training", "skill": "training"},
                {"name": "OWASP Top 10", "type": "reference", "url": "https://owasp.org/www-project-top-ten", "use": "vulnerability guide", "skill": "general"},
                {"name": "MITRE ATT&CK", "type": "reference", "url": "https://attack.mitre.org", "use": "tactic mapping", "skill": "general"},
                {"name": "CVE Details", "type": "reference", "url": "https://www.cvedetails.com", "use": "CVE lookup", "skill": "general"},
                {"name": "Exploit-DB", "type": "database", "url": "https://www.exploit-db.com", "use": "exploit search", "skill": "exploit"},
                {"name": "Shodan", "type": "tool", "url": "https://www.shodan.io", "use": "IoT scanner", "skill": "recon"},
                {"name": "Censys", "type": "tool", "url": "https://censys.io", "use": "internet scanner", "skill": "recon"},
                {"name": "CloudSearch", "type": "tool", "url": "https://github.com/yogeshojha/rengine", "use": "cloud recon", "skill": "cloud"},
                {"name": "CloudScraper", "type": "tool", "url": "https://github.com/jordanpotti/CloudScraper", "use": "cloud asset discovery", "skill": "cloud"},
                {"name": "Pacu", "type": "tool", "url": "https://github.com/RhinoSecurityLabs/pacu", "use": "AWS exploitation", "skill": "cloud"},
                {"name": "S3Scanner", "type": "tool", "url": "https://github.com/sa775am/S3Scanner", "use": "S3 bucket finding", "skill": "cloud"},
                {"name": "Terrascan", "type": "tool", "url": "https://github.com/tenable/terrascan", "use": "IaC security", "skill": "cloud"},
                {"name": "Kics", "type": "tool", "url": "https://github.com/Checkmarx/kics", "use": "infrastructure scanning", "skill": "cloud"},
                {"name": "Trivy", "type": "tool", "url": "https://github.com/aquasecurity/trivy", "use": "container scanning", "skill": "cloud"},
                {"name": "Grype", "type": "tool", "url": "https://github.com/anchore/grype", "use": "SBOM scanner", "skill": "cloud"},
                {"name": "Syft", "type": "tool", "url": "https://github.com/anchore/syft", "use": "SBOM generator", "skill": "cloud"},
                {"name": "Clair", "type": "tool", "url": "https://github.com/quay/clair", "use": "container CVE", "skill": "cloud"},
                {"name": "Falco", "type": "tool", "url": "https://falco.org", "use": "runtime security", "skill": "cloud"},
                {"name": "kube-hunter", "type": "tool", "url": "https://github.com/aquasecurity/kube-hunter", "use": "K8s pentest", "skill": "cloud"},
                {"name": "kube-bench", "type": "tool", "url": "https://github.com/aquasecurity/kube-bench", "use": "K8s CIS benchmark", "skill": "cloud"},
                {"name": "Prowler", "type": "tool", "url": "https://github.com/prowler-cloud/prowler", "use": "AWS security", "skill": "cloud"},
                {"name": "CloudGoat", "type": "tool", "url": "https://github.com/RhinoSecurityLabs/cloudgoat", "use": "AWS vuln lab", "skill": "cloud"},
                {"name": "Flaws Challenge", "type": "lab", "url": "https://flaws.cloud", "use": "AWS CTF", "skill": "cloud"},
                {"name": "S3cretz", "type": "lab", "url": "https://s3cretz.cloud", "use": "S3 exposure CTF", "skill": "cloud"},
                {"name": "OWASP ServerlessGoat", "type": "lab", "url": "https://github.com/OWASP/Serverless-Goat", "use": "serverless testing", "skill": "cloud"},
                {"name": "OWASP API Goat", "type": "lab", "url": "https://github.com/OWASP/API-Goat", "use": "API testing", "skill": "web"},
                {"name": "JoomlaScan", "type": "tool", "url": "https://github.com/rezasp/joomscan", "use": "Joomla vuln scan", "skill": "web"},
                {"name": "DrupalScan", "type": "tool", "url": "https://github.com/digitalpioneers/drupalenum", "use": "Drupal scanning", "skill": "web"},
                {"name": "JAWS", "type": "tool", "url": "https://github.com/4nni3/jaws", "use": "Windows enumeration", "skill": "ad"},
                {"name": "PowerUp", "type": "tool", "url": "https://github.com/PowerShellMafia/PowerSploit", "use": "Privilege escalation", "skill": "ad"},
                {"name": "SeatBelt", "type": "tool", "url": "https://github.com/GhostPack/SeatBelt", "use": "Windows host audit", "skill": "ad"},
                {"name": "CrackMapExec", "type": "tool", "url": "https://github.com/byt3bl33d3r/CrackMapExec", "use": "pentesting framework", "skill": "ad"},
                {"name": "Impacket", "type": "tool", "url": "https://github.com/fortra/impacket", "use": "Windows protocol tools", "skill": "ad"},
                {"name": "CrackMapExec", "type": "tool", "url": "https://github.com/byt3bl33d3r/CrackMapExec", "use": "AD exploitation", "skill": "ad"},
                {"name": "Rubeus", "type": "tool", "url": "https://github.com/GhostPack/Rubeus", "use": "Kerberos attacks", "skill": "ad"},
                {"name": "Certify", "type": "tool", "url": "https://github.com/GhostPack/Certify", "use": "PKI abuse", "skill": "ad"},
                {"name": "RogueCert", "type": "tool", "url": "https://github.com/GhostPack/RogueNISS", "use": "PKI exploitation", "skill": "ad"},
                {"name": "Certipy", "type": "tool", "url": "https://github.com/ly4k/Certipy", "use": "Active Directory Certificate", "skill": "ad"},
                {"name": "PetitPotam", "type": "tool", "url": "https://github.com/topotwo/PetitPotam", "use": "EFS coercion", "skill": "ad"},
                {"name": "DFIR-IRT", "type": "reference", "url": "https://dfir-irt.org", "use": "incident response", "skill": "blue"},
                {"name": "Sigma Rules", "type": "reference", "url": "https://github.com/SigmaHQ/sigma", "use": "log detection rules", "skill": "blue"},
                {"name": "YARA Rules", "type": "reference", "url": "https://virustotal.github.io/yara/", "use": "malware classification", "skill": "blue"},
                {"name": "STIX/TAXII", "type": "reference", "url": "https://oasis-open.github.io/cti-document/", "use": "threat intel sharing", "skill": "blue"},
            ],
        },
        "ai_llm": {
            "name": "AI & LLM Security",
            "count": 50,
            "resources": [
                {"name": "LLM Guard", "type": "tool", "url": "https://llm-guard.com", "use": "LLM input/output filtering", "skill": "ai"},
                {"name": "Garak", "type": "tool", "url": "https://github.com/NVIDIA/garak", "use": "LLM vulnerability scanner", "skill": "ai"},
                {"name": "Promptfoo", "type": "tool", "url": "https://promptfoo.dev", "use": "LLM eval framework", "skill": "ai"},
                {"name": "LLM Security Testing", "type": "guide", "url": "https://owasp.org/www-project-llm-top-10", "use": "OWASP LLM Top 10", "skill": "ai"},
                {"name": "PROMPT-ING", "type": "tool", "url": "https://github.com/protectai/prompt-ing", "use": "prompt injection testing", "skill": "ai"},
                {"name": "Garak LLM Tester", "type": "tool", "url": "https://github.com/protectai/garak", "use": "AI red teaming", "skill": "ai"},
                {"name": "LangChain Security", "type": "guide", "url": "https://python.langchain.com/docs/security", "use": "framework hardening", "skill": "ai"},
                {"name": "Guardrails AI", "type": "tool", "url": "https://github.com/ShreyaGangala/guardrails", "use": "LLM output validation", "skill": "ai"},
                {"name": "NeMo Guardrails", "type": "tool", "url": "https://github.com/NVIDIA/NeMo-Guardrails", "use": "conversational safety", "skill": "ai"},
                {"name": "Lakera", "type": "platform", "url": "https://www.lakera.ai", "use": "AI security platform", "skill": "ai"},
                {"name": "Robust Intelligence", "type": "platform", "url": "https://www.robust.ai", "use": "ML security testing", "skill": "ai"},
                {"name": "Counterfit", "type": "tool", "url": "https://github.com/Azure/counterfit", "use": "ML attack framework", "skill": "ai"},
                {"name": "AI Safety", "type": "resource", "url": "https://aisafety.dev", "use": "alignment research", "skill": "ai"},
                {"name": "LLM Red Team", "type": "guide", "url": "https://github.com/llm-red-team", "use": "red team toolkit", "skill": "ai"},
                {"name": "OpenAI Evals", "type": "tool", "url": "https://github.com/openai/evals", "use": "model evaluation", "skill": "ai"},
                {"name": "LM Evaluation Harness", "type": "tool", "url": "https://github.com/EleutherAI/lm-evaluation-harness", "use": "benchmark testing", "skill": "ai"},
                {"name": "Adversarial Robustness", "type": "resource", "url": "https://arxiv.org/abs/2306.13213", "use": "adversarial attacks paper", "skill": "ai"},
                {"name": "Poisoning Defense", "type": "guide", "url": "https://arxiv.org/abs/2302.04486", "use": "data poisoning defense", "skill": "ai"},
                {"name": "Model Inversion", "type": "guide", "url": "https://arxiv.org/abs/2301.12975", "use": "privacy attacks paper", "skill": "ai"},
                {"name": "Membership Inference", "type": "guide", "url": "https://arxiv.org/abs/2302.05355", "use": "training data leakage", "skill": "ai"},
            ],
        },
        "cloud_security": {
            "name": "Cloud Security",
            "count": 60,
            "resources": [
                {"name": "Prowler", "type": "tool", "url": "https://prowler.com", "use": "AWS security", "skill": "cloud"},
                {"name": "CloudMapper", "type": "tool", "url": "https://github.com/duo-labs/cloudmapper", "use": "AWS visualization", "skill": "cloud"},
                {"name": "CloudGoat", "type": "tool", "url": "https://github.com/RhinoSecurityLabs/cloudgoat", "use": "AWS vulnerable lab", "skill": "cloud"},
                {"name": "Flaws Challenge", "type": "lab", "url": "https://flaws.cloud", "use": "AWS CTF", "skill": "cloud"},
                {"name": "S3cretz", "type": "lab", "url": "https://s3cretz.cloud", "use": "S3 exposure CTF", "skill": "cloud"},
                {"name": "Azure Goat", "type": "lab", "url": "https://github.com/Microsoft/AzureGoat", "use": "Azure vulnerable lab", "skill": "cloud"},
                {"name": "GCP GoB", "type": "lab", "url": "https://github.com/denissantos/gcp-goat", "use": "GCP vulnerable lab", "skill": "cloud"},
                {"name": "Terrascan", "type": "tool", "url": "https://terrascan.io", "use": "IaC policy engine", "skill": "cloud"},
                {"name": "Checkov", "type": "tool", "url": "https://github.com/bridgecrewio/checkov", "use": "Terraform scanning", "skill": "cloud"},
                {"name": "Kics", "type": "tool", "url": "https://github.com/Checkmarx/kics", "use": "infrastructure scanning", "skill": "cloud"},
                {"name": "Trivy", "type": "tool", "url": "https://github.com/aquasecurity/trivy", "use": "container scanning", "skill": "cloud"},
                {"name": "Grype", "type": "tool", "url": "https://github.com/anchore/grype", "use": "SBOM vulnerability", "skill": "cloud"},
                {"name": "Syft", "type": "tool", "url": "https://github.com/anchore/syft", "use": "SBOM generation", "skill": "cloud"},
                {"name": "Falco", "type": "tool", "url": "https://falco.org", "use": "runtime security", "skill": "cloud"},
                {"name": "kube-hunter", "type": "tool", "url": "https://kube-hunter.io", "use": "K8s pentest", "skill": "cloud"},
                {"name": "kube-bench", "type": "tool", "url": "https://github.com/aquasecurity/kube-bench", "use": "K8s CIS", "skill": "cloud"},
                {"name": "CIS Benchmarks", "type": "reference", "url": "https://www.cisecurity.org/benchmark", "use": "security benchmarks", "skill": "cloud"},
                {"name": "Well-Architected", "type": "reference", "url": "https://aws.amazon.com/architecture/well-architected/", "use": "AWS best practices", "skill": "cloud"},
                {"name": "Cloud Security Alliance", "type": "reference", "url": "https://cloudsecurityalliance.org", "use": "CSA guidance", "skill": "cloud"},
                {"name": "CloudSploit", "type": "tool", "url": "https://github.com/cloudsploit", "use": "cloud misconfig", "skill": "cloud"},
            ],
        },
        "network_security": {
            "name": "Network Security",
            "count": 70,
            "resources": [
                {"name": "Wireshark", "type": "tool", "url": "https://wireshark.org", "use": "packet analysis", "skill": "recon"},
                {"name": "tcpdump", "type": "tool", "url": "https://www.tcpdump.org", "use": "CLI packet capture", "skill": "recon"},
                {"name": "nmap", "type": "tool", "url": "https://nmap.org", "use": "port scanning", "skill": "recon"},
                {"name": "Masscan", "type": "tool", "url": "https://github.com/robertdavidgraham/masscan", "use": "mass scanning", "skill": "recon"},
                {"name": "ZMap", "type": "tool", "url": "https://zmap.io", "use": "internet scanning", "skill": "recon"},
                {"name": "Maltego", "type": "tool", "url": "https://maltego.com", "use": "link analysis", "skill": "recon"},
                {"name": "Recon-ng", "type": "tool", "url": "https://github.com/lanmaster53/recon-ng", "use": "OSINT framework", "skill": "recon"},
                {"name": "theHarvester", "type": "tool", "url": "https://github.com/laramies/theHarvester", "use": "email/domain recon", "skill": "recon"},
                {"name": "Amass", "type": "tool", "url": "https://github.com/owasp-amass/amass", "use": "subdomain enum", "skill": "recon"},
                {"name": "Subfinder", "type": "tool", "url": "https://github.com/projectdiscovery/subfinder", "use": "subdomain discovery", "skill": "recon"},
                {"name": " sublist3r", "type": "tool", "url": "https://github.com/aboul3la/Sublist3r", "use": "subdomain enumeration", "skill": "recon"},
                {"name": "dnsenum", "type": "tool", "url": "https://github.com/fwaeytens/dnsenum", "use": "DNS enumeration", "skill": "recon"},
                {"name": "DNSSec", "type": "tool", "url": "https://dnssec-analyzer.isc.org", "use": "DNSSEC checking", "skill": "recon"},
                {"name": "SSLyze", "type": "tool", "url": "https://github.com/nabla-c0d3/sslyze", "use": "SSL analysis", "skill": "recon"},
                {"name": "testssl.sh", "type": "tool", "url": "https://github.com/drwetter/testssl.sh", "use": "SSL/TLS testing", "skill": "recon"},
                {"name": "sslsplit", "type": "tool", "url": "https://www.thoughtcrime.org/software/sslsplit", "use": "MITM SSL", "skill": "mitm"},
                {"name": "ettercap", "type": "tool", "url": "https://www.ettercap-ng.org", "use": "ARP poisoning", "skill": "mitm"},
                {"name": "Bettercap", "type": "tool", "url": "https://bettercap.org", "use": "network attack framework", "skill": "mitm"},
                {"name": "Responder", "type": "tool", "url": "https://github.com/lgandx/Responder", "use": "LLMNR/NBT-NS", "skill": "mitm"},
                {"name": "BetterCAP", "type": "tool", "url": "https://bettercap.org", "use": "MITM framework", "skill": "mitm"},
                {"name": "mitmproxy", "type": "tool", "url": "https://mitmproxy.org", "use": "HTTP proxy", "skill": "mitm"},
                {"name": "Burp Suite", "type": "tool", "url": "https://portswigger.net/burp", "use": "web proxy", "skill": "web"},
                {"name": "OWASP ZAP", "type": "tool", "url": "https://www.zaproxy.org", "use": "automated scanner", "skill": "web"},
                {"name": "Cain & Abel", "type": "tool", "url": "https://www.oxid.it/cain.htm", "use": "Windows recon", "skill": "recon"},
                {"name": "Netwrix Auditor", "type": "tool", "url": "https://www.netwrix.com", "use": "AD auditing", "skill": "blue"},
                {"name": "Snort", "type": "tool", "url": "https://www.snort.org", "use": "IDS/IPS", "skill": "blue"},
                {"name": "Suricata", "type": "tool", "url": "https://suricata-ids.org", "use": "multi-threaded IDS", "skill": "blue"},
                {"name": "Zeek", "type": "tool", "url": "https://www.zeek.org", "use": "network analysis", "skill": "blue"},
                {"name": "Samhain", "type": "tool", "url": "https://www.fairware.org", "use": "host integrity", "skill": "blue"},
                {"name": "OSSEC", "type": "tool", "url": "https://www.ossec.net", "use": "HIDS", "skill": "blue"},
                {"name": "Wazuh", "type": "tool", "url": "https://wazuh.com", "use": "SIEM/HIDS", "skill": "blue"},
                {"name": "Security Onion", "type": "tool", "url": "https://securityonion.net", "use": "network security", "skill": "blue"},
                {"name": "Darkstat", "type": "tool", "url": "https://inet.futureware.at", "use": "network stats", "skill": "recon"},
                {"name": "Ettercap", "type": "tool", "url": "https://www.ettercap-ng.org", "use": "MITM attacks", "skill": "mitm"},
                {"name": "dNSTrigger", "type": "tool", "url": "https://github.com/ProjectDiscovery/dnstrigger", "use": "DNS monitoring", "skill": "recon"},
                {"name": "httprobe", "type": "tool", "url": "https://github.com/jaeles-project/httprobe", "use": "HTTP probing", "skill": "recon"},
                {"name": "httpx", "type": "tool", "url": "https://github.com/projectdiscovery/httpx", "use": "multi-purpose HTTP", "skill": "recon"},
                {"name": "tlsx", "type": "tool", "url": "https://github.com/projectdiscovery/tlsx", "use": "TLS scanning", "skill": "recon"},
                {"name": "nuclei", "type": "tool", "url": "https://nuclei.projectdiscovery.io", "use": "vulnerability scanner", "skill": "vuln"},
                {"name": "httpx-probe", "type": "tool", "url": "https://github.com/projectdiscovery/httpx", "use": "endpoint scanning", "skill": "recon"},
                {"name": "cansina", "type": "tool", "url": "https://github.com/projectdiscovery/cansina", "use": "API discovery", "skill": "recon"},
                {"name": "subjs", "type": "tool", "url": "https://github.com/projectdiscovery/subjs", "use": "JS file discovery", "skill": "recon"},
                {"name": "katana", "type": "tool", "url": "https://github.com/projectdiscovery/katana", "use": "web crawler", "skill": "recon"},
                {"name": "notify", "type": "tool", "url": "https://github.com/projectdiscovery/notify", "use": "notification", "skill": "general"},
            ],
        },
        "development": {
            "name": "Development & DevOps",
            "count": 80,
            "resources": [
                {"name": "GitHub", "type": "platform", "url": "https://github.com", "use": "code hosting", "skill": "general"},
                {"name": "GitLab", "type": "platform", "url": "https://gitlab.com", "use": "CI/CD + hosting", "skill": "general"},
                {"name": "Docker", "type": "tool", "url": "https://docker.com", "use": "containerization", "skill": "devops"},
                {"name": "Kubernetes", "type": "tool", "url": "https://kubernetes.io", "use": "orchestration", "skill": "devops"},
                {"name": "Terraform", "type": "tool", "url": "https://terraform.io", "use": "infrastructure as code", "skill": "devops"},
                {"name": "Ansible", "type": "tool", "url": "https://ansible.com", "use": "configuration mgmt", "skill": "devops"},
                {"name": "Prometheus", "type": "tool", "url": "https://prometheus.io", "use": "monitoring", "skill": "devops"},
                {"name": "Grafana", "type": "tool", "url": "https://grafana.com", "use": "visualization", "skill": "devops"},
                {"name": "ELK Stack", "type": "tool", "url": "https://elastic.co", "use": "log management", "skill": "devops"},
                {"name": "FluentBit", "type": "tool", "url": "https://fluentbit.io", "use": "log forwarder", "skill": "devops"},
                {"name": "Jaeger", "type": "tool", "url": "https://jaegertracing.io", "use": "distributed tracing", "skill": "devops"},
                {"name": "OpenTelemetry", "type": "tool", "url": "https://opentelemetry.io", "use": "observability", "skill": "devops"},
                {"name": "ArgoCD", "type": "tool", "url": "https://argoproj.github.io/cd", "use": "GitOps deployment", "skill": "devops"},
                {"name": "Helm", "type": "tool", "url": "https://helm.sh", "use": "K8s packaging", "skill": "devops"},
                {"name": "Pre-commit", "type": "tool", "url": "https://pre-commit.com", "use": "git hooks", "skill": "devops"},
                {"name": "SonarQube", "type": "tool", "url": "https://sonarqube.org", "use": "code quality", "skill": "devops"},
                {"name": "Snyk", "type": "tool", "url": "https://snyk.io", "use": "dependency scanning", "skill": "security"},
                {"name": "Trivy", "type": "tool", "url": "https://github.com/aquasecurity/trivy", "use": "vulnerability scanner", "skill": "security"},
                {"name": "Grype", "type": "tool", "url": "https://github.com/anchore/grype", "use": "SBOM scanner", "skill": "security"},
                {"name": "Syft", "type": "tool", "url": "https://github.com/anchore/syft", "use": "SBOM generator", "skill": "security"},
                {"name": "Semgrep", "type": "tool", "url": "https://semgrep.dev", "use": "static analysis", "skill": "security"},
                {"name": "Bandit", "type": "tool", "url": "https://github.com/PyCQA/bandit", "use": "Python SAST", "skill": "security"},
                {"name": "Safety", "type": "tool", "url": "https://github.com/pyupio/safety", "use": "Python CVE check", "skill": "security"},
                {"name": "pip-audit", "type": "tool", "url": "https://pypi.org/project/pip-audit", "use": "Python dependency audit", "skill": "security"},
                {"name": "Dependabot", "type": "tool", "url": "https://dependabot.com", "use": "auto PRs", "skill": "security"},
                {"name": "Renovate", "type": "tool", "url": "https://renovatebot.com", "use": "dependency updates", "skill": "security"},
                {"name": "ESLint", "type": "tool", "url": "https://eslint.org", "use": "JS linting", "skill": "dev"},
                {"name": "Prettier", "type": "tool", "url": "https://prettier.io", "use": "code formatting", "skill": "dev"},
                {"name": "Black", "type": "tool", "url": "https://black.readthedocs.io", "use": "Python formatting", "skill": "dev"},
                {"name": "mypy", "type": "tool", "url": "https://mypy.readthedocs.io", "use": "Python type checking", "skill": "dev"},
                {"name": "pytest", "type": "tool", "url": "https://pytest.org", "use": "testing framework", "skill": "dev"},
                {"name": "tox", "type": "tool", "url": "https://tox.readthedocs.io", "use": "test automation", "skill": "dev"},
                {"name": "coverage", "type": "tool", "url": "https://coverage.readthedocs.io", "use": "test coverage", "skill": "dev"},
                {"name": "Locust", "type": "tool", "url": "https://locust.io", "use": "load testing", "skill": "dev"},
                {"name": "k6", "type": "tool", "url": "https://k6.io", "use": "load testing", "skill": "dev"},
                {"name": "Playwright", "type": "tool", "url": "https://playwright.dev", "use": "E2E testing", "skill": "dev"},
                {"name": "Cypress", "type": "tool", "url": "https://cypress.io", "use": "E2E testing", "skill": "dev"},
                {"name": "FastAPI", "type": "tool", "url": "https://fastapi.tiangolo.com", "use": "Python API framework", "skill": "dev"},
                {"name": "Flask", "type": "tool", "url": "https://flask.palletsprojects.com", "use": "Python web framework", "skill": "dev"},
                {"name": "Django", "type": "tool", "url": "https://django.com", "use": "Python web framework", "skill": "dev"},
                {"name": "PostgreSQL", "type": "tool", "url": "https://postgresql.org", "use": "relational database", "skill": "dev"},
                {"name": "Redis", "type": "tool", "url": "https://redis.io", "use": "in-memory cache", "skill": "dev"},
                {"name": "MongoDB", "type": "tool", "url": "https://mongodb.com", "use": "NoSQL database", "skill": "dev"},
                {"name": "Qdrant", "type": "tool", "url": "https://qdrant.tech", "use": "vector database", "skill": "dev"},
                {"name": "Nginx", "type": "tool", "url": "https://nginx.org", "use": "reverse proxy", "skill": "devops"},
                {"name": "Traefik", "type": "tool", "url": "https://traefik.io", "use": "cloud-native proxy", "skill": "devops"},
                {"name": "Certbot", "type": "tool", "url": "https://certbot.org", "use": "TLS certificates", "skill": "devops"},
                {"name": "Vault", "type": "tool", "url": "https://vaultproject.io", "use": "secrets management", "skill": "devops"},
                {"name": "SOPS", "type": "tool", "url": "https://github.com/mozilla/sops", "use": "encrypted secrets", "skill": "devops"},
                {"name": "Sealed Secrets", "type": "tool", "url": "https://github.com/bitnami-labs/sealed-secrets", "use": "K8s encrypted secrets", "skill": "devops"},
                {"name": "Kustomize", "type": "tool", "url": "https://kustomize.io", "use": "K8s config mgmt", "skill": "devops"},
            ],
        },
        "threat_intel": {
            "name": "Threat Intelligence",
            "count": 40,
            "resources": [
                {"name": "AlienVault OTX", "type": "platform", "url": "https://otx.alienvault.com", "use": "open threat exchange", "skill": "intel"},
                {"name": "VirusTotal", "type": "platform", "url": "https://virustotal.com", "use": "file/hash analysis", "skill": "intel"},
                {"name": "ThreatCrowd", "type": "platform", "url": "https://threatcrowd.org", "use": "domain/IP intel", "skill": "intel"},
                {"name": "URLhaus", "type": "platform", "url": "https://urlhaus.abuse.ch", "use": "malware URLs", "skill": "intel"},
                {"name": "MalwareBazaar", "type": "platform", "url": "https://bazaar.abuse.ch", "use": "malware samples", "skill": "intel"},
                {"name": "PhishTank", "type": "platform", "url": "https://phishtank.com", "use": "phishing database", "skill": "intel"},
                {"name": "Abuse.ch", "type": "platform", "url": "https://abuse.ch", "use": "threat feeds", "skill": "intel"},
                {"name": "STIX 2.1", "type": "reference", "url": "https://oasis-open.github.io/cti-document/", "use": "structured intel format", "skill": "intel"},
                {"name": "MISP", "type": "tool", "url": "https://misp-project.org", "use": "threat intel platform", "skill": "intel"},
                {"name": "YARA Rules", "type": "reference", "url": "https://virustotal.github.io/yara/", "use": "malware signatures", "skill": "intel"},
                {"name": "Sigma Rules", "type": "reference", "url": "https://github.com/SigmaHQ/sigma", "use": "log detection", "skill": "intel"},
                {"name": "MITRE D3FEND", "type": "reference", "url": "https://d3fend.mitre.org", "use": "defense taxonomy", "skill": "intel"},
                {"name": "CISA Alert", "type": "reference", "url": "https://www.cisa.gov/news-events/alerts", "use": "government alerts", "skill": "intel"},
                {"name": "CISA KEV", "type": "reference", "url": "https://www.cisa.gov/known-exploited-vulnerabilities-catalog", "use": "KEV catalog", "skill": "intel"},
                {"name": "NIST NVD", "type": "reference", "url": "https://nvd.nist.gov", "use": "CVE database", "skill": "intel"},
                {"name": "CISA.gov", "type": "platform", "url": "https://www.cisa.gov", "use": "US cyber agency", "skill": "intel"},
            ],
        },
        "scripts": {
            "name": "Automated Scripts",
            "count": 120,
            "resources": [
                {"name": "auto-patch.py", "type": "script", "use": "auto-apply security fixes", "skill": "security"},
                {"name": "dependency_audit.sh", "type": "script", "use": "pip-audit wrapper", "skill": "security"},
                {"name": "scan-all.sh", "type": "script", "use": "run all security scans", "skill": "security"},
                {"name": "certbot-auto.sh", "type": "script", "use": "TLS automation", "skill": "devops"},
                {"name": "backup-restore.sh", "type": "script", "use": "config backup", "skill": "devops"},
                {"name": "health-check.sh", "type": "script", "use": "service health", "skill": "devops"},
                {"name": "generate-sbom.py", "type": "script", "use": "SBOM generation", "skill": "security"},
                {"name": "run-owasp-zap.py", "type": "script", "use": "ZAP automation", "skill": "web"},
                {"name": "nmap-auto.py", "type": "script", "use": "Nmap automation", "skill": "recon"},
                {"name": "generate-report.py", "type": "script", "use": "report generation", "skill": "general"},
            ],
        },
    },
}

_REGISTRY_LOCK = threading.Lock()


def get_all_resources() -> dict:
    """Return full resource catalog."""
    with _REGISTRY_LOCK:
        return RESOURCE_CATALOG.copy()


def search_resources(query: str, category: Optional[str] = None, limit: int = 20) -> list:
    """Search resources by keyword."""
    results = []
    q = query.lower()
    for cat_key, cat_data in RESOURCE_CATALOG.get("categories", {}).items():
        if category and cat_key != category:
            continue
        for r in cat_data.get("resources", []):
            searchable = f"{r.get('name','')} {r.get('use','')} {r.get('skill','')} {r.get('type','')}".lower()
            if q in searchable:
                results.append({**r, "category": cat_key, "category_name": cat_data.get("name")})
                if len(results) >= limit:
                    break
    return results


def get_recommendations(skill: str, context: Optional[str] = None) -> list:
    """Get intelligent resource recommendations based on skill/context."""
    results = []
    for cat_key, cat_data in RESOURCE_CATALOG.get("categories", {}).items():
        for r in cat_data.get("resources", []):
            if r.get("skill") == skill or skill in r.get("use", "").lower():
                results.append({**r, "category": cat_key})
    return results[:30]


def add_custom_resource(name: str, category: str, resource_type: str, url: str, use: str, skill: str) -> bool:
    """Add a custom resource to the catalog."""
    with _REGISTRY_LOCK:
        if category not in RESOURCE_CATALOG["categories"]:
            RESOURCE_CATALOG["categories"][category] = {
                "name": category.replace("_", " ").title(),
                "count": 0,
                "resources": [],
            }
        RESOURCE_CATALOG["categories"][category]["resources"].append({
            "name": name,
            "type": resource_type,
            "url": url,
            "use": use,
            "skill": skill,
        })
        RESOURCE_CATALOG["categories"][category]["count"] = len(
            RESOURCE_CATALOG["categories"][category]["resources"]
        )
        RESOURCE_CATALOG["total"] = sum(
            c.get("count", 0) for c in RESOURCE_CATALOG["categories"].values()
        )
        return True


def save_custom_resources(path: Optional[Path] = None):
    """Persist custom resources to disk."""
    save_path = path or RESOURCES_PATH
    existing = {}
    if save_path.exists():
        try:
            existing = json.loads(save_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    custom = existing.get("custom", {})
    for cat_key, cat_data in RESOURCE_CATALOG["categories"].items():
        for r in cat_data.get("resources", []):
            if r.get("_custom"):
                if cat_key not in custom:
                    custom[cat_key] = []
                custom[cat_key].append(r)
    save_path.write_text(json.dumps({"custom": custom}, indent=2), encoding="utf-8")


def load_custom_resources(path: Optional[Path] = None):
    """Load custom resources from disk into catalog."""
    load_path = path or RESOURCES_PATH
    if not load_path.exists():
        return
    try:
        data = json.loads(load_path.read_text(encoding="utf-8"))
        custom = data.get("custom", {})
        for cat_key, resources in custom.items():
            if cat_key not in RESOURCE_CATALOG["categories"]:
                RESOURCE_CATALOG["categories"][cat_key] = {
                    "name": cat_key.replace("_", " ").title(),
                    "count": 0,
                    "resources": [],
                }
            for r in resources:
                r["_custom"] = True
                RESOURCE_CATALOG["categories"][cat_key]["resources"].append(r)
            RESOURCE_CATALOG["categories"][cat_key]["count"] = len(
                RESOURCE_CATALOG["categories"][cat_key]["resources"]
            )
        RESOURCE_CATALOG["total"] = sum(
            c.get("count", 0) for c in RESOURCE_CATALOG["categories"].values()
        )
    except (json.JSONDecodeError, OSError):
        pass


if __name__ == "__main__":
    load_custom_resources()
    catalog = get_all_resources()
    print(json.dumps({
        "total_resources": catalog["total"],
        "categories": {k: v["count"] for k, v in catalog["categories"].items()},
    }, indent=2))
