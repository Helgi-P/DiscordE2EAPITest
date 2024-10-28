import requests
import allure


# Метод для удаления сообщения
def delete_message(base_url, headers, channel_id, message_id, expect_not_found=False):
    url = f"{base_url}/channels/{channel_id}/messages/{message_id}"

    with allure.step(f"Отправка DELETE-запроса для удаления сообщения {message_id}"):
        response = requests.delete(url, headers=headers)
        allure.attach(str(response.status_code), name="HTTP Status Code", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Проверка кода ответа"):
        if response.status_code == 204:
            allure.attach(f"Сообщение {message_id} успешно удалено", name="Message Deleted",
                          attachment_type=allure.attachment_type.TEXT)
        elif response.status_code == 404:
            allure.attach(f"Сообщение {message_id} не найдено или уже было удалено",
                          name="Message Not Found", attachment_type=allure.attachment_type.TEXT)
            if not expect_not_found:
                raise AssertionError(f"Сообщение {message_id} не существует или уже было удалено (404)")
            else:
                allure.attach(f"Ожидаемое поведение: сообщение {message_id} уже было удалено или не найдено",
                              name="Expected Not Found", attachment_type=allure.attachment_type.TEXT)
        else:
            allure.attach(f"Неожиданный статус ответа: {response.status_code}",
                          name="Unexpected Status Code", attachment_type=allure.attachment_type.TEXT)
            raise AssertionError(f"Неожиданный код ответа: {response.status_code}")
