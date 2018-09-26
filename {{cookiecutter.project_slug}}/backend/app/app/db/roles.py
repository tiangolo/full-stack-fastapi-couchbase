# Installed packages
from cloudant.security_document import SecurityDocument

# Types
from cloudant.database import CloudantDatabase


def add_user_or_role_to_db(
    name: str, database: CloudantDatabase, user_class="members", in_roles=False
):
    section = "roles" if in_roles else "names"
    with SecurityDocument(database) as security_document:
        class_dict = security_document.get(user_class, {})
        names = class_dict.get(section, [])
        if name not in names:
            names.append(name)
            class_dict[section] = names
            security_document[user_class] = class_dict


def add_user_to_db(username: str, database: CloudantDatabase, user_class="members"):
    add_user_or_role_to_db(username, database, user_class=user_class, in_roles=False)


def add_role_to_db(role: str, database: CloudantDatabase, user_class="members"):
    add_user_or_role_to_db(role, database, user_class=user_class, in_roles=True)


def add_user_to_db_members(username: str, database: CloudantDatabase):
    add_user_to_db(username, database, user_class="members")


def add_user_to_db_admins(username: str, database: CloudantDatabase):
    add_user_to_db(username, database, user_class="admins")


def add_role_to_db_members(role: str, database: CloudantDatabase):
    add_role_to_db(role, database, user_class="members")


def add_role_to_db_admins(role: str, database: CloudantDatabase):
    add_role_to_db(role, database, user_class="admins")
