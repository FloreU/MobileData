
a = "from t3.py"


def print_a():
    global a
    a = "edit in print a"
    print a


def print_a_again():
    print a
