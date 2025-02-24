import os

import logger_config
from git import Repo, Git, InvalidGitRepositoryError
from Common_polymorfic import VCSProvider, log_level
from collections import defaultdict

logger = logger_config.get_logger(log_level)
Git().config('--global', 'http.sslCAInfo', 'C:\\temp\\GIT\\Gitlab\\na-main\\NaPatchManagerV0\\CA_Promsvyazbank.crt')


class GitProvider(VCSProvider):
    def __init__(self, repo_url, local_path, patch_dir_for_copy, branch_name):
        super().__init__(repo_url, local_path)
        self._repo = Repo(local_path)

    def is_git_repository(self):
        """Проверяем есть ли там репозиторий"""

        try:
            _ = Repo(self.local_path)
            logger.info("локальный репозиторий git существует")
            return True
        except InvalidGitRepositoryError:
            logger.info("локальный репозиторий git не существует")
            return False

    def get_files_for_bilding(self):
        """Клонируем репозиторий"""
        # requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        if not self.is_git_repository():
            logger.info(f"клонирование репозитория {self.repo_url} в {self.local_path}")

            Repo.clone_from(self.repo_url, self.local_path, branch=self.branch)
        else:
            logger.info(f"Обновление существующего репозитория в {self.local_path}")
            repo = Repo(self.local_path)
            origin = repo.remotes.origin
            origin.pull(self.branch)

    def _added_and_modified_files(self, commit, issue):
        """Проверяем комиты на наличие привязки к нашим задачам"""
        files = []
        for diff in commit.diff(commit.parents or None):
            if diff.change_type in {'A', 'M'}:
                file_path = diff.b_path
                if file_path:
                    files.append([file_path, commit.hexsha[:8], commit.author.email,
                                  commit.committed_datetime.strftime('%Y-%m-%d %H:%M:%S')])
        logger.debug(f"for task '{issue}' files={files} in commit {commit.hexsha[:8]} autor {commit.author.email}")
        return files

    def get_tasks_and_objects(self, list_of_tasks):

        """"""
        list_of_tasks = [item[1:] for item in list_of_tasks]
        files_by_task = {}
        for commit in self._repo.iter_commits(self.branch):

            for issue in list_of_tasks:

                if issue in commit.message[1:]:

                    files = self._added_and_modified_files(commit, issue)

                    if issue not in files_by_task:
                        files_by_task[issue]=[]
                    for file in files:
                        if file not in files_by_task[issue]:
                            files_by_task[issue].append(file)

        logger.info(f"выходной словарь из гита {files_by_task}")
        return files_by_task
