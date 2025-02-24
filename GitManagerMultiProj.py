import os
import re
from datetime import datetime, timedelta

import requests
from git import Git
from urllib3.exceptions import InsecureRequestWarning

import logger_config
from Common_polymorfic import VCSProvider, log_level

logger = logger_config.get_logger(log_level)
Git().config('--global', 'http.sslCAInfo', 'CA_Promsvyazbank.crt')


class GitProviderMultiproj(VCSProvider):
    def __init__(self, repo_url, local_path, projects, token, dict_from_task_manager):
        super().__init__(repo_url, local_path)
        self.repo = repo_url
        self.projects = projects
        self.headers = {'PRIVATE-TOKEN': token}
        self.issue_numbers = self.get_issues_list(dict_from_task_manager)

    # def get_paginated_data(self, url, params=None):
    #     all_data = []
    #     if params is None:
    #         params = {"per_page": 100}
    #         page = 1
    #         while True:
    #             params["page"] = page
    #             requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    #             response = requests.get(url, headers=self.headers, params=params, verify=False)
    #             if response.status_code != 200:
    #                 break
    #             data = response.json()
    #             if not data:
    #                 break
    #             all_data.extend(data)
    #             next_page = response.headers.get("X-Next-Page")
    #             if not next_page:
    #                 break
    #             page = int(next_page)
    #     return all_data
    def get_issues_list(self, dict_from_task_manager: dict):
        issues_list = []
        for issues in dict_from_task_manager:
            issues_list.append("#" + str(issues))

        return issues_list

    def get_branches(self, project_id):
        """ Получает список всех веток проекта
        :return:Список названий веток
        """
        url = f"{self.repo_url}/projects/{project_id}/repository/branches"
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        response = requests.get(url, headers=self.headers, verify=False)
        if response.status_code == 200:

            return [branch["name"] for branch in response.json()]
        else:
            logger.info(f"Ошибка получения веток:{response.text}")
            return []

    def get_commits(self, branch: str, project_id, days: int = 360):
        """ Получает комиты в указанной ветке за последние 'days' дней
        :param brench: Название ветки
        :param project_id: id проекта(репозитория) в Gitlab
        :param days: количество дней, за которые получать коммиты( по умолчанию 365 дней)
        """
        since_date = (datetime.now() - timedelta(days=days)).isoformat()
        url = f"{self.repo_url}/projects/{project_id}/repository/commits"
        params = {"per_page": 100, "since": since_date, "ref_name": branch}  # "ref_name": branch, "since": since_date
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        response = requests.get(url, headers=self.headers, params=params, verify=False)

        return [
            {
                "commit_id": commit["id"][:8],
                "author": commit["author_name"],
                "date": commit["created_at"],
                "message": commit["message"],
                "branch": branch
            }
            for commit in response.json()
        ] if response.status_code == 200 else []

    def get_commit_files(self, commit_id: str, project_id):
        """ Получает список файлов, измененных в данном коммите
        :param commit_id: Хеш коммита укороченный
        :param project_id:  id проекта Гитлаба
        :return: Список путей измененных файлов(полное имя файла)
        """

        url = f"{self.repo_url}/projects/{project_id}/repository/commits/{commit_id}/diff"
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        response = requests.get(url, headers=self.headers, verify=False)
        return [file["new_path"] for file in response.json()] if response.status_code == 200 else []

    def scan_single_proj(self, project_id, days: int = 360):
        """ выдает словарь по задачам из определенного проекта(репозитория)
         :param project_id: id проекта Гитлаба
         :param days: Количество дней для фильтрации коммитов
         :return: Словарь issues с файлами, и их паратрами по репозиторию
         """
        branches = self.get_branches(project_id)
        project_name = self.get_project_name(project_id)
        issue_files = {str(issue): [] for issue in self.issue_numbers}
        for branch in branches:
            commits = self.get_commits(branch, project_id, days)
            for commit in commits:
                for issue_number in self.issue_numbers:
                    if issue_number in commit["message"]:
                        files = self.get_commit_files(commit["commit_id"], project_id)
                        if files:
                            for file in files:
                                local_file_path = self.get_files_for_bilding(project_id, file, commit["commit_id"])
                                issue_files[str(issue_number)].append([
                                    file,
                                    commit["commit_id"],
                                    commit["author"],
                                    commit["date"],
                                    project_name,
                                    branch,
                                    local_file_path

                                ])
        rezult = {k: v for k, v in issue_files.items() if v}
        logger.info(f"выходной словарь из проекта {project_id} {rezult}")
        return rezult

    def sanitize_filename(self, filename):
        """Убираем запрещенные символы в Windows и заменяем прямые слеши на обратные"""
        new_filename = re.sub(r'[<>:"\\|?*]', '_', filename)
        repl_slash = new_filename.replace("/", "\\")
        return repl_slash

    def get_files_for_bilding(self, project_id, filename, commit_id):
        """ Копирует файлы из репозитория в локалный каталог, сохраняя структуру директорий
        :param project_id: id проекта Гитлаба
        :param filename: имя файла с путями, который мы вытащили из коммита
        :param commit_id: id коммита
        :return: возвращаем локальный путь до скачанного файла
        """

        project_name = self.get_project_name(project_id)
        project_dir = os.path.join(self.local_path, project_name)

        safe_file_path = self.sanitize_filename(filename)
        local_file_path = os.path.join(project_dir, safe_file_path)

        if os.name == "nt" and len(local_file_path) > 240:
            local_file_path = f"\\\\?\\{local_file_path}"

        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

        file_url = f"{self.repo}/projects/{project_id}/repository/files/{filename.replace('/', '%2F')}/raw?ref={commit_id}"
        response = requests.get(file_url, headers=self.headers, verify=False)

        if response.status_code == 200:
            with open(local_file_path, "w", encoding="utf-8") as f:
                f.write(response.text)

            logger.info(f"Файл {filename} скачан в {local_file_path}")

        else:
            logger.info(f"Не удалось скачать {filename} (код {response.status_code})")

        return local_file_path

    def get_project_name(self, project_id):
        """Получает имя проекта по его ID
        :param project_id: id проекта Гитлаба
        :return: имя проекта(репозитория)
        """
        url = f"{self.repo_url}/projects/{project_id}"
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        response = requests.get(url, headers=self.headers, verify=False)
        return response.json().get("name", f"project_{project_id}") if response.status_code == 200 else []

    def get_tasks_and_objects(self, issue_list):
        """Получает обьединенный словарь из нескольких репозиториев сгруппированный по задачам
        :param issue_list:
        :return: Словарь где ключи номера issue а значения список обьектов(файлов) их их параметров
        """
        all_issues = {}
        for project in self.projects:
            project_issues = self.scan_single_proj(project)
            for issue, commits in project_issues.items():
                if issue not in all_issues:
                    all_issues[issue] = []
                all_issues[issue].extend(commits)
        logger.info(f"выходной словарь из гита {all_issues}")

        return all_issues
