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

from dsl_parser.tests.abstract_test_parser import AbstractTestParser
from dsl_parser.parser import parse, parse_from_file


class TestParserApi(AbstractTestParser):

    def _assert_minimal_application_template(self, result):
        self.assertEquals('testApp', result['name'])
        self.assertEquals(1, len(result['nodes']))
        node = result['nodes'][0]
        self.assertEquals('testApp.testNode', node['id'])
        self.assertEquals('test_type', node['type'])
        self.assertEquals('val', node['properties']['key'])

    def test_single_node_application_template(self):
        result = parse(self.MINIMAL_APPLICATION_TEMPLATE)
        self._assert_minimal_application_template(result)

    def test_type_without_interface(self):
        yaml = self.MINIMAL_APPLICATION_TEMPLATE
        result = parse(yaml)
        self._assert_minimal_application_template(result)

    def test_import_from_path(self):
        yaml = self.create_yaml_with_imports([self.MINIMAL_APPLICATION_TEMPLATE])
        result = parse(yaml)
        self._assert_minimal_application_template(result)

    def _assert_application_template(self, result):
        node = result['nodes'][0]
        self.assertEquals('test_type', node['type'])
        plugin_props = node['plugins']['test_plugin']['properties']
        self.assertEquals('test_interface1', plugin_props['interface'])
        self.assertEquals('http://test_url.zip', plugin_props['url'])
        operations = node['operations']
        self.assertEquals('test_plugin', operations['install'])
        self.assertEquals('test_plugin', operations['test_interface1.install'])
        self.assertEquals('test_plugin', operations['terminate'])
        self.assertEquals('test_plugin', operations['test_interface1.terminate'])

    def test_type_with_single_explicit_interface_and_plugin(self):
        yaml = self.BASIC_APPLICATION_TEMPLATE + self.BASIC_INTERFACE_AND_PLUGIN + """
types:
    test_type:
        interfaces:
            -   test_interface1: "test_plugin"
        properties:
            install_agent: 'false'
            """

        result = parse(yaml)
        self._assert_application_template(result)

    def test_type_with_single_implicit_interface_and_plugin(self):
        yaml = self.APPLICATION_TEMPLATE
        result = parse(yaml)
        self._assert_application_template(result)

    def test_dsl_with_type_with_both_explicit_and_implicit_interfaces_declarations(self):
        yaml = self.create_yaml_with_imports([self.BASIC_APPLICATION_TEMPLATE, self.BASIC_INTERFACE_AND_PLUGIN]) + """
types:
    test_type:
        interfaces:
            -   test_interface1: "test_plugin"
            -   test_interface2

interfaces:
    test_interface2:
        operations:
            -   "start"
            -   "shutdown"

plugins:
    other_test_plugin:
        properties:
            interface: "test_interface2"
            url: "http://test_url2.zip"
"""
        result = parse(yaml)
        node = result['nodes'][0]
        self._assert_application_template(result)

        plugin_props = node['plugins']['other_test_plugin']['properties']
        self.assertEquals('test_interface2', plugin_props['interface'])
        self.assertEquals('http://test_url2.zip', plugin_props['url'])
        operations = node['operations']
        self.assertEquals('other_test_plugin', operations['start'])
        self.assertEquals('other_test_plugin', operations['test_interface2.start'])
        self.assertEquals('other_test_plugin', operations['shutdown'])
        self.assertEquals('other_test_plugin', operations['test_interface2.shutdown'])

    def test_merge_plugins_and_interfaces_imports(self):
        yaml = self.create_yaml_with_imports([self.BASIC_APPLICATION_TEMPLATE, self.BASIC_INTERFACE_AND_PLUGIN]) + """
plugins:
    other_test_plugin:
        properties:
            interface: "test_interface2"
            url: "http://test_url2.zip"
types:
    test_type:
        interfaces:
            -   test_interface1
            -   test_interface2

interfaces:
    test_interface2:
        operations:
            -   "start"
            -   "shutdown"
        """
        result = parse(yaml)
        node = result['nodes'][0]
        self._assert_application_template(result)

        plugin_props = node['plugins']['other_test_plugin']['properties']
        self.assertEquals('test_interface2', plugin_props['interface'])
        self.assertEquals('http://test_url2.zip', plugin_props['url'])
        operations = node['operations']
        self.assertEquals('other_test_plugin', operations['start'])
        self.assertEquals('other_test_plugin', operations['test_interface2.start'])
        self.assertEquals('other_test_plugin', operations['shutdown'])
        self.assertEquals('other_test_plugin', operations['test_interface2.shutdown'])

    def test_recursive_imports(self):
        bottom_level_yaml = self.BASIC_TYPE
        bottom_file_name = self.make_yaml_file(bottom_level_yaml)

        mid_level_yaml = self.BASIC_INTERFACE_AND_PLUGIN + """
imports:
    -   {0}""".format(bottom_file_name)
        mid_file_name = self.make_yaml_file(mid_level_yaml)

        top_level_yaml = self.BASIC_APPLICATION_TEMPLATE + """
imports:
    -   {0}""".format(mid_file_name)
        result = parse(top_level_yaml)
        self._assert_application_template(result)

    def test_parse_dsl_from_file(self):
        filename = self.make_yaml_file(self.MINIMAL_APPLICATION_TEMPLATE)
        result = parse_from_file(filename)
        self._assert_minimal_application_template(result)

    def test_parse_dsl_from_file_bad_path(self):
        self.assertRaises(EnvironmentError, parse_from_file, 'fake-file.yaml')

    def test_import_empty_list(self):
        yaml = self.MINIMAL_APPLICATION_TEMPLATE + """
imports: []
        """
        result = parse(yaml)
        self._assert_minimal_application_template(result)

    def test_diamond_imports(self):
        bottom_level_yaml = self.BASIC_TYPE
        bottom_file_name = self.make_yaml_file(bottom_level_yaml)

        mid_level_yaml = self.BASIC_INTERFACE_AND_PLUGIN + """
imports:
    -   {0}""".format(bottom_file_name)
        mid_file_name = self.make_yaml_file(mid_level_yaml)

        mid_level_yaml2 = """
imports:
    -   {0}""".format(bottom_file_name)
        mid_file_name2 = self.make_yaml_file(mid_level_yaml2)

        top_level_yaml = self.BASIC_APPLICATION_TEMPLATE + """
imports:
    -   {0}
    -   {1}""".format(mid_file_name, mid_file_name2)
        result = parse(top_level_yaml)
        self._assert_application_template(result)

    def test_node_get_type_properties_including_overriding_properties(self):
        yaml = self.BASIC_APPLICATION_TEMPLATE + """
types:
    test_type:
        properties:
            key: "not_val"
            key2: "val2"
    """
        result = parse(yaml)
        self._assert_minimal_application_template(result) #this will also check property "key" = "val"
        node = result['nodes'][0]
        self.assertEquals('val2', node['properties']['key2'])


########################################################################



    def test_type_properties_derivation(self):
        yaml = self.BASIC_APPLICATION_TEMPLATE + """
types:
    test_type:
        properties:
            key: "not_val"
            key2: "val2"
        derived_from: "test_type_parent"

    test_type_parent:
        properties:
            key: "val1_parent"
            key2: "val2_parent"
            key3: "val3_parent"
    """
        result = parse(yaml)
        self._assert_minimal_application_template(result) #this will also check property "key" = "val"
        node = result['nodes'][0]
        self.assertEquals('val2', node['properties']['key2'])
        self.assertEquals('val3_parent', node['properties']['key3'])

    def test_type_properties_recursive_derivation(self):
        yaml = self.BASIC_APPLICATION_TEMPLATE + """
types:
    test_type:
        properties:
            key: "not_val"
            key2: "val2"
        derived_from: "test_type_parent"

    test_type_parent:
        properties:
            key: "val_parent"
            key2: "val2_parent"
            key4: "val4_parent"
        derived_from: "test_type_grandparent"

    test_type_grandparent:
        properties:
            key: "val1_grandparent"
            key2: "val2_grandparent"
            key3: "val3_grandparent"
        derived_from: "test_type_grandgrandparent"

    test_type_grandgrandparent: {}
    """
        result = parse(yaml)
        self._assert_minimal_application_template(result) #this will also check property "key" = "val"
        node = result['nodes'][0]
        self.assertEquals('val2', node['properties']['key2'])
        self.assertEquals('val3_grandparent', node['properties']['key3'])
        self.assertEquals('val4_parent', node['properties']['key4'])

    def test_type_interface_derivation(self):
        yaml = self.create_yaml_with_imports([self.BASIC_APPLICATION_TEMPLATE, self.BASIC_INTERFACE_AND_PLUGIN]) + """
types:
    test_type:
        interfaces:
            -   test_interface1
            -   test_interface2: test_plugin2
            -   test_interface3
        derived_from: "test_type_parent"

    test_type_parent:
        interfaces:
            -   test_interface1: nop-plugin
            -   test_interface2
            -   test_interface3
            -   test_interface4

interfaces:
    test_interface2:
        operations:
            -   "start"
            -   "stop"
    test_interface3:
        operations:
            -   "op1"
    test_interface4:
        operations:
            -   "op2"

plugins:
    test_plugin2:
        properties:
            interface: "test_interface2"
            url: "http://test_url2.zip"
    test_plugin3:
        properties:
            interface: "test_interface3"
            url: "http://test_url3.zip"
    test_plugin4:
        properties:
            interface: "test_interface4"
            url: "http://test_url4.zip"
    """

        result = parse(yaml)
        self._assert_application_template(result)
        node = result['nodes'][0]
        plugin_props = node['plugins']['test_plugin2']['properties']
        self.assertEquals('test_interface2', plugin_props['interface'])
        self.assertEquals('http://test_url2.zip', plugin_props['url'])
        operations = node['operations']
        self.assertEquals(12, len(operations))
        self.assertEquals('test_plugin2', operations['start'])
        self.assertEquals('test_plugin2', operations['test_interface2.start'])
        self.assertEquals('test_plugin2', operations['stop'])
        self.assertEquals('test_plugin2', operations['test_interface2.stop'])
        self.assertEquals('test_plugin3', operations['op1'])
        self.assertEquals('test_plugin3', operations['test_interface3.op1'])
        self.assertEquals('test_plugin4', operations['op2'])
        self.assertEquals('test_plugin4', operations['test_interface4.op2'])
        self.assertEquals(4, len(node['plugins']))

    def test_type_interface_recursive_derivation(self):
        yaml = self.create_yaml_with_imports([self.BASIC_APPLICATION_TEMPLATE, self.BASIC_INTERFACE_AND_PLUGIN]) + """
types:
    test_type:
        interfaces:
            -   test_interface1
        derived_from: "test_type_parent"

    test_type_parent:
        derived_from: "test_type_grandparent"

    test_type_grandparent:
        interfaces:
            -   test_interface1: "non_plugin"
            -   test_interface2: "test_plugin2"

interfaces:
    test_interface2:
        operations:
            -   "start"
            -   "stop"

plugins:
    test_plugin2:
        properties:
            interface: "test_interface2"
            url: "http://test_url2.zip"
        """

        result = parse(yaml)
        self._assert_application_template(result)
        node = result['nodes'][0]
        plugin_props = node['plugins']['test_plugin2']['properties']
        self.assertEquals('test_interface2', plugin_props['interface'])
        self.assertEquals('http://test_url2.zip', plugin_props['url'])
        operations = node['operations']
        self.assertEquals(8, len(operations))
        self.assertEquals('test_plugin2', operations['start'])
        self.assertEquals('test_plugin2', operations['test_interface2.start'])
        self.assertEquals('test_plugin2', operations['stop'])
        self.assertEquals('test_plugin2', operations['test_interface2.stop'])
        self.assertEquals(2, len(node['plugins']))

        #TODO: protect from cyclic deriving
        #TODO: test for explicit interface with same operation name
        #TODO: test for relative import
        #TODO: tests for same interface twice / arrays with same values in general (node name,
        # implicit/explicit interfaces)