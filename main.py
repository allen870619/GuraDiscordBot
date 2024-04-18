import discord
import datetime
# import Message as Msg
import MusicModule
import LeetcodeCrawler as LCC
import asyncio
from EnvData import TOKEN
from PoisonSoup import getPoisonSoup
from package.Utils.Utils import flush_log, generate_log
import SQLConnect as SQL
import DrawSQL
import ExpModule


class DiscordAppClient(discord.Client):
    # main func
    async def on_ready(self):
        for guild in self.guilds:
            flush_log("Logged on as %s @ %s" % (self.user, guild))

        # clear async tasks
        for task in asyncio.all_tasks():
            if "Custom" in task.get_name():
                task.cancel()

        # update state
        state = discord.Activity(
            type=discord.ActivityType.competing,
            name="最可i的 Holo EN")
        await client.change_presence(status=discord.Status.online, activity=state)

        # tasks
        asyncio.create_task(self.run_daily_schedule_service(), name="Custom: Leetcode")
        asyncio.create_task(self.update_server_status(), name="Custom: Server Info")
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
        if message_context.author != self.user:
            log_message = generate_log(message_context, False)
            print(log_message)
            flush_log(log_message)

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
        # if message_context.guild.id == 273814671985999873:  # 一言堂用
        #     if "指令" in message_context.channel.name:
        #         await Msg.messageReact(self, client, message_context)
        # else:
        #     await Msg.messageReact(self, client, message_context)

    # edit message
    async def on_message_edit(self, _, message_context):
        # log
        if message_context.author != self.user:
            log_message = generate_log(message_context, True)
            flush_log(log_message)

        # 觸發區域限制
        # if message_context.guild.id == 273814671985999873:  # 一言堂用
        #     if "指令" in message_context.channel.name:
        #         await Msg.messageReact(self, client, message_context)
        # else:
        #     await Msg.messageReact(self, client, message_context, isFromEdit=True)
            
    # error
    # async def on_error(self, event, *args, **kwargs):
    #     try:
    #         logStr = "[ERROR]", event, args[0]
    #     except:
    #         logStr = "[ERROR]", event
    #     flush_log(logStr)
  
    # daily schedule
    async def run_daily_schedule_service(self):
        flush_log("[SYS] Daily scheduler activated")
        while True:
            now = datetime.datetime.now()
            if now.strftime("%H:%M") == "08:00":
                await self.publish_leetcode()
                await self.send_poison_soup()
                
                current_sec = int(now.strftime("%S"))
                await asyncio.sleep(60 * 60 * 24 - 60 + current_sec)  # preserve for 1 mins
            await asyncio.sleep(1)

    async def publish_leetcode(self):
        question = LCC.dailyProblem()

        channel_list = SQL.queryLeetChn()
        for channel_id in channel_list:
            channel = client.get_channel(int(channel_id))
            if channel != None:
                await channel.send(question)

    async def send_poison_soup(self):
        poison_soup = getPoisonSoup()
        message = f"---本日毒雞湯---\n{poison_soup}\n\n共勉之"

        channel = client.get_channel(929379945346629642)
        if channel != None:
            await channel.send(message)
                    
    async def update_server_status(self):
        flush_log("[SYS] Server status updater activated")
        while True:
            await self.change_date()
            await self.set_online_status()
            await asyncio.sleep(60)
        
    async def change_date(self):
        channel = client.get_channel(1050243994111709234)
        date = datetime.datetime.now().strftime("%Y年%m月%d日")
        if channel.name != f"{date}":
            await channel.edit(name=f"{date}")
        
    async def set_online_status(self):
        guild = client.get_guild(870855015676391505)
        channel = client.get_channel(1050252285936140349)
        online_filter = filter(lambda fx: fx.status != discord.Status.offline, guild.members)
        online_list = list(online_filter)
        if channel.name != f"上線人數: {len(online_list)}":
            await channel.edit(name=f"上線人數: {len(online_list)}")

# start client here
intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True
intents.presences = True

client = DiscordAppClient(intents=intents)
client.run(TOKEN)