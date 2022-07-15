import pymysql.cursors
from EnvData import DB_URL, DB_USR, DB_PW, DB_DATABASE

def connect():
    return pymysql.connect(host=DB_URL,
                           user=DB_USR,
                           password=DB_PW,
                           database=DB_DATABASE,
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)


def queryUrl(cmd=None):
    connection = connect()
    with connection.cursor() as cursor:
        if cmd != None:
            sql = "SELECT * FROM PicCmd WHERE `cmd` = %s"
            cursor.execute(sql, cmd)
        else:
            sql = "SELECT * FROM PicCmd WHERE `show_in_help` = 1 ORDER BY `cmd` asc"
            cursor.execute(sql, cmd)
        result = cursor.fetchall()
        if len(result) == 0:
            return ""
        elif cmd == None:
            list = []
            for i in result:
                list.append(i["cmd"])
            return (list)
        else:
            return (result[0]["url"], result[0]["color"], result[0]["need_delete"], result[0]["need_embed"])


def queryPrefixURL(channel):
    connection = connect()
    with connection.cursor() as cursor:
        sql = "SELECT `prefix` FROM ServerCmdPrefix WHERE `server_id` = %s"
        cursor.execute(sql, channel)
        result = cursor.fetchone()
        if result == None:
            return ""
        else:
            return result["prefix"]


def queryUser(callName):
    connection = connect()
    with connection.cursor() as cursor:
        sql = "SELECT `id`, `message`, `image_url`, `color` FROM User NATURAL JOIN Caller WHERE `call_name` = %s"
        cursor.execute(sql, callName)
        result = cursor.fetchone()
        if result == None:
            return ""
        else:
            return (result["id"], result["message"], result["image_url"], result["color"])


def queryAlarmUrl(callCmd):
    connection = connect()
    with connection.cursor() as cursor:
        sql = "SELECT `path` FROM AlarmSrc WHERE `call_cmd` = %s"
        cursor.execute(sql, callCmd)
        result = cursor.fetchone()
        if result == None:
            return ""
        else:
            return (result["path"])


def queryLeetChn(guild=None):
    connection = connect()
    with connection:
        with connection.cursor() as cursor:
            if guild == None:
                sql = "SELECT `chn_id` FROM LeetBroadcast WHERE `enable` is True"
                cursor.execute(sql)
            else:
                sql = "SELECT `chn_id` FROM LeetBroadcast WHERE `enable` is True and `guild_id` = %s"
                cursor.execute(sql, guild)
            result = cursor.fetchall()
            list = []
            for i in result:
                list.append(i["chn_id"])
            return list

def queryProxyChat(cmd):
    connection = connect()
    with connection.cursor() as cursor:
        sql = "SELECT chn_id FROM ProxyChat WHERE `cmd` = %s"
        cursor.execute(sql, cmd)   
        result = cursor.fetchall()
        if len(result) == 0:
            return []
        else:
            list = []
            for i in result:
                list.append(int(i["chn_id"]))
            return (list)

def queryScriptPath(cmd):
    connection = connect()
    with connection.cursor() as cursor:
        sql = "SELECT path FROM ScriptTable WHERE `cmd` = %s"
        cursor.execute(sql, cmd)   
        result = cursor.fetchone()
        if result == None:
                return None
        else:
            return (result["path"])

# Exp System
def queryEnableExpSys(guildId):
    connection = connect()
    with connection.cursor() as cursor:
        sql = "SELECT `brodcast_chn`, `is_avbl` FROM ExpSystem WHERE `guild_id` = %s" %(guildId)
        cursor.execute(sql)
        result = cursor.fetchone()
        if result == None:
                return None
        else:
            return (result["brodcast_chn"], result["is_avbl"])

def queryUsrExp(usrId, guildId):
    connection = connect()
    with connection.cursor() as cursor:
        sql = "SELECT `max`, `level`, `exp` FROM ExpUsrTable NATURAL JOIN ExpLevel WHERE `usr_id` = %s AND `guild_id` = %s"
        cursor.execute(sql, (usrId, guildId))
        result = cursor.fetchone()
        if result == None:
                return None
        else:
            return (result["exp"], result["max"], result["level"])

def addExpUsr(usrId, guildId):
    connection = connect()
    with connection.cursor() as cursor:
        sql = "INSERT INTO `ExpUsrTable` (`usr_id`, `guild_id`) VALUES (%d, %d)" %(usrId, guildId)
        cursor.execute(sql)
        connection.commit()

def increaseUsrExp(usrId, guildId, value=1):
    connection = connect()
    with connection.cursor() as cursor:
        sql = "UPDATE ExpUsrTable SET `exp`=`exp`+%d WHERE `usr_id` = %d AND `guild_id` = %d" %(value, usrId, guildId)
        cursor.execute(sql)
        connection.commit()

def upgradeUsrLv(usrId, guildId):
    connection = connect()
    with connection.cursor() as cursor:
        sql = "UPDATE ExpUsrTable SET `level`=`level`+1 WHERE `usr_id` = %d AND `guild_id` = %d" %(usrId, guildId)
        cursor.execute(sql)
        connection.commit()

