def match_data(data: str, has_dates: bool) -> str:
    match (data, has_dates):
        case ("My data doesn't contain dates", True):
            print("Hej")
        case (_, False):
            print("He2")

# Example usage:
match_data("My data doesn't contain dates", False)
