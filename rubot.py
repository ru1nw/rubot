from cd import CD
from user_ratings import User_Ratings
import discord
from datetime import datetime, timedelta
from random import randint
now = datetime.utcnow

TEST_SERVER_ID = 0
TEST_CHANNEL_ID = 0
INFO_CHANNEL_ID = 0
HOMIE_SERVER_ID = 0
HOMIE_SCHEDULES_CHANNEL_ID = 0
MY_USER_ID = 0
BOT_USER_ID = 0

CAR_EMOJI = "🚙"
CAR_EMOJI_FLIPPED = "<:upsidedowncar:0>"
FLAG_RU = "🇷🇺"
ARROW_BACKWARD_EMOJI = "◀"
ARROW_FORWARD_EMOJI = "▶"
CIRCLE_EMOJI = "⭕"
CROSS_EMOJI = "❌"
STAR_EMOJI = "⭐"

BUG_REPORT_QUESTION = "[INFO] do you want to report a bug?"
RATING_OPTIN_QUESTION = """[ERR] you are not opt in to the rating system; do you want to opt in to the rating system?
the bot will record your discord information including id, name, and the time when you send a rating;
none of these information will be used other than this user rating feature for this bot.
react to circle if you want to opt in, or react to cross if you do not want to opt in.
**warning**: the algorithm of this rating system is subjected to change, so the ratings is very likely to be reset in the future"""

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents = intents)

@client.event
async def on_ready():
    reason = input("reason for restart>>>")
    
    print("We have logged in as {0.user}".format(client))

    channel = client.get_guild(TEST_SERVER_ID).get_channel(INFO_CHANNEL_ID)
    if reason == '':
        await channel.send(f"[INFO] bot restarted at UTC <{now()}>")
    else:
        await channel.send(f"[INFO] bot restarted at UTC <{now()}>, reason: {reason}")

@client.event
async def on_message(message):
    special = False
    if (float(message.channel.id) in await CD.get_exceptions()) and (await CD.get_special_counter() >= await CD.get_special()):
        if (await CD.get_special_counter() > await CD.get_special()):
            if (message.content in ["[ru] rm cd", "[ru] remove cooldown", "[ru] cooldown"]) and ((message.author.id == MY_USER_ID) or (message.author.guild_permissions.administrator)):
                await CD.reset_special_counter()
                await message.channel.send("[INFO] cooldown removed")
            return
        await CD.add_counter(True)
        await message.channel.send("[ERR] message limit reached, bot on cooldown, ask a moderator or the creator to remove the cd")
        return
    elif float(message.channel.id) in (await CD.get_exceptions()):
        special = True
    elif (message.author.bot):
        return

    if message.content.startswith("$hello"):
        await message.channel.send("Hello!")

    msg = message.content.lower()
    if msg.startswith("im ") or msg.startswith("i'm ") or msg.startswith("i am ") or msg.startswith("i’m "):
        await message.channel.send(f"hi {message.content[(msg.find('m ') + 2):]}!")

    for i in range(len(msg)):
        if msg[i:i+2] == " i":
            if msg[i+2:i+4] == "m ":
                await message.channel.send(f"hi {message.content[i+4:]}!")
                break
            elif msg[i+2:i+5] in ["'m ", "’m "]:
                await message.channel.send(f"hi {message.content[i+5:]}!")
                break
            elif msg[i+2:i+5] == " am":
                await message.channel.send(f"hi {message.content[i+5:]}!")
                break

    if ("69" in message.content) or ("420" in message.content):
        nicecount = message.content.count("69") + message.content.count("420")
        if not (len(message.mentions) == 0):
            for m in message.mentions:
                nicecount -= (str(m.id).count("69") + str(m.id).count("420"))
        for i in range(len(message.content)):
            left = message.content.find("<", i)
            right = message.content.find(">", left)
            sub = message.content[left:right]
            nicecount -= (sub.count("69") + sub.count("420"))
            i = right
        nicestr = ""
        for i in range(nicecount):
            nicestr += "nice "
        if not (len(nicestr) == 0):
            await message.reply(nicestr)

    if CAR_EMOJI in message.content:
        if (message.content.count(CAR_EMOJI) > 1):
            await message.reply("imma run a car over you the next time you try to spam")
        else:
            await message.reply(CAR_EMOJI_FLIPPED)
            await CD.add_counter(special)

    if message.content.startswith("[ru]rating") or message.content.startswith("[ru] rating"):
        if len(message.mentions) != 1:
            await message.reply("please mention 1 and only 1 user")
            return

        receiver = message.mentions[0]
        if not await User_Ratings.check_user(message.author.id):
            optinmsg = await message.reply(RATING_OPTIN_QUESTION)
            await optinmsg.add_reaction(CIRCLE_EMOJI)
            await optinmsg.add_reaction(CROSS_EMOJI)
        elif not await User_Ratings.check_user(receiver.id):
            await message.reply(f"[ERR] {receiver} hasn't agree to opt in to the rating system")
        elif message.mentions[0] == message.author:
            await message.reply("you can't rate yourself")
        elif (change := message.content.count(STAR_EMOJI)) < 1 or change > 5:
            await message.reply("you can rate 1 to 5 stars")
        else:
            rating = await User_Ratings.rate(receiver=receiver.id, rater=message.author.id, change=change)
            if rating == -1:
                cd = await User_Ratings.check_time(receiver.id, message.author.id)
                await message.reply(f"you are on cooldown: {cd.seconds // 60}:{cd.seconds % 60} left")
            elif rating > 5:
                await message.channel.send(f"[INFO] {receiver} already has a maximum rating of 5.000!")
            elif rating < 1:
                await message.channel.send(f"[INFO] {receiver} already has a minimum rating of 1.000!")
            else:
                await message.channel.send(f"[INFO] {receiver} now has a rating of {eval(format(rating, '.3f'))}!")

    if (message.content in [FLAG_RU, "[ru]", "ru", "rubot", "rwr"]):
        if (message.content == FLAG_RU) and ((message.guild.id == HOMIE_SERVER_ID) or (message.guild.id == TEST_SERVER_ID)):
            await message.channel.send("hey its the flag of ru")
        await message.channel.send(f'''rubot v1.0 created by {client.get_user(MY_USER_ID).mention} with discordpy
help:```yaml
info:        "[ru]" or ":flag_ru:"
schedule:    "[ru] schedule *(mention someone)"
bug:         "[ru] bug (message)"
rating:      "[ru] rating *(user) *(1-5 star emojis)"
```* required''')

    if (message.guild.id in [HOMIE_SERVER_ID, TEST_SERVER_ID]) and ((message.content.startswith("[ru] schedule")) or (message.content.startswith("[ru]schedule"))):
        if len(message.mentions) != 1:
            await message.channel.send("[ERR] please specify one user and one only")
        else:
            channel_id = HOMIE_SCHEDULES_CHANNEL_ID if (message.guild.id == HOMIE_SERVER_ID) else TEST_CHANNEL_ID
            pic_info_msg = await message.channel.send(f"[INFO] looking for images sent by <{message.mentions[0].display_name}> in {client.get_channel(channel_id).mention}, please wait patiently as there are lots of messages!")
            target = message.mentions[0]
            pic = await find_pic(channel = channel_id, target_id = target.id)
            if pic == None:
                await pic_info_msg.edit("[INFO] no images found!")
            else:
                pic_dict = {
                    "title": "schedule finder",
                    "description": "",
                    "url": pic.jump_url,
                    "timestamp": pic.created_at.isoformat(),
                    "color": 65535,
                    "footer": {
                        "text": "if more than 1 image is found, use the arrow emojis to see other images"
                        },
                    "image": {
                        "url": ""
                        },
                    "author": {
                        "name": target.name,
                        "icon_url": f"https://cdn.discordapp.com/avatars/{target.id}/{target.avatar}.png"
                        }
                    }
                pic_dict["description"] = pic.attachments[0].filename if (len(pic.attachments) > 0) else pic.content[pic.content.rfind('/')+1:]
                pic_dict["image"]["url"] = pic.attachments[0].url if (len(pic.attachments) > 0) else pic.content[pic.content.find("https://cdn.discordapp.com/attachments"):pic.content.find(".png")+4]
                pic_embed = discord.Embed.from_dict(pic_dict)
                await pic_info_msg.edit(embed=pic_embed)
                await pic_info_msg.add_reaction(ARROW_BACKWARD_EMOJI)
                await pic_info_msg.add_reaction(ARROW_FORWARD_EMOJI)

    if message.content.startswith("[ru]bug") or message.content.startswith("[ru] bug"):
        if (randint(1,100) == 69):
            await message.channel.send("provide ur credit card no. and the code on the back and ur social security no. to continue", delete_after=5.0)
        bugq = await message.channel.send(f"{BUG_REPORT_QUESTION} reason: <{message.content[message.content.find('bug')+4:]}>")
        await bugq.add_reaction(CIRCLE_EMOJI)
        await bugq.add_reaction(CROSS_EMOJI)



# adapted from the example https://github.com/Rapptz/discord.py/blob/d30fea5b0dcba9cd130026b56ec01e78bd788aff/examples/reaction_roles.py
role_message_id = 0
emoji_to_role = {
    discord.PartialEmoji(name=''): 0, # red
    discord.PartialEmoji(name=''): 0, # yellow
    discord.PartialEmoji(name=''): 0, # blue
}

@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    msg = await client.get_channel(payload.channel_id).fetch_message(payload.message_id)
    if (msg.created_at < (now() - timedelta(hours=6))) or (payload.member.bot):
        return
    
    if payload.message_id == role_message_id:
        guild = client.get_guild(payload.guild_id)
        if guild is None:
            return

        try:
            role_id = emoji_to_role[payload.emoji]
        except KeyError:
            return

        role = guild.get_role(role_id)
        if role is None:
            return

        try:
            await payload.member.add_roles(role)
        except discord.HTTPException:
            # If we want to do something in case of errors we'd do it here.
            pass

        channel = guild.get_channel(payload.channel_id)
        if channel is not None:
            await channel.send(f"[INFO] added the role <{role.name}> to the user {payload.member.display_name}!", delete_after=5.0)
        return
    
    if len(pic_msg := msg.embeds) > 0 and (payload.user_id != BOT_USER_ID) and (pic_msg[0].title == "schedule finder"):
        for re in msg.reactions:
            if (re.me) and (str(payload.emoji)[0] == str(re.emoji)[0]):
                channel_id = HOMIE_SCHEDULES_CHANNEL_ID if (payload.guild_id == HOMIE_SERVER_ID) else TEST_CHANNEL_ID
                target = None
                for m in msg.guild.members:
                    if (pic_msg[0].to_dict()["author"]['name']) == m.name:
                        target = m
                        break
                if str(re.emoji)[0] == ARROW_BACKWARD_EMOJI:
                    if (pic := await find_pic(channel=channel_id, before_date=pic_msg[0].timestamp, old_to_new=False, target_id = target.id)) == None:
                        pic_dict = pic_msg[0].to_dict()
                        pic_dict["description"] = "no more images found!"
                        pic_dict["url"] = ""
                        pic_dict["timestamp"] = (datetime(now().year, now().month, now().day) - timedelta(days=(30*6))).isoformat()
                        pic_dict.update({"image": {"url": ""}})
                        pic_embed = discord.Embed.from_dict(pic_dict)
                        await msg.edit(embed=pic_embed)
                        await msg.remove_reaction(ARROW_BACKWARD_EMOJI, client.get_user(BOT_USER_ID))
                    else:
                        pic_dict = pic_msg[0].to_dict()
                        pic_dict["description"] = pic.attachments[0].filename if (len(pic.attachments) > 0) else pic.content[pic.content.rfind('/')+1:]
                        pic_dict["url"] = pic.jump_url
                        pic_dict["timestamp"] = pic.created_at.isoformat()
                        pic_dict.update({"image": {"url": ""}})
                        pic_dict["image"]["url"] = pic.attachments[0].url if (len(pic.attachments) > 0) else pic.content[pic.content.find("https://cdn.discordapp.com/attachments"):pic.content.find(".png")+4]
                        pic_embed = discord.Embed.from_dict(pic_dict)
                        await msg.edit(embed=pic_embed)
                    await re.remove(payload.member)
                    if ARROW_FORWARD_EMOJI not in [str(r.emoji)[0] for r in msg.reactions]:
                        await msg.add_reaction(ARROW_FORWARD_EMOJI)
                        break
                elif str(re.emoji)[0] == ARROW_FORWARD_EMOJI:
                    pic = await find_pic(channel=channel_id, after_date=pic_msg[0].timestamp, old_to_new=True, target_id = target.id)
                    if ((pic) == None) or (pic.created_at < (datetime(now().year, now().month, now().day) - timedelta(days=30*6))):
                        pic_dict = pic_msg[0].to_dict()
                        pic_dict["description"] = "no more images found!"
                        pic_dict["url"] = ""
                        pic_dict["timestamp"] = now().isoformat()
                        pic_dict.update({"image": {"url": ""}})
                        pic_embed = discord.Embed.from_dict(pic_dict)
                        await msg.edit(embed=pic_embed)
                        await msg.remove_reaction(ARROW_FORWARD_EMOJI, client.get_user(BOT_USER_ID))
                    else:
                        pic_dict = pic_msg[0].to_dict()
                        pic_dict["description"] = pic.attachments[0].filename if (len(pic.attachments) > 0) else pic.content[pic.content.rfind('/')+1:]
                        pic_dict["url"] = pic.jump_url
                        pic_dict["timestamp"] = pic.created_at.isoformat()
                        pic_dict.update({"image": {"url": ""}})
                        pic_dict["image"]["url"] = pic.attachments[0].url if (len(pic.attachments) > 0) else pic.content[pic.content.find("https://cdn.discordapp.com/attachments"):pic.content.find(".png")+4]
                        pic_embed = discord.Embed.from_dict(pic_dict)
                        await msg.edit(embed=pic_embed)
                    await re.remove(payload.member)
                    if ARROW_BACKWARD_EMOJI not in [str(r.emoji)[0] for r in msg.reactions]:
                        await msg.remove_reaction(ARROW_FORWARD_EMOJI, client.get_user(BOT_USER_ID))
                        await msg.add_reaction(ARROW_BACKWARD_EMOJI)
                        await msg.add_reaction(ARROW_FORWARD_EMOJI)
                        break
        return

    if (msg.author == client.get_user(BOT_USER_ID)) and (msg.content.startswith(BUG_REPORT_QUESTION)) and (not(payload.member == client.get_user(BOT_USER_ID))):
        if str(payload.emoji) == CIRCLE_EMOJI:
            await msg.clear_reactions()
            await (await client.fetch_channel(INFO_CHANNEL_ID)).send(f"**[BUG] {payload.member.mention} reported a bug! Time: {now().isoformat()}\nreason: {msg.content[msg.content.find('reason')+6:]}\nbug report link: {msg.jump_url}**")
            await msg.edit(content="[INFO] bug reported! the creator will soon ask for further info")
        elif str(payload.emoji) == CROSS_EMOJI:
            await msg.clear_reactions()
            await msg.edit(content="[INFO] bug report canceled")
        return

    if (msg.content == RATING_OPTIN_QUESTION) and (msg.author == client.get_user(BOT_USER_ID)) and (payload.member == msg.mentions[0]):
        if str(payload.emoji) == CIRCLE_EMOJI:
            await msg.clear_reactions()
            await msg.edit(content="[INFO] you're now opt in to the rating system")
            await User_Ratings.init(payload.member.id)
        elif str(payload.emoji) == CROSS_EMOJI:
            await msg.clear_reactions()
            await msg.edit(content="[INFO] opt in cancelled")
        return

@client.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    msg = await client.get_channel(payload.channel_id).fetch_message(payload.message_id)
    if (msg.created_at < (now() - timedelta(hours=6))) or (payload.member.bot):
        return
    
    if payload.message_id != role_message_id:
        return

    guild = client.get_guild(payload.guild_id)
    if guild is None:
        return

    try:
        role_id = emoji_to_role[payload.emoji]
    except KeyError:
        return

    role = guild.get_role(role_id)
    if role is None:
        return

    member = guild.get_member(payload.user_id)
    if member is None:
        return

    try:
        await member.remove_roles(role)
    except discord.HTTPException:
        # If we want to do something in case of errors we'd do it here.
        pass

    channel = guild.get_channel(payload.channel_id)
    if channel is not None:
        await channel.send(f"[INFO] removed the role <{role.name}> from the user <{member.display_name}>!", delete_after=5.0)

async def find_pic(*, channel,
                   before_date = None,
                   after_date = datetime(now().year, now().month, now().day) - timedelta(days=(30*6)),
                   old_to_new = False,
                   target_id = MY_USER_ID
                   ):
    target = client.get_user(target_id)
    found = False
    pic = None
    async for oldmsg in client.get_channel(channel).history(limit=None, before=before_date, after=after_date, oldest_first=old_to_new):
        if oldmsg.author == target:
            if len(oldmsg.attachments) > 0:
                for att in oldmsg.attachments:
                    if att.content_type.startswith("image/"):
                        pic = oldmsg
                        found = True
                        break
            elif ("https://cdn.discordapp.com/attachments" in oldmsg.content) and (".png" in oldmsg.content):
                pic = oldmsg
                found = True
        if found:
            break
    return pic

client.run("token")
