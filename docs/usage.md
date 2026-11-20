# Run the paper-review study

Clone the GitHub project and run commands from its root. Install uv, Git, Python 3.12, an NVIDIA driver and Ollama. On Windows install Ubuntu under WSL and its bubblewrap package. A native Linux host uses the same worker protocol. The frozen Ollama manifest digest is checked by the broker. The repository lockfile pins OpenRQGM and Python dependencies. [uv](https://docs.astral.sh/uv/) · [Ollama chat API](https://docs.ollama.com/api/chat) · [bubblewrap](https://github.com/containers/bubblewrap)

~~~powershell
uv sync --locked
Copy-Item .env.example .env
wsl -d Ubuntu -- sudo apt-get install -y bubblewrap
ollama pull qwen3.5:4b
uv run --locked rqgm-study prepare
uv run --locked rqgm-study selftest
uv run --locked rqgm-study preflight
uv run --locked rqgm-study campaign
~~~

The campaign runs the pilot, chooses a budget from pilot timing, runs the confirmatory pairs and controls, freezes all endpoints, and scores the sealed test set. Restart the same command after interruption. Commit the registration for an independent replication before first inference. The publication option uses the author's configured GitHub origin and Hugging Face repository; new studies should configure their own destination. Ensure sufficient local space for full prompts and responses. The private source dataset, model traffic and inference cache remain on the host.

~~~powershell
uv run --locked rqgm-study run --stage pilot --seed 0 --arm editable --budget 64
uv run --locked rqgm-study evaluate --split pilot --name pilot-00-editable
uv run --locked rqgm-study report
uv run --locked rqgm-study serve
~~~

Open http://127.0.0.1:8765/ for a ten-second refresh of local validation metrics. GitHub Pages serves the most recently published stage. The complete model traffic also streams on the campaign terminal and to timestamped files in logs. Each result in results/runs contains the full node workspaces, source identity, choice snapshot, evaluator events, record validity, paired replay draw and cumulative compute. results/evaluations contains per-paper decisions and coverage. reports/experiments records each run. Cached deterministic requests contribute logical tokens and zero additional model-service time. A failed edit consumes that validation count's expansion opportunity. The terminal checkpoint also supplies the frozen reviewer for the endpoint.

The broker verifies the Ollama release and model digest when resuming. Stage and event-specific random streams derive from the seed and validation counter. Atomic snapshots additionally contain OpenRQGM's NumPy state, selector history and cache identities. The midpoint intervention starts immediately after the registered checkpoint. Read the preregistration before interpreting a partial cohort. [Protocol](../reports/preregistration.md) · [Analysis](../reports/summary.md)
