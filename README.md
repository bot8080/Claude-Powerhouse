# ⚡ Claude-Powerhouse

A professional-grade collection of **MCP Servers** and **Claude Skills** designed to push the boundaries of Agentic AI. This suite transforms Claude from a chat assistant into a powerhouse of financial analysis and project management.

---

## 🏗️ Project Structure

```text
Claude-Powerhouse/
├── mcps/                   # Model Context Protocol Servers
│   └── market-intelligence  # Flagship: US/India/CA Financial Intelligence
├── skills/                 # Custom Claude.ai Skills (.skill)
│   ├── ai-project-setup    # Automate project knowledge base audits
│   └── prompt-improver     # Professional precision prompt engineering
└── README.md
```

---

## 🔌 MCP Servers (`/mcps`)

Our flagship MCP server provides deep financial intelligence across multiple markets.

### 📈 [Market-Intelligence](./mcps/market-intelligence/)
- **8 Pro Tools:** Multi-market resolution, technical analysis, scoring, and smart money tracking.
- **Multi-Market:** Native support for **US (NASDAQ/NYSE)**, **India (NSE/BSE)**, and **Canada (TSX)**.
- **Scoring Engine:** 4-pillar quantitative scoring (Valuation, Quality, Momentum, Risk).
- **Setup:**
  ```bash
  cd mcps/market-intelligence
  uv sync
  ```
  [View Market-Intelligence Documentation](./mcps/market-intelligence/README.md)

---

## 🧠 AI Skills (`/skills`)

Extend Claude.ai's core behavior with installable `.skill` files. These trigger automatically based on your natural language intent.

| Skill | Purpose |
|---|---|
| **[AI Project Setup Kit](./skills/ai-project-setup-kit/)** | Audit and build Claude Project knowledge bases instantly. |
| **[Prompt Improver](./skills/prompt-improver/)** | Professional-quality prompt rewriting using Anthropic's methodology. |

### 🛠️ How to Install Skills
1. Download the `.skill` file from the relevant folder.
2. Open **Claude.ai → Settings → Skills**.
3. Click **Install Skill** and upload the file.

---

## 🚀 Getting Started

To explore everything in this repository:

```bash
git clone https://github.com/[YOUR-USERNAME]/Claude-Powerhouse.git
cd Claude-Powerhouse
```

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](./LICENSE) file for details.

---

> [!NOTE]
> *This repository is built for personal and professional use. Always verify financial data before making investment decisions.*
