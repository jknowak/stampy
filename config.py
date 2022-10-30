from api.utilities.gooseutils import GooseAIEngines
from enum import Enum
import dotenv
import os

dotenv.load_dotenv()
NOT_PROVIDED = '__NOT_PROVIDED__'


def getenv(env_var, default=NOT_PROVIDED):
    """
    Get an environment variable with a default,
    raise an exception if the environment variable isn't set and no default is provided
    """
    value = os.getenv(env_var, default)
    if value == NOT_PROVIDED:
        raise Exception(f"Environment Variable '{env_var}' not set and no default provided")
    return value


class Services(Enum):
    DISCORD = "Discord"
    FLASK = "Flask"
    SLACK = "Slack"

    def __str__(self) -> None:
        return str(self._value_)

    def __eq__(self, other: object) -> bool:
        try:
            return str(self) == str(other)
        except Exception:
            return False

    def __hash__(self):

        return hash(str(self)) >> 22


maximum_recursion_depth = 30
subs_dir = "./database/subs"
youtube_api_service_name = "youtube"
youtube_api_version = "v3"
rob_id = 181142785259208704
stampy_id = "736241264856662038"
wikifeed_id = "819348549820088350"
plex_id = "756254556811165756"
god_id = "0"
youtube_testing_thread_url = "https://www.youtube.com/watch?v=vuYtSDMBLtQ&lc=Ugx2FUdOI6GuxSBkOQd4AaABAg"

# Multiply this by the total number of votes made, to get the number of stamps needed to post a reply comment
comment_posting_threshold_factor = 0.15

discord_token_env_variable = "DISCORD_TOKEN"
discord_guild_env_variable = "DISCORD_GUILD"
youtube_api_key_env_variable = "YOUTUBE_API_KEY"
database_path_env_variable = "DATABASE_PATH"
wiki_password_path_env_variable = "WIKI_BOT_PASSWORD"
environment_type_env_variable = "ENVIRONMENT_TYPE"
openai_env_variable = "OPENAI_API_KEY"
test_response_message = "LOGGED_TEST_RESPONSE"

TEST_QUESTION_PREFIX = "TEST_QUESTION "
TEST_RESPONSE_PREFIX = "TEST_RESPONSE "
CONFUSED_RESPONSE = "I don't understand"

prod_local_path = "/home/rob/stampy.local"

ENVIRONMENT_TYPE = getenv("ENVIRONMENT_TYPE")
acceptable_environment_types = ("production", "development")
assert (
    ENVIRONMENT_TYPE in acceptable_environment_types
), f"ENVIRONMENT_TYPE {ENVIRONMENT_TYPE} is not in {acceptable_environment_types}"

rob_miles_youtube_channel_id = {
    "production": "UCLB7AzTwc6VFZrBsO2ucBMg",
    "development": "UCDvKrlpIXM0BGYLD2jjLGvg",
}[ENVIRONMENT_TYPE]
stampy_youtube_channel_id = {
    "production": "UCFDiTXRowzFvh81VOsnf5wg",
    "development": "DvKrlpIXM0BGYLD2jjLGvg",
}[ENVIRONMENT_TYPE]

bot_dev_channel_id = {"production": 808138366330994688, "development": 803448149946662923}[ENVIRONMENT_TYPE] # TODO: the id is for talk-to-stampy, does the var name need to change, or does the id (correct is 758062805810282526//817518145472299009)
error_channel_id = {"production": 1017527224540344380, "development": 1017531179664150608}[ENVIRONMENT_TYPE]

stamp_scores_csv_file_path = {
    "production": "/var/www/html/stamps-export.csv",
    "development": "stamps-export.csv",
}[ENVIRONMENT_TYPE]

# admin_usernames = ["robertskmiles", "sudonym"]

discord_token = getenv("DISCORD_TOKEN")
discord_guild = getenv("DISCORD_GUILD")
youtube_api_key = getenv("YOUTUBE_API_KEY")
database_path = getenv("DATABASE_PATH")
wiki_password = getenv("WIKI_BOT_PASSWORD")
openai_api_key = getenv("OPENAI_API_KEY", default=None)
goose_api_key = getenv("GOOSE_API_KEY", default=None)
wolfram_token = getenv("WOLFRAM_TOKEN", default=None)
# These defaults are just to not break production until slack is set up.
slack_app_token = getenv("SLACK_APP_TOKEN", default=None)
slack_bot_token = getenv("SLACK_BOT_TOKEN", default=None)

wiki_config = {"uri": "https://stampy.ai/w/api.php", "user": "Stampy@stampy", "password": wiki_password}


stampy_control_channel_ids = (
    {"production": -1, "development": 803448149946662923}[ENVIRONMENT_TYPE],  # test
    {"production": 736247813616304159, "development": 817518389848309760}[ENVIRONMENT_TYPE],  # stampy-dev-priv
    {"production": 758062805810282526, "development": 817518145472299009}[ENVIRONMENT_TYPE],  # stampy-dev
    {"production": 758062805810282526, "development": 817518440192409621}[ENVIRONMENT_TYPE],  # talk-to-stampy
    {"production": -1, "development": 736241264856662038}[ENVIRONMENT_TYPE],  # robertskmiles TODO: replace -1 with the id for robs DM with stampy,
)
bot_admin_role_id = {"production": 819898114823159819, "development": 948709263461711923}[ENVIRONMENT_TYPE]


goose_engine_fallback_order = [  # What engine to use in order of preference in case one goes down.
    GooseAIEngines.GPT_20B,
    GooseAIEngines.GPT_6B,
    GooseAIEngines.GPT_2_7B,
    GooseAIEngines.GPT_1_3B,
    GooseAIEngines.GPT_125M,
    GooseAIEngines.FAIRSEQ_13B,
    GooseAIEngines.FAIRSEQ_6_7B,
    GooseAIEngines.FAIRSEQ_2_7B,
    GooseAIEngines.FAIRSEQ_1_3B,
    GooseAIEngines.FAIRSEQ_125M,
]


openai_channels: list[tuple[str, Services]] = [  # What channels may use openai.
    ("stampy-dev-priv", Services.DISCORD),
    ("aligned-intelligences-only", Services.DISCORD),
    ("ai", Services.DISCORD),
    ("not-ai", Services.DISCORD),
    ("events", Services.DISCORD),
    ("projects", Services.DISCORD),
    ("book-club", Services.DISCORD),
    ("dialogues-with-stampy", Services.DISCORD),
    ("meta", Services.DISCORD),
]


service_italics_marks = {
    Services.SLACK: "_",
    Services.FLASK: "",
}


default_italics_mark = "*"
