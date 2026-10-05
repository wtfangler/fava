title @a times 10 90 20
title @a subtitle ["",{"color":"gold","bold":true,"translate":"tempered.ui.all_done"}]
title @a title ["",{"text":"TEMPERED","color":"white","bold":true}]
execute as @a at @s run playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 1 0.8
recipe give @a *
tellraw @a ["",{"text":"\n  TEMPERED  //  ","color":"gold","bold":true},{"color":"gold","bold":true,"translate":"tempered.ui.all_done"},{"text":"\n"}]
