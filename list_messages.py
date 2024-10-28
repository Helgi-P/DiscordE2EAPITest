import json
import requests
import allure
from jsonschema import validate, ValidationError


# Загрузка JSON-схемы из файла
def load_schema(schema_file='list_messages_schema.json'):
    with open(schema_file, 'r', encoding='utf-8') as file:
        return json.load(file)


# Базовая функция для получения списка сообщений
def list_messages(base_url, headers, channel_id, message_id_around=None, limit=50):
    url = f"{base_url}/channels/{channel_id}/messages?limit={limit}"
    if message_id_around:
        url += f"&around={message_id_around}"

    with allure.step("Отправка GET-запроса"):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            allure.attach(str(e), name="Request Exception", attachment_type=allure.attachment_type.TEXT)
            assert False, f"Failed to send request: {e}"

        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
        allure.attach(str(response.status_code), name="HTTP Status Code", attachment_type=allure.attachment_type.TEXT)

    response_json = response.json()

    with allure.step("Валидация JSON-схемы ответа"):
        schema = load_schema()
        assert isinstance(response_json, list), "Response should be a list of messages"

        for message in response_json:
            try:
                validate(instance=message, schema=schema)
            except ValidationError as e:
                allure.attach(str(e), name="JSON Schema Validation Error", attachment_type=allure.attachment_type.TEXT)
                assert False, f"JSON schema validation failed for message: {message}"

    with allure.step("Проверка содержимого сообщений"):
        for message in response_json:
            # Проверка основных полей сообщения
            assert 'id' in message and message['id'] is not None, "Message must have an 'id' field"
            assert 'content' in message and message['content'] is not None, "Message must have a 'content' field"
            assert 'channel_id' in message and message[
                'channel_id'] is not None, "Message must have a 'channel_id' field"
            assert 'author' in message and message['author'] is not None, "Message must have an 'author' field"

            # Дополнительные проверки для вложенных полей автора
            author = message['author']
            assert 'id' in author and author['id'] is not None, "Author must have an 'id' field"
            assert 'username' in author and author['username'] is not None, "Author must have an 'username' field"
            assert 'discriminator' in author and author[
                'discriminator'] is not None, "Author must have a 'discriminator' field"
            assert 'public_flags' in author and author[
                'public_flags'] is not None, "Author must have 'public_flags' field"
            assert 'flags' in author and author['flags'] is not None, "Author must have 'flags' field"

            # Проверка вложений (если есть)
            if 'attachments' in message:
                assert isinstance(message['attachments'], list), "Attachments must be a list"
                allure.attach(f"Количество вложений: {len(message['attachments'])}", name="Attachments Count",
                              attachment_type=allure.attachment_type.TEXT)

    return response_json
