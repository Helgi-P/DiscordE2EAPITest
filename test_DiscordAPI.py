import pytest
import allure
from create_message import send_message_1, send_message_2, send_message_2_1, send_message_3_1, send_message_3_2, \
    send_message_3_3, generate_random_image
from delete_message import delete_message
from list_messages import list_messages
from get_message import get_message
from add_reaction import add_reaction
from delete_reaction import delete_reaction

# Глобальные переменные для хранения message_id
message_1_id = None
message_2_id = None
message_2_1_id = None
message_3_1_id = None
message_3_2_id = None
message_3_3_id = None


@pytest.fixture(params=[
    "1286673531911929856",
    "1286673475565518878",
    "1281160246110457922",
    "1286673450064412684",
    "1286673511733268552",
    "1286673548005343252"
])
def channel_id(request):
    return request.param


@allure.feature('Отправка сообщений в Discord')
@allure.story('Отправка текстового сообщения с jpeg файлом, его проверка, удаление сообщения')
@pytest.mark.order(1)
def test_send_message_and_delete_it_1(base_url, headers, channel_id):
    global message_1_id

    # Генерация случайного JPG изображения
    image_path = generate_random_image('JPEG')

    with allure.step('Отправка сообщения Message_1 с изображением'):
        message_1_id = send_message_1(base_url, headers, channel_id, image_path)
        assert message_1_id is not None, "Message 1 failed to send"
        allure.attach(str(message_1_id), name="Message ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Проверка сообщения Message_1"):
        get_message(base_url, headers, channel_id, message_1_id, emojis_to_check=None)

    with allure.step("Удаление сообщения Message_1"):
        delete_message(base_url, headers, channel_id, message_1_id)


@allure.story('Отправка нескольких сообщений, с добавлением и удалением реакций с проверками')
@pytest.mark.order(2)
def test_send_several_messages_add_delete_reactions_2(base_url, headers, channel_id, emojis, user_id):
    global message_2_id, message_2_1_id

    emoji_name_1 = emojis["emoji_name_1"]
    emoji_name_2 = emojis["emoji_name_2"]
    emoji_name_3 = emojis["emoji_name_3"]

    image_path = generate_random_image('PNG')

    with allure.step('Отправка сообщения Message_2'):
        message_2_id = send_message_2(base_url, headers, channel_id, image_path)
        assert message_2_id is not None, "Message 2 failed to send"
        allure.attach(str(message_2_id), name="Message ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step(f"Добавление реакции {emoji_name_1} на сообщение Message_2"):
        add_reaction(base_url, headers, channel_id, message_2_id, emoji_name_1)

    with allure.step("Проверка списка сообщений через list_messages"):
        response = list_messages(base_url, headers, channel_id, message_id_around=None, limit=50)
        allure.attach(str(response), name="List of Messages", attachment_type=allure.attachment_type.JSON)
        assert response is not None, "List of messages is empty"

    with allure.step("Проверка сообщения Message_2 с проверкой эмодзи"):
        get_message(base_url, headers, channel_id, message_2_id, emojis_to_check=[emoji_name_1])

    with allure.step('Отправка сообщения Message_2_1'):
        message_2_1_id = send_message_2_1(base_url, headers, channel_id)
        assert message_2_1_id is not None, "Message 2_1 failed to send"
        allure.attach(str(message_2_1_id), name="Message ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step(f"Добавление реакции {emoji_name_2} на сообщение Message_2"):
        add_reaction(base_url, headers, channel_id, message_2_id, emoji_name_2)

    with allure.step("Проверка сообщения Message_2 с проверкой двух эмодзи"):
        get_message(base_url, headers, channel_id, message_2_id, emojis_to_check=[emoji_name_1, emoji_name_2])

    with allure.step(f"Добавление реакции {emoji_name_3} на сообщение Message_2_1"):
        add_reaction(base_url, headers, channel_id, message_2_1_id, emoji_name_3)

    with allure.step("Проверка сообщения Message_2_1 с проверкой эмодзи"):
        get_message(base_url, headers, channel_id, message_2_1_id, emojis_to_check=[emoji_name_3])

    with allure.step(f"Удаление эмодзи {emoji_name_1} в Message_2"):
        delete_reaction(base_url, headers, channel_id, message_2_id, emoji_name_1, user_id)

    with allure.step("Проверка сообщения Message_2 на отсутствие удаленного эмодзи "):
        get_message(base_url, headers, channel_id, message_2_id, emojis_to_check_absent=[emoji_name_1])

    with allure.step("Удаление сообщений после теста"):
        if message_2_id:
            delete_message(base_url, headers, channel_id, message_2_id)
        if message_2_1_id:
            delete_message(base_url, headers, channel_id, message_2_1_id)

    # Обнуление идентификаторов
    message_2_id = None
    message_2_1_id = None


@allure.story('Негативный путь: добавление сообщений, неоднократное удаление, '
              'добавление реакции на удаленное сообщение')
@pytest.mark.order(3)
def test_negative_flow(base_url, headers, channel_id, emojis, user_id):
    global message_3_1_id, message_3_2_id

    emoji_name_4 = emojis["emoji_name_zaika"]

    image_path = generate_random_image('JPEG')

    with allure.step('Отправка сообщения Message_3_1'):
        message_3_1_id = send_message_3_1(base_url, headers, channel_id, image_path)
        assert message_3_1_id is not None, "Message 3_1 failed to send"
        allure.attach(str(message_3_1_id), name="Message ID", attachment_type=allure.attachment_type.TEXT)

    image_path = generate_random_image('PNG')

    with allure.step('Отправка сообщения Message_3_2'):
        message_3_2_id = send_message_3_2(base_url, headers, channel_id, image_path)
        assert message_3_2_id is not None, "Message 3_2 failed to send"
        allure.attach(str(message_3_2_id), name="Message ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Удаление сообщения Message_3_1"):
        delete_message(base_url, headers, channel_id, message_3_1_id)

    with allure.step("Проверка сообщения Message_3_1"):
        get_message(base_url, headers, channel_id, message_3_1_id, emojis_to_check=None)

    with allure.step(f"Добавление реакции {emoji_name_4} на сообщение Message_3_1"):
        add_reaction(base_url, headers, channel_id, message_3_1_id, emoji_name_4)

    with allure.step("Проверка сообщения Message_3_1"):
        get_message(base_url, headers, channel_id, message_3_1_id, emojis_to_check=emoji_name_4)

    with allure.step("Удаление сообщения Message_3_2"):
        delete_message(base_url, headers, channel_id, message_3_2_id)

    with allure.step("Проверка сообщения Message_3_2"):
        get_message(base_url, headers, channel_id, message_3_2_id, emojis_to_check=None)

    with allure.step("Повторное удаление сообщения Message_3_2"):
        delete_message(base_url, headers, channel_id, message_3_2_id, expect_not_found=True)


@allure.story('Отправка большого сообщения')
@pytest.mark.order(4)
def test_large_message(base_url, headers, channel_id, emojis, user_id):
    global message_3_3_id

    with allure.step('Отправка сообщения Message_3_3'):
        message_3_3_id = send_message_3_3(base_url, headers, channel_id)
        assert message_3_3_id is not None, "Message 3_3 failed to send"
        allure.attach(str(message_3_3_id), name="Message ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Удаление сообщения Message_3_3"):
        delete_message(base_url, headers, channel_id, message_3_3_id)
