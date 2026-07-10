Zeegem_MapScripts::
	.byte 0


Zeegem_EventScript_OldSailor::
# 4 "data/maps/Zeegem/scripts.pory"
	lock
# 5 "data/maps/Zeegem/scripts.pory"
	faceplayer
# 6 "data/maps/Zeegem/scripts.pory"
	switch VAR_RANGER_RANK
# 7 "data/maps/Zeegem/scripts.pory"
	case RANGER_RANK_SECOND_CLASS, Zeegem_EventScript_OldSailor_3
# 10 "data/maps/Zeegem/scripts.pory"
	case RANGER_RANK_FIRST_CLASS, Zeegem_EventScript_OldSailor_4
# 14 "data/maps/Zeegem/scripts.pory"
	case RANGER_RANK_ELITE, Zeegem_EventScript_OldSailor_5
# 19 "data/maps/Zeegem/scripts.pory"
	msgbox Zeegem_EventScript_OldSailor_Text_3
Zeegem_EventScript_OldSailor_1:
# 24 "data/maps/Zeegem/scripts.pory"
	release
	end

Zeegem_EventScript_OldSailor_3:
# 8 "data/maps/Zeegem/scripts.pory"
	msgbox Zeegem_EventScript_OldSailor_Text_0
	goto Zeegem_EventScript_OldSailor_1

Zeegem_EventScript_OldSailor_4:
# 11 "data/maps/Zeegem/scripts.pory"
	msgbox Zeegem_EventScript_OldSailor_Text_1
	goto Zeegem_EventScript_OldSailor_1

Zeegem_EventScript_OldSailor_5:
# 15 "data/maps/Zeegem/scripts.pory"
	msgbox Zeegem_EventScript_OldSailor_Text_2
	goto Zeegem_EventScript_OldSailor_1


Zeegem_EventScript_OldSailor_Text_0:
# 8 "data/maps/Zeegem/scripts.pory"
	.string "Second Class already? Fast\n"
	.string "work, kid. Keep it up.$"

Zeegem_EventScript_OldSailor_Text_1:
# 11 "data/maps/Zeegem/scripts.pory"
	.string "First Class! The whole\n"
	.string "Tidal Reach is talking\l"
	.string "about you.$"

Zeegem_EventScript_OldSailor_Text_2:
# 15 "data/maps/Zeegem/scripts.pory"
	.string "An Elite Ranger, standing\n"
	.string "right here in Zeegem.\l"
	.string "Never thought I'd see it.$"

Zeegem_EventScript_OldSailor_Text_3:
# 19 "data/maps/Zeegem/scripts.pory"
	.string "Another challenger, eh?\n"
	.string "Everybody starts at zero\l"
	.string "stars. Let's see if you've\l"
	.string "got what it takes.$"
