from members.utils.roles import get_user_role


def role_flags(request):
    """
    Expose role-based booleans to templates.
    Read-only. No side effects.
    """
    role = get_user_role(request)
    role_display = {"OWNER": "Owner", "ADMIN": "Admin", "ACCOUNTANT": "Accountant",
                    "TEACHER": "Teacher", "STAFF": "Staff", "STUDENT": "Student", "PARENT": "Parent"}.get(role, role or "User")

    return {
        "user_role_display": role_display,
        "is_owner": role == "OWNER",
        "is_admin": role == "ADMIN",
        "is_accountant": role == "ACCOUNTANT",
        "is_teacher": role == "TEACHER",
        "is_staff": role == "STAFF",
        "is_student": role == "STUDENT",
        "is_parent": role == "PARENT",

        # Composite helpers (UX-focused)
        "can_manage_staff": role in ("OWNER", "ADMIN"),
        "can_view_finance": role in ("OWNER", "ADMIN", "ACCOUNTANT"),
        "can_add_notice": role in ("OWNER", "ADMIN"),
        "can_delete_fee": role in ("OWNER", "ADMIN"),
        "can_delete_student": role in ("OWNER", "ADMIN"),
    }
