# get log and save
# docker log --tail 500 >> "chat_$(date +"%Y-%m-%dT%H:%M:%S").log"

# build all
docker stop gura
docker rm gura
docker create --name gura allen870619/gura_discord_bot
docker start gura
