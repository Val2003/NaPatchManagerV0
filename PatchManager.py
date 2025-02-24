import json
import os.path
from datetime import datetime
from typing import List

import TextFileSaver

from Common_polymorfic import log_level
from logger_config import get_logger

logger = get_logger(log_level)


class PatchBuilder:
    def __init__(self, work_dir, patch_number: str, ordered_list_of_tasks: list,
                 bildlog_dir: str):
        self.work_dir = work_dir
        self.patch_number = patch_number
        self.ordered_list_of_tasks = ordered_list_of_tasks
        self.patch_bildlog_dir = bildlog_dir

    def get_list_db(self):
        db_list=[]
        for task in self.ordered_list_of_tasks:
            db_list.extend(task[1])
        return db_list


    def make_dirs(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.debug(f"Directory created: {directory}")

        # Функция для создания или перезаписи файла

    def create_file(self, filepath, content=""):
        directory = os.path.dirname(filepath)
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.debug(f"Directory created: {directory}")

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.debug(f"File created: {filepath}")

    def process_files(self, base_path, files):
        for file in files:
            filepath = os.path.join(base_path, file)
            if os.path.exists(filepath):
                logger.debug(f"File exists: {filepath}")
            else:
                logger.debug(f"File not found: {filepath}")
                self.create_file(filepath, f"-- Content for {file}")

    def check_file_exists(self, filepath):
        """Проверяет существование файла."""
        if os.path.exists(filepath):
            logger.debug(f"File exists: {filepath}")
            return True
        logger.debug(f"File not found: {filepath}")
        return False

    def _write_file(self, path, file_name: str, content: str, append=False):
        mode = "a" if append else "w"
        with open(path + "\\" + file_name, mode, encoding="windows-1251") as f:
            f.write(content)
        logger.info(f"Файл {path}\\{file_name} создан")

    def generate_patch(self):
        for db in self.get_list_db():
            db_safe = db.replace(" ", "_")
            content = TextFileSaver.generate_add_sql(self.ordered_list_of_tasks, self.patch_number, db)
            cont_bat = TextFileSaver.generate_text_base_bat(db, self.work_dir, self.patch_number)
            cont_inv = TextFileSaver.generate_text_base_inv_sql(self.patch_bildlog_dir, self.patch_number, db)
            self._write_file(self.work_dir, f"add_{db_safe}.sql", content)
            self._write_file(self.work_dir, f"{db}.bat", cont_bat)
            self._write_file(self.work_dir, f"{db}_inv.sql", cont_inv)

        self._write_file(self.work_dir, "comp.sql", TextFileSaver.generate_text_comp_sql())
        self._write_file(self.work_dir, "check_rev.bat", TextFileSaver.generate_text_check_rev_bat())
        self._write_file(self.work_dir, "check_rev.py", TextFileSaver.generate_text_check_rev_py())
        self._write_file(self.work_dir, "pars.bat", TextFileSaver.generate_text_pars_bat())
        self._write_file(self.work_dir, "parsing_logs.py", TextFileSaver.generate_text_parsing_logs_py())
        self._write_file(self.work_dir, "s.bat", TextFileSaver.generate_text_s_bat())
        self._write_file(self.work_dir, "send_logs.py", TextFileSaver.generate_text_send_logs())
        self._write_file(self.work_dir, "recompile.sql", TextFileSaver.generate_text_recompile_sql())

        logger.info(f"Сборка патча {self.patch_number} завершена")


class OrderListMaker:
    def __init__(self, list_of_tasks):
        pass

    def get_rfc(self, list_of_rfc):
        pass
