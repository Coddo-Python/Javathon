import inspect
import ast
import struct

from .converter import Converter, cpool, constant_method_count, method_table, method_count
from .types import *
from .pools import *
from rich import print


class JVMTarget:
    CAFEBABE = b'\xca\xfe\xba\xbe'
    # JAVA SE 16 and this is counts as 4 hex binary strings
    JAVA_VERSION = b'\x00\x00\x00<'


class JavaCompiler:
    def __init__(self, python_file_path, python_file, class_file):
        self.py_data = None
        self.this_class_index = None
        self.object_index = None

        self.file_name = class_file
        self.py_file = python_file_path
        self.py_file_name = python_file
        self.file = open(class_file, 'wb')
        self.converter = Converter()

    def compile_to_java(self):
        self.file.write(JVMTarget.CAFEBABE +
                        JVMTarget.JAVA_VERSION)
        self.read_constant_pool()

    def read_constant_pool(self):
        self.object_index = self.converter.object()
        self.this_class_index = self.converter.this_class(self.py_file_name)
        code = self.read_ast()

        print("init")
        self.converter.init_method()
        print("main")
        self.converter.main_method(code)
        print("main done!")

        cpool.pop(0)
        # Write cpool count
        # Add 1 to the constant pool count as we shift everything up an index, so we dont use 0, and we need to
        # always use a count which is at least 1 more than the actual count
        self.file.write(struct.pack('>H', len(cpool) + 1))

        print(cpool)

        for info_class in cpool:
            print(info_class)
            self.write_class(info_class)

        # Write access flag (ACC_SUPER)
        self.file.write(struct.pack('>H', 32))

        # Write this class index
        self.file.write(struct.pack('>H', self.this_class_index))

        # Write super class index (We write the object index as just like in Python, by default java inherits from
        # object
        self.file.write(struct.pack('>H', self.object_index))

        # Write superinterfaces count, we have none
        self.file.write(struct.pack('>H', 0))
        # Usually you would write the superinterfaces table

        # Write fields count, we have none
        self.file.write(struct.pack('>H', 0))
        # Usually you would write the fields table

        print("method count")

        # Write method count
        self.file.write(struct.pack('>H', len(method_table)))
        # Write methods table
        print(method_table)
        for method in method_table:
            self.write_class(method)

        # Write attribute count
        self.file.write(struct.pack('>H', 0))

    def read_ast(self):
        with open(self.py_file, "r") as f:
            self.py_data = ast.parse(f.read())
        to_return = []
        variables = {}
        for ast_object in self.py_data.body:
            if isinstance(ast_object, ast.Expr):
                if isinstance(ast_object.value, ast.Call):
                    if isinstance(ast_object.value.func, ast.Name):
                        if ast_object.value.func.id == 'print':
                            print("Print found, registering...")
                            to_return.extend(
                                self.converter.print(" ".join([arg.value for arg in ast_object.value.args])))

            if isinstance(ast_object, ast.Assign):
                variables[ast_object.targets[0].id] = [ast_object.value.value]

            if isinstance(ast_object, ast.AnnAssign):
                variables[ast_object.annotation.id] = [ast_object.value.value]

        return to_return

    def write_class(self, info_class, return_towrite: bool = False):
        sig = inspect.signature(info_class.__init__)
        try:
            # U1, 1 char unsigned
            towrite = struct.pack('B', info_class.tag)
        except AttributeError:
            towrite = b""
        for param, value in sig.parameters.items():
            if param != 'self':
                if param.startswith('_'):
                    param = param[1:]
                if value.annotation == list:
                    for _ in getattr(info_class, param):
                        if type(_) in (Code_attribute, attribute_info, method_info):
                            towrite += self.write_class(_, True)
                        else:
                            towrite += self.apply_logic(_)
                elif value.annotation is not inspect._empty:
                    towrite += self.apply_logic(getattr(info_class, param), value.annotation, )

        # print("\nTowrite:")
        # print(towrite)
        if return_towrite:
            return towrite
        self.file.write(towrite)

    def apply_logic(self, attr, annotation=None):
        # > Meaning big-endian
        if annotation == u1 or isinstance(attr, u1):
            # B meaning unsigned char (or 1 byte int)
            return struct.pack('>B', attr)
        elif annotation == u2 or isinstance(attr, u2):
            # H meaning unsigned short (or 2 byte int)
            return struct.pack('>H', attr)
        elif annotation == u4 or isinstance(attr, u4):
            # I meaning unsigned int (or 4 byte int)
            return struct.pack('>I', attr)
        elif annotation == str or isinstance(attr, str):
            return attr.encode("utf-8")
