"""Deterministic Random Number Generator (RNG) wrapper for SYS//ROGUE."""

import random
from typing import Sequence, TypeVar

T = TypeVar("T")

class GameRNG:
    """Explicit seed-based RNG wrapper passed to simulation systems."""

    def __init__(self, seed: int | None = None) -> None:
        if seed is None:
            seed = random.SystemRandom().randint(100_000, 999_999)
        self.seed = int(seed)
        self._rng = random.Random(self.seed)

    def randint(self, a: int, b: int) -> int:
        return self._rng.randint(a, b)

    def uniform(self, a: float, b: float) -> float:
        return self._rng.uniform(a, b)

    def random(self) -> float:
        return self._rng.random()

    def choice(self, seq: Sequence[T]) -> T:
        if not seq:
            raise IndexError("Cannot choose from an empty sequence")
        return self._rng.choice(seq)

    def sample(self, population: Sequence[T], k: int) -> list[T]:
        return self._rng.sample(population, k)

    def shuffle(self, seq: list[T]) -> None:
        self._rng.shuffle(seq)

    def d20(self) -> int:
        """Helper for standard d20 checks."""
        return self._rng.randint(1, 20)
