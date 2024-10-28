import requests
import allure


# Метод для удаления реакции с сообщения
def delete_reaction(base_url, headers, channel_id, message_id, emoji_name, user_id):
    url = f"{base_url}/channels/{channel_id}/messages/{message_id}/reactions/{emoji_name}/{user_id}"

    with allure.step(
            f"Отправка DELETE-запроса для удаления реакции {emoji_name} пользователя {user_id} из сообщения {message_id}"):
        response = requests.delete(url, headers=headers)
        allure.attach(str(response.status_code), name="HTTP Status Code", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Проверка кода ответа"):
        assert response.status_code == 204, f"Expected 204 No Content, got {response.status_code}"

    allure.attach(f"Реакция '{emoji_name}' пользователя {user_id} успешно удалена из сообщения {message_id}",
                  name="Reaction Deleted", attachment_type=allure.attachment_type.TEXT)
