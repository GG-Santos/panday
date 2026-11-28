# Panday

**Turn the way you work into skills your AI can reuse.**

You finally get your AI assistant to produce the report, review, or summary you wanted. Next week, you explain the same process again. Panday helps you turn that useful routine into a reusable skill—and gives you the tools to find, check, improve, and organize skills as your needs grow.

![An illustrated workbench with reusable idea cards, a magnifying glass, tools, and connected pieces](assets/panday-workbench.png)

**12 focused skills. Use one when you need it, or combine them into a workflow.**

[Install Panday](#install-panday) · [Choose a skill](#choose-the-right-skill) · [Explore all 12](#the-12-panday-skills) · [Questions](#frequently-asked-questions) · [Download](https://github.com/GG-Santos/panday/releases/latest)

## Project description

A skill is a set of reusable instructions and supporting materials for an AI assistant. Think of it as a recipe: it explains what to do, what ingredients are needed, what a good result looks like, and what to do when something is missing.

For example, a weekly update skill might turn your notes into a consistent report with achievements, blockers, and next steps. A meeting skill might extract decisions without inventing owners or deadlines. A review skill might check a document against your team's own checklist.

Panday helps you build and maintain those recipes. You describe the work in ordinary language; your assistant uses the appropriate Panday skill to guide the process.

- **Keep what works.** Capture a successful conversation or recurring task as a skill you can use again.
- **Start with something useful.** Search for existing skills before building another one.
- **Know what you are adding.** Review a downloaded skill's instructions, permissions, and supporting files.
- **Improve with a clear target.** Repair mistakes, add a capability, or compare different ways of completing the same task.
- **Organize growing workflows.** Combine overlapping skills or connect independent ones without losing their roles.
- **Understand your tools.** Produce readable skill summaries and prepare packages for another supported assistant.

Panday is useful for writers, researchers, operations teams, project leads, and anyone who repeatedly asks an AI assistant to follow a particular process. You do not need to write code to describe a workflow. Initial setup still depends on how your assistant supports local skills.

## Install Panday

### 1. Choose how you want to use Panday

**For everyday use, start with the skills.** Download the [latest release](https://github.com/GG-Santos/panday/releases/latest), extract the ZIP, and open its `skills` folder. Each `panday-*` folder is a separate skill. You can start with one or install all 12.

Add the selected folders to the skill directory supported by your AI assistant, following that assistant's installation instructions. Keep each complete folder together: its instructions can depend on the included references, templates, and scripts. Reload the assistant if its installation process requires it.

Panday is a skill collection, not a separate chat application. Your assistant supplies the conversation, model, tools, and access to your files. A host that cannot load skill folders will need a supported integration before these skills can be used as intended.

**The command-line helper is optional.** It is useful for people who want repeatable package checks, local discovery, evaluation reports, or automation. Installing it does not automatically activate the skills in your assistant.

### 2. Try a small, real task

Start with something you already understand, such as a recurring report or a checklist you use every week:

> Use $panday-create to turn this weekly update process into a reusable skill. The report should include achievements, blockers, and next steps. Ask for missing information instead of making it up.

Provide an example of the input and a result you consider good. Real examples help your assistant distinguish your preferences from assumptions.

The `$panday-create` spelling is an invocation example. Your assistant may expose skills through a picker, slash command, or another convention; use the equivalent selection in your host.

### 3. Review the result, then try it

Read the proposed instructions, check that they describe your process, and try the resulting skill on another representative input. When something goes wrong, retain the input and output: they give Fix or Evaluate a concrete starting point.

You do not have to run every Panday skill in order. Use Create to make something new, Inspect to examine something unfamiliar, or Fix to address a specific problem.

## Choose the right skill

| What you want to do | Start here |
| --- | --- |
| Find a skill that already does the job | [Discover](#discover--find-a-useful-starting-point) |
| Turn a process, document, or conversation into a reusable skill | [Create](#create--make-your-good-process-reusable) |
| Understand whether a downloaded skill raises concerns | [Inspect](#inspect--understand-a-skill-before-trusting-it) |
| Test a skill or make sense of its results | [Evaluate](#evaluate--find-out-how-well-a-skill-works) |
| Repair a skill that keeps getting something wrong | [Fix](#fix--repair-a-skill-that-misses-the-mark) |
| Add a selected skill to a destination | [Install](#install--add-the-skill-you-selected) |
| Create a readable overview of a skill | [Card](#card--make-a-skill-easy-to-understand) |
| Give a working skill a new capability | [Augment](#augment--add-something-useful) |
| Merge overlapping skills into one | [Synthesize](#synthesize--combine-skills-without-losing-their-value) |
| Improve a working skill for a specific task | [Optimize](#optimize--find-a-better-way-to-do-the-job) |
| Make independent skills work together | [Connect](#connect--build-a-workflow-between-skills) |
| Prepare a skill for another supported assistant | [Migrate](#migrate--prepare-a-skill-for-another-assistant) |

## The 12 Panday skills

Each skill below has its own purpose, personality, and visual identity. Select one section to understand the value it brings, then open its full instructions for the complete workflow.

### Discover — find a useful starting point

<div align="center"><img src="assets/../skills/panday-discover/assets/panday-discover-small.svg" alt="Panday Discover icon" width="72" height="72"></div>

**Look for a suitable existing skill before spending time building one.** Discover turns your task into a focused search and helps compare the candidates it finds.

Use it when you know the outcome you want but do not know which skill to choose. Give it the task, your assistant or environment, and any constraints—such as local-only processing or an approved source list.

> Use $panday-discover to find a skill for turning meeting notes into action items. I want clear owners and deadlines, and it should flag missing details.

**You get:** a shortlist with source links, an explanation of the fit, and relevant limitations or unanswered questions. If no candidate is suitable, that is a useful result too.

Discover helps you choose; it does not automatically install a result. Popularity and a convincing description are not substitutes for inspecting the actual package.

[Open Discover's instructions](skills/panday-discover/SKILL.md)

---

### Create — make your good process reusable

<div align="center"><img src="assets/../skills/panday-create/assets/panday-create-small.svg" alt="Panday Create icon" width="72" height="72"></div>

**Turn a recurring task, a useful conversation, or a document into a skill.** Create helps identify the repeatable method and express it as clear instructions with the supporting materials it needs.

Use it when you keep explaining the same process or want to share a dependable workflow. Supply examples, a checklist, a document, or the conversation that captured the method. Explain what a good result must include and what the assistant should never assume.

> Use $panday-create to turn this onboarding checklist into a skill. It should prepare a personalized first-week plan and flag any missing information about the new hire.

**You get:** a skill package with a defined purpose, actionable steps, expected outputs, appropriate resources, and planned test cases. The amount of supporting material should follow the task's needs.

Create should resolve important gaps rather than hide them in vague instructions. A newly written skill is a candidate to try and evaluate, not proof that every future result will be correct.

[Open Create's instructions](skills/panday-create/SKILL.md)

---

### Inspect — understand a skill before trusting it

<div align="center"><img src="assets/../skills/panday-inspect/assets/panday-inspect-small.svg" alt="Panday Inspect icon" width="72" height="72"></div>

**Look beyond the description and examine what a skill actually asks your assistant to do.** Inspect reviews the source files for suspicious instructions, excessive permissions, unsafe dependencies, and other concerns.

Use it before adopting an unfamiliar package or after a meaningful source change. Give it the exact folder or repository location and explain the environment where you intend to use it.

> Use $panday-inspect to review this downloaded skill. Explain what files or services it wants to access, whether it sends information elsewhere, and anything I should resolve before installing it.

**You get:** findings tied to specific source material, their practical implications, and a clear account of what was and was not reviewed.

Inspection is read-only and does not run the candidate's scripts. It can identify concerns and missing evidence; it cannot guarantee that a package is harmless in every environment. A changed package needs a fresh review of the affected content.

[Open Inspect's instructions](skills/panday-inspect/SKILL.md)

---

### Evaluate — find out how well a skill works

<div align="center"><img src="assets/../skills/panday-evaluate/assets/panday-evaluate-small.svg" alt="Panday Evaluate icon" width="72" height="72"></div>

**Replace “it seems good” with examples and results you can examine.** Evaluate helps write test cases, validate evaluation files, compare outputs, interpret benchmark reports, and define quality checks.

Use it when you want to know whether a skill performs its intended task or whether a change made things better. Provide realistic inputs, your definition of success, and any existing results. Include awkward cases, not just ideal examples.

> Use $panday-evaluate to test this meeting-summary skill. Check whether it preserves decisions, avoids invented deadlines, and handles notes with no action items. Explain failures in plain language.

**You get:** appropriate cases or configuration, assessed results when execution is available, and a report separating demonstrated outcomes from missing evidence. Comparisons should account for repeated runs, incomplete results, and available time or cost data.

Writing tests is different from running them. If the required model or tools are unavailable, Evaluate should identify that gap rather than report unperformed tests as passed.

[Open Evaluate's instructions](skills/panday-evaluate/SKILL.md)

---

### Fix — repair a skill that misses the mark

<div align="center"><img src="assets/../skills/panday-fix/assets/panday-fix-small.svg" alt="Panday Fix icon" width="72" height="72"></div>

**Address a failure in what a skill is already supposed to do.** Fix starts with a reproducible problem, identifies the likely cause, and makes a targeted correction.

Use it when a skill repeatedly misses required information, violates its own instructions, produces the wrong format, or fails under a specific condition. Provide the skill, the input that exposed the problem, the actual result, and the result you expected.

> Use $panday-fix to repair this report skill. It keeps dropping unresolved blockers even though they are present in the notes. Here are two examples and the expected output.

**You get:** a supported diagnosis, a revised candidate, an explanation of the change, and regression cases that check the failure while protecting useful behavior.

Fix is for broken promises. If the existing behavior is correct and you want a new feature, choose Augment. If it works but could be more effective for a particular task, choose Optimize.

[Open Fix's instructions](skills/panday-fix/SKILL.md)

---

### Install — add the skill you selected

<div align="center"><img src="assets/../skills/panday-install/assets/panday-install-small.svg" alt="Panday Install icon" width="72" height="72"></div>

**Move a chosen skill into the right place with a clear preview of the change.** Install supports selected local packages and repository sources, including private repositories when access is available.

Use it after choosing the skill and destination. Provide the source, the specific skill if the repository contains several, and where it should be installed. You can also ask it to list skills from a supplied curated source.

> Use $panday-install to install the meeting-notes skill from this repository into my project. Show the source and destination before applying the change.

**You get:** a preview of the selected package and destination, any blockers or conflicts, and verification of the installed files after an eligible installation is applied.

The package applied must match the one reviewed for that operation. Missing authorization, unresolved findings, destination conflicts, or changed source files should be surfaced rather than silently bypassed. Private repository access uses the access available in your environment.

[Open Install's instructions](skills/panday-install/SKILL.md)

---

### Card — make a skill easy to understand

<div align="center"><img src="assets/../skills/panday-card/assets/panday-card-small.svg" alt="Panday Card icon" width="72" height="72"></div>

**Create a readable overview for the next person who encounters a skill.** Card summarizes its purpose, use, ownership, permissions, evidence, and known limitations from available sources.

Use it when sharing a skill, reviewing a collection, or refreshing documentation after a change. Supply the skill and any relevant evaluation results, ownership details, or review records.

> Use $panday-card to create a skill card for this customer-feedback workflow. Explain what it does, what information it uses, and which claims have actually been tested.

**You get:** a source-linked summary that helps readers understand the skill without first reading every file. Unknown or unverified details remain visible.

A card is a summary, not a certificate. It should not invent an owner, license, approval, or successful test result. The responsible owner can review it before publication.

[Open Card's instructions](skills/panday-card/SKILL.md)

---

### Augment — add something useful

<div align="center"><img src="assets/../skills/panday-augment/assets/panday-augment-small.svg" alt="Panday Augment icon" width="72" height="72"></div>

**Extend a working skill while keeping the behavior you already value.** Augment adds a justified capability and checks how it interacts with the existing workflow.

Use it when a skill does its current job but your needs have expanded. Describe the new capability, when it should apply, and what must remain unchanged.

> Use $panday-augment to add a customer-facing summary to this internal project-update skill. Keep the existing internal report and exclude confidential notes from the customer version.

**You get:** an expanded skill candidate, an explanation of the new behavior, and cases covering both the addition and the original capabilities.

Augment should make the addition explicit. It should not quietly redefine the skill's purpose or remove existing value to make room for the new feature.

[Open Augment's instructions](skills/panday-augment/SKILL.md)

---

### Synthesize — combine skills without losing their value

<div align="center"><img src="assets/../skills/panday-synthesize/assets/panday-synthesize-small.svg" alt="Panday Synthesize icon" width="72" height="72"></div>

**Bring overlapping skills into one coherent skill while preserving what each contributes.** Synthesize examines the source skills before deciding how their instructions and resources fit together.

Use it when two or more skills serve a related purpose and maintaining them separately creates duplication or confusion. Supply the complete source packages and describe the capabilities you want to retain.

> Use $panday-synthesize to combine these meeting-decisions and meeting-actions skills. Preserve decision rationale, action owners, missing-deadline warnings, and both output formats where useful.

**You get:** a capability map, a combined candidate where the merge is appropriate, and checks showing how the original responsibilities are covered.

The goal is a useful combined workflow, not a shorter document. Conflicting rules need an explicit resolution. If the skills have incompatible purposes or authority requirements, keeping them separate may be the better result.

[Open Synthesize's instructions](skills/panday-synthesize/SKILL.md)

---

### Optimize — find a better way to do the job

<div align="center"><img src="assets/../skills/panday-optimize/assets/panday-optimize-small.svg" alt="Panday Optimize icon" width="72" height="72"></div>

**Improve a working skill against a specific goal.** Optimize explores whether a different approach produces better results, uses less time, or reduces unnecessary work while maintaining required quality.

Use it when the skill already works but its current method may not be the best fit. Define the task, the desired improvement, and the constraints that must hold.

> Use $panday-optimize to improve this long-document review skill. I want fewer missed requirements without increasing the review time substantially. Compare the revised approach with the current one.

**You get:** a baseline, a proposed alternative, and available comparison evidence, with tradeoffs and uncertainty stated clearly.

Shorter instructions are not automatically better. An optimization that removes necessary checks or weakens the result has not met the goal. If the comparison is inconclusive, retaining the current approach is a valid outcome.

[Open Optimize's instructions](skills/panday-optimize/SKILL.md)

---

### Connect — build a workflow between skills

<div align="center"><img src="assets/../skills/panday-connect/assets/panday-connect-small.svg" alt="Panday Connect icon" width="72" height="72"></div>

**Make independent skills cooperate without merging them.** Connect defines how one skill's output becomes another's input, what information must accompany it, and when the workflow should pause.

Use it when separate capabilities would be useful together. Provide the participating skills, the desired end result, and any review or approval points.

> Use $panday-connect to connect this interview-summary skill with this project-planning skill. The planner should use confirmed findings and pause when important requirements are still unanswered.

**You get:** a workflow with clear responsibilities, input and output expectations, handoff conditions, and handling for incomplete or unsuitable results.

The connected skills retain their independent purposes. Connecting them does not automatically grant new permissions or create a background automation service; execution still depends on your assistant and available tools.

[Open Connect's instructions](skills/panday-connect/SKILL.md)

---

### Migrate — prepare a skill for another assistant

<div align="center"><img src="assets/../skills/panday-migrate/assets/panday-migrate-small.svg" alt="Panday Migrate icon" width="72" height="72"></div>

**Adapt a skill package for a supported destination without hiding what changes.** Migrate reviews the source structure and prepares the packaging and metadata required by the target host.

Use it when moving a skill between supported Codex and Claude formats. Specify the source package and destination, and identify any host-specific tools the skill relies on.

> Use $panday-migrate to prepare this skill for Claude. Preserve its instructions and resources, explain metadata changes, and flag anything that still depends on Codex-specific tools.

**You get:** a migration preview, a target package when the operation can proceed, and a report of preserved content, changes, and manual review items.

Packaging compatibility is different from identical behavior. The destination assistant may have different tools or instruction handling, so try the migrated skill in its new environment before relying on it.

[Open Migrate's instructions](skills/panday-migrate/SKILL.md)

## What this looks like in everyday work

### Turn a recurring report into a repeatable routine

Start with **Create** and provide last week's notes plus a report you liked. Use **Evaluate** on a different week to check the structure and factual accuracy. If the skill omits a required section, use **Fix** with that example. Later, use **Augment** to add a second audience or output format.

### Adopt an existing skill thoughtfully

Use **Discover** to find candidates for your task. Choose one and use **Inspect** on its exact source. Resolve any concerns, then use **Install** for the selected destination. Try it on a representative task and use **Card** to document what your team now knows about it.

### Bring several useful tools into one process

Suppose one skill summarizes research and another prepares a plan. Use **Connect** to define which findings the planner can rely on and what happens when evidence is missing. If you instead have two overlapping research skills, use **Synthesize** to explore a single combined workflow. Use **Optimize** only after you have a clear improvement target to measure.

These are examples, not a mandatory sequence. Each skill can be used independently.

## Optional command-line setup

The helper provides repeatable local checks and reports. It requires [uv](https://docs.astral.sh/uv/getting-started/installation/) and a compatible Python environment; the CLI supports Python 3.11 or newer. The Windows installer uses PowerShell. The macOS/Linux installer also needs `unzip` and either `curl` or `wget`.

### Windows

Run in PowerShell:

```powershell
irm https://raw.githubusercontent.com/GG-Santos/panday/main/install.bat -OutFile install.bat
.\install.bat
```

### macOS and Linux

```sh
curl -fsSL https://raw.githubusercontent.com/GG-Santos/panday/main/install.sh -o install.sh
sh install.sh
```

The installers currently download bundle **v1.1.2**, install the local helper, and initialize its configuration. The default package location is `%LOCALAPPDATA%\Panday` on Windows and `${XDG_DATA_HOME:-$HOME/.local/share}/panday` on macOS/Linux. Use `PANDAY_HOME` to choose another location.

Check the installation:

```sh
panday --version
panday doctor
```

To make the downloaded skill folders visible to the helper, add their location to `~/.panday/config.toml` (on Windows, `%USERPROFILE%\.panday\config.toml`):

```toml
version = 1

[registries]
paths = ["/absolute/path/to/panday/skills"]
```

Replace the example path with your actual extracted `skills` folder. This registers folders with the helper; follow your assistant's own installation process to activate the skills in chat.

Useful first commands:

```sh
panday skills list
panday skills show panday-create
panday eval validate /path/to/a/skill
```

The helper validates files, summarizes recorded results, and supports package operations. It does not run model evaluations or execute candidate skill scripts. The bundle and helper have separate version numbers, so their version strings may differ.

See the [CLI reference](cli/README.md) for commands, configuration, private-source access, reports, and exit codes. See the [lifecycle resources](lifecycle/) for optional records used when skills hand work to one another.

## Frequently asked questions

### Is Panday an AI assistant?

No. It provides skills for an assistant that supports them. Your host supplies the model, chat interface, and tools. Panday guides how that assistant carries out particular skill-related tasks.

### Do I need all 12 skills or the command-line helper?

No. Start with the skill that solves your immediate problem. Each has its own workflow and can operate without the optional shared helper. Some tasks still require files, tools, network access, or a model runner appropriate to the work.

### Do I need to know how to code?

You can describe tasks and review outputs in ordinary language. Installing skill folders may require a little familiarity with your assistant's setup. Script development, automated evaluations, and command-line integrations are more technical and optional for everyday use.

### Does installing Panday give my assistant access to everything?

Access comes from the host and the tools you authorize. A skill package does not replace those controls. Review the intended source, destination, and permissions for operations that read, write, install, or use external services.

### Are files uploaded somewhere automatically?

The local helper does not itself run model tasks. Your AI assistant's handling of the material you share depends on that host and its configuration. Discovery and repository downloads use network services when invoked; other integrations depend on the tools used in the task. Review those settings before providing sensitive material.

### Does using a skill guarantee a correct result?

No. Instructions help structure work, but results still depend on the model, inputs, tools, and task. Use representative examples, retain failures, and evaluate important changes. A structural check or a successful example is not proof of universal reliability.

### Which should I choose: Fix, Augment, or Optimize?

Choose **Fix** when promised behavior is failing. Choose **Augment** when you want an additional capability. Choose **Optimize** when the existing behavior works and you want a better method for a defined task.

### How are Synthesize and Connect different?

**Synthesize** creates one skill from multiple source skills. **Connect** keeps the skills separate and defines how they cooperate. Choose based on whether you want one combined capability or a workflow between independent capabilities.

### Will migration make a skill behave exactly the same elsewhere?

No. Migration adapts supported packaging and metadata and identifies remaining dependencies. Test the resulting skill in the destination host to assess its behavior there.

### What will it cost to use?

Your model subscription, API usage, and connected services determine execution costs. Evaluation can involve repeated model runs. Ask for a bounded test plan when cost or time matters; the helper cannot infer monetary cost when it has not been recorded.

## Help shape Panday

Found a confusing instruction, a broken installation step, or a task a skill handles poorly? [Open an issue](https://github.com/GG-Santos/panday/issues) with the skill name, what you expected, what happened, and a small example with private information removed.

For improvements, include the intended behavior and an example that would demonstrate it. Changes to instructions are easier to assess when they come with realistic cases, including failures and missing information. [Pull requests](https://github.com/GG-Santos/panday/pulls) are welcome.

Browse the [skill source](skills/), read the [CLI documentation](cli/README.md), or [download the latest packaged release](https://github.com/GG-Santos/panday/releases/latest).
