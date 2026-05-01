# Phase 6 Change Log — LangGraph Agents (Individual)

**Tarih:** 2026-04-29  
**Phase:** 06 — LangGraph Agents (Individual)  
**Durum:** Kod tarafı tamamlandı, doğrulandı ve GSD summary/verification/tracking güncellemesine hazırlandı.

## Kısa Özet

Bu phase’de Apex’in tekil agent katmanı kuruldu:

- LangGraph `AgentState` kontratı eklendi.
- Technical Agent için RSI, MACD, Bollinger, SMA ve EMA hesaplayan indicator modülü eklendi.
- 4 async agent node eklendi:
  - Technical Agent
  - Fundamental Agent
  - Risk Agent
  - Portfolio Manager
- LLM çağrıları LangSmith’te agent ve ticker metadata’sı ile izlenebilir hale getirildi.
- Agent usage tracking için `AnalysisTurnSummary` ve `UsageTracker` eklendi.
- Pre/post analysis security hook’ları eklendi.
- Tool boundary için Pydantic `TradeDecisionInput` şeması eklendi.
- Phase 6 unit testleri eklendi ve kalite kapıları çalıştırıldı.

## Commit’ler

| Commit | Amaç |
|---|---|
| `b1edb06` | AgentState ve technical indicator helper’larını ekledi |
| `315fef6` | 4 async agent node ve LangSmith trace config akışını ekledi |
| `a80006f` | Usage tracker ve Phase 6 unit test başlangıcını ekledi |
| `f26432d` | Pre/post analysis hook sistemini ekledi |
| `3cabf0d` | `TradeDecisionInput` Pydantic tool schema’sını ekledi |
| `b0a7204` | Ruff/typecheck kalite düzeltmelerini yaptı |
| `b64883b` | Post-analysis confidence gate’i anlamlı threshold’a bağladı |

## Değişen / Eklenen Dosyalar

### Agent Package

#### `src/apex/agents/state.py` *(yeni)*

**Ne yapar:** LangGraph node’ları arasında taşınan ortak state kontratını tanımlar.

Alanlar:

- `ticker`
- `market_data`
- `technical_analysis`
- `fundamental_analysis`
- `risk_assessment`
- `portfolio_decision`
- `errors`
- `compaction_applied`
- `usage`

**Neden böyle:** Phase 7’de `StateGraph` kurulurken tüm node’ların aynı TypedDict üzerinden konuşması gerekiyor. `errors` alanı agent hatalarının workflow’u kırmadan taşınmasını sağlar; `compaction_applied` Phase 7 context compaction için hazırlandı.

#### `src/apex/agents/indicators.py` *(yeni)*

**Ne yapar:** Technical Agent’ın kullandığı saf indicator hesaplamalarını içerir.

Eklenen fonksiyonlar:

- `calculate_rsi`
- `calculate_macd`
- `calculate_bollinger_bands`
- `calculate_sma`
- `calculate_ema`
- `closing_prices`

**Neden böyle:** Indicator hesapları LLM’den bağımsız ve deterministik olmalı. Bu dosya pandas `Series` üretir; böylece hem test edilebilir hem de agent prompt’una son değer snapshot’ı verilebilir.

#### `src/apex/agents/_common.py` *(yeni)*

**Ne yapar:** Agent node’ları arasında paylaşılan küçük helper’ları içerir.

Öne çıkanlar:

- `append_error`
- `llm_trace_config`
- `signal_from_text`
- `confidence_from_text`
- `merge_usage`
- `decision_from_parts`

**Neden böyle:** 4 agent aynı LLM response parsing, LangSmith config ve usage merge mantığını kullanıyor. Kopya kod yerine küçük ortak helper kullanıldı.

#### `src/apex/agents/technical.py` *(yeni)*

**Ne yapar:** Technical Agent node’u.

Akış:

1. `market_data` içinden close fiyatlarını çıkarır.
2. RSI, MACD, Bollinger, SMA ve EMA hesaplar.
3. Indicator snapshot’ını LLM’e yorumlatır.
4. `technical_analysis` partial state update’i döndürür.
5. Hata olursa exception yükseltmek yerine `errors` listesine ekler.

LangSmith metadata:

```python
config={
    "run_name": "technical_agent",
    "metadata": {"ticker": ticker, "agent": "technical_agent"},
}
```

#### `src/apex/agents/fundamental.py` *(yeni)*

**Ne yapar:** Fundamental Agent node’u.

Şimdilik full RAG pipeline yok; planlandığı gibi `retrieve_fundamental_context()` MVP stub döndürür. LLM bu context’i analiz edip BUY/SELL/HOLD + confidence yorumuna çevirir.

**Neden stub:** Full RAG Phase 10’a defer edildi. Phase 6 sınırı tekil agent node kontratını kurmak.

#### `src/apex/agents/risk.py` *(yeni)*

**Ne yapar:** Risk Agent node’u.

Hesaplanan metrikler:

- volatility
- max drawdown
- Sharpe ratio stub

LLM bu metrikleri risk değerlendirmesine çevirir. Ayrıca deterministic `_risk_score_from_metrics()` ile `risk_score` üretilir.

#### `src/apex/agents/portfolio_manager.py` *(yeni)*

**Ne yapar:** Technical, fundamental ve risk çıktılarından final `portfolio_decision` üretir.

Davranış:

- LLM’den BUY/SELL/HOLD + confidence ister.
- Eğer LLM sinyal parse edilemezse çoğunluk/fallback olarak HOLD’a döner.
- Risk score confidence üzerinde hafif penalty olarak kullanılır.

**Neden böyle:** Phase 6’da workflow assembly yok; Portfolio Manager tek başına çağrılabilir bir supervisor node olarak hazırlandı.

#### `src/apex/agents/usage_tracker.py` *(yeni)*

**Ne yapar:** Agent çağrılarının token/cost/error/timing özetini tutar.

Eklenenler:

- `AnalysisTurnSummary`
- `UsageTracker`

`UsageTracker` toplamları ve agent bazlı kırılımı döndürür.

#### `src/apex/agents/hooks.py` *(yeni)*

**Ne yapar:** 3 katmanlı güvenlik mimarisinin pre/post hook bölümünü uygular.

Pre-hook:

- Ticker whitelist kontrolü
- Prompt injection pattern scan
- Budget snapshot kontrolü

Post-hook:

- `portfolio_decision` var mı kontrol eder
- `TradeDecisionInput` ile schema validation yapar
- Confidence threshold uygular
- Reasoning içinde instruction hierarchy violation pattern’lerini arar

**Önemli düzeltme:** İlk implementasyonda confidence gate `MIN_CONFIDENCE=0.0` ile fiilen no-op olacaktı. Review sonrası `HOLD_CONFIDENCE_THRESHOLD` kullanılarak düşük confidence output’lar gerçekten engellenir hale getirildi.

#### `src/apex/agents/tool_schemas.py` *(yeni)*

**Ne yapar:** Tool boundary için Pydantic şeması.

`TradeDecisionInput` alanları:

- `ticker`
- `signal: Signal`
- `confidence: 0.0–1.0`
- `reasoning`
- `risk_score: 0.0–1.0`

**Neden böyle:** Agent output’u downstream tool/workflow katmanına geçmeden önce tip ve sınır validasyonundan geçer.

#### `src/apex/agents/__init__.py`

Güncellendi:

- Agent node’ları package seviyesinde export edildi.
- Hook’lar, schema ve usage tracker export listesine eklendi.

Örnek:

```python
from apex.agents import technical_agent, pre_analysis_hook, TradeDecisionInput
```

### Service Layer

#### `src/apex/services/llm_client.py`

Güncellendi:

- `LLMClient.generate()` imzasına `config: RunnableConfig | None` eklendi.
- `OpenAIClient.generate()` bu config’i `ChatOpenAI.ainvoke()` çağrısına geçirir.
- `FakeLLMClient.generate()` aynı imzayı destekler.

**Neden:** LangSmith trace metadata’sını agent node’larından provider abstraction’ı bozmadan geçirmek için.

### Tests

#### `tests/unit/test_agents_phase6.py` *(yeni)*

Eklenen test kapsamı:

- Indicator fonksiyonları beklenen key/series üretir.
- 4 agent node partial state update döndürür.
- LangSmith config metadata’sında doğru `agent` isimleri taşınır.
- `UsageTracker` toplamları doğru hesaplar.
- Pre-hook unknown ticker ve prompt injection’ı bloklar.
- `TradeDecisionInput` confidence sınırlarını enforce eder.
- Post-hook düşük confidence’ı reddeder, geçerli output’u normalize eder.

## Doğrulama

Çalıştırılan komutlar:

```bash
uv run ruff check src tests
uv run mypy src/apex/agents src/apex/services/llm_client.py tests/unit/test_agents_phase6.py
uv run pytest -q --tb=short
uv run python -c "from langgraph.graph import StateGraph; from apex.agents.state import AgentState; ..."
graphify update .
```

Sonuç:

- Ruff: geçti
- Targeted mypy: geçti
- Pytest: `23 passed, 1 skipped`
- Phase 6 smoke verification: geçti
- Graphify: güncellendi (`533 nodes`, `920 edges`, `44 communities`)

## Bilinen Sınırlar / Deferred

- Full workflow assembly Phase 7’ye bırakıldı.
- PostgreSQL checkpoint saver Phase 7’ye bırakıldı.
- Agent decision persistence Phase 7’de yapılacak.
- Full RAG pipeline Phase 10’a bırakıldı.
- Live OpenAI/LangSmith trace doğrulaması credential gerektirdiği için local smoke ile sınırlı kaldı.

## Sonraki Phase’e Hazırlık

Phase 7 artık şu hazır kontratları kullanabilir:

- `AgentState`
- `technical_agent`
- `fundamental_agent`
- `risk_agent`
- `portfolio_manager`
- `pre_analysis_hook`
- `post_analysis_hook`
- `TradeDecisionInput`
- `UsageTracker`

Bu parçalar `StateGraph` içinde wiring yapılmaya hazır.
