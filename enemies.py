import random


class Enemies:
    def __init__(self, HP_max, dmg, hp):
        self.HP_max = HP_max
        self.dmg = dmg
        self.hp = hp
        self.stage = 1

    def attack(self, character):
        dmg_roll = random.randint(1, self.dmg)
        character.decrease_hp(dmg_roll)
        return dmg_roll

    def decrease_health(self, dmg_roll):
        self.hp = self.hp - dmg_roll
        if self.hp <= 0:
            self.hp = 0

    def dict_info(self):
        return {'type': self.__class__.__name__, 'hp': self.hp}

    def __str__(self):
        return f"{self.__class__.__name__}: Stats: {self.hp}HP and {self.dmg}DMG"


class Partial_Exam(Enemies):
    HP = 20
    DMG = 6

    def __init__(self, stage, hp=HP):
        super().__init__(stage, Partial_Exam.DMG, hp)


class Final_Exam(Enemies):
    HP = 40
    DMG = 12

    def __init__(self, stage, hp=HP):
        super().__init__(stage, Final_Exam.DMG, hp)


class Theoretical_Class(Enemies):
    HP = 8
    DMG = 4

    def __init__(self, stage, hp=HP):
        super().__init__(stage, Theoretical_Class.DMG, hp)

    def attack(self, enemy):
        dmg_roll = random.randint(1, self.dmg) + self.stage
        enemy.decrease_hp(dmg_roll)
        return dmg_roll


class Teacher(Enemies):
    HP = 15
    DMG = 7

    def __init__(self, stage, hp=HP):
        super().__init__(stage, Teacher.DMG, hp)

    def attack(self, enemy):
        dmg_roll = random.randint(1, self.dmg)
        if dmg_roll == 7:
            dmg_roll = 14
        enemy.decrease_hp(dmg_roll)
        return dmg_roll


