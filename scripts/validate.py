#!/usr/bin/env python3
"""
validate.py — Script de validation complète de l'infrastructure Meeting AI Platform.

Ce script vérifie automatiquement l'état de tous les services Docker et API.
Usage : python scripts/validate.py
"""
import sys
import json
import time
import urllib.request
import urllib.error
from typing import NamedTuple


# ─── Configuration des services à tester ───────────────────────────────────────
SERVICES = [
    {"name": "Backend FastAPI",   "url": "http://localhost:80/api/health"},
    {"name": "Frontend React",    "url": "http://localhost:80/"},
    {"name": "Keycloak",          "url": "http://localhost:8080/keycloak/health/live"},
    {"name": "MinIO",             "url": "http://localhost:9000/minio/health/live"},
    {"name": "Flower (Celery)",   "url": "http://localhost:5555/"},
    {"name": "Prometheus",        "url": "http://localhost:9090/-/healthy"},
    {"name": "Grafana",           "url": "http://localhost:3000/api/health"},
    {"name": "ChromaDB",          "url": "http://localhost:8002/api/v1/heartbeat"},
    {"name": "Ollama",            "url": "http://localhost:11434/api/tags"},
]

API_CHECKS = [
    {"name": "Health Check",          "url": "http://localhost:80/api/health",          "expected_key": "status"},
    {"name": "Workers Health",        "url": "http://localhost:80/api/v1/workers/health","expected_key": "broker"},
    {"name": "Storage Health",        "url": "http://localhost:80/api/v1/storage/health","expected_key": "status"},
    {"name": "RAG Health",            "url": "http://localhost:80/api/v1/rag/health",   "expected_key": "status"},
]

# ─── Couleurs ANSI pour le terminal ────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"


class CheckResult(NamedTuple):
    name: str
    success: bool
    detail: str


def check_http(name: str, url: str, timeout: int = 5) -> CheckResult:
    """Vérifie qu'un endpoint HTTP est accessible et renvoie une réponse 2xx."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "MeetingAI-Validator/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status < 300:
                return CheckResult(name=name, success=True, detail=f"HTTP {resp.status}")
            return CheckResult(name=name, success=False, detail=f"HTTP {resp.status}")
    except urllib.error.HTTPError as e:
        if e.code in (302, 301):
            return CheckResult(name=name, success=True, detail=f"HTTP {e.code} (redirect OK)")
        return CheckResult(name=name, success=False, detail=f"HTTP Error {e.code}")
    except urllib.error.URLError as e:
        return CheckResult(name=name, success=False, detail=f"Connexion impossible : {e.reason}")
    except Exception as e:
        return CheckResult(name=name, success=False, detail=str(e))


def check_api_key(name: str, url: str, expected_key: str, timeout: int = 5) -> CheckResult:
    """Vérifie qu'un endpoint API JSON contient une clé spécifique dans sa réponse."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "MeetingAI-Validator/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            if expected_key in body:
                return CheckResult(name=name, success=True, detail=f"'{expected_key}': {body[expected_key]}")
            return CheckResult(name=name, success=False, detail=f"Clé '{expected_key}' absente du payload")
    except Exception as e:
        return CheckResult(name=name, success=False, detail=str(e))


def print_result(result: CheckResult) -> None:
    icon = f"{GREEN}✅{RESET}" if result.success else f"{RED}❌{RESET}"
    name_padded = result.name.ljust(30)
    print(f"  {icon} {BOLD}{name_padded}{RESET}  {result.detail}")


def print_section(title: str) -> None:
    print(f"\n{CYAN}{BOLD}{'═' * 60}{RESET}")
    print(f"{CYAN}{BOLD}  {title}{RESET}")
    print(f"{CYAN}{BOLD}{'═' * 60}{RESET}")


def main() -> int:
    print(f"\n{BOLD}Meeting AI Platform — Validation de l'Infrastructure{RESET}")
    print(f"Démarré le : {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    results: list[CheckResult] = []

    # ─── Vérification de la disponibilité des services ────────────────────────
    print_section("1. Disponibilité des Services Docker")
    for svc in SERVICES:
        r = check_http(svc["name"], svc["url"])
        print_result(r)
        results.append(r)

    # ─── Vérification des endpoints API critiques ──────────────────────────────
    print_section("2. Endpoints API Critiques")
    for check in API_CHECKS:
        r = check_api_key(check["name"], check["url"], check["expected_key"])
        print_result(r)
        results.append(r)

    # ─── Résumé final ──────────────────────────────────────────────────────────
    total   = len(results)
    ok      = sum(1 for r in results if r.success)
    failed  = total - ok
    pct     = round(ok / total * 100) if total > 0 else 0

    print_section(f"Résumé : {ok}/{total} ({pct}%) services opérationnels")

    if failed == 0:
        print(f"\n  {GREEN}{BOLD}🎉 TOUTE L'INFRASTRUCTURE EST OPÉRATIONNELLE{RESET}\n")
    else:
        print(f"\n  {YELLOW}{BOLD}⚠️  {failed} service(s) non disponible(s){RESET}")
        print(f"  Vérifiez que 'docker compose up -d' s'est bien exécuté.\n")
        for r in results:
            if not r.success:
                print(f"  {RED}→ {r.name} : {r.detail}{RESET}")
        print()

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
