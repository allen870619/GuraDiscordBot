import discord
import subprocess
import LeetcodeCrawler as LCC
import MusicModule
from datetime import datetime
# 抽卡
from DrawCard import drawCard, cardPool, decomposeCard
import DrawSQL
# 發圖片請求用
import requests
# Requests基本設定Class
import SQLConnect as SQL
from package.Utils.Utils import flush_log, hex_color_string_to_int
from PsutilSensor import getAllInfo
# 雞湯
from PoisonSoup import getPoisonSoup
# openai
from openaiChat import openai_txt_chat, openai_gpt_chat

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


async def messageReact(self, client, ctx, isFromEdit=False):
    global isProxyMode, proxyList
    if ctx.author == self.user:
        return
    origin = ctx.content  # received message

    # 直接播音樂模組: 頻道名稱有 '音樂' 或 'music' 才會觸發
    if "music" in ctx.channel.name or "音樂" in ctx.channel.name:
        if ctx.content.startswith("http"):
            urlList = origin.split("\n")
            origin = ""
            for cmd in urlList:
                if cmd.startswith("http"):
                    origin += '!play ' + cmd + "\n" # music channel directly paste url

    # preprocess
    rawMsg = origin.split(sep=" ")
    msg = rawMsg[0]
    CMD_PF = SQL.queryPrefixURL(ctx.guild.id)

    # voice channel
    if msg.lower() == CMD_PF+"join" or msg.lower() == CMD_PF+"j":
        await MusicModule.joining(ctx)

    elif msg.lower() == CMD_PF+"kick" or msg.lower() == CMD_PF+"k":
        await MusicModule.leaving(ctx)

    elif msg.lower() == CMD_PF+"play" or msg.lower() == CMD_PF+"p":
        if isFromEdit:
            return
        try:
            # initial
            if MusicModule.vc is None:
                await MusicModule.joining(ctx)

            # play
            if len(rawMsg) > 1:  # with src
                localUrl = SQL.queryAlarmUrl(rawMsg[1])
                if localUrl != "":
                    MusicModule.playSource(localUrl)
                else:
                    urlList = origin.split("\n")
                    for eachCmd in urlList:
                        urlSplit = eachCmd.split(" ")
                        if len(urlSplit) > 1:
                            ytRawLink = urlSplit[1].split("&")[0]
                            MusicModule.playYT(ytRawLink)
            else:
                if MusicModule.audioSource != None:
                    MusicModule.vc.resume()
                else:
                    MusicModule.playSource(SQL.queryAlarmUrl("4"))
        except Exception as e:
            flush_log(e)
            await ctx.channel.send("發生錯誤ＱwＱ")

    elif msg.lower() == CMD_PF+"pause" or msg.lower() == CMD_PF+"pau":
        try:
            if MusicModule.is_playing:
                MusicModule.vc.pause()
        except Exception:
            flush_log("Nothing to pause")

    elif msg.lower() == CMD_PF+"next":
        try:
            if MusicModule.is_playing:
                MusicModule.vc.stop()
                MusicModule.is_playing = False
        except Exception:
            flush_log("Nothing to next")

    elif msg.lower() == CMD_PF+"stop":
        try:
            if MusicModule.is_playing:
                MusicModule.clearPlaylist()
                MusicModule.vc.stop()
                MusicModule.is_playing = False
        except Exception:
            flush_log("Nothing to stop")

    elif msg.lower() == CMD_PF+"list":
        if len(rawMsg) == 1:
            if len(MusicModule.getPlaylist()) == 0:
                await ctx.channel.send("清單是空的OuO")
            else:
                str1 = "待播歌曲:\n"
                for i in MusicModule.getPlaylist():
                    str1 += i + "\n"
                await ctx.channel.send(str1)
        else:
            if rawMsg[1] == "clear":
                MusicModule.clearPlaylist()
                await ctx.channel.send("清單已清除")

    # gifs
    elif (msg.lower() == 'a') or (msg.lower() == 'ａ') or (msg == 'ā') or (msg == 'あ') or (msg.lower() == 'aa'):
        await ctx.channel.send('A')
        dbUrl = SQL.queryUrl('a')
        if dbUrl != "":
            await showImg(ctx, dbUrl[0], dbUrl[1])

    elif (msg == CMD_PF+"集合") or (msg.lower() == CMD_PF+"gather") or (msg.lower() == CMD_PF+"g"):
        allowed_mentions = discord.AllowedMentions(everyone=True)
        await ctx.channel.send(content="@everyone 集合嘍～～", allowed_mentions=allowed_mentions)
        await showImg(ctx, 'https://c.tenor.com/agmJYnSKj50AAAAC/gwar-gura-gura.gif')

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
            toSend = LCC.dailyProblem()
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

    # computer info
    elif msg.lower() == CMD_PF + 'status':
        await ctx.channel.send(getAllInfo())

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

    # 抽卡機
    # 抽卡
    elif rawMsg[0].lower() == CMD_PF + 'draw':
        # get desire draw time
        if len(rawMsg) == 1:
            times = 1
        else:
            try:
                times = int(rawMsg[1])
                if times > 50: 
                    times = 50
            except Exception:
                times = 1

        # calculate coins and free
        actualDraw = 0
        containFreeDraw = False
        coin = DrawSQL.getUsrDrawCoin(ctx.author.id, ctx.guild.id)
        free = DrawSQL.getFreeDraw(ctx.author.id, ctx.guild.id)
        allFree = free
        for _ in range(0, times):
            if coin < DrawSQL.drawCost and free == 0:
                break
            actualDraw += 1
            hasFree = free > 0
            if hasFree:
                free -= 1
            else:
                coin -= DrawSQL.drawCost
            DrawSQL.drawConsume(ctx.author.id, ctx.guild.id, hasFree)

        # discount when draw 10 cards
        costDraw = actualDraw - allFree
        if actualDraw >= 10 and costDraw > 0:
            for _ in range(0, int(costDraw / 10)):
                DrawSQL.drawAddCoin(ctx.author.id, ctx.guild.id, 5)

        # send message
        if actualDraw > 0:
            cards = drawCard(ctx.author.id, ctx.guild.id, actualDraw)

            await ctx.channel.send('抽卡 %d 張   <:gura_fascinate:922084439822053377>' % (actualDraw))
            cardAlert = ""
            for index, card in enumerate(cards):
                if card.id == 1:
                    allowed_mentions = discord.AllowedMentions(everyone=True)
                    await ctx.channel.send(content="@everyone 全員注意!!", allowed_mentions=allowed_mentions)
                    await ctx.channel.send('恭喜<@%s> 抽到 鯊魚本人\n%s卡「 *%s* 」!!!!!!' % (ctx.author.id, card.rarityData.name, card.name))
                else:
                    cardAlert += "恭喜<@%s> 抽到 %s卡「 *%s* 」\n" % (
                        ctx.author.id, card.rarityData.name, card.name)
                if (index+1) % 10 == 0 and cardAlert != "":
                    await ctx.channel.send(cardAlert)
                    cardAlert = ""
            if cardAlert != "":
                await ctx.channel.send(cardAlert)
        else:
            await ctx.channel.send("代幣不足 <:gura_cry:922084439465553920>")

    # 卡池
    elif msg.lower() == CMD_PF + 'drawpool':
        pool = cardPool()
        embedList = []
        colorList = ["#ec695e", "#ab5d75", "#6a518c", "#2a46a4"]
        colorIndex = 0
        for data in pool:
            rarity = data[0]
            cardList = data[1]

            # form up text
            title = "%s 卡池 (%s%%)\n分解 %d 金幣" % (
                rarity.name, rarity.probability, rarity.decompose)
            strCardList = ""
            for card in cardList:
                strCardList += "%d. %s \n -> %s%%\n" % (card.id,
                                                        card.name,
                                                        card.probability)

            embedList.append(embedCreator(
                title, strCardList, colorList[colorIndex]))
            colorIndex += 1

        for i in embedList:
            await ctx.channel.send(embed=i)

    # 代幣餘額
    elif msg.lower() == CMD_PF + "drawcoin":
        coin = DrawSQL.getUsrDrawCoin(ctx.author.id, ctx.guild.id)
        free = DrawSQL.getFreeDraw(ctx.author.id, ctx.guild.id)
        await ctx.channel.send("<@%d> 剩餘代幣: %d, 免費次數: %d" % (ctx.author.id, coin, free))

    # 查詢自己有的卡
    elif msg.lower() == CMD_PF + "mycard":
        list = DrawSQL.getUsrCardList(ctx.author.id, ctx.guild.id)
        if len(list) == 0:
            await ctx.channel.send("<@%d>卡片空空如也 0.0" % (ctx.author.id))
            return

        allData = "<@%d> 持有的卡片\n" % (ctx.author.id)
        for data in list:
            # form up text
            allData += "-----%s 卡-----\n" % (data[0]["rarity_name"])
            for card in data:
                allData += "%s. %s : %s張\n" % (card["card_id"],
                                               card["card_name"],
                                               card["card_mount"])
            allData += "\n"
        await ctx.channel.send(allData)

    # 分解卡片
    elif rawMsg[0].lower() == CMD_PF + "decomp":
        if len(rawMsg) == 3:
            try:
                id = int(rawMsg[1])
                count = int(rawMsg[2])
                isPass = True
            except e:
                isPass = False
        elif len(rawMsg) == 2:
            try:
                id = int(rawMsg[1])
                count = 1
                isPass = True
            except e:
                isPass = False
        else:
            await ctx.channel.send("指令錯誤 <:gura_angry:922084439813673001>")
            isPass = False
        if isPass:
            result = decomposeCard(ctx.author.id, ctx.guild.id, id, count)
            if result is None:
                await ctx.channel.send("你沒有這張卡 <:gura_cry:922084439465553920>")
            else:
                await ctx.channel.send("<@%d> 分解%d張卡, 獲得%d枚金幣" % (ctx.author.id, result[0], result[1]))

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
    
    # openai chat
    elif rawMsg[0].lower() == CMD_PF + "ask" and ctx.channel.id == 1078152776300896338:
        prompts = origin[5:]
        
        txt = openai_txt_chat(prompts)
        str = f"<@{ctx.author.id}> \n{txt}"
        await ctx.channel.send(str)
    
    # openai chat
    elif (ctx.channel.id == 1081213613274050620 or ctx.channel.id == 1127251556690034738) and len(origin) > 0:
        resp = openai_gpt_chat(origin, user_id=ctx.author.id)
        await ctx.channel.send(resp)

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

        # Music
        musicDesc = f'''
        # {CMD_PF}join / {CMD_PF}kick 
        -呼叫/趕走唱歌的鯊鯊(請在語音頻道使用)
        # {CMD_PF}play [1, 2, 3, 4, <url>] 
        -鯊鯊語音(1,2,3,4為鬧鐘, 預設4)/恢復暫停播放
        # {CMD_PF}pause -暫停
        # {CMD_PF}stop -停止(清單會被清除)
        # {CMD_PF}next -清單下一首
        # {CMD_PF}list [clear] -清單/清單清除
        '''
        music = embedCreator(
            title="---鯊魚廣播---",
            description=musicDesc,
            color="#6582c9",
        )

        # Draw
        drawCardDesc = f'''
        # {CMD_PF}draw [time=1] 抽卡[次數, 最多10張]
        # {CMD_PF}drawPool 卡池資訊
        # {CMD_PF}drawCoin 查詢剩餘代幣
        # {CMD_PF}mycard 查詢持有的卡片
        # {CMD_PF}decomp <id> [count=1] 分解持有的卡片
        '''
        drawCardHint = embedCreator(
            title="---血統認證機(開發中)---",
            description=drawCardDesc,
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
        await ctx.channel.send(embed=music)
        await ctx.channel.send(embed=drawCardHint)
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
        else:
            # 增加代幣
            DrawSQL.drawAddCoin(ctx.author.id, ctx.guild.id)
    