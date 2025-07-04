import discord
import subprocess
import LeetcodeCrawler as LCC
from datetime import datetime
# 發圖片請求用
import requests
# Requests基本設定Class
import SQLConnect as SQL
from package.Utils.Utils import hex_color_string_to_int
# from PsutilSensor import getAllInfo
# 雞湯
from PoisonSoup import getPoisonSoup
# openai
from OpenAIHelper import send_chat
import asyncio

# utils
# getting img

# proxy chat
isProxyMode = False
proxyList = []

# Utils: show image


async def showImg(ctx, targetUrl, color=None):
    embed = discord.Embed(color=hex_color_string_to_int(color))
    embed.set_image(url=targetUrl)
    await ctx.channel.send(embed=embed)

# Utils: Embed


def embedCreator(title, description, color=None, authorName=None, authorUrl=None, thumbnailUrl=None, imageUrl=None):
    embed = discord.Embed(
        title=title,
        colour=discord.Colour(hex_color_string_to_int(color)),
        description=description
        # url="https://www.google.com", # this is the link for title
    )

    if authorName != None:
        if authorUrl != None:
            embed.set_author(name=authorName, icon_url=authorUrl)
        else:
            embed.set_author(name=authorName)

    if thumbnailUrl != None:
        embed.set_thumbnail(url=thumbnailUrl)  # right image (small)

    if imageUrl != None:
        embed.set_image(url=imageUrl)  # bottom image (large)

    embed.set_footer(text="")
    return embed

async def clock(client, channelId, userId):
    await asyncio.sleep(60 * 60)
    channel = client.get_channel(channelId)
    str = "<@%d> 1 小時了，工作！" % (userId)
    if channel != None:
        await channel.send(str)


async def messageReact(self, client, ctx, isFromEdit=False):
    global isProxyMode, proxyList
    if ctx.author == self.user:
        return
    origin = ctx.content  # received message

    # preprocess
    rawMsg = origin.split(sep=" ")
    msg = rawMsg[0]
    CMD_PF = SQL.queryPrefixURL(ctx.guild.id)

    # gifs
    if (msg.lower() == 'a') or (msg.lower() == 'ａ') or (msg == 'ā') or (msg == 'あ') or (msg.lower() == 'aa'):
        await ctx.channel.send('A')
        dbUrl = SQL.queryUrl('a')
        if dbUrl != "":
            await showImg(ctx, dbUrl[0], dbUrl[1])

    # ayame counter
    elif msg.lower() == CMD_PF + 'ayame':
        url = 'https://script.googleusercontent.com/macros/echo?user_content_key=OspWpl4Qc16jCdPwz6_BPHH5AOV_Zq1NIzWa9La-IGzsetFs_geoxiLZ-LgDlp4TR3O5NZR5OHn1-eF4sK-NFMcmF9r1nS69m5_BxDlH2jW0nuo2oDemN9CCS2h10ox_1xSncGQajx_ryfhECjZEnNqVaIg6uWIusfaT6109P6AiX8-Jc70itxwf3vkR0F4vwX0NWBNrxNkTEKkvViUG5ASCAyw-o_Tv2w637yi-8rE7WE8Pq9zTnw&lib=Mv0Flh1wcXT8fGz2m4i_W0fGCLS4z58-Q'
        resp = requests.get(url).json()
        rawOnTime = datetime.strptime(resp["pubt"], "%Y-%m-%dT%H:%M:%SZ")
        diff = datetime.now()-rawOnTime
        hr = diff.seconds / 3600
        minute = (diff.seconds % 3600) / 60
        sec = diff.seconds % 60
        await ctx.channel.send('https://tenor.com/view/hololive-%E3%83%9B%E3%83%AD%E3%83%A9%E3%82%A4%E3%83%96-hologra-%E3%83%9B%E3%83%AD%E3%81%90%E3%82%89-nakiri-ayame-gif-23864357')
        await ctx.channel.send("百鬼距離上次開台過了 %d天 %d小時 %d分 %d秒" % (diff.days, hr, minute, sec))

    # leetcode
    elif msg.lower() == CMD_PF + 'leet':
        toSend = ""
        if len(rawMsg) == 1:
            toSend = LCC.fetch_daily_problem()
        else:
            return

        await ctx.delete()
        list = SQL.queryLeetChn(ctx.guild.id)
        if len(list) == 0:
            await ctx.channel.send(toSend)
        else:
            for i in list:
                chn = client.get_channel(int(i))
                await chn.send(toSend)

    elif msg.lower() == CMD_PF + 'leetrand':
        await ctx.delete()
        await ctx.channel.send(LCC.fetch_random_problem())

    # bot state
    elif msg.lower() == CMD_PF + 'cs':
        if len(rawMsg) <= 1:
            state = discord.Activity(
                type=discord.ActivityType.watching, name="Shaaaaaaark")
            await client.change_presence(status=discord.Status.idle, activity=state)
        else:
            state = discord.Activity(
                type=discord.ActivityType.watching, name=rawMsg[1])
            await client.change_presence(status=discord.Status.online, activity=state)

    # run script
    elif msg.lower() == CMD_PF + "sh":
        if len(rawMsg) == 2:
            path = SQL.queryScriptPath(rawMsg[1].lower())
            if path != None:
                result = subprocess.run(
                    ["sudo", "bash", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                await ctx.channel.send(result.stdout)

    # caller
    elif msg.lower().startswith(CMD_PF + 'call'):
        res = SQL.queryUser(ctx.content.lower().split("call")[1])
        if res != "":
            await ctx.channel.send('<@%s> %s' % (res[0], res[1]))
            if res[2] != "":
                await showImg(ctx, res[2], res[3])

    # poison soup
    elif msg.lower() == CMD_PF + 'poison':
        if len(rawMsg) == 2:
            try:
                cmd = int(rawMsg[1])
                soup = getPoisonSoup(cmd)
            except Exception:
                soup = getPoisonSoup()
        else:
            soup = getPoisonSoup()
        await ctx.channel.send(soup)

    # change name
    elif msg.lower() == CMD_PF + 'editname':
        data = origin.split(" ", 2)
        usrId = int(data[1][2:-1])
        usr = ctx.guild.get_member(usrId)
        if usr != None and data[2] != '':
            await usr.edit(nick=data[2])

    # exp
    elif msg.lower() == CMD_PF + 'exp':
        exp = SQL.queryUsrExp(ctx.author.id, ctx.guild.id)
        if exp != None:
            embed = embedCreator(title="經驗值",
                                 description="等級: Lv.%d\n總經驗: %d\n升至下一級還差: %d" % (
                                     exp[2], exp[0], exp[1]-exp[0]),
                                 color="#b9d3e9",
                                 authorName=ctx.author,
                                 thumbnailUrl=ctx.author.avatar_url)
            await ctx.channel.send(embed=embed)
        else:
            await ctx.channel.send("此伺服器尚未啟動經驗系統")

    # repo
    elif msg.lower() == CMD_PF + 'heart':
        await ctx.channel.send("幫古拉按個星星吧 <:gura_peek_wall:980739498474348595>\nhttps://github.com/allen870619/GuraDiscordBot")

    # thxhf
    elif msg.lower() == CMD_PF + 'thxhf':
        count = SQL.queryThxHf(ctx.author.id, ctx.guild.id)
        str = "<@%d> 已在本伺服器感謝HF **%d** 次, 真是太感謝了 <:gura_love_2:989819626282168321>" % (
            ctx.author.id, count)
        await ctx.channel.send(str)

    # thxhf here
    elif msg.lower() == CMD_PF + 'thxhfhere':
        count = SQL.queryThxHf(ctx.author.id, ctx.guild.id, ctx.channel.id)
        str = "<@%d> 已在 <#%d> 感謝HF **%d** 次, 真是太感謝了 <:gura_love_2:989819626282168321>" % (
            ctx.author.id, ctx.channel.id, count)
        await ctx.channel.send(str)

    elif msg.lower() == CMD_PF + 'cd':
        asyncio.create_task(clock(client, ctx.channel.id, ctx.author.id), name="Clock")
    
    # openai chat
    elif rawMsg[0].lower() == CMD_PF + "ask" and ctx.channel.id == 1078152776300896338:
        prompts = origin[5:]
        
        txt = send_chat(prompts, ctx.author.id)
        str = f"<@{ctx.author.id}> \n{txt}"
        await ctx.channel.send(str)
    
    # openai chat 
    elif (ctx.channel.id == 1081213613274050620 or ctx.channel.id == 1127251556690034738 or ctx.channel.id == 1239966332641087693) and len(origin) > 0:  
        response_text = send_chat(origin, user_id=ctx.author.id)
        await ctx.channel.send(response_text)

    # help
    elif msg == CMD_PF + '功能' or msg.lower() == CMD_PF + 'func' or msg.lower() == CMD_PF + 'help':
        await showImg(ctx, 'https://c.tenor.com/TgPXdDAfIeIAAAAd/gawr-gura-gura.gif', '#b9d3e9')
        helpShark = """
        ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
        ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
        ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⢛⠋⠉⠁⠄⠄⠄⠄⠄⠈⠙⠛⠻⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
        ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠛⠁⠄⣁⣤⣤⣤⣤⣤⣤⣄⡀⠄⠄⠰⠶⠎⠙⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
        ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠉⠄⣠⣶⠾⢛⡉⠩⣭⡭⠉⣭⣉⠻⣷⣦⡄⠄⠄⠄⠄⠙⢿⣿⣿⣿⣿⣿⣿⣿⣿
        ⣿⣿⣿⣿⣿⣿⣿⣿⡿⠃⢀⡴⢟⡉⢀⠻⠟⣸⡄⣃⣴⣆⠘⣉⡀⠠⣙⢿⣷⡄⠄⠄⠄⠄⢿⣿⣿⣿⣿⣿⣿⣿
        ⣿⣿⣿⣿⣿⣿⡿⠿⠄⢠⠾⣁⡸⢁⣼⣦⠾⢹⣿⣿⣿⠻⣾⣿⣷⣀⣀⢀⡻⣿⣄⠄⠄⠄⠄⠻⣿⣿⣿⣿⣿⣿
        ⣿⣿⣿⣿⡟⠋⠄⠄⣤⢣⣴⣿⡟⢻⣿⠟⢠⣿⣵⣿⣿⠄⢻⣿⣟⠻⣿⠄⠓⠘⣿⡄⠄⠄⠄⠄⢿⣿⣿⣿⣿⣿
        ⣿⣿⣿⠉⠄⠄⠄⢠⢁⡎⢹⠟⠡⠿⢇⡾⠘⠛⠛⠛⠛⣰⠸⠿⣿⡀⢿⡆⣿⣧⠘⣷⠄⠄⠄⠄⠈⣿⣿⣿⣿⣿
        ⣿⣿⡇⠄⠄⠄⠄⡎⣾⡇⣨⣴⣶⣶⣾⣬⣿⣿⣿⣿⣿⣉⣵⣶⣶⣦⠈⠃⢻⣿⣇⣿⡇⠄⠄⠄⠄⠹⣿⣿⣿⣿
        ⣿⣿⣿⣄⡀⠄⣸⢠⣿⣷⣿⡟⠄⠄⢘⣿⣿⣿⣿⣿⣿⣿⡿⠟⠛⠻⣿⡇⢸⣿⣿⠸⡇⠄⠄⠄⠄⠄⠘⣿⣿⣿
        ⣿⣿⣿⣿⡇⠄⡇⣸⣿⡿⡿⣻⣦⣤⣼⣿⢿⡿⢿⣿⡿⣿⣇⡀⠄⣀⣿⡇⣸⣿⣿⠄⡇⠄⠄⠄⠄⠄⠄⢻⣿⣿
        ⣿⣿⣿⣿⣷⠄⠁⣿⡏⠃⠛⢿⣿⣿⣿⣿⣤⣴⣤⣭⣴⣿⣿⣿⣟⣽⣿⢇⣿⣿⣿⢠⡇⠄⠄⠄⣠⣤⣤⣿⣿⣿
        ⣿⣿⣿⣿⣿⣷⠄⣿⡵⡔⢶⡾⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣟⠁⢚⣹⣿⣿⣼⠇⠄⠄⠄⣿⣿⣿⣿⣿⣿
        ⣿⣿⣿⣿⣿⣿⡆⣿⣹⣃⢀⠁⠂⠙⢡⣌⠻⠟⢉⠹⣿⠟⠋⢻⡿⠛⡟⢸⣿⣿⡏⠏⠄⠄⠄⢠⣿⣿⣿⣿⣿⣿
        ⣿⣿⣿⣿⣿⡿⠗⡸⣯⣿⡄⠿⣿⣿⣶⣤⣤⣈⣙⣃⠄⣛⣓⣀⣠⠤⠰⠻⢟⡏⠈⠄⠄⠄⣠⣿⣿⣿⣿⣿⣿⣿
        ⣿⣿⣿⣿⣿⣿⣤⣤⠻⣥⠈⣀⣨⣙⠛⠿⢿⣧⡤⠜⢂⡿⠿⠛⢃⠄⣤⡿⢛⣤⣤⠒⠚⠓⢈⣩⣽⣿⣿⣿⣿⣿
        ⣿⣿⣿⣿⣿⣿⣿⣿⣷⣬⣃⣙⣻⣿⣿⣶⣤⣤⣤⣤⣤⣴⣖⡛⢁⣚⣭⣤⣬⡙⠛⠄⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿
        ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
        """
        # 開頭
        intro = embedCreator(
            title="Gawr Gura 機器人 幫助清單",
            description=helpShark,
            color="#9db8de",
        )

        # leetcode
        leetcodeDesc = f'''
        # {CMD_PF}leet [ac] 每日題目 / 通過率
        # {CMD_PF}leetrand 隨機題目
        '''
        leetcode = embedCreator(
            title="---Leetcode功能---",
            description=leetcodeDesc,
            color="#819dd4",
        )

        # Others
        otherDesc = f'''
        # {CMD_PF}status 主機狀態
        # {CMD_PF}cs [state] 變更鯊魚狀態
        # {CMD_PF}editName <tag user> <nickname> 變更暱稱
        # {CMD_PF}getoff 下班倒數計時
        # {CMD_PF}ayame 百鬼開台計時器
        # {CMD_PF}poison [mode: 0雞湯, 1舔狗日記, 2社會語錄] 心靈毒雞湯
        # {CMD_PF}集合 / {CMD_PF}gather
        # {CMD_PF}exp 查看自己的經驗值
        # {CMD_PF}mijian 咪醬刪除紀錄
        # {CMD_PF}heart 查看古拉的心臟
        '''
        other = embedCreator(
            title="---其他功能---",
            description=otherDesc,
            color="#4967bf",
        )

        # Pic
        picDesc = ""
        for i in SQL.queryUrl():
            picDesc += "# %s\n" % (i)

        pic = embedCreator(
            title="---貼圖功能---",
            description=picDesc,
            color="#2e4db5",
        )

        await ctx.channel.send(embed=intro)
        await ctx.channel.send(embed=leetcode)
        await ctx.channel.send(embed=other)
        await ctx.channel.send(embed=pic)    
    else:
        # thxhf counter
        if msg.lower() == "thxhf":
            SQL.increaseThxHf(ctx.author.id, ctx.guild.id, ctx.channel.id)

        # text cmd
        textCmd = SQL.queryTextCmd(msg.lower())
        if textCmd is not None:
            await ctx.channel.send(textCmd)

        # 預設顯示圖床圖片
        dbUrl = SQL.queryUrl(ctx.content.lower())
        if dbUrl != "":
            if dbUrl[2] == True:
                await ctx.delete()
            if dbUrl[3] == True:
                await showImg(ctx, dbUrl[0], dbUrl[1])
            else:
                await ctx.channel.send(dbUrl[0])
    