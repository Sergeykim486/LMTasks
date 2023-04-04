import requests

bot_token = "303078994:AAFJHY1df6bRv8VtXxzxHoajhVmlHz3cyeY"

response = requests.get(f'https://api.telegram.org/bot{bot_token}/deleteWebhook')

print(response.content)
