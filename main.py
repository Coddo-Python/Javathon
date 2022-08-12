from Javathon.compiler import JavaCompiler

import ast

from rich import print

target = JavaCompiler('./Javathon/test/test.py', 'test', './Javathon/test/test.class')

target.compile_to_java()
