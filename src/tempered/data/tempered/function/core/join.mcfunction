tag @s add tempered.player
scoreboard players set @s tempered.lock 0
scoreboard players set @s tempered.lockn 0
scoreboard players operation @s tempered.gen = #generation tempered.data
scoreboard players operation @s tempered.bonusgen = #bonus_generation tempered.data
scoreboard players enable @s tempered.menu
recipe give @s *
function tempered:recipe/sync
tellraw @s ["",{"text":"\n  TEMPERED","color":"gold","bold":true},{"color":"gray","bold":false,"translate":"tempered.ui.welcome_sub"},{"color":"dark_gray","bold":false,"translate":"tempered.ui.welcome_hint"},{"text":"/trigger tempered.menu\n","color":"white","bold":false,"click_event":{"action":"run_command","command":"/trigger tempered.menu"}}]
function tempered:core/sync_ui
function tempered:core/status
