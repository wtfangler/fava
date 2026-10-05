execute if score #q.7k tempered.data matches 1 run return 0
scoreboard players set #q.7k tempered.data 1
scoreboard players add #done tempered.data 1
advancement grant @a only tempered:quest/7/7k
experience add @a 150 points
execute as @a at @s run playsound minecraft:entity.player.levelup master @s ~ ~ ~ 0.6 1.6
tellraw @a ["",{"color":"dark_gray","bold":false,"translate":"tempered.ui.quest_done"},{"color":"light_purple","bold":true,"translate":"tempered.quest.7k.title"},{"text":"   +150 XP","color":"green","bold":false}]
