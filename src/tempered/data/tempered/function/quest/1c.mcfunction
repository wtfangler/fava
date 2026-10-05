execute if score #q.1c tempered.data matches 1 run return 0
scoreboard players set #q.1c tempered.data 1
scoreboard players add #done tempered.data 1
advancement grant @a only tempered:quest/1/1c
experience add @a 20 points
execute as @a at @s run playsound minecraft:entity.player.levelup master @s ~ ~ ~ 0.6 1.6
tellraw @a ["",{"color":"dark_gray","bold":false,"translate":"tempered.ui.quest_done"},{"color":"gray","bold":true,"translate":"tempered.quest.1c.title"},{"text":"   +20 XP","color":"green","bold":false}]
