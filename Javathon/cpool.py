from .types import *


CONSTANT_Class = 7
CONSTANT_Fieldref = 9
CONSTANT_Methodref = 10
CONSTANT_InterfaceMethodref = 11
CONSTANT_String = 8
CONSTANT_Integer = 3
CONSTANT_Float = 4
CONSTANT_Long = 5
CONSTANT_Double = 6
CONSTANT_NameAndType = 12
CONSTANT_Utf8 = 1
CONSTANT_MethodHandle = 15
CONSTANT_MethodType = 16
CONSTANT_InvokeDynamic = 18

cpool = [None, ]  # We use None as the cpool starts from #1, not #0, we can remove None later.
constant_method_count = 0


class Info:
    def __init__(self):
        global cpool
        self.index = len(cpool)
        cpool.append(self)


class CONSTANT_Class_info(Info):
    def __init__(self, name_index: u2):
        self.tag = CONSTANT_Class
        self.name_index = name_index
        super().__init__()


class CONSTANT_Fieldref_info(Info):
    def __init__(self, class_index: u2, name_and_type_index: u2):
        self.tag = CONSTANT_Fieldref
        self.class_index = class_index
        self.name_and_type_index = name_and_type_index
        super().__init__()


class CONSTANT_Methodref_info(Info):
    def __init__(self, class_index: u2, name_and_type_index: u2):
        global constant_method_count
        constant_method_count += 1
        self.tag = CONSTANT_Methodref
        self.class_index = class_index
        self.name_and_type_index = name_and_type_index
        super().__init__()


class CONSTANT_InterfaceMethodref_info(Info):
    def __init__(self, class_index: u2, name_and_type_index: u2):
        self.tag = CONSTANT_InterfaceMethodref
        self.class_index = class_index
        self.name_and_type_index = name_and_type_index
        super().__init__()


class CONSTANT_String_info(Info):
    def __init__(self, string_index: u2):
        self.tag = CONSTANT_String
        self.string_index = string_index
        super().__init__()


class CONSTANT_Integer_info(Info):
    def __init__(self, _bytes: u4):
        self.tag = CONSTANT_Integer
        self.bytes = _bytes
        super().__init__()


class CONSTANT_Float_info(Info):
    def __init__(self, _bytes: u4):
        self.tag = CONSTANT_Float
        self.bytes = _bytes
        super().__init__()


class CONSTANT_Long_info(Info):
    def __init__(self, high_bytes: u4, low_bytes: u4):
        self.tag = CONSTANT_Long
        self.high_bytes = high_bytes
        self.low_bytes = low_bytes
        super().__init__()


class CONSTANT_Double_info(Info):
    def __init__(self, high_bytes: u4, low_bytes: u4):
        self.tag = CONSTANT_Double
        self.high_bytes = high_bytes
        self.low_bytes = low_bytes
        super().__init__()


class CONSTANT_NameAndType_info(Info):
    def __init__(self, name_index: u2, descriptor_index: u2):
        self.tag = CONSTANT_NameAndType
        self.name_index = name_index
        self.descriptor_index = descriptor_index
        super().__init__()


class CONSTANT_Utf8_info(Info):
    def __init__(self, legnth: u2, _bytes, original: str):
        print(_bytes)
        self.tag = CONSTANT_Utf8
        self.legnth = legnth
        self._bytes = _bytes
        self.original = original
        super().__init__()


class CONSTANT_MethodHandle_inf(Info):
    def __init__(self, reference_kind, reference_index: u2):
        self.tag = CONSTANT_MethodHandle
        self.reference_kind = reference_kind
        self.reference_index = reference_index
        super().__init__()


class CONSTANT_MethodType_info(Info):
    def __init__(self, descriptor_index: u2):
        self.tag = CONSTANT_MethodType
        self.descriptor_index = descriptor_index
        super().__init__()


class CONSTANT_InvokeDynamic_info(Info):
    def __init__(self, bootstrap_method_attr_index: u2, name_and_type_index: u2):
        self.tag = CONSTANT_InvokeDynamic
        self.bootstrap_method_attr_index = bootstrap_method_attr_index
        self.name_and_type_index = name_and_type_index
        super().__init__()
