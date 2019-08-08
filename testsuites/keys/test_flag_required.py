import unittest


class FlagRequired(unittest.TestCase):

    def setUp(self):
        print()

    def test_normal_flag_required(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
