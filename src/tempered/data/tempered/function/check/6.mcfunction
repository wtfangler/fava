# ERA 6 :: END   (8 z 13 questow)
scoreboard players set #done tempered.data 0
execute if score #q.6a tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.6b tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.6c tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.6d tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.6e tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.6f tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.6g tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.6h tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.6i tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.6j tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.6k tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.6l tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.6m tempered.data matches 1 run scoreboard players add #done tempered.data 1

execute unless score #q.6a tempered.data matches 1 as @a store result score @s tempered.n run clear @s minecraft:ender_pearl 0
execute unless score #q.6a tempered.data matches 1 as @a[scores={tempered.n=4..}] run function tempered:quest/6a
execute unless score #q.6b tempered.data matches 1 as @a[scores={tempered.6b=1..}] run function tempered:quest/6b
execute unless score #q.6c tempered.data matches 1 as @a at @s if dimension minecraft:the_end run function tempered:quest/6c
execute unless score #q.6d tempered.data matches 1 as @a[scores={tempered.6d=5..}] run function tempered:quest/6d
execute unless score #q.6e tempered.data matches 1 as @a[scores={tempered.6e=1..}] run function tempered:quest/6e
execute unless score #q.6f tempered.data matches 1 as @a store result score @s tempered.n run clear @s minecraft:elytra 0
execute unless score #q.6f tempered.data matches 1 as @a[scores={tempered.n=1..}] run function tempered:quest/6f
execute unless score #q.6g tempered.data matches 1 as @a store result score @s tempered.n run clear @s minecraft:shulker_shell 0
execute unless score #q.6g tempered.data matches 1 as @a[scores={tempered.n=2..}] run function tempered:quest/6g
execute unless score #q.6h tempered.data matches 1 as @a store result score @s tempered.n run clear @s minecraft:chorus_fruit 0
execute unless score #q.6h tempered.data matches 1 as @a[scores={tempered.n=4..}] run function tempered:quest/6h
execute unless score #q.6i tempered.data matches 1 as @a[scores={tempered.6i=100000..}] run function tempered:quest/6i
execute unless score #q.6j tempered.data matches 1 as @a[scores={tempered.6j=20..}] run function tempered:quest/6j
execute unless score #q.6k tempered.data matches 1 as @a[scores={tempered.6k=10..}] run function tempered:quest/6k
execute unless score #q.6l tempered.data matches 1 as @a[scores={tempered.6l=1..}] run function tempered:quest/6l
execute unless score #q.6m tempered.data matches 1 as @a store result score @s tempered.n run clear @s minecraft:netherite_ingot 0
execute unless score #q.6m tempered.data matches 1 as @a[scores={tempered.n=1..}] run function tempered:quest/6m

execute if score #done tempered.data matches 8.. run function tempered:core/advance
