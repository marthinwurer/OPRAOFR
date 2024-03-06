from opr_structs import *
from opr_ai import *
from opr_logic import *

hand_weapon = Weapon(1)

champion_hand_weapon = Weapon(3, {"AP": 1})
dual_hand_weapon = Weapon(2)
fire_rifle = Weapon(2, {"Range": 18, "Rending": 0})
rifle = Weapon(1, {"Range": 18, "AP": 1})
crossbow = Weapon(1, {"Range": 24, "Rending": 0})

claw = Weapon(10)
stomp = Weapon(4, {"AP": 1})
giant_beast = Model(4, 3, [claw, stomp], rules={"Fear":2, "Regeneration":True, "Tough":12})
giant_beast_u = Unit([giant_beast], 1, name="Giant Beast")


#### Dwarves ####

hand_weapon = Weapon(1)
halberd = Weapon(1, {"Rending": 0})
spear = Weapon(1, {"Counter": True})
dwarf_warrior = Model(4, 5, [hand_weapon], rules={"Shield Wall":0, "Slow":0})
warriors = Unit(models_for(dwarf_warrior, 20), 5, name="Warriors")
warriors_10 = Unit(models_for(dwarf_warrior, 10), 5, name="Warriors")
dwarf_halb = Model(4, 5, [halberd], rules={"Shield Wall":0, "Slow":0})
halb_warrs = Unit(models_for(dwarf_halb, 20), 5, name="Warriors")
dwarf_spear = Model(4, 5, [spear], rules={"Shield Wall":0, "Slow":0})
spear_warrs = Unit(models_for(dwarf_spear, 20), 5, name="Warriors")

heavy_hand_weapon = Weapon(1, {"AP": 1})
veteran = Model(3, 4, [heavy_hand_weapon], rules={"Fearless":0, "Slow":0})
veterans = Unit(models_for(veteran, 10), 10, name="Veterans")
heavy_spear = Weapon(1, {"AP": 1, "Counter": True})
spear_vet = Model(3, 4, [heavy_spear], rules={"Fearless":0, "Slow":0})
spear_vets = Unit(models_for(spear_vet, 10), 10, name="Spear Veterans")
veterans_3 = Unit(models_for(veteran, 15), 10, name="Veterans")


berserker = Model(4, 5, [dual_hand_weapon], rules={"Fearless":True, "Furious":True, "Slayer":True, "Slow":True})
berserkers = Unit(models_for(berserker, 10), 5, name="Berserkers")

rune_weapon = Weapon(1, {"Rending": 0})
iron_warrior = Model(3, 3, [rune_weapon], rules={"Shield Wall":True, "Slow":True})
iron_warriors = Unit(models_for(iron_warrior, 10), 5, name="Iron Warriors")
iron_warriors_5 = Unit(models_for(iron_warrior, 5), 5, name="Iron Warriors")

great_weapon = Weapon(2, {"AP": 2})
hammerer = Model(3, 4, [great_weapon], rules={"Slow":0})
hammerers = Unit(models_for(hammerer, 10), 5, name="Hammerers")

great_weapons = Weapon(6, {"AP": 2})
stomp = Weapon(4, {"AP": 1})
giant_construct = Model(3, 2, [great_weapons, stomp], rules={"Fear":2, "Slow":True, "Tough":12})
giant_construct_u = Unit([giant_construct], 1, name="Giant Construct")

stone_fists = Weapon(3, {"AP": 1})
golem = Model(4, 5, [stone_fists], rules={"Tough":3, "Slow":0})
golems = Unit(models_for(golem, 3), 3, name="Golems")
golems_c = Unit(models_for(golem, 6), 3, name="Golems")

rifle_dwarf = Model(4, 5, [rifle, hand_weapon], rules={"Slow":0})
rifle_dwarves = Unit(models_for(rifle_dwarf, 5), 5, name="Marksmen")
rifle_dwarves_c = Unit(models_for(rifle_dwarf, 10), 5, name="Marksmen")

xbow_dwarf = Model(4, 5, [crossbow, hand_weapon], rules={"Slow":0})
xbow_dwarves = Unit(models_for(xbow_dwarf, 5), 5, name="Marksmen")
xbow_dwarves_c = Unit(models_for(xbow_dwarf, 10), 5, name="Marksmen")

fire_rifle = Weapon(2, {"Range": 18, "Rending": 0})
drake_marksman = Model(3, 3, [fire_rifle, hand_weapon], rules={"Slow":0})
drake_marksmen = Unit(models_for(drake_marksman, 5), 5, name="Drakes")
drake_marksmen_c = Unit(models_for(drake_marksman, 10), 5, name="Drakes")

crew = Weapon(3)
bolt_thrower = Weapon(1, {"Range": 36, "AP": 3, "Deadly":6})
bolt_thrower_m = Model(4, 5, [crew, bolt_thrower], rules={"Immobile":0, "Entrenched":0, "Tough":3})
bolt_thrower_u = Unit([bolt_thrower_m], 1, name="Arty")

cannon = Weapon(2, {"Range": 30, "AP": 1, "Blast":3})
dwarven_cannon = Model(4, 5, [crew, cannon], rules={"Immobile":0, "Entrenched":0, "Tough":3})
dwarven_cannon_u = Unit([dwarven_cannon], 1, name="Arty")


# chivalrous kingdoms
throw_stones = Weapon(1, {"Range": 12})
peasant = Model(6, 6, [hand_weapon, throw_stones], rules={})
peasants = Unit(models_for(peasant, 20), 5, name="Peasants")

man_at_arms = Model(5, 5, [hand_weapon], rules={})
men_at_arms = Unit(models_for(man_at_arms, 20), 5, name="Men-At-Arms")
men_at_arms_10 = Unit(models_for(man_at_arms, 10), 5, name="Men-At-Arms")

longbow = Weapon(1, {"Range": 30})
longbowman = Model(5, 5, [hand_weapon, longbow], rules={})
longbowmen = Unit(models_for(longbowman, 5), 5, name="Longbowmen")
longbowmen_10 = Unit(models_for(longbowman, 10), 5, name="Longbowmen")

foot_knight = Model(4, 4, [heavy_hand_weapon], rules={"Fearless":True})
foot_knights = Unit(models_for(foot_knight, 10), 5, name="Foot Knights")
foot_knights_5 = Unit(models_for(foot_knight, 5), 5, name="Foot Knights")
heavy_great_weapon = Weapon(1, {"AP": 3})
heavy_foot_knight = Model(4, 4, [heavy_great_weapon], rules={"Fearless":True})
heavy_foot_knights = Unit(models_for(heavy_foot_knight, 10), 5, name="Heavy Foot Knights")
heavy_foot_knights_5 = Unit(models_for(heavy_foot_knight, 5), 5, name="Heavy Foot Knights")

lance = Weapon(1, {"Lance": True})
realm_knight = Model(4, 4, [lance], rules={"Fast": True, "Fearless": True, "Furious": True, "Impact": 1, "Joust": True})
realm_knights = Unit(models_for(realm_knight, 5), 5, name="Realm Knights")
realm_knights_c = Unit(models_for(realm_knight, 10), 5, name="Realm Knights")

heavy_lance = Weapon(1, {"Lance": True, "AP": 1})
grail_knight = Model(4, 4, [lance], rules={"Fast": True, "Fearless": True, "Impact": 1, "Joust": True})
grail_knights = Unit(models_for(grail_knight, 5), 5, name="Grail Knights")
grail_knights_c = Unit(models_for(grail_knight, 10), 5, name="Grail Knights")



# Other
goblin_warrior = Model(5, 6, [hand_weapon], rules={})
goblin_warriors = Unit(models_for(goblin_warrior, 20), 5, name="Gobbos")

giant_club = Weapon(6, {"AP": 2})
stomp = Weapon(4, {"AP": 1})
giant = Model(4, 3, [giant_club, stomp], rules={"Fear":2, "Slow":True, "Tough":12})
giant_u = Unit([giant], 1, name="Giant")

heavy_hand_weapons = Weapon(2, {"AP": 1})
ogre = Model(4, 4, [heavy_hand_weapons], rules={"Tough":3})
ogres = Unit(models_for(ogre, 6), 3, name="Ogres")
ogres_3 = Unit(models_for(ogre, 3), 3, name="Ogres")


