# strategies/paaf

PAAF Framework v0.1.1（Context Framework；无 Market State 算法）

```text
Domain → Interface → Engine → Strategy → Detector
```

```text
paaf/
├── domain.py              # Session / MarketState / Context（Semantic Layer）
├── metadata.py
├── config.py
├── base_detector.py
├── registry.py
├── paaf_strategy.py
├── adapters/
│   └── vnpy_adapter.py
├── engines/
│   ├── context_engine.py  # update → freeze → publish；恒 UNKNOWN
│   ├── signal_engine.py
│   ├── risk_engine.py
│   ├── execution_engine.py
│   └── logger.py
└── detectors/
```

冻结：

- MarketState: `UNKNOWN` `TREND` `RANGE`（一级语义）
- Session: `DAY` `NIGHT` `UNKNOWN`
- Direction: `LONG` `SHORT` `NONE`
- Signal.confidence 默认 `1.0`
- Context 发布后只读；Detector 经 Registry 插件式接入
- Spec: `docs/specs/CONTEXT_ENGINE_SPEC.md`（Accepted）
