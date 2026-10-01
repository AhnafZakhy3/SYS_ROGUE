# SYS//ROGUE

**SYS//ROGUE** is a single-player terminal cyberpunk roguelike built in pure Python 3.12+ (zero external pip dependencies).

The player assumes control of an autonomous intrusion probe (`SYS_PROBE`) navigating a procedurally generated computer/network environment. Infiltrate systems, inspect virtual filesystems, terminate surveillance daemons, acquire hardware upgrades, avoid network traces, decrypt the classified `nexus_core.enc` archive, and extract through the gateway.

---

## Quickstart

Run the game directly from the command line:

```bash
# Start a new run with a random seed
python -m sysrogue

# Start a run with a specific deterministic seed
python -m sysrogue --seed 424242

# Enable casual mode (allows non-destructive save checkpoints)
python -m sysrogue --casual

# Disable ANSI colors (plain text fallback)
python -m sysrogue --no-color
```

---

## Core Gameplay Commands

| Category | Command | Description | Action Cost |
| :--- | :--- | :--- | :--- |
| **Exploration** | `look` | Inspect current node, files, services, and running processes | Free |
| | `scan` | Scan local subnet to discover adjacent nodes | 1 Turn, 1 CPU, 1 NET |
| | `connect <node>` | Traverse to an adjacent discovered network host | 1 Turn, 1 NET |
| | `map` | View discovered network topology ASCII map | Free |
| **Filesystem** | `ls` | List files on current host filesystem | Free |
| | `cat <file>` | Read plaintext contents or extract credentials | Free |
| | `decrypt <file>` | Attempt cryptanalysis on encrypted files/archives | 1 Turn, 2 CPU |
| **Processes** | `ps` | Display process table running on current host | Free |
| | `inspect <target>` | View detailed telemetry on file, PID, or service | Free |
| | `interact <pid>` | Terminate or inject into a process to siphon credits | 1 Turn, 2 CPU |
| **Software** | `status` | View player attributes, resource pools, and trace | Free |
| | `inventory` | View installed programs, hardware patches, and keyring | Free |
| | `run <prog>` | Execute resident program (`cleaner`, `debugger`, etc.) | 1 Turn |
| | `upgrade [id]` | Browse vendor catalog or purchase an upgrade | Purchase: 1 Turn |
| **System** | `objective` | View primary and secondary mission objectives | Free |
| | `log` | View system event log history | Free |
| | `save` | Persist run state to disk | Free |
| | `load` | Restore saved run state from disk | Free |
| | `restart` | Abandon session and generate a new run | Free |
| | `quit` | Exit game | Free |

---

## Testing

Run the full automated test suite with standard library `unittest`:

```bash
python -m unittest discover tests
```
