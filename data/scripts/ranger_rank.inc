Common_EventScript_RangerRankUp::
# 8 "data/scripts/ranger_rank.pory"
	compare VAR_RANGER_RANK, RANGER_RANK_MAX
	goto_if_lt Common_EventScript_RangerRankUp_2
Common_EventScript_RangerRankUp_1:
# 11 "data/scripts/ranger_rank.pory"
	playfanfare MUS_OBTAIN_BADGE
# 12 "data/scripts/ranger_rank.pory"
	switch VAR_RANGER_RANK
# 13 "data/scripts/ranger_rank.pory"
	case RANGER_RANK_SECOND_CLASS, Common_EventScript_RangerRankUp_6
# 15 "data/scripts/ranger_rank.pory"
	case RANGER_RANK_FIRST_CLASS, Common_EventScript_RangerRankUp_7
# 17 "data/scripts/ranger_rank.pory"
	case RANGER_RANK_ELITE, Common_EventScript_RangerRankUp_8
# 20 "data/scripts/ranger_rank.pory"
	msgbox Common_EventScript_RangerRankUp_Text_3
Common_EventScript_RangerRankUp_4:
# 22 "data/scripts/ranger_rank.pory"
	waitfanfare
	return

Common_EventScript_RangerRankUp_2:
# 9 "data/scripts/ranger_rank.pory"
	addvar VAR_RANGER_RANK, 1
	goto Common_EventScript_RangerRankUp_1

Common_EventScript_RangerRankUp_6:
# 14 "data/scripts/ranger_rank.pory"
	msgbox Common_EventScript_RangerRankUp_Text_0
	goto Common_EventScript_RangerRankUp_4

Common_EventScript_RangerRankUp_7:
# 16 "data/scripts/ranger_rank.pory"
	msgbox Common_EventScript_RangerRankUp_Text_1
	goto Common_EventScript_RangerRankUp_4

Common_EventScript_RangerRankUp_8:
# 18 "data/scripts/ranger_rank.pory"
	msgbox Common_EventScript_RangerRankUp_Text_2
	goto Common_EventScript_RangerRankUp_4


Common_EventScript_RangerRankUp_Text_0:
# 14 "data/scripts/ranger_rank.pory"
	.string "You are now a RANGER SECOND CLASS!$"

Common_EventScript_RangerRankUp_Text_1:
# 16 "data/scripts/ranger_rank.pory"
	.string "You are now a RANGER FIRST CLASS!$"

Common_EventScript_RangerRankUp_Text_2:
# 18 "data/scripts/ranger_rank.pory"
	.string "You are now an ELITE RANGER!$"

Common_EventScript_RangerRankUp_Text_3:
# 20 "data/scripts/ranger_rank.pory"
	.string "You are now a CHALLENGER!$"
