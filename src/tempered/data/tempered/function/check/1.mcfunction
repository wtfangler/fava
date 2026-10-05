# ERA 1 :: DREWNO   (6 z 9 questow)
scoreboard players set #done tempered.data 0
execute if score #q.1a tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.1b tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.1c tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.1d tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.1e tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.1f tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.1g tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.1h tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.1i tempered.data matches 1 run scoreboard players add #done tempered.data 1

execute unless score #q.1a tempered.data matches 1 as @a store result score @s tempered.n run clear @s #minecraft:logs 0
execute unless score #q.1a tempered.data matches 1 as @a[scores={tempered.n=1..}] run function tempered:quest/1a
execute unless score #q.1b tempered.data matches 1 as @a[scores={tempered.1b=1..}] run function tempered:quest/1b
execute unless score #q.1c tempered.data matches 1 as @a[scores={tempered.1c=1..}] run function tempered:quest/1c
execute unless score #q.1d tempered.data matches 1 as @a store result score @s tempered.n run clear @s #minecraft:planks 0
execute unless score #q.1d tempered.data matches 1 as @a[scores={tempered.n=32..}] run function tempered:quest/1d
execute unless score #q.1e tempered.data matches 1 as @a[scores={tempered.1e=1..}] run function tempered:quest/1e
execute unless score #q.1f tempered.data matches 1 as @a[scores={tempered.1f=1..}] run function tempered:quest/1f
execute unless score #q.1g tempered.data matches 1 as @a[scores={tempered.1g=1..}] run function tempered:quest/1g
execute unless score #q.1h tempered.data matches 1 as @a[scores={tempered.1h=3000..}] run function tempered:quest/1h
execute unless score #q.1i tempered.data matches 1 as @a[scores={tempered.1i=1..}] run function tempered:quest/1i

execute if score #done tempered.data matches 6.. run function tempered:core/advance
