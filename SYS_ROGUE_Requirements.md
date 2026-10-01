# SYS//ROGUE — Software Requirements Specification

## 1. Document Purpose

This document defines the functional, non-functional, gameplay, architectural, safety, and acceptance requirements for SYS//ROGUE.

The requirements describe **what the game must do**. Implementation details are primarily covered in the separate Implementation Plan.

## 2. Product Definition

SYS//ROGUE is a single-player terminal roguelike that simulates a fictional computer/network environment. The player controls a process, explores procedurally generated nodes, interacts with simulated files and programs, manages resources, handles security reactions, collects upgrades, completes objectives, and can lose the run permanently.

## 3. Target Environment

### Required

- Windows support
- Python 3.12 or newer
- Standard terminal/PowerShell compatibility
- Keyboard-driven controls
- No graphical desktop application required

### Optional later support

- Linux
- macOS
- Rich terminal UIs beyond the initial implementation

## 4. User Roles

Only one role is required for MVP:

### Player

The player can:

- Start and restart runs
- Enter commands
- Explore the world
- Inspect simulated systems
- Use programs
- Manage resources
- Acquire upgrades
- Complete objectives
- Save/load progress
- Win or lose a run

## 5. Functional Requirements

## FR-001 — Start New Run

The system shall allow the player to start a new run.

The system shall:

- Generate a seed.
- Generate a new world from the seed.
- Create a new player process.
- Reset run-specific progression.
- Display the starting state.

## FR-002 — Seed Support

The system shall accept an optional user-supplied seed.

Using the same seed and equivalent game version shall generate the same initial procedural world.

The seed shall be displayed to the player.

## FR-003 — Game State

The system shall maintain a complete in-memory game state containing, at minimum:

- Current node
- Known nodes
- World connections
- Player stats
- Player resources
- Inventory
- Programs/upgrades
- Security state
- Turn count
- Objectives
- Narrative flags
- Run status

## FR-004 — Command Input

The system shall accept commands from the terminal.

The command parser shall:

- Recognize commands.
- Support arguments.
- Support aliases where defined.
- Validate required arguments.
- Reject malformed input without crashing.

## FR-005 — Help

The `help` command shall display available commands and usage information.

## FR-006 — Status

The `status` command shall display current player statistics and key resources.

At minimum it shall show:

- Processing
- Memory
- Network
- Reverse engineering
- Stealth
- Integrity
- Trace

## FR-007 — World Generation

The system shall generate a connected graph of nodes for every new run.

The generated world shall contain:

- A starting node
- Multiple reachable nodes
- Node types
- Security levels
- Connections
- Node contents

The system shall guarantee at least one viable progression path toward the run objective.

## FR-008 — Node Discovery

The player shall initially have incomplete knowledge of the world.

The system shall track whether a node is:

- Unknown
- Discovered
- Connected/current
- Inspected

## FR-009 — Map Display

The `map` command shall display discovered network topology.

Unknown nodes may remain hidden or abstracted.

## FR-010 — Network Scan

The `scan` command shall inspect the current node or accessible network area according to game rules.

A scan may reveal:

- Nodes
- Services
- Security information
- Processes
- Network anomalies

Scanning shall not access real external network resources.

## FR-011 — Node Connection

The `connect <node>` command shall attempt to move the player to a target node.

Connection attempts shall validate:

- Whether the node is known.
- Whether a connection exists.
- Security requirements.
- Resource requirements.
- Current lockdown/trace conditions.

## FR-012 — Virtual Filesystem

Every suitable node shall be able to contain a simulated filesystem.

The filesystem shall support:

- Directories
- Files
- Hidden files
- Encrypted files
- Logs
- Program objects

Filesystem contents shall exist only inside the game simulation.

## FR-013 — Directory Listing

The `ls` command shall list files/directories available at the current virtual filesystem location.

## FR-014 — File Reading

The `cat <file>` command shall display readable text file contents.

Unreadable/encrypted files shall provide an appropriate status message rather than crashing.

## FR-015 — Process Inspection

The `ps` command shall display processes running on the current simulated node.

Processes may include:

- System processes
- User processes
- Security processes
- Decoys
- Narrative processes

## FR-016 — Process Interaction

The player shall be able to inspect or interact with supported process objects.

Process interactions shall use game rules and shall not interact with actual operating-system processes.

## FR-017 — Programs

The system shall support installable/usable in-game programs.

Each program shall define, as appropriate:

- Unique ID
- Name
- Description
- Resource cost
- Requirements
- Effects
- Security/trace impact

At least five distinct programs shall be available in MVP.

## FR-018 — Program Execution

The player shall be able to activate compatible programs through commands.

Invalid program usage shall return a clear explanation.

## FR-019 — Inventory

The `inventory` command shall show currently owned programs, upgrades, and relevant resources.

## FR-020 — Player Stats

The player process shall have at least these base stats:

```text
Processing
Memory
Network
Reverse Engineering
Stealth
```

Stat modifiers shall be representable by temporary or permanent effects.

## FR-021 — Resource Management

The game shall track finite resources.

At minimum:

- CPU/processing capacity
- Memory
- Bandwidth/network capacity
- Integrity
- Trace

A failed resource check shall not corrupt game state.

## FR-022 — Stat Checks

Some game actions shall perform stat checks against defined difficulty values.

The result shall be one of:

- Success
- Partial success, where supported
- Failure

The player shall receive enough information to understand why the result occurred.

## FR-023 — Trace System

The game shall maintain a trace/detection value.

Actions may increase or decrease trace.

High trace shall increase the possibility or severity of security responses.

## FR-024 — Security State

The game shall model security states.

At minimum:

```text
CLEAR
SUSPICIOUS
ALERT
LOCKDOWN
TERMINATED
```

Security transitions shall occur according to defined rules.

## FR-025 — Security Events

Security events may be triggered by:

- High-risk actions
- Detection checks
- Special node conditions
- Scripted/narrative events
- Random encounters

The event system shall support multiple outcomes.

## FR-026 — Encounters

The game shall support procedural encounters.

At minimum, encounter content shall be able to:

- Change resources.
- Change trace.
- Change security.
- Reveal information.
- Spawn processes.
- Unlock/lock paths.
- Start an objective interaction.

## FR-027 — Upgrades

The player shall be able to acquire upgrades that modify capabilities.

At minimum, upgrade categories shall correspond to player stats or utility capacity.

The MVP shall include at least ten distinct upgrade/content items available through gameplay.

## FR-028 — Upgrade Requirements

Upgrades may require:

- Credits/resources
- Existing upgrades
- Minimum stats
- Specific discoveries
- Specific objectives

Invalid purchases or acquisitions shall be rejected cleanly.

## FR-029 — Objectives

Every run shall provide at least one primary objective.

The game shall optionally provide secondary/optional objectives.

Objectives shall have:

- Identifier
- Description
- Completion conditions
- Failure conditions, where applicable
- Completion state

## FR-030 — Multiple Approaches

Major progression obstacles should support multiple valid solutions where practical.

A player should not be forced into one exact command sequence for the whole game.

## FR-031 — Victory

The game shall provide at least one explicit victory condition in MVP.

On victory, the system shall:

- Stop normal run progression.
- Display a victory message.
- Display run statistics.
- Preserve the final seed.
- Offer a restart/new-run path.

## FR-032 — Permadeath

The game shall support permanent run failure.

When the player process reaches a fatal state, the run shall end and normal progression shall stop.

## FR-033 — Death Summary

After death, the game shall display:

- Cause of termination
- Seed
- Turns/actions completed
- Nodes explored
- Important discoveries
- Relevant run statistics

## FR-034 — Restart

The player shall be able to start a new run after death or victory.

A restart shall not silently reuse the previous run state unless explicitly requested via the seed feature.

## FR-035 — Save

The `save` command shall persist the current run.

The save shall contain sufficient information to recreate the current playable state.

## FR-036 — Load

The `load` command shall restore a compatible saved run.

Invalid or incompatible save files shall produce a controlled error message.

## FR-037 — Save Versioning

Save data shall include a version field.

Future versions shall be able to reject or migrate older save versions intentionally.

## FR-038 — Run Statistics

The system shall track statistics such as:

- Turns taken
- Nodes discovered
- Nodes explored
- Files inspected
- Successful checks
- Failed checks
- Trace generated
- Programs used
- Upgrades obtained
- Security incidents

Not every statistic must be displayed during the active run.

## FR-039 — Event Log

The game shall maintain a visible log of important game events.

The log shall support enough entries to understand recent actions and consequences.

## FR-040 — Narrative Flags

The game shall maintain hidden narrative state flags.

These flags shall support conditional story content without requiring the player to follow one linear path.

## FR-041 — Hidden Narrative

The system shall be capable of presenting story information through simulated artifacts such as:

- Logs
- Notes
- Process metadata
- File contents
- System messages
- Encounters

## FR-042 — Real-System Isolation

The game shall not:

- Scan real networks.
- Open arbitrary network connections as part of gameplay.
- Modify real system files as a game mechanic.
- Execute arbitrary user-provided shell commands as an in-game action.
- Control real processes based on game commands.

All hacking/cyber mechanics shall operate on fictional in-memory or saved game objects.

## FR-043 — Debug Mode

The application shall optionally support a developer/debug mode.

Debug mode may expose:

- Seed
- Hidden node data
- Internal IDs
- State transitions
- Additional logs

Debug mode shall not be required for normal play.

## FR-044 — Command Safety

Commands that could be confused with real destructive shell operations shall be interpreted only as game commands.

The game shall not silently forward arbitrary command strings to PowerShell, CMD, bash, or another system shell.

## 6. Non-Functional Requirements

## NFR-001 — Performance

Normal command processing should feel immediate on a typical modern Windows laptop/desktop for MVP-sized worlds.

## NFR-002 — Determinism

Seeded generation and simulation should be deterministic whenever the same version, seed, and command sequence are used.

## NFR-003 — Reliability

Invalid player input shall not terminate the application.

Unexpected failures should be logged and handled where recovery is possible.

## NFR-004 — Maintainability

The codebase shall use clear module boundaries and avoid a monolithic game class.

Core logic shall be testable independently of the terminal renderer.

## NFR-005 — Extensibility

Adding a new node type, upgrade, event, or command should require localized changes and should not require rewriting unrelated systems.

## NFR-006 — Testability

Core systems shall have automated unit tests.

Critical game-state transitions shall have integration tests.

## NFR-007 — Portability

The core simulation should avoid OS-specific APIs except where necessary for terminal behavior.

## NFR-008 — Resource Safety

The game shall place reasonable bounds on memory-heavy generated structures and log sizes.

## NFR-009 — Usability

Commands shall have predictable names, clear error messages, and discoverable help.

## NFR-010 — Accessibility

The game shall remain playable in a plain text terminal without relying exclusively on color.

Important information shall be conveyed with text, symbols, labels, or layout as well as optional color.

## NFR-011 — Offline Operation

The MVP shall run without requiring internet access.

## NFR-012 — Dependency Simplicity

The first release should use a small number of third-party dependencies.

## 7. Data Requirements

### Player entity

Required fields:

```text
id
pid/name
stats
resources
integrity
trace
inventory
programs
upgrades
status_effects
```

### Node entity

Required fields:

```text
id
name
type
security_level
connections
filesystem
processes
services
discovery_state
metadata
```

### Program entity

Required fields:

```text
id
name
description
costs
requirements
effects
```

### Upgrade entity

Required fields:

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

### Event entity

Required fields:

```text
id
name
conditions
weight
effects
messages
```

### Save entity

Required fields:

```text
save_version
seed
run_status
game_state
```

## 8. Command Requirements

The MVP command set shall include:

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
interact <target>
decrypt <file>
upgrade
inventory
log
objective
save
load
quit
restart
```

Aliases may be added, but each command must have one canonical name.

## 9. UX Requirements

### Startup

The player shall immediately see:

- Game title
- Version
- Seed
- Initial objective or guidance
- Initial status

### Active gameplay

The screen should expose:

- Current node
- Important player resources
- Security/trace state
- Recent event log
- Command prompt

### Failure

Errors must be understandable to a non-expert player.

Example:

```text
Unknown node: NODE-99
Use `map` to view discovered nodes.
```

### Death

Death must clearly indicate that the current run has ended.

## 10. Content Requirements

MVP content shall include at minimum:

- 6 node archetypes
- 5 usable programs
- 10 upgrades/content items
- 10 encounter/event definitions
- 1 primary objective type
- Multiple file/document types
- At least 1 hidden narrative thread
- Multiple valid progression approaches for at least some obstacles

## 11. Balancing Requirements

The game shall avoid requiring perfect knowledge to make progress.

The game should create meaningful tradeoffs among:

- Speed
- Power
- Stealth
- Information
- Resource conservation
- Risk

No single player stat should be mandatory for every viable run strategy.

## 12. Acceptance Criteria

The MVP is accepted only when all of the following are true:

### Core

- [ ] Application starts from the documented Python entry point.
- [ ] New game works.
- [ ] Seeded game works.
- [ ] Commands are parsed correctly.
- [ ] Invalid commands do not crash the game.

### World

- [ ] A connected procedural world is generated.
- [ ] The player can discover nodes.
- [ ] The player can move between reachable nodes.
- [ ] The map reflects discovered topology.

### Systems

- [ ] Player stats affect actions.
- [ ] Resources are consumed/restored correctly.
- [ ] Virtual filesystem works.
- [ ] Processes can be inspected.
- [ ] Programs can be used.
- [ ] Upgrades can be acquired.
- [ ] Security states change according to actions.
- [ ] Events can alter game state.

### Game loop

- [ ] A primary objective exists.
- [ ] The objective can be completed.
- [ ] Victory can occur.
- [ ] Death can occur.
- [ ] Permadeath ends the run.
- [ ] Run summary appears after victory/death.

### Persistence

- [ ] Save works.
- [ ] Load works.
- [ ] Corrupt/invalid saves fail gracefully.
- [ ] Save version is checked.

### Quality

- [ ] Unit tests pass.
- [ ] Integration tests pass.
- [ ] Core simulation is not dependent on UI code.
- [ ] No gameplay command executes arbitrary real shell commands.
- [ ] MVP can run offline.

## 13. Suggested Priority Levels

### P0 — Must have

Game loop, player state, command parser, world generation, exploration, filesystem, resources, security, objective, death, victory, and tests.

### P1 — Important

Programs, upgrades, save/load, event system, map visualization, statistics, and narrative flags.

### P2 — Later

Advanced narrative, multiple endings, achievements, challenge modes, richer terminal UI, meta-progression, and optional LLM-driven content.

## 14. Future Optional Requirements

These are explicitly excluded from MVP but compatible with the architecture:

- Procedural mission generation
- Faction system
- Dynamic NPC/process personalities
- Multiple endings
- Meta-progression between runs
- Challenge modifiers
- Replay viewer
- Daily seeded runs
- Local leaderboard
- Optional LLM-assisted narrative generation
- Optional graphical/TUI mode

## 15. Requirement Traceability

The implementation plan should map each functional requirement to one or more modules and tests.

Suggested traceability pattern:

```text
Requirement → System Module → Automated Test → Manual Playtest
```

Example:

```text
FR-007
  → world/generator.py
  → tests/test_world_generation.py
  → Generate 100 seeded worlds manually/automatically
```

## 16. Final Product Constraint

SYS//ROGUE must remain a **fictional simulation game**. Its cyber-security theme is for gameplay, puzzles, programming practice, and storytelling; the application must not require or encourage interacting with real unauthorized systems.
