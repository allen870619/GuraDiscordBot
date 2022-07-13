import psutil
import numpy as np
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
    uptime = getUptime().seconds
    hr = int(uptime / 3600)
    min = int((uptime % 3600) / 60)
    sec = uptime % 60
    msg = f"CPU 使用率: {np.round(getCpuUsage(), 1)}%\n"
    msg += f"CPU 溫度: {np.round(getCpuTemp(), 1)} ºC\n"
    msg += f"CPU 頻率: {int(getCpuFreq(0))} Mhz\n"
    msg += f"RAM 使用率: {np.round(getMemUsage(), 1)}%\n"
    msg += f"開機時間:  {getUptime().days}天 {hr}小時 {min}分 {sec}秒"
    return msg