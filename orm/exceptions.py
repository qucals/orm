class InvalidArgumentType(Exception):
    """Вызывается при несооветствии типов аргументов с типами полей таблицы"""
    pass


class IncorrectCountOfArguments(Exception):
    """Вызывается при неверном количестве передаваемых аргументов"""
    pass


class IncorrectDatabaseFileName(Exception):
    """Вызывается при некорректном имени для файла базы данных"""
    pass


class DatabaseCreationError(Exception):
    """Вызывается при ошибке создания файла базы данных"""
    pass
