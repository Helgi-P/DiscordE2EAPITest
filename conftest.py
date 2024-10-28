import pytest
import os
from dotenv import load_dotenv
load_dotenv('DISCORD_TOKEN.env')


@pytest.fixture
def base_url():
    return "https://discord.com/api/v10"


@pytest.fixture
def api_token():
    return os.getenv('DISCORD_TOKEN')

@pytest.fixture
def headers(api_token):
    return {
        "Authorization": api_token
    }

@pytest.fixture
def channel_id():
    return "1286673531911929856"

@pytest.fixture
def user_id():
    return "1286609819137998883"

@pytest.fixture
def emojis():
    return {
        "emoji_name_1": "😱",
        "emoji_name_2": "👹",
        "emoji_name_3": "💀",
        "emoji_name_zaika": "🐇"
    }
