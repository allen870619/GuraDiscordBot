from pprint import pprint
import discord
import datetime
import requests
import Message as Msg
import MusicModule
import LeetcodeCrawler as LCC
import asyncio
from EnvData import TOKEN
from Utils import log
import SQLConnect as SQL
import ExpModule

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
class MyClient(discord.Client):
    # message log to console
    def msgLog(self, ctx, isEdited=False):
        # log
        if ctx.author != self.user:
            caller = "%s"%(ctx.author)
            if ctx.author.nick != None:
                caller += "(%s)"%(ctx.author.nick)
            editMark = ""
            if isEdited:
                editMark = "[Edited] "
            if ctx.content != '':
                caller += " @ %s/%s: %s%s"%(ctx.guild, ctx.channel.name, editMark, ctx.content)
            else:
                caller += " @ %s/%s %s"%(ctx.guild, ctx.channel.name, editMark)

            for i in ctx.attachments:
                caller += "\n\t [attachments] %s"%(i.url)
            log(caller)
        else:
            return
    
    # meme image filter
    async def memeFilter(self, ctx):
        if ctx.channel.id == 928824631345971241:
            url = ctx.content
            if url != '':
                try:
                    if url.startswith('http') or url.startswith('www'):
                        if not requests.get(url).ok:
                            await Msg.memeWarning(self, client, ctx)
                            await ctx.delete()
                    else:
                        await Msg.memeWarning(self, client, ctx)
                        await ctx.delete()
                except Exception as e:
                    if type(e) == requests.exceptions.MissingSchema:
                        await Msg.memeWarning(self, client, ctx)
                    else:
                        await Msg.memeWarning(self, client, ctx, '連線錯誤, 請檢查連結')
                    await ctx.delete()


    # main func
    async def on_ready(self):
        for guild in self.guilds:
            log("Logged on as %s @ %s"%(self.user, guild))
        log("[SYS] %s is on ready."%(self.user))
        asyncio.create_task(self.runSchedule())
        log("[SYS] Set state")
        state = discord.Activity(type=discord.ActivityType.competing, name="最可i的 Holo EN")
        await client.change_presence(status=discord.Status.online, activity=state)
        log("[SYS] Startup finished")

    # message
    async def on_message(self, ctx):
        # log
        self.msgLog(ctx)

        # filter
        # 梗圖過濾
        await self.memeFilter(ctx)

        # 經驗值系統 (beta)
        expSys=SQL.queryEnableExpSys(ctx.guild.id)
        if expSys != None and expSys[1] == True:
            exp=ExpModule.addUsrExp(ctx.author.id, ctx.guild.id)
            if exp[0] == exp[1]:
                ExpModule.upgradeUsrLv(ctx.author.id, ctx.guild.id)
                chn = client.get_channel(expSys[0])
                await chn.send("Congrats! <@%d> has upgraded to Level %d!"%(ctx.author.id, exp[2]+1))

        # 觸發區域限制
        if ctx.guild.id == 273814671985999873: #一言堂用
            if "指令" in ctx.channel.name:
                await Msg.messageReact(self, client, ctx)
        else:
            await Msg.messageReact(self, client, ctx)

    # edit message
    async def on_message_edit(self, _, ctx):
        # log
        self.msgLog(ctx, True)

        # filter
        # 梗圖過濾
        await self.memeFilter(ctx)

        # 觸發區域限制
        if ctx.guild.id == 273814671985999873: #一言堂用
            if "指令" in ctx.channel.name:
                await Msg.messageReact(self, client, ctx)
        else:
            await Msg.messageReact(self, client, ctx)

    # voice
    async def on_voice_state_update(self, member, _, after):
        if member == self.user and after.channel == None:
            await MusicModule.leaving(None)

    # leet schedule
    async def runSchedule(self):
        log("[SYS] Leetcode crawler activated")
        while True:
            now = datetime.datetime.now()
            if now.strftime("%H:%M") == "08:00":
                await self.leetSchedule()
                await asyncio.sleep(60 * 60 * 24 - 60) # preserve for 1 mins
            await asyncio.sleep(1)

    async def leetSchedule(self):
        toSend = LCC.dailyProblem()
        list = SQL.queryLeetChn()
        for i in list:
            chn = client.get_channel(int(i))
            if  chn != None:
                await chn.send(toSend)
            
client = MyClient(intents=intents)
client.run(TOKEN)