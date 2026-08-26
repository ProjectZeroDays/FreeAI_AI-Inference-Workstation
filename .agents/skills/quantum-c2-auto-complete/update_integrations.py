"""Update __init__.py files and main.py to register all 30 new integrations."""
import re

BASE = r"C:\Projects\Quantum C2\backend\app"

TOOLS = [
    "openpgpjs", "shadowsocks_manager", "asscan", "dcipher", "active_onions",
    "tor_detect", "hash_detector", "hex", "url", "binary",
    "nginx_pm", "openvpn_install", "dnscrypt_proxy", "amass", "bettercap",
    "v2ray_plugin", "graphenex", "nucypher", "webscraping", "cowrie",
    "certbot", "attack_range", "spraying_toolkit", "king_phisher", "toolbox",
    "opencti", "mitmproxy", "bloodyad", "shadowsocks_api", "fastjson",
]

# Prefixes matching the router definitions
PREFIXES = {
    "openpgpjs": "/api/crypto/pgp",
    "shadowsocks_manager": "/api/proxy/shadowsocks",
    "asscan": "/api/recon/asscan",
    "dcipher": "/api/crypto/dcipher",
    "active_onions": "/api/recon/onions",
    "tor_detect": "/api/security/tor-detect",
    "hash_detector": "/api/crypto/hash",
    "hex": "/api/tools/hex",
    "url": "/api/tools/url",
    "binary": "/api/tools/binary",
    "nginx_pm": "/api/admin/nginx-pm",
    "openvpn_install": "/api/admin/openvpn",
    "dnscrypt_proxy": "/api/admin/dnscrypt",
    "amass": "/api/recon/amass",
    "bettercap": "/api/exploit/bettercap",
    "v2ray_plugin": "/api/proxy/v2ray",
    "graphenex": "/api/exploit/graphenex",
    "nucypher": "/api/crypto/nucypher",
    "webscraping": "/api/recon/webscraping",
    "cowrie": "/api/security/cowrie",
    "certbot": "/api/admin/certbot",
    "attack_range": "/api/security/attack-range",
    "spraying_toolkit": "/api/exploit/spraying",
    "king_phisher": "/api/exploit/phishing",
    "toolbox": "/api/tools/toolbox",
    "opencti": "/api/intel/opencti",
    "mitmproxy": "/api/tools/mitmproxy",
    "bloodyad": "/api/exploit/bloodyad",
    "shadowsocks_api": "/api/proxy/shadowsocks-api",
    "fastjson": "/api/exploit/fastjson",
}

# Service class names and getter functions
SERVICE_MAP = {
    "openpgpjs": ("OpenPgpjsService", "get_openpgpjs_service"),
    "shadowsocks_manager": ("ShadowsocksManagerService", "get_shadowsocks_manager_service"),
    "asscan": ("AsscanService", "get_asscan_service"),
    "dcipher": ("DCipherService", "get_dcipher_service"),
    "active_onions": ("ActiveOnionsService", "get_active_onions_service"),
    "tor_detect": ("TorDetectService", "get_tor_detect_service"),
    "hash_detector": ("HashDetectorService", "get_hash_detector_service"),
    "hex": ("HexService", "get_hex_service"),
    "url": ("UrlService", "get_url_service"),
    "binary": ("BinaryService", "get_binary_service"),
    "nginx_pm": ("NginxProxyManagerService", "get_nginx_pm_service"),
    "openvpn_install": ("OpenVpnInstallService", "get_openvpn_install_service"),
    "dnscrypt_proxy": ("DNSCryptProxyService", "get_dnscrypt_proxy_service"),
    "amass": ("AmassService", "get_amass_service"),
    "bettercap": ("BettercapService", "get_bettercap_service"),
    "v2ray_plugin": ("V2rayPluginService", "get_v2ray_plugin_service"),
    "graphenex": ("GrapheneXService", "get_graphenex_service"),
    "nucypher": ("NucypherService", "get_nucypher_service"),
    "webscraping": ("WebscrapingService", "get_webscraping_service"),
    "cowrie": ("CowrieService", "get_cowrie_service"),
    "certbot": ("CertbotService", "get_certbot_service"),
    "attack_range": ("AttackRangeService", "get_attack_range_service"),
    "spraying_toolkit": ("SprayingToolkitService", "get_spraying_toolkit_service"),
    "king_phisher": ("KingPhisherService", "get_king_phisher_service"),
    "toolbox": ("ToolboxService", "get_toolbox_service"),
    "opencti": ("OpenCTIService", "get_opencti_service"),
    "mitmproxy": ("MitmproxyService", "get_mitmproxy_service"),
    "bloodyad": ("BloodyADService", "get_bloodyad_service"),
    "shadowsocks_api": ("ShadowsocksApiService", "get_shadowsocks_api_service"),
    "fastjson": ("FastjsonService", "get_fastjson_service"),
}


def update_routers_init():
    path = rf"{BASE}\routers\__init__.py"
    with open(path, "r") as f:
        content = f.read()

    # Add imports after xencrypt_routes
    imports_to_add = "\n".join(f"    {name}_routes," for name in TOOLS)
    content = content.replace(
        "    xencrypt_routes,\n    # Security tool integrations",
        f"    xencrypt_routes,\n{imports_to_add}\n    # Security tool integrations"
    )
    
    # Add to __all__ list
    all_entries = "\n".join(f'    "{name}_routes",' for name in TOOLS)
    content = content.replace(
        '    "xencrypt_routes",\n]',
        f'    "xencrypt_routes",\n{all_entries}\n]'
    )
    
    with open(path, "w") as f:
        f.write(content)
    print(f"Updated {path}")


def update_all_routes():
    path = rf"{BASE}\api\all_routes.py"
    with open(path, "r") as f:
        content = f.read()

    # Add imports
    imports_to_add = "\n".join(f"    {name}_routes," for name in TOOLS)
    content = content.replace(
        "    xencrypt_routes,\n)",
        f"    xencrypt_routes,\n{imports_to_add}\n)"
    )

    # Add ROUTER_PREFIXES entries after xencrypt
    prefix_lines = []
    for name in TOOLS:
        prefix_lines.append(f'    "{name}_routes": "{PREFIXES[name]}",')
    prefix_entries = "\n".join(prefix_lines)
    content = content.replace(
        '    "xencrypt_routes": "/api/exploit/xencrypt",\n    # Security tool integrations',
        prefix_entries + "\n    # Security tool integrations"
    )

    # Add router_modules entries after xencrypt
    module_lines = []
    for name in TOOLS:
        module_lines.append(f'    ("{name}_routes", {name}_routes),')
    module_entries = "\n".join(module_lines)
    content = content.replace(
        '    ("xencrypt_routes", xencrypt_routes),\n        ]',
        f'    ("xencrypt_routes", xencrypt_routes),\n{module_entries}\n        ]'
    )

    with open(path, "w") as f:
        f.write(content)
    print(f"Updated {path}")


def update_main():
    path = rf"{BASE}\main.py"
    with open(path, "r") as f:
        content = f.read()

    # Build service initialization blocks
    init_blocks = []
    shutdown_blocks = []
    for name in TOOLS:
        cls, get_fn = SERVICE_MAP[name]
        var_name = f"{name}_service"
        init_blocks.append(f'''
    # Initialize {cls}
    try:
        from app.services.{name}_service import {get_fn}
        {var_name} = {get_fn}()
        app.state.{var_name} = {var_name}
        logger.info("{cls} initialized")
    except Exception as e:
        logger.warning(f"{cls} init failed: {{e}}")''')
        shutdown_blocks.append(f'''
    # Shutdown {cls}
    try:
        if hasattr(app.state, '{var_name}'):
            logger.info("{cls} shut down")
    except Exception as e:
        logger.warning(f"{cls} shutdown warning: {{e}}")''')

    # Add imports at top of lifespan (after existing imports section)
    import_lines = "\n".join(f"    from app.services.{name}_service import {get_fn}" for name in TOOLS)
    
    # Add service initializations before the `yield` statement
    yield_marker = "    yield\n\n    # Stop exploit feed scheduler"
    content = content.replace(yield_marker, "".join(init_blocks) + "\n\n    yield\n\n    # Stop exploit feed scheduler")
    
    # Add shutdown blocks before the final logger line
    shutdown_marker = '    logger.info("Application shutdown complete")'
    content = content.replace(shutdown_marker, "".join(shutdown_blocks) + '\n\n    ' + shutdown_marker)

    with open(path, "w") as f:
        f.write(content)
    print(f"Updated {path}")


def main():
    update_routers_init()
    update_all_routes()
    update_main()
    print("\nAll integration files updated successfully.")


if __name__ == "__main__":
    main()
