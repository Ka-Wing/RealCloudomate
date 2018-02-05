from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import unittest
import time
import os

from future import standard_library

from cloudomate.util.infura import Infura

standard_library.install_aliases()


class TestInfura(unittest.TestCase):

    def setUp(self):
        self.infura = Infura()

    def test_random_generator(self):
        random_sequence = self.infura.random_generator()
	
        self.assertNotEqual(self.infura.random_generator(), random_sequence)

if __name__ == "__main__":
    unittest.main()

