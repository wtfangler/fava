execute if score #q.2l tempered.data matches 1 run return 0
scoreboard players set #q.2l tempered.data 1
scoreboard players add #done tempered.data 1
advancement grant @a only tempered:quest/2/2l
experience add @a 20 points
execute as @a at @s run playsound minecraft:entity.player.levelup master @s ~ ~ ~ 0.6 1.6
tellraw @a ["",{"color":"dark_gray","bold":false,"translate":"tempered.ui.quest_done"},{"color":"gray","bold":true,"translate":"tempered.quest.2l.title"},{"text":"   +20 XP","color":"green","bold":false}]
