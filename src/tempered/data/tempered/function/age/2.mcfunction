advancement grant @a only tempered:age/2
title @a times 10 70 20
title @a subtitle ["",{"color":"gold","bold":true,"translate":"tempered.era.2"}]
title @a title ["",{"color":"white","bold":false,"translate":"tempered.ui.era_up","with":["2",""]}]
execute as @a at @s run playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 1 1
tellraw @a ["",{"text":"\n  >> ","color":"gold","bold":true},{"color":"gold","bold":true,"translate":"tempered.ui.era_up","with":["2",{"translate":"tempered.era.2"}]},{"color":"gray","bold":false,"translate":"tempered.ui.era_up_sub"},{"text":"\n","color":"gray","bold":false}]
function tempered:recipe/unlock_2
execute as @a run function tempered:core/sync_ui
