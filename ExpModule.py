import SQLConnect as SQL

def addUsrExp(usrId, guildId):
    exp = SQL.queryUsrExp(usrId, guildId)
    if exp == None:
        # append new user
        SQL.addExpUsr(usrId, guildId)
        exp = SQL.queryUsrExp(usrId, guildId)
    SQL.increaseUsrExp(usrId, guildId)
    exp = (exp[0]+1, exp[1], exp[2])
    return exp

def upgradeUsrLv(usrId, guildId):
    SQL.upgradeUsrLv(usrId, guildId)