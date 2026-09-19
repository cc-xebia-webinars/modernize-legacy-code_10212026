# Demos

These four demos follow one legacy codebase, ShipBill, a courier's monthly billing system written around 2012, from first contact to a partial rewrite. Each demo starts where the previous one leaves off, and each is self-contained, with its own copy of the code and its own `uv` project pinned to Python 3.14, so you can run any of them on its own. GitHub Copilot in Visual Studio Code is the AI tool throughout.

| # | Demo | Description | Time |
|---|------|-------------|------|
| 1 | [Read Before You Change](./01-understand-legacy/README.md) | Using Copilot to map the architecture, trace how one invoice total is calculated, and surface the questions the code can't answer, then checking its claims with a mechanical code map and turning what you learned into documentation and custom instructions. | 17 min |
| 2 | [Build the Safety Net](./02-safety-net/README.md) | A golden master that pins a whole billing month byte for byte, characterization tests written with Copilot that pin each rule by name, coverage used to find gaps, and a deliberate break to prove the net catches it. | 18 min |
| 3 | [Modernize in Small Steps](./03-small-steps/README.md) | A targeted refactor planned and made with Copilot one step at a time, and a dependency upgrade from a 2019 release of `arrow` to 1.4.0, driven by deprecation warnings and failing tests. | 17 min |
| 4 | [Strangle, Rewrite, and Know When to Stop](./04-strangler-fig/README.md) | A new pricing engine grown behind a strangler fig router, a parallel run that catches a one-cent rounding difference, a recorded decision to keep the legacy behavior, and a module that's better left alone. | 18 min |

## Getting Ready

Every demo needs these tools:

- [uv](https://docs.astral.sh/uv/getting-started/installation/) 0.11 or later. It installs Python 3.14 for you if you don't have it.
- [Visual Studio Code](https://code.visualstudio.com/) with [GitHub Copilot set up](https://code.visualstudio.com/docs/copilot/setup).

Run `uv sync` in each demo folder while you're online. After that, everything runs offline except Copilot itself and Demo 3's `uv add` step, which downloads a newer version of `arrow`.

Open each demo as its own VS Code window, for example `code demos/02-safety-net`. On macOS, install the `code` command first: open the Command Palette and run **Shell Command: Install 'code' command in PATH**. Copilot reads custom instructions, scoped instructions, and prompt files from the `.github` folder at the root of the workspace, so opening the demo folder directly gives Copilot that demo's context and nothing else.

In the Chat view, set **Session Target** to **Local**. The demos use three of the built-in agents in the agent picker in the chat input, which the trails call roles: **Ask** for questions about the code, **Plan** for planning a change before making it, and **Agent** when Copilot should edit files or run commands. Prompt files, which you run by typing `/` and the file's name, such as `/document-legacy` in Demo 1, only load in Local sessions.

### Make Sure You're in a Local Session

VS Code can run a chat on more than one agent harness, and it recommends the Copilot harness for everyday work. These demos need the Local harness, because prompt files only run in Local sessions. Both harnesses offer the **Ask**, **Agent**, and **Plan** roles, so the agent picker won't tell you which one you're on. Check the **Session Target** control instead:

1. Select **New Chat** at the top of the Chat view.
2. Open the **Session Target** control and select **Local** before you send the first prompt. A session keeps the harness it started with.
3. Type `/` in the chat input. If you see the demo's prompt files, such as `/document-legacy` in Demo 1, you're set.

If you'd rather work in the Copilot harness, VS Code's equivalent of a prompt file there is an [agent skill](https://code.visualstudio.com/docs/copilot/customization/agent-skills): a `SKILL.md` file in its own folder under `.github/skills`, such as `.github/skills/characterize/SKILL.md`, with a `name` that matches the folder and a `description`. The instructions in each prompt file work unchanged as the body of a skill.

## The Sample Data

Every demo builds a small SQLite database in its `data` folder the first time ShipBill runs. It holds eleven customers and 272 shipments across August and September 2026, generated from a fixed seed so every machine gets the same invoices. It's never committed. If a demo's data gets into a strange state, rebuild it from that demo's folder:

```
uv run sample_data.py --reset
```

Billing runs write the LedgerLink file to the demo's `out` folder, and the tests use their own in-memory database, so neither one touches the other.

## Copilot's Answers Will Vary

Copilot won't write the same tests, plans, or code for you that it wrote for us, so the trails tell you what to look for rather than what to expect word for word. Each demo starts from a finished, reviewed version of the previous demo's work, and the [reference folder](./reference/README.md) holds two versions of Demo 4's new pricing engine to compare with yours. It sits outside the demo folders on purpose, so Copilot can't find the answer while it's working.

## Using Another AI Tool

The workflow doesn't depend on Copilot. The custom instructions in each demo's `.github/copilot-instructions.md` are plain Markdown, and if you want one file that several tools read, rename it `AGENTS.md` and put it at the root of the project: Copilot, [Claude Code](https://code.claude.com/docs/en/memory), and [Cursor](https://cursor.com/docs/context/rules) all support it. The prompt files are plain Markdown too, so you can paste their text into any agent's chat or turn them into skills.
