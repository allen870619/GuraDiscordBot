
import discord
import DiscordHelper

async def x_video_url_renamer(message: discord.Message, client: discord.Client):
    # get original message
    # check whether has https://x.com/ or https://twitter.com/
    # delete, replace and send it back to channel

    originMessage =  message.content
    if "https://x.com/" in originMessage:
        originMessage = originMessage.replace("https://x.com/", "https://vxtwitter.com/")
    elif "https://twitter.com/" in originMessage:
        originMessage = originMessage.replace("https://twitter.com/", "https://vxtwitter.com/")
    else:
        return

    await message.delete()
    await DiscordHelper.send_message(originMessage, client=client, channel_id=message.channel.id)