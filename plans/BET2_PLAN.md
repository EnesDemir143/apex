# Bet 2 — Core + Agent Sistemi (Detaylı Phase Planı)

Not: `portfolio_manager` ve `portfolio_decision` isimleri karar-sentezi agent/payload adıdır; gerçek kullanıcı portföyü ya da eldeki miktar anlamına gelmez. İzlenen semboller `Watchlist` / `/api/v1/watchlist` ile temsil edilir.


> **Tarih:** 5–9 Mayıs 2026
> **Milestone:** `Bet-2: Core + Agent System`
> **Hedef:** Domain modelleri, API katmanı, LangGraph 4-agent workflow + Claw Code pattern'leri
> **Phase'ler:** Phase 5, 6, 7
> **Requirement ID'leri:** API-03..04, DB-04..05, CACHE-01..02, CORE-01..06, AGENT-01..09, SEC-01..03, RES-01..04, LSMI-01, LSMI-02, TEST-03
> **Not:** DB şeması Phase 4'te analysis_runs + agent_decisions olarak ayrıldı. Phase 7'de her agent kararı agent_decisions tablosuna persist edilecek.
> **Plan dosyaları:** 05-PLAN-01..03, 06-PLAN-01..02, 07-PLAN-01..03
> **Bağımlılık:** Bet 1 tamamlanmış olmalı

---

## Phase 5: Domain Models & Core Services (Gün 1 — Pazartesi)

**Detay:** `.planning/phases/05-domain-models-core-services/05-PLAN-01..03.md`
**Durum:** ✅ Tamamlandı — 2026-04-29
**Özetler:** `.planning/phases/05-domain-models-core-services/05-01-SUMMARY.md`, `05-02-SUMMARY.md`, `05-03-SUMMARY.md`
**Doğrulama:** `.planning/phases/05-domain-models-core-services/05-VERIFICATION.md`

**Plan 01 — Domain Models + Value Objects:**
- `src/apex/domain/`: stock.py, trade.py, analysis.py, watchlist.py, prediction_band.py
- Value objects: Signal enum (BUY/SELL/HOLD), Indicator
- Constants: TICKERS_WHITELIST, MAX/MIN_CONFIDENCE, DEFAULT_TIMEOUT, FALLBACK_CONFIDENCE
- Exceptions: ApexError, LLMBudgetExceededError, DataFetchError, AgentError, ConfigError

**Plan 02 — LLM Client + Cost Guard + DB/Cache Services:**
- `LLMClient` ABC + `OpenAIClient` (GPT-5.4 mini) + `FakeLLMClient`
- `BudgetLimiter`: günlük LLM harcama limiti, Redis tracking
- Async SQLAlchemy session factory
- Repository pattern CRUD (stock, analysis)
- Redis 8 client + cache service + rate limiter

**Plan 03 — API Routes:**
- `POST /api/v1/analyze/{ticker}` (stub response)
- `GET /api/v1/watchlist`
- Error handler + rate limit middleware

**Doğrulama:**
```bash
uv run ruff check src tests
uv run mypy src
uv run pytest -q --tb=short tests/unit tests/test_placeholder.py
uv run python -c "from apex.domain import Signal; print(Signal.BUY)"
uv run python -c "from apex.services.llm_client import FakeLLMClient; print('OK')"
# ASGI smoke: POST /api/v1/analyze/AAPL ve GET /api/v1/watchlist → 200 stub
```

---

## Phase 6: LangGraph Agents — Individual (Gün 3-4 — Çarşamba-Perşembe)

**Detay:** `.planning/phases/06-langgraph-agents-individual/06-PLAN-01..02.md`
**Durum:** ✅ Tamamlandı — 2026-04-29
**Özetler:** `.planning/phases/06-langgraph-agents-individual/06-01-SUMMARY.md`, `06-02-SUMMARY.md`
**Doğrulama:** `.planning/phases/06-langgraph-agents-individual/06-VERIFICATION.md`

**Plan 01 — 4 Agent Node + Indicators + Usage Tracker (LSMI-01):**
- `AgentState(TypedDict)`: ticker, market_data, technical_analysis, fundamental_analysis, risk_assessment, portfolio_decision, errors, compaction_applied, usage
- `src/apex/agents/indicators.py`: calculate_rsi, calculate_macd, calculate_bollinger_bands, calculate_sma, calculate_ema
- 4 async agent fonksiyonu:
  - `technical_agent(state)` → indicators hesapla → LLM yorumlasın
  - `fundamental_agent(state)` → RAG stub → LLM analiz
  - `risk_agent(state)` → volatility, max_drawdown → LLM değerlendirme
  - `portfolio_manager(state)` → tüm çıktıları BUY/SELL/HOLD + confidence'a sentezle
- `AnalysisTurnSummary` + `UsageTracker`
- **LangSmith:** Her LLM `ainvoke()` çağrısında `config={"run_name": "<agent_name>", "metadata": {"ticker": ..., "agent": ...}}` ile trace

**Plan 02 — 3-Katman Güvenlik:**
- Pre-hook: ticker whitelist, prompt injection scan, budget check
- Tool isolation: `TradeDecisionInput(BaseModel)` Pydantic schema
- Post-hook: output validation, confidence threshold, instruction hierarchy

**Doğrulama:**
```bash
uv run python -c "from apex.agents.technical import technical_agent; print('OK')"
uv run python -c "from apex.agents.hooks import pre_analysis_hook; print('OK')"
```

---

## Phase 7: Workflow Assembly & Resilience (Gün 5 — Cuma)

**Detay:** `.planning/phases/07-workflow-assembly-resilience/07-PLAN-01..03.md`
**Durum:** ✅ Tamamlandı — 2026-05-01
**Özetler:** `.planning/phases/07-workflow-assembly-resilience/07-01-SUMMARY.md`, `07-02-SUMMARY.md`, `07-03-SUMMARY.md`
**Doğrulama:** `.planning/phases/07-workflow-assembly-resilience/07-VERIFICATION.md`

**Plan 01 — StateGraph + Checkpoint + Compaction (LSMI-02):**
- `create_workflow()`: StateGraph → pre_hook → [technical, fundamental, risk] (parallel) → compact_context → portfolio_manager → post_hook → END
- PostgreSQL checkpoint saver via `AsyncPostgresSaver.setup()` — 4 tablo otomatik oluşur (Alembic'e dokunma!)
- Context compaction: token bütçesi aşılınca verbose çıktıları özetle
- Agent decision persistence: her agent kararı `agent_decisions` tablosuna yazılır (reasoning, tokens, cost, prompt_version)
- Analysis run persistence: workflow sonuçları `analysis_runs` tablosuna (UUID correlation_id)
- **LangSmith:** Workflow invocation'da `config={"run_name": f"analyze_{ticker}", "metadata": {"ticker": ..., "project": "apex"}}` — tüm agent sub-run'lar parent trace altında nested

**Plan 02 — Resilience:**
- Circuit breaker: Redis state, 3 failure → open, 60s recovery
- Retry: exponential backoff (base=1s, max=30s, max_retries=3)
- Rule-based fallback: RSI-only, confidence=0.3, source="rule_based"
- LLM response cache: Redis, hash(ticker+date+agent+prompt_version), 24h TTL

**Plan 03 — Workflow Tests + Endpoint:**
- `test_workflow.py`: FakeLLMClient ile full pipeline
- `test_circuit_breaker.py`: state transition testleri
- `test_fallback.py`: rule-based fallback doğrulama
- `POST /api/v1/analyze/{ticker}` → gerçek workflow çalıştır
- Workflow guard: max iteration/recursion limit=5, timeout=120s

**Doğrulama:**
```bash
curl -X POST http://localhost:8000/api/v1/analyze/AAPL | jq .
# {
#   "ticker": "AAPL",
#   "signal": "BUY",
#   "confidence": 0.72,
#   "agent_decisions": { "technical": {...}, "fundamental": {...}, "risk": {...} },
#   "usage_summary": { "tokens_in": 1200, "cost_usd": 0.003, ... }
# }
# agent_decisions tablosunda her agent için ayrı kayıt mevcut
# llm_usage_log tablosunda maliyet detayları + cache_hit bilgisi

# LangSmith'te trace görünür (LANGCHAIN_TRACING_V2=true ise)
uv run pytest tests/unit/test_workflow.py tests/unit/test_circuit_breaker.py tests/unit/test_fallback.py -v
uv run pytest -q  # 30 passed, 1 skipped
```

---

## ✅ Bet 2 Bitirme Kriterleri

**Durum:** Phase 5, 6 ve 7 kod + test tarafı tamamlandı. Phase 7 sonrası full pytest sonucu: `30 passed, 1 skipped`.

```bash
# 1. Analiz endpoint'i çalışıyor
curl -X POST http://localhost:8000/api/v1/analyze/AAPL | jq .
# BUY/SELL/HOLD + confidence + usage_summary

# 2. Hatalı agent varsa workflow durmadan tamamlanır
# (FakeLLMClient ile test)

# 3. Budget limiti çalışıyor
# (Günlük limiti $0.01'e düşürüp BudgetExceededError al)

# 4. Circuit breaker + fallback çalışıyor
# (3 ardışık hata → fallback RSI rules, confidence=0.3)

# 5. LangSmith'te trace'ler görünüyor
# (https://smith.langchain.com → project: apex)

# 6. Testler geçiyor
uv run pytest tests/ -v --cov=src
```
