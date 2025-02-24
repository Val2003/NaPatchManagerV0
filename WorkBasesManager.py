import json
import os.path
from datetime import datetime


class WorkDb:
    def __init__(self,id, name, envinonment, server, login, password, comment=""):
        self.id=id
        self.name = name
        self.environment = envinonment
        self.server = server
        self.login = login
        self.password = password
        self.comment = comment
        self.created_at = datetime.now().isoformat()

    def to_dict(self):
        return {
            "name": self.name,
            "environment": self.environment,
            "server": self.server,
            "login": self.login,
            "password": self.password,
            "comment": self.comment,
            "created_at": self.created_at
        }

    @staticmethod
    def from_dict(data):
        return WorkDb(
            data["name"], data["environment"], data["server"], data["login"], data["password"], data["comment"]
        )

    def __str__(self):
        return (f"БД:{self.name}({self.environment})\n"
                f"Сервер:{self.server}\n"

                )


class WorkDbManager:
    FILENAME = "C:\\temp\\GIT\\Gitlab\\na-main\\NaPatchManagerV0\\venv\\workDb.json"

    def __init__(self):
        self.databases = []
        self.ensure_file_exists()
        self.load_from_file()

    def add_database(self, db):
        self.databases.append(db)
        self.save_to_file()

    def list_databases(self):
        if not self.databases:
            return print("Список баз данных пуст")
        for idx, db in enumerate(self.databases, 1):
            return print(f"{idx},{db}")

    def ensure_file_exists(self):
        if not os.path.exists(self.FILENAME):
            with open(self.FILENAME, "w", encoding="utf-8") as f:
                json.dump([], f)

    def save_to_file(self):
        with open(self.FILENAME, "w", encoding="utf-8") as f:
            json.dump([db.to_dict() for db in self.databases], f, ensure_ascii=False, indent=4)

    def load_from_file(self):
        try:
            with open(self.FILENAME,"r", encoding="utf-8") as f:
                data= json.load(f)
                self.databases=[WorkDb.from_dict(db_data) for db_data in data]
        except (FileNotFoundError,json.JSONDecodeError):
            self.databases=[]
            self.save_to_file()


