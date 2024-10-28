import requests
import allure


# Метод для добавления реакции к сообщению
def add_reaction(base_url, headers, channel_id, message_id, emoji_name):
    url = f"{base_url}/channels/{channel_id}/messages/{message_id}/reactions/{emoji_name}/@me"

    with allure.step(f"Отправка PUT-запроса для добавления реакции к сообщению {message_id}"):
        response = requests.put(url, headers=headers)
        allure.attach(str(response.status_code), name="HTTP Status Code", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Проверка кода ответа"):
        if response.status_code == 404:
            error_response = response.json()
            assert error_response.get("code") == 10008, "Expected error code 10008 for 'Unknown Message'"
            allure.attach(str(error_response), name="Error Response", attachment_type=allure.attachment_type.JSON)
            return  # Если сообщение не найдено, завершаем проверку

        # Ожидание успешного добавления реакции
        assert response.status_code == 204, f"Expected 204 No Content, got {response.status_code}"

    allure.attach(f"Реакция '{emoji_name}' успешно добавлена к сообщению {message_id}", name="Reaction Added",
                  attachment_type=allure.attachment_type.TEXT)
