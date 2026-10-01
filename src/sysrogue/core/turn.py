"""Turn loop management and periodic state updates for SYS//ROGUE."""

from sysrogue.core.events import SecurityManager, SecurityState, EncounterManager
from sysrogue.core.rng import GameRNG
from sysrogue.core.state import GameState

class TurnManager:
    """Orchestrates turn progression, security ticks, and encounter rolls."""

    def __init__(self, rng: GameRNG) -> None:
        self.rng = rng
        self.encounter_mgr = EncounterManager(rng)

    def advance_turn(self, state: GameState, is_active_action: bool = True) -> None:
        if not is_active_action or state.run_status != "ACTIVE":
            return

        state.turn += 1
        state.stats.turns_taken += 1

        # 1. Regenerate player resources
        state.player.restore_turn_resources()

        # 2. Tick program cooldowns
        for prog in state.player.programs.values():
            if prog.cooldown_remaining > 0:
                prog.cooldown_remaining -= 1

        # 3. Tick temporary effects
        remaining_effects = []
        for effect in state.player.temporary_effects:
            duration = effect.get("duration", 1) - 1
            if duration > 0:
                effect["duration"] = duration
                remaining_effects.append(effect)
            else:
                state.log(f"Effect expired: {effect.get('name', 'Modifier')}")
        state.player.temporary_effects = remaining_effects

        # 4. Security & Trace Evaluation
        curr_security = SecurityManager.evaluate_state(state.player.trace, state.player.is_alive)
        state.security_state = curr_security

        # 5. Check Termination Conditions
        if state.player.integrity <= 0:
            state.run_status = "TERMINATED"
            state.termination_reason = "Kernel process integrity depleted to 0% (Fatal Segmentation Fault)."
            state.log("FATAL: Process integrity hit 0%. Terminated.")
            return

        if state.player.trace >= 100:
            state.run_status = "TERMINATED"
            state.termination_reason = "Process back-traced and purged by central security IDS hunter."
            state.log("FATAL: Trace reached 100%. Process terminated by remote supervisor.")
            return

        # 6. Check Active Security Reactions (Hunters on current node)
        for proc in state.current_node.processes:
            if proc.is_active and proc.is_hunter and state.security_state in (SecurityState.ALERT, SecurityState.LOCKDOWN):
                dmg = proc.security_risk * 2
                state.player.take_damage(dmg)
                state.log(f"ALERT: Hunter daemon '{proc.name}' engaged! Inflicted {dmg} integrity damage.")

        # 7. Check Post-Damage Termination
        if state.player.integrity <= 0:
            state.run_status = "TERMINATED"
            state.termination_reason = "Killed by hunter daemon."
            return

        # 8. Roll Procedural Encounter
        outcome = self.encounter_mgr.roll_encounter(state.player, state.current_node)
        if outcome:
            state.stats.encounters_survived += 1
            state.log(f"[{outcome.title}] {outcome.message}")
            if outcome.trace_change:
                state.stats.trace_generated += abs(outcome.trace_change)

        # 9. Final Security State Re-evaluation
        state.security_state = SecurityManager.evaluate_state(state.player.trace, state.player.is_alive)
        if state.player.integrity <= 0 or state.player.trace >= 100:
            state.run_status = "TERMINATED"
            state.termination_reason = "Terminated during encounter resolution."
