"""Simulated virtual filesystem file entity."""

from dataclasses import dataclass, field
from typing import Any

@dataclass
class VirtualFile:
    id: str
    name: str
    path: str
    file_type: str = "text"  # text, log, config, encrypted, archive
    content: str = ""
    is_encrypted: bool = False
    is_hidden: bool = False
    decrypted_content: str = ""
    decrypt_difficulty: int = 5
    key_required: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def read(self) -> tuple[bool, str]:
        """Returns (success, content_or_error_message)."""
        if self.is_encrypted:
            return False, f"File '{self.name}' is encrypted. Decryption required (use `decrypt {self.name}`)."
        return True, self.content

    def decrypt(self, check_success: bool) -> tuple[bool, str]:
        if not self.is_encrypted:
            return True, f"File '{self.name}' is not encrypted."
        if check_success:
            self.is_encrypted = False
            self.content = self.decrypted_content or self.content
            return True, f"Decryption successful. Contents of '{self.name}' are now plaintext."
        return False, f"Decryption failed for '{self.name}'. Reverse-engineering check did not pass."
