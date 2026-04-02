import math


EARTH_RADIUS_M = 6_371_000  # mètres


def haversine(lat1, lon1, lat2, lon2):
    """
    Calcule la distance en mètres entre deux points GPS (lat/lon en degrés).
    Utilisée comme heuristique admissible pour A*.
    """
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))
