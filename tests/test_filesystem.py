import unittest
from sysrogue.core.rng import GameRNG
from sysrogue.core.state import GameState
from sysrogue.entities.file import VirtualFile
from sysrogue.entities.player import PlayerProcess
from sysrogue.systems.filesystem import FilesystemSystem
from sysrogue.world.node import NetworkNode

class TestFilesystemSystem(unittest.TestCase):
    def setUp(self):
        self.state = GameState(seed=12345)
        node = NetworkNode(id="TEST-01", name="Test Workstation", node_type="workstation")
        node.files["/home/user/notes.txt"] = VirtualFile(
            id="f1",
            name="notes.txt",
            path="/home/user/notes.txt",
            content="TOP SECRET: KEY_MATERIAL: MASTER_ACCESS_KEY_0x99AAFF",
        )
        node.files["/home/user/secret.enc"] = VirtualFile(
            id="f2",
            name="secret.enc",
            path="/home/user/secret.enc",
            content="ENCRYPTED CONTENT",
            is_encrypted=True,
            decrypted_content="PLAINTEXT REVEALED",
            decrypt_difficulty=5,
        )
        self.state.nodes["TEST-01"] = node
        self.state.current_node_id = "TEST-01"

    def test_list_and_read_plaintext(self):
        listing = FilesystemSystem.list_files(self.state)
        self.assertIn("notes.txt", listing)

        success, content = FilesystemSystem.read_file(self.state, "notes.txt")
        self.assertTrue(success)
        self.assertIn("TOP SECRET", content)
        # Verify key was extracted to player keyring
        self.assertIn("MASTER_ACCESS_KEY_0x99AAFF", self.state.player.keyring)

    def test_read_encrypted_fails_before_decrypt(self):
        success, content = FilesystemSystem.read_file(self.state, "secret.enc")
        self.assertFalse(success)
        self.assertIn("encrypted", content.lower())

    def test_decrypt_flow(self):
        rng = GameRNG(9999)
        # Give high reverse_eng to ensure success
        self.state.player.reverse_eng = 10
        success, msg = FilesystemSystem.decrypt_file(self.state, "secret.enc", rng)
        self.assertTrue(success)

        # Now reading succeeds
        read_success, read_content = FilesystemSystem.read_file(self.state, "secret.enc")
        self.assertTrue(read_success)
        self.assertIn("PLAINTEXT REVEALED", read_content)

if __name__ == "__main__":
    unittest.main()
