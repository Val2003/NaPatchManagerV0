import logger_config
from GitManagerMultiProj import GitProviderMultiproj
from GitlabTaskManager import GitLabTaskProvider
from PatchManager import PatchBuilder
from Gitlab_TaskProcessing import TaskProcesing

log_level = "DEBUG"
my_logger = logger_config.get_logger(log_level)
git_token = 'so5R_yfxyt35D9Cdd4pV'

rfc_dict = {}
projects = ['2102','9956']
task_proj_id = '2102'


class Config:
    """Конфигурация для сборки патча"""

    def __init__(self, repos_url, local_repo, local_dir, branch_name, work_dir, patch_number,
                 patch_log_dir, issue_numbers):
        self.repos_url = repos_url
        self.local_repo = local_repo
        self.local_dir = local_dir
        self.branch_name = branch_name
        self.work_dir = work_dir
        self.patch_number = patch_number
        self.patch_log_dir = patch_log_dir
        self.issue_numbers = issue_numbers


class PatchBilderManager:
    def __init__(self, config, rfc_dict, scenario="patch_add"):
        self.config = config
        self.rfc_dict = rfc_dict
        self.scenario = scenario

    def run(self):
        """Патч добавка"""
        my_logger.info(f"Запуск сценария:{self.scenario}")
        # 1 Получаем приоритеты задач
        task_man = GitLabTaskProvider(self.config.repos_url, self.config.branch_name, self.config.issue_numbers,
                                      task_proj_id)
        """получаем словарб с задачами и приоритетами"""
        list_of_task_priority = task_man.get_issues_info(self.config.issue_numbers)
        # 2.Обрабатываем задачи и обьекты на сортировку



        # 3.Работа с Git
        """создаем класс для получения Git репы"""
        git_provider = GitProviderMultiproj(self.config.repos_url, self.config.local_dir, projects,
                                            git_token,list_of_task_priority)

        # 2.Получаем задачи и обьекты
        """получаем словарь из задач с обьектами для установки"""
        getting_task_and_obj = git_provider.get_tasks_and_objects(self.config.issue_numbers)
        """ создем класс для получения задач"""


        task_proc = TaskProcesing(list_of_task_priority, getting_task_and_obj, rfc_dict={})

        list_proc = task_proc.get_sorted_tasks_with_objects()
        # 5.Генерация патча
        builder = PatchBuilder(self.config.work_dir, self.config.patch_number, list_proc,
                               self.config.patch_log_dir)
        builder.get_list_db()
        builder.generate_patch()


config = Config(
    repos_url=f"https://gitlab-ci-token:{git_token}@gitlab-01/api/v4",
    local_repo="c:\\temp\\test-git",
    work_dir="C:\\temp\\test_folder2",
    local_dir="c:\\temp\\target_folder",
    branch_name="5.06.3078.001",
    patch_log_dir="c:\\temp\\patch_log_dir",
    #db_list=["INAE02", "INAF02", "INA02", "TNA01"],
    patch_number="5.06.3078.001",
    issue_numbers=["#13", "#10"]  #"#13", "#10"
)

patch_manager = PatchBilderManager(config, rfc_dict, scenario="патч_добавка")
patch_manager.run()
