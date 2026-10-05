# ERA 4 :: DIAMENT   (8 z 13 questow)
scoreboard players set #done tempered.data 0
execute if score #q.4a tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.4b tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.4c tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.4d tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.4e tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.4f tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.4g tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.4h tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.4i tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.4j tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.4k tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.4l tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.4m tempered.data matches 1 run scoreboard players add #done tempered.data 1

execute unless score #q.4a tempered.data matches 1 as @a store result score @s tempered.n run clear @s minecraft:diamond 0
execute unless score #q.4a tempered.data matches 1 as @a[scores={tempered.n=3..}] run function tempered:quest/4a
execute unless score #q.4b tempered.data matches 1 as @a[scores={tempered.4b=1..}] run function tempered:quest/4b
execute unless score #q.4c tempered.data matches 1 as @a store result score @s tempered.n run clear @s minecraft:obsidian 0
execute unless score #q.4c tempered.data matches 1 as @a[scores={tempered.n=10..}] run function tempered:quest/4c
execute unless score #q.4d tempered.data matches 1 as @a[scores={tempered.4d=1..}] run function tempered:quest/4d
execute unless score #q.4e tempered.data matches 1 as @a[scores={tempered.4e=1..}] run function tempered:quest/4e
execute unless score #q.4f tempered.data matches 1 as @a[scores={tempered.4f=1..}] run function tempered:quest/4f
execute unless score #q.4g tempered.data matches 1 as @a store result score @s tempered.n run clear @s minecraft:gold_ingot 0
execute unless score #q.4g tempered.data matches 1 as @a[scores={tempered.n=5..}] run function tempered:quest/4g
execute unless score #q.4h tempered.data matches 1 as @a[scores={tempered.4h=1..}] run function tempered:quest/4h
execute unless score #q.4i tempered.data matches 1 as @a[scores={tempered.4i=3..}] run function tempered:quest/4i
execute unless score #q.4j tempered.data matches 1 as @a[scores={tempered.4j=10..}] run function tempered:quest/4j
execute unless score #q.4k tempered.data matches 1 as @a[scores={tempered.4k=10..}] run function tempered:quest/4k
execute unless score #q.4l tempered.data matches 1 as @a[scores={tempered.4l=30000..}] run function tempered:quest/4l
execute unless score #q.4m tempered.data matches 1 as @a[scores={tempered.4m=5..}] run function tempered:quest/4m

execute if score #done tempered.data matches 8.. run function tempered:core/advance
