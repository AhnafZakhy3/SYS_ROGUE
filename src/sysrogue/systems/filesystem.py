"""Virtual filesystem interaction system."""

from sysrogue.core.rng import GameRNG
from sysrogue.core.state import GameState

class FilesystemSystem:
    """Manages virtual file listings, reads, and cryptanalysis."""

    @staticmethod
    def list_files(state: GameState) -> str:
        curr = state.current_node
        if not curr.files:
            return "No files found on this host filesystem."

        lines = [f"FILESYSTEM INDEX FOR {curr.id}:", "─" * 45]
        for f in curr.files.values():
            status = "[ENCRYPTED]" if f.is_encrypted else "[READABLE] "
            lines.append(f"{status}  {f.path:<32} ({f.file_type})")
        return "\n".join(lines)

    @staticmethod
    def read_file(state: GameState, filename: str) -> tuple[bool, str]:
        curr = state.current_node
        f = curr.get_file(filename)
        if not f:
            return False, f"File '{filename}' not found on {curr.id}. Use `ls` to view files."

        success, content = f.read()
        if not success:
            return False, content

        state.stats.files_inspected += 1

        # Check for key extraction in plaintext
        if "KEY_MATERIAL:" in content:
            # Extract key
            for part in content.split():
                if part.startswith("MASTER_ACCESS_KEY_"):
                    clean_key = part.strip(" ,.;:'\"")
                    if clean_key not in state.player.keyring:
                        state.player.keyring.append(clean_key)
                        state.log(f"[KEYRING] Captured security token '{clean_key}'!")

        # Check narrative flags
        if "nemesis" in f.path.lower() or "nemesis" in content.lower():
            state.narrative_flags["read_nemesis_lore"] = True

        return True, f"=== FILE: {f.path} ===\n{content}"

    @staticmethod
    def decrypt_file(state: GameState, filename: str, rng: GameRNG) -> tuple[bool, str]:
        curr = state.current_node
        f = curr.get_file(filename)
        if not f:
            return False, f"File '{filename}' not found on {curr.id}. Use `ls` to view files."

        if not f.is_encrypted:
            return True, f"File '{f.name}' is already unencrypted. Use `cat {f.name}` to read it."

        if not state.player.consume_cpu(2):
            return False, "Decryption requires at least 2 CPU cycles."

        # Modifiers
        modifier = 0
        if "crypto_accelerator" in state.player.upgrades:
            modifier += 3

        state.stats.checks_attempted += 1
        res = state.player.check_stat("reverse_eng", f.decrypt_difficulty, rng, modifier=modifier)

        if res.success:
            state.stats.checks_succeeded += 1
            state.stats.files_decrypted += 1
            f.is_encrypted = False
            f.content = f.decrypted_content or f.content

            # Cache optimizer upgrade bonus
            if "cache_optimizer" in state.player.upgrades:
                state.player.cpu = min(state.player.max_cpu, state.player.cpu + 2)
                state.log("[CACHE OPTIMIZER] +2 CPU recovered from cryptanalysis buffers.")

            # Check if this was the primary target archive
            if f.id == "target_archive" or "nexus_core" in f.name:
                state.narrative_flags["archive_decrypted"] = True
                state.log("OBJECTIVE UPDATE: Archive 'nexus_core.enc' decrypted! Now retreat to GATEWAY-01 to escape!")

            # Auto key extraction if key was inside encrypted payload
            if "KEY_MATERIAL:" in f.content:
                for part in f.content.split():
                    if part.startswith("MASTER_ACCESS_KEY_"):
                        clean_key = part.strip(" ,.;:'\"")
                        if clean_key not in state.player.keyring:
                            state.player.keyring.append(clean_key)
                            state.log(f"[KEYRING] Captured security token '{clean_key}'!")

            return True, f"DECRYPTION SUCCESSFUL!\n{res.description}\n\n=== {f.path} ===\n{f.content}"
        else:
            state.player.add_trace(5)
            state.stats.trace_generated += 5
            return False, f"DECRYPTION FAILED!\n{res.description}\nTrace +5 accrued from failed cryptanalysis."
