# Optional web and browser tool

Install this only when you want web search or a browser check. It runs separately, so ordinary chat and coding do not keep a browser process in memory.

```sh
cd browser
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m playwright install chromium
```

The browser helper is already installed in this checkout's `browser/.venv`. From a Cenere coding-terminal session, you can request web search or local page inspection directly; the agent invokes the helper when needed. You can also run commands with `!` and confirm them at the prompt:

```text
! python3 /path/to/cenere-ai/browser/cenere_browser.py --search "Rust axum latest docs"
! python3 /path/to/cenere-ai/browser/cenere_browser.py --url http://127.0.0.1:3000 --screenshot /tmp/site.png
```

The browser utility uses a headless Playwright Chromium instance by default. Web search retrieves Bing results through Jina Reader because direct automated search requests may be blocked; search queries are sent to those services. It can attach to a user-launched Chrome with `--cdp http://127.0.0.1:9222`; for agent requests, set `CENERE_CDP_URL=http://127.0.0.1:9222` before starting Cenere. Only expose a CDP endpoint on localhost; it grants broad control over that browser session. Browser checks run on demand and should not run concurrently with model fine-tuning if memory pressure is high.
