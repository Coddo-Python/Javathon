import inspect

from .cpool import *
from .pools import *

from typing import List

method_count = 0
method_table = []


class Tools:
    @staticmethod
    # Not made by me, https://gist.github.com/BarelyAliveMau5/000e7e453b6d4ebd0cb06f39bc2e7aec
    def utf8s_to_utf8m(string):
        """\
        :param string: utf8 encoded string
        :return: modified utf8 encoded string
        """
        new_str = []
        i = 0
        while i < len(string):
            byte1 = string[i]
            # NULL bytes and bytes starting with 11110xxx are special
            if (byte1 & 0x80) == 0:
                if byte1 == 0:
                    new_str.append(0xC0)
                    new_str.append(0x80)
                else:
                    # Single byte
                    new_str.append(byte1)

            elif (byte1 & 0xE0) == 0xC0:  # 2byte encoding
                new_str.append(byte1)
                i += 1
                new_str.append(string[i])

            elif (byte1 & 0xF0) == 0xE0:  # 3byte encoding
                new_str.append(byte1)
                i += 1
                new_str.append(string[i])
                i += 1
                new_str.append(string[i])

            elif (byte1 & 0xF8) == 0xF0:  # 4byte encoding
                # Beginning of 4byte encoding, turn into 2 3byte encodings
                # Bits in: 11110xxx 10xxxxxx 10xxxxxx 10xxxxxx
                i += 1
                byte2 = string[i]
                i += 1
                byte3 = string[i]
                i += 1
                byte4 = string[i]

                # Reconstruct full 21bit value
                u21 = (byte1 & 0x07) << 18
                u21 += (byte2 & 0x3F) << 12
                u21 += (byte3 & 0x3F) << 6
                u21 += (byte4 & 0x3F)

                # Bits out: 11101101 1010xxxx 10xxxxxx
                new_str.append(0xED)
                new_str.append((0xA0 + (((u21 >> 16) - 1) & 0x0F)))
                new_str.append((0x80 + ((u21 >> 10) & 0x3F)))

                # Bits out: 11101101 1011xxxx 10xxxxxx
                new_str.append(0xED)
                new_str.append((0xB0 + ((u21 >> 6) & 0x0F)))
                new_str.append(byte4)
            i += 1
        return bytes(new_str)

    @staticmethod
    def string_to_bytes(_string):
        to_return = [format(x, 'b') for x in Tools.utf8s_to_utf8m(_string.encode("utf-8"))]
        return len(to_return), to_return, _string

    @staticmethod
    def unpack(function, args):
        """A method to automatically type convert arguments to a function accordingly"""
        sig = inspect.signature(function)
        function.picky = [None if sig.parameters[key].annotation is
                                  inspect._empty else sig.parameters[key].annotation
                          for key in list(sig.parameters.keys())]

        counter = -1
        for var_type in function.picky:
            counter += 1
            if var_type is not None:
                args[counter] = var_type(args[counter])
        return args


class BuiltIns:
    def __init__(self):
        self.first_print = True

    def print(self, text):
        if self.first_print:
            # Register PrintStream in the constant pool so that we can println
            # We only need to do this ONCE
            self.print_field_ref = len(cpool)
            CONSTANT_Fieldref_info(u2(len(cpool) + 1), u2(len(cpool) + 2))
            CONSTANT_Class_info(u2(len(cpool) + 2))
            CONSTANT_NameAndType_info(u2(len(cpool) + 2), u2(len(cpool) + 3))
            CONSTANT_Utf8_info(*Tools.string_to_bytes("java/lang/System"))
            CONSTANT_Utf8_info(*Tools.string_to_bytes("out"))
            CONSTANT_Utf8_info(*Tools.string_to_bytes("Ljava/io/PrintStream;"))

            # Register print method in constant pool
            self.print_method_ref = len(cpool)
            CONSTANT_Methodref_info(u2(len(cpool) + 1), u2(len(cpool) + 2))
            CONSTANT_Class_info(u2(len(cpool) + 2))
            CONSTANT_NameAndType_info(u2(len(cpool) + 2), u2(len(cpool) + 3))
            CONSTANT_Utf8_info(*Tools.string_to_bytes("java/io/PrintStream"))
            CONSTANT_Utf8_info(*Tools.string_to_bytes("println"))
            CONSTANT_Utf8_info(*Tools.string_to_bytes("(Ljava/lang/String;)V"))
            self.first_print = False

        # Register the text as a String in the constant pool
        self.printable = len(cpool)
        CONSTANT_String_info(u2(len(cpool) + 1))
        CONSTANT_Utf8_info(*Tools.string_to_bytes(text))
        return [
            u1(JVMBytecode.getstatic),
            u2(self.print_field_ref),
            u1(JVMBytecode.ldc),
            u1(self.printable),
            u1(JVMBytecode.invokevirtual),
            u2(self.print_method_ref),
        ]


class Converter(BuiltIns):
    def __init__(self):
        self.init_index = 0

        super().__init__()

    def object(self):
        CONSTANT_Methodref_info(u2(len(cpool) + 1), u2(len(cpool) + 2))
        print(f"Object index: {len(cpool)}")
        index = CONSTANT_Class_info(u2(len(cpool) + 2))
        CONSTANT_NameAndType_info(u2(len(cpool) + 2), u2(len(cpool) + 3))
        CONSTANT_Utf8_info(*Tools.string_to_bytes("java/lang/Object"))
        self.init_index = len(cpool)
        CONSTANT_Utf8_info(*Tools.string_to_bytes("<init>"))
        CONSTANT_Utf8_info(*Tools.string_to_bytes("()V"))
        return index.index

    def this_class(self, name):
        print(f"Class index: {len(cpool)}")
        this_info_class = CONSTANT_Class_info(u2(len(cpool)) + 1)
        CONSTANT_Utf8_info(*Tools.string_to_bytes(name))
        return this_info_class.index

    def code(self):
        # https://docs.oracle.com/javase/specs/jvms/se7/html/jvms-4.html#jvms-4.7.3
        self.code_index = len(cpool)
        CONSTANT_Utf8_info(*Tools.string_to_bytes("Code"))

    @staticmethod
    def apply_type_logic(_value):
        if isinstance(_value, u1):
            return 1
        elif isinstance(_value, u2):
            return 2
        elif isinstance(_value, u4):
            return 4
        elif isinstance(_value, list):
            return [Converter.apply_type_logic(_) for _ in _value]

    def init_method(self):
        global method_count
        method_count += 1

        self.code()

        code_table = [u1(JVMBytecode.aload_0), u1(JVMBytecode.invokespecial), u2(1),
                      u1(JVMBytecode._return)]

        code_attribute_args = [
            u2(self.code_index),
            None,
            u2(1),
            u2(1),
            u4(sum(self.apply_type_logic(code_table))),
            code_table,
            u2(0),
            [],
            u2(0),
            []
        ]

        print("HUHUHUHUH")

        count = 0
        for value in code_attribute_args[2:]:
            result = self.apply_type_logic(value)
            if type(result) == list:
                count += sum(result)
            else:
                count += result

        print("init count")
        print(count)

        code_attribute_args[1] = u4(count)

        args = [
            u2(0),  # No access flag
            u2(self.init_index),
            u2(self.init_index + 1),  # ()V
            u2(1),
            [Code_attribute(
                *code_attribute_args
            )]
        ]

        method_table.append(method_info(*args))

    def main_method(self, code):
        global method_count
        method_count += 1

        # Register 'main' method on constant pool
        self.main_index = len(cpool)
        CONSTANT_Utf8_info(*Tools.string_to_bytes("main"))
        _string_index = len(cpool)
        CONSTANT_Utf8_info(*Tools.string_to_bytes("([Ljava/lang/String;)V"))

        code_table = code + [u1(JVMBytecode._return)]

        code_attribute_args = [
            u2(self.code_index),
            None,
            u2(2),
            u2(1),
            u4(sum(self.apply_type_logic(code_table))),
            code_table,
            u2(0),
            [],
            u2(0),
            []
        ]

        count = 0
        for value in code_attribute_args[2:]:
            result = self.apply_type_logic(value)
            if type(result) == list:
                for _ in result:
                    count += _
            else:
                count += result

        print("main count")
        print(count)

        code_attribute_args[1] = u4(count)

        args = [
            u2(9),  # Public static access modifier
            u2(self.main_index),  # Main file index
            u2(_string_index),
            u2(1),  # We have one attribute, the code table
            [Code_attribute(
                *code_attribute_args
            )]
        ]

        method_table.append(method_info(*args))


class JVMBytecode:
    aaload = 50
    aastore = 83
    aconst_null = 1
    aload = 25
    aload_0 = 42
    aload_1 = 43
    aload_2 = 44
    aload_3 = 45
    anewarray = 189
    areturn = 176
    arraylength = 190
    astore = 58
    astore_0 = 75
    astore_1 = 76
    astore_2 = 77
    astore_3 = 78
    athrow = 191
    baload = 51
    bastore = 84
    bipush = 16
    breakpoint = 202
    caload = 52
    castore = 85
    checkcast = 192
    d2f = 144
    d2i = 142
    d2l = 143
    dadd = 99
    daload = 49
    dastore = 82
    dcmpg = 152
    dcmpl = 151
    dconst_0 = 14
    dconst_1 = 15
    ddiv = 111
    dload = 24
    dload_0 = 38
    dload_1 = 39
    dload_2 = 40
    dload_3 = 41
    dmul = 107
    dneg = 119
    drem = 115
    dreturn = 175
    dstore = 57
    dstore_0 = 71
    dstore_1 = 72
    dstore_2 = 73
    dstore_3 = 74
    dsub = 103
    dup = 89
    dup_x1 = 90
    dup_x2 = 91
    dup2 = 92
    dup2_x1 = 93
    dup2_x2 = 94
    f2d = 141
    f2i = 139
    f2l = 140
    fadd = 98
    faload = 48
    fastore = 81
    fcmpg = 150
    fcmpl = 149
    fconst_0 = 11
    fconst_1 = 12
    fconst_2 = 13
    fdiv = 110
    fload = 23
    fload_0 = 34
    fload_1 = 35
    fload_2 = 36
    fload_3 = 37
    fmul = 106
    fneg = 118
    frem = 114
    freturn = 174
    fstore = 56
    fstore_0 = 67
    fstore_1 = 68
    fstore_2 = 69
    fstore_3 = 70
    fsub = 102
    getfield = 180
    getstatic = 178
    goto = 167
    goto_w = 200
    i2b = 145
    i2c = 146
    i2d = 135
    i2f = 134
    i2l = 133
    i2s = 147
    iadd = 96
    iaload = 46
    iand = 126
    iastore = 79
    iconst_m1 = 2
    iconst_0 = 3
    iconst_1 = 4
    iconst_2 = 5
    iconst_3 = 6
    iconst_4 = 7
    iconst_5 = 8
    idiv = 108
    if_acmpeq = 165
    if_acmpne = 166
    if_icmpeq = 159
    if_icmpge = 162
    if_icmpgt = 163
    if_icmple = 164
    if_icmplt = 161
    if_icmpne = 160
    ifeq = 153
    ifge = 156
    ifgt = 157
    ifle = 158
    iflt = 155
    ifne = 154
    ifnonnull = 199
    ifnull = 198
    iinc = 132
    iload = 21
    iload_0 = 26
    iload_1 = 27
    iload_2 = 28
    iload_3 = 29
    impdep1 = 254
    impdep2 = 255
    imul = 104
    ineg = 116
    instanceof = 193
    invokedynamic = 186
    invokeinterface = 185
    invokespecial = 183
    invokestatic = 184
    invokevirtual = 182
    ior = 128
    irem = 112
    ireturn = 172
    ishl = 120
    ishr = 122
    istore = 54
    istore_0 = 59
    istore_1 = 60
    istore_2 = 61
    istore_3 = 62
    isub = 100
    iushr = 124
    ixor = 130
    jsr = 168
    jsr_w = 201
    l2d = 138
    l2f = 137
    l2i = 136
    ladd = 97
    laload = 47
    land = 127
    lastore = 80
    lcmp = 148
    lconst_0 = 9
    lconst_1 = 10
    ldc = 18
    ldc_w = 19
    ldc2_w = 20
    ldiv = 109
    lload = 22
    lload_0 = 30
    lload_1 = 31
    lload_2 = 32
    lload_3 = 33
    lmul = 105
    lneg = 117
    lookupswitch = 171
    lor = 129
    lrem = 113
    lreturn = 173
    lshl = 121
    lshr = 123
    lstore = 55
    lstore_0 = 63
    lstore_1 = 64
    lstore_2 = 65
    lstore_3 = 66
    lsub = 101
    lushr = 125
    lxor = 131
    monitorenter = 194
    monitorexit = 195
    multianewarray = 197
    new = 187
    newarray = 188
    nop = 0
    pop = 87
    pop2 = 88
    putfield = 181
    putstatic = 179
    ret = 169
    _return = 177
    saload = 53
    sastore = 86
    sipush = 17
    swap = 95
    tableswitch = 170
    wide = 196
