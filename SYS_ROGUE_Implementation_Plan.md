# SYS//ROGUE — Complete Implementation Plan

## 1. Project Overview

**SYS//ROGUE** is a terminal-based programming roguelike in which the player controls a simulated process exploring a procedurally generated computer/network environment.

The player investigates nodes, interacts with simulated files and processes, solves security challenges, installs upgrades, manages limited resources, and survives random system events. Each run is procedurally generated and uses permadeath.

The project should begin as a single-player Python CLI game and evolve toward a modular architecture that supports richer terminal presentation, save/load, content expansion, procedural generation, and a narrative layer.

## 2. Goals

### Primary goals

1. Create a fully playable terminal roguelike with a strong computer-system theme.
2. Make each run meaningfully different through procedural generation.
3. Make player decisions matter through resource management, exploration, risk, and upgrades.
4. Keep the codebase understandable enough for modification and experimentation.
5. Avoid dependence on a full game engine.
6. Provide a deterministic seed option for debugging and reproducible runs.
7. Build the architecture so later versions can add narrative, richer UI, more systems, and content without rewriting the core.

### Non-goals for the first release

- Real network scanning of external systems.
- Real password cracking against real credentials.
- Real exploitation of machines.
- Real persistence, privilege escalation, or destructive system operations.
- Multiplayer.
- Graphical UI.
- LLM integration as a core dependency.

All cyber-style mechanics are simulated entirely inside the game world.

## 3. Recommended Technology Stack

- **Language:** Python 3.12+
- **Runtime:** CPython
- **Primary UI:** `rich`
- **Optional terminal enhancements:** `textual` in a later version if desired
- **Testing:** `pytest`
- **Type checking:** `mypy` or `pyright`
- **Linting/formatting:** `ruff`
- **Configuration:** TOML/JSON where appropriate
- **Persistence:** JSON save files for v0.1; SQLite can be considered later
- **Packaging:** `pyproject.toml`

Recommended initial dependencies:

```text
rich
pytest
ruff
```

## 4. High-Level Architecture

Use a layered design:

```text
Input / CLI
    ↓
Command Parser
    ↓
Game Controller
    ↓
Game State
    ├── World / Map
    ├── Player Process
    ├── Processes / NPCs
    ├── Files / Programs
    ├── Resources
    ├── Events
    └── Progression
    ↓
Simulation Systems
    ├── Exploration
    ├── Network
    ├── Security
    ├── Investigation
    ├── Resource management
    ├── Encounters
    └── Upgrade system
    ↓
Persistence + Content Data
```

Keep UI rendering separate from game logic so the core game can be tested without terminal interaction.

## 5. Proposed Repository Structure

```text
sys-rogue/
├── pyproject.toml
├── README.md
├── LICENSE
├── .gitignore
├── requirements-dev.txt
├── src/
│   └── sysrogue/
│       ├── __init__.py
│       ├── __main__.py
│       ├── app.py
│       ├── config.py
│       │
│       ├── commands/
│       │   ├── __init__.py
│       │   ├── parser.py
│       │   ├── registry.py
│       │   └── handlers.py
│       │
│       ├── core/
│       │   ├── __init__.py
│       │   ├── game.py
│       │   ├── state.py
│       │   ├── turn.py
│       │   ├── rng.py
│       │   └── events.py
│       │
│       ├── world/
│       │   ├── __init__.py
│       │   ├── generator.py
│       │   ├── graph.py
│       │   ├── node.py
│       │   ├── connection.py
│       │   └── templates.py
│       │
│       ├── entities/
│       │   ├── __init__.py
│       │   ├── player.py
│       │   ├── process.py
│       │   ├── file.py
│       │   ├── program.py
│       │   └── account.py
│       │
│       ├── systems/
│       │   ├── __init__.py
│       │   ├── exploration.py
│       │   ├── network.py
│       │   ├── security.py
│       │   ├── filesystem.py
│       │   ├── process.py
│       │   ├── upgrades.py
│       │   ├── encounters.py
│       │   └── progression.py
│       │
│       ├── content/
│       │   ├── __init__.py
│       │   ├── nodes.json
│       │   ├── files.json
│       │   ├── programs.json
│       │   ├── upgrades.json
│       │   ├── events.json
│       │   └── narrative.json
│       │
│       ├── persistence/
│       │   ├── __init__.py
│       │   ├── save.py
│       │   └── schema.py
│       │
│       └── ui/
│           ├── __init__.py
│           ├── renderer.py
│           ├── panels.py
│           ├── prompts.py
│           └── themes.py
│
├── tests/
│   ├── test_commands.py
│   ├── test_rng.py
│   ├── test_world_generation.py
│   ├── test_player.py
│   ├── test_security.py
│   ├── test_filesystem.py
│   ├── test_upgrades.py
│   ├── test_events.py
│   └── test_persistence.py
│
├── saves/
└── docs/
    ├── implementation-plan.md
    └── requirements.md
```

## 6. Core Game Loop

The primary loop should follow this lifecycle:

```text
START GAME
   ↓
Create seed
   ↓
Generate world
   ↓
Spawn player process
   ↓
Render state
   ↓
Read command
   ↓
Parse command
   ↓
Validate action
   ↓
Execute system operation
   ↓
Advance simulation
   ↓
Resolve queued/random events
   ↓
Check victory/death conditions
   ↓
Render updated state
   ↓
Repeat
```

The game must use an explicit turn or action system. Not every command needs to consume a turn; purely informational commands can be free.

## 7. Game State Design

Create a central serializable state object containing:

- Run identifier
- World seed
- Current node
- Player process state
- Player inventory
- Installed programs/upgrades
- Known nodes
- Discovered files
- Active effects
- Security alerts
- Event queue
- Turn count
- Run statistics
- Current objective(s)
- Narrative flags
- Victory/death status

The state must be independent of the renderer.

## 8. Player Process

The player should be modeled as a process rather than a conventional RPG character.

### Base stats

```text
PROCESSING
MEMORY
NETWORK
REVERSE_ENG
STEALTH
```

Each stat should have:

- Base value
- Current modifiers
- Upgrade modifiers
- Temporary effects

Use a consistent stat check API such as:

```python
check(stat, difficulty, modifiers) -> CheckResult
```

The system must make the result explainable to the player.

Example:

```text
REVERSE_ENG check
Your value: 6
Required:   8
Penalty:    -1 from damaged debugger
Result:     FAIL
```

## 9. Resources

Use several resources with different strategic purposes.

Recommended resources:

- **CPU:** temporary execution capacity
- **Memory:** capacity for running tools/programs
- **Bandwidth:** network action resource
- **Integrity:** process health; reaching 0 causes termination
- **Trace:** how detectable the player currently is
- **Credits:** long-term purchasing currency

The exact names and values should be configurable.

## 10. World Generation

Represent the world as a graph rather than a grid.

Example:

```text
                 [GATEWAY]
                   /    \
                  /      \
             [NODE-12]  [NODE-42]
               /  \         |
              /    \        |
         [DB]      [USER] [BACKUP]
```

### Node types

Initial node templates:

- Gateway
- Workstation
- Database
- File server
- Backup server
- Admin panel
- Monitoring server
- Research server
- Unknown node

Each generated node should contain a combination of:

- Security level
- Files
- Processes
- Accounts
- Programs
- Connections
- Optional secrets
- Optional events

### Generation requirements

The generator must:

1. Produce a connected playable graph.
2. Guarantee at least one valid progression route.
3. Place the starting node safely enough to let the player learn the game.
4. Scale difficulty according to run depth.
5. Avoid impossible requirements without providing alternate routes.
6. Support a fixed seed for reproducibility.
7. Produce enough variation to prevent runs from becoming identical.

## 11. Exploration System

The player discovers nodes incrementally.

Unknown nodes should initially appear as:

```text
UNKNOWN
```

Discovery can reveal:

- Host identity
- Node type
- Security level
- Available services
- Connections
- Visible files
- Running processes

The game should distinguish between:

- Known information
- Observed information
- Inferred information
- Fully inspected information

## 12. Command System

Initial commands:

```text
help
status
look
map
scan
connect <node>
inspect <target>
ls
cat <file>
ps
run <program>
use <program>
decrypt <file>
interact <target>
upgrade
inventory
log
objective
save
load
quit
restart
```

Use a command registry so commands can be added without editing one giant `if/elif` block.

Each command should define:

- Name
- Aliases
- Usage
- Description
- Arguments
- Whether it consumes a turn
- Permission requirements
- Handler

## 13. Simulated Network System

The network system should only manipulate in-game objects.

It should simulate:

- Host discovery
- Service discovery
- Latency
- Network noise
- Firewall-like barriers
- Connection failures
- Network traces
- Temporary outages

Example:

```text
> scan

SCAN COMPLETE
────────────────────────
NODE-17   workstation   security: 3
NODE-23   database      security: 6
NODE-42   ???           security: 9
```

No actual sockets or external hosts should be accessed by the game.

## 14. Simulated Filesystem

Each node can expose a virtual filesystem.

Example:

```text
/
├── bin/
├── home/
│   └── admin/
│       ├── notes.txt
│       └── vault.enc
├── logs/
└── tmp/
```

File types should include:

- Text files
- Logs
- Configuration files
- Encrypted files
- Executable/program objects
- Evidence files
- Decoy files

The player can inspect files using game commands only.

## 15. Programs and Tools

Programs are in-game items that modify actions.

Examples:

- Packet Sniffer
- Debugger
- Memory Scanner
- Decoder
- Process Monitor
- Log Analyzer
- Network Mapper
- Sandbox
- Trace Cleaner

Programs should have:

- Memory cost
- CPU cost
- Security impact
- Trace impact
- Cooldown or availability constraints where useful
- Description
- Upgrade path

The system should support both passive and active programs.

## 16. Upgrade System

Use a modular upgrade model.

### Example upgrade categories

- Processing
- Memory
- Network
- Reverse engineering
- Stealth
- Integrity
- Utility slots

Each upgrade should contain:

```text
id
name
category
cost
requirements
effects
rarity
description
```

Use data-driven content so new upgrades can be added without changing core code.

## 17. Security System

Security is simulated and should behave predictably enough for the player to learn it.

Security mechanics:

- Access requirements
- Detection chance
- Trace accumulation
- Security alerts
- Lockouts
- Process hunters
- Decoys
- Escalating response

### Security states

```text
CLEAR
SUSPICIOUS
ALERT
LOCKDOWN
TERMINATED
```

Security transitions must be represented as state changes rather than hard-coded terminal messages.

## 18. Encounter System

Encounters are turn-based or action-triggered events.

Examples:

- Unexpected process appears.
- Firewall changes behavior.
- A suspicious admin logs in.
- A node goes offline.
- Malware-like decoy process launches.
- Backup window opens.
- Trace spikes.
- A hidden file appears.

Each encounter should have:

- Trigger condition
- Weight
- Allowed node types
- Minimum depth
- Outcomes
- Optional stat checks

## 19. Narrative System

The story should exist underneath the procedural gameplay rather than replacing it.

Use flags such as:

```text
found_unknown_process = true
read_admin_note_03 = true
met_operator_echo = true
opened_black_box = false
```

Narrative fragments can be injected into:

- Logs
- Files
- Process names
- Events
- Node metadata
- Objectives

A hidden meta-story should emerge across multiple runs.

## 20. Objective System

Objectives should provide short-term direction without dictating one solution.

Examples:

```text
PRIMARY OBJECTIVE
Locate the missing archive.

OPTIONAL OBJECTIVES
- Inspect the monitoring server.
- Recover a deleted log.
- Avoid triggering lockdown.
```

An objective can be completed by more than one route whenever practical.

## 21. Victory and Death

### Death conditions

Examples:

- Integrity reaches zero.
- Process is terminated by security response.
- Catastrophic event.
- Optional self-destruct or unstable-program outcomes.

Death should show run statistics and seed.

### Victory conditions

The first release should support a clear, finite objective, such as recovering a high-value archive and escaping through a gateway.

Later versions can add multiple endings.

## 22. Procedural Difficulty Scaling

Difficulty should scale primarily with world depth and optional risk.

Possible scaling variables:

```text
security_level
trace_pressure
resource scarcity
encounter frequency
node complexity
file obfuscation
```

Do not scale every system linearly. Some safer nodes should remain useful late in a run.

## 23. RNG Design

Use one explicit RNG object initialized from the run seed.

Do not call the global random generator all over the codebase.

Recommended pattern:

```python
rng = Random(seed)
```

Systems should receive the RNG through dependencies or a simulation context.

This allows:

- Reproducible bug reports
- Deterministic tests
- Seed sharing
- Debugging

## 24. Persistence

Implement save/load after the basic game loop works.

### Save data should include

- Version
- Seed
- Game state
- Turn count
- Player state
- World state
- Progression state
- Narrative flags

Example:

```json
{
  "save_version": 1,
  "seed": 123456,
  "turn": 47,
  "player": {},
  "world": {},
  "narrative": {}
}
```

Validate save files before loading.

## 25. UI Implementation

Use `rich` for the first release.

Target screen structure:

```text
┌──────────────────────────────────────────────────────────┐
│ SYS//ROGUE                                               │
├───────────────────────┬──────────────────────────────────┤
│ STATUS                │ CURRENT NODE                     │
│ CPU      ██████░       │ NODE-17                         │
│ MEMORY   ████░░        │ workstation                     │
│ NET      ███████       │                                  │
│ INTEGRITY ███████      │ Files: 7                         │
│ TRACE    ███░░░        │ Processes: 4                    │
├───────────────────────┴──────────────────────────────────┤
│ EVENT LOG                                                │
│ > Scanner found NODE-42                                  │
│ > Suspicious process detected                            │
├──────────────────────────────────────────────────────────┤
│ > _                                                      │
└──────────────────────────────────────────────────────────┘
```

The renderer should support both a dashboard mode and a simple text fallback.

## 26. Logging and Debugging

Use Python's `logging` module for internal diagnostics.

Separate:

- User-visible game messages
- Developer/debug logs

Provide a debug mode that can expose:

- Seed
- Internal node IDs
- Hidden values
- RNG decisions where useful
- State transitions

Debug output should never be required for normal gameplay.

## 27. Test Strategy

### Unit tests

Test each system independently:

- Command parsing
- Stat checks
- Resource changes
- RNG behavior
- World graph connectivity
- Filesystem operations
- Security transitions
- Upgrade application
- Event resolution
- Serialization/deserialization

### Integration tests

Run a full deterministic game sequence from a known seed and assert expected milestones.

### Property-style checks

Important invariants:

- Generated maps are connected.
- Resource values never become invalid unless explicitly allowed.
- Loading a saved state reproduces equivalent state.
- Every generated run has a valid progression path.

## 28. Development Phases

### Phase 0 — Project bootstrap

Deliverables:

- Repository
- `pyproject.toml`
- Virtual environment instructions
- Ruff + pytest setup
- Basic `__main__.py`
- CI-ready test command

Definition of done:

```text
python -m sysrogue
```

starts successfully.

### Phase 1 — Core game shell

Implement:

- Game state
- Turn loop
- Input loop
- Command registry
- Renderer abstraction
- Status screen

Definition of done: the player can enter commands and see persistent state changes.

### Phase 2 — Player and resources

Implement:

- Player process
- Stats
- Resources
- Integrity
- Trace
- Basic stat checks

Definition of done: actions can succeed/fail based on stats and resource costs.

### Phase 3 — Procedural world

Implement:

- Graph generation
- Node templates
- Connections
- Starting node
- Exploration state
- Seed support

Definition of done: a new connected map is generated each run.

### Phase 4 — Virtual filesystem

Implement:

- Files
- Directories
- `ls`
- `cat`
- `inspect`
- Encrypted files
- Hidden files

Definition of done: the player can investigate node contents.

### Phase 5 — Network simulation

Implement:

- `scan`
- `connect`
- Network barriers
- Latency/noise
- Discovery state

Definition of done: the player can move through generated nodes.

### Phase 6 — Programs and upgrades

Implement:

- Program definitions
- Inventory
- Program activation
- Upgrade store/loot
- Stat modifiers

Definition of done: player progression changes available strategies.

### Phase 7 — Security and encounters

Implement:

- Security states
- Detection
- Trace system
- Lockdowns
- Security events
- Random encounters

Definition of done: risky actions can trigger escalating consequences.

### Phase 8 — Objectives and victory/death

Implement:

- Primary objective
- Optional objectives
- Death handling
- Victory handling
- Run summary
- Restart flow

Definition of done: a complete run can be won or lost.

### Phase 9 — Persistence

Implement:

- Save
- Load
- Validation
- Versioning

Definition of done: quitting and resuming preserves the run.

### Phase 10 — Narrative layer

Implement:

- Narrative flags
- Story fragments
- Hidden process
- Cross-run meta narrative
- Multiple discovery paths

Definition of done: gameplay generates a coherent mystery without requiring scripted linear progression.

### Phase 11 — Balancing and polish

Tune:

- Starting resources
- Difficulty curves
- Encounter weights
- Upgrade economy
- Trace growth
- Victory frequency
- UI readability

Definition of done: repeated play produces different but generally understandable runs.

## 29. Implementation Order Within a Phase

For each phase:

1. Define data models.
2. Implement pure logic.
3. Write unit tests.
4. Connect the logic to the game controller.
5. Add UI rendering.
6. Add content data.
7. Run deterministic integration tests.
8. Playtest manually.
9. Refactor before starting the next phase.

Avoid building UI first and then coupling the logic to it.

## 30. Coding Conventions

- Prefer small modules with explicit responsibilities.
- Prefer dataclasses for state-heavy entities.
- Keep side effects at the application/persistence/UI boundaries.
- Use type hints throughout.
- Avoid global mutable state.
- Keep content in data files whenever practical.
- Keep command handlers thin.
- Use enums for finite state categories.
- Use IDs instead of object-name strings for internal references.
- Validate all external/save data.

## 31. Error Handling

Expected user errors should produce friendly messages:

```text
Unknown command: connec
Type `help` for available commands.
```

Invalid actions should not crash the run.

Unexpected programmer/runtime failures should:

1. Log the error.
2. Display a concise recovery message.
3. Preserve the save when possible.
4. Provide debug information only in debug mode.

## 32. Balancing Guidelines

The game should reward information gathering.

A risky action should generally trade one or more of:

- Time/turns
- CPU
- Memory
- Bandwidth
- Integrity
- Trace

Avoid making one stat universally dominant.

Every major obstacle should ideally have at least two approaches, such as:

```text
HIGH NETWORK + LOW STEALTH
        OR
LOW NETWORK + HIGH REVERSE_ENG
```

## 33. Example First Play Session

```text
$ python -m sysrogue

SYS//ROGUE v0.1
Seed: 582104

You are process PID 417.

> status

CPU        7
MEMORY     5
NETWORK    8
REV_ENG    3
STEALTH    6
INTEGRITY  100/100
TRACE      4/100

> scan

2 nodes discovered.

NODE-17  workstation  security 3
NODE-42  unknown      security 7

> connect NODE-17

Connected to NODE-17.

> ls

/bin
/home/admin
/logs
/tmp

> cat /home/admin/notes.txt

"Something is waking up inside NODE-42."

> scan

WARNING: unexpected traffic detected.

TRACE +7

> _
```

## 34. Definition of MVP

MVP is complete when all of the following work:

- Start a new run.
- Generate a connected procedural world.
- Explore nodes.
- Inspect a virtual filesystem.
- Manage stats/resources.
- Use at least 5 programs/tools.
- Acquire at least 10 upgrades/content items.
- Trigger security events.
- Experience permadeath.
- Complete one primary objective.
- Win and see a run summary.
- Save and load.
- Restart with a new seed.
- Run a meaningful automated test suite.

## 35. Post-MVP Expansion Roadmap

### v0.2

- More node archetypes
- More programs
- More events
- Better map display
- More objectives
- Basic achievements

### v0.3

- Multiple mission types
- Procedural factions/process personalities
- More complex security systems
- Advanced inventory
- Challenge runs

### v0.4

- Meta-progression
- Multiple endings
- Expanded narrative
- Unlockable programs
- Difficulty modes

### v1.0

- Stable content pipeline
- Strong narrative integration
- Extensive balancing
- Comprehensive test coverage
- Packaging/distribution
- Full documentation

## 36. Suggested Milestone Schedule

This schedule is sequence-based rather than time-based.

```text
M1 Bootstrap
M2 Core Loop
M3 Player Systems
M4 World Generation
M5 Virtual Filesystem
M6 Network Simulation
M7 Programs + Upgrades
M8 Security + Encounters
M9 Objectives + Death/Victory
M10 Save/Load
M11 Narrative
M12 Polish + MVP Release
```

## 37. Final Engineering Principle

The central rule for SYS//ROGUE is:

> **Simulation first, presentation second, content third.**

If the underlying simulation is deterministic, testable, modular, and fun, the terminal UI and narrative can evolve without destabilizing the project.
