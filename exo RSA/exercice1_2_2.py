from exercice1_2_1 import euclide_etendu


def inverse_mod(a: int, m: int) -> int:
    pgcd, u, _ = euclide_etendu(a % m, m)
    if pgcd != 1:
        raise ValueError(f"{a} n'est pas inversible modulo {m} (pgcd = {pgcd} ≠ 1)")
    return u % m


a = int(input("Entier a : "))
m = int(input("Modulo m : "))

try:
    x = inverse_mod(a, m)
    print(f"inverse_mod({a}, {m}) = {x}   →   {a}·{x} mod {m} = {(a * x) % m}")
except ValueError as e:
    print(e)