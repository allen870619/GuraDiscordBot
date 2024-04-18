import time
import discord.message


def generate_log(message_context: discord.message, is_edit: bool):
    log_string = ""

    # user
    log_string += "%s" % (message_context.author)
    if message_context.author.nick != None:
        log_string += "(%s)" % (message_context.author.nick)

    # main context
    edit_mark = ""
    if is_edit:
        edit_mark = "[Edited] "
    if message_context.content != '':
        log_string += " @ %s/%s: %s%s" % (message_context.guild,
                                      message_context.channel.name, edit_mark, message_context.content)
    else:
        log_string += " @ %s/%s %s" % (message_context.guild,
                                   message_context.channel.name, edit_mark)
    
    # attachments
    for i in message_context.attachments:
        log_string += "\n\t [attachments] %s" % (i.url)
    
    return log_string

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