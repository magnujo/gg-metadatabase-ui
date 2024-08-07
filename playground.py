def run_match():
    num = int(input("Enter a number between 1 and 3: "))
    one = 1
    two = 2
    three = 3
    match num:
        case one:
            print("One")
        case two:
            print("Two")
        case three:
            print("Three")
        case _:
            print("Number not between 1 and 3")

run_match()
