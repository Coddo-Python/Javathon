from .types import *


class method_info:
    def __init__(self, access_flags: u2, name_index: u2, descriptor_index: u2, attributes_count: u2,
                 _attribute_info: list):
        self.access_flags = access_flags
        self.name_index = name_index
        self.descriptor_index = descriptor_index
        self.attributes_count = attributes_count
        self.attribute_info = table(_attribute_info)


class attribute_info:
    def __init__(self, attribute_name_index: u2, attribute_length: u2, info: list):
        self.attribute_name_index = attribute_name_index
        self.attribute_length = attribute_length
        self.info = table(info)


class Code_attribute:
    def __init__(self, attribute_name_index: u2, attribute_length: u4, max_stack: u2, max_locals: u2, code_length: u4,
                 code: list, exception_table_length: u2, exception_table: list, attributes_count: u2,
                 _attribute_info: list):
        self.attribute_name_index = attribute_name_index
        self.attribute_length = attribute_length
        self.max_stack = max_stack
        self.max_locals = max_locals
        self.code_length = code_length
        self.code = table(code)
        self.exception_table_length = exception_table_length
        self.exception_table = table(exception_table)
        self.attributes_count = attributes_count
        self.attribute_info = table(_attribute_info)
