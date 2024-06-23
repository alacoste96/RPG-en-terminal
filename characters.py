import random


class Characters:
    def __init__(self, HP_max, dmg, hp):
        self.HP_max = HP_max
        self.dmg = dmg
        self.hp = hp

    def attack(self, enemy):
        dmg_roll = random.randint(1, self.dmg)
        enemy.decrease_health(dmg_roll)
        return dmg_roll

    def decrease_hp(self, dmg_roll):
        self.hp -= dmg_roll
        if self.hp <= 0:
            self.hp = 0

    def increase_hp(self):
        healing = int(self.HP_max/4)
        self.hp += healing 
        if self.hp >= self.HP_max:
            self.hp = self.HP_max

    def __str__(self):
        return f"The {self.__class__.__name__}-> Stats: {self.hp} HP and {self.dmg} DMG"

    def dict_info(self):
        return {"type": self.__class__.__name__, "hp": self.hp}

class Bookworn(Characters):
    HP = 50
    DMG = 2

    def __init__(self, hp=HP):
        super().__init__(Bookworn.HP, Bookworn.DMG, hp)


class Worker(Characters):
    HP = 25
    DMG = 5

    def __init__(self, hp=HP):
        super().__init__(Worker.HP, Worker.DMG, hp)


class Procrastinator(Characters):
    HP = 30
    DMG = 6

    def __init__(self, hp=HP):
        super().__init__(Procrastinator.HP, Procrastinator.DMG, hp)


class Whatsapper(Characters):
    HP = 20
    DMG = 6

    def __init__(self, hp=HP):
        super().__init__(Whatsapper.HP, Whatsapper.DMG, hp)