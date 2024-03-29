import secrets
import DrawSQL
# 全部都用1/10000計算


# 抽取分區


def drawRarity(rarityList):
    value = secrets.randbelow(9999)+1
    sumRary = 0
    for rarity in rarityList:
        sumRary += rarity.probability * 100
        if value <= sumRary:
            return rarity
    return None

# 抽取卡片


def drawSingleCard(cardList):
    value = secrets.randbelow(9999)+1
    sumRary = 0
    for card in cardList:
        sumRary += card.probability * 100
        if value <= sumRary:
            return card
    return None


def drawCard(usrId, guildId, time):
    rarityList = DrawSQL.queryRarity()
    cardDict = {}
    cards = []
    for _ in range(0, time):
        rarityPart = drawRarity(rarityList)
        if cardDict.get(rarityPart.id) is None:
            cardDict[rarityPart.id] = DrawSQL.queryCard(rarityPart)
        cards.append(drawSingleCard(cardDict[rarityPart.id]))
        DrawSQL.addDrawRecord(usrId, guildId, cards[-1])
    return cards


# 卡池
def cardPool():
    list = []
    rarityList = DrawSQL.queryRarity()
    for rarity in rarityList:
        list.append((rarity, DrawSQL.queryCard(rarity)))
    return list

# 分解卡片
def decomposeCard(usrId, guildId, id, num):
    count = DrawSQL.getUsrCardCount(usrId, guildId, id)
    if count == -1:
        return None
    else:
        result = DrawSQL.decomposeCard(usrId, guildId, id, num, count)
        return result
    

# debug
def test():
    patition = DrawSQL.queryRarity()
    for i in range(0, 10000):
        rarityPart = drawRarity(patition)
        card = drawSingleCard(DrawSQL.queryCard(rarityPart)) 
        if i % 100 == 0:
            print(i)
        if card.id == 25:
            print(card.name)
        # print("%s卡 ! 恭喜你抽到 *%s*" % (card.rarityData.name, card.name))
    # print(decomposeCard(405739307517870110, 870855015676391505, 18, 5))
    print("end")
    
# test()