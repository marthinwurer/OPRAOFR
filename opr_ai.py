from collections import namedtuple
import random
import math
import copy

import logging

log = logging.getLogger(__name__)


def calc_distance(x1, y1, x2, y2):
    return ((x1 - x2)**2 + (y1 - y2)**2)**(1/2)

def copify(a):
    return [copy.deepcopy(u) for u in a]


def deploy(battle):
    # alternate between players, placing units
    # p1 on top, p2 on bottom
    # how do I keep track of the non-deployed units?
    
    # TODO real deployment, for now just do randomly in their zones
    # TODO Scout
    # TODO Ambush
    for p in battle.players:
        z = p.zone
        for u in p.units:
            u.x = random.randint(z[2], z[3])
            u.y = random.randint(z[0], z[1])
            u.controller = p.name
            
def choose_unit_to_activate(battle, player):
    available_units = [u for u in player.units if "Activated" not in u.rules and u.alive]
    if not available_units:
        return None
    
    # pick a non-fatigued impact unit first
    nfi = [u for u in available_units if "Fatigued" not in u.rules and "Impact" in u.models[-1].rules]
    if nfi:
        return random.sample(nfi, 1)[0]
    
    # TODO sample from a zone, with priority baseed on rules
    # for now, just sample a random unit
    return random.sample(available_units, 1)[0]


Point = namedtuple("Point", "x y")



def unpack_points(*args):
    out = []
    for arg in args:
        out.append(arg.x)
        out.append(arg.y)
    return tuple(out)


def get_closest(x, y, choices):
    """
    Choices must have the x and y coordinates as x and y members
    """
    closest = choices[0]
    closest_distance = calc_distance(x, y, closest.x, closest.y)
    
    for choice in choices:
        choice_distance = calc_distance(x, y, choice.x, choice.y)
        if choice_distance < closest_distance:
            closest = choice
            closest_distance = choice_distance
    return closest


def get_angle_to(x, y, target):
    return math.atan2(x - target.x, y - target.y)


def offset_at_angle(angle, distance):
    x = distance * math.sin(angle)
    y = distance * math.cos(angle)
    return Point(-x, -y)


def line_point_distance(p1, p2, p0):
    # https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line
    x1, y1 = p1.x, p1.y
    x2, y2 = p2.x, p2.y
    x0, y0 = p0.x, p0.y
    distance = calc_distance(x1, y1, x2, y2)
    if distance == 0:
        return 100000000
    return abs((x2 - x1) * (y1 - y0) - (x1 - x0) * (y2 - y1)) / distance


def terrain_collision(start, end, radius, terrain):
    collisions = []
    for t in terrain:
        to_end = calc_distance(*unpack_points(t, end))
        to_start = calc_distance(*unpack_points(t, start))
        from_line = line_point_distance(start, end, t)
        between = calc_distance(*unpack_points(start, end))
#         print(to_end, to_start, from_line, t)
        
        td = (t.diameter / 2) + radius
        btd = td + between
        if to_end < td or to_start < td or (from_line < td and to_end < btd and to_start < btd):
            collisions.append(t)
    return collisions


def units_in_way(battle, start, finish, width=6):
    # find the line from start to finish, then calculate the distance from that line for all units.
    # if they're within the width, then they're in the way
    in_way = [u for u in battle.all_units if line_point_distance(start, finish, u) <= width]
    return in_way


def choose_action_for_unit(battle, player, unit):
    # if unit is wavering/shaken, they can only hold
    if "Wavering" in unit.rules:
        return ("Hold",)
    speed = unit.speed
    
    # TODO decision tree for unit types, for now move towards nearest enemy unit
    enemy_units = [u for u in battle.all_units if u.controller != player.name and u.alive]
    
    if not enemy_units:
        not_controlled = [o for o in battle.objectives if o.controller != player.name]
        
        if not not_controlled:
            return "Hold", None
        
        closest_obj = get_closest(unit.x, unit.y, not_controlled)
        distance_to = calc_distance(unit.x, unit.y, closest_obj.x, closest_obj.y)
        return "Rush", min(speed * 2, distance_to + 2.5), get_angle_to(unit.x, unit.y, closest_obj)
    
    closest = get_closest(unit.x, unit.y, enemy_units)
    distance_to_closest = calc_distance(unit.x, unit.y, closest.x, closest.y)
    
    # now that we have the closest, figure out the angle to them. 
    angle = get_angle_to(unit.x, unit.y, closest)
    
    
    # melee decision tree
    if unit.is_melee:
        not_controlled = [o for o in battle.objectives if o.controller != player.name]
        if not_controlled:
            closest_obj = get_closest(unit.x, unit.y, not_controlled)
            distance_to = calc_distance(unit.x, unit.y, closest_obj.x, closest_obj.y)
            enemies_in_way = [u for u in units_in_way(battle, unit, closest_obj) if u.controller != player.name and u.alive and calc_distance(u.x, u.y, closest_obj.x, closest_obj.y) < (distance_to + 3.5)]
            if enemies_in_way:
                closest_in_way = get_closest(unit.x, unit.y, enemies_in_way)
                if calc_distance(*unpack_points(unit, closest_in_way)) <= speed * 2:
                    return "Charge", closest_in_way
            return "Rush", min(speed * 2, distance_to + 2.5), get_angle_to(unit.x, unit.y, closest_obj)
        else: # 3
            if distance_to_closest <= speed * 2:
                return "Charge", closest
            return "Rush", speed * 2, angle
    
    elif unit.is_ranged:
#         u_range = unit.range
#         if unit.range > distance_to_closest:
#             return "Advance", 0, 0, closest
        shootable_distance = speed + unit.range
        in_range = [u for u in enemy_units if calc_distance(unit.x, unit.y, u.x, u.y) <= shootable_distance]
        if in_range:
            target = random.choice(in_range)
        else:
            target = closest
        
        angle = get_angle_to(unit.x, unit.y, target)
        distance_to_target = calc_distance(unit.x, unit.y, target.x, target.y)
        
        dist_to_move = max(0, min(distance_to_target - 3, speed))
        
        return "Advance", dist_to_move, angle, closest
                                 
    
    if not unit.is_melee:
        
        dist_to_move = max(0, min(distance_to_closest - 2, speed))
        
        return "Advance", dist_to_move, angle, closest
    
    if distance_to_closest <= speed * 2:
        return "Charge", closest
    
    return "Rush", speed * 2, angle


def basic_activation(battle, player):
    unit = choose_unit_to_activate(battle, player)
    if unit is None:
        log.debug(f"skipping {player}")
        return (None, None)

    action = choose_action_for_unit(battle, player, unit)
    return (unit, action)





def a_choose_action_for_unit(battle, player, unit):
    # if unit is wavering/shaken, they can only hold
    if "Wavering" in unit.rules:
        return ("Hold",)
    speed = unit.speed
    
    # TODO decision tree for unit types, for now move towards nearest enemy unit
    enemy_units = [u for u in battle.all_units if u.controller != player.name and u.alive]
    
    if not enemy_units:
        not_controlled = [o for o in battle.objectives if o.controller != player.name]
        
        if not not_controlled:
            return "Hold", None
        
        closest_obj = get_closest(unit.x, unit.y, not_controlled)
        distance_to = calc_distance(unit.x, unit.y, closest_obj.x, closest_obj.y)
        return "Rush", min(speed * 2, distance_to + 2.5), get_angle_to(unit.x, unit.y, closest_obj)
    
    closest = get_closest(unit.x, unit.y, enemy_units)
    distance_to_closest = calc_distance(unit.x, unit.y, closest.x, closest.y)
    
    # now that we have the closest, figure out the angle to them. 
    angle = get_angle_to(unit.x, unit.y, closest)
    
    
    # melee decision tree
    if unit.is_melee:
        not_controlled = [o for o in battle.objectives if o.controller != player.name]
        if not_controlled:
            closest_obj = get_closest(unit.x, unit.y, not_controlled)
            distance_to = calc_distance(unit.x, unit.y, closest_obj.x, closest_obj.y)
            enemies_in_way = [u for u in units_in_way(battle, unit, closest_obj) if u.controller != player.name and u.alive and calc_distance(u.x, u.y, closest_obj.x, closest_obj.y) < (distance_to + 3.5)]
            if enemies_in_way:
                closest_in_way = get_closest(unit.x, unit.y, enemies_in_way)
                if calc_distance(*unpack_points(unit, closest_in_way)) <= speed * 2:
                    return "Charge", closest_in_way
            return "Rush", min(speed * 2, distance_to + 2.5), get_angle_to(unit.x, unit.y, closest_obj)
        else: # 3
            if distance_to_closest <= speed * 2:
                return "Charge", closest
            return "Rush", speed * 2, angle
    
    elif unit.is_ranged:
#         u_range = unit.range
#         if unit.range > distance_to_closest:
#             return "Advance", 0, 0, closest
        shootable_distance = speed + unit.range
        in_range = [u for u in enemy_units if calc_distance(unit.x, unit.y, u.x, u.y) <= shootable_distance]
        if in_range:
            target = random.choice(in_range)
        else:
            target = closest
        
        angle = get_angle_to(unit.x, unit.y, target)
        distance_to_target = calc_distance(unit.x, unit.y, target.x, target.y)
        
        dist_to_move = max(0, min(distance_to_target - 3, speed))
        
        return "Advance", dist_to_move, angle, closest
                                 
    
    if not unit.is_melee:
        
        dist_to_move = max(0, min(distance_to_closest - 2, speed))
        
        return "Advance", dist_to_move, angle, closest
    
    if distance_to_closest <= speed * 2:
        return "Charge", closest
    
    return "Rush", speed * 2, angle




def advanced_activation(battle, player):
    unit = choose_unit_to_activate(battle, player)
    if unit is None:
        log.debug(f"skipping {player}")
        return (None, None)

    action = a_choose_action_for_unit(battle, player, unit)
    return (unit, action)




