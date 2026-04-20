def validate_username(name: str):
    """Basic username validation."""
    if len(name) < 3:
        return False, "Benutzername muss mindestens 3 Zeichen lang sein."
    if " " in name:
        return False, "Benutzername darf keine Leerzeichen enthalten."
    if not name.isalnum():
        return False, "Benutzername darf nur Buchstaben und Zahlen enthalten."
    return True, ""


def validate_password(pw: str):
    """Basic password validation."""
    if len(pw) < 4:
        return False, "Passwort muss mindestens 4 Zeichen lang sein."
    if " " in pw:
        return False, "Passwort darf keine Leerzeichen enthalten."
    return True, ""
