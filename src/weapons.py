from base_weapon import BaseWeapon
from base_bullet import NineMM, FiveFiveSix

class Glock(BaseWeapon):
    def __init__(self, x, y):
        super().__init__(
            x, y, 
            "assets/weapon/glock/image/glock.png",
            NineMM,
            15,
            1,
            0.175,
            size=(30, 15)
        )

class M16(BaseWeapon):
    def __init__(self, x, y):
        super().__init__(
            x, y, 
            "assets/weapon/m16/image/m16.png", 
            FiveFiveSix, 
            50,
            2,
            0.087,
            size=(60, 20)
        )
