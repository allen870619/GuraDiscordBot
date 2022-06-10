from SQLConnect import connect

# 基礎資料

drawCost = 10

# 等級分區


class RarityEntity:
    def __init__(self, id, name, probability) -> None:
        super().__init__()
        self.id = id
        self.name = name
        self.probability = probability

# 卡片資料包


class CardEntity:
    def __init__(self, id, name, probability, rarityData) -> None:
        super().__init__()
        self.id = id
        self.name = name
        self.probability = probability
        self.rarityData = rarityData
        self.wholeProb = rarityData.probability * self.probability / 100

# 金錢控制
# 取得抽卡金幣


def getUsrDrawCoin(usrId, guildId):
    connection = connect()
    with connection.cursor() as cursor:
        sql = "SELECT * FROM `CardUsrData` WHERE `usr_id`=%s AND `guild_id`=%s" % (
            usrId, guildId)
        cursor.execute(sql)
        result = cursor.fetchone()
        if result == None:
            # 初始化資料
            sql = "SELECT `exp` FROM `ExpUsrTable` WHERE `usr_id`=%s AND `guild_id`=%s" % (
                usrId, guildId)
            cursor.execute(sql)
            result = cursor.fetchone()
            value = 0
            if result != None:
                value = result["exp"]
                value = int(value/3)  # 預設抽卡寶石為經驗值/3

            sql = "INSERT INTO `CardUsrData` (`usr_id`, `guild_id`, `draw_coin`) VALUES (%d, %d, %d)" % (
                usrId, guildId, value)
            cursor.execute(sql)
            connection.commit()
            return value
        else:
            return result["draw_coin"]

# 抽卡


def drawConsume(usrId, guildId, drawCost=drawCost):
    connection = connect()
    with connection.cursor() as cursor:
        sql = "UPDATE `CardUsrData` SET `draw_coin`=`draw_coin`-%d WHERE `usr_id` = %d AND `guild_id` = %d" % (
            drawCost, usrId, guildId)
        cursor.execute(sql)
        connection.commit()

# 加錢


def drawAddCoin(usrId, guildId, addCoin=1):
    connection = connect()
    with connection.cursor() as cursor:
        sql = "UPDATE `CardUsrData` SET `draw_coin`=`draw_coin`+%d WHERE `usr_id` = %d AND `guild_id` = %d" % (
            addCoin, usrId, guildId)
        cursor.execute(sql)
        connection.commit()

# 卡片資料
# 取得分區資料


def queryRarity():
    connection = connect()
    with connection.cursor() as cursor:
        sql = "SELECT * FROM CardRarity ORDER BY probability ASC"
        cursor.execute(sql)
        result = cursor.fetchall()
        if len(result) == 0:
            return []
        else:
            list = []
            for i in result:
                rarity = RarityEntity(i["id"], i["name"], i["probability"])
                list.append(rarity)
            return list

# 取得特定等級的卡片資料


def queryCard(rarityData):
    connection = connect()
    with connection.cursor() as cursor:
        sql = "SELECT * FROM CardPool WHERE `rarity` = %s ORDER BY probability ASC"
        cursor.execute(sql, rarityData.id)
        result = cursor.fetchall()
        list = []
        if len(result) == 0:
            return list
        else:
            for i in result:
                card = CardEntity(i["id"], i["name"],
                                  i["probability"], rarityData)
                list.append(card)
            return list

# 新增抽卡資料到紀錄中


def addDrawRecord(usrId, guildId, card):
    connection = connect()
    with connection.cursor() as cursor:
        sql = "SELECT COUNT(*) as total FROM `CardUsrProperty` WHERE `usr_id` = %d AND `guild_id`=%s AND `card_id`=%s" % (
            usrId, guildId, card.id)
        cursor.execute(sql)
        result = cursor.fetchone()
        count = result["total"]
        if count > 0:  # update
            sql = "UPDATE `CardUsrProperty` SET `card_mount`=`card_mount`+1 WHERE `usr_id` = %d AND `guild_id` = %d AND `card_id`=%s" % (
                usrId, guildId, card.id)
        else:  # create
            sql = "INSERT INTO `CardUsrProperty` (`usr_id`, `guild_id`, `card_id`, `card_mount`) VALUES (%d, %d, %d, %d)" % (
                usrId, guildId, card.id, 1)
        cursor.execute(sql)
        connection.commit()

# 取得使用者個卡片清單


def getUsrCardList(usrId, guildId):
    connection = connect()
    with connection.cursor() as cursor:
        sql = "SELECT B.name AS rarity_name,A.name AS card_name,A.card_mount,A.rarity FROM(SELECT usr_id,guild_id,card_mount,CardPool.*FROM CardUsrProperty INNER JOIN CardPool ON CardUsrProperty.card_id=CardPool.id)AS A LEFT JOIN CardRarity AS B ON A.rarity=B.id WHERE A.usr_id=%d AND A.guild_id=%d ORDER BY A.rarity,A.probability ASC" % (
            usrId, guildId)
        cursor.execute(sql)
        result = cursor.fetchall()
        list = []
        last = -1
        tmpList = []
        for i in result:
            if i["rarity"] != last:
                last = i["rarity"]
                if len(tmpList) != 0:
                    list.append(tmpList.copy())
                    tmpList.clear()
            tmpList.append(i)
        if len(tmpList) != 0:
            list.append(tmpList.copy())
        return list

# debug


# def test():
    # # get coin
    # print(getUsrDrawCoin(405739307517870110, 870855015676391505))
    # # draw
    # print(drawConsume(405739307517870110, 870855015676391505))
    # # after
    # print(getUsrDrawCoin(405739307517870110, 870855015676391505))
