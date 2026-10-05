# item z wyzszej ery w rece/na sobie = blokada uzycia (mining fatigue + weakness)
scoreboard players set @a tempered.lockn 0

execute if score #age tempered.data matches ..1 as @a[gamemode=!creative,gamemode=!spectator] if items entity @s weapon.mainhand #tempered:tier/2 run function tempered:lock/2
execute if score #age tempered.data matches ..1 as @a[gamemode=!creative,gamemode=!spectator] if items entity @s weapon.offhand #tempered:tier/2 run function tempered:lock/2
execute if score #age tempered.data matches ..1 as @a[gamemode=!creative,gamemode=!spectator] if items entity @s armor.head #tempered:tier/2 run function tempered:lock/2
execute if score #age tempered.data matches ..1 as @a[gamemode=!creative,gamemode=!spectator] if items entity @s armor.chest #tempered:tier/2 run function tempered:lock/2
execute if score #age tempered.data matches ..1 as @a[gamemode=!creative,gamemode=!spectator] if items entity @s armor.legs #tempered:tier/2 run function tempered:lock/2
execute if score #age tempered.data matches ..1 as @a[gamemode=!creative,gamemode=!spectator] if items entity @s armor.feet #tempered:tier/2 run function tempered:lock/2
execute if score #age tempered.data matches ..2 as @a[gamemode=!creative,gamemode=!spectator] if items entity @s weapon.mainhand #tempered:tier/3 run function tempered:lock/3
execute if score #age tempered.data matches ..2 as @a[gamemode=!creative,gamemode=!spectator] if items entity @s weapon.offhand #tempered:tier/3 run function tempered:lock/3
execute if score #age tempered.data matches ..2 as @a[gamemode=!creative,gamemode=!spectator] if items entity @s armor.head #tempered:tier/3 run function tempered:lock/3
execute if score #age tempered.data matches ..2 as @a[gamemode=!creative,gamemode=!spectator] if items entity @s armor.chest #tempered:tier/3 run function tempered:lock/3
execute if score #age tempered.data matches ..2 as @a[gamemode=!creative,gamemode=!spectator] if items entity @s armor.legs #tempered:tier/3 run function tempered:lock/3
execute if score #age tempered.data matches ..2 as @a[gamemode=!creative,gamemode=!spectator] if items entity @s armor.feet #tempered:tier/3 run function tempered:lock/3
execute if score #age tempered.data matches ..3 as @a[gamemode=!creative,gamemode=!spectator] if items entity @s weapon.mainhand #tempered:tier/4 run function tempered:lock/4
execute if score #age tempered.data matches ..3 as @a[gamemode=!creative,gamemode=!spectator] if items entity @s weapon.offhand #tempered:tier/4 run function tempered:lock/4
execute if score #age tempered.data matches ..3 as @a[gamemode=!creative,gamemode=!spectator] if items entity @s armor.head #tempered:tier/4 run function tempered:lock/4
execute if score #age tempered.data matches ..3 as @a[gamemode=!creative,gamemode=!spectator] if items entity @s armor.chest #tempered:tier/4 run function tempered:lock/4
execute if score #age tempered.data matches ..3 as @a[gamemode=!creative,gamemode=!spectator] if items entity @s armor.legs #tempered:tier/4 run function tempered:lock/4
execute if score #age tempered.data matches ..3 as @a[gamemode=!creative,gamemode=!spectator] if items entity @s armor.feet #tempered:tier/4 run function tempered:lock/4
execute if score #age tempered.data matches ..4 as @a[gamemode=!creative,gamemode=!spectator] if items entity @s weapon.mainhand #tempered:tier/5 run function tempered:lock/5
execute if score #age tempered.data matches ..4 as @a[gamemode=!creative,gamemode=!spectator] if items entity @s weapon.offhand #tempered:tier/5 run function tempered:lock/5
execute if score #age tempered.data matches ..4 as @a[gamemode=!creative,gamemode=!spectator] if items entity @s armor.head #tempered:tier/5 run function tempered:lock/5
execute if score #age tempered.data matches ..4 as @a[gamemode=!creative,gamemode=!spectator] if items entity @s armor.chest #tempered:tier/5 run function tempered:lock/5
execute if score #age tempered.data matches ..4 as @a[gamemode=!creative,gamemode=!spectator] if items entity @s armor.legs #tempered:tier/5 run function tempered:lock/5
execute if score #age tempered.data matches ..4 as @a[gamemode=!creative,gamemode=!spectator] if items entity @s armor.feet #tempered:tier/5 run function tempered:lock/5
execute if score #age tempered.data matches ..5 as @a[gamemode=!creative,gamemode=!spectator] if items entity @s weapon.mainhand #tempered:tier/6 run function tempered:lock/6
execute if score #age tempered.data matches ..5 as @a[gamemode=!creative,gamemode=!spectator] if items entity @s weapon.offhand #tempered:tier/6 run function tempered:lock/6
execute if score #age tempered.data matches ..5 as @a[gamemode=!creative,gamemode=!spectator] if items entity @s armor.head #tempered:tier/6 run function tempered:lock/6
execute if score #age tempered.data matches ..5 as @a[gamemode=!creative,gamemode=!spectator] if items entity @s armor.chest #tempered:tier/6 run function tempered:lock/6
execute if score #age tempered.data matches ..5 as @a[gamemode=!creative,gamemode=!spectator] if items entity @s armor.legs #tempered:tier/6 run function tempered:lock/6
execute if score #age tempered.data matches ..5 as @a[gamemode=!creative,gamemode=!spectator] if items entity @s armor.feet #tempered:tier/6 run function tempered:lock/6
execute if score #age tempered.data matches ..6 as @a[gamemode=!creative,gamemode=!spectator] if items entity @s weapon.mainhand #tempered:tier/7 run function tempered:lock/7
execute if score #age tempered.data matches ..6 as @a[gamemode=!creative,gamemode=!spectator] if items entity @s weapon.offhand #tempered:tier/7 run function tempered:lock/7
execute if score #age tempered.data matches ..6 as @a[gamemode=!creative,gamemode=!spectator] if items entity @s armor.head #tempered:tier/7 run function tempered:lock/7
execute if score #age tempered.data matches ..6 as @a[gamemode=!creative,gamemode=!spectator] if items entity @s armor.chest #tempered:tier/7 run function tempered:lock/7
execute if score #age tempered.data matches ..6 as @a[gamemode=!creative,gamemode=!spectator] if items entity @s armor.legs #tempered:tier/7 run function tempered:lock/7
execute if score #age tempered.data matches ..6 as @a[gamemode=!creative,gamemode=!spectator] if items entity @s armor.feet #tempered:tier/7 run function tempered:lock/7

# debuff: krotki (1 s) i odnawiany, dopoki item jest trzymany/noszony
execute as @a[scores={tempered.lockn=1..}] run effect give @s minecraft:mining_fatigue 1 200 true
execute as @a[scores={tempered.lockn=1..}] run effect give @s minecraft:weakness 1 200 true

execute as @a[scores={tempered.lockn=2}] run function tempered:lock/hud/2
execute as @a[scores={tempered.lockn=3}] run function tempered:lock/hud/3
execute as @a[scores={tempered.lockn=4}] run function tempered:lock/hud/4
execute as @a[scores={tempered.lockn=5}] run function tempered:lock/hud/5
execute as @a[scores={tempered.lockn=6}] run function tempered:lock/hud/6
execute as @a[scores={tempered.lockn=7}] run function tempered:lock/hud/7

# pelne wyjasnienie tylko przy przejsciu odblokowany -> zablokowany (zero spamu)
execute as @a[scores={tempered.lockn=2,tempered.lock=0}] run function tempered:lock/why/2
execute as @a[scores={tempered.lockn=3,tempered.lock=0}] run function tempered:lock/why/3
execute as @a[scores={tempered.lockn=4,tempered.lock=0}] run function tempered:lock/why/4
execute as @a[scores={tempered.lockn=5,tempered.lock=0}] run function tempered:lock/why/5
execute as @a[scores={tempered.lockn=6,tempered.lock=0}] run function tempered:lock/why/6
execute as @a[scores={tempered.lockn=7,tempered.lock=0}] run function tempered:lock/why/7

# item odlozony -> debuff schodzi natychmiast, nie blokuje sprzetu z Twojej ery
execute as @a[scores={tempered.lockn=0,tempered.lock=1..}] run effect clear @s minecraft:mining_fatigue
execute as @a[scores={tempered.lockn=0,tempered.lock=1..}] run effect clear @s minecraft:weakness

execute as @a run scoreboard players operation @s tempered.lock = @s tempered.lockn
