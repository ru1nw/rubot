# some of the values are left empty on purpose
from enum import IntEnum
from enum import Enum
from enum import unique

@unique
class ID(IntEnum):
    TEST_SERVER_ID = 0
    TEST_CHANNEL_ID = 0
    INFO_CHANNEL_ID = 0
    HOMIE_SERVER_ID = 0
    HOMIE_SCHEDULES_CHANNEL_ID = 0
    MY_USER_ID = 0
    BOT_USER_ID = 0
    TEST_BOT_USER_ID = 0
    ROLE_MESSAGE_ID = 0
    RED_ROLE_ID = 0
    YELLOW_ROLE_ID = 0
    BLUE_ROLE_ID = 0

@unique
class UnicodeEmoji(Enum):
    RED_EMOJI = "🔴"
    YELLOW_EMOJI = "🟡"
    BLUE_EMOJI = "🔵"
    CAR_EMOJI = "🚙"
    CAR_EMOJI_FLIPPED = "<:upsidedowncar:0>"
    FLAG_RU = "🇷🇺"
    ARROW_BACKWARD_EMOJI = "◀"
    ARROW_FORWARD_EMOJI = "▶"
    CIRCLE_EMOJI = "⭕"
    CROSS_EMOJI = "❌"
    STAR_EMOJI = "⭐"

@unique
class InfoText(Enum):
    BUG_REPORT_QUESTION = "[INFO] do you want to report a bug?"
    RATING_OPTIN_QUESTION = """
[ERR] you are not opt in to the rating system; do you want to opt in to the rating system?
the bot will record your discord information including id, name, and the time when you send a rating;
none of these information will be used other than this user rating feature for this bot.
react to circle if you want to opt in, or react to cross if you do not want to opt in.
**warning**: the algorithm of this rating system is subjected to change, so the ratings is very likely to be reset in the future
"""
    ROLE_ERR = """
[ERR] wrong format! format should be ```
[ru] role
emoji - @role
emoji - @role
```(number of whitespaces around the hyphen doesnt matter)
"""
    INFO = """
help:```yaml
info:       "[ru]" or ":flag_ru:"
schedule:   "[ru] schedule *(mention someone)"
bug:        "[ru] bug (message)"
rating:     "[ru] rating *(user) *(1-5 star emojis)"
```mod:```yaml
remove cooldown: "[ru] remove cooldown" or "[ru] cooldown"
role:       "[ru] role"
            "emoji - @role"
            "emoji - @role"
            so on...
```* required
"""

@unique
class Token(Enum):
    MAIN_BOT = ""
    TEST_BOT = ""

@unique
class Path(Enum):
    RUBOT_FIREBASE_CERTIFICATE = u"./service-account-private-key.json"