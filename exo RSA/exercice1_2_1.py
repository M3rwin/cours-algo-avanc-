def euclide_etendu(a: int, b: int) -> tuple[int, int, int]:
    """
    Algorithme d'Euclide étendu.
    Retourne (pgcd, u, v) tels que a*u + b*v = pgcd(a, b).
    """
    if b == 0:
        return a, 1, 0

    old_r, r = a, b
    old_u, u = 1, 0
    old_v, v = 0, 1

    while r != 0:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_u, u = u, old_u - q * u
        old_v, v = v, old_v - q * v

    pgcd = old_r
    return pgcd, old_u, old_v


a = int(input("Entier a : "))
b = int(input("Entier b : "))

pgcd, u, v = euclide_etendu(a, b)
print(f"pgcd({a}, {b}) = {pgcd}  |  relation de Bézout : {a}·({u}) + {b}·({v}) = {a*u + b*v}")
if pgcd == 1:
    print(f"=> {a} et {b} sont premiers entre eux")
