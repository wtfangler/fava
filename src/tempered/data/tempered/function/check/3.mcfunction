# ERA 3 :: ZELAZO   (8 z 13 questow)
scoreboard players set #done tempered.data 0
execute if score #q.3a tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.3b tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.3c tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.3d tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.3e tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.3f tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.3g tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.3h tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.3i tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.3j tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.3k tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.3l tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.3m tempered.data matches 1 run scoreboard players add #done tempered.data 1

execute unless score #q.3a tempered.data matches 1 as @a store result score @s tempered.n run clear @s minecraft:iron_ingot 0
execute unless score #q.3a tempered.data matches 1 as @a[scores={tempered.n=5..}] run function tempered:quest/3a
execute unless score #q.3b tempered.data matches 1 as @a[scores={tempered.3b=1..}] run function tempered:quest/3b
execute unless score #q.3c tempered.data matches 1 as @a[scores={tempered.3c=1..}] run function tempered:quest/3c
execute unless score #q.3d tempered.data matches 1 as @a[scores={tempered.3d=1..}] run function tempered:quest/3d
execute unless score #q.3e tempered.data matches 1 as @a[scores={tempered.3e=1..}] run function tempered:quest/3e
execute unless score #q.3f tempered.data matches 1 as @a[scores={tempered.3f=10..}] run function tempered:quest/3f
execute unless score #q.3g tempered.data matches 1 as @a[scores={tempered.3g=1..}] run function tempered:quest/3g
execute unless score #q.3h tempered.data matches 1 as @a store result score @s tempered.n run clear @s minecraft:diamond 0
execute unless score #q.3h tempered.data matches 1 as @a[scores={tempered.n=1..}] run function tempered:quest/3h
execute unless score #q.3i tempered.data matches 1 as @a[scores={tempered.3i=1..}] run function tempered:quest/3i
execute unless score #q.3j tempered.data matches 1 as @a[scores={tempered.3j=10..}] run function tempered:quest/3j
execute unless score #q.3k tempered.data matches 1 as @a[scores={tempered.3k=5..}] run function tempered:quest/3k
execute unless score #q.3l tempered.data matches 1 as @a[scores={tempered.3l=1..}] run function tempered:quest/3l
execute unless score #q.3m tempered.data matches 1 as @a[scores={tempered.3m=300..}] run function tempered:quest/3m

execute if score #done tempered.data matches 8.. run function tempered:core/advance
