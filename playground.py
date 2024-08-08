

d: dict[int, list[str]] = {

    15: ["test", 2]

}

for key, value in d.items():
    if not isinstance(key, int):
        raise TypeError(f"Expected key of type int, but got {type(key).__name__}")
    if not isinstance(value, list):
        raise TypeError(f"Expected value of type list, but got {type(value).__name__}")
    for item in value:
        if not isinstance(item, str):
            raise TypeError(f"Expected value of type str, but got {type(item).__name__}")
    print(f"Key: {key}, Value: {value}")