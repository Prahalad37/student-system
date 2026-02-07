def is_owner(user):
    return user.userprofile.role == "OWNER"


def is_admin(user):
    return user.userprofile.role in ["OWNER", "ADMIN"]


def is_accountant(user):
    return user.userprofile.role in ["OWNER", "ADMIN", "ACCOUNTANT"]


def is_teacher(user):
    return user.userprofile.role in ["OWNER", "ADMIN", "TEACHER"]
