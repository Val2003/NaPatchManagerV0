from Common_polymorfic import log_level
from logger_config import get_logger

logger = get_logger(log_level)


class TaskProcesing:
    def __init__(self, tasks_info: dict, tasks_objects: dict, rfc_dict: dict):
        self.tasks_info = tasks_info
        self.tasks_objects = tasks_objects
        self.rfc_dict = rfc_dict

    def filtered_and_sorted_tasks(self):
        # completed_tasks={
        #     task_id: info
        #     for task_id, info in self.tasks_info.items()
        #     if info[2].lower()=="выполнен"
        # }
        #
        # sorted_tasks=sorted(
        #     completed_tasks.items(),
        #     key=lambda  item:(item[1][0],item[0])
        # )
        return self.tasks_objects

    # def log_unlinked_objects(self):
    #     unlinked_objects = []
    #     for task_id, objects in self.tasks_objects.items():
    #         if task_id not in self.tasks_info:
    #             unlinked_objects.append(objects)
    #             continue
    #         install_order = self.tasks_info[task_id][3]
    #         if not install_order:
    #             unlinked_objects.extend(objects)
    #             continue
    #
    #         for obj in objects:
    #             if obj not in install_order:
    #                 unlinked_objects.append(obj)
    #
    #     if unlinked_objects:
    #         logger.info(f"Объекты без привязки или порядка установки")

    def get_databases_list_for_task(self, issue):
        db_list = []
        info = self.tasks_info[int(issue)]
        labels = info["labels"]
        for label in labels:
            if str(label).startswith("DB::"):
                db_list = label[4:].split()
        return db_list
    def get_mapping_db(self,issue):
        mapping_db=[]
        for db_name in self.get_databases_list_for_task(issue):

            test_bases = {
                "PSB": ["tdb1", "psbpp", "tdb9", "svpsb", "ltpsb", "psbift", "tdb02", "rna01", "ina02", "tna01"],
                "PSBE": ["tse1", "psbepp", "tse9", "svpsbe", "ltpsbe", "psbeift", "tse02", "rnae01", "inae02", "tnae01"],
                "PSBF": ["tsf3", "psbfpp", "tsf9", "svpsbf", "ltpsbf", "psbfift", "tsf02", "rnaf01", "inaf02", "tnaf01"],
                "cyp1": ["cyp1"],
                "psbsw": ["tpsbsw"],
                "TAX": ["ttax", "taxd11"],
                "skhed": ["tskhed", "dskhed"],
            }
            mapping_db.extend(test_bases[db_name])
        return mapping_db








    def get_sorted_tasks_with_objects(self):
        """Заглушка пока ральной сортировки нет"""
        sorted_tasks = self.filtered_and_sorted_tasks()
        result = []
        # for task_id, info in sorted_tasks:
        #     objects=self.tasks_objects.get(task_id,[])
        #     install_order=info[3]
        #
        #     sorted_objects=sorted(
        #         objects,
        #         key=lambda obj: install_order.index(obj) if obj in install_order else len(
        #             install_order)
        #     )
        #     result.append(task_id,sorted_objects)
        for key, inner_dict in sorted_tasks.items():
            row = [key]
            ext=self.get_mapping_db(key[1:])
            row.append(ext)
            row.extend(inner_dict)
            result.append(row)
        logger.info(f"выходной список из компаратора {result}")
        return result
