# Greenfield vs. Brownfield

In AI-assisted development, the split looks like this:

**Greenfield with AI tools** means pointing an agent at an empty directory and asking it to build something. The model picks the stack, the structure, and the conventions, often leaning on whatever is most common in its training data. There's nothing in the repository for it to conflict with, so it rarely gets things "wrong" in a way that's immediately visible. This is the scenario most vendor demos show: a working app from a prompt in a few minutes.

**Brownfield with AI tools** means dropping an agent into an existing codebase and asking it to make a change. Now the model has to figure out how this particular system is organized, which patterns the team actually uses versus the ones it would default to, where the change belongs, and what else depends on the code it's about to touch. The repository is full of context that the model doesn't have unless it goes and reads it, and the quality of the result depends heavily on whether it does.

The practical differences, restated:

- **Greenfield feels fast but hides the risk.** The agent will happily make dozens of architectural decisions in seconds, and because nothing pushes back, you won't notice the questionable ones until later. The freedom that makes greenfield demos impressive is the same thing that lets a model lay down a foundation you'll be living with for years. Strong, explicit direction up front matters more here than it looks like it does.

- **Brownfield is slower per change because context gathering is the work.** A good agentic session on an existing codebase spends most of its tokens reading, searching, and tracing before it writes anything. Teams that skip this and ask for the edit directly tend to get code that compiles, looks plausible, and quietly violates the way the rest of the system works. Tools like project-level instruction files, conventions documents, and well-structured repositories exist mostly to make this phase cheaper and more reliable.

- **The skills the human needs differ.** In greenfield, your leverage is in specification: describing the architecture you want, the constraints, and the conventions, so the model doesn't invent them. In brownfield, your leverage is in review and scoping: knowing the codebase well enough to tell when the model has missed something, keeping changes small enough to verify, and insisting on tests that capture current behavior before anything is modified. Brownfield is where "I don't know this code well enough to evaluate the output" becomes a real problem, because the model will not tell you when it has misunderstood the system.

The reason this distinction matters for evaluating the tools: a model's raw coding ability shows up in greenfield, but its usefulness on a real team shows up in brownfield, and the two are not the same measurement. An assistant can be excellent at generating a clean new service and still be a liability when asked to extend a fifteen-year-old monolith, because the second task is mostly about reading and restraint rather than generation. Most of the work most engineers do is the second kind.