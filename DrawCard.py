import random
import DrawSQL
# 全部都用1/10000計算


# 抽取分區


def drawRarity(rarityList):
    value = random.randint(1, 10000)
    sumRary = 0
    for rarity in rarityList:
        sumRary += rarity.probability * 100
        if value <= sumRary:
            return rarity
    return None

# 抽取卡片


def drawSingleCard(cardList):
    value = random.randint(1, 10000)
    sumRary = 0
    for card in cardList:
        sumRary += card.probability * 100
        if value <= sumRary:
            return card
    return None


def drawCard(usrId, guildId):
    rarityPart = drawRarity(DrawSQL.queryRarity())
    card = drawSingleCard(DrawSQL.queryCard(rarityPart))
    # add to record
    DrawSQL.addDrawRecord(usrId, guildId, card)
    return card


# 卡池
def cardPool():
    list = []
    rarityList = DrawSQL.queryRarity()
    for rarity in rarityList:
        list.append((rarity, DrawSQL.queryCard(rarity)))
    return list


# debug
def test():
    a = DrawSQL.queryRarity()
    for i in range(0, 500):
        rarityPart = drawRarity(a)
        card = drawSingleCard(DrawSQL.queryCard(rarityPart))
        print("%s卡 ! 恭喜你抽到 *%s*" % (card.rarityData.name, card.name))
