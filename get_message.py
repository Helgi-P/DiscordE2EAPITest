import json
import requests
import allure
from jsonschema import validate, ValidationError


# Загрузка JSON-схемы из файла
def load_schema(schema_file='get_message_schema.json'):
    with open(schema_file, 'r', encoding='utf-8') as file:
        return json.load(file)


# Базовая функция для получения конкретного сообщения
def get_message(base_url, headers, channel_id, message_id, emojis_to_check=None, emojis_to_check_absent=None):
    url = f"{base_url}/channels/{channel_id}/messages/{message_id}"

    with allure.step("Отправка GET-запроса"):
        try:
            response = requests.get(url, headers=headers)
        except requests.exceptions.RequestException as e:
            allure.attach(str(e), name="Request Exception", attachment_type=allure.attachment_type.TEXT)
            assert False, f"Failed to send request: {e}"

        # Проверка статуса ответа, если сообщение было удалено, проверяем статус код
        if response.status_code == 404:
            error_response = response.json()
            assert error_response.get("code") == 10008, "Expected error code 10008 for 'Unknown Message'"
            allure.attach(str(error_response), name="Error Response", attachment_type=allure.attachment_type.JSON)
            return None  # Сообщение не найдено, возврат None

        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
        allure.attach(str(response.status_code), name="HTTP Status Code", attachment_type=allure.attachment_type.TEXT)

    response_json = response.json()

    with allure.step("Валидация JSON-схемы ответа"):
        schema = load_schema()
        assert isinstance(response_json, dict), "Response should be a message object"

        try:
            validate(instance=response_json, schema=schema)
        except ValidationError as e:
            allure.attach(str(e), name="JSON Schema Validation Error", attachment_type=allure.attachment_type.TEXT)
            assert False, f"JSON schema validation failed for message: {response_json}"

    with allure.step("Проверка содержимого сообщения"):
        assert 'id' in response_json and response_json['id'] is not None, "Message must have an 'id' field"
        assert 'content' in response_json and response_json[
            'content'] is not None, "Message must have a 'content' field"
        assert 'channel_id' in response_json and response_json[
            'channel_id'] is not None, "Message must have a 'channel_id' field"
        assert 'author' in response_json and response_json['author'] is not None, "Message must have an 'author' field"

        # Дополнительные проверки для вложенных полей автора
        author = response_json['author']
        assert 'id' in author and author['id'] is not None, "Author must have an 'id' field"
        assert 'username' in author and author['username'] is not None, "Author must have an 'username' field"
        assert 'discriminator' in author and author[
            'discriminator'] is not None, "Author must have a 'discriminator' field"
        assert 'public_flags' in author and author['public_flags'] is not None, "Author must have 'public_flags' field"
        assert 'flags' in author and author['flags'] is not None, "Author must have 'flags' field"

    # Проверка наличия реакций, если передан список эмодзи для проверки
    if emojis_to_check:
        with allure.step(f"Проверка реакций для эмодзи {emojis_to_check}"):
            assert 'reactions' in response_json, "Expected reactions in the message, but none were found"
            reactions = response_json['reactions']
            assert isinstance(reactions, list), "Reactions must be a list"

            for emoji in emojis_to_check:
                reaction_found = any(reaction['emoji']['name'] == emoji for reaction in reactions)
                assert reaction_found, f"Expected reaction with emoji '{emoji}' not found"

    # Проверка отсутствия реакций, если передан список эмодзи для проверки отсутствия
    if emojis_to_check_absent:
        with allure.step(f"Проверка отсутствия реакций для эмодзи {emojis_to_check_absent}"):
            assert 'reactions' in response_json, "Expected reactions in the message, but none were found"
            reactions = response_json['reactions']
            assert isinstance(reactions, list), "Reactions must be a list"

            for emoji in emojis_to_check_absent:
                reaction_found = any(reaction['emoji']['name'] == emoji for reaction in reactions)
                assert not reaction_found, f"Unexpected reaction with emoji '{emoji}' found"

    return response_json
