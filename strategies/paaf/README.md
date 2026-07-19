# strategies/paaf

PAAF Framework v0.1.0（Commit 001）

```text
Domain → Interface → Engine → Strategy → Detector
```

```text
paaf/
├── domain.py
├── metadata.py
├── config.py
├── base_detector.py
├── registry.py
├── paaf_strategy.py
├── adapters/
│   └── vnpy_adapter.py   # vn.py 边界；Domain 禁止直接 import vn.py
├── engines/
│   ├── context_engine.py
│   ├── signal_engine.py
│   ├── risk_engine.py
│   ├── execution_engine.py
│   └── logger.py
└── detectors/
```

冻结：

- MarketState: `UNKNOWN` `TREND` `RANGE`
- Direction: `LONG` `SHORT` `NONE`
- Signal.confidence 默认 `1.0`
- Detector 通过 `registry.register(...)` 插件式接入
