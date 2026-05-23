import unittest
import logic

class TestSkysensioEngine(unittest.TestCase):
    """
    Automated test suite for the Skysensio algorithmic observing engine.
    Run this file to verify all meteorological logic and edge cases.
    """

    # --- POSITIVE CASES (Good Weather) ---
    def test_perfect_night(self):
        """Tests the absolute best possible stargazing conditions."""
        weather = {
            'current': {
                'cloud': 0, 'humidity': 40, 'vis_km': 10.0, 
                'wind_kph': 1.0, 'is_day': 0, 'precip_mm': 0.0,
                'temp_c': 15.0, 'dewpoint_c': 5.0, 'pressure_mb': 1020
            }
        }
        # Perfect weather + high pressure bonus = exactly 10.0
        self.assertEqual(logic.calculate_score(weather), 10.0)

    def test_average_night(self):
        """Tests standard conditions with minor penalties applied."""
        weather = {
            'current': {
                # 30% clouds, 5km visibility, slightly windy
                'cloud': 30, 'humidity': 60, 'vis_km': 5.0, 
                'wind_kph': 15.0, 'is_day': 0, 'precip_mm': 0.0,
                'temp_c': 15.0, 'dewpoint_c': 10.0, 'pressure_mb': 1010
            }
        }
        score = logic.calculate_score(weather)
        # Score should drop due to penalties, but stay above a 5.0
        self.assertTrue(5.0 <= score <= 8.5)

    # --- NEGATIVE CASES (Bad Weather & Dealbreakers) ---
    def test_daylight_dealbreaker(self):
        """Tests if the daylight check overrides perfect weather."""
        weather = {
            'current': {
                'cloud': 0, 'humidity': 40, 'vis_km': 10.0, 
                'wind_kph': 1.0, 'is_day': 1, 'precip_mm': 0.0, # is_day is 1!
                'temp_c': 15.0, 'dewpoint_c': 5.0, 'pressure_mb': 1020
            }
        }
        self.assertEqual(logic.calculate_score(weather), 1.0)

    def test_precipitation_dealbreaker(self):
        """Tests if a tiny amount of rain ruins the night."""
        weather = {
            'current': {
                'cloud': 0, 'humidity': 40, 'vis_km': 10.0, 
                'wind_kph': 1.0, 'is_day': 0, 'precip_mm': 0.1, # Just 0.1mm of rain!
                'temp_c': 15.0, 'dewpoint_c': 5.0, 'pressure_mb': 1020
            }
        }
        self.assertEqual(logic.calculate_score(weather), 1.0)

    # --- EDGE CASES (Physics & Defenses) ---
    def test_dewpoint_fog_risk(self):
        """Tests the thermodynamic edge case where temperature hits the dew point."""
        weather = {
            'current': {
                'cloud': 0, 'humidity': 95, 'vis_km': 10.0, 
                'wind_kph': 1.0, 'is_day': 0, 'precip_mm': 0.0,
                'temp_c': 10.0, 'dewpoint_c': 9.5, 'pressure_mb': 1010 # Spread is only 0.5C!
            }
        }
        score = logic.calculate_score(weather)
        # Should apply the severe thermodynamic penalty, dropping the perfect score
        self.assertTrue(score < 9.0)

    def test_extreme_bounds_clamping(self):
        """Tests if a hurricane API glitch is safely clamped to 1.0."""
        weather = {
            'current': {
                # Impossible API numbers (e.g., 200% clouds, 500kph winds)
                'cloud': 200, 'humidity': 500, 'vis_km': 0.0, 
                'wind_kph': 500.0, 'is_day': 0, 'precip_mm': 0.0,
                'temp_c': 15.0, 'dewpoint_c': 15.0, 'pressure_mb': 900
            }
        }
        # The math would result in a massive negative number, but max(1.0, score) must catch it
        self.assertEqual(logic.calculate_score(weather), 1.0)

    def test_corrupted_missing_data(self):
        """Tests the defensive armor: what if the API sends an empty dictionary?"""
        weather = {
            'current': {} # Total data failure from the API!
        }
        # Because we used .get() with safe defaults, it should assume terrible weather
        # and safely return 1.0 instead of throwing a KeyError and crashing.
        self.assertEqual(logic.calculate_score(weather), 1.0)

if __name__ == "__main__":
    # This runs the professional test suite when the file is executed
    print("Initializing Skysensio Automated Test Suite...\n")
    unittest.main(verbosity=2)