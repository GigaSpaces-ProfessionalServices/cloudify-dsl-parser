########
# Copyright (c) 2013 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.

__author__ = 'ran'

from dsl_parser.parser import DSLParsingFormatException
from dsl_parser.tests.abstract_test_parser import AbstractTestParser


class TestParserFormatExceptions(AbstractTestParser):

    def test_empty_dsl(self):
        self._assert_dsl_parsing_exception_error_code('', 0, DSLParsingFormatException)

    def test_illegal_yaml_dsl(self):
        yaml = """
interfaces:
    test_interface:
        -   item1: {}
    -   bad_format: {}
        """
        self._assert_dsl_parsing_exception_error_code(yaml, -1, DSLParsingFormatException)

    def test_no_application_template(self):
        yaml = """
interfaces:
    test_interface2:
        operations:
            -   "install"
            -   "terminate"
            """
        self._assert_dsl_parsing_exception_error_code(yaml, 1, DSLParsingFormatException)

    def test_no_application_template_name(self):
        yaml = """
application_template:
    topology:
        -   name: testNode
            type: test_type
            properties:
                key: "val"
        """
        self._assert_dsl_parsing_exception_error_code(yaml, 1, DSLParsingFormatException)

    def test_illegal_first_level_property(self):
        yaml = """
application_template:
    topology:
        -   name: testNode
            type: test_type
            properties:
                key: "val"

illegal_property:
    illegal_sub_property: "some_value"
        """
        self._assert_dsl_parsing_exception_error_code(yaml, 1, DSLParsingFormatException)

    def test_node_without_name(self):
        yaml = """
application_template:
    name: testApp
    topology:
        -   type: test_type
            properties:
                key: "val"
        """
        self._assert_dsl_parsing_exception_error_code(yaml, 1, DSLParsingFormatException)

    def test_node_without_type_declaration(self):
        yaml = """
application_template:
    name: testApp
    topology:
        -   name: testNode
            properties:
                key: "val"
        """
        self._assert_dsl_parsing_exception_error_code(yaml, 1, DSLParsingFormatException)

    def test_interface_with_no_operations(self):
        yaml = self.BASIC_APPLICATION_TEMPLATE + """
interfaces:
    test_interface1: {}
        """
        self._assert_dsl_parsing_exception_error_code(yaml, 1, DSLParsingFormatException)

    def test_interface_with_empty_operations_list(self):
        yaml = self.MINIMAL_APPLICATION_TEMPLATE + """
interfaces:
    test_interface1:
        operations: {}
        """
        self._assert_dsl_parsing_exception_error_code(yaml, 1, DSLParsingFormatException)

    def test_interface_with_duplicate_operations(self):
        yaml = self.MINIMAL_APPLICATION_TEMPLATE + """
interfaces:
    test_interface1:
        operations:
            -   "install"
            -   "terminate"
            -   "install"
        """
        self._assert_dsl_parsing_exception_error_code(yaml, 1, DSLParsingFormatException)

    def test_type_with_illegal_interface_declaration(self):
        yaml = self.BASIC_APPLICATION_TEMPLATE + self.BASIC_INTERFACE_AND_PLUGIN + """
types:
    test_type:
        interfaces:
            -   test_interface1: "test_plugin"
                some_other_property: "meh"

            """
        self._assert_dsl_parsing_exception_error_code(yaml, 1, DSLParsingFormatException)

    def test_type_with_illegal_interface_declaration_2(self):
        yaml = self.BASIC_APPLICATION_TEMPLATE + self.BASIC_INTERFACE_AND_PLUGIN + """
types:
    test_type:
        interfaces:
            -   test_interface1:
                    explicit_plugin1: "test_plugin1"
                    explicit_plugin2: "test_plugin2"
            """
        self._assert_dsl_parsing_exception_error_code(yaml, 1, DSLParsingFormatException)

    def test_type_with_empty_interfaces_declaration(self):
        yaml = self.BASIC_APPLICATION_TEMPLATE + self.BASIC_INTERFACE_AND_PLUGIN + """
types:
    test_type:
        interfaces: {}
            """
        self._assert_dsl_parsing_exception_error_code(yaml, 1, DSLParsingFormatException)

    def test_dsl_with_explicit_interface_mapped_to_two_plugins(self):
        yaml = self.BASIC_APPLICATION_TEMPLATE + self.BASIC_INTERFACE_AND_PLUGIN + """
types:
    test_type:
        interfaces:
            -   test_interface1:
                    -   "test_plugin"
                    -   "test_plugin2"
        properties:
            install_agent: 'false'
"""
        self._assert_dsl_parsing_exception_error_code(yaml, 1, DSLParsingFormatException)

    def test_node_extra_properties(self):
        #testing for additional properties directly under node (i.e. not within the node's 'properties' section)
        yaml = self.BASIC_APPLICATION_TEMPLATE + """
            extra_property: "val"
            """
        self._assert_dsl_parsing_exception_error_code(yaml, 1, DSLParsingFormatException)

    def test_plugin_without_url(self):
        yaml = self.MINIMAL_APPLICATION_TEMPLATE + """
interfaces:
    test_interface1:
        operations:
            -   "install"

plugins:
    test_plugin:
        properties:
            interface: "test_interface1"
            """
        self._assert_dsl_parsing_exception_error_code(yaml, 1, DSLParsingFormatException)

    def test_import_bad_syntax(self):
        yaml = """
imports: fake-file.yaml
        """
        self._assert_dsl_parsing_exception_error_code(yaml, 2, DSLParsingFormatException)

    def test_import_bad_syntax2(self):
        yaml = """
imports:
    first_file: fake-file.yaml
        """
        self._assert_dsl_parsing_exception_error_code(yaml, 2, DSLParsingFormatException)

    def test_import_bad_syntax3(self):
        yaml = """
imports:
    -   first_file: fake-file.yaml
        """
        self._assert_dsl_parsing_exception_error_code(yaml, 2, DSLParsingFormatException)

    def test_duplicate_import_in_same_file(self):
        yaml = """
imports:
    -   fake-file.yaml
    -   fake-file2.yaml
    -   fake-file.yaml
        """
        self._assert_dsl_parsing_exception_error_code(yaml, 2, DSLParsingFormatException)

    def test_type_multiple_derivation(self):
        yaml = self.BASIC_APPLICATION_TEMPLATE + """
types:
    test_type:
        properties:
            key: "not_val"
        derived_from:
            -   "test_type_parent"
            -   "test_type_parent2"

    test_type_parent:
        properties:
            key: "val1_parent"
    test_type_parent2:
        properties:
            key: "val1_parent2"
    """
        self._assert_dsl_parsing_exception_error_code(yaml, 1, DSLParsingFormatException)

    def test_plugin_without_interface(self):
        yaml = self.MINIMAL_APPLICATION_TEMPLATE + """
interfaces:
    test_interface1:
        operations:
            -   "install"

plugins:
    test_plugin:
        properties:
            url: "http://test_url.zip"
            """
        self._assert_dsl_parsing_exception_error_code(yaml, 1, DSLParsingFormatException)

    def test_plugin_with_extra_properties(self):
        yaml = self.MINIMAL_APPLICATION_TEMPLATE + """
interfaces:
    test_interface1:
        operations:
            -   "install"

plugins:
    test_plugin:
        properties:
            url: "http://test_url.zip"
            interface: "test_interface1"
            extra_prop: "some_val"
            """
        self._assert_dsl_parsing_exception_error_code(yaml, 1, DSLParsingFormatException)