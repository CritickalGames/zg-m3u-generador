def clave_ordenamiento(name: str):
    name = name.strip()
    if not name:
        return (3, "")
    first_char = name[0]
    if not first_char.isalnum():
        return (0, name.lower())
    elif first_char.isdigit():
        return (1, name.lower())
    else:
        return (2, name.lower())