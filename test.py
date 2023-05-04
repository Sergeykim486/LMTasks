import requests

bot_token = "911710144:AAGmHGL80xy_dlQPhx-LxqivNSNQDHrGEjw"

response = requests.get(f'https://api.telegram.org/bot{bot_token}/deleteWebhook')

print(response.content)
