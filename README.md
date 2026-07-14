# vnpy 商品期货离线回测项目

基于 [vnpy](https://github.com/vnpy/vnpy) / `vnpy_ctastrategy` 搭建的商品期货 CTA 策略离线回测框架，
离线历史数据来自天勤量化(TQSDK)，下载的是**原始无复权分月合约**（非天勤自带的 `KQ.m@` 后复权主连）。

本项目当前仅覆盖**离线回测**，不包含实盘/仿真交易网关（CTP 等）配置。

## 目录结构

```
data/tq/{prefix}/          天勤离线数据落盘目录（prefix 如 rb, hc, m, MA, TA）
  {prefix}_{yymm}.parquet    分月合约原始 OHLCV（无复权），如 rb_2410.parquet
  rollover_map.parquet       换月映射表（回测 CbC 拼接必需）
  dominant_windows.json      两阶段下载主力 1m 窗口
  oi_daily/                  Phase-1 日频 OI（可选）
  manifest.json              1m 数据质量与元信息
  tick/                      tick 级离线数据
    {contract}_tick.parquet  如 rb2305_tick.parquet
    manifest.json            tick 元信息

tools/                     数据下载与维护脚本
  download_rb_monthly.py     分月 1m 下载器（默认两阶段 OI→主力 1m）
  download_tick_monthly.py   分月 tick 批量下载（落盘 data/tq/{prefix}/tick/）
  download_tick_streaming.py 单合约 tick 流式下载
  build_rollover_map.py      换月映射生成（回测仅需 --map-only）
  check_all_data_quality.py  全品种数据质量审计
  rollover_rules.py          交割月白名单、换月切点规则
  tq_parquet_io.py           1m parquet schema
  tq_tick_io.py              tick parquet schema
  tq_paths.py                数据目录路径约定

scripts/
  tq_data_loader.py          CbC 分月 raw + rollover_map -> vnpy BarData（无复权）
  run_backtest.py            组装 BacktestingEngine 并跑回测

strategies/
  template_strategy.py       CtaTemplate 空骨架策略（无交易逻辑，供二次开发）
```

## 环境准备

本项目默认使用仓库根目录下的 **`.venv`** 虚拟环境。`.vscode/settings.json` 已配置
`python.terminal.activateEnvironment`，在 Cursor 中打开集成终端时会自动激活 `.venv`。

首次克隆或依赖变更后执行：

```powershell
# 若 .venv 不存在则创建
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
copy .env.example .env
# 编辑 .env，填入 TQ_USER / TQ_PASSWORD（天勤账号）
```

验证虚拟环境（终端提示符前应出现 `(.venv)`）：

```powershell
python --version
python -c "import vnpy, vnpy_ctastrategy, tqsdk; print('ok')"
```

若终端未自动激活，在 Cursor 命令面板执行 **Python: Select Interpreter**，
选择 `.venv\Scripts\python.exe`，然后新建终端或 **Developer: Reload Window**。

## 三步走：下载数据 -> 生成换月表 -> 回测

### 1. 下载分月合约（原始无复权）

默认 **两阶段**：日 OI 建换月表 → 仅下主力段 1m（自动生成 `rollover_map.parquet`）。

```powershell
# 螺纹钢 2021~2026（默认两阶段）
.venv\Scripts\python.exe tools\download_rb_monthly.py -s SHFE.rb -y 2021 2026

# 传统全量 1m（每合约约交割月前 365 天起）
.venv\Scripts\python.exe tools\download_rb_monthly.py -s SHFE.rb -y 2021 2026 --phase full

# 其他品种示例
.venv\Scripts\python.exe tools\download_rb_monthly.py -s DCE.m -y 2021 2026
.venv\Scripts\python.exe tools\download_rb_monthly.py -s CZCE.MA -y 2021 2026
```

数据落盘在 `data/tq/{prefix}/`（如 `data/tq/rb/rb_2410.parquet`）；OI 侦察在 `oi_daily/`。

常用参数：
- `--phase oi` / `--phase 1m`：只跑 Phase-1 或 Phase-2
- `-u / --update`：尾部增量更新
- `-r / --repair`：仅修复质量不合格/缺失的合约
- `--all-months`：下载全部交割月（默认仅白名单月份）

### 2. 生成换月映射表（全量模式或补图时）

两阶段下载**已自动**生成 `rollover_map.parquet`；若使用 `--phase full` 或需重建：

```powershell
# 回测主路径只需 rollover_map（+ 可选 cost_detail）；不写 continuous
.venv\Scripts\python.exe tools\build_rollover_map.py -s rb --map-only
```

生成 `data/tq/rb/rollover_map.parquet`。`scripts/tq_data_loader.py` 据此按换月日切 bar，
将各分月 raw 序列拼接成主力 1m 流（CbC，无复权）。

全量构建（去掉 `--map-only`）会额外写出 `rollover_cost_detail.parquet`（移仓滑点/手续费），
**不**再生成 `*_continuous.parquet`。
### 3. 检查数据质量（可选）

```powershell
.venv\Scripts\python.exe tools\check_all_data_quality.py
```

### 4. 运行回测

```powershell
.venv\Scripts\python.exe scripts\run_backtest.py --prefix rb --start 2023-07-01 --end 2026-06-30
```

默认使用 `strategies/template_strategy.py` 中的空骨架策略（`TemplateStrategy`），
仅用于验证数据链路可正常跑通回测，不产生任何交易信号。

## 开发自己的策略

1. 复制 `strategies/template_strategy.py` 为新文件（如 `strategies/my_strategy.py`），
   在 `on_bar` 中填充信号逻辑（可参考 vnpy 官方文档的双均线、唐奇安通道等示例）。
2. 修改 `scripts/run_backtest.py` 顶部的 `from strategies.template_strategy import TemplateStrategy`
   为你的新策略类。
3. 如需回测新品种，在 `scripts/run_backtest.py` 的 `EXCHANGE_MAP` / `CONTRACT_SPEC` 中补充
   该品种的交易所、合约乘数、最小变动价位。

### SMC + OrderFlow + VWAP 融合策略（rb）

目录：[strategies/smc_orderflow_vwap/](strategies/smc_orderflow_vwap/)

- **1H**：SMC 流动性掠夺 + 机构订单块（OB）结构过滤
- **5M**：交易日 VWAP（夜盘 21:00 重置）+ Z-Score 统计边界
- **订单流**：Tick 级 Delta；离线 1m 回测时用 K 线方向代理（精度低于 Tick）
- **Scale Out**：14:55 平半仓，余仓止损抬至保本

```powershell
# CbC 分月 raw + rollover_map，无复权
.venv\Scripts\python.exe strategies\smc_orderflow_vwap\run_backtest.py --start 2023-07-01 --end 2026-06-30
```

## 关于数据口径

- **下载**：`download_rb_monthly.py` 落盘分月原始合约（如 `rb2410`），非天勤 `KQ.m@` 后复权主连。
- **回测主路径（CbC）**：`tq_data_loader.load_bars_from_tq()` 读取分月 raw + `rollover_map.parquet`，
  按换月日拼接主力序列，**不做复权**；换月边界保留真实价格跳空。
- **单合约回测**：`load_bars_from_tq(..., yymm="2410")` 仅加载指定分月文件。
- **移仓成本**：`rollover_cost_detail.parquet` 供 `RolloverBacktestingEngine` 计入换月滑点/手续费；行情本身不做复权。
