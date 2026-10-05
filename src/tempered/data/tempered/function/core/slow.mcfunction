scoreboard players set #clock tempered.data 0
execute if score #gate tempered.data matches 1 run function tempered:core/locks
execute if score #age tempered.data matches 1 run function tempered:check/1
execute if score #age tempered.data matches 2 run function tempered:check/2
execute if score #age tempered.data matches 3 run function tempered:check/3
execute if score #age tempered.data matches 4 run function tempered:check/4
execute if score #age tempered.data matches 5 run function tempered:check/5
execute if score #age tempered.data matches 6 run function tempered:check/6
execute if score #age tempered.data matches 7 run function tempered:check/7
execute as @a[scores={tempered.menu=1..}] run function tempered:core/status
