import json
import os
import time
import uuid
import threading
import requests
from pathlib import Path

# Module-level shared state so chains persist across agent instances
_chain_lock = threading.Lock()
_chains = {}

# CVE API integration
SHODAN_API_KEY = os.getenv("SHODAN_API_KEY", "")

# Cache for API results with TTL (10 minutes)
_CVE_API_CACHE = {}
_CACHE_TTL = 600


def fetch_cve_from_shodan(cve_id):
    """Fetch CVE details from Shodan API.
    
    Args:
        cve_id: CVE identifier (e.g., "CVE-2019-8641")
    
    Returns:
        Dict with CVE details or None if not found
    """
    if not SHODAN_API_KEY:
        return None
    
    # Check cache
    cache_key = f"shodan:{cve_id}"
    if cache_key in _CVE_API_CACHE:
        cached_entry = _CVE_API_CACHE[cache_key]
        if time.time() - cached_entry["timestamp"] < _CACHE_TTL:
            return cached_entry["data"]
    
    try:
        # Query Shodan for CVE details
        url = f"https://api.shodan.io/v2/cve/{cve_id}?key={SHODAN_API_KEY}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            vulns = data.get("vulns", {})
            if cve_id in vulns:
                cve_data = vulns[cve_id]
                
                # Extract relevant CVE information
                result = {
                    "title": cve_data.get("title", "Not Available"),
                    "source": cve_data.get("source", "shodan"),
                    "references": cve_data.get("references", []),
                    "stats": cve_data.get("stats", {}),
                    "published": cve_data.get("published", ""),
                    "modified": cve_data.get("modified", "")
                }
                
                # Store in cache
                _CVE_API_CACHE[cache_key] = {
                    "timestamp": time.time(),
                    "data": result
                }
                
                return result
        else:
            print(f"Shodan API error for {cve_id}: HTTP {response.status_code}")
            return None
    
    except requests.RequestException as e:
        print(f"Shodan API request failed for {cve_id}: {str(e)}")
        return None
    except Exception as e:
        print(f"Unexpected error fetching CVE from Shodan: {str(e)}")
        return None


class ChainedZeroDayAgent:
    """Chained zero-day exploitation simulation agent.
    
    Models multi-stage exploit chains for defensive research and red team planning.
    All exploit-related methods return {"status": "simulated"} — no real payloads.
    """

    def __init__(self):
        self._known_chains = {
            "pegasus": {
                "name": "Pegasus (NSO Group)",
                "stages": [
                    {"stage": 1, "type": "messaging_rce", "cve": "CVE-2019-8641", "description": "iMessage vulnerability for initial access"},
                    {"stage": 2, "type": "kernel_lpe", "cve": "CVE-2019-8646", "description": "Kernel vulnerability for privilege escalation"},
                    {"stage": 3, "type": "sandbox_escape", "cve": "CVE-2019-8647", "description": "Sandbox escape for persistence"}
                ],
                "description": "Three-stage no-click exploit chain targeting iOS devices",
                "success_probability": 0.72
            },
            "forcedentry": {
                "name": "FORCEDENTRY",
                "stages": [
                    {"stage": 1, "type": "image_parsing", "cve": "CVE-2021-30860", "description": "GIF parsing vulnerability bypassing blast door"},
                    {"stage": 2, "type": "kernel_lpe", "cve": "CVE-2021-30860", "description": "Kernel privilege escalation"}
                ],
                "description": "No-click iMessage exploit chain using image parsing",
                "success_probability": 0.65
            },
            "blastpass": {
                "name": "BLASTPASS",
                "stages": [
                    {"stage": 1, "type": "image_parsing", "cve": "CVE-2023-41064", "description": "Image parsing vulnerability in iMessage"},
                    {"stage": 2, "type": "kernel_lpe", "cve": "CVE-2023-41061", "description": "Kernel privilege escalation"},
                    {"stage": 3, "type": "sandbox_escape", "cve": "CVE-2023-40425", "description": "Sandbox escape for full compromise"}
                ],
                "description": "No-click exploit chain targeting Apple devices via iMessage",
                "success_probability": 0.68
            }
        }
        self._cve_database = {
            "CVE-2019-8641": {
                "title": "iMessage Remote Code Execution",
                "severity": "critical",
                "stage": "initial_access",
                "type": "messaging_rce",
                "cvss": 9.8,
                "description": "Memory corruption in iMessage processing"
            },
            "CVE-2019-8646": {
                "title": "Kernel Privilege Escalation",
                "severity": "high",
                "stage": "privilege_escalation",
                "type": "kernel_lpe",
                "cvss": 8.8,
                "description": "Use-after-free in kernel memory management"
            },
            "CVE-2019-8647": {
                "title": "Sandbox Escape",
                "severity": "high",
                "stage": "persistence",
                "type": "sandbox_escape",
                "cvss": 8.4,
                "description": "Sandbox bypass via type confusion"
            },
            "CVE-2021-30860": {
                "title": "GIF Parsing Vulnerability",
                "severity": "critical",
                "stage": "initial_access",
                "type": "image_parsing",
                "cvss": 9.8,
                "description": "Integer overflow in GIF parsing bypasses blast door"
            },
            "CVE-2023-41064": {
                "title": "Image Parsing RCE",
                "severity": "critical",
                "stage": "initial_access",
                "type": "image_parsing",
                "cvss": 9.8,
                "description": "Buffer overflow in image processing"
            },
            "CVE-2023-41061": {
                "title": "Kernel LPE",
                "severity": "high",
                "stage": "privilege_escalation",
                "type": "kernel_lpe",
                "cvss": 8.8,
                "description": "Kernel memory corruption"
            },
            "CVE-2023-40425": {
                "title": "Sandbox Escape",
                "severity": "high",
                "stage": "persistence",
                "type": "sandbox_escape",
                "cvss": 8.4,
                "description": "Sandbox bypass vulnerability"
            }
        }

    def describe(self):
        """Return agent description and capabilities."""
        return {
            "name": "chained_zero_day",
            "description": "Chained zero-day exploitation simulation agent for multi-stage attack chains",
            "category": "red_teaming",
            "capabilities": [
                "build_chain",
                "analyze_chain",
                "simulate_chain",
                "list_chains",
                "optimize_chain",
                "get_cves"
            ]
        }

    def build_chain(self, stages):
        """Construct a multi-stage exploit chain.
        
        Args:
            stages: List of stage dicts with keys: stage, type, cve (optional), description (optional)
        
        Returns:
            Dict with chain_id, stages, created_at, status
        """
        chain_id = str(uuid.uuid4())[:8]
        chain = {
            "chain_id": chain_id,
            "stages": stages,
            "created_at": time.time(),
            "status": "built",
            "num_stages": len(stages)
        }
        with _chain_lock:
            _chains[chain_id] = chain
        return {"status": "simulated", "chain_id": chain_id, "chain": chain}

    def analyze_chain(self, chain_id):
        """Analyze chain viability, dependencies, and success probability.
        
        Args:
            chain_id: ID of the chain to analyze
        
        Returns:
            Dict with analysis results including viability score and success probability
        """
        with _chain_lock:
            if chain_id not in _chains:
                return {"status": "simulated", "error": "chain not found", "chain_id": chain_id}
            chain = _chains[chain_id]

        # Calculate success probability based on stages
        base_prob = 0.85
        stage_penalty = 0.05 * (chain["num_stages"] - 1)
        success_prob = max(0.1, base_prob - stage_penalty)

        # Dependency analysis
        dependencies = []
        for i, stage in enumerate(chain["stages"]):
            dep = {
                "stage": stage["stage"],
                "type": stage["type"],
                "depends_on": chain["stages"][i - 1]["type"] if i > 0 else None,
                "failure_impact": "chain_failure" if i < len(chain["stages"]) - 1 else "partial_success"
            }
            dependencies.append(dep)

        analysis = {
            "status": "simulated",
            "chain_id": chain_id,
            "viability_score": round(success_prob * 100, 2),
            "success_probability": round(success_prob, 4),
            "num_stages": chain["num_stages"],
            "dependencies": dependencies,
            "risk_assessment": {
                "detection_probability": round(1 - success_prob, 4),
                "complexity": "high" if chain["num_stages"] > 3 else "medium",
                "stealth_rating": round(success_prob * 0.9, 4)
            }
        }
        return analysis

    def simulate_chain(self, chain_id, target=None):
        """Simulate chain execution against a target.
        
        Args:
            chain_id: ID of the chain to simulate
            target: Target identifier (IP, hostname, etc.)
        
        Returns:
            Dict with simulation results (always {"status": "simulated"})
        """
        with _chain_lock:
            if chain_id not in _chains:
                return {"status": "simulated", "error": "chain not found", "chain_id": chain_id}
            chain = _chains[chain_id]

        simulation = {
            "status": "simulated",
            "chain_id": chain_id,
            "target": target,
            "stages_executed": chain["num_stages"],
            "stage_results": []
        }

        for stage in chain["stages"]:
            stage_result = {
                "stage": stage["stage"],
                "type": stage["type"],
                "status": "simulated",
                "success": True,
                "timestamp": time.time()
            }
            simulation["stage_results"].append(stage_result)

        simulation["overall_status"] = "simulated_success"
        simulation["simulated_at"] = time.time()
        return simulation

    def list_chains(self):
        """Return known real-world exploit chains."""
        chains = {}
        for key, chain in self._known_chains.items():
            chains[key] = {
                "name": chain["name"],
                "num_stages": len(chain["stages"]),
                "description": chain["description"],
                "success_probability": chain["success_probability"]
            }
        return {"status": "simulated", "chains": chains}

    def optimize_chain(self, chain_id):
        """AI-assisted chain optimization suggestions.
        
        Args:
            chain_id: ID of the chain to optimize
        
        Returns:
            Dict with optimization suggestions
        """
        with _chain_lock:
            if chain_id not in _chains:
                return {"status": "simulated", "error": "chain not found", "chain_id": chain_id}
            chain = _chains[chain_id]

        suggestions = []

        # Suggest redundancy for critical stages
        if chain["num_stages"] >= 2:
            suggestions.append({
                "type": "redundancy",
                "description": "Add fallback vulnerability for stage 1 to increase reliability",
                "impact": "Increases success probability by ~15%"
            })

        # Suggest stealth improvements
        suggestions.append({
            "type": "stealth",
            "description": "Use encrypted C2 channel for exfiltration stage",
            "impact": "Reduces detection probability by ~30%"
        })

        # Suggest timing optimization
        suggestions.append({
            "type": "timing",
            "description": "Implement delay between stages to avoid correlation detection",
            "impact": "Reduces detection probability by ~20%"
        })

        # Suggest alternative paths
        if chain["num_stages"] < 4:
            suggestions.append({
                "type": "chain_extension",
                "description": "Consider adding persistence and exfiltration stages for full lifecycle",
                "impact": "Completes attack chain for operational readiness"
            })

        return {
            "status": "simulated",
            "chain_id": chain_id,
            "suggestions": suggestions,
            "num_suggestions": len(suggestions)
        }

    def get_cves(self):
        """Return CVE database for chain building.
        
        Queries real CVE APIs (Shodan) when available, merging with 
        simulated database. Fallback to simulated data if API fails.
        
        Returns:
            Dict with merged CVE database including real API data
        """
        enhanced_cves = {}

        # Start with simulated database
        for cve_id, data in self._cve_database.items():
            enhanced_cves[cve_id] = data.copy()

        # Use only CVEs from our simulated database for API queries
        cve_ids_to_query = list(self._cve_database.keys())

        # Fetch real CVE data from Shodan API
        real_cves_found = 0
        for cve_id in cve_ids_to_query:
            cve_data = fetch_cve_from_shodan(cve_id)
            if cve_data:
                # Enrich the entry with real data
                enhanced_cves[cve_id].update({
                    "source": "api_enriched",
                    "api_title": cve_data.get("title"),
                    "api_published": cve_data.get("published", ""),
                    "api_modified": cve_data.get("modified", ""),
                    "api_references": cve_data.get("references", []),
                    "api_stats": cve_data.get("stats", {}),
                    "data_source": "Mixed (simulated + Shodan API)"
                })
                real_cves_found += 1

        return {
            "status": "simulated",  # Maintain backward compatibility
            "data_source": f"Mixed (simulated base {len(self._cve_database)} + {real_cves_found} real API enrichments)",
            "cves": enhanced_cves,
            "api_enrichments_applied": real_cves_found
        }
