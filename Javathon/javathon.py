import ast
import binascii
import inspect

from cpool import *
from rich import print
from compiler import JavaCompiler


#
# # CONTAINS INSTRUCTIONS TO CONVERT PYTHON BUILT-INS INTO JAVA BYTECODE
# PY_TO_BYTES = {
#     'print': {
#         'WRITE': b'\t\x00\x08\x00\t\x07\x00\n\x0c\x00\x0b\x00\x0c\x01\x00\x10java/lang/System\x01\x00\x03out\x01'
#                  b'\x00\x15Ljava/io/PrintStream;',
#         'INFO': (CONSTANT_String_info, 'NEXT_INDEX'),
#
#     }
#
# }


# class JVMTargetHandler(JVMTarget):
#     test = "hi"
#
#     def __init__(self):
#         self.constant_pool = b''
#         self.file = open('./test/test.class', 'wb')
#         self.writer = HexWriter(self.file)
#         self.file.write(JVMTarget.CAFEBABE +
#                         JVMTarget.JAVA_VERSION)
#         # The bytes 8 and 9 are reserved for the constant pool count
#         self.cpool_count = 9
#         self.file.write(JVMTarget.STARTING_METHODREF)


class BuiltIns:
    def _print(self, string_input):
        self.write()


# class HexWriter(BuiltIns):
#     def __init__(self, file):
#         self.file = file
#         # Meant to be used for counting in the cpool
#         self.current_index = -1
#
#     def write(self, info_class):
#         self.current_index += 1
#         sig = inspect.signature(info_class.__init__)
#         towrite = ""
#         for param in sig.parameters:
#             if param != 'self':
#                 towrite += getattr(info_class, param)
#         self.file.write(binascii.unhexlify(towrite))
#
#     def convert_args(self, info_class, args: dict):
#         sig = inspect.signature(info_class.__init__)
#         for key, value in args.items():
#             if sig.parameters[key].annotation == u2:
#                 # Because u2 and u4 use big-edian byte order (more important bytes go last)
#                 args[key] = "".join(
#                     ["0" for _ in range(4 - len(value))]) + value
#             if sig.parameters[key].annotation == u4:
#                 args[key] = "".join(
#                     ["0" for _ in range(8 - len(value))]) + value
#         return args


with open("./test/test.py", "r") as f:
    result = ast.parse(f.read())

target = JavaCompiler('./test/test.class')

for ast_object in result.body:
    if isinstance(ast_object, ast.Expr):
        if isinstance(ast_object.value, ast.Call):
            if isinstance(ast_object.value.func, ast.Name):
                print(ast_object.value.args)
                if ast_object.value.func.id == 'print':
                    print("hi")
    # if isinstance(ast_object, ast.FunctionDef): if ast_object.name == 'main': if ast_object.args.posonlyargs != []
    # or ast_object.args.kwonlyargs != [] or ast_object.args.kw_defaults != [] or ast_object.args.kwarg is not None
    # or ast_object.args.defaults != []: print( "[red]The only supported argument in the main function is *args or
    # args[/red]") break

    #         print(ast_object.args.__dict__)
    #         print(result.body[0].__dict__)
