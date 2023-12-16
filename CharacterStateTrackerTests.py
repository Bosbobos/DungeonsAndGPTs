import unittest
from CharacterStateTracker import SetCharacterState, CharacterStateEnum


class MockDbContext:
    def __init__(self):
        self.data = {}

    def create_record(self, table, data):
        if table not in self.data:
            self.data[table] = []
        self.data[table].append(data)

    def update_latest_record(self, table, key_field, key_value, data):
        if table in self.data:
            for record in reversed(self.data[table]):
                if record[key_field] == key_value:
                    record.update(data)
                    break

    def get_record(self, table, key_field, key_value):
        if table in self.data:
            for record in reversed(self.data[table]):
                if record[key_field] == key_value:
                    return record
        return None
