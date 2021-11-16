class IncorrectDatabaseFileName(Exception):
    """Вызывается при некорректном имени для файла базы данных"""
    pass


class DatabaseCreationError(Exception):
    """Вызывается при ошибке создания файла базы данных"""
    pass
