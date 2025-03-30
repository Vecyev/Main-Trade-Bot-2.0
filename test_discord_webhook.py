import requests
import unittest
from discord_webhook import DiscordWebhook

class TestDiscordWebhook(unittest.TestCase):
    def setUp(self):
        self.webhook = DiscordWebhook()
        self.webhook.set_webhook_url('https://discord.com/api/webhooks/1354076379746140211/xKKT4dCTRpKt15_Uh3bgJtLDlCukgrGttgPtYF1ZnjYB1mvdjYEl7r_L_ktel5TyWzIn')

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