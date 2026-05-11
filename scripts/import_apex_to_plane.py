# ruff: noqa: E501
"""Import Apex project structure into a Plane project.

Usage:
  export PLANE_API_KEY="..."
  export PLANE_BASE_URL="http://localhost:8080"
  export PLANE_WORKSPACE="enes-workspace"
  export PLANE_PROJECT_ID="f791e9c0-8833-4687-a995-99275d1b5c24"
  uv run python scripts/import_apex_to_plane.py

The script is intentionally idempotent-ish: it reuses modules by name and skips
work items with an existing matching title when the list endpoint is available.
"""

from __future__ import annotations

import html
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx


@dataclass(frozen=True)
class ModuleSpec:
    name: str
    description: str
    status: str = "planned"


@dataclass(frozen=True)
class WorkItemSpec:
    name: str
    module: str
    priority: str
    description: str
    state_group: str = "unstarted"


@dataclass(frozen=True)
class PhaseSpec:
    name: str
    module: str
    priority: str
    description: str
    state_group: str


MODULES = [
    ModuleSpec("CLI / TUI Cockpit", "Textual tabanlı terminal kokpiti, slash komutları, ticker seçimi ve kullanıcı deneyimi."),
    ModuleSpec("Local Analysis Engine", "FastAPI/DB gerektirmeden lokal analiz çalıştıran servis katmanı ve CLI entegrasyonu."),
    ModuleSpec("Agent Workflow", "LangGraph ile Technical, Fundamental, Risk ve Portfolio Manager ajan akışı."),
    ModuleSpec("Market Data & Indicators", "Alpaca/yfinance veri sağlayıcıları, OHLCV snapshot, RSI/MACD/SMA/EMA göstergeleri."),
    ModuleSpec("Reports / History / Replay", "Markdown rapor exportu, JSONL history ve kayıtlı analiz replay akışı."),
    ModuleSpec("Web Stack Legacy", "FastAPI, Streamlit, PostgreSQL, Redis ve K8s stack'inin opsiyonel/legacy olarak korunması."),
    ModuleSpec("Infrastructure & Observability", "Docker, K3s, OpenTelemetry, Grafana/Loki/Tempo ve deployment/runbook işleri."),
    ModuleSpec("Testing & Quality", "Unit, integration, e2e, smoke testleri; ruff/mypy kalite kapıları."),
]

WORK_ITEMS = [
    WorkItemSpec("TUI market panelini OHLCV ve indicator datasına bağla", "Market Data & Indicators", "high", "Seçili ticker için Open/High/Low/Close/Volume, RSI, MACD, SMA/EMA özetlerini LLM çağırmadan göster.", "completed"),
    WorkItemSpec("Terminal-native /chart ekranını tamamla", "CLI / TUI Cockpit", "high", "/chart ve /chart TICKER komutlarıyla fiyat trendi, volume özeti ve indicator paneli açılmalı.", "completed"),
    WorkItemSpec("apex analyze --save-report markdown rapor exportunu finalize et", "Reports / History / Replay", "high", "Final signal, confidence, agent bölümleri, caveat, token/cost ve disclaimer içeren sectioned rapor üret."),
    WorkItemSpec("Local history JSONL kaydını tamamla", "Reports / History / Replay", "medium", "Her analiz koşusu metadata ve sonuç özetleriyle lokal JSONL geçmişe kaydedilmeli."),
    WorkItemSpec("apex history komutunu tamamla", "Reports / History / Replay", "medium", "Önceki lokal analizleri ticker, tarih, signal ve confidence bilgisiyle listele."),
    WorkItemSpec("apex replay PATH komutunu tamamla", "Reports / History / Replay", "medium", "Kaydedilmiş bir analizi LLM/market-data tekrar çalıştırmadan render et."),
    WorkItemSpec("Web stack revival dokümanını yaz", "Web Stack Legacy", "medium", "Streamlit, FastAPI, DB/Redis, Docker/K8s ve tekrar aktive etme adımlarını dokümante et."),
    WorkItemSpec("README'de web stack'i optional/legacy olarak netleştir", "Web Stack Legacy", "medium", "İlk ekran TUI-first kalmalı; web/API/DB/K8s opsiyonel extension olarak anlatılmalı.", "completed"),
    WorkItemSpec("Local RAG Lite araştırması yap", "Agent Workflow", "low", "Fundamental Agent için Postgres/pgvector gerektirmeyen ticker-scoped markdown/plaintext knowledge yaklaşımını tasarla."),
    WorkItemSpec("Provider/model/cost ayarlarını TUI içinde görünür yap", "CLI / TUI Cockpit", "medium", "OpenAI/model, LangSmith status, token/cost bilgileri slash panel veya setup panelde görünmeli.", "completed"),
    WorkItemSpec("TUI smoke testlerini güçlendir", "Testing & Quality", "medium", "Slash-command routing, selected ticker market panel update ve chart route için manuel terminal gerektirmeyen testler ekle.", "completed"),
    WorkItemSpec("Full local analysis E2E testini ekle", "Testing & Quality", "high", "Fake LLM ve deterministic market fallback ile API/DB olmadan uçtan uca analiz testi çalışmalı."),
    WorkItemSpec("Rule-based fallback davranışını raporda görünür yap", "Agent Workflow", "medium", "Ajan pipeline bozulduğunda fallback sinyalinin confidence ve caveat bilgisi rapor/TUI'da açık yazmalı."),
    WorkItemSpec("Watchlist temelli ticker seçimini TUI'a bağla", "CLI / TUI Cockpit", "low", "AAPL, TSLA, MSFT, NVDA, GOOGL gibi seed/watchlist ticker'ları hızlı seçilebilir olmalı."),
]

PHASE_ITEMS = [
    PhaseSpec("Phase 1 — Project Skeleton & Config", "Infrastructure & Observability", "medium", "uv project setup, src layout, config, structured logging ve paket temeli tamamlandı.", "completed"),
    PhaseSpec("Phase 2 — Docker & Database Foundation", "Infrastructure & Observability", "medium", "PostgreSQL/pgvector, Redis, Grafana/Loki/Promtail, Dockerfile ve Alembic temeli tamamlandı.", "completed"),
    PhaseSpec("Phase 3 — FastAPI & Data Ingestion Core", "Market Data & Indicators", "medium", "FastAPI health/ready endpointleri, Alpaca/yfinance OHLCV clientları ve integration testleri tamamlandı.", "completed"),
    PhaseSpec("Phase 4 — Database Schema & Data Pipeline", "Market Data & Indicators", "medium", "10 tablo şema, seed tickerlar, idempotent ingestion, market calendar ve VCR testleri tamamlandı.", "completed"),
    PhaseSpec("Phase 5 — Domain Models & Core Services", "Local Analysis Engine", "medium", "Domain modelleri, LLM client abstraction, cost guard, DB/cache servisleri ve API route seamleri tamamlandı.", "completed"),
    PhaseSpec("Phase 6 — LangGraph Agents Individual", "Agent Workflow", "medium", "Technical, Fundamental, Risk ve Portfolio Manager ajan node'ları; security hooks ve usage tracking tamamlandı.", "completed"),
    PhaseSpec("Phase 7 — Workflow Assembly & Resilience", "Agent Workflow", "high", "Parallel StateGraph workflow, checkpointing, compaction, circuit breaker, retry, fallback ve workflow tests tamamlandı.", "completed"),
    PhaseSpec("Phase 8 — Streamlit Frontend", "Web Stack Legacy", "medium", "Streamlit AI market intelligence cockpit, mock data, dashboard/signals/backtest/replay/observability sayfaları tamamlandı.", "completed"),
    PhaseSpec("Phase 9 — CI/CD, K8s & Monitoring", "Infrastructure & Observability", "medium", "GitHub Actions, Docker multi-arch, K3s manifests, OTel/Tempo/Loki/Prometheus/Grafana kurulumu tamamlandı.", "completed"),
    PhaseSpec("Phase 10 — Cooldown Polish & Harden", "Testing & Quality", "medium", "RAG stub, sanitizer, DLQ, distributed lock, E2E tests, README/ADR/runbook ve restore scriptleri tamamlandı.", "completed"),
    PhaseSpec("Phase 11 — Streamlit API Wiring", "Web Stack Legacy", "medium", "Dashboard/Signals/Observability canlı FastAPI'ye bağlandı; mock fallback korundu.", "completed"),
    PhaseSpec("Phase 12 — TUI Pivot Product Cleanup", "CLI / TUI Cockpit", "high", "README/roadmap/state Bet 5 pivot ile TUI-first hale getirildi; web stack optional/legacy olarak konumlandı.", "completed"),
    PhaseSpec("Phase 13 — Local Analysis + CLI Foundation", "Local Analysis Engine", "high", "run_local_analysis, apex entrypoint, analyze command ve DB/API gerektirmeyen local path tamamlandı.", "completed"),
    PhaseSpec("Phase 14 — Textual Terminal Cockpit", "CLI / TUI Cockpit", "high", "Textual TUI cockpit, slash commands, ticker selector, progress/log/report panels ve smoke tests tamamlandı.", "completed"),
    PhaseSpec("Phase 14.1 — TUI Market Panel + Terminal Chart", "Market Data & Indicators", "high", "Market snapshot service, gerçek/fallback OHLCV paneli ve terminal-native /chart ekranı tamamlandı.", "completed"),
    PhaseSpec("Phase 15 — Reports, History, Replay", "Reports / History / Replay", "high", "Markdown report export, local JSONL history ve replay komutları tamamlanacak.", "unstarted"),
    PhaseSpec("Phase 16 — Web Stack Freeze + Revival Docs", "Web Stack Legacy", "medium", "Streamlit/FastAPI/DB/K8s optional legacy olarak işaretlenecek ve revival guide yazılacak.", "unstarted"),
    PhaseSpec("Phase 17 — Local RAG Lite + Provider Options", "Agent Workflow", "medium", "Postgres gerektirmeyen lokal knowledge, provider/model/cost seçenekleri araştırılıp uygulanacak.", "unstarted"),
    PhaseSpec("Phase 18 — Turkish Output / Localization", "CLI / TUI Cockpit", "low", "İsteğe bağlı Türkçe rapor/ajan çıktısı modu stabil workflow sonrası eklenecek.", "backlog"),
    PhaseSpec("Phase 19 — Optional Quant ML Agent + Device Selection", "Agent Workflow", "low", "Opsiyonel Quant Agent, CPU/MPS/CUDA device seçimi ve PM entegrasyonu değerlendirilecek.", "backlog"),
    PhaseSpec("v2 Backlog — Policy Engine + Broker Execution", "Agent Workflow", "low", "Policy Engine, paper/live broker execution, hardening ve advanced agent pattern işleri v2 backlog'unda tutulacak.", "backlog"),
]


PROJECT_PAGE_MD = """# Apex Overview\n\nApex, terminal odaklı çalışan local-first bir multi-agent piyasa araştırma ve hisse analiz platformudur. LangGraph ile Technical, Fundamental, Risk ve Portfolio Manager ajanlarını çalıştırarak hisseler için BUY / SELL / HOLD sinyali, confidence skoru ve gerekçeli analiz raporu üretir.\n\nAna deneyim CLI/TUI üzerindedir. FastAPI, Streamlit, PostgreSQL, Redis, observability ve K8s tarafı opsiyonel/legacy production stack olarak repoda korunur.\n\n## Ana modüller\n\n- CLI / TUI Cockpit\n- Local Analysis Engine\n- Agent Workflow\n- Market Data & Indicators\n- Reports / History / Replay\n- Web Stack Legacy\n- Infrastructure & Observability\n- Testing & Quality\n\n## Kısa hedef\n\nSunucu kurmadan lokal terminalde çalışabilen, CV/demo değeri yüksek, çok ajanlı finansal analiz deneyimi sunmak.\n"""


def load_dotenv_file(path: str = ".env.plane.local") -> None:
    """Load simple KEY=VALUE dotenv files without requiring shell-specific source syntax."""
    dotenv = Path(path)
    if not dotenv.exists():
        return
    for raw_line in dotenv.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if not value:
        raise SystemExit(f"Missing env: {name}")
    return value.rstrip("/")


def html_desc(text: str) -> str:
    return "<p>" + html.escape(text).replace("\n", "<br>") + "</p>"


class PlaneClient:
    def __init__(self) -> None:
        self.base_url = env("PLANE_BASE_URL", "http://localhost:8080")
        self.workspace = env("PLANE_WORKSPACE", "enes-workspace")
        self.project_id = env("PLANE_PROJECT_ID", "f791e9c0-8833-4687-a995-99275d1b5c24")
        self.client = httpx.Client(
            base_url=self.base_url,
            headers={"X-API-Key": env("PLANE_API_KEY"), "Content-Type": "application/json"},
            timeout=20,
        )

    def path(self, suffix: str) -> str:
        return f"/api/v1/workspaces/{self.workspace}/projects/{self.project_id}/{suffix.lstrip('/')}"

    def get_json(self, path: str) -> Any:
        r = self.client.get(path)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, dict) and "results" in data:
            return data["results"]
        return data

    def post_json(self, path: str, payload: dict[str, Any]) -> Any:
        r = self.client.post(path, json=payload)
        if r.status_code >= 400:
            print(f"POST failed {r.status_code}: {path}\n{r.text[:1000]}", file=sys.stderr)
        r.raise_for_status()
        return r.json() if r.content else {}

    def patch_json(self, path: str, payload: dict[str, Any]) -> Any:
        r = self.client.patch(path, json=payload)
        if r.status_code >= 400:
            print(f"PATCH failed {r.status_code}: {path}\n{r.text[:1000]}", file=sys.stderr)
        r.raise_for_status()
        return r.json() if r.content else {}

    def state_ids_by_group(self) -> dict[str, str]:
        states = self.get_json(self.path("states/"))
        return {s.get("group"): s.get("id") for s in states if isinstance(s, dict) and s.get("group") and s.get("id")}


def main() -> None:
    load_dotenv_file()
    plane = PlaneClient()
    print(f"Importing into {plane.base_url}/{plane.workspace}/projects/{plane.project_id}")

    existing_modules_raw = plane.get_json(plane.path("modules/"))
    existing_modules = {m.get("name"): m for m in existing_modules_raw if isinstance(m, dict)}

    module_ids: dict[str, str] = {}
    for spec in MODULES:
        current = existing_modules.get(spec.name)
        if current:
            module_ids[spec.name] = current["id"]
            print(f"= module exists: {spec.name}")
            continue
        created = plane.post_json(
            plane.path("modules/"),
            {"name": spec.name, "description": spec.description, "status": spec.status},
        )
        module_ids[spec.name] = created["id"]
        print(f"+ module created: {spec.name}")

    state_ids = plane.state_ids_by_group()
    default_state = state_ids.get("unstarted") or state_ids.get("backlog")

    existing_by_title: dict[str, dict[str, Any]] = {}
    try:
        existing_items_raw = plane.get_json(plane.path("work-items/"))
        existing_by_title = {i.get("name"): i for i in existing_items_raw if isinstance(i, dict) and i.get("name")}
    except httpx.HTTPStatusError as exc:
        print(f"! Could not list existing work items; will create without duplicate check: {exc.response.status_code}")

    def upsert_work_item(name: str, module: str, priority: str, description: str, state_group: str) -> None:
        module_id = module_ids.get(module)
        state_id = state_ids.get(state_group) or default_state
        payload: dict[str, Any] = {
            "name": name,
            "description_html": html_desc(description),
            "priority": priority,
        }
        if module_id:
            payload["module"] = module_id
        if state_id:
            payload["state"] = state_id

        existing = existing_by_title.get(name)
        if existing:
            plane.patch_json(plane.path(f"work-items/{existing['id']}/"), payload)
            print(f"= work item updated: {name} [{state_group}]")
            return
        created = plane.post_json(plane.path("work-items/"), payload)
        if isinstance(created, dict) and created.get("id"):
            existing_by_title[name] = created
        print(f"+ work item created: {name} [{state_group}]")

    for phase in PHASE_ITEMS:
        upsert_work_item(phase.name, phase.module, phase.priority, phase.description, phase.state_group)

    for item in WORK_ITEMS:
        upsert_work_item(item.name, item.module, item.priority, item.description, item.state_group)

    print("\nPages API self-host sürümünde dokümante olmayabilir. UI > Pages içine şunu kopyalayabilirsin:\n")
    print(PROJECT_PAGE_MD)


if __name__ == "__main__":
    main()
