execute at @s run playsound minecraft:block.note_block.bass master @s ~ ~ ~ 0.5 0.6
tellraw @s ["",{"text":"\n  [TEMPERED] ","color":"gold","bold":true},{"color":"white","bold":false,"translate":"tempered.ui.locked_chat"},{"color":"yellow","bold":true,"translate":"tempered.ui.locked_era","with":["7",{"translate":"tempered.era.7"}]},{"text":".","color":"white","bold":false}]
function tempered:lock/todo
tellraw @s ["",{"color":"dark_gray","bold":false,"translate":"tempered.ui.locked_keep"}]
