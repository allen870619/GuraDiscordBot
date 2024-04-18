import discord

async def send_message(message: str, client: discord.Client, channel_id:int):
    channel = client.get_channel(channel_id)
    if channel != None:
        await channel.send(message)