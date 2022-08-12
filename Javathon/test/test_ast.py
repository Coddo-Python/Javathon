import ast

from rich import print

with open("./test.py", "r") as f:
    py_data = ast.parse(f.read())
to_return = []
for ast_object in py_data.body:
    if isinstance(ast_object, ast.Expr):
        if isinstance(ast_object.value, ast.Call):
            if isinstance(ast_object.value.func, ast.Name):
                if ast_object.value.func.id == 'print':
                    print("Print found, registering...")

    if isinstance(ast_object, ast.Assign):
        print(ast_object.value.__dict__)
        print(type(ast_object.value.value))
        print(type(ast_object.targets[0].id))

    if isinstance(ast_object, ast.AnnAssign):
        print(ast_object.value.value)
        print(type(ast_object.annotation.id))
