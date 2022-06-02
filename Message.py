import discord
import subprocess
import LeetcodeCrawler as LCC
import MusicModule
import time
from datetime import datetime
# 發圖片請求用
import requests
# Requests基本設定Class
from RequestSetting import *
import SQLConnect as SQL
from Utils import log, colorToHex
from PsutilSensor import getAllInfo

# utils
# getting img

# proxy chat
isProxyMode = False
proxyList=[]

# Utils: show image
async def showImg(ctx, targetUrl, color=None):
    embed = discord.Embed(color=colorToHex(color))
    embed.set_image(url=targetUrl)
    await ctx.channel.send(embed=embed)

# Utils: Embed
def embedCreator(title, description, color=None, authorName=None, authorUrl=None, thumbnailUrl = None, imageUrl = None):
    embed = discord.Embed(
        title=title,
        colour=discord.Colour(colorToHex(color)),
        description=description
        # url="https://www.google.com", # this is the link for title
    )
    
    if authorName != None:
        if authorUrl != None:            
            embed.set_author(name=authorName,icon_url=authorUrl)
        else:
            embed.set_author(name=authorName)

    if thumbnailUrl != None:
        embed.set_thumbnail(url=thumbnailUrl) # right image (small)

    if imageUrl != None:
        embed.set_image(url=imageUrl) # bottom image (large)

    embed.set_footer(text="")
    return embed

async def messageReact(self, client, ctx):
    global isProxyMode, proxyList
    if ctx.author == self.user:
        return
    origin = ctx.content  # received message

    # 直接播音樂模組: 頻道名稱有 '音樂' 或 'music' 才會觸發
    if "music" in ctx.channel.name or "音樂" in ctx.channel.name:
        if ctx.content.startswith("http"):
            origin = '!play ' + ctx.content # music channel directly paste url

    # preprocess
    rawMsg = origin.split(sep=" ")
    msg = rawMsg[0]
    CMD_PF = SQL.queryPrefixURL(ctx.guild.id)
    
    # proxy chat send
    if isProxyMode and "proxy" in ctx.channel.name:
        if origin == "!proxy":
            isProxyMode = False
            proxyList.clear()
            await ctx.channel.send("---代理聊天已結束---")
            return
        for i in proxyList:
            chn = client.get_channel(i)
            await chn.send(origin)
        return

    # voice channel
    if msg.lower() == CMD_PF+"join" or msg.lower() == CMD_PF+"j":
        await MusicModule.joining(ctx)

    elif msg.lower() == CMD_PF+"kick" or msg.lower() == CMD_PF+"k":
        await MusicModule.leaving(ctx)

    elif msg.lower() == CMD_PF+"play" or msg.lower() == CMD_PF+"p":
        try:
            # initial
            if MusicModule.vc == None:
                await MusicModule.joining(ctx)

            # play
            if len(rawMsg) > 1:  # with src
                localUrl = SQL.queryAlarmUrl(rawMsg[1])
                if localUrl != "":
                    MusicModule.playSource(localUrl)
                else:
                    MusicModule.playYT(rawMsg[1])
            else:
                if MusicModule.audioSource != None:
                    MusicModule.vc.resume()
                else:
                    MusicModule.playSource(SQL.queryAlarmUrl("4"))
        except Exception as e:
            log(e)
            await ctx.channel.send("發生錯誤ＱwＱ")

    elif msg.lower() == CMD_PF+"pause" or msg.lower() == CMD_PF+"pau":
        try:
            if MusicModule.is_playing:
                MusicModule.vc.pause()
        except:
            log("Nothing to pause")

    elif msg.lower() == CMD_PF+"next":
        try:
            if MusicModule.is_playing:
                MusicModule.vc.stop()
                MusicModule.is_playing = False
        except:
            log("Nothing to next")

    elif msg.lower() == CMD_PF+"stop":
        try:
            if MusicModule.is_playing:
                MusicModule.clearPlaylist()
                MusicModule.vc.stop()
                MusicModule.is_playing = False
        except:
            log("Nothing to stop")

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

    # get random waifu photo
    elif msg == "這是我的翅膀" or msg.lower() == 'anipic':
        dbUrl = SQL.queryUrl('這是我的翅膀')
        if dbUrl != "":
            try:
                response = requests.get(dbUrl[0], timeout=10)
                # Getting 307 redirected new url and send out
                if response.history:
                    await ctx.channel.send('認識一下😎')
                    await ctx.channel.send(response.url)
            except Exception as e:
                log(e)
        else:
            await ctx.channel.send('出現異常錯誤啦~~')

    # Get Technology Courses
    elif msg.lower() == "geek":
        # Split message
        try:
            # Determine the type of query
            dbUrl = SQL.queryUrl('geek')
            if dbUrl != "":
                try:
                    ressetting = RequestSetting()
                    # Setting Headers
                    ressetting.setHeaders(
                        {
                            "Content-Type": "application/json",
                            "Origin": "https://time.geekbang.org",
                            "Referer": "https://time.geekbang.org",
                            "Host": "time.geekbang.org"
                        }
                    )

                    response = requests.post(
                        dbUrl[0], json={'page': 'pc_home'}, headers=ressetting.getHeaders(), timeout=10).json()

                    # Response List: 8：直播（對應指令1） 1：小編推薦（對應指令2）
                    if(rawMsg[1] == '1'):
                        await ctx.channel.send('😎未來幾天的技術直播資訊')
                        await showImg(ctx, 'https://i.imgur.com/HXrWMXj.png')
                        for list in response['data']['list'][8]['list']:
                            await ctx.channel.send(
                                '標體：' + str(list['title']) + '\n' +
                                '描述：' + str(list['subtitle']) + '\n' +
                                '連結：' + str(list['live_url']) + '\n'
                            )
                            await showImg(ctx, list['cover'])
                    elif(rawMsg[1] == '2'):
                        await ctx.channel.send('😏今日推薦')
                        await showImg(ctx, 'https://i.imgur.com/HXrWMXj.png')
                        for list in response['data']['list'][1]['list']:
                            await ctx.channel.send(
                                '標體：' + str(list['main_title']) + '\n' +
                                '描述：' + str(list['reason']) + '\n' +
                                '連結：https://time.geekbang.org/dailylesson/detail/' +
                                str(list['sku']) + '\n'
                            )
                            await showImg(ctx, list['cover'])
                    else:
                        await ctx.channel.send('目前只有1跟2而已哦~~例如可以輸入geek 1')
                except Exception as e:
                    log(e)
            else:
                await ctx.channel.send('出現異常錯誤啦~~')
        except:
            await ctx.channel.send('我猜你是想要查詢geek的資訊，請輸入 geek 1\n 1：技術直播資訊 2：今日推薦～')

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
        rawOnTime=datetime.strptime(resp["pubt"], "%Y-%m-%dT%H:%M:%SZ")
        diff=datetime.now()-rawOnTime
        hr = diff.seconds / 3600
        minute = (diff.seconds % 3600) / 60
        sec = diff.seconds % 60
        await ctx.channel.send('https://tenor.com/view/hololive-%E3%83%9B%E3%83%AD%E3%83%A9%E3%82%A4%E3%83%96-hologra-%E3%83%9B%E3%83%AD%E3%81%90%E3%82%89-nakiri-ayame-gif-23864357')
        await ctx.channel.send("百鬼距離上次開台過了 %d天 %d小時 %d分 %d秒"%(diff.days, hr, minute,sec))

    # get off counter
    elif msg.lower() == CMD_PF + 'getoff':
        y = time.localtime().tm_year
        M = time.localtime().tm_mon
        D = time.localtime().tm_mday
        h = time.localtime().tm_hour
        m = time.localtime().tm_min
        s = time.localtime().tm_sec
        nowDate = datetime(y,M,D,h,m,s)
        off = datetime(y,M,D,17,30,00)
        diff = off-nowDate
        imgSrc = SQL.queryUrl("getoff")
        if diff.days < 0:
            await ctx.channel.send("下班摟~")
            if len(imgSrc) != 0:
                await showImg(ctx, imgSrc[0] ,imgSrc[1])
        else:
            sec = diff.seconds
            if sec >= 34200:
                await ctx.channel.send("還沒上班拉")
            else:
                hh = sec / 3600
                mm = (sec % 3600) / 60
                ss = sec % 60
                await ctx.channel.send("還有 %d小時%d分%d秒 下班~"%(hh, mm, ss))

    # proxy chat mode
    elif msg.lower() == CMD_PF + "proxy":
        if len(rawMsg) == 2:
            isProxyMode = True
            cmd = rawMsg[1]
            proxyList = SQL.queryProxyChat(cmd)
            if len(proxyList) == 0:
                isProxyMode = False
                await ctx.channel.send("---指令錯誤---")
            else:
                await ctx.channel.send("---代理聊天已啟動---")

    # leetcode
    elif msg.lower() == CMD_PF + 'leet':
        toSend = ""
        if len(rawMsg) == 1:
            toSend = LCC.dailyProblem()
        elif len(rawMsg) == 2 and rawMsg[1].lower() == 'ac':
            toSend = LCC.dailyProblemAC()
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
        await ctx.channel.send(LCC.randProblem())

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
            path=SQL.queryScriptPath(rawMsg[1].lower())
            if path != None:
                result=subprocess.run(["sudo","bash",path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                await ctx.channel.send(result.stdout)

    # caller
    elif msg.lower().startswith(CMD_PF + 'call'):
        res = SQL.queryUser(ctx.content.lower().split("call")[1])
        if res != "":
            await ctx.channel.send('<@%s> %s' % (res[0], res[1]))
            if res[2] != "":
                await showImg(ctx, res[2], res[3])

    # change name
    elif msg.lower() == CMD_PF + 'editname':
        data=origin.split(" ", 2)
        usrId = int(data[1][2:-1])
        usr = ctx.guild.get_member(usrId)
        if usr != None and data[2] != '':
            await usr.edit(nick=data[2])

    # exp
    elif msg.lower() == CMD_PF + 'exp':
        exp = SQL.queryUsrExp(ctx.author.id, ctx.guild.id)
        if exp != None:
            embed=embedCreator(title="經驗值",
            description="等級: Lv.%d\n總經驗: %d\n升至下一級還差: %d"%(exp[2],exp[0],exp[1]-exp[0]),
            color="#b9d3e9",
            authorName=ctx.author,
            thumbnailUrl=ctx.author.avatar_url)
            await ctx.channel.send(embed=embed)
        else:
            await ctx.channel.send("此伺服器尚未啟動經驗系統")

    # stickers
    elif msg.lower() == 'gcf' and ctx.guild.id == 870855015676391505:
        await ctx.delete()
        await ctx.channel.send('<:gura_confuse:922084439733973013>')

    elif msg.lower() == 'gmm' and ctx.guild.id == 870855015676391505:
        await ctx.delete()
        await ctx.channel.send('<:gura_meom:922084440178561044>')

    elif msg.lower() == 'gfcn' and ctx.guild.id == 870855015676391505:
        await ctx.delete()
        await ctx.channel.send('<:gura_fascinate:922084439822053377>')

    elif msg.lower() == 'ghp' and ctx.guild.id == 870855015676391505:
        await ctx.delete()
        await ctx.channel.send('<:gura_happy:922084439717187644>')

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
        leetcodeDesc='''
        # %sleet [ac] 每日題目 / 通過率
        # %sleetrand 隨機題目
        '''% (CMD_PF, CMD_PF)
        leetcode = embedCreator(
            title="---Leetcode功能---",
            description=leetcodeDesc,
            color="#819dd4",
        )

        # Music
        musicDesc='''
        # %sjoin / %skick 
        -呼叫/趕走唱歌的鯊鯊(請在語音頻道使用)
        # %splay [1, 2, 3, 4, <url>] 
        -鯊鯊語音(1,2,3,4為鬧鐘, 預設4)/恢復暫停播放
        # %spause -暫停
        # %sstop -停止(清單會被清除)
        # %snext -清單下一首
        # %slist [clear] -清單/清單清除
        '''% (CMD_PF, CMD_PF, CMD_PF, CMD_PF, CMD_PF, CMD_PF, CMD_PF)
        music = embedCreator(
            title="---鯊魚廣播---",
            description=musicDesc,
            color="#6582c9",
        )

        # Others
        otherDesc='''
        # %sstatus 主機狀態
        # %scs [state] 變更鯊魚狀態
        # %seditName <tag user> <nickname> 變更暱稱
        # %sgetoff 下班倒數計時
        # %sayame 百鬼開台計時器
        # %s集合 / %sgather
        # %sexp 查看自己的經驗值
        '''% (CMD_PF, CMD_PF, CMD_PF, CMD_PF, CMD_PF, CMD_PF, CMD_PF, CMD_PF)
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
        await ctx.channel.send(embed=other)
        await ctx.channel.send(embed=pic)            

    else:
        # 預設顯示圖床圖片
        dbUrl = SQL.queryUrl(ctx.content.lower())
        if dbUrl != "":
            if dbUrl[2] == True:
                await ctx.delete()
            if dbUrl[3] == True:
                await showImg(ctx, dbUrl[0], dbUrl[1])
            else:
                await ctx.channel.send(dbUrl[0])


async def memeWarning(self, client, ctx, memo=None):
    if ctx.author == self.user:
        return
    chn = client.get_channel(929379945346629642)
    if memo == None or memo == '':
        await chn.send('<@%s> 不要在梗圖版打字 <:gura_angry:922084439813673001>' % (ctx.author.id))
    else:
        await chn.send('<@%s> %s' % (ctx.author.id, memo))
