from game.config import (
    FRUIT_VALUE, FRUIT_HEAL_AMOUNT, FRUIT_STAMINA_RECOVERY, FRUIT_HUNGER_RECOVERY,
    GREEN_FRUIT_HEAL_AMOUNT, GREEN_FRUIT_STAMINA_RECOVERY, GREEN_FRUIT_HUNGER_RECOVERY,
    RED_FRUIT_HEAL_AMOUNT, RED_FRUIT_STAMINA_RECOVERY, RED_FRUIT_HUNGER_RECOVERY
)

class Resource:
    def __init__(self, name, value, position=None):
        self.name = name
        self.value = value
        self.position = position

class Fruit(Resource):
    def __init__(self, name="Fruit", value=FRUIT_VALUE, heal_amount=FRUIT_HEAL_AMOUNT, stamina_recovery=FRUIT_STAMINA_RECOVERY, hunger_recovery=FRUIT_HUNGER_RECOVERY, position=None):
        super().__init__(name, value, position)
        self.heal_amount = heal_amount
        self.stamina_recovery = stamina_recovery
        self.hunger_recovery = hunger_recovery

    def consume(self, animal):
        """L'animal consomme le fruit et récupère des points de vie, de stamina et de faim"""
        hp_recovered = animal.heal(self.heal_amount)
        stamina_recovered = animal.recover_stamina(self.stamina_recovery)
        hunger_recovered = animal.recover_hunger(self.hunger_recovery)
        return hp_recovered, stamina_recovered, hunger_recovered

class GreenFruit(Fruit):
    def __init__(self, position=None):
        super().__init__(
            name="GreenFruit", 
            value=FRUIT_VALUE, 
            heal_amount=GREEN_FRUIT_HEAL_AMOUNT,
            stamina_recovery=GREEN_FRUIT_STAMINA_RECOVERY,
            hunger_recovery=GREEN_FRUIT_HUNGER_RECOVERY,
            position=position
        )

class RedFruit(Fruit):
    def __init__(self, position=None):
        super().__init__(
            name="RedFruit", 
            value=FRUIT_VALUE, 
            heal_amount=RED_FRUIT_HEAL_AMOUNT,
            stamina_recovery=RED_FRUIT_STAMINA_RECOVERY,
            hunger_recovery=RED_FRUIT_HUNGER_RECOVERY,
            position=position
        ) 