from abc import ABC, abstractmethod

import hvac

from logger_config import get_logger

# === Настройки===
VAULT_URL = 'https://devops-hcv.headoffice.psbank.local:8200'
GITLAB_URL = "https://gitlab-01/api/v4/"
PROJECT_ID = "123"
TUZ_usename: ""
TUZ_passw: ""
git_lab_token = "so5R_yfxyt35D9Cdd4pV"
HEADERS = {"PRIVATE-TOKEN": git_lab_token}

log_level = "DEBUG"
logger = get_logger(log_level)


class VailtAuth:
    """Аутефикация в Vailt"""

    def __init__(self):
        # requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        self.client = hvac.Client(url=VAULT_URL, verify='CA_Promsvyazbank.crt')
        self.token = self.authenticate()

    def authenticate(self):
        response = self.client.auth.ldap.login(
            username=TUZ_usename,
            password=TUZ_passw,
        )
        return response["auth"]["client_token"]

    def get_secret(self, secret_path: str, key: str):
        self.client.token = self.token
        response = self.client.secrets.kv.v2.read_secret_version(path=secret_path)
        return response["data"]["data"].get(key)


class TaskProvider(ABC):
    def __init__(self, repos_url: str, patch_number: str, issue_numbers: list):
        self.repos_url = repos_url
        self.patch_number = patch_number
        self.issue_numbers = issue_numbers

    @abstractmethod
    def get_tasks_and_order_objects(self):
        pass


class VCSProvider(ABC):
    def __init__(self, repo_url, local_path):
        self.repo_url = repo_url
        self.local_path = local_path


    @abstractmethod
    def get_tasks_and_objects(self, issue_list):
        pass

    # @abstractmethod
    # def get_files_for_bilding(self):
    #     pass


class SVNProvider(VCSProvider, ABC):
    """Заглушка"""

    def get_tasks_and_objects(self, issue_list):
        logger.info(f"Получение  SQL файлов для {issue_list} из SVN")
        return [""]


class Notifier(ABC):
    @abstractmethod
    def send(self, message, recipients):
        pass


class EmailNotifier(Notifier):
    def send(self, message, recipients):
        logger.info(f"Отправка email:{message}->{recipients}")


class MolnyaNotifier(Notifier):
    def send(self, message, recipients):
        logger.info(f"Отправка в молнию:{message}->{recipients}")


class GitlabNotifier(Notifier):
    def send(self, message, recipients):
        logger.info(f"Отправка в issue:{message}->{recipients}")


class NotificationManager:
    """Менеджер уведомлений, обьединяющий все типы отправки"""

    def __init__(self, notifiers):
        self.notifiers = notifiers

    def notify(self, message, recipients):
        for notifier in self.notifiers:
            notifier.send(message, recipients)

# gitlab_token = vault.get_secret("factoring/", "token")
# print("Gitlab token:", gitlab_token)
# db_password = vault.get_secret("factoring/show/test/od", "tfact01")
# print(db_password)
# временно
# task_provider = GitlabRepoManager
# print(task_provider.get_tasks('2102'))
# vcs_provider = GitProvider()
# builder = PatchBuilder("5.06.3113.000", ['tna01'], task_provider, vcs_provider)
# builder.generate_patch()
