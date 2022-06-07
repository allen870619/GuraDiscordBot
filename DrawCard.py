import random
from SQLConnect import connect

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

# 取得分區資料
# 給出 [(RarityEntity, sumRarity)]

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
            probVal = 0
            for i in result:
                probVal += (i["probability"] * 100)
                rarity = RarityEntity(i["id"], i["name"], i["probability"])
                list.append((rarity, probVal))
            return list

# 取得特定等級的卡片資料
# 給出 [(CardEntity, sumRarity)]

def queryCard(rarityData):
    connection = connect()
    with connection.cursor() as cursor:
        sql = "SELECT * FROM CardPool WHERE `rarity` = %s ORDER BY probability ASC"
        cursor.execute(sql, rarityData.id)
        result = cursor.fetchall()
        if len(result) == 0:
            return []
        else:
            list = []
            probVal = 0
            for i in result:
                probVal += (i["probability"] * 100)
                card = CardEntity(i["id"], i["name"],
                                  i["probability"], rarityData)
                list.append((card, probVal))
            return list

# 抽取分區


def drawRarity(rarityList):
    value = random.randint(0, 10000)
    for i in rarityList:
        if i[1] > value:
            return i[0]
    return None

# 抽取卡片


def drawSingleCard(cardList):
    draw = random.randint(0, 10000)
    for i in cardList:
        if i[1] > draw:
            return i[0]
    return None


def drawCard():
    rarityPart = drawRarity(queryRarity())
    card = drawSingleCard(queryCard(rarityPart))
    return card


# 卡池
def cardPool():
    list = []
    rp = queryRarity() # rarityPart
    for i in rp:
        re = i[0] # rarityEntity
        list.append((re, queryCard(re)))
    return list

def test():
    for i in range(0, 50):
        card = drawCard()
        print("%s卡 ! 恭喜你抽到 *%s*" % (card.rarityData.name, card.name))
