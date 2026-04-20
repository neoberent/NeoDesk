def get_modules(role: str | None = None) -> list[dict]:
    modules = [
        {"title": "Chat", "open": "chat"},
        {"title": "Notizen", "open": "notes"},
    ]
    admin_modules = [{"title": "Adminbereich", "open": "admin"}]
    if role and role.lower() == "admin":
        return modules + admin_modules
    return modules
