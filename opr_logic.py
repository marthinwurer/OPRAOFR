from opr_structs import *
from opr_ai import *

import math
import logging

log = logging.getLogger(__name__)


def get_melee_attacks(unit, charging, against):
    # first two rows attack
    attacking_models = unit.models[:unit.width * 2]
    
#     charging = aga
    # TODO phalanx

    # gather the attacks
    attacks = []
    for model in attacking_models:
        # impact
        if "Impact" in model.rules and charging and "Fatigued" not in unit.rules:
            extra = {}
            if "Joust" in model.rules:
                extra["AP"] = 1
            for i in range(model.rules["Impact"]):
                attacks.append(Attack(2, rules={"Impacted":0, **extra}))
        # get the attacks from melee weapons, ie range == 0
        for weapon in model.equipment:
            if not weapon.melee:
                continue
            
#             print(weapon)
            # TODO furious
            num_attacks = weapon.attacks
#             if 
            for _ in range(num_attacks):
                attacks.append(Attack(model.quality, 
                                      rules=merge_rules(merge_rules(weapon.rules, model.rules), unit.rules)))
                if charging:
                    attacks[-1].rules["Charging"] = True

    # postprocess slayer etc
    num_impact = 0
    for attack in attacks:
        if "Impacted" in attack.rules:
            num_impact += 1
        if "Slayer" in attack.rules:
            large_count = len([m for m in against.models if m.rules.get("Tough", 1) >= 3])
            if large_count > len(against.models) / 2:
                attack.rules["AP"] = attack.rules.get("AP", 0) + 2
    if num_impact:
        log.debug(f"num impact: {num_impact}")
#         assert
#     log.debug(f"Attacks: {attacks}")
    return attacks


def models_for(model, count, heros=None):
    if heros is None:
        heros = []
    models = []
    models.extend(heros)
    for i in range(count):
        models.append(model)
    return models


def roll_attacks(attacks, target):
    hits = []
    for attack in attacks:
        # TODO Fatigued, wavering
        bonus = attack.rules.get("Bonus", 0)
        if "Fatigued" in attack.rules:
            bonus -= 999
        if "Wavering" in attack.rules:
            bonus -= 999
        if "Impacted" in attack.rules:
            bonus += 9999

        # do the thing
        roll = random.randint(1, 6)
        success = (roll + bonus >= attack.quality or roll == 6) and roll != 1
        if not success:
            continue
        
        
        if roll == 6:
            # do special stuff here
            
            # TODO furious and relentless before rending?
            if "Furious" in attack.rules and "Charging" in attack.rules:
                log.debug("Furious trigger")
                hits.append(Hit(attack.rules))
            
            # rending
            if "Rending" in attack.rules:
                attack.rules["Rended"] = 0
                attack.rules["AP"] = 4
            
            # TODO Furious

        # add the hits
        # Handle blast
        for _ in range(min(attack.rules.get("Blast", 1), len(target.models))):
            hits.append(Hit(attack.rules))

    return hits


def apply_hits(unit, hits):
    # turn hits into wounds via defending
    # make defense rolls
    # TODO Deadly hits/wounds resolved first
    wounds = []
    for hit in hits:
        # TODO better Shield Wall
        bonus = 0
        if "Shield Wall" in unit.models[-1].rules:
            bonus += 1
        if "Cover" in hit.rules:
            bonus += 1
        roll = random.randint(1, 6)
        success = (roll - hit.rules.get("AP", 0) + bonus >= unit.defense or roll == 6) and roll != 1
        if success:
            # defended, skip its abilities
            continue
        
        # add the wounds from the hit
        wounds.append(hit.rules)
    return wounds


def apply_wounds(unit: Unit, wounds):
    total = 0
    # TODO Deadly hits/wounds resolved first
    for wound in wounds:
        current_model = unit.models[-1]
        # apply the wound to the unit.
        count = wound.get("Deadly", 1) # TODO Deadly
        
        if "Regeneration" in unit.models[-1].rules:
            for i in range(count):
                roll = random.randint(1, 6)
                if "Poison" in wound:
                    break
                if "Rending" in wound:
                    break
                
                if roll >= 5:
                    count -= 1
                    log.debug("Regenerated")

        unit.accumulated_wounds += count
        total += count

        toughness = current_model.rules.get("Tough", 1)
        if unit.accumulated_wounds >= toughness:
            unit.models.pop()
            unit.accumulated_wounds = 0
            # if all the models are dead, we're done here
            if not unit.models:
                return total

    return total



def strike(attacker, defender, charging):
    log.debug(f"{attacker} strikes {defender}")
    # determine attacks
    attacks = get_melee_attacks(attacker, charging, defender)
    log.debug(f"{len(attacks)} attacks")
    # roll to hit
    hits = roll_attacks(attacks, defender)
    log.debug(f"{len(hits)} hits")
    # roll to block
    # TODO do hits and wounds at the same time, to accurately deal with heros
    wounds = apply_hits(defender, hits)
    # remove casualties
    total_wounds = apply_wounds(defender, wounds)
    log.debug(f"{total_wounds} wounds")
    
    # apply fatigued
    attacker.rules["Fatigued"] = True
    
    return total_wounds



def do_melee(attacker, defender):
    # TODO figure out how to do Counter here
    # TODO rules accurate counter
    equipment = []
    for m in defender.models:
        equipment.extend(m.equipment)
    do_counter = any(["Counter" in e.rules for e in equipment])
    
    if do_counter:
        log.debug("Counter attacking!")
        d_wounds = strike(defender, attacker, False)
        if not attacker.models:
            # enemy is dead, we're done
            log.debug(f"{attacker} has been slain!")
            return
    
    a_wounds = strike(attacker, defender, True)
    if not defender.models:
        # enemy is dead, we're done
        log.debug(f"{defender} has been slain!")
        return
    
    if not do_counter: 
        d_wounds = strike(defender, attacker, False)
        if not attacker.models:
            # enemy is dead, we're done
            log.debug(f"{attacker} has been slain!")
            return
    
    # TODO musician and standard bearer
    a_score = a_wounds + attacker.full_rows + attacker.command
    d_score = d_wounds + defender.full_rows + defender.command
    
    log.debug(f"scores: a: {a_score}, d: {d_score}")

    if a_score > d_score:
        loser = defender
    elif d_score > a_score:
        loser = attacker
    else:
        loser = None

    if loser:
        loser.do_morale()

        
def generate_shooting_attacks(unit, distance):
    # all models attack
    attacking_models = unit.models[:]

    # gather the attacks
    attacks = []
    for model in attacking_models:
        # TODO weapon groups
        for weapon in model.equipment:
            if weapon.rules.get("Range", 0) < distance:
                continue
            

            num_attacks = weapon.attacks
            for _ in range(num_attacks):
                attacks.append(Attack(model.quality, 
                                      rules=merge_rules(merge_rules(weapon.rules, model.rules), unit.rules)))
    
    # ranged attacks are not fatigued
    for attack in attacks:
        if "Fatigued" in attack.rules:
            del attack.rules["Fatigued"]
    
    return attacks


def shoot(battle, attacker, defender, distance):
    log.debug(f"{attacker} shooting at {defender}")
    # determine attacks
    attacks = generate_shooting_attacks(attacker, distance)
    if len(attacks) == 0:
        log.debug("Out of range")
        return 0
    log.debug(f"{len(attacks)} attacks")
    
    # handle cover:
    # TODO skip cover terrain that the unit is in
    collisions = terrain_collision(attacker, defender, 0, battle.terrain)
    if any(["Cover" in t.rules for t in collisions]):
        log.debug("Target has cover")
        for a in attacks:
            a.rules["Cover"] = True
    
    # Handle stealth
    if all(["Stealth" in model.rules for model in defender.models]) and distance >= 12:
        log.debug("Target is stealthed")
        for a in attacks:
            a.rules["Bonus"] = a.rules.get("Bonus", 0) - 1
    
    # roll to hit
    hits = roll_attacks(attacks, defender)
    log.debug(f"{len(hits)} hits")
    # roll to block
    # TODO do hits and wounds at the same time, to accurately deal with heros
    wounds = apply_hits(defender, hits)
    # remove casualties
    total_wounds = apply_wounds(defender, wounds)
    log.debug(f"{total_wounds} wounds")
    
#     # apply fatigued
#     attacker.rules["Fatigued"] = 0
    
    return total_wounds


def do_shooting(battle, attacker, defender, distance):
    a_wounds = shoot(battle, attacker, defender, distance)    
    if not defender.models:
        # enemy is dead, we're done
        return
    
    if a_wounds > 0 and defender.under_half:
        defender.do_ranged_morale()
        
        



def calc_terrain_movement(battle, unit, angle, distance):
    potential = battle.terrain
    while True:
        # get the offset and apply it to the unit's position
        x_off, y_off = offset_at_angle(angle, distance)

        t_x = unit.x + x_off
        t_y = unit.y + y_off

        # check terrain collisions
        collisions = terrain_collision(unit, Point(t_x, t_y), 2, potential)
        potential = collisions
        
        # for now just iterate until less than or equal to 6
        if any(["Strider" not in m.rules for m in unit.models]) and distance > 6 and any(["Difficult" in c.rules for c in collisions]):
            distance = max(0, distance - 1)
            continue
        
        break
    
    return distance, t_x, t_y


def execute_advance(battle, player, unit, action):
    # (Advance, desired_distance, angle, shooting target)
    # TODO validate desired distance
    # TODO movement effects
    # get the offset and apply it to the unit's position
    angle = action[2]
    distance = action[1]
    
    distance, t_x, t_y = calc_terrain_movement(battle, unit, angle, distance)
    
    unit.x = t_x
    unit.y = t_y
    
    # TODO collisions with terrain and other units
    
    if action[3]:
        distance = calc_distance(unit.x, unit.y, action[3].x, action[3].y)
        do_shooting(battle, unit, action[3], distance)

        
        
def execute_rush(battle, player, unit, action):
    # (rush, desired_distance, angle)
    # TODO validate desired distance
    # TODO movement effects
    angle = action[2]
    distance = action[1]
    
    distance, t_x, t_y = calc_terrain_movement(battle, unit, angle, distance)
    
    unit.x = t_x
    unit.y = t_y
    
    # TODO collisions with other units
    
    # no combat
    

def execute_charge(battle, player, unit, action):
    # (Charge, target)
    # TODO validate target range and all that
    closest = action[1]
    distance_to_closest = calc_distance(unit.x, unit.y, closest.x, closest.y)
    
    assert distance_to_closest <= unit.speed * 2
    
    # move to touch the enemy
    movement_needed = distance_to_closest - 2  # For now units are 1" spheres
    angle_needed = get_angle_to(unit.x, unit.y, closest)
    
    distance, t_x, t_y = calc_terrain_movement(battle, unit, angle_needed, movement_needed)
    
    unit.x = t_x
    unit.y = t_y
    
    if distance < movement_needed:
        log.debug(f"Charge failed, needed {movement_needed} but only went {distance}")
        return
    
    # do the combat
    do_melee(unit, closest)
    
    # back up
    x_off, y_off = offset_at_angle(angle_needed, -1)
    unit.x += x_off
    unit.y += y_off
    
    
def execute_action(battle, player, unit, action):
    a_type = action[0]
    log.debug(f"executing {player.name} {unit}, {action}")
    unit.rules["Activated"] = True

    if a_type == "Hold":
        if "Wavering" in unit.rules:
            del unit.rules["Wavering"]
        else:
            if len(action) > 1:
                # TODO potential shooting
                pass
    elif a_type == "Advance":
        execute_advance(battle, player, unit, action)
    elif a_type == "Rush":
        execute_rush(battle, player, unit, action)
    elif a_type == "Charge":
        execute_charge(battle, player, unit, action)
    else:
        log.debug("Invalid action")

def check_objectives(battle):
    alive_units = [u for u in battle.all_units if u.alive and "Wavering" not in u.rules]
    for o in battle.objectives:
        # find all units within 3" of the objective (for now will be 4" because they're circles)
        near = [u for u in alive_units if calc_distance(u.x, u.y, o.x, o.y) <= 4]
        if not near:
            # if no units are near enough, the objective stays the same
            continue
        
        # if they're all the same player's, then they gain control. Otherwise, it's contested
        if all([u.controller == near[0].controller for u in near]):
            o.controller = near[0].controller
        else:
            o.controller = None
            
        
    

def do_round(battle, first_player_index):
    battle.round += 1
    log.debug(f"Starting Round {battle.round}")
    # start by resetting activations
    for u in battle.all_units:
        if "Activated" in u.rules:
            del u.rules["Activated"]
        if "Fatigued" in u.rules:
            del u.rules["Fatigued"]
    
    # TODO Ambush
    
    next_player_index = first_player_index
    current_player = None
#     limit = 50
    while any(["Activated" not in u.rules for u in battle.all_units if u.alive]):
#         limit -= 1
#         if limit < 0:
#             return
#         available = [u for u in battle.all_units if "Activated" not in u.rules and u.alive]
#         print(available)
        current_player = battle.players[next_player_index]
        next_player_index = (next_player_index + 1) % len(battle.players)
        
        if current_player.activation:
            (unit, action) = current_player.activation(battle, current_player)
        else:
            (unit, action) = basic_activation(battle, current_player)
        
        if unit is None:
            log.debug(f"skipping {current_player}")
            continue
        
        execute_action(battle, current_player, unit, action)
    
    check_objectives(battle)
    
    return next_player_index # player who finished activating first


def run_battle(battle):
    next_player = 0
    for i in range(4):
        next_player = do_round(battle, next_player)
