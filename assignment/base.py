""" some assignment classes
    dec 2014
"""
from pytextron import LatexDocument
from pytextron import blocks

class Assignment(LatexDocument):

    title = ''
    teacher = ''
    date = ''
    course = ''
    course_short = None
    _student = ''
    version = 'A'
    # TODO versions, short_title, instructions

    def _get_student(self):
        name = self._student
        if name == '' and self.with_solution:
            return r'\color{red} Solutionnaire'
        if self.with_solution:
            return r'\color{red} ' + name
        else:
            return name

    def _set_student(self, v):
        self._student = v

    student = property(_get_student, _set_student)

    @property
    def preambule(self):
        simple_pkgs = ('amstext amsmath amsfonts amssymb MnSymbol graphicx'
                        ' textcomp array xcolor pgfplots').split()

        geometry_def_args = 'landscape' if self.landscape else None
        preambule = [blocks.Documentclass('article', 'french'),
            blocks.Usepackage('inputenc', def_args='utf8'),
            blocks.Usepackage('geometry', def_args=geometry_def_args)] + \
            [blocks.Usepackage(p) for p in simple_pkgs]

        eqexam_args = ['pointsonboth', 'nosummarytotals']
        if self.with_solution:
            eqexam_args.append('solutionsafter')
        else:
            eqexam_args.append('nosolutions')
        if self.for_paper:
            eqexam_args.append('forpaper')
        preambule += [blocks.Usepackage('eqexam', eqexam_args)]

        preambule += \
            [blocks.Command('usetikzlibrary', 'arrows'),
            blocks.Command('pagestyle', 'empty'),
            blocks.Command('everymath', r'\displaystyle'),
            r'\setlength\parindent{0pt}',
            r'\def\exsectitle{\normalsize\hspace*',
            r'{-\oddsidemargin}Solutions}',
            r'\def\exsecrunhead{Solutions}',
            ur'\examNameLabel{{Nom: {} }}'.format(self.student),
            r'\def\exsolafter{\color{red}}',
            blocks.Command('forVersion', self.version),
            blocks.Command('title', unicode(self.title)),
            blocks.Command('author', 'prof : ' + self.teacher),
            blocks.Command('date', self.date),  # TODO automatiser ca
            blocks.Command('subject', self.course, def_args=self.course_short),
            r'\chead{}',
            r'\rhead{}',
            r'\cheadSol{}',
            r'\rheadSol{}',
             ]

        return preambule

    def __init__(self, content, instructions=None, with_solution=True,
                 for_paper=False, nb_compile_times=3, landscape=False,
                 **kwargs):
        """ content should be the inside of the eqexam Exam class,
            i.e. something like a list of problems
        """
        self.with_solution = with_solution
        self.for_paper = for_paper
        self.landscape = landscape
        for k,v in kwargs.iteritems():
            if v is not None:
                setattr(self, k, v)

        if not hasattr(content, '__iter__'):
            content = [content]

        if instructions is not None:
            instructions = blocks.Instructions(instructions, title='Instructions : ')
            content = [instructions] + content

        exam = blocks.Exam(content)

        # without the \n, eqexam isn't happy
        content = [blocks.Command('maketitle'), '', exam]

        super(Assignment, self).__init__(self.preambule + [blocks.Document(content)], nb_compile_times)

class Exam(Assignment):
    pass

class Homework(Assignment):
    pass
