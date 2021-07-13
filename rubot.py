from cd import CD
from user_ratings import User_Ratings
from role import Role
from constants import ID, UnicodeEmoji, InfoText, Token
import discord
from datetime import datetime, timedelta
from random import randint
import re
now = datetime.utcnow

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    reason = input("reason for restart>>>")
    
    print("We have logged in as {0.user}".format(client))

    channel = client.get_guild(ID.TEST_SERVER_ID.value).get_channel(
        ID.INFO_CHANNEL_ID.value)
    out = f"[INFO] bot restarted at UTC <{now()}>"
    if reason == '':
        await channel.send(out)
    else:
        await channel.send(f"{out}, reason: {reason}")


@client.event
async def on_message(message):
    author = message.author
    guild = message.guild
    channel = message.channel
    content = message.content.lower()
    mentions = message.mentions

    special = await check_cd(message, author, channel, content)
    if special == None:
        return

    # legit commands
    if content.startswith("rutk ") and (author.id == ID.MY_USER_ID):
        content = content[5:]
        old = message
        e = None if (len(old.embeds) < 1) else old.embeds[0]
        message = await channel.send(content, embed=e, files=[await f.to_file() for f in old.attachments], reference=old.reference)
        await old.delete()
    if content.startswith("[ru]"):
        if content.startswith("[ru] rating"):
            await rating(message, author, channel, content, mentions)
        elif message.content in ("[ru]", "[ru] help",
                                 "[ru] menu", "[ru] info"):
            await info(guild, channel, content)
        elif ((message.guild.id in (ID.HOMIE_SERVER_ID.value,
                                    ID.TEST_SERVER_ID.value))
                  and message.content.startswith("[ru] schedule")):
            await first_schedule(guild, channel, mentions)
        elif message.content.startswith("[ru] bug"):
            await bug(channel, content)
        elif message.content.startswith("[ru] role"):
            if author.permissions_in(channel).administrator:
                await role(message, guild, content)
            else:
                await message.reply(
                    "[ERR] this is an administrator-only command!")

    # jokes
    if ("69" in content) or ("420" in content):
        await funny_number(message, content, mentions)
    await im_joke(message, content)
    if UnicodeEmoji.CAR_EMOJI.value in content:
        await flip_car(message, content, special)





@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    if (member := payload.member).bot:
        return
    guild = client.get_guild(payload.guild_id)
    channel = guild.get_channel(payload.channel_id)
    msg = await channel.fetch_message(payload.message_id)
    
    if str(payload.message_id) in (await Role.get_msg(str(payload.guild_id))):
        await assign_role(
            str(payload.emoji), member, guild, channel, remove=False)
        
    if (msg.created_at < (now() - timedelta(hours=6))):
        for r in msg.reactions:
            if r.me:
                await r.clear()
        return
    
    if (len(pic_msg := msg.embeds) > 0
            and (payload.user_id != client.user.id)
            and (pic_msg[0].title == "schedule finder")):
        for re in msg.reactions:
            if (re.me) and (str(payload.emoji)[0] == str(re.emoji)[0]):
                if (payload.guild_id == ID.HOMIE_SERVER_ID.value):
                    channel_id = ID.HOMIE_SCHEDULES_CHANNEL_ID.value
                else:
                    channel_id = ID.TEST_CHANNEL_ID.value
                target = None
                for m in msg.guild.members:
                    if (pic_msg[0].to_dict()["author"]['name']) == m.name:
                        target = m
                        break
                if str(re.emoji)[0] == UnicodeEmoji.ARROW_BACKWARD_EMOJI.value:
                    if (pic := await find_pic(channel=channel_id,
                                              before_date=pic_msg[0].timestamp,
                                              old_to_new=False,
                                              target_id = target.id)
                            ) == None:
                        pic_dict = pic_msg[0].to_dict()
                        pic_dict["description"] = "no more images found!"
                        pic_dict["url"] = ""
                        pic_dict["timestamp"] = (datetime(now().year,
                                                          now().month,
                                                          now().day)
                                                 - timedelta(days=(30*6))
                                                 ).isoformat()
                        pic_dict.update({"image": {"url": ""}})
                        pic_embed = discord.Embed.from_dict(pic_dict)
                        await msg.edit(embed=pic_embed)
                        await msg.remove_reaction(
                            UnicodeEmoji.ARROW_BACKWARD_EMOJI.value,
                            client.user)
                    else:
                        pic_dict = pic_msg[0].to_dict()
                        if (len(pic.attachments) > 0):
                            pic_dict["description"
                                     ] = pic.attachments[0].filename
                        else:
                            pic_dict["description"
                                     ] = pic.content[pic.content.rfind('/')+1:]
                        pic_dict["url"] = pic.jump_url
                        pic_dict["timestamp"] = pic.created_at.isoformat()
                        pic_dict.update({"image": {"url": ""}})
                        if len(pic.attachments) > 0:
                            pic_dict["image"]["url"] = pic.attachments[0].url
                        else:
                            pic_dict["image"]["url"] = pic.content[
                                pic.content.find(
                                    "https://cdn.discordapp.com/attachments")
                                : pic.content.find(".png")+4]
                        pic_embed = discord.Embed.from_dict(pic_dict)
                        await msg.edit(embed=pic_embed)
                    await re.remove(payload.member)
                    if UnicodeEmoji.ARROW_FORWARD_EMOJI.value not in [
                            str(r.emoji)[0] for r in msg.reactions]:
                        await msg.add_reaction(
                            UnicodeEmoji.ARROW_FORWARD_EMOJI.value)
                        break
                elif str(re.emoji)[0] == UnicodeEmoji.ARROW_FORWARD_EMOJI.value:
                    pic = await find_pic(
                        channel=channel_id,
                        after_date=pic_msg[0].timestamp,
                        old_to_new=True,
                        target_id = target.id)
                    if ((pic == None)
                            or (pic.created_at < (datetime(now().year,
                                                           now().month,
                                                           now().day)
                                                  - timedelta(days=30*6)))):
                        pic_dict = pic_msg[0].to_dict()
                        pic_dict["description"] = "no more images found!"
                        pic_dict["url"] = ""
                        pic_dict["timestamp"] = now().isoformat()
                        pic_dict.update({"image": {"url": ""}})
                        pic_embed = discord.Embed.from_dict(pic_dict)
                        await msg.edit(embed=pic_embed)
                        await msg.remove_reaction(
                            UnicodeEmoji.ARROW_FORWARD_EMOJI.value, client.user)
                    else:
                        pic_dict = pic_msg[0].to_dict()
                        if (len(pic.attachments) > 0):
                            pic_dict["description"
                                     ] = pic.attachments[0].filename
                        else:
                            pic_dict["description"
                                     ] = pic.content[pic.content.rfind('/')+1:]
                        pic_dict["url"] = pic.jump_url
                        pic_dict["timestamp"] = pic.created_at.isoformat()
                        pic_dict.update({"image": {"url": ""}})
                        if (len(pic.attachments) > 0):
                            pic_dict["image"]["url"] = pic.attachments[0].url
                        else:
                            pic_dict["image"]["url"] = pic.content[
                                pic.content.find(
                                    "https://cdn.discordapp.com/attachments")
                                : pic.content.find(".png")+4]
                        pic_embed = discord.Embed.from_dict(pic_dict)
                        await msg.edit(embed=pic_embed)
                    await re.remove(payload.member)
                    if UnicodeEmoji.ARROW_BACKWARD_EMOJI.value not in [
                        str(r.emoji)[0] for r in msg.reactions]:
                        await msg.remove_reaction(
                            UnicodeEmoji.ARROW_FORWARD_EMOJI.value,
                            client.user)
                        await msg.add_reaction(
                            UnicodeEmoji.ARROW_BACKWARD_EMOJI.value)
                        await msg.add_reaction(
                            UnicodeEmoji.ARROW_FORWARD_EMOJI.value)
                        break
        return

    if ((msg.author == client.user)
            and (msg.content.startswith(InfoText.BUG_REPORT_QUESTION.value))
            and (payload.member != client.user)):
        if str(payload.emoji) == UnicodeEmoji.CIRCLE_EMOJI.value:
            await msg.clear_reactions()
            await (
                await client.fetch_channel(ID.INFO_CHANNEL_ID.value)
                    ).send(f"**[BUG] \
{await client.fetch_user(payload.user_id)} {payload.member.mention} \
reported a bug! Time: {now().isoformat()}\n\
reason: {msg.content[msg.content.find('reason')+8:]}\n\
bug report link: {msg.jump_url}**")
            await msg.edit(content="[INFO] \
bug reported! the creator will soon ask for further info")
        elif str(payload.emoji) == UnicodeEmoji.CROSS_EMOJI.value:
            await msg.clear_reactions()
            await msg.edit(content="[INFO] bug report canceled")
        return

    if ((msg.content == InfoText.RATING_OPTIN_QUESTION.value)
            and (msg.author == client.user)
            and (payload.member == msg.mentions[0])):
        if str(payload.emoji) == UnicodeEmoji.CIRCLE_EMOJI.value:
            await msg.clear_reactions()
            await msg.edit(content="[INFO] \
you're now opt in to the rating system")
            await User_Ratings.init(payload.member.id)
        elif str(payload.emoji) == UnicodeEmoji.CROSS_EMOJI.value:
            await msg.clear_reactions()
            await msg.edit(content="[INFO] opt in cancelled")
        return


@client.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    guild = client.get_guild(payload.guild_id)
    if (member := guild.get_member(payload.user_id)).bot:
        return
    channel = guild.get_channel(payload.channel_id)
    msg = await channel.fetch_message(payload.message_id)
    
    if str(payload.message_id) in await Role.get_msg(str(payload.guild_id)):
        await assign_role(str(payload.emoji), member,
                          guild, channel, remove=True)
    
    if (msg.created_at < (now() - timedelta(hours=6))):
        for r in msg.reactions:
            if r.me:
                await r.clear()
        return





async def check_cd(message, author, channel, content):
    if str(channel.id) in (await CD.get_exceptions()):
        special_counter = await CD.get_special_counter()
        special_msg_count = await CD.get_special()
        
        if special_counter >= special_msg_count:
            if ((content in ("[ru] rm cd", "[ru] remove cooldown",
                             "[ru] cooldown"))
                    and ((author.id == ID.MY_USER_ID.value)
                             or (author.guild_permissions.administrator))):
                await CD.reset_special_counter()
                await channel.send("[INFO] cooldown removed")
            elif special_counter == special_msg_count:
                await CD.add_special_counter()
                await channel.send("[ERR] \
message limit reached, bot on cooldown, \
ask a moderator or the creator to remove the cd")
            return
        else:
            return True
    elif author.bot:
        return

    return False


async def rating(message, author, channel, content, mentions):
    if len(mentions) != 1:
        await message.reply("please mention 1 and only 1 user")
        return

    receiver = mentions[0]
    if not await User_Ratings.check_user(author.id):
        optinmsg = await message.reply(InfoText.RATING_OPTIN_QUESTION.value)
        await optinmsg.add_reaction(UnicodeEmoji.CIRCLE_EMOJI.value)
        await optinmsg.add_reaction(UnicodeEmoji.CROSS_EMOJI.value)
    elif not await User_Ratings.check_user(receiver.id):
        await message.reply(f"[ERR] \
{receiver} hasn't agree to opt in to the rating system")
    elif mentions[0] == author:
        await message.reply("you can't rate yourself")
    elif ((change := content.count(UnicodeEmoji.STAR_EMOJI.value)) < 1
              or change > 5):
        await message.reply("you can rate 1 to 5 stars")
    else:
        rating = await User_Ratings.rate(receiver=receiver.id,
                                         rater=author.id, change=change)
        if rating == -1:
            cd = await User_Ratings.check_time(receiver.id, author.id)
            await message.reply(f"you are on cooldown: \
{cd.seconds // 60}:{cd.seconds % 60} left")
        elif rating > 5:
            await channel.send(f"[INFO] \
{receiver} already has a maximum rating of 5.000!")
        elif rating < 1:
            await channel.send(f"[INFO] \
{receiver} already has a minimum rating of 1.000!")
        else:
            await channel.send(f"[INFO] \
{receiver} now has a rating of {eval(format(rating, '.3f'))}!")


async def info(guild, channel, content):
    if ((content == UnicodeEmoji.FLAG_RU.value)
            and ((guild.id == ID.HOMIE_SERVER_ID.value)
                     or (guild.id == ID.TEST_SERVER_ID.value))):
        await channel.send("hey its the flag of ru")
    await channel.send(f"rubot v1.3 created by \
{await client.fetch_user(ID.MY_USER_ID.value)} \
{(await client.fetch_user(ID.MY_USER_ID.value)).mention} with discordpy\
{InfoText.INFO.value}")


async def first_schedule(guild, channel, mentions):
    if len(mentions) != 1:
        await channel.send("[ERR] please specify one user and one only")
    else:
        if (guild.id == ID.HOMIE_SERVER_ID.value):
            channel_id = ID.HOMIE_SCHEDULES_CHANNEL_ID.value
        else:
            channel_id = ID.TEST_CHANNEL_ID.value
        pic_info_msg = await channel.send(f"[INFO] \
looking for images sent by <{mentions[0].display_name}> \
in {client.get_channel(channel_id).mention}, \
please wait patiently as there are lots of messages!")
        target = mentions[0]
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
                    "text": "if more than 1 image is found, \
use the arrow emojis to see other images"
                    },
                "image": {
                    "url": ""
                    },
                "author": {
                    "name": target.name,
                    "icon_url": f"https://cdn.discordapp.com/\
avatars/{target.id}/{target.avatar}.png"
                    }
                }
            if (len(pic.attachments) > 0):
                pic_dict["description"] = pic.attachments[0].filename
                pic_dict["image"]["url"] = pic.attachments[0].url
            else:
                pic_dict["description"] = pic.content[pic.content.rfind('/')+1:]
                pic_dict["image"]["url"] = pic.content[
                    pic.content.find("https://cdn.discordapp.com/attachments")
                    : pic.content.find(".png")+4]
            pic_embed = discord.Embed.from_dict(pic_dict)
            await pic_info_msg.edit(embed=pic_embed)
            await pic_info_msg.add_reaction(
                UnicodeEmoji.ARROW_BACKWARD_EMOJI.value)
            await pic_info_msg.add_reaction(
                UnicodeEmoji.ARROW_FORWARD_EMOJI.value)


async def bug(channel, content):
    if (randint(1,100) == 69):
        await channel.send(
            "provide ur credit card no. and the code on the back \
and ur social security no. to continue",
            delete_after=5.0)
    bugq = await channel.send(f"""
{InfoText.BUG_REPORT_QUESTION.value}
react to auto-send a bug report directly, or contact the creator here: \
{await client.fetch_user(ID.MY_USER_ID.value)} \
{(await client.fetch_user(ID.MY_USER_ID.value)).mention}
reason: `{content[content.find('bug')+4:]}`
""")
    await bugq.add_reaction(UnicodeEmoji.CIRCLE_EMOJI.value)
    await bugq.add_reaction(UnicodeEmoji.CROSS_EMOJI.value)


async def role(message, guild, content):
    lines = content.splitlines()
    lines.pop(0)
    if len(lines) < 1:
        await message.reply(f"[ERR] \
no emoji and roles found! check format using `[ru] help` command")
        return
    for l in lines:
        r = re.compile(r"((<:\w{2,}:\d{18}>)|(.{1,4})) *- *<@&\d{18}>")
        if (r.match(l) == None):
            await message.reply(InfoText.ROLE_ERR.value)
            return
        try:
            emojistr, rolestr = l.split(sep="-", maxsplit=1)
        except ValueError:
            await message.reply(InfoText.ROLE_ERR.value)
            return
        emoji = emojistr.strip()
        rid = int(rolestr.strip()[3:21])
        try:
            await message.add_reaction(emoji)
        except HTTPException:
            await message.reply("[ERR] \
invalid emoji! try using a different emoji")
            await message.clear_reactions()
            return
        await Role.add_role(emoji, str(rid), str(guild.id))
    await Role.add_msg(str(guild.id), str(message.id))

async def funny_number(message, content, mentions):
    nicecount = content.count("69") + content.count("420")
    
    if len(mentions) != 0:
        for m in mentions:
            nicecount -= (str(m.id).count("69") + str(m.id).count("420"))
    for i in range(len(content)):
        left = content.find("<", i)
        right = content.find(">", left)
        sub = content[left:right]
        nicecount -= (sub.count("69") + sub.count("420"))
        i = right
        
    nicestr = ""
    for i in range(nicecount):
        nicestr += "nice "
    if len(nicestr) != 0:
        await message.reply(nicestr)


async def im_joke(message, content):
    match = re.finditer(r"\b((i('|’|)m)|i\s+am)\s+.", content, re.I)
    for m in match:
        if len(content[m.end()-1:]) <= 100:
            await message.reply(f"hi {content[m.end()-1:]}!")
            break

async def flip_car(message, content, special):
    if (content.count(UnicodeEmoji.CAR_EMOJI.value) > 1):
        await message.reply(
            "imma run a car over you the next time you try to spam")
    else:
        await message.reply(UnicodeEmoji.CAR_EMOJI_FLIPPED.value)
        await CD.add_counter(special)


# adapted from the example
# https://github.com/Rapptz/discord.py/blob/d30fea5b0dcba9cd130026b56ec01e78bd788aff/examples/reaction_roles.py
async def assign_role(emoji, member, guild, channel, *, remove):
    try:
        role_id = await Role.get_role(str(guild.id), str(emoji))
    except KeyError:
        return

    role = guild.get_role(int(role_id))
    if role is None:
        return

    if member is None:
        return

    try:
        if remove:
            await member.remove_roles(role)
        else:
            await member.add_roles(role)
    except discord.HTTPException as ex:
        # If we want to do something in case of errors we'd do it here.
        if ex.code == 50013:
            await channel.send(f"[ERR] \
the bot lacks permission to assign roles, \
please ask the moderators to place the bot higher on the role hierarchy",
                               delete_after=5.0)
        else:
            await channel.send(f"[ERR] \
unexpected error, \
please report to the bot creator by using the `[ru] bug (reason)` command",
                               delete_after=5.0)
            raise
    else:
        if channel is not None:
            if remove:
                await channel.send(f"[INFO] \
removed the role <{role.name}> from the user {member.mention}!",
                                   delete_after=5.0)
            else:
                await channel.send(f"[INFO] \
added the role <{role.name}> to the user {member.mention}!",
                                   delete_after=5.0)


async def find_pic(*, channel,
                   before_date = None,
                   after_date = datetime(now().year,
                                         now().month,
                                         now().day)
                   - timedelta(days=(30*6)),
                   old_to_new = False,
                   target_id = ID.MY_USER_ID.value):
    target = client.get_user(target_id)
    found = False
    pic = None
    async for oldmsg in client.get_channel(channel).history(
            limit=None, before=before_date,
            after=after_date, oldest_first=old_to_new):
        if oldmsg.author == target:
            if len(oldmsg.attachments) > 0:
                for att in oldmsg.attachments:
                    if att.content_type.startswith("image/"):
                        pic = oldmsg
                        found = True
                        break
            elif (("https://cdn.discordapp.com/attachments" in oldmsg.content)
                      and (".png" in oldmsg.content)):
                pic = oldmsg
                found = True
        if found:
            break
    return pic





test_mode = input("run as test?")
if (test_mode.lower() in ("n", "no", "m", "main", "f", "false", "x")):
    client.run(Token.MAIN_BOT.value)
else:
    client.run(Token.TEST_BOT.value)
