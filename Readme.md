![Platform](https://img.shields.io/badge/Lang-Python-blue)
![Date](https://img.shields.io/github/last-commit/allen870619/GuraDiscordBot?style=flat)
# Gura Discord Bot
> 可i的Gura

## 目前功能
1. 訊息模組: Message.py
2. 音樂模組: MusicModule.py
3. Leetcode爬蟲發題目: LeetcodeCrawler.py

## 引用核心模組
* Discord.py
* EnvData
* ffmpeg
* youtube-dl
* psutil


## 架構說明
### Main
主要進入點為main.py, 啟動方式
```
python3 main.py
```

### Message
負責處理指令的模組, 有filter掛在main底下
主要有call人, 發圖片, 音樂控制指令判讀等

### MusicModule
音樂處理模組, 有Gura鬧鐘 跟 YT音樂播放

### EnvData
放Token, 路徑等等重要資料

### SQLConnect
連接db的模組

### Exp

### DB連動
部分圖庫會連到DB後取得圖片連結跟目標UserId, 回傳後在由Message發送

## 常用指令
```
!help (前綴請根據DB, 預設為!)
```