import unittest


class ValidatorTest(unittest.TestCase):

    def setUp(self):
        from mib import create_app
        self.app = create_app()
