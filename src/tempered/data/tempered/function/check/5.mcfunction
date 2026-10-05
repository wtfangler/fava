# ERA 5 :: NETHER   (9 z 14 questow)
scoreboard players set #done tempered.data 0
execute if score #q.5a tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.5b tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.5c tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.5d tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.5e tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.5f tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.5g tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.5h tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.5i tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.5j tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.5k tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.5l tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.5m tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.5n tempered.data matches 1 run scoreboard players add #done tempered.data 1

execute unless score #q.5a tempered.data matches 1 as @a[scores={tempered.5a=1..}] run function tempered:quest/5a
execute unless score #q.5b tempered.data matches 1 as @a at @s if dimension minecraft:the_nether run function tempered:quest/5b
execute unless score #q.5c tempered.data matches 1 as @a store result score @s tempered.n run clear @s minecraft:blaze_rod 0
execute unless score #q.5c tempered.data matches 1 as @a[scores={tempered.n=2..}] run function tempered:quest/5c
execute unless score #q.5d tempered.data matches 1 as @a[scores={tempered.5d=1..}] run function tempered:quest/5d
execute unless score #q.5e tempered.data matches 1 as @a store result score @s tempered.n run clear @s minecraft:nether_wart 0
execute unless score #q.5e tempered.data matches 1 as @a[scores={tempered.n=4..}] run function tempered:quest/5e
execute unless score #q.5f tempered.data matches 1 as @a[scores={tempered.5f=1..}] run function tempered:quest/5f
execute unless score #q.5g tempered.data matches 1 as @a store result score @s tempered.n run clear @s minecraft:quartz 0
execute unless score #q.5g tempered.data matches 1 as @a[scores={tempered.n=8..}] run function tempered:quest/5g
execute unless score #q.5h tempered.data matches 1 as @a store result score @s tempered.n run clear @s minecraft:ancient_debris 0
execute unless score #q.5h tempered.data matches 1 as @a[scores={tempered.n=1..}] run function tempered:quest/5h
execute unless score #q.5i tempered.data matches 1 as @a[scores={tempered.5i=10..}] run function tempered:quest/5i
execute unless score #q.5j tempered.data matches 1 as @a[scores={tempered.5j=2000..}] run function tempered:quest/5j
execute unless score #q.5k tempered.data matches 1 as @a[scores={tempered.5k=5..}] run function tempered:quest/5k
execute unless score #q.5l tempered.data matches 1 as @a[scores={tempered.5l=20000..}] run function tempered:quest/5l
execute unless score #q.5m tempered.data matches 1 as @a[scores={tempered.5m=1..}] run function tempered:quest/5m
execute unless score #q.5n tempered.data matches 1 as @a store result score @s tempered.n run clear @s minecraft:netherite_scrap 0
execute unless score #q.5n tempered.data matches 1 as @a[scores={tempered.n=4..}] run function tempered:quest/5n

execute if score #done tempered.data matches 9.. run function tempered:core/advance
