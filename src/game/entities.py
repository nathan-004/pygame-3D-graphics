from src.render.utils import Ennemy as EnnemyRender

class Entity:
    def __init__(self, name: str, life: float, attack: float, defense: float):
        self.name = name

        self.max_life = life
        self.life = life

        self.attack = attack
        self.defense = defense
    
    def damage(self, dmg):
        self.life -= dmg

class Ennemy(Entity):
    def __init__(self, name, life, damage, defense, ennemy_render: EnnemyRender):
        self.ennemy_render = ennemy_render
        super().__init__(name, life, damage, defense)