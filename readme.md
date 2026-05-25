# NIA-OS

## Network Infrastructure Automation & Orchestration System

> **🎓 Academic Use Notice:**
> This software was developed as a Bachelor's Thesis at the **Technical University of Sofia (FDIBA)**. Permission is explicitly granted for academic evaluation and research purposes.

---

## 📖 Overview

**NIA-OS** is a modern, lightweight, and secure platform designed to simplify the management, monitoring, and automation of distributed infrastructure nodes. With a signature **"Glass OS" aesthetic**, it provides a seamless user experience that brings the feel of a native desktop operating system directly into your browser.

Unlike bloated enterprise solutions, NIA-OS prioritizes interactivity and speed. It leverages **HTMX** and **WebSockets** to deliver a highly reactive interface without the complexity of a heavy Single Page Application (SPA).

---

## 🚀 Key Features

| Feature | Description |
| --- | --- |
| **Glass OS UI** | Immersive glassmorphism with fluid animations and a macOS-style dock. |
| **HTMX-Powered** | Smooth modal interactions and live updates with near-zero frontend overhead. |
| **Agent-Based** | Dependency-free Python agent (std-lib only) – no `pip` required on target nodes. |
| **Orchestration** | Cron-like scheduler for executing tasks across specific clusters or nodes. |
| **Live Terminal** | In-browser SSH via `xterm.js` and low-latency WebSocket tunneling. |
| **Observability** | Real-time monitoring of CPU, RAM, and Disk metrics with status pulse effects. |

---

## 🛠️ Tech Stack

### Backend

* **Django 6** – The core application framework.
* **Django Channels** – Handling WebSockets for the live terminal and metrics.
* **Django Q** – Robust, asynchronous task queue for automation jobs.
* **PostgreSQL** – Relational data storage.

### Frontend

* **UI/UX** – Tailwind CSS & DaisyUI.
* **Interactivity** – HTMX.
* **Icons** – Lucide Icons.
* **Terminal** – xterm.js integration.

---

## ⚙️ Getting Started

### Prerequisites

* Python 3.14+
* [uv](https://github.com/astral-sh/uv) (Extremely fast package management)
* PostgreSQL

### Installation

1. **Clone the repository:**

```bash
git clone https://github.com/mmanchev23/nia-os.git
cd nia-os

```

2. **Setup Environment:**

NIA-OS uses `uv` to manage the environment and dependencies automatically.

```bash
uv sync
source .venv/bin/activate  # Or .venv\Scripts\activate on Windows

```

3. **Configuration:**

Configure your environment variables:

```bash
cp .env.example .env
# Edit .env and update DATABASE_URL, SECRET_KEY, etc.

```

4. **Initialize:**

```bash
python manage.py migrate
python manage.py tailwind runserver

```

5. **Start the Scheduler:**

In a separate terminal (with the venv activated):

```bash
python manage.py qcluster

```

---

## 🤖 Agent Setup

To register a new node:

1. Navigate to **Nodes** → **"Add Node"**.
2. Copy the generated one-line command.
3. Run it on your target server:
```bash
# Agent runs via Python standard library (no pip needed!)
nohup bash -c 'curl -s https://nia-os.manchev.dev/static/agent.py | python3 - https://nia-os.manchev.dev/monitoring/api/ingest/ <AGENT_KEY>' > /dev/null 2>&1 &

```


---

## 📜 License & Copyright

**All Rights Reserved.**

Copyright (c) 2026 **Martin Manchev Manchev**

> **Proprietary Notice:**
> The contents of this project are proprietary and confidential. Unauthorized copying, transferring, or reproduction of the contents of this project, via any medium, is strictly prohibited. Receipt or possession of this source code does not convey or imply any right to use it for any purpose other than for which it was provided.

*THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.*

---

**Developed by Martin Manchev Manchev**
*Bachelor's Thesis, Technical University of Sofia*
