# Phase 7 Change Log — Workflow Assembly & Resilience

**Tarih:** 2026-05-01  
**Phase:** 07 — Workflow Assembly & Resilience  
**Durum:** Kod tarafı tamamlandı, feature bazlı commit’lendi ve test/ruff/mypy kalite kapıları geçti. GSD `SUMMARY.md`, `STATE.md`, `ROADMAP.md` güncellemesi manual gate sonrasına bırakıldı.

## Kısa Özet

Bu phase’de Apex’in tekil agent node’ları tam bir LangGraph workflow’una bağlandı ve workflow’un production’a yaklaşması için resilience katmanı eklendi:

- LangGraph `StateGraph` assembly eklendi.
- Technical + Fundamental + Risk agent’ları paralel branch olarak çalışacak şekilde bağlandı.
- Branch sonuçları context compaction aşamasından geçip Portfolio Manager’a aktarılıyor.
- Portfolio Manager sonrası post-analysis hook ile final output validation çalışıyor.
- PostgreSQL checkpoint saver entegrasyonu eklendi (`AsyncPostgresSaver.setup()`).
- Parallel branch merge için `AgentState` reducer fonksiyonları eklendi.
- Redis-backed circuit breaker eklendi.
- Async exponential retry helper eklendi.
- RSI tabanlı deterministic rule-based fallback eklendi.
- Redis-backed LLM response cache eklendi.
- `/api/v1/analyze/{ticker}` endpoint’i Phase 5 stub’dan gerçek workflow çağrısına geçirildi.
- Phase 7 unit testleri eklendi.

## Commit’ler

| Commit | Amaç |
|---|---|
| `d46a709` | LangGraph workflow foundation, checkpoint saver, context compaction ve state reducer altyapısı |
| `d79c0cd` | Circuit breaker, retry, rule-based fallback ve LLM cache resilience primitive’leri |
| `f6b792b` | Analysis API’nin workflow’a bağlanması ve Phase 7 testleri |
| `6eea858` | Workflow timeout ve max-iteration guard tamamlaması |

## Değişen / Eklenen Dosyalar

### Agent Workflow

#### `src/apex/agents/workflow.py` *(yeni)*

**Ne yapar:** Apex’in Phase 6’da yazılan tekil agent node’larını tek bir LangGraph workflow’u altında toplar.

Akış:

1. `pre_hook`
2. Paralel agent branch’leri:
   - `technical`
   - `fundamental`
   - `risk`
3. `compact_context`
4. `portfolio_manager`
5. `post_hook`
6. `END`

Öne çıkan fonksiyonlar:

- `create_workflow()`
- `create_workflow_with_checkpointer(checkpointer)`
- `workflow_run_config(ticker)`
- `analyze_with_workflow(state)`
- `persist_workflow_results(session, stock_id, state)`

**Neden böyle:** Phase 6 agent’ları tek tek çalışabiliyordu; Phase 7’nin amacı bunları analiz pipeline’ı olarak birleştirmekti. Technical/Fundamental/Risk branch’leri birbirinden bağımsız olduğu için paralel edge’lerle çalışacak şekilde kuruldu.

LangSmith metadata:

```python
{
    "run_name": f"analyze_{ticker}",
    "metadata": {"ticker": ticker, "project": "apex"},
}
```

Bu sayede bir analiz çalışması LangSmith’te parent trace, agent node’ları ise child span olarak görülebilir.

#### `src/apex/agents/state.py`

Güncellendi:

- `errors` için reducer: `merge_errors`
- `usage` için reducer: `merge_usage`
- `compaction_applied` için reducer: `merge_compaction`

**Neden:** LangGraph paralel branch’lerden gelen partial state update’lerini merge ederken aynı key’e birden fazla branch yazabilir. Reducer’lar olmadan parallel execution’da state çakışması yaşanır.

#### `src/apex/agents/compaction.py` *(yeni)*

**Ne yapar:** Agent output’ları token budget’ın %80’ini aşarsa verbose alanları kısaltır ve `compaction_applied=True` set eder.

Eklenen fonksiyonlar:

- `compact_agent_context(state, token_budget=4096)`
- `_compact_payload(payload)`
- `_rough_token_count(value)`

**Neden:** Phase 7 context compaction requirement’ı için workflow içinde deterministic ve test edilebilir bir compaction seam kuruldu. LLM tabanlı summarization yerine MVP için güvenli/sade string kısaltma kullanıldı.

#### `src/apex/agents/checkpoint.py` *(yeni)*

**Ne yapar:** LangGraph PostgreSQL checkpoint saver setup’ını sağlar.

Eklenenler:

- `checkpoint_database_url()`
- `create_checkpoint_saver()` async context manager
- `setup_checkpoint_saver()`
- `close_checkpoint_saver()`

Kullanılan paketler:

- `langgraph-checkpoint-postgres`
- `psycopg`
- `psycopg-pool`
- `psycopg-binary`

Önemli davranış:

- `AsyncPostgresSaver.setup()` çağrılır.
- Checkpoint tabloları LangGraph tarafından yönetilir.
- Application Alembic migration’larına checkpoint tablosu eklenmedi.

**Neden:** Crash/retry/resume senaryoları için workflow checkpoint persistence gerekiyor. Bu schema LangGraph’ın kendi migration/setup mekanizmasına ait olduğu için app schema migration’larıyla karıştırılmadı.

#### `src/apex/agents/__init__.py`

Güncellendi:

- `create_workflow`
- `create_workflow_with_checkpointer`

package export listesine eklendi.

### Resilience Layer

#### `src/apex/agents/circuit_breaker.py` *(yeni)*

**Ne yapar:** Redis üzerinde state tutan circuit breaker implementasyonu.

Eklenenler:

- `CircuitBreaker`
- `CircuitOpenError`

State’ler:

- `CLOSED`
- `OPEN`
- `HALF_OPEN`

Davranış:

- Varsayılan `failure_threshold=3`
- Varsayılan `recovery_timeout=60`
- Başarısız çağrılar Redis counter ile takip edilir.
- Threshold aşılırsa circuit `OPEN` olur.
- Recovery süresi geçince `HALF_OPEN` denemeye izin verir.
- Başarılı çağrı circuit’i tekrar `CLOSED` yapar.

**Neden:** LLM/provider tarafında tekrarlı hata olduğunda workflow’un sürekli aynı dış bağımlılığı zorlamaması ve fallback path’e dönebilmesi gerekiyor.

#### `src/apex/agents/retry.py` *(yeni)*

**Ne yapar:** Async fonksiyonlar için exponential backoff decorator’ı sağlar.

Eklenen:

- `async_retry(max_retries=3, base_delay=1.0, max_delay=30.0)`

Backoff formülü:

```python
delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
```

**Neden:** Geçici provider/network hataları için küçük, dependency-free retry seam’i.

#### `src/apex/agents/fallback.py` *(yeni)*

**Ne yapar:** Degraded path için deterministic RSI-only fallback kararı üretir.

Davranış:

- RSI `< 30` → `BUY`
- RSI `> 70` → `SELL`
- Diğer durumlar → `HOLD`
- Confidence sabit: `0.3`
- Source: `rule_based`

**Neden:** Circuit open, budget exceeded veya LLM unavailable olduğunda sistem hâlâ düşük güvenli, açıkça fallback olarak işaretlenmiş bir analiz sonucu döndürebilmeli.

### Service Layer

#### `src/apex/services/llm_cache.py` *(yeni)*

**Ne yapar:** Redis cache üzerinden LLM response cache katmanı sağlar.

Eklenen:

- `LLMCacheService`
- `cache_key()`

Cache key girdileri:

- ticker
- trading date
- agent name
- prompt version

Hash:

```python
hashlib.sha256(raw.encode("utf-8")).hexdigest()
```

TTL:

- Varsayılan `86_400` saniye, yani 24 saat.

**Neden:** Aynı ticker/date/agent/prompt_version kombinasyonu için gereksiz LLM maliyetini azaltmak ve latency’yi düşürmek.

### API Layer

#### `src/apex/api/routes/analysis.py`

Güncellendi:

- Phase 5 stub response kaldırıldı.
- Endpoint artık `create_workflow()` ile gerçek workflow’u çağırır.
- `workflow_run_config()` ile LangSmith metadata geçirir.
- Response hâlâ `AnalysisResult` contract’ını korur.
- `summary` içine şu alanlar eklendi:
  - `usage_summary`
  - `agent_outputs`
  - `errors`

Endpoint davranışı:

- Whitelist dışı ticker → deterministic rejected response.
- Whitelist içi ticker → workflow çalışır.
- API smoke path için local synthetic OHLCV data üretilir.

**Neden synthetic data:** Phase 7’nin endpoint wiring doğrulaması dış market-data provider’ına bağımlı olmamalı. Gerçek market data ingestion zaten ayrı katmanda var; burada amaç API → workflow bağlantısını stabilize etmek.

### Dependency Changes

#### `pyproject.toml`

Eklenen runtime dependency’ler:

- `langgraph-checkpoint-postgres>=3.0.5`
- `psycopg-binary>=3.3.3`
- `psycopg-pool>=3.3.0`

#### `uv.lock`

Yeni dependency resolution lock’a yansıdı.

### Tests

#### `tests/unit/test_workflow.py` *(yeni)*

Eklenen kapsam:

- `FakeLLMClient` ile full workflow pipeline testi.
- Workflow output’unda valid `signal` ve expected `confidence` kontrolü.
- `/api/v1/analyze/AAPL` endpoint smoke testi.
- Endpoint response içinde `signal`, `confidence`, `usage_summary` kontrolü.
- LangSmith `metadata.project == "apex"` doğrulaması.

#### `tests/unit/test_circuit_breaker.py` *(yeni)*

Eklenen kapsam:

- Fake Redis ile circuit state transition testi.
- 3 hata sonrası `OPEN` state.
- `OPEN` state’te `CircuitOpenError`.
- `record_success()` sonrası `CLOSED` state.

#### `tests/unit/test_fallback.py` *(yeni)*

Eklenen kapsam:

- RSI `< 30` için `BUY` fallback.
- Confidence `0.3`.
- Source `rule_based`.

## Doğrulama

Çalıştırılan kalite kapıları:

```fish
fish -c "uv run ruff check src/apex/agents src/apex/api/routes/analysis.py src/apex/services/llm_cache.py tests/unit/test_workflow.py tests/unit/test_circuit_breaker.py tests/unit/test_fallback.py"
```

Sonuç:

- Passed

```fish
fish -c "uv run mypy src/apex/agents src/apex/api/routes/analysis.py src/apex/services/llm_cache.py"
```

Sonuç:

- `Success: no issues found in 19 source files`

```fish
fish -c "uv run pytest tests/unit/test_workflow.py tests/unit/test_circuit_breaker.py tests/unit/test_fallback.py -q"
```

Sonuç:

- `4 passed`

Full suite:

```fish
fish -c "uv run pytest -q"
```

Sonuç:

- `30 passed, 1 skipped`

Graphify update:

```fish
fish -c "graphify update ."
```

Sonuç:

- Graph rebuilt: `656 nodes`, `1143 edges`, `58 communities`

## Önemli Notlar

### Checkpoint schema app migration’larına eklenmedi

LangGraph checkpoint tabloları `AsyncPostgresSaver.setup()` ile oluşturulur. Bu nedenle Alembic tarafına checkpoint table migration’ı eklenmedi.

### Post-hook sırası bilinçli olarak Portfolio Manager sonrasında

Phase context’te “Pre-hook → parallel agents → Post-hook → Portfolio Manager” ifadesi vardı; fakat mevcut `post_analysis_hook()` implementation’ı `portfolio_decision` bekliyor. Bu yüzden workflow’da final validation olarak Portfolio Manager sonrasında çalıştırıldı.

### Fallback trading execution değildir

`rule_based_fallback()` BUY/SELL/HOLD analizi üretir; trade order veya execution üretmez. Confidence düşük ve source açıkça `rule_based` olarak işaretlenir.

### API hâlâ `AnalysisResult` döndürüyor

Endpoint contract genişletilmedi; usage ve agent detayları `summary` içine kondu. Bu sayede Phase 5 API contract’ı korunurken Phase 7 workflow output’u taşınabiliyor.

## Sonraki Phase’e Etkisi

Phase 8 Streamlit Frontend artık şunlara bağlanabilir:

- `/api/v1/analyze/{ticker}` üzerinden gerçek workflow-backed analiz sonucu
- `summary.usage_summary` ile token/cost görünürlüğü
- `summary.agent_outputs` ile agent bazlı açıklamalar
- `status=completed/degraded/rejected` ile UI state ayrımı

Phase 9 Monitoring/DevOps tarafı şunları gözlemleyebilir:

- LangSmith parent workflow trace
- Circuit breaker state ve fallback source
- LLM cache hit/miss için ileride `llm_usage_log` entegrasyon noktası

---

*Phase: 07-workflow-assembly-resilience*  
*Change log generated: 2026-05-01*
