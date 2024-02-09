import discord
import datetime
import Message as Msg
import MusicModule
import LeetcodeCrawler as LCC
import asyncio
from EnvData import TOKEN
from PoisonSoup import getPoisonSoup
from package.Utils.Utils import flush_log
import SQLConnect as SQL
import DrawSQL
import ExpModule

class DiscordAppClient(discord.Client):
    # message log to console
    def msgLog(self, message_context, isEdited=False):
        # log
        if message_context.author != self.user:
            caller = "%s" % (message_context.author)
            if message_context.author.nick != None:
                caller += "(%s)" % (message_context.author.nick)
            editMark = ""
            if isEdited:
                editMark = "[Edited] "
            if message_context.content != '':
                caller += " @ %s/%s: %s%s" % (message_context.guild,
                                              message_context.channel.name, editMark, message_context.content)
            else:
                caller += " @ %s/%s %s" % (message_context.guild,
                                           message_context.channel.name, editMark)

            for i in message_context.attachments:
                caller += "\n\t [attachments] %s" % (i.url)
            flush_log(caller)
        else:
            return

    # main func
    async def on_ready(self):
        for guild in self.guilds:
            flush_log("Logged on as %s @ %s" % (self.user, guild))
        flush_log("[SYS] %s is on ready." % (self.user))
       
        # clear async tasks
        for task in asyncio.all_tasks():
            if "Custom" in task.get_name():
                task.cancel()

        # create tasks
        asyncio.create_task(self.run_schedule(), name="Custom: Leetcode")
        flush_log("[SYS] Set state")
        state = discord.Activity(
            type=discord.ActivityType.competing,
            name="最可i的 Holo EN")
        await client.change_presence(status=discord.Status.online, activity=state)
        asyncio.create_task(self.update_server_status(), name="Custom: Server Info")
        flush_log("[SYS] Startup finished")
            
        # update state
        state = discord.Activity(
                type=discord.ActivityType.competing,
                name="最可i的 Holo EN")
        await client.change_presence(status=discord.Status.online, activity=state)
        flush_log("[SYS] Startup finished")  

    # message reaction
    async def on_raw_reaction_add(self, message_context):
        guildId = message_context.guild_id
        messageId = message_context.message_id
        emojiId = message_context.emoji.id
        roleId = SQL.query_reaction_role_id(guildId=guildId, messageId=messageId, emojiId=emojiId)

        if roleId is not None: 
            guild = client.get_guild(guildId)
            role = guild.get_role(eval(roleId))
            await message_context.member.add_roles(role)    
        
    async def on_raw_reaction_remove(self, message_context):
        guildId = message_context.guild_id
        messageId = message_context.message_id
        emojiId = message_context.emoji.id
        roleId = SQL.query_reaction_role_id(guildId=guildId, messageId=messageId, emojiId=emojiId)

        if roleId is not None: 
            guild = client.get_guild(guildId)
            usr = guild.get_member(message_context.user_id)
            role = guild.get_role(eval(roleId))
            await usr.remove_roles(role)
            
    # message
    async def on_message(self, message_context):
        # log
        self.msgLog(message_context)

        # 經驗值系統 (beta)
        if message_context.author.id != 879980183522779137 and message_context.author.id != 950919884802510890:
            expSys = SQL.queryEnableExpSys(message_context.guild.id)
            if expSys != None and expSys[1] == True:
                exp = ExpModule.addUsrExp(message_context.author.id, message_context.guild.id)
                if exp[0] == exp[1]:
                    ExpModule.upgradeUsrLv(message_context.author.id, message_context.guild.id)
                    if expSys[0] != None:
                        chn = client.get_channel(expSys[0])
                        await chn.send("Congrats! <@%d> has upgraded to Level %d!" % (message_context.author.id, exp[2]+1))

        # 觸發區域限制
        if message_context.guild.id == 273814671985999873:  # 一言堂用
            if "指令" in message_context.channel.name:
                await Msg.messageReact(self, client, message_context)
        else:
            await Msg.messageReact(self, client, message_context)

    # edit message
    async def on_message_edit(self, _, message_context):
        # log
        self.msgLog(message_context, True)   

        # 觸發區域限制
        if message_context.guild.id == 273814671985999873:  # 一言堂用
            if "指令" in message_context.channel.name:
                await Msg.messageReact(self, client, message_context)
        else:
            await Msg.messageReact(self, client, message_context, isFromEdit=True)
            
    # error
    async def on_error(self, event, *args, **kwargs):
        try:
            logStr = "[ERROR]", event, args[0]
        except:
            logStr = "[ERROR]", event
        flush_log(logStr)

    # voice
    async def on_voice_state_update(self, member, _, after):
        if member == self.user and after.channel is None:
            await MusicModule.leaving(None)

    # leet schedule
    async def run_schedule(self):
        flush_log("[SYS] Leetcode crawler activated")
        while True:
            now = datetime.datetime.now()
            if now.strftime("%H:%M") == "08:00":
                await self.leet_schedule()
                await self.poison_soup()
                DrawSQL.refreshFreeDraw()
                await asyncio.sleep(60 * 60 * 24 - 60)  # preserve for 1 mins
            await asyncio.sleep(1)

    async def leet_schedule(self):
        toSend = LCC.dailyProblem()
        list = SQL.queryLeetChn()
        for i in list:
            chn = client.get_channel(int(i))
            if chn != None:
                await chn.send(toSend)

    async def poison_soup(self):
        soup = f"---本日毒雞湯---\n{getPoisonSoup()}\n\n共勉之"
        chn = client.get_channel(929379945346629642)
        if chn != None:
            await chn.send(soup)
                    
    async def update_server_status(self):
        while True:
            await self.change_date()
            await self.set_online_status()
            await asyncio.sleep(30)
        
    async def change_date(self):
        chn = client.get_channel(1050243994111709234)
        date = datetime.datetime.now().strftime("%Y年%m月%d日")
        if chn.name != f"{date}":
            await chn.edit(name=f"{date}")
        
    async def set_online_status(self):
        guild = client.get_guild(870855015676391505)
        chn = client.get_channel(1050252285936140349)
        onlineFilter = filter(lambda fx: fx.status != discord.Status.offline, guild.members)
        online = list(onlineFilter)
        if chn.name != f"上線人數: {len(online)}":
            await chn.edit(name=f"上線人數: {len(online)}")

# start client here
intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True
intents.presences = True

client = DiscordAppClient(intents=intents)
client.run(TOKEN)