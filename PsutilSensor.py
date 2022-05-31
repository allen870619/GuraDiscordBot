import psutil
import datetime
import time
import math

# cpu
def getCpuUsage():
    # cpu usage(single)
    cpuUsage = psutil.cpu_percent(interval=1, percpu=False)
    # cpu usage free
    # cpuUsageFree = psutil.cpu_times_percent().idle
    return cpuUsage

# Only on Linux
def getCpuTemp():
    # cpu temp
    try:
        cpuTemp = psutil.sensors_temperatures()['coretemp'][0].current
    except AttributeError:
        cpuTemp = -1000
    return cpuTemp

def getCpuFreq(mode):
    if(mode == 0):
        return psutil.cpu_freq(percpu=False).current
    elif(mode == 1):
        return psutil.cpu_freq(percpu=False).min
    elif(mode == 2):
        return psutil.cpu_freq(percpu=False).max

# mem
def getMemUsage():
    return psutil.virtual_memory().percent

# uptime
def getUptime():
    now = time.time()
    rawUptime = math.floor(now - psutil.boot_time())
    return datetime.timedelta(seconds=rawUptime)

# info
def getComputerInfo():
    data = {}
    cpuCore = psutil.cpu_count(logical=False)
    cpuThread = psutil.cpu_count(logical=True)
    memTotal = psutil.virtual_memory().total/1024/1024
    data["cpuCore"] = cpuCore
    data["cpuThread"] = cpuThread
    data["memTotal"] = memTotal
    return data

def getAllInfo():
    usage = getCpuUsage()
    temp = getCpuTemp()
    freq = getCpuFreq(0)
    memUsage = getMemUsage()
    uptime = getUptime().seconds
    d = getUptime().days
    h = uptime / 3600
    m = (uptime % 3600) / 60
    s = uptime % 60
    return "Cpu使用率: %.1f %%\nCpu 溫度:  %.1f ºC\nCpu頻率:   %d Mhz\nRAM使用率: %.1f %%\n開機時間:  %d天 %d小時 %d分 %d秒"%(usage, temp, freq, memUsage,d ,h ,m, s)