import unittest
from datetime import datetime
from assignment import Assignment
from assignment.utils import extract_problems, parse_colnet_class_list
from pytextron.blocks import Problem

@unittest.skip
class TestAssigment(unittest.TestCase):
    def test_assigment(self):
        class AssigmentX(Assignment):
            title = 'assignment x'
            teacher = 'simon'
            date = 'A14'
            course = 'calculus'

        prob = Problem(content='1+1', solution='2')

        assigment = AssigmentX(prob, nb_compile_times=1)
        assigment.make('tmp/test_assigment1', force=True)

class TestUtils(unittest.TestCase):
    def test_extract_problem(self):
        prob = Problem(content='1+1', solution='2')
        prob2 = Problem(content='1+2', solution='3')
        s = 'bla bla bla\n' + unicode(prob) + '\n' + unicode(prob2) \
            + '\n bla bla bla'
        ext = extract_problems(s)
        self.assertEqual(ext, '\n\n'.join([unicode(prob), unicode(prob2)]))

    def test_parse_colnet_class_list(self):
        students = parse_colnet_class_list([
            'Lemieux, Simon 12345 300.A11',
            'O\'Brien-Laplante, Patate-chose bin-chose 12340, 200.A12 (2)',
            '\nabc, def 123 ab.2\n',
            'Pa, Ta\t 123  ',
            '',
            '\n',
            'Pa,  Ta  \t 123 32 ',
            'Pa ,Ta  \t 123 32 '])
        self.assertEqual(list(students),
            [('Lemieux', 'Simon'),
             ('O\'Brien-Laplante', 'Patate-chose bin-chose'),
             ('abc', 'def'),
             ('Pa', 'Ta'),
             ('Pa', 'Ta'),
             ('Pa', 'Ta')])


if __name__ == '__main__':
    unittest.main()
