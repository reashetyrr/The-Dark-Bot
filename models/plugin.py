import json
from models.DB import DB


def get_fields():
    return 'id, name, on_enable, on_disable, display'


class Plugin:
    def __init__(self, plugin_id: int, name: str, on_enable: str = None, on_disable: str = None, display: bool = False):
        self.id = plugin_id
        self.name = name
        self.on_enable = json.loads(on_enable) if on_enable else None
        self.on_disable = json.loads(on_disable) if on_disable else None
        self.display = display

    @classmethod
    def get_by_id(cls, plugin_id: int):
        result = DB().fetch_one(f'SELECT {get_fields()} FROM plugins WHERE id=%s', [plugin_id])
        return cls(*result) if result else None

    @classmethod
    def get_all(cls):
        results = DB().fetch_all(f'SELECT {get_fields()} FROM plugins WHERE display=1')
        return [cls(*result) for result in results] if results else None

    @classmethod
    def get_plugin_by_name(cls, plugin_name: str):
        result = DB().fetch_one(f'SELECT {get_fields()} FROM plugins WHERE name=%s', [plugin_name])
        return cls(*result) if result else None


if __name__ == '__main__':
    plugins = Plugin.get_all()
    pass
