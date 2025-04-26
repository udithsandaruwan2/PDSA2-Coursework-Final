import unittest
from ..toh_routes import solve_toh_recursive, solve_toh_iterative, frame_stewart_algorithm, validate_move_sequence

class TestTowerOfHanoiFunctions(unittest.TestCase):
    def setUp(self):
        # Define pegs for 3-peg and 4-peg setups
        self.pegs_3 = ['A', 'B', 'C']
        self.pegs_4 = ['A', 'B', 'C', 'D']
        # Expected minimum moves for 3-peg (2^n - 1) and approximate for 4-peg (Frame-Stewart)
        self.min_moves_3peg = {n: (2**n) - 1 for n in range(1, 12)}  # Extended to 11 for boundary test
        # Frame-Stewart moves are approximate; using known values or upper bounds
        self.max_moves_4peg = {1: 1, 2: 3, 5: 17, 6: 25, 7: 33, 8: 41, 9: 49, 10: 57, 11: 65}

    def validate_move_sequence_internal(self, disk_count, moves, pegs, target_peg):
        """Validate a move sequence for correctness (internal test logic)."""
        towers = {peg: list(range(disk_count, 0, -1)) if peg == 'A' else [] for peg in pegs}
        for disk, source, dest in moves:
            self.assertIn(source, pegs, f"Invalid source peg {source}")
            self.assertIn(dest, pegs, f"Invalid destination peg {dest}")
            self.assertNotEqual(source, dest, f"Source and destination pegs must differ: {source} to {dest}")
            self.assertTrue(towers[source], f"No disks on source peg {source}")
            top_disk = towers[source][-1]
            self.assertEqual(top_disk, disk, f"Expected disk {disk} on top of {source}, found {top_disk}")
            if towers[dest]:
                self.assertTrue(towers[dest][-1] > disk, f"Cannot place disk {disk} on smaller disk {towers[dest][-1]}")
            towers[dest].append(towers[source].pop())
        self.assertEqual(len(towers[target_peg]), disk_count, f"Not all {disk_count} disks on target peg {target_peg}")
        for peg in pegs:
            if peg != target_peg:
                self.assertEqual(len(towers[peg]), 0, f"Non-target peg {peg} should be empty")
        for i in range(disk_count - 1):
            self.assertTrue(towers[target_peg][i] > towers[target_peg][i + 1],
                           f"Disks out of order on {target_peg}: {towers[target_peg]}")

    def test_recursive_algorithm(self):
        """Test recursive algorithm for 5 to 10 disks."""
        for n in range(5, 11):
            with self.subTest(disk_count=n):
                moves = solve_toh_recursive(n, 'A', 'B', 'C')
                self.assertEqual(len(moves), self.min_moves_3peg[n],
                                 f"Recursive: Expected {self.min_moves_3peg[n]} moves for {n} disks, got {len(moves)}")
                self.validate_move_sequence_internal(n, moves, self.pegs_3, 'C')
                self.assertTrue(validate_move_sequence(n, moves),
                                f"Recursive: Valid sequence for {n} disks should pass toh_routes validation")

    def test_iterative_algorithm(self):
        """Test iterative algorithm for 5 to 10 disks."""
        for n in range(5, 11):
            with self.subTest(disk_count=n):
                moves = solve_toh_iterative(n, 'A', 'B', 'C')
                self.assertEqual(len(moves), self.min_moves_3peg[n],
                                 f"Iterative: Expected {self.min_moves_3peg[n]} moves for {n} disks, got {len(moves)}")
                self.validate_move_sequence_internal(n, moves, self.pegs_3, 'C')
                self.assertTrue(validate_move_sequence(n, moves),
                                f"Iterative: Valid sequence for {n} disks should pass toh_routes validation")

    def test_frame_stewart_algorithm(self):
        """Test Frame-Stewart algorithm for 5 to 10 disks."""
        for n in range(5, 11):
            with self.subTest(disk_count=n):
                moves = frame_stewart_algorithm(n, 'A', 'B', 'C', 'D')
                self.assertTrue(len(moves) <= self.max_moves_4peg[n],
                                f"Frame-Stewart: Expected <= {self.max_moves_4peg[n]} moves for {n} disks, got {len(moves)}")
                self.validate_move_sequence_internal(n, moves, self.pegs_4, 'D')
                self.assertTrue(validate_move_sequence(n, moves),
                                f"Frame-Stewart: Valid sequence for {n} disks should pass toh_routes validation")

    def test_frame_stewart_small_cases(self):
        """Test Frame-Stewart algorithm for small disk counts (1 and 2)."""
        # 1 disk
        with self.subTest(disk_count=1):
            moves = frame_stewart_algorithm(1, 'A', 'B', 'C', 'D')
            self.assertEqual(len(moves), 1, "Frame-Stewart: Expected 1 move for 1 disk")
            self.assertEqual(moves, [[1, 'A', 'D']], "Frame-Stewart: Incorrect move sequence for 1 disk")
            self.validate_move_sequence_internal(1, moves, self.pegs_4, 'D')
            self.assertTrue(validate_move_sequence(1, moves), "Frame-Stewart: Valid sequence for 1 disk should pass validation")
        # 2 disks
        with self.subTest(disk_count=2):
            moves = frame_stewart_algorithm(2, 'A', 'B', 'C', 'D')
            self.assertEqual(len(moves), 3, "Frame-Stewart: Expected 3 moves for 2 disks")
            expected_moves = [[1, 'A', 'B'], [2, 'A', 'D'], [1, 'B', 'D']]
            self.assertEqual(moves, expected_moves, "Frame-Stewart: Incorrect move sequence for 2 disks")
            self.validate_move_sequence_internal(2, moves, self.pegs_4, 'D')
            self.assertTrue(validate_move_sequence(2, moves), "Frame-Stewart: Valid sequence for 2 disks should pass validation")

    def test_invalid_pegs(self):
        """Test algorithms with invalid peg inputs."""
        n = 5
        # Recursive
        with self.subTest(algorithm='recursive', disk_count=n):
            try:
                solve_toh_recursive(n, 'X', 'B', 'C')
                self.fail("Recursive: Expected exception for invalid source peg 'X'")
            except (ValueError, KeyError, AssertionError):
                pass
        # Iterative
        with self.subTest(algorithm='iterative', disk_count=n):
            try:
                solve_toh_iterative(n, 'X', 'B', 'C')
                self.fail("Iterative: Expected exception for invalid source peg 'X'")
            except (ValueError, KeyError, AssertionError):
                pass
        # Frame-Stewart
        with self.subTest(algorithm='frame_stewart', disk_count=n):
            try:
                frame_stewart_algorithm(n, 'X', 'B', 'C', 'D')
                self.fail("Frame-Stewart: Expected exception for invalid source peg 'X'")
            except (ValueError, KeyError, AssertionError):
                pass

    def test_boundary_disk_count(self):
        """Test algorithms with disk count just outside valid range (11)."""
        n = 11
        # Recursive
        with self.subTest(algorithm='recursive', disk_count=n):
            moves = solve_toh_recursive(n, 'A', 'B', 'C')
            self.assertEqual(len(moves), self.min_moves_3peg[n],
                             f"Recursive: Expected {self.min_moves_3peg[n]} moves for {n} disks, got {len(moves)}")
            self.validate_move_sequence_internal(n, moves, self.pegs_3, 'C')
            self.assertTrue(validate_move_sequence(n, moves), "Recursive: Valid sequence for 11 disks should pass validation")
        # Iterative
        with self.subTest(algorithm='iterative', disk_count=n):
            moves = solve_toh_iterative(n, 'A', 'B', 'C')
            self.assertEqual(len(moves), self.min_moves_3peg[n],
                             f"Iterative: Expected {self.min_moves_3peg[n]} moves for {n} disks, got {len(moves)}")
            self.validate_move_sequence_internal(n, moves, self.pegs_3, 'C')
            self.assertTrue(validate_move_sequence(n, moves), "Iterative: Valid sequence for 11 disks should pass validation")
        # Frame-Stewart
        with self.subTest(algorithm='frame_stewart', disk_count=n):
            moves = frame_stewart_algorithm(n, 'A', 'B', 'C', 'D')
            self.assertTrue(len(moves) <= self.max_moves_4peg[n],
                            f"Frame-Stewart: Expected <= {self.max_moves_4peg[n]} moves for {n} disks, got {len(moves)}")
            self.validate_move_sequence_internal(n, moves, self.pegs_4, 'D')
            self.assertTrue(validate_move_sequence(n, moves), "Frame-Stewart: Valid sequence for 11 disks should pass validation")

    def test_validate_move_sequence_edge_cases(self):
        """Test validate_move_sequence with edge cases."""
        # Empty moves for non-zero disk count
        with self.subTest(case='empty_moves_non_zero_disks'):
            self.assertFalse(validate_move_sequence(5, []),
                            "validate_move_sequence: Empty moves for 5 disks should fail")
        # Malformed move format
        with self.subTest(case='malformed_move'):
            moves = [[1, 'A']]  # Missing destination
            with self.assertRaises(ValueError, msg="validate_move_sequence: Malformed move should raise ValueError"):
                validate_move_sequence(1, moves)

    def test_edge_cases(self):
        """Test edge cases for all algorithms."""
        # 0 disks
        with self.subTest(case='zero_disks'):
            moves = solve_toh_recursive(0, 'A', 'B', 'C')
            self.assertEqual(moves, [], "Recursive: Expected empty moves for 0 disks")
            self.assertTrue(validate_move_sequence(0, moves), "Recursive: Empty sequence for 0 disks should pass validation")
            moves = solve_toh_iterative(0, 'A', 'B', 'C')
            self.assertEqual(moves, [], "Iterative: Expected empty moves for 0 disks")
            self.assertTrue(validate_move_sequence(0, moves), "Iterative: Empty sequence for 0 disks should pass validation")
            moves = frame_stewart_algorithm(0, 'A', 'B', 'C', 'D')
            self.assertEqual(moves, [], "Frame-Stewart: Expected empty moves for 0 disks")
            self.assertTrue(validate_move_sequence(0, moves), "Frame-Stewart: Empty sequence for 0 disks should pass validation")
        # Negative disks
        with self.subTest(case='negative_disks'):
            moves = solve_toh_recursive(-1, 'A', 'B', 'C')
            self.assertEqual(moves, [], "Recursive: Expected empty moves for -1 disks")
            self.assertFalse(validate_move_sequence(-1, moves), "Recursive: Empty sequence for -1 disks should fail validation")
            moves = solve_toh_iterative(-1, 'A', 'B', 'C')
            self.assertEqual(moves, [], "Iterative: Expected empty moves for -1 disks")
            self.assertFalse(validate_move_sequence(-1, moves), "Iterative: Empty sequence for -1 disks should fail validation")
            moves = frame_stewart_algorithm(-1, 'A', 'B', 'C', 'D')
            self.assertEqual(moves, [], "Frame-Stewart: Expected empty moves for -1 disks")
            self.assertFalse(validate_move_sequence(-1, moves), "Frame-Stewart: Empty sequence for -1 disks should fail validation")

if __name__ == '__main__':
    unittest.main()