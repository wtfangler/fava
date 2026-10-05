execute as @a[tag=!tempered.player] run function tempered:core/join
# A player absent during an administrative reset must discard their old UI too.
execute as @a unless score @s tempered.gen matches 0.. run scoreboard players set @s tempered.gen 0
execute as @a unless score @s tempered.bonusgen matches 0.. run scoreboard players set @s tempered.bonusgen 0
execute as @a unless score @s tempered.gen = #generation tempered.data run function tempered:core/reset_player
execute as @a[scores={tempered.left=1..}] run function tempered:core/rejoin
# zdjecie blokady sprawdzane co tick, ale tylko dla graczy aktualnie zablokowanych
execute as @a[scores={tempered.lock=1..}] run function tempered:core/release
scoreboard players add #clock tempered.data 1
execute if score #clock tempered.data matches 5.. run function tempered:core/slow
