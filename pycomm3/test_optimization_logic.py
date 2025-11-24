import unittest
from unittest.mock import MagicMock
from omron_optimization import OmronOptimizer
from pyomron_fins.fins_client import FinsClient, FinsAddress

class TestOmronOptimizer(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock(spec=FinsClient)
        self.optimizer = OmronOptimizer(self.mock_client)

    def test_contiguous_block_read(self):
        # Setup: Request D0, D1, D2 (Contiguous)
        addresses = ["D0", "D1", "D2"]
        
        # Mock client.read to return [10, 20, 30]
        self.mock_client.read.return_value = [10, 20, 30]
        
        results = self.optimizer.read_smart(addresses)
        print(f"DEBUG KEYS: {list(results.keys())}")
        
        # Verify results
        self.assertEqual(results["D0000"], 10)
        self.assertEqual(results["D0001"], 20)
        self.assertEqual(results["D0002"], 30)
        
        # Verify that client.read was called (optimization used)
        # Instead of read_multiple
        self.mock_client.read.assert_called()
        self.mock_client.read_multiple.assert_not_called()

    def test_scattered_read(self):
        # Setup: Request D0, D100, D200 (Scattered)
        addresses = ["D0", "D100", "D200"]
        
        # Mock client.read_multiple to return dict
        self.mock_client.read_multiple.return_value = {
            "D0000": 10, "D0100": 100, "D0200": 200
        }
        
        results = self.optimizer.read_smart(addresses)
        
        self.assertEqual(results["D0000"], 10)
        self.assertEqual(results["D0100"], 100)
        
        # Verify that read_multiple was called
        self.mock_client.read_multiple.assert_called()

    def test_mixed_optimization(self):
        # Setup: D0-D4 (Contiguous) and D100 (Scattered)
        addresses = ["D0", "D1", "D2", "D3", "D4", "D100"]
        
        # We expect:
        # 1. Block read for D0-D4
        # 2. Read multiple (or single read) for D100? 
        # Actually my logic groups by area. 
        # D0-D4 and D100 are all DM area.
        # Range is 0 to 100 = 101 items.
        # Count is 6 items.
        # Span (101) < Count*2 (12)? NO.
        # So it should default to read_multiple for ALL of them because they are in the same area bucket.
        
        # Wait, my logic groups ALL addresses in an area together.
        # If I have a mix of contiguous and scattered in the SAME area, 
        # and the total span is large, it falls back to read_multiple for EVERYTHING.
        # This is a valid strategy (safe), but maybe not optimal if we have huge blocks.
        # But for now, let's verify it does that.
        
        self.mock_client.read_multiple.return_value = {
            "D0": 0, "D1": 1, "D2": 2, "D3": 3, "D4": 4, "D100": 100
        }
        
        self.optimizer.read_smart(addresses)
        self.mock_client.read_multiple.assert_called()

if __name__ == '__main__':
    unittest.main()
