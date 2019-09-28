from allinbot.database import DatabaseTask, QueryBuilder


class FetchAllinMembersDatabaseTask(DatabaseTask[dict]):
    def execute_with_database(self, db: QueryBuilder) -> dict:
        return db.child("members").order_by_child("is_full_member").equal_to(True).get()
