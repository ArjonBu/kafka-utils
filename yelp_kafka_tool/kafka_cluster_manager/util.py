from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import logging
import json
import os
import subprocess
import tempfile
from .cluster_info.util import get_assignment_map

KAFKA_SCRIPT_PATH = '/usr/bin/kafka-reassign-partitions.sh'


class KafkaInterface(object):
    """This class acts as an interface to interact with kafka-scripts."""

    def __init__(self, kafka_script_path=KAFKA_SCRIPT_PATH):
        self._kafka_script_path = KAFKA_SCRIPT_PATH
        self.log = logging.getLogger(self.__class__.__name__)

    def run_repartition_cmd(
        self,
        zookeeper,
        brokers,
        temp_file_name,
        is_execute=False,
    ):
        """Run reassignment kafka command based on given parameters.

        Keywords:
        temp_file_name: File containing the topic list
                        or topic-partition layout over brokers,
                        which helps reassignment script to
                        generate or execute the plan.
        is_execute:     Flag symbolizing generation or execution of plan.
        return:         Generated and Proposed plan or execution status based on
                        whether command is for generation
                        or execution respectively.
        """
        cmd_params = {}
        if is_execute:
            cmd_params['action'] = '--execute'
            cmd_params['file_flag'] = '--reassignment-json-file'
        else:
            cmd_params['action'] = '--generate'
            cmd_params['file_flag'] = '--topics-to-move-json-file'
        brokers_str = ','.join(str(e) for e in brokers)
        reassignment_path = os.path.join(
            os.path.abspath(self._kafka_script_path),
            'kafka-reassign-partitions.sh',
        )
        cmd = [
            reassignment_path,
            cmd_params['action'],
            '--zookeeper',
            zookeeper,
            cmd_params['file_flag'],
            temp_file_name,
            '--broker-list',
            brokers_str
        ]
        return subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()

        """Run reassignment kafka command based on given parameters."""
        return

    def get_cluster_assignment(self, zookeeper, brokers, topic_ids):
        """Generate the reassignment plan for given zookeeper
        configuration, brokers and topics.
        """
        topic_data = {
            'topics': [{'topic': topic_id} for topic_id in topic_ids],
            'version': 1
        }
        with tempfile.NamedTemporaryFile() as temp_topic_file:
            temp_topic_file.write(json.dumps(topic_data))
            temp_topic_file.flush()
            result = self.run_repartition_cmd(
                zookeeper,
                brokers,
                temp_topic_file.name
            )
            try:
                json_result_list = result[0].split('\n')
                curr_layout = json.loads(json_result_list[-5])
                if curr_layout:
                    assignment = get_assignment_map(curr_layout)
                    return assignment
                else:
                    raise ValueError(
                        'Output: {output} Plan Generation Error: {error}'
                        .format(output=result[0], error=result[1])
                    )
            except ValueError as error:
                self.log.error('%s', error)
                raise ValueError(
                    'Could not parse output of kafka-executable script %s',
                    result,
                )

    def execute_plan(
        self,
        proposed_layout,
        zookeeper,
        brokers,
        topics,
    ):
        """Execute the proposed plan.

        Execute the given proposed plan over given
        brokers and zookeeper configuration

        Arguments:
        proposed_plan:   Proposed plan in json format
        """
        with tempfile.NamedTemporaryFile() as temp_reassignment_file:
            json.dump(proposed_layout, temp_reassignment_file)
            temp_reassignment_file.flush()
            self.run_repartition_cmd(
                zookeeper,
                brokers,
                temp_reassignment_file.name,
                True,
            )
