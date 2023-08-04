from typing import List, Tuple

from . import KDL3TestBase
from .TestGoal import TestNormalGoal

class TestCopyAbilityShuffle(KDL3TestBase):
    options = {
        "goal_speed": "normal",
        "total_heart_stars": 30,
        "heart_stars_required": 50,
        "filler_percentage": 0,
        "copy_ability_randomization": "enabled",
    }

    def testGoal(self):
        self.assertBeatable(False)
        heart_stars = self.get_items_by_name("Heart Star")
        self.collect(heart_stars[0:14])
        self.assertEqual(self.count("Heart Star"), 14)
        self.assertBeatable(False)
        self.collect(heart_stars[14:15])
        self.assertEqual(self.count("Heart Star"), 15)
        self.assertBeatable(False)
        self.collect_by_name(["Burning", "Cutter", "Kine"])
        self.assertBeatable(True)
        self.remove([self.get_item_by_name("Love-Love Rod")])
        self.collect(heart_stars)
        self.assertEqual(self.count("Heart Star"), 30)
        self.assertBeatable(True)

    def testKine(self):
        self.collect_by_name(["Cutter", "Burning", "Heart Star"])
        self.assertBeatable(False)

    def testCutter(self):
        self.collect_by_name(["Kine", "Burning", "Heart Star"])
        self.assertBeatable(False)

    def testBurning(self):
        self.collect_by_name(["Cutter", "Kine", "Heart Star"])
        self.assertBeatable(False)

    def testValidAbilitiesForROB(self):
        # there exists a subset of 4-7 abilities that will allow us access to ROB heart star on default settings
        self.collect_by_name(["Heart Star", "Kine", "Coo"])  # we will guaranteed need Coo, Kine, and Heart Stars to reach
        # first we need to identify our bukiset requirements
        groups = [
            ({"Parasol Ability", "Cutter Ability"}, {'Bukiset (Parasol)', 'Bukiset (Cutter)'}),
            ({"Spark Ability", "Clean Ability"}, {'Bukiset (Spark)', 'Bukiset (Clean)'}),
            ({"Ice Ability", "Needle Ability"}, {'Bukiset (Ice)', 'Bukiset (Needle)'}),
            ({"Stone Ability", "Burning Ability"}, {'Bukiset (Stone)', 'Bukiset (Burning)'}),
        ]
        copy_abilities = self.multiworld.worlds[1].copy_abilities
        required_abilities: List[Tuple[str]] = []
        for abilities, bukisets in groups:
            potential_abilities: List[str] = list()
            for bukiset in bukisets:
                if copy_abilities[bukiset] in abilities:
                    potential_abilities.append(copy_abilities[bukiset])
            required_abilities.append(tuple(potential_abilities))
        collected_abilities = list()
        for group in required_abilities:
            self.assertFalse(len(group) == 0)
            collected_abilities.append(group[0])
        self.collect_by_name([ability.replace(" Ability", "") for ability in collected_abilities])
        if "Parasol Ability" not in collected_abilities or "Stone Ability" not in collected_abilities:
            # required for non-Bukiset related portions
            self.collect_by_name(["Parasol", "Stone"])

        if "Cutter Ability" not in collected_abilities:
            # we can't actually reach 3-6 without Cutter
            assert not self.can_reach_location("Sand Canyon 6 - Professor Hector & R.O.B")
            self.collect_by_name(["Cutter"])

        assert self.can_reach_location("Sand Canyon 6 - Professor Hector & R.O.B")




class TestAnimalShuffle(KDL3TestBase):
    options = {
        "goal_speed": "normal",
        "total_heart_stars": 30,
        "heart_stars_required": 50,
        "filler_percentage": 0,
        "animal_randomization": "full",
    }

    def testGoal(self):
        self.assertBeatable(False)
        heart_stars = self.get_items_by_name("Heart Star")
        self.collect(heart_stars[0:14])
        self.assertEqual(self.count("Heart Star"), 14)
        self.assertBeatable(False)
        self.collect(heart_stars[14:15])
        self.assertEqual(self.count("Heart Star"), 15)
        self.assertBeatable(False)
        self.collect_by_name(["Burning", "Cutter", "Kine"])
        self.assertBeatable(True)
        self.remove([self.get_item_by_name("Love-Love Rod")])
        self.collect(heart_stars)
        self.assertEqual(self.count("Heart Star"), 30)
        self.assertBeatable(True)

    def testKine(self):
        self.collect_by_name(["Cutter", "Burning", "Heart Star"])
        self.assertBeatable(False)

    def testCutter(self):
        self.collect_by_name(["Kine", "Burning", "Heart Star"])
        self.assertBeatable(False)

    def testBurning(self):
        self.collect_by_name(["Cutter", "Kine", "Heart Star"])
        self.assertBeatable(False)

    def testLockedAnimals(self):
        self.assertTrue(self, self.multiworld.get_location("Ripple Field 5 - Animal 2", 1).item.name == "Pitch Spawn")
        self.assertTrue(self, self.multiworld.get_location("Iceberg 4 - Animal 1", 1).item.name == "ChuChu Spawn")
        self.assertTrue(self, self.multiworld.get_location("Sand Canyon 6 - Animal 1", 1).item.name in {"Kine Spawn", "Coo Spawn"})


class TestAllShuffle(KDL3TestBase):
    options = {
        "goal_speed": "normal",
        "total_heart_stars": 30,
        "heart_stars_required": 50,
        "filler_percentage": 0,
        "animal_randomization": "full",
        "copy_ability_randomization": "enabled",
    }

    def testGoal(self):
        self.assertBeatable(False)
        heart_stars = self.get_items_by_name("Heart Star")
        self.collect(heart_stars[0:14])
        self.assertEqual(self.count("Heart Star"), 14)
        self.assertBeatable(False)
        self.collect(heart_stars[14:15])
        self.assertEqual(self.count("Heart Star"), 15)
        self.assertBeatable(False)
        self.collect_by_name(["Burning", "Cutter", "Kine"])
        self.assertBeatable(True)
        self.remove([self.get_item_by_name("Love-Love Rod")])
        self.collect(heart_stars)
        self.assertEqual(self.count("Heart Star"), 30)
        self.assertBeatable(True)

    def testKine(self):
        self.collect_by_name(["Cutter", "Burning", "Heart Star"])
        self.assertBeatable(False)

    def testCutter(self):
        self.collect_by_name(["Kine", "Burning", "Heart Star"])
        self.assertBeatable(False)

    def testBurning(self):
        self.collect_by_name(["Cutter", "Kine", "Heart Star"])
        self.assertBeatable(False)

    def testLockedAnimals(self):
        self.assertTrue(self, self.multiworld.get_location("Ripple Field 5 - Animal 2", 1).item.name == "Pitch Spawn")
        self.assertTrue(self, self.multiworld.get_location("Iceberg 4 - Animal 1", 1).item.name == "ChuChu Spawn")
        self.assertTrue(self, self.multiworld.get_location("Sand Canyon 6 - Animal 1", 1).item.name in {"Kine Spawn", "Coo Spawn"})