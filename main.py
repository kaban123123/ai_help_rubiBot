def get_gigachat_response(user_message: str) -> str:
    try:
        auth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        auth_headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "RqUID": str(uuid.uuid4()),
            "Authorization": f"Basic {GIGACHAT_KEY}",
        }
        auth_data = {"scope": "GIGACHAT_API_PERS"}

        auth_response = requests.post(
            auth_url,
            headers=auth_headers,
            data=auth_data,
            verify=False,
            timeout=60,
        )

        if auth_response.status_code != 200:
            return f"Ошибка авторизации GigaChat: {auth_response.status_code} {auth_response.text}"

        auth_json = auth_response.json()
        access_token = auth_json.get("access_token")
        if not access_token:
            return f"Не получен access_token: {auth_response.text}"

        chat_url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        chat_headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        chat_data = {
            "model": "GigaChat",
            "messages": [
                {"role": "system", "content": "Ты полезный помощник для Telegram-бота ai_help_rubiBot."},
                {"role": "user", "content": user_message},
            ],
            "temperature": 0.7,
            "max_tokens": 1000,
        }

        response = requests.post(
            chat_url,
            headers=chat_headers,
            json=chat_data,
            verify=False,
            timeout=120,
        )

        if response.status_code != 200:
            return f"Ошибка GigaChat: {response.status_code} {response.text}"

        result = response.json()
        return result["choices"][0]["message"]["content"].strip()

    except requests.exceptions.RequestException as e:
        return f"Ошибка соединения с GigaChat: {e}"
    except Exception as e:
        return f"Ошибка ИИ: {e}"
