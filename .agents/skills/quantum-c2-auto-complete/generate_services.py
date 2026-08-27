"""Generate all 30 service and router files for Quantum C2 integration."""
import os
import re

BASE = r"C:\Projects\Quantum C2\backend\app"
SERVICES_DIR = os.path.join(BASE, "services")
ROUTERS_DIR = os.path.join(BASE, "routers")

TOOLS = [
    {"name": "openpgpjs", "service_class": "OpenPgpjsService", "get_func": "get_openpgpjs_service", "prefix": "/api/crypto/pgp", "tag": "PGP Encryption",
     "routes": [("POST","/encrypt","encrypt","Encrypt data with PGP"),("POST","/decrypt","decrypt","Decrypt PGP encrypted data"),("POST","/sign","sign","Create PGP digital signature"),("POST","/verify","verify","Verify PGP signature"),("POST","/generate-key","generate_key","Generate PGP key pair"),("GET","/keys","list_keys","List PGP keys")],
     "features": "PGP encryption/decryption, digital signatures, key management"},
    {"name": "shadowsocks_manager", "service_class": "ShadowsocksManagerService", "get_func": "get_shadowsocks_manager_service", "prefix": "/api/proxy/shadowsocks", "tag": "Shadowsocks Manager",
     "routes": [("POST","/add","add_server","Add Shadowsocks server"),("GET","/list","list_servers","List Shadowsocks servers"),("POST","/remove","remove_server","Remove Shadowsocks server"),("POST","/update","update_server","Update Shadowsocks server"),("GET","/traffic","get_traffic","Get traffic stats")],
     "features": "Shadowsocks server management, user management, traffic tracking"},
    {"name": "asscan", "service_class": "AsscanService", "get_func": "get_asscan_service", "prefix": "/api/recon/asscan", "tag": "AS Scanner",
     "routes": [("POST","/scan","scan","Start AS scan"),("GET","/results","get_results","Get AS scan results"),("DELETE","/results/{scan_id}","delete_results","Delete AS scan results")],
     "features": "AS number scanning, BGP monitoring, IP range discovery"},
    {"name": "dcipher", "service_class": "DCipherService", "get_func": "get_dcipher_service", "prefix": "/api/crypto/dcipher", "tag": "DCipher Decoder",
     "routes": [("POST","/decode","decode","Decode/decrypt data"),("GET","/results","get_results","Get decode results"),("DELETE","/results/{result_id}","delete_result","Delete decode result")],
     "features": "Hash detection, encoding detection, decryption"},
    {"name": "active_onions", "service_class": "ActiveOnionsService", "get_func": "get_active_onions_service", "prefix": "/api/recon/onions", "tag": "Active Onions",
     "routes": [("POST","/scan","scan","Scan for onion services"),("GET","/results","get_results","Get onion scan results"),("DELETE","/results/{scan_id}","delete_results","Delete onion scan results")],
     "features": "Onion service scanning, hidden service discovery"},
    {"name": "tor_detect", "service_class": "TorDetectService", "get_func": "get_tor_detect_service", "prefix": "/api/security/tor-detect", "tag": "Tor Detection",
     "routes": [("POST","/check","check","Check if IP uses Tor"),("GET","/results","get_results","Get Tor detection results"),("GET","/exit-nodes","list_exit_nodes","List known Tor exit nodes")],
     "features": "Tor exit node detection, anonymity checking"},
    {"name": "hash_detector", "service_class": "HashDetectorService", "get_func": "get_hash_detector_service", "prefix": "/api/crypto/hash", "tag": "Hash Detector",
     "routes": [("POST","/detect","detect","Detect hash type"),("GET","/results","get_results","Get hash detection results"),("POST","/crack","crack","Attempt hash crack")],
     "features": "Hash type detection, algorithm identification"},
    {"name": "hex", "service_class": "HexService", "get_func": "get_hex_service", "prefix": "/api/tools/hex", "tag": "Hex Tools",
     "routes": [("POST","/convert","convert","Convert hex to/from text"),("GET","/results","get_results","Get hex conversion results"),("POST","/analyze","analyze","Analyze binary data")],
     "features": "Hex encoding/decoding, binary analysis"},
    {"name": "url", "service_class": "UrlService", "get_func": "get_url_service", "prefix": "/api/tools/url", "tag": "URL Analyzer",
     "routes": [("POST","/analyze","analyze","Analyze URL"),("GET","/results","get_results","Get URL analysis results"),("POST","/safety","check_safety","Check URL safety")],
     "features": "URL parsing, encoding detection, safety analysis"},
    {"name": "binary", "service_class": "BinaryService", "get_func": "get_binary_service", "prefix": "/api/tools/binary", "tag": "Binary Analyzer",
     "routes": [("POST","/analyze","analyze","Analyze binary file"),("GET","/results","get_results","Get binary analysis results"),("POST","/parse-pe","parse_pe","Parse PE file"),("POST","/magic","detect_magic","Detect magic numbers")],
     "features": "Binary analysis, PE parsing, magic number detection"},
    {"name": "nginx_pm", "service_class": "NginxProxyManagerService", "get_func": "get_nginx_pm_service", "prefix": "/api/admin/nginx-pm", "tag": "Nginx Proxy Manager",
     "routes": [("POST","/proxy","create_proxy","Create reverse proxy"),("GET","/status","get_status","Get proxy status"),("DELETE","/proxy/{proxy_id}","delete_proxy","Delete reverse proxy"),("PUT","/proxy/{proxy_id}","update_proxy","Update reverse proxy")],
     "features": "Reverse proxy management, SSL termination"},
    {"name": "openvpn_install", "service_class": "OpenVpnInstallService", "get_func": "get_openvpn_install_service", "prefix": "/api/admin/openvpn", "tag": "OpenVPN Installer",
     "routes": [("POST","/install","install","Install OpenVPN server"),("POST","/client","generate_client","Generate client profile"),("GET","/status","get_status","Get OpenVPN status"),("POST","/uninstall","uninstall","Uninstall OpenVPN")],
     "features": "OpenVPN server installation, client profile generation"},
    {"name": "dnscrypt_proxy", "service_class": "DNSCryptProxyService", "get_func": "get_dnscrypt_proxy_service", "prefix": "/api/admin/dnscrypt", "tag": "DNSCrypt Proxy",
     "routes": [("POST","/start","start","Start DNSCrypt proxy"),("POST","/stop","stop","Stop DNSCrypt proxy"),("GET","/status","get_status","Get DNSCrypt status"),("POST","/config","update_config","Update DNSCrypt config")],
     "features": "DNSCrypt server management, resolver configuration"},
    {"name": "amass", "service_class": "AmassService", "get_func": "get_amass_service", "prefix": "/api/recon/amass", "tag": "Amass Enumeration",
     "routes": [("POST","/enumerate","enumerate","Start subdomain enumeration"),("GET","/results","get_results","Get enumeration results"),("DELETE","/results/{scan_id}","delete_results","Delete enumeration results"),("GET","/sources","list_sources","List available sources")],
     "features": "Subdomain enumeration, passive/active sources, DNS resolution"},
    {"name": "bettercap", "service_class": "BettercapService", "get_func": "get_bettercap_service", "prefix": "/api/exploit/bettercap", "tag": "Bettercap",
     "routes": [("POST","/run","run","Run bettercap session"),("GET","/status","get_status","Get bettercap status"),("POST","/stop","stop","Stop bettercap session"),("GET","/events","get_events","Get bettercap events")],
     "features": "MITM attacks, packet sniffing, network mapping"},
    {"name": "v2ray_plugin", "service_class": "V2rayPluginService", "get_func": "get_v2ray_plugin_service", "prefix": "/api/proxy/v2ray", "tag": "V2Ray Plugin",
     "routes": [("POST","/configure","configure","Configure V2Ray"),("GET","/status","get_status","Get V2Ray status"),("POST","/start","start","Start V2Ray"),("POST","/stop","stop","Stop V2Ray")],
     "features": "V2Ray plugin management, proxy configuration"},
    {"name": "graphenex", "service_class": "GrapheneXService", "get_func": "get_graphenex_service", "prefix": "/api/exploit/graphenex", "tag": "GrapheneX",
     "routes": [("POST","/run","run","Run GrapheneX attack"),("GET","/results","get_results","Get GrapheneX results"),("GET","/status","get_status","Get GrapheneX status")],
     "features": "Network exploitation, protocol attacks"},
    {"name": "nucypher", "service_class": "NucypherService", "get_func": "get_nucypher_service", "prefix": "/api/crypto/nucypher", "tag": "Nucypher",
     "routes": [("POST","/encrypt","encrypt","Encrypt with threshold crypto"),("POST","/decrypt","decrypt","Decrypt with threshold crypto"),("POST","/key-share","key_share","Generate key share"),("GET","/status","get_status","Get Nucypher status")],
     "features": "Threshold cryptography, key sharing, encryption"},
    {"name": "webscraping", "service_class": "WebscrapingService", "get_func": "get_webscraping_service", "prefix": "/api/recon/webscraping", "tag": "Webscraping Framework",
     "routes": [("POST","/run","run","Run web scrape"),("GET","/results","get_results","Get scrape results"),("DELETE","/results/{scan_id}","delete_results","Delete scrape results")],
     "features": "Web scraping, data extraction, crawling"},
    {"name": "cowrie", "service_class": "CowrieService", "get_func": "get_cowrie_service", "prefix": "/api/security/cowrie", "tag": "Cowrie Honeypot",
     "routes": [("POST","/start","start","Start Cowrie honeypot"),("GET","/logs","get_logs","Get Cowrie logs"),("POST","/stop","stop","Stop Cowrie honeypot"),("GET","/status","get_status","Get Cowrie status")],
     "features": "SSH honeypot management, attack logging, threat intelligence"},
    {"name": "certbot", "service_class": "CertbotService", "get_func": "get_certbot_service", "prefix": "/api/admin/certbot", "tag": "Certbot",
     "routes": [("POST","/request","request_cert","Request SSL certificate"),("GET","/status","get_status","Get certbot status"),("GET","/certs","list_certs","List certificates"),("POST","/renew","renew_certs","Renew certificates")],
     "features": "SSL certificate management, Let's Encrypt integration"},
    {"name": "attack_range", "service_class": "AttackRangeService", "get_func": "get_attack_range_service", "prefix": "/api/security/attack-range", "tag": "Attack Range",
     "routes": [("POST","/deploy","deploy","Deploy attack range"),("POST","/attack","run_attack","Run attack simulation"),("GET","/status","get_status","Get attack range status"),("POST","/teardown","teardown","Tear down attack range")],
     "features": "MITRE ATT&CK simulation, attack replay, detection testing"},
    {"name": "spraying_toolkit", "service_class": "SprayingToolkitService", "get_func": "get_spraying_toolkit_service", "prefix": "/api/exploit/spraying", "tag": "Password Spraying",
     "routes": [("POST","/run","run","Run password spraying"),("GET","/results","get_results","Get spraying results"),("GET","/status","get_status","Get spraying status")],
     "features": "Password spraying, credential stuffing, dictionary attacks"},
    {"name": "king_phisher", "service_class": "KingPhisherService", "get_func": "get_king_phisher_service", "prefix": "/api/exploit/phishing", "tag": "King Phisher",
     "routes": [("POST","/create","create_campaign","Create phishing campaign"),("POST","/send","send_email","Send phishing email"),("GET","/campaigns","list_campaigns","List campaigns"),("GET","/results","get_results","Get campaign results")],
     "features": "Phishing campaign management, template creation, tracking"},
    {"name": "toolbox", "service_class": "ToolboxService", "get_func": "get_toolbox_service", "prefix": "/api/tools/toolbox", "tag": "Security Toolbox",
     "routes": [("POST","/run","run","Run toolbox command"),("GET","/results","get_results","Get toolbox results"),("GET","/tools","list_tools","List available tools")],
     "features": "Security tool aggregation, tool execution, results collection"},
    {"name": "opencti", "service_class": "OpenCTIService", "get_func": "get_opencti_service", "prefix": "/api/intel/opencti", "tag": "OpenCTI",
     "routes": [("POST","/import","import_intel","Import threat intel"),("GET","/query","query_intel","Query threat intel"),("GET","/status","get_status","Get OpenCTI status"),("POST","/stix","import_stix","Import STIX object")],
     "features": "Threat intelligence platform integration, STIX/TAXII"},
    {"name": "mitmproxy", "service_class": "MitmproxyService", "get_func": "get_mitmproxy_service", "prefix": "/api/tools/mitmproxy", "tag": "Mitmproxy",
     "routes": [("POST","/start","start","Start mitmproxy"),("POST","/stop","stop","Stop mitmproxy"),("GET","/status","get_status","Get mitmproxy status"),("GET","/flows","get_flows","Get proxy flows")],
     "features": "HTTP/HTTPS proxy, traffic interception, request modification"},
    {"name": "bloodyad", "service_class": "BloodyADService", "get_func": "get_bloodyad_service", "prefix": "/api/exploit/bloodyad", "tag": "BloodyAD",
     "routes": [("POST","/run","run","Run AD attack"),("GET","/results","get_results","Get AD attack results"),("GET","/status","get_status","Get BloodyAD status")],
     "features": "Active Directory exploitation, privilege escalation"},
    {"name": "shadowsocks_api", "service_class": "ShadowsocksApiService", "get_func": "get_shadowsocks_api_service", "prefix": "/api/proxy/shadowsocks-api", "tag": "Shadowsocks REST API",
     "routes": [("POST","/add","add_user","Add Shadowsocks user via API"),("GET","/list","list_users","List Shadowsocks users"),("POST","/update","update_user","Update Shadowsocks user"),("POST","/remove","remove_user","Remove Shadowsocks user")],
     "features": "RESTful API for Shadowsocks management"},
    {"name": "fastjson", "service_class": "FastjsonService", "get_func": "get_fastjson_service", "prefix": "/api/exploit/fastjson", "tag": "Fastjson RCE",
     "routes": [("POST","/test","test_rce","Test Fastjson RCE"),("GET","/results","get_results","Get Fastjson test results"),("GET","/status","get_status","Get Fastjson status")],
     "features": "Fastjson RCE detection, exploitation testing"},
]


def create_service(tool):
    name = tool["name"]
    cls = tool["service_class"]
    get_fn = tool["get_func"]
    features = tool["features"]
    routes = tool["routes"]

    lines = []
    lines.append(f'"""')
    lines.append(f'{cls} Service - {features}.')
    lines.append(f'"""')
    lines.append('from __future__ import annotations')
    lines.append('')
    lines.append('import asyncio')
    lines.append('import logging')
    lines.append('import uuid')
    lines.append('from datetime import datetime, timezone')
    lines.append('from typing import Any')
    lines.append('')
    lines.append('logger = logging.getLogger(__name__)')
    lines.append('')
    lines.append('')
    lines.append(f'class {cls}:')
    lines.append(f'    """Wrapper for {name} tool: {features}."""')
    lines.append('')
    lines.append('    def __init__(self):')
    lines.append('        self._results: dict[str, dict[str, Any]] = {}')
    lines.append('        self._lock = asyncio.Lock()')
    lines.append(f'        logger.info("{cls} initialized")')
    
    for method, path, fn_name, desc in routes:
        path_params = re.findall(r"\{(\w+)\}", path)
        lines.append('')
        if path_params:
            param = path_params[0]
            if method in ("PUT", "PATCH"):
                lines.append(f'    async def {fn_name}(self, {param}: str, data: dict[str, Any] = None) -> dict[str, Any]:')
                lines.append(f'        """{desc}."""')
                lines.append(f'        return {{"status": "updated", "{param}": {param}, "data": data}}')
            else:
                lines.append(f'    async def {fn_name}(self, {param}: str) -> dict[str, Any]:')
                lines.append(f'        """{desc}."""')
                lines.append(f'        return {{"status": "ok", "{param}": {param}}}')
        elif method in ("POST", "PUT"):
            lines.append(f'    async def {fn_name}(self, **kwargs) -> dict[str, Any]:')
            lines.append(f'        """{desc}."""')
            lines.append('        scan_id = str(uuid.uuid4())')
            lines.append('        self._results[scan_id] = {"id": scan_id, "status": "completed", "data": {}}')
            lines.append('        return self._results[scan_id]')
        else:
            lines.append(f'    async def {fn_name}(self) -> dict[str, Any]:')
            lines.append(f'        """{desc}."""')
            lines.append('        return {"status": "ok", "data": {}}')
    
    lines.append('')
    lines.append('    async def fetch_result(self, item_id: str) -> dict[str, Any]:')
    lines.append('        """Get results for a specific item."""')
    lines.append('        return self._results.get(item_id, {"id": item_id, "status": "not_found"})')
    lines.append('')
    lines.append('    async def cleanup(self, item_id: str) -> bool:')
    lines.append('        """Clean up results."""')
    lines.append('        if item_id in self._results:')
    lines.append('            del self._results[item_id]')
    lines.append('            return True')
    lines.append('        return False')
    lines.append('')
    lines.append('')
    lines.append('# Singleton')
    lines.append(f'_service: {cls} | None = None')
    lines.append('')
    lines.append('')
    lines.append(f'def {get_fn}() -> {cls}:')
    lines.append('    global _service')
    lines.append('    if _service is None:')
    lines.append(f'        _service = {cls}()')
    lines.append('    return _service')
    lines.append('')
    
    return '\n'.join(lines)


def create_router(tool):
    name = tool["name"]
    cls = tool["service_class"]
    get_fn = tool["get_func"]
    prefix = tool["prefix"]
    tag = tool["tag"]
    routes = tool["routes"]

    lines = []
    lines.append(f'"""')
    lines.append(f'{cls} Routes - REST API for {name}.')
    lines.append(f'"""')
    lines.append('import os')
    lines.append('from typing import Any')
    lines.append('')
    lines.append('from fastapi import APIRouter, Depends, HTTPException, Request')
    lines.append('')
    lines.append(f'from app.services.{name}_service import {get_fn}')
    lines.append('')
    lines.append('')
    lines.append('# Authentication dependency')
    lines.append('QUANTUM_C2_API_KEY = os.environ.get("QUANTUM_C2_API_KEY", "")')
    lines.append('')
    lines.append('')
    lines.append('def verify_auth(request: Request):')
    lines.append('    """Verify API key authentication for Quantum C2 endpoints."""')
    lines.append('    if not QUANTUM_C2_API_KEY:')
    lines.append('        raise HTTPException(')
    lines.append('            status_code=500,')
    lines.append('            detail="QUANTUM_C2_API_KEY environment variable not configured"')
    lines.append('        )')
    lines.append('    ')
    lines.append('    provided = (')
    lines.append('        request.headers.get("X-API-Key")')
    lines.append('        or request.headers.get("X-Auth-Token")')
    lines.append('        or request.headers.get("Authorization", "").replace("Bearer ", "")')
    lines.append('    )')
    lines.append('    ')
    lines.append('    if provided != QUANTUM_C2_API_KEY:')
    lines.append('        raise HTTPException(status_code=401, detail="Unauthorized")')
    lines.append('    ')
    lines.append('    return True')
    lines.append('')
    lines.append('')
    lines.append(f'router = APIRouter(prefix="{prefix}", tags=["{tag}"], dependencies=[Depends(verify_auth)])')
    lines.append('')
    lines.append(f'_service = {get_fn}()')
    lines.append('')
    
    for method, path, fn_name, desc in routes:
        path_params = re.findall(r"\{(\w+)\}", path)
        sig_parts = []
        if path_params:
            sig_parts.extend(f"{p}: str" for p in path_params)
        if method in ("POST", "PUT"):
            sig_parts.append('req: dict[str, Any] = {}')
        sig = ", ".join(sig_parts)
        
        call_args = []
        if path_params:
            call_args.extend(path_params)
        if method in ("POST", "PUT"):
            call_args.append("req")
        call_str = ", ".join(call_args)
        
        lines.append(f'@router.{method.lower()}("{path}")')
        lines.append(f'async def {fn_name}({sig}):')
        lines.append(f'    """{desc}."""')
        lines.append(f'    return await _service.{fn_name}({call_str})')
        lines.append('')
    
    return '\n'.join(lines)


def main():
    os.makedirs(SERVICES_DIR, exist_ok=True)
    os.makedirs(ROUTERS_DIR, exist_ok=True)

    for tool in TOOLS:
        name = tool["name"]
        service_path = os.path.join(SERVICES_DIR, f"{name}_service.py")
        with open(service_path, "w", encoding="utf-8") as f:
            f.write(create_service(tool))
        print(f"Created: {service_path}")

        router_path = os.path.join(ROUTERS_DIR, f"{name}_routes.py")
        with open(router_path, "w", encoding="utf-8") as f:
            f.write(create_router(tool))
        print(f"Created: {router_path}")

    print(f"\nDone: {len(TOOLS)} services, {len(TOOLS)} routers")


if __name__ == "__main__":
    main()
