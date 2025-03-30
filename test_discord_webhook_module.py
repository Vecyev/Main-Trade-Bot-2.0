import unittest
import sys
import os

# Ensure the directory is in the sys.path
print("Current working directory:", os.getcwd())
print("File path:", os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from discord_webhook import DiscordWebhook

class TestDiscordWebhook(unittest.TestCase):
    def setUp(self):
        self.webhook = DiscordWebhook()

    def test_send_message(self):
        response = self.webhook.send_message("Test message from unittest", "TestBot")
        self.assertEqual(response, 204)

    def test_send_empty_message(self):
        response = self.webhook.send_message("", "TestBot")
        self.assertNotEqual(response, 204)

    def test_send_message_without_username(self):
        response = self.webhook.send_message("Test message without username")
        self.assertEqual(response, 204)

    def test_send_message_with_embed(self):
        response = self.webhook.send_message("Test message with embed", "TestBot", embeds=[{
            "title": "Test Embed",
            "description": "This is a test embed"
        }])
        self.assertEqual(response, 204)

if __name__ == '__main__':
    unittest.main()
