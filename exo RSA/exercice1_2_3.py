from exercice1_2_1 import euclide_etendu


def euler_totient(m: int) -> int:
    """Calcule φ(m) = nombre d'entiers dans [1, m] premiers avec m."""
    result = m
    n = m
    p = 2
    while p * p <= n:
        if n % p == 0:
            while n % p == 0:
                n //= p
            result -= result // p
        p += 1
    if n > 1:
        result -= result // n
    return result


def inverse_mod(a: int, m: int) -> int:
    """
    Retourne l'inverse de a modulo m via le théorème d'Euler.

    Théorème d'Euler : si pgcd(a, m) = 1, alors  a^φ(m) ≡ 1 (mod m)
    Donc  a^(φ(m)−1) ≡ a^(−1) (mod m).
    """
    pgcd, _, _ = euclide_etendu(a % m, m)
    if pgcd != 1:
        raise ValueError(f"{a} n'est pas inversible modulo {m} (pgcd = {pgcd} ≠ 1)")

    phi = euler_totient(m)
    return pow(a, phi - 1, m)


a = int(input("Entier a : "))
m = int(input("Modulo m : "))

try:
    x = inverse_mod(a, m)
    print(f"φ({m}) = {euler_totient(m)}")
    print(f"inverse_mod({a}, {m}) = {a}^(φ({m})−1) mod {m} = {x}   →   {a}·{x} mod {m} = {(a * x) % m}")
except ValueError as e:
    print(e)