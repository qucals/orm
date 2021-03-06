class IncompatibleProperty(Exception):
    """Вызывается при задании несовместимых свойств для поля таблицы"""
    pass


class ArgumentNotFound(Exception):
    """Вызывается, когда аргумент не находится в списке полей таблицы"""
    pass


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
