import json
import os.path
import re
import ssl
from abc import ABC
from datetime import datetime
from typing import List
import TextFileSaver

from urllib3.exceptions import InsecureRequestWarning

import logger_config
import requests
import gitlab

from Common_polymorfic import TaskProvider, log_level

git_token = 'so5R_yfxyt35D9Cdd4pV'
# repos_url = f"https://gitlab-ci-token:{git_token}@gitlab-01/na_main/na_sourcecode.git"
HEADERS = {"PRIVATE-TOKEN": git_token}
logger = logger_config.get_logger(log_level)
gl = gitlab.Gitlab('https://gitlab-01/api/v4/', private_token=git_token, ssl_verify='CA_Promsvyazbank.crt')


class GitLabTaskProvider(TaskProvider):
    def get_tasks_and_order_objects(self):
        pass

    def __init__(self, repos_url: str, patch_number: str, list_of_tasks: list, project_id):
        super().__init__(repos_url, patch_number, list_of_tasks)
        self.project_id = project_id

    def get_issues_info(self, issue_numbers):
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        issue_numbers=[issue[1:] for issue in issue_numbers]
        issues_info = {}
        issues = []
        url = f"https://gitlab-01/api/v4/projects/{self.project_id}/issues?labels=release::{self.patch_number}"
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        response = requests.get(url, headers=HEADERS, verify=False)
        all_issues=[issue['iid'] for issue in response.json()]

        if response.status_code == 200:
            all_issues = {str(issue['iid']) for issue in response.json()}

            if not issue_numbers:
                issues = response.json()
            else:
                if set(issue_numbers) <= all_issues:
                    issues = [issue for issue in response.json() if str(issue['iid']) in issue_numbers]
                else:
                    logger.error(f"Задачи не из патча {self.patch_number}")
                    return []

            for issue in issues:
                installation_order = self._extract_installation_order(issue['description'])
                issues_info[issue['iid']] = {
                    'id': issue['iid'],
                    "project_id": issue["project_id"],
                    'state': issue['state'],
                    'type': issue['type'],
                    'status': issue['state'],
                    'labels': issue['labels'],
                    'description': issue["description"],
                    'created_at': issue['created_at'],
                    'installation_order': installation_order
                }
            logger.info(f"выходной словарь из трекера задач{issues_info}")
            return issues_info


    def check_isue_numbers(self, all_list, issue_list):
        return  str(issue_list).strip('[]') in str(all_list).strip('[]')



    def _extract_installation_order(self, description):
        match = re.search(r'порядок установки:\s*\n(.*)', description, re.IGNORECASE | re.DOTALL)
        if match:
            lines = match.group(1).strip().splitlines()
            files = [line.strip() for line in lines if line.strip()]
            return files
        return []
