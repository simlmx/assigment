import re, os, shutil, argparse, sys, codecs
from os.path import join, basename, dirname, splitext, exists
from pytextron.utils import ask_before_overwrite


def extract_problems(tex_str, keep_idx=None):
    """ extract latex code that are eqexam Problems from a string
        (usually from a fileobj.read())
        If there is only one problem found and you specified `keep_idx`,
        we will only keep the corresponding Items
    """
    regex = r'\\begin\{problem\*\}.*?\\end\{problem\*\}'
    problems = re.findall(regex, tex_str, re.DOTALL)

    if len(problems) == 1 and keep_idx is not None:
        prob = problems[0]
        parts = re.findall(r'(.*\\begin\{parts\})(.*?)(\\end\{parts\}.*)', prob, re.DOTALL)[0]
        items = re.findall(r'(\\item.*?\\end\{solution\})', parts[1], re.DOTALL)
        items = [items[i] for i in keep_idx]
        return '\n'.join([parts[0]] + items + [parts[-1]])
    else:
        return '\n\n'.join(problems)


def parse_colnet_class_list(lines):
    """ util to parse copy-pasted student lists from the colnet web
        interface
    """
    regex = re.compile(r'^(?P<surname>[^\s][^,]*[^\s])'
                       r'[\s]*,[\s]*'
                       r'(?P<firstname>[^\s][^\d]*[^\s\d])'
                       r'.*', re.UNICODE)
    for l in lines:
        l = l.strip()
        if l == '':
            continue
        m = regex.match(l)
        if m:
            yield (m.group('surname'), m.group('firstname'))
        else:
            raise ValueError('Unable to parse line ' + l)


def assignment_main(make_assignment, make_args=None):
    """
        A "main" that parses a teacher/date/student_list arguments and
        batch-makes assignments for each student in the list using the
        provided function.

        params:
            make_assignment
                function that takes as input a teacher, date and
                student (all strings), and returns a tuple of two assignments
                (the assignment, its solution)
            make_args
                extra arguments for the Assignment.make(...) function
    """
    def uni_arg(bytestring):
        unicode_string = bytestring.decode(sys.getfilesystemencoding())
        return unicode_string

    parser = argparse.ArgumentParser()
    parser.add_argument('--teacher', type=uni_arg, default='')
    parser.add_argument('--date', type=uni_arg, default='')
    parser.add_argument('--student-list',
                        default=None,
                        help='colnet copy-pasted student list')
    parser.add_argument('--output', help='output file, can be a .zip or other')
    args = parser.parse_args()

    def make_assignment2(student):
        """ wrapper with only the student argument """
        return make_assignment(teacher=args.teacher,
                                date=args.date,
                                student=student)

    if args.student_list is None:
        student_list = [None]  # one student with no name
    else:
        student_list = list(parse_colnet_class_list(
            codecs.open(args.student_list, encoding='utf-8').readlines()))
    batch_assignment(make_assignment2, student_list, args.output, make_args)


def batch_assignment(make_assignment, students, output, make_args=None):
    """ make_assignment has to be a function that takes a student name
        (lastname, firstname) tuple (or None) and that returns two assignment instances,
        one with the questions, and one with de solutions
        students is the list of (lastname, firstname) tuples
        output is the output dir or .zip file or .gz file
        We will create an intermediary folder with name `output`.
    """
    output, ext = splitext(output)
    sol_output = join(dirname(output), 'sol_' + basename(output))

    if make_args is None:
        make_args = {}

    for folder in [output, sol_output]:
        if exists(folder) and ask_before_overwrite(folder):
            shutil.rmtree(folder)
        os.mkdir(folder)

    for s in students:
        name = ''
        filename_suffix = ''
        if s is not None:
            name = ', '.join(s)
            filename_suffix += '_' + '_'.join(s)

        ass, sol = make_assignment(name)
        for folder, homework in zip([output, sol_output], [ass, sol]):
            filename = basename(folder) + filename_suffix
            homework.make(join(folder, filename), **make_args)

    if ext != '':
        for o in [output, sol_output]:
            print 'zipping', o
            shutil.make_archive(o, ext.replace('.', ''), o)
