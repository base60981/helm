import csv
from email.policy import default
import os
from typing import List
from collections import defaultdict
import re
import pdb
import json

from pyparsing import delimited_list
from transformers import DEBERTA_PRETRAINED_CONFIG_ARCHIVE_MAP
from common.general import ensure_file_downloaded
from common.hierarchical_logger import hlog
from .scenario import Scenario, Instance, Reference, TRAIN_TAG, VALID_TAG, TEST_TAG, CORRECT_TAG


flatten_list=lambda l: sum(map(flatten_list, l),[]) if isinstance(l,list) else [l]

class WIKIScenario(Scenario):
    """
    """

    name = "wiki"
    description = "Fact Completion in WikiData"
    tags = ["knowledge", "generation"]

    def __init__(self, subject: str):
        self.subject = subject
        assert subject in ['P31', 'P17', 'P131', 'P279', 'P20', 'P19', 'P27', 'P106', 'P127', 'P138', 'P30', 'P361', 'P407', 'P50', 'P136', 'P527', 'P57', 'P364', 'P495', 'P69', 'P1412', 'P47', 'P413', 'P54', 'P159', 'P170', 'P276', 'P108', 'P176', 'P86', 'P264', 'P1923', 'P1303', 'P449', 'P102', 'P101', 'P140', 'P39', 'P452', 'P463', 'P103', 'P166', 'P1001', 'P61', 'P178', 'P36', 'P306', 'P277', 'P937', 'P6', 'P737', 'P1906', 'P5826', 'P740', 'P135', 'P414', 'P1313', 'P1591', 'P1376', 'P2176', 'P355', 'P37', 'P189', 'P2175', 'P2568', 'P122', 'P190', 'P2293', 'P38', 'P780', 'P111', 'P35', 'P2384', 'P8111', 'P530', 'P1304', 'P3014', 'P1620', 'P1136', 'P4006', 'P4044']

    def get_instances(self) -> List[Instance]:
        # Download the raw data
        data_path = os.path.join(self.output_path, "data")
        # TODO: download the file from server

        # Read all the instances
        instances = []
        splits = {
            "train": TRAIN_TAG,
            "dev": VALID_TAG,
            "test": TEST_TAG,
        }

        for split in splits:
            json_path = os.path.join(data_path, f"{split}.jsonl")

            hlog(f"Reading {json_path}")
            with open(json_path) as f:
                all_raw_data = f.readlines()
            for line in all_raw_data:
                raw_data = json.loads(line)
                if raw_data['property'] != self.subject:
                    continue
                question, answers = raw_data['template'], flatten_list(raw_data['result_names'])

                def answer_to_reference(answer):
                    return Reference(output=" "+answer.strip(), tags=[CORRECT_TAG])

                instance = Instance(
                    input=question, references=list(map(answer_to_reference, answers)), tags=[splits[split]],
                )
                instances.append(instance)
        
        return instances


if __name__ == "__main__":
    # f = open("benchmark_output/scenarios/wiki/data/test.jsonl").readlines()
    # t = defaultdict(int)
    # for line in f:
    #     r = json.loads(line)
    #     t[len(r['result_names'])] += 1
    #     if len(r['result_names']) != 1:
    #         print(r)
    #         pdb.set_trace()
    # print(t)
    # exit(-1)
    s = WIKIScenario(subject='P31')
    s.output_path = "benchmark_output/scenarios/wiki"
    i = s.get_instances()
    for ii in i:
        print('-'*10)
        print(ii)
    pdb.set_trace()
'''
1. 71555 queries in data.tsv
 70814 have answers with qid in names.tsv
2. Do we want to have space to be the end of a question? 
clean the data so that it ends with a space.
defaultdict(<class 'int'>, {'f': 7101, 'n': 7583, 's': 44727, 'e': 1787, 'y': 5011, 'r': 899, 'h': 2991, ' ': 622, 'm': 93})
'''