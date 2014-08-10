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

__author__ = 'dank'

import random

from dsl_parser.tests.abstract_test_parser import AbstractTestParser
from dsl_parser.multi_instance import create_multi_instance_plan
from dsl_parser.parser import parse


def parse_multi(yaml):
    return create_multi_instance_plan(parse(yaml))


class TestMultiInstance(AbstractTestParser):

    BASE_BLUEPRINT = """
node_types:
    cloudify.types.host:
        properties:
            x:
                default: y
    db: {}
    webserver: {}
    db_dependent: {}
    type: {}
    network: {}
relationships:
    cloudify.relationships.depends_on:
        properties:
            connection_type:
                default: 'all_to_all'
    cloudify.relationships.contained_in:
        derived_from: cloudify.relationships.depends_on
    cloudify.relationships.connected_to:
        derived_from: cloudify.relationships.depends_on

node_templates:
    """

    def setUp(self):
        random.seed(0)
        AbstractTestParser.setUp(self)

    def tearDown(self):
        AbstractTestParser.tearDown(self)

    def test_single_node(self):

        yaml = self.BASE_BLUEPRINT + """

    host:
        type: cloudify.types.host
        instances:
            deploy: 2
"""

        multi_plan = parse_multi(yaml)
        nodes = multi_plan['node_instances']
        self.assertEquals(2, len(nodes))
        self.assertEquals('host_d82c0', nodes[0]['id'])
        self.assertEquals('host_c2094', nodes[1]['id'])
        self.assertEquals('host_d82c0', nodes[0]['host_id'])
        self.assertEquals('host_c2094', nodes[1]['host_id'])

    def test_two_nodes_one_contained_in_other(self):

        yaml = self.BASE_BLUEPRINT + """
    host:
        type: cloudify.types.host
    db:
        type: db
        relationships:
            -   type: cloudify.relationships.contained_in
                target: host
"""
        multi_plan = parse_multi(yaml)
        nodes = multi_plan['node_instances']
        db = nodes[0]
        host = nodes[1]
        self.assertEquals(2, len(nodes))
        self.assertEquals('host_d82c0', host['id'])
        self.assertEquals('db_c2094', db['id'])
        self.assertEquals('host_d82c0', host['host_id'])
        self.assertEquals('host_d82c0', db['host_id'])

        db_relationships = db['relationships']
        self.assertEquals(1, len(db_relationships))
        self.assertEquals('host_d82c0', db_relationships[0]['target_id'])

    def test_two_nodes_one_contained_in_other_two_instances(self):

        yaml = self.BASE_BLUEPRINT + """
    host:
        type: cloudify.types.host
        instances:
            deploy: 2
    db:
        type: db
        relationships:
            -   type: cloudify.relationships.contained_in
                target: host
"""
        multi_plan = parse_multi(yaml)
        nodes = multi_plan['node_instances']
        self.assertEquals(4, len(nodes))

        db_1 = nodes[1]
        db_2 = nodes[0]
        host_1 = nodes[2]
        host_2 = nodes[3]

        self.assertEquals('host_d82c0', host_1['id'])
        self.assertEquals('host_6baa9', host_2['id'])
        self.assertEquals('db_c2094', db_1['id'])
        self.assertEquals('db_42485', db_2['id'])
        self.assertEquals('host_d82c0', host_1['host_id'])
        self.assertEquals('host_6baa9', host_2['host_id'])
        self.assertEquals('host_d82c0', db_1['host_id'])
        self.assertEquals('host_6baa9', db_2['host_id'])

        db1_relationships = db_1['relationships']
        self.assertEquals(1, len(db1_relationships))
        self.assertEquals('host_d82c0', db1_relationships[0]['target_id'])
        db2_relationships = db_2['relationships']
        self.assertEquals(1, len(db2_relationships))
        self.assertEquals('host_6baa9', db2_relationships[0]['target_id'])

    def test_single_connected_to(self):
        yaml = self.BASE_BLUEPRINT + """
    host1:
        type: cloudify.types.host
    host2:
        type: cloudify.types.host
    db:
        type: db
        relationships:
            -   type: cloudify.relationships.contained_in
                target: host1
    webserver:
        type: webserver
        relationships:
            -   type: cloudify.relationships.contained_in
                target: host2
            -   type: cloudify.relationships.connected_to
                target: db
    db_dependent:
        type: db_dependent
        relationships:
            -   type: cloudify.relationships.contained_in
                target: host1
            -   type: cloudify.relationships.connected_to
                target: db
"""

        multi_plan = parse_multi(yaml)
        nodes = multi_plan['node_instances']
        self.assertEquals(5, len(nodes))

        db = nodes[0]
        webserver = nodes[2]
        db_dependent = nodes[1]
        host2 = nodes[4]
        host1 = nodes[3]

        self.assertEquals('db_dependent_6baa9', db_dependent['id'])
        self.assertEquals('webserver_82e2e', webserver['id'])
        self.assertEquals('db_c2094', db['id'])
        self.assertEquals('host2_42485', host2['id'])
        self.assertEquals('host1_d82c0', host1['id'])

        self.assertEquals('host1_d82c0', db_dependent['host_id'])
        self.assertEquals('host2_42485', webserver['host_id'])
        self.assertEquals('host1_d82c0', db['host_id'])
        self.assertEquals('host2_42485', host2['host_id'])
        self.assertEquals('host1_d82c0', host1['host_id'])

        db_relationships = db['relationships']
        self.assertEquals(1, len(db_relationships))
        self.assertEquals('host1_d82c0', db_relationships[0]['target_id'])
        webserver_relationships = webserver['relationships']
        self.assertEquals(2, len(webserver_relationships))
        self.assertEquals('host2_42485',
                          webserver_relationships[0]['target_id'])
        self.assertEquals('db_c2094',
                          webserver_relationships[1]['target_id'])
        db_dependent_relationships = db_dependent['relationships']
        self.assertEquals(2, len(db_dependent_relationships))
        self.assertEquals('db_c2094',
                          db_dependent_relationships[0]['target_id'])
        self.assertEquals('host1_d82c0',
                          db_dependent_relationships[1]['target_id'])

    def test_prepare_deployment_plan_single_none_host_node(self):

        yaml = self.BASE_BLUEPRINT + """
    node1_id:
        type: type
"""

        multi_plan = parse_multi(yaml)
        nodes = multi_plan['node_instances']
        self.assertEquals(1, len(nodes))
        self.assertEquals('node1_id_d82c0', nodes[0]['id'])
        self.assertTrue('host_id' not in nodes[0])

    def test_connected_to_and_contained_in_with_and_without_host_id(self):
        yaml = self.BASE_BLUEPRINT + """
    host1:
        type: cloudify.types.host
        instances:
            deploy: 2
    host2:
        type: cloudify.types.host
        instances:
            deploy: 2
    host3:
        type: cloudify.types.host
        instances:
            deploy: 2
    network:
        type: network
    db:
        type: db
        instances:
            deploy: 2
        relationships:
            -   type: cloudify.relationships.contained_in
                target: host1
    webserver1:
        type: webserver
        relationships:
            -   type: cloudify.relationships.contained_in
                target: host2
            -   type: cloudify.relationships.connected_to
                target: db
                properties:
                    connection_type: all_to_one
    webserver2:
        type: webserver
        relationships:
            -   type: cloudify.relationships.contained_in
                target: host2
            -   type: cloudify.relationships.depends_on
                target: db
                properties:
                    connection_type: all_to_all
    db_dependent:
        type: db_dependent
        relationships:
            -   type: cloudify.relationships.contained_in
                target: db
"""
        multi_plan = parse_multi(yaml)
        nodes = multi_plan['node_instances']
        print len(nodes)
        self.assertEquals(19, len(nodes))

        network_1 = nodes[15]
        host1_1 = nodes[9]
        host1_2 = nodes[17]
        host2_1 = nodes[3]
        host2_2 = nodes[14]
        host3_1 = nodes[12]
        host3_2 = nodes[13]
        webserver1_1 = nodes[4]
        webserver1_2 = nodes[16]
        webserver2_1 = nodes[5]
        webserver2_2 = nodes[8]
        db_1 = nodes[0]
        db_2 = nodes[1]
        db_3 = nodes[7]
        db_4 = nodes[18]
        db_dependent_1 = nodes[2]
        db_dependent_2 = nodes[6]
        db_dependent_3 = nodes[10]
        db_dependent_4 = nodes[11]

        network_1_id = 'network_e8e52'
        host1_1_id = 'host1_67a9c'
        host1_2_id = 'host1_d82c0'
        host2_1_id = 'host2_e87a1'
        host2_2_id = 'host2_c17c6'
        host3_1_id = 'host3_fb97d'
        host3_2_id = 'host3_cf6a6'
        webserver1_1_id = 'webserver1_40212'
        webserver1_2_id = 'webserver1_48268'
        webserver2_1_id = 'webserver2_81332'
        webserver2_2_id = 'webserver2_9e4d6'
        db_1_id = 'db_42485'
        db_2_id = 'db_c2094'
        db_3_id = 'db_c8a70'
        db_4_id = 'db_7a024'
        db_dependent_1_id = 'db_dependent_6baa9'
        db_dependent_2_id = 'db_dependent_4da5e'
        db_dependent_3_id = 'db_dependent_82e2e'
        db_dependent_4_id = 'db_dependent_95588'

        self.assertEquals(network_1_id, network_1['id'])
        self.assertEquals(host1_1_id, host1_1['id'])
        self.assertEquals(host1_2_id, host1_2['id'])
        self.assertEquals(host2_1_id, host2_1['id'])
        self.assertEquals(host2_2_id, host2_2['id'])
        self.assertEquals(host3_1_id, host3_1['id'])
        self.assertEquals(host3_2_id, host3_2['id'])
        self.assertEquals(webserver1_1_id, webserver1_1['id'])
        self.assertEquals(webserver1_2_id, webserver1_2['id'])
        self.assertEquals(webserver2_1_id, webserver2_1['id'])
        self.assertEquals(webserver2_2_id, webserver2_2['id'])
        self.assertEquals(db_1_id, db_1['id'])
        self.assertEquals(db_2_id, db_2['id'])
        self.assertEquals(db_3_id, db_3['id'])
        self.assertEquals(db_4_id, db_4['id'])
        self.assertEquals(db_dependent_1_id, db_dependent_1['id'])
        self.assertEquals(db_dependent_2_id, db_dependent_2['id'])
        self.assertEquals(db_dependent_3_id, db_dependent_3['id'])
        self.assertEquals(db_dependent_4_id, db_dependent_4['id'])

        self.assertTrue('host_id' not in network_1)
        self.assertEquals(host1_1_id, host1_1['host_id'])
        self.assertEquals(host1_2_id, host1_2['host_id'])
        self.assertEquals(host2_1_id, host2_1['host_id'])
        self.assertEquals(host2_2_id, host2_2['host_id'])
        self.assertEquals(host3_1_id, host3_1['host_id'])
        self.assertEquals(host3_2_id, host3_2['host_id'])
        self.assertEquals(host2_2_id, webserver1_1['host_id'])
        self.assertEquals(host2_1_id, webserver1_2['host_id'])
        self.assertEquals(host2_1_id, webserver2_1['host_id'])
        self.assertEquals(host2_2_id, webserver2_2['host_id'])
        self.assertEquals(host1_2_id, db_1['host_id'])
        self.assertEquals(host1_2_id, db_2['host_id'])
        self.assertEquals(host1_1_id, db_3['host_id'])
        self.assertEquals(host1_1_id, db_4['host_id'])
        self.assertEquals(host1_2_id, db_dependent_1['host_id'])
        self.assertEquals(host1_1_id, db_dependent_2['host_id'])
        self.assertEquals(host1_2_id, db_dependent_3['host_id'])
        self.assertEquals(host1_1_id, db_dependent_4['host_id'])

        network_1_relationships = network_1['relationships']
        host1_1_relationships = host1_1['relationships']
        host1_2_relationships = host1_2['relationships']
        host2_1_relationships = host2_1['relationships']
        host2_2_relationships = host2_2['relationships']
        host3_1_relationships = host3_1['relationships']
        host3_2_relationships = host2_2['relationships']
        webserver1_1_relationships = webserver1_1['relationships']
        webserver1_2_relationships = webserver1_2['relationships']
        webserver2_1_relationships = webserver2_1['relationships']
        webserver2_2_relationships = webserver2_2['relationships']
        db_1_relationships = db_1['relationships']
        db_2_relationships = db_2['relationships']
        db_3_relationships = db_3['relationships']
        db_4_relationships = db_4['relationships']
        db_dependent_1_relationships = db_dependent_1['relationships']
        db_dependent_2_relationships = db_dependent_2['relationships']
        db_dependent_3_relationships = db_dependent_3['relationships']
        db_dependent_4_relationships = db_dependent_4['relationships']

        self.assertEquals(0, len(network_1_relationships))
        self.assertEquals(0, len(host1_1_relationships))
        self.assertEquals(0, len(host1_2_relationships))
        self.assertEquals(0, len(host2_1_relationships))
        self.assertEquals(0, len(host2_2_relationships))
        self.assertEquals(0, len(host3_1_relationships))
        self.assertEquals(0, len(host3_2_relationships))

        self.assertEquals(2, len(webserver1_1_relationships))
        self.assertEquals(db_1_id, webserver1_1_relationships[0]['target_id'])
        self.assertEquals(host2_2_id,
                          webserver1_1_relationships[1]['target_id'])

        self.assertEquals(2, len(webserver1_2_relationships))
        self.assertEquals(db_1_id, webserver1_2_relationships[0]['target_id'])
        self.assertEquals(host2_1_id,
                          webserver1_2_relationships[1]['target_id'])

        self.assertEquals(5, len(webserver2_1_relationships))
        self.assertEquals(db_1_id, webserver2_1_relationships[0]['target_id'])
        self.assertEquals(db_2_id, webserver2_1_relationships[1]['target_id'])
        self.assertEquals(db_3_id, webserver2_1_relationships[2]['target_id'])
        self.assertEquals(db_4_id, webserver2_1_relationships[3]['target_id'])
        self.assertEquals(host2_1_id,
                          webserver2_1_relationships[4]['target_id'])

        self.assertEquals(5, len(webserver2_2_relationships))
        self.assertEquals(db_1_id, webserver2_2_relationships[0]['target_id'])
        self.assertEquals(db_2_id, webserver2_2_relationships[1]['target_id'])
        self.assertEquals(db_3_id, webserver2_2_relationships[2]['target_id'])
        self.assertEquals(db_4_id, webserver2_2_relationships[3]['target_id'])
        self.assertEquals(host2_2_id,
                          webserver2_2_relationships[4]['target_id'])

        self.assertEquals(1, len(db_1_relationships))
        self.assertEquals(host1_2_id, db_1_relationships[0]['target_id'])
        self.assertEquals(1, len(db_2_relationships))
        self.assertEquals(host1_2_id, db_2_relationships[0]['target_id'])
        self.assertEquals(1, len(db_3_relationships))
        self.assertEquals(host1_1_id, db_3_relationships[0]['target_id'])
        self.assertEquals(1, len(db_4_relationships))
        self.assertEquals(host1_1_id, db_4_relationships[0]['target_id'])

        self.assertEquals(1, len(db_dependent_1_relationships))
        self.assertEquals(db_2_id,
                          db_dependent_1_relationships[0]['target_id'])
        self.assertEquals(1, len(db_dependent_2_relationships))
        self.assertEquals(db_3_id,
                          db_dependent_2_relationships[0]['target_id'])
        self.assertEquals(1, len(db_dependent_3_relationships))
        self.assertEquals(db_1_id,
                          db_dependent_3_relationships[0]['target_id'])
        self.assertEquals(1, len(db_dependent_4_relationships))
        self.assertEquals(db_4_id,
                          db_dependent_4_relationships[0]['target_id'])
