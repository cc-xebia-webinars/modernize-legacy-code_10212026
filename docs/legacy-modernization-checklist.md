# Legacy Modernization Checklist

Use this checklist when you point an AI assistant at a codebase you didn't write, and again before each change you ask it to make. It follows the same order as the webinar: understand the code, protect it, change it in small steps, and know when to stop. The demos in this repository show most of these checks in action.

## Before You Change Anything

- [ ] You've run the system and seen its real output, rather than relying on its documentation. Old READMEs and comments are claims to check.
- [ ] You've scoped the assistant to the code when asking how it works, so it isn't misled by out-of-date documents.
- [ ] Every rule the assistant reports comes with a `file:line` citation, and you've opened a sample of them to confirm they say what it claims.
- [ ] You've checked the assistant's map against something mechanical, such as an import graph, a search for callers, or a run of the code.
- [ ] You've listed what the code can't tell you, such as hard-coded customers, magic numbers, and odd fallbacks, as questions for named people in the business.
- [ ] You know who depends on the output, such as an import, a report, or another system, and exactly what format they expect.
- [ ] The reviewed findings are written down: architecture notes for people, and custom instructions for every future AI session.

## The Safety Net

- [ ] A golden master pins the system's end-to-end output, and a person reviewed it before approving it.
- [ ] Golden master files are compared byte for byte, and your version control is set not to change their line endings.
- [ ] Characterization tests pin each rule by name, including the quirks, and say so in a comment when a pinned value looks like a bug.
- [ ] Every expected value came from running the real code, not from the assistant's arithmetic or anyone's idea of what's correct.
- [ ] Money is compared exactly, never with a tolerance, because a one-cent change is the kind of break you're guarding against.
- [ ] You've used coverage to find untested branches, and you've decided which gaps matter rather than chasing a number.
- [ ] You've broken a rule on purpose and watched the tests catch it.

## Making Changes

- [ ] Each change is either a structural change or a behavior change, never both.
- [ ] The assistant plans before it edits, and you've read the plan for anything that quietly changes behavior.
- [ ] Changes are small enough to review in one sitting, with the tests run before and after each one.
- [ ] The assistant isn't allowed to edit characterization tests or approved files to make a change pass.
- [ ] Bugs found along the way are recorded as open questions, not fixed in the middle of a refactor.
- [ ] Dependency upgrades start from the deprecation warnings, change one dependency at a time, and finish with warnings treated as errors.

## Rewrites and Strangler Figs

- [ ] New code sits behind a seam, such as a router or a facade, that can send one slice of work to it and move it back in one change.
- [ ] A parallel run compares the old and new code on real data before any slice moves, and it reports every disagreement.
- [ ] A person decides what to do about each disagreement, and the decision is written down with its evidence.
- [ ] Translations to another language or framework are checked the same way: the old system's recorded inputs and outputs are the test.
- [ ] There's a plan for deleting the legacy code once nothing routes to it.

## Knowing the Limits

- [ ] You let the assistant work freely where a mistake is caught quickly, such as reading code, drafting tests, and making changes under a strong test suite.
- [ ] You step in when the evidence shows a behavior change, when the assistant wants to change a test, or when a change touches a contract with another system.
- [ ] Code that works, rarely changes, and carries an external contract is left alone unless there's a reason to change it, and scoped instructions tell the assistant so.
- [ ] Approvals stay on for terminal commands and file edits, and the people approving them read what they're approving.
