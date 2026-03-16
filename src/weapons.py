from base_weapon import BaseWeapon
from base_bullet import PistolBullet, RifleBullet

class Pistol(BaseWeapon):
    def __init__(self, x, y):
        super().__init__(
            x, y, 
            "assets/weapon/pistol/image/pistol.png",
            PistolBullet,
            15,
            1,
            0.175,
            size=(30, 15)
        )

class Rifle(BaseWeapon):
    def __init__(self, x, y):
        super().__init__(
            x, y, 
            "assets/weapon/rifle/image/rifle.png", 
            RifleBullet, 
            50,
            2,
            0.087,
            size=(60, 20)
        )
