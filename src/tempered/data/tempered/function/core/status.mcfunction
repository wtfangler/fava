scoreboard players set @s tempered.menu 0
scoreboard players enable @s tempered.menu
tellraw @s ["",{"text":"\n  TEMPERED  //  STATUS","color":"gold","bold":true}]
execute if score #age tempered.data matches 1 run function tempered:core/status_1
execute if score #age tempered.data matches 2 run function tempered:core/status_2
execute if score #age tempered.data matches 3 run function tempered:core/status_3
execute if score #age tempered.data matches 4 run function tempered:core/status_4
execute if score #age tempered.data matches 5 run function tempered:core/status_5
execute if score #age tempered.data matches 6 run function tempered:core/status_6
execute if score #age tempered.data matches 7 run function tempered:core/status_7
execute if score #age tempered.data matches 8 run tellraw @s ["",{"translate":"tempered.msg.status.end","color":"gold","bold":false}]
