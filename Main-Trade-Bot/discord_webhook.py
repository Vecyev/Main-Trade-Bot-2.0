import requests

class DiscordWebhook:
    def __init__(self, webhook_url=None):
        self.webhook_url = webhook_url or 'https://discord.com/api/webhooks/1354076379746140211/xKKT4dCTRpKt15_Uh3bgJtLDlCukgrGttgPtYF1ZnjYB1mvdjYEl7r_L_ktel5TyWzIn'

    def set_webhook_url(self, webhook_url):
        self.webhook_url = webhook_url

    def send_message(self, content, username="Bot", embeds=None):
        data = {
            "content": content,
            "username": username
        }
        if embeds:
            data["embeds"] = embeds

        response = requests.post(self.webhook_url, json=data)
        return response.status_code