LaekonRoute1_MapScripts::
	.byte 0


LaekonRoute1_EventScript_RangerCheckpoint::
# 4 "data/maps/LaekonRoute1/scripts.pory"
	lock
# 5 "data/maps/LaekonRoute1/scripts.pory"
	faceplayer
# 6 "data/maps/LaekonRoute1/scripts.pory"
	compare VAR_RANGER_RANK, RANGER_RANK_CHALLENGER
	goto_if_eq LaekonRoute1_EventScript_RangerCheckpoint_2
# 14 "data/maps/LaekonRoute1/scripts.pory"
	msgbox LaekonRoute1_EventScript_RangerCheckpoint_Text_1
LaekonRoute1_EventScript_RangerCheckpoint_1:
# 19 "data/maps/LaekonRoute1/scripts.pory"
	release
	end

LaekonRoute1_EventScript_RangerCheckpoint_2:
# 7 "data/maps/LaekonRoute1/scripts.pory"
	msgbox LaekonRoute1_EventScript_RangerCheckpoint_Text_0
	goto LaekonRoute1_EventScript_RangerCheckpoint_1


LaekonRoute1_EventScript_RangerCheckpoint_Text_0:
# 7 "data/maps/LaekonRoute1/scripts.pory"
	.string "Hold it. The waters east of\n"
	.string "here are Corps business.\p"
	.string "Come back when you're a\n"
	.string "ranked Ranger, not just a\l"
	.string "challenger.$"

LaekonRoute1_EventScript_RangerCheckpoint_Text_1:
# 14 "data/maps/LaekonRoute1/scripts.pory"
	.string "Ranger business is quiet out\n"
	.string "this way for now. Nothing\l"
	.string "past here yet -- but you've\l"
	.string "earned the right to look.$"
