# ERA 7 :: POST-END   (8 z 12 questow)
scoreboard players set #done tempered.data 0
execute if score #q.7a tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.7b tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.7c tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.7d tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.7e tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.7f tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.7g tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.7h tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.7i tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.7j tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.7k tempered.data matches 1 run scoreboard players add #done tempered.data 1
execute if score #q.7l tempered.data matches 1 run scoreboard players add #done tempered.data 1

execute unless score #q.7a tempered.data matches 1 as @a[scores={tempered.7a=1..}] run function tempered:quest/7a
execute unless score #q.7b tempered.data matches 1 as @a store result score @s tempered.n run clear @s minecraft:nether_star 0
execute unless score #q.7b tempered.data matches 1 as @a[scores={tempered.n=1..}] run function tempered:quest/7b
execute unless score #q.7c tempered.data matches 1 as @a[scores={tempered.7c=1..}] run function tempered:quest/7c
execute unless score #q.7d tempered.data matches 1 as @a store result score @s tempered.n run clear @s minecraft:totem_of_undying 0
execute unless score #q.7d tempered.data matches 1 as @a[scores={tempered.n=1..}] run function tempered:quest/7d
execute unless score #q.7e tempered.data matches 1 as @a[scores={tempered.7e=1..}] run function tempered:quest/7e
execute unless score #q.7f tempered.data matches 1 as @a store result score @s tempered.n run clear @s minecraft:emerald 0
execute unless score #q.7f tempered.data matches 1 as @a[scores={tempered.n=16..}] run function tempered:quest/7f
execute unless score #q.7g tempered.data matches 1 as @a[scores={tempered.7g=500..}] run function tempered:quest/7g
execute unless score #q.7h tempered.data matches 1 as @a[scores={tempered.7h=5000000..}] run function tempered:quest/7h
execute unless score #q.7i tempered.data matches 1 as @a[scores={tempered.7i=1..}] run function tempered:quest/7i
execute unless score #q.7j tempered.data matches 1 as @a[scores={tempered.7j=5..}] run function tempered:quest/7j
execute unless score #q.7k tempered.data matches 1 as @a[scores={tempered.7k=50..}] run function tempered:quest/7k
execute unless score #q.7l tempered.data matches 1 as @a[scores={tempered.7l=8000..}] run function tempered:quest/7l

execute if score #done tempered.data matches 8.. run function tempered:core/advance
