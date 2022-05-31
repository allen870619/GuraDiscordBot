import time

def getTime():
    return str(time.strftime("%Y/%m/%d %a %H:%M:%S,", time.localtime()))

def log(str):
    print(getTime(), str, flush=True)

# format: #XXXXXX
def colorToHex(color):
    desireColor = "#000000"
    if color != None and color != "":
        desireColor = color

    sixteenIntegerHex = int(desireColor.replace("#", ""), 16)
    return int(hex(sixteenIntegerHex), 0)