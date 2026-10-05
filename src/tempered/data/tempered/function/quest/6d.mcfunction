execute if score #q.6d tempered.data matches 1 run return 0
scoreboard players set #q.6d tempered.data 1
scoreboard players add #done tempered.data 1
advancement grant @a only tempered:quest/6/6d
experience add @a 60 points
execute as @a at @s run playsound minecraft:entity.player.levelup master @s ~ ~ ~ 0.6 1.6
tellraw @a ["",{"color":"dark_gray","bold":false,"translate":"tempered.ui.quest_done"},{"color":"aqua","bold":true,"translate":"tempered.quest.6d.title"},{"text":"   +60 XP","color":"green","bold":false}]
