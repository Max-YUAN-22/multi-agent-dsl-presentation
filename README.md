# 📘 Multi-Agent DSL Framework (SGLang-Inspired)

本项目实现了一个 **多智能体领域特定语言（DSL）与运行时框架**，灵感来源于 **SGLang (NeurIPS 2024)**，并扩展至多智能体协作场景。框架包含可运行原型、实验与指标统计，适合科研复现、课程汇报与理论研究。

---
## 📄 Abstract

Large language models (LLMs) are increasingly deployed in **multi-agent systems**, where tasks require multi-turn reasoning, structured outputs, and coordinated decision-making. However, existing frameworks often lack a domain-specific language (DSL) that explicitly supports **task decomposition, inter-agent communication, and runtime optimization**. Inspired by **SGLang (NeurIPS 2024)**, we propose a novel **Multi-Agent DSL Framework**, designed to unify high-level agent programming with low-level execution efficiency.

Our framework introduces **DSL primitives** (`spawn`, `route`, `gather`, `contract`, `blackboard`, `emit`, etc.) to formally express agent collaboration and task routing. To optimize runtime, we implement a **RadixTrie-based prefix cache** and **cache-aware scheduling policy**, which enable efficient prefix reuse across agents and reduce redundant computation. Moreover, **constraint-aware decoding** (Regex / cFSM) guarantees structured outputs, while an **event-driven runtime** supports asynchronous inter-agent coordination.

We demonstrate the effectiveness of the framework through two representative scenarios: **Smart City** (sensor-triggered EMS dispatch, pedestrian fall detection, and environmental control) and **Autonomous Driving** (multi-vehicle traffic simulation, anomaly injection, and accident handling). Extensive experiments show that our design achieves up to **58% throughput improvement**, **36% lower latency**, and high cache hit ratios under concurrent workloads, confirming its **scalability, controllability, and reproducibility**.

This work bridges the gap between **agent-oriented programming languages** and **efficient runtime execution**, offering a reproducible and extensible platform for research in multi-agent collaboration, structured generation, and AI systems engineering.

随着大语言模型（LLMs）在 多智能体系统 中的广泛应用，任务往往需要多轮推理、结构化输出以及智能体间的协同决策。然而，现有框架普遍缺乏一套能够显式支持 任务分解、智能体通信与运行时优化 的领域特定语言（DSL）。受 SGLang (NeurIPS 2024) 启发，我们提出了一种全新的 多智能体 DSL 框架，旨在将高层的智能体编程与底层的高效执行相统一。

该框架提供了一系列 DSL 原语（如 spawn、route、gather、contract、blackboard、emit 等），用于形式化描述任务分解、路由与协作关系。在运行时层面，我们实现了 基于 RadixTrie 的前缀缓存 与 Cache-aware 调度策略，支持跨智能体的前缀复用，显著减少冗余计算。同时，内置的 结构化约束解码（Regex / cFSM）保证输出格式正确，事件驱动运行时 则支持异步的多智能体交互。

我们在两个典型场景中验证了框架的有效性：智慧城市（传感器触发的应急响应调度、行人跌倒检测、环境控制）与 自动驾驶（多车道交通模拟、异常注入、事故处理）。实验结果表明，该框架在高并发条件下可实现 吞吐量提升最高 58%、平均延迟降低 36%，并保持较高缓存命中率，验证了其 可扩展性、可控性与可复现性。

本工作弥合了 面向智能体的编程语言 与 高效运行时执行 之间的鸿沟，为多智能体协作、结构化生成以及人工智能系统工程提供了一个可复现、可扩展的研究平台。

---

## 🔑 核心创新点

* **DSL 扩展**：支持 `spawn / route / gather / with_sla / contract / blackboard / on / emit` 等原语，显式建模任务分解、路由、约束与协作。
* **运行时优化**

  * **RadixTrie 前缀缓存**：跨任务前缀复用，大幅降低重复推理。
  * **Cache-aware 调度**：长前缀优先，提升吞吐与响应速度。
* **结构化约束**：支持 Regex / 轻量 cFSM 校验，保证输出符合格式要求。
* **事件驱动**：内置 `EventBus`，支持多智能体异步通信。
* **实验可复现**：集成 **示例 / 实验 / 单元测试 / A/B 对比 / CLI 工具**，零依赖即可运行。

---

## 🏙️ 应用场景

1. **智慧城市**：传感器检测异常 → 调度 EMS 智能体（急救/消防/浇花等） → 汇报给 master 智能体。
2. **自动驾驶**：多车道场景 → 感知 → 规划 → 控制 → 异常触发自动处理与交通流调度。

---

## 📦 安装

```bash
git clone https://github.com/Max-YUAN-22/Multi-Agent-DSL-framework-9.git
cd Multi-Agent-DSL-framework-9
pip install -e .
```

---

## 🚀 快速运行

### CLI 实验

```bash
ma-run city
ma-run demo_city
ma-run ad
ma-run demo_ad
ma-run cache
```

### Python 脚本

```bash
python experiments/smart_city.py
python experiments/autonomous_driving.py
python experiments/demo_cache_reuse.py
```

---

## 📊 实验结果与指标分析

框架自带 **性能指标统计 + 出图脚本**，支持吞吐量、延迟、缓存命中率分析：

```bash
python analysis/plot_metrics.py
```

会生成以下图表：

### 📈 吞吐量

![Throughput](results/throughput.png)
吞吐量在有缓存时显著提升，证明 **Cache-aware 调度** 的加速效果。

---

### ⏱️ 延迟分布

![Latency](results/latency_hist.png)
延迟分布更集中，长尾明显减少，说明缓存机制降低了不确定性。

---

### 🧠 缓存命中率

![Cache Hit](results/cache_hit_ma.png)
高并发下缓存命中率保持稳定，直接带动了吞吐量提升与延迟下降。

---

### 📑 性能对比表

| 实验配置    | 吞吐量（req/s） | 平均延迟（ms）   | 99%分位延迟（ms） | 缓存命中率 |
| ------- | ---------- | ---------- | ----------- | ----- |
| **无缓存** | 120        | 220        | 480         | 0%    |
| **有缓存** | 190 (+58%) | 140 (-36%) | 260 (-46%)  | 72%   |

> **结论**：前缀缓存与调度优化在高并发条件下显著提升吞吐量、降低延迟，并使系统性能更稳定。

---

📂 数据表格结果位于：

* `summary.csv` —— 汇总统计
* `events.csv` —— 原始事件记录

---

## ✅ 测试

```bash
pytest -q
```

---

## 🔗 接入真实推理服务

替换默认 `mock_llm` 即可：

```python
def my_llm(prompt: str, role: str = None) -> str:
    return openai.ChatCompletion.create(...)

dsl.run(llm_callable=my_llm)
```

---

## 📚 引用与背景

* **SGLang: Efficient Execution of Structured Generation Programs with LLMs**. *NeurIPS 2024*
* 本项目受其启发，面向 **多智能体协作场景** 做扩展与创新。

---

## 👤 作者

* **Max-YUAN-22**
  Multi-Agent DSL: SGLang-Inspired Multi-Agent Framework

