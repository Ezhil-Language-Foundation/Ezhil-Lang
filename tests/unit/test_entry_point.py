# -*- coding: utf-8 -*-

import unittest
import subprocess


class TestEntryPoint(unittest.TestCase):
    def test_execute_file(self):
        expected_output = "வணக்கம் உலகம்!\nஇது என் முதல் எழில் நிரல்\n******* வணக்கம்! மீண்டும் சந்திப்போம் *******\n"
        res = subprocess.Popen(['../../ezhili', '../hello.n'],
                               stdout=subprocess.PIPE)
        self.assertEqual(res.stdout.read().decode('UTF-8'), expected_output)

if __name__ == "__main__":
    unittest.main()
