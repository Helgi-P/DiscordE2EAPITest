import requests
from jsonschema import validate, ValidationError
import allure
import json
import tempfile
import numpy as np
from PIL import Image


# Загрузка JSON-схемы
def load_message_schema(schema_path="message_schema.json"):
    with open(schema_path, 'r', encoding='utf-8') as file:
        return json.load(file)


message_schema = load_message_schema()


def validate_message_schema(response_json):
    try:
        validate(instance=response_json, schema=message_schema)
        return True
    except ValidationError as e:
        with allure.step('Ошибка валидации JSON-схемы'):
            allure.attach(f"Ошибка валидации: {e.message}", name="Ошибка JSON валидации",
                          attachment_type=allure.attachment_type.TEXT)
        return False


def generate_random_image(img_format='JPEG'):
    img_size = (128, 128)
    img = np.random.rand(*img_size, 3)
    img = (img * 255).astype(np.uint8)

    # Создание временного файла с изображением
    with tempfile.NamedTemporaryFile(suffix=f'.{img_format.lower()}', delete=False) as temp_image_file:
        image_path = temp_image_file.name
        image = Image.fromarray(img)
        image.save(image_path, format=img_format.upper())
    return image_path


# Базовая функция для создания сообщения
def create_message(base_url, headers, channel_id, message_data, file_path=None):
    url = f"{base_url}/channels/{channel_id}/messages"
    print(f"URL: {url}")

    with allure.step("Отправка POST-запроса"):

        form_data = {
            'content': message_data['content'],
        }

        print(f"Form data: {form_data}")

        files = {}  # Словарь для файлов

        if file_path:
            with open(file_path, 'rb') as f:
                files['file'] = f
                print(f"Sending file: {file_path}")

                # Отправляем запрос с файлом
                response = requests.post(url, headers=headers, data=form_data, files=files)
        else:
            # Отправка без файла
            print("Sending without file")
            response = requests.post(url, headers=headers, data=form_data)

        print(f"Response Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")

        allure.attach(str(response.status_code), name="HTTP Status Code", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Проверка кода ответа"):
        assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"

    try:
        response_json = response.json()
        print(f"Response JSON: {response_json}")  # Отладка: выводим JSON-ответ
    except ValueError as e:
        print(f"Failed to parse JSON response: {e}")
        raise AssertionError(f"Response is not JSON: {response.text}")

    with allure.step("Валидация JSON-схемы ответа"):
        required_fields = ['id', 'channel_id', 'content', 'author', 'attachments']
        for field in required_fields:
            assert field in response_json, f"Field '{field}' is missing in the response"

        if file_path:
            assert 'attachments' in response_json, "No attachments found in the response"
            assert len(response_json['attachments']) > 0, "No attachment present in the response"

            # Дополнительная проверка на соответствие вложений
            for attachment in response_json['attachments']:
                assert 'id' in attachment, "Attachment is missing 'id'"
                assert 'filename' in attachment, "Attachment is missing 'filename'"
                assert 'url' in attachment, "Attachment is missing 'url'"

    with allure.step("Проверка содержимого сообщения"):
        assert response_json['content'] == message_data['content'], "Message content mismatch"

    message_id = response_json['id']
    allure.attach(str(message_id), name="Message ID", attachment_type=allure.attachment_type.TEXT)

    return message_id


# Сообщения
Message_1 = "12345 вышел зайчик погулять"
Message_2 = ("Vdrug ohotnik vibegaet, pryamo v zaichika strelyaet <@1067428387817279541> "
             "Обрати внимание что творится! Öŕðéŕ þļåçéð šûççéššƒûļļý!")
Message_2_1 = "ПИФ-ПАФ!!!  哎呀呀！我的小兔子死了！"
Message_3_1 = "Принесли его домой"
Message_3_2 = "Оказался он живой!"
Message_3_3 = ("Родные Мягколапа,  зайца из семьи Лесных, были в отчаянии, когда их пушистый друг"
               " не вернулся с прогулки по лесу. Они искали его несколько дней и, наконец, нашли на "
               "краю болот. Заяц лежал бездыханный, с жуткими ранами, которые сразу сказали им о причине "
               "гибели: китайский браконьер, орудовавший в этих краях, убил его ради меха. Семья с тяжелым "
               "сердцем принесла Мягколапа домой. Они ещё не знали, что в темных лесах кто-то уже почуял "
               "смерть их друга. Этот некто — архилич некромант, известный в подземных кругах как К'Заларг Морг-Мар, "
               "повелитель мертвых. Он был другом Мягколапа, и хоть его сердце давно перестало биться, "
               "К'Заларг сохранил искру привязанности к этому пушистому созданию. Услышав зов смерти, он "
               "не мог оставить старого друга в руках загробной тьмы. В полночь густой туман окутал дом Лесных, "
               "и среди теней появился К'Заларг. Он не произнес ни слова, но его зловещие глаза вспыхнули ледяным светом, "
               "когда он увидел мертвого зайца. Некромант протянул свои костлявые руки, и темная энергия наполнила тело Мягколапа. "
               "Заяц очнулся, но теперь в его глазах светилась не жизнь, а магия, наполненная ненавистью и силой. Мягколап не просто "
               "воскрес. Он теперь мог гипнотизировать людей одним взглядом и управлять их мыслями. Но самое главное — в его сердце "
               "пылала жажда мести за свою смерть. Через несколько дней после этого заяц отправился на поиски убийцы. Он легко "
               "нашел браконьера — с помощью гипноза заставил его охотничьих псов показать путь. Когда они встретились лицом к лицу, "
               "Мягколап неподвижно смотрел на человека, пока тот пытался прицелиться, но пальцы охотника словно прилипли к ружью. "
               "Браконьер был парализован. Мягколап сосредоточился, и в этот момент его ментальная сила заставила охотника шаг за шагом "
               "подойти к краю болотистой трясины. Браконьер пытался кричать, но каждый его шаг был как чужой, будто кто-то другой вел его "
               "вперед. Мягколап не двигался, просто смотрел, удерживая его под полным контролем. С последним шагом человек исчез под водой, "
               "поглощенный болотом AHAHAHAH")


# Функции для отправки разных сообщений
def send_message_1(base_url, headers, channel_id, file_path=None):
    message_data = {"content": Message_1}
    return create_message(base_url, headers, channel_id, message_data, file_path)


def send_message_2(base_url, headers, channel_id, file_path=None):
    message_data = {"content": Message_2}
    return create_message(base_url, headers, channel_id, message_data, file_path)


def send_message_2_1(base_url, headers, channel_id, file_path=None):
    message_data = {"content": Message_2_1}
    return create_message(base_url, headers, channel_id, message_data, file_path)


def send_message_3_1(base_url, headers, channel_id, file_path=None):
    message_data = {"content": Message_3_1}
    return create_message(base_url, headers, channel_id, message_data, file_path)


def send_message_3_2(base_url, headers, channel_id, file_path=None):
    message_data = {"content": Message_3_2}
    return create_message(base_url, headers, channel_id, message_data, file_path)


def send_message_3_3(base_url, headers, channel_id, file_path=None):
    message_data = {"content": Message_3_3}

    message_length = len(Message_3_3)

    with allure.step(f"Проверка длины сообщения перед отправкой: {message_length} знаков"):
        allure.attach(f"Длина сообщения: {message_length}", name="Message Length",
                      attachment_type=allure.attachment_type.TEXT)

    try:
        response = create_message(base_url, headers, channel_id, message_data, file_path)

        with allure.step("Сообщение успешно отправлено"):
            allure.attach(f"Сообщение успешно отправлено длиной {message_length} знаков.",
                          name="Успех отправки", attachment_type=allure.attachment_type.TEXT)

        return response

    except AssertionError as e:
        with allure.step("Сообщение не удалось отправить"):
            allure.attach(f"Ошибка: {str(e)}", name="Ошибка отправки", attachment_type=allure.attachment_type.TEXT)
            allure.attach(f"Текст сообщения: {Message_3_3}", name="Текст сообщения",
                          attachment_type=allure.attachment_type.TEXT)

        with allure.step("Проблема с длиной сообщения"):
            max_length = 2000
            allure.attach(
                f"Ошибка при отправке сообщения длиной {message_length} символов. "
                f"Ограничение: {max_length} символов.",
                name="Возможная проблема", attachment_type=allure.attachment_type.TEXT)

        # Выбрасываем ошибку для завершения теста
        raise AssertionError(f"Тест упал: сообщение длиной {message_length} символов не отправлено.")
