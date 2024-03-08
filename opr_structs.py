import random
import logging

log = logging.getLogger(__name__)


def quality_test(quality, modifier=0):
    roll = random.randint(1, 6)
    return (roll + modifier >= quality or roll == 6) and roll != 1


def merge_rules(a, b):
    merged = {}
    for r in a.keys():
        total = a.get(r, 0) + b.get(r, 0)
        merged[r] = total

    for r in b.keys():
        if r in merged:
            continue
        merged[r] = b[r]
    return merged


class Attack:
    def __init__(self, quality, rules=None):
        if rules is None:
            rules = {}
        self.quality = quality
        self.rules = rules
    
    def __repr__(self):
        return f"Attack({self.quality}, {self.rules})"

class Weapon:
    def __init__(self, attacks, rules=None):
        if rules is None:
            rules = {}
        
        self.attacks = attacks
        self.rules = rules
    
    @property
    def range(self):
        return self.rules.get("Range", 0)
    
    @property
    def melee(self):
        return self.range == 0
    
class Model:
    def __init__(self, quality, defense, equipment, rules=None):
        if rules is None:
            rules = {}
        self.quality = quality
        self.defense = defense
        self.equipment = equipment
        self.rules = rules
    
    def __repr__(self):
        return f"Model({self.quality}, {self.defense}, {self.equipment}, {self.rules})"

class Unit:
    def __init__(self, models, width, rules=None, name=None):
        if rules is None:
            rules = {}
        self.models = models
        self.width = width
        self.rules: dict = rules
        self.starting_models = len(self.models)
        self.accumulated_wounds = 0
        self.x = 0
        self.y = 0
        self.controller = None # currently player name or None
        if name is None:
            self.name = f"Unit {random.randint(0, 1000)}"
        else:
            self.name = name
    
    def __repr__(self):
        wounds = ""
        if self.accumulated_wounds > 0:
            wounds = f" w{self.accumulated_wounds}"
        status = ""
        if "Fatigued" in self.rules:
            status += "f"
        if "Wavering" in self.rules:
            status += "s"
        if "Activated" in self.rules:
            status += "a"
        return f"Unit({self.name} {status}({len(self.models)}/{self.starting_models}{wounds})({self.x:.1f},{self.y:.1f})"

    @property
    def full_rows(self):
        return len(self.models) // self.width
    
    @property
    def under_half(self):
        first_tough = self.models[0].rules.get("Tough", 1)
        if len(self.models) == 1 and first_tough != 1:
            return (first_tough - self.accumulated_wounds) / first_tough <= 0.5
        return len(self.models) / self.starting_models <= 0.5
    
    @property
    def alive(self):
        return len(self.models) > 0

    @property
    def defense(self):
        return self.models[-1].defense
    
    @property
    def command(self):
        total = 0
        for model in self.models:
            if "Command" in model.rules:
                total += 1
        return total
    
    @property
    def is_melee(self):
        for model in self.models:
            for equipment in model.equipment:
                if not equipment.melee:
                    return False
        return True
    
    @property
    def is_hybrid(self):
        # TODO fire breath
        # Melee takes precidence
        if self.is_melee:
            return False
        
        all_ranged = []
        all_melee = []
        for model in self.models:
            for equipment in model.equipment:
                if equipment.melee:
                    all_melee.append(equipment)
                else:
                    all_ranged.append(equipment)
        
        if len(all_melee) > len(all_ranged) * 2:
            return True # if we just have a single model with a ranged weapon, we're hybrid
        
        # short ranged (12" or less) are hybrid (skip single model)
        if len([e for e in all_ranged if e.range <= 12]) > 1:
            return True
        
        return False
    
    @property
    def is_ranged(self):
        return not self.is_melee and not self.is_hybrid
    
    @property
    def speed(self):
        _speed = 6
        if "Slow" in self.rules or any(["Slow" in model.rules for model in self.models]):
            _speed -= 2
        elif "Fast" in self.rules or all(["Fast" in model.rules for model in self.models]):
            _speed += 2
        if "Immobile" in self.rules or any(["Immobile" in model.rules for model in self.models]):
            _speed = 0
        return _speed
    
    @property
    def range(self):
        all_ranged = []
        for model in self.models:
            for equipment in model.equipment:
                if not equipment.melee:
                    all_ranged.append(equipment)
        
        if not all_ranged:
            return 0
        else:
            return all_ranged[-1].range
    
    def apply_wounds(self, wounds):
        pass
    
    def apply_hits(self, hits):
        pass
    
    def morale_test(self):
        # If the unit is wavering, automatically fail the test
        if "Wavering" in self.rules:
            return False
        
        # pick a model to do the 
        # If there are heroes and their quality is higher, use it for quality tests
        # TODO pick optimal model, by default just do the first
        morale_model = self.models[0]
        
        bonus = 0
        
        test = quality_test(morale_model.quality, bonus)
        #  new 3.1 fearless
        if not test and "Fearless" in morale_model.rules:
            log.debug("rolling fearless test")
            roll = random.randint(1, 6)
            if roll >= 4:
                log.debug(f"{self.name} is fearless!")
                test = True
        
        return test
    
    def do_morale(self):
        log.debug(f"{self.name} doing morale test")
        if not self.morale_test():
            log.debug(f"{self.name} failed morale test")
            
            
            
            if self.under_half:
                self.models.clear()
                self.rules["Routed"] = True
                log.debug(f"{self.name} routed!")
            else:
                self.rules["Wavering"] = True
        
    def do_ranged_morale(self):
        log.debug(f"{self.name} doing ranged morale test")
        if not self.morale_test():
            log.debug(f"{self.name} failed ranged morale test")
            self.rules["Wavering"] = True
       
    
class Hit:
    def __init__(self, rules=None):
        if rules is None:
            rules = {}
        self.rules = rules
    
    def __repr__(self):
        return f"Hit({self.rules})"
    
    
class Player:
    def __init__(self, name, units, zone):
        self.name = name
        self.units = units
        self.zone = zone
        self.activation = None
        for unit in self.units:
            unit.controller = self.name
        
        
        
class Objective:
    def __init__(self, x, y, controller=None):
        self.x = x
        self.y = y
        self.controller = controller # currently player name or None
    
    def __repr__(self):
        return f"Objective({self.x}, {self.y}, {self.controller})"


    
    
class Battle:
    def __init__(self, players):
        # TODO allow objective placement
        self.objectives = [Objective(12, 24),Objective(36, 24),Objective(60, 24),]
        self.terrain = []
        self.players = players
        self.round = 0
    
    @property
    def all_units(self):
        units = []
        for p in self.players:
            units.extend(p.units)
        return units
    

