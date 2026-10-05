scoreboard players add #age tempered.data 1
scoreboard players set #done tempered.data 0
execute if score #age tempered.data matches 2 run function tempered:age/2
execute if score #age tempered.data matches 3 run function tempered:age/3
execute if score #age tempered.data matches 4 run function tempered:age/4
execute if score #age tempered.data matches 5 run function tempered:age/5
execute if score #age tempered.data matches 6 run function tempered:age/6
execute if score #age tempered.data matches 7 run function tempered:age/7
execute if score #age tempered.data matches 8.. run scoreboard players set #age tempered.data 8
execute if score #age tempered.data matches 8 run function tempered:age/done
