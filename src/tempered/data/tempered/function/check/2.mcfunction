# ERA 2 :: KAMIEN   (9 z 15 questow)
scoreboard players set #done tempered.data 0
execute if score #q.2a tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.2b tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.2c tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.2d tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.2e tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.2f tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.2g tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.2h tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.2i tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.2j tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.2k tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.2l tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.2m tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.2n tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.2o tempered.data matches 1 run scoreboard players add #done tempered.data 1

execute unless score #q.2a tempered.data matches 1 as @a store result score @s tempered.n run clear @s minecraft:cobblestone 0
execute unless score #q.2a tempered.data matches 1 as @a[scores={tempered.n=32..}] run function tempered:quest/2a
execute unless score #q.2b tempered.data matches 1 as @a[scores={tempered.2b=1..}] run function tempered:quest/2b
execute unless score #q.2c tempered.data matches 1 as @a[scores={tempered.2c=1..}] run function tempered:quest/2c
execute unless score #q.2d tempered.data matches 1 as @a store result score @s tempered.n run clear @s #minecraft:coals 0
execute unless score #q.2d tempered.data matches 1 as @a[scores={tempered.n=8..}] run function tempered:quest/2d
execute unless score #q.2e tempered.data matches 1 as @a[scores={tempered.2e=4..}] run function tempered:quest/2e
execute unless score #q.2f tempered.data matches 1 as @a[scores={tempered.2f=64..}] run function tempered:quest/2f
execute unless score #q.2g tempered.data matches 1 as @a store result score @s tempered.n run clear @s minecraft:raw_iron 0
execute unless score #q.2g tempered.data matches 1 as @a[scores={tempered.n=3..}] run function tempered:quest/2g
execute unless score #q.2h tempered.data matches 1 as @a[scores={tempered.2h=1..}] run function tempered:quest/2h
execute unless score #q.2i tempered.data matches 1 as @a[scores={tempered.2i=20..}] run function tempered:quest/2i
execute unless score #q.2j tempered.data matches 1 as @a[scores={tempered.2j=5..}] run function tempered:quest/2j
execute unless score #q.2k tempered.data matches 1 as @a[scores={tempered.2k=1..}] run function tempered:quest/2k
execute unless score #q.2l tempered.data matches 1 as @a store result score @s tempered.n run clear @s minecraft:copper_ingot 0
execute unless score #q.2l tempered.data matches 1 as @a[scores={tempered.n=8..}] run function tempered:quest/2l
execute unless score #q.2m tempered.data matches 1 as @a run scoreboard players set @s tempered.n 0
execute unless score #q.2m tempered.data matches 1 as @a run scoreboard players operation @s tempered.n += @s tempered.2m1
execute unless score #q.2m tempered.data matches 1 as @a run scoreboard players operation @s tempered.n += @s tempered.2m2
execute unless score #q.2m tempered.data matches 1 as @a[scores={tempered.n=32..}] run function tempered:quest/2m
execute unless score #q.2n tempered.data matches 1 as @a[scores={tempered.2n=1..}] run function tempered:quest/2n
execute unless score #q.2o tempered.data matches 1 as @a[scores={tempered.2o=1..}] run function tempered:quest/2o

execute if score #done tempered.data matches 9.. run function tempered:core/advance
