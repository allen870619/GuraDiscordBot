import time

def flush_log(message):
    current_time = str(time.strftime("%Y/%m/%d %a %H:%M:%S,", time.localtime()))
    print(current_time, message, flush=True)

# format: #XXXXXX
def hex_color_string_to_int(color):
    desire_color = "#000000"
    if color != None and color != "":
        desire_color = color

    hex_value = int(desire_color.replace("#", ""), 16)
    return int(hex(hex_value), 0)