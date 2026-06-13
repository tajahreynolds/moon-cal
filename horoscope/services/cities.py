"""Bundled offline city database for birth-location lookup.

No runtime geocoding API is used. Each entry carries latitude, longitude and
an IANA timezone name so the natal chart can be computed entirely offline. If a
user's birth city is missing, onboarding offers a manual lat/lon/timezone
fallback, so this list only needs to cover common cases, not every city.

Each entry: ``{"name", "country", "lat", "lon", "tz"}``.
"""

from __future__ import annotations

from typing import List, Optional

CITIES: List[dict] = [
    # North America
    {"name": "New York", "country": "US", "lat": 40.7128, "lon": -74.0060, "tz": "America/New_York"},
    {"name": "Los Angeles", "country": "US", "lat": 34.0522, "lon": -118.2437, "tz": "America/Los_Angeles"},
    {"name": "Chicago", "country": "US", "lat": 41.8781, "lon": -87.6298, "tz": "America/Chicago"},
    {"name": "Houston", "country": "US", "lat": 29.7604, "lon": -95.3698, "tz": "America/Chicago"},
    {"name": "Phoenix", "country": "US", "lat": 33.4484, "lon": -112.0740, "tz": "America/Phoenix"},
    {"name": "Philadelphia", "country": "US", "lat": 39.9526, "lon": -75.1652, "tz": "America/New_York"},
    {"name": "San Antonio", "country": "US", "lat": 29.4241, "lon": -98.4936, "tz": "America/Chicago"},
    {"name": "San Diego", "country": "US", "lat": 32.7157, "lon": -117.1611, "tz": "America/Los_Angeles"},
    {"name": "Dallas", "country": "US", "lat": 32.7767, "lon": -96.7970, "tz": "America/Chicago"},
    {"name": "San Jose", "country": "US", "lat": 37.3382, "lon": -121.8863, "tz": "America/Los_Angeles"},
    {"name": "Austin", "country": "US", "lat": 30.2672, "lon": -97.7431, "tz": "America/Chicago"},
    {"name": "San Francisco", "country": "US", "lat": 37.7749, "lon": -122.4194, "tz": "America/Los_Angeles"},
    {"name": "Seattle", "country": "US", "lat": 47.6062, "lon": -122.3321, "tz": "America/Los_Angeles"},
    {"name": "Denver", "country": "US", "lat": 39.7392, "lon": -104.9903, "tz": "America/Denver"},
    {"name": "Boston", "country": "US", "lat": 42.3601, "lon": -71.0589, "tz": "America/New_York"},
    {"name": "Atlanta", "country": "US", "lat": 33.7490, "lon": -84.3880, "tz": "America/New_York"},
    {"name": "Miami", "country": "US", "lat": 25.7617, "lon": -80.1918, "tz": "America/New_York"},
    {"name": "Detroit", "country": "US", "lat": 42.3314, "lon": -83.0458, "tz": "America/Detroit"},
    {"name": "Minneapolis", "country": "US", "lat": 44.9778, "lon": -93.2650, "tz": "America/Chicago"},
    {"name": "Las Vegas", "country": "US", "lat": 36.1699, "lon": -115.1398, "tz": "America/Los_Angeles"},
    {"name": "Portland", "country": "US", "lat": 45.5152, "lon": -122.6784, "tz": "America/Los_Angeles"},
    {"name": "Washington", "country": "US", "lat": 38.9072, "lon": -77.0369, "tz": "America/New_York"},
    {"name": "Honolulu", "country": "US", "lat": 21.3069, "lon": -157.8583, "tz": "Pacific/Honolulu"},
    {"name": "Anchorage", "country": "US", "lat": 61.2181, "lon": -149.9003, "tz": "America/Anchorage"},
    {"name": "Toronto", "country": "CA", "lat": 43.6532, "lon": -79.3832, "tz": "America/Toronto"},
    {"name": "Montreal", "country": "CA", "lat": 45.5017, "lon": -73.5673, "tz": "America/Toronto"},
    {"name": "Vancouver", "country": "CA", "lat": 49.2827, "lon": -123.1207, "tz": "America/Vancouver"},
    {"name": "Calgary", "country": "CA", "lat": 51.0447, "lon": -114.0719, "tz": "America/Edmonton"},
    {"name": "Ottawa", "country": "CA", "lat": 45.4215, "lon": -75.6972, "tz": "America/Toronto"},
    {"name": "Mexico City", "country": "MX", "lat": 19.4326, "lon": -99.1332, "tz": "America/Mexico_City"},
    {"name": "Guadalajara", "country": "MX", "lat": 20.6597, "lon": -103.3496, "tz": "America/Mexico_City"},
    {"name": "Monterrey", "country": "MX", "lat": 25.6866, "lon": -100.3161, "tz": "America/Monterrey"},
    {"name": "Havana", "country": "CU", "lat": 23.1136, "lon": -82.3666, "tz": "America/Havana"},
    {"name": "Guatemala City", "country": "GT", "lat": 14.6349, "lon": -90.5069, "tz": "America/Guatemala"},
    {"name": "Panama City", "country": "PA", "lat": 8.9824, "lon": -79.5199, "tz": "America/Panama"},
    {"name": "San Juan", "country": "PR", "lat": 18.4655, "lon": -66.1057, "tz": "America/Puerto_Rico"},
    # South America
    {"name": "Sao Paulo", "country": "BR", "lat": -23.5505, "lon": -46.6333, "tz": "America/Sao_Paulo"},
    {"name": "Rio de Janeiro", "country": "BR", "lat": -22.9068, "lon": -43.1729, "tz": "America/Sao_Paulo"},
    {"name": "Brasilia", "country": "BR", "lat": -15.7939, "lon": -47.8828, "tz": "America/Sao_Paulo"},
    {"name": "Buenos Aires", "country": "AR", "lat": -34.6037, "lon": -58.3816, "tz": "America/Argentina/Buenos_Aires"},
    {"name": "Lima", "country": "PE", "lat": -12.0464, "lon": -77.0428, "tz": "America/Lima"},
    {"name": "Bogota", "country": "CO", "lat": 4.7110, "lon": -74.0721, "tz": "America/Bogota"},
    {"name": "Medellin", "country": "CO", "lat": 6.2476, "lon": -75.5658, "tz": "America/Bogota"},
    {"name": "Santiago", "country": "CL", "lat": -33.4489, "lon": -70.6693, "tz": "America/Santiago"},
    {"name": "Caracas", "country": "VE", "lat": 10.4806, "lon": -66.9036, "tz": "America/Caracas"},
    {"name": "Quito", "country": "EC", "lat": -0.1807, "lon": -78.4678, "tz": "America/Guayaquil"},
    {"name": "Montevideo", "country": "UY", "lat": -34.9011, "lon": -56.1645, "tz": "America/Montevideo"},
    {"name": "La Paz", "country": "BO", "lat": -16.4897, "lon": -68.1193, "tz": "America/La_Paz"},
    # Europe
    {"name": "London", "country": "GB", "lat": 51.5074, "lon": -0.1278, "tz": "Europe/London"},
    {"name": "Manchester", "country": "GB", "lat": 53.4808, "lon": -2.2426, "tz": "Europe/London"},
    {"name": "Birmingham", "country": "GB", "lat": 52.4862, "lon": -1.8904, "tz": "Europe/London"},
    {"name": "Edinburgh", "country": "GB", "lat": 55.9533, "lon": -3.1883, "tz": "Europe/London"},
    {"name": "Dublin", "country": "IE", "lat": 53.3498, "lon": -6.2603, "tz": "Europe/Dublin"},
    {"name": "Paris", "country": "FR", "lat": 48.8566, "lon": 2.3522, "tz": "Europe/Paris"},
    {"name": "Marseille", "country": "FR", "lat": 43.2965, "lon": 5.3698, "tz": "Europe/Paris"},
    {"name": "Lyon", "country": "FR", "lat": 45.7640, "lon": 4.8357, "tz": "Europe/Paris"},
    {"name": "Madrid", "country": "ES", "lat": 40.4168, "lon": -3.7038, "tz": "Europe/Madrid"},
    {"name": "Barcelona", "country": "ES", "lat": 41.3851, "lon": 2.1734, "tz": "Europe/Madrid"},
    {"name": "Valencia", "country": "ES", "lat": 39.4699, "lon": -0.3763, "tz": "Europe/Madrid"},
    {"name": "Lisbon", "country": "PT", "lat": 38.7223, "lon": -9.1393, "tz": "Europe/Lisbon"},
    {"name": "Porto", "country": "PT", "lat": 41.1579, "lon": -8.6291, "tz": "Europe/Lisbon"},
    {"name": "Rome", "country": "IT", "lat": 41.9028, "lon": 12.4964, "tz": "Europe/Rome"},
    {"name": "Milan", "country": "IT", "lat": 45.4642, "lon": 9.1900, "tz": "Europe/Rome"},
    {"name": "Naples", "country": "IT", "lat": 40.8518, "lon": 14.2681, "tz": "Europe/Rome"},
    {"name": "Berlin", "country": "DE", "lat": 52.5200, "lon": 13.4050, "tz": "Europe/Berlin"},
    {"name": "Munich", "country": "DE", "lat": 48.1351, "lon": 11.5820, "tz": "Europe/Berlin"},
    {"name": "Hamburg", "country": "DE", "lat": 53.5511, "lon": 9.9937, "tz": "Europe/Berlin"},
    {"name": "Frankfurt", "country": "DE", "lat": 50.1109, "lon": 8.6821, "tz": "Europe/Berlin"},
    {"name": "Cologne", "country": "DE", "lat": 50.9375, "lon": 6.9603, "tz": "Europe/Berlin"},
    {"name": "Amsterdam", "country": "NL", "lat": 52.3676, "lon": 4.9041, "tz": "Europe/Amsterdam"},
    {"name": "Rotterdam", "country": "NL", "lat": 51.9244, "lon": 4.4777, "tz": "Europe/Amsterdam"},
    {"name": "Brussels", "country": "BE", "lat": 50.8503, "lon": 4.3517, "tz": "Europe/Brussels"},
    {"name": "Vienna", "country": "AT", "lat": 48.2082, "lon": 16.3738, "tz": "Europe/Vienna"},
    {"name": "Zurich", "country": "CH", "lat": 47.3769, "lon": 8.5417, "tz": "Europe/Zurich"},
    {"name": "Geneva", "country": "CH", "lat": 46.2044, "lon": 6.1432, "tz": "Europe/Zurich"},
    {"name": "Copenhagen", "country": "DK", "lat": 55.6761, "lon": 12.5683, "tz": "Europe/Copenhagen"},
    {"name": "Stockholm", "country": "SE", "lat": 59.3293, "lon": 18.0686, "tz": "Europe/Stockholm"},
    {"name": "Oslo", "country": "NO", "lat": 59.9139, "lon": 10.7522, "tz": "Europe/Oslo"},
    {"name": "Helsinki", "country": "FI", "lat": 60.1699, "lon": 24.9384, "tz": "Europe/Helsinki"},
    {"name": "Warsaw", "country": "PL", "lat": 52.2297, "lon": 21.0122, "tz": "Europe/Warsaw"},
    {"name": "Krakow", "country": "PL", "lat": 50.0647, "lon": 19.9450, "tz": "Europe/Warsaw"},
    {"name": "Prague", "country": "CZ", "lat": 50.0755, "lon": 14.4378, "tz": "Europe/Prague"},
    {"name": "Budapest", "country": "HU", "lat": 47.4979, "lon": 19.0402, "tz": "Europe/Budapest"},
    {"name": "Bucharest", "country": "RO", "lat": 44.4268, "lon": 26.1025, "tz": "Europe/Bucharest"},
    {"name": "Athens", "country": "GR", "lat": 37.9838, "lon": 23.7275, "tz": "Europe/Athens"},
    {"name": "Sofia", "country": "BG", "lat": 42.6977, "lon": 23.3219, "tz": "Europe/Sofia"},
    {"name": "Belgrade", "country": "RS", "lat": 44.7866, "lon": 20.4489, "tz": "Europe/Belgrade"},
    {"name": "Zagreb", "country": "HR", "lat": 45.8150, "lon": 15.9819, "tz": "Europe/Zagreb"},
    {"name": "Kyiv", "country": "UA", "lat": 50.4501, "lon": 30.5234, "tz": "Europe/Kyiv"},
    {"name": "Moscow", "country": "RU", "lat": 55.7558, "lon": 37.6173, "tz": "Europe/Moscow"},
    {"name": "Saint Petersburg", "country": "RU", "lat": 59.9311, "lon": 30.3609, "tz": "Europe/Moscow"},
    {"name": "Istanbul", "country": "TR", "lat": 41.0082, "lon": 28.9784, "tz": "Europe/Istanbul"},
    {"name": "Reykjavik", "country": "IS", "lat": 64.1466, "lon": -21.9426, "tz": "Atlantic/Reykjavik"},
    # Africa
    {"name": "Cairo", "country": "EG", "lat": 30.0444, "lon": 31.2357, "tz": "Africa/Cairo"},
    {"name": "Lagos", "country": "NG", "lat": 6.5244, "lon": 3.3792, "tz": "Africa/Lagos"},
    {"name": "Kano", "country": "NG", "lat": 12.0022, "lon": 8.5920, "tz": "Africa/Lagos"},
    {"name": "Johannesburg", "country": "ZA", "lat": -26.2041, "lon": 28.0473, "tz": "Africa/Johannesburg"},
    {"name": "Cape Town", "country": "ZA", "lat": -33.9249, "lon": 18.4241, "tz": "Africa/Johannesburg"},
    {"name": "Durban", "country": "ZA", "lat": -29.8587, "lon": 31.0218, "tz": "Africa/Johannesburg"},
    {"name": "Nairobi", "country": "KE", "lat": -1.2921, "lon": 36.8219, "tz": "Africa/Nairobi"},
    {"name": "Addis Ababa", "country": "ET", "lat": 9.0300, "lon": 38.7400, "tz": "Africa/Addis_Ababa"},
    {"name": "Casablanca", "country": "MA", "lat": 33.5731, "lon": -7.5898, "tz": "Africa/Casablanca"},
    {"name": "Marrakesh", "country": "MA", "lat": 31.6295, "lon": -7.9811, "tz": "Africa/Casablanca"},
    {"name": "Tunis", "country": "TN", "lat": 36.8065, "lon": 10.1815, "tz": "Africa/Tunis"},
    {"name": "Algiers", "country": "DZ", "lat": 36.7538, "lon": 3.0588, "tz": "Africa/Algiers"},
    {"name": "Accra", "country": "GH", "lat": 5.6037, "lon": -0.1870, "tz": "Africa/Accra"},
    {"name": "Dakar", "country": "SN", "lat": 14.7167, "lon": -17.4677, "tz": "Africa/Dakar"},
    {"name": "Kinshasa", "country": "CD", "lat": -4.4419, "lon": 15.2663, "tz": "Africa/Kinshasa"},
    {"name": "Dar es Salaam", "country": "TZ", "lat": -6.7924, "lon": 39.2083, "tz": "Africa/Dar_es_Salaam"},
    {"name": "Khartoum", "country": "SD", "lat": 15.5007, "lon": 32.5599, "tz": "Africa/Khartoum"},
    # Middle East
    {"name": "Dubai", "country": "AE", "lat": 25.2048, "lon": 55.2708, "tz": "Asia/Dubai"},
    {"name": "Abu Dhabi", "country": "AE", "lat": 24.4539, "lon": 54.3773, "tz": "Asia/Dubai"},
    {"name": "Riyadh", "country": "SA", "lat": 24.7136, "lon": 46.6753, "tz": "Asia/Riyadh"},
    {"name": "Jeddah", "country": "SA", "lat": 21.4858, "lon": 39.1925, "tz": "Asia/Riyadh"},
    {"name": "Tel Aviv", "country": "IL", "lat": 32.0853, "lon": 34.7818, "tz": "Asia/Jerusalem"},
    {"name": "Jerusalem", "country": "IL", "lat": 31.7683, "lon": 35.2137, "tz": "Asia/Jerusalem"},
    {"name": "Tehran", "country": "IR", "lat": 35.6892, "lon": 51.3890, "tz": "Asia/Tehran"},
    {"name": "Baghdad", "country": "IQ", "lat": 33.3152, "lon": 44.3661, "tz": "Asia/Baghdad"},
    {"name": "Doha", "country": "QA", "lat": 25.2854, "lon": 51.5310, "tz": "Asia/Qatar"},
    {"name": "Kuwait City", "country": "KW", "lat": 29.3759, "lon": 47.9774, "tz": "Asia/Kuwait"},
    {"name": "Beirut", "country": "LB", "lat": 33.8938, "lon": 35.5018, "tz": "Asia/Beirut"},
    {"name": "Amman", "country": "JO", "lat": 31.9454, "lon": 35.9284, "tz": "Asia/Amman"},
    # Asia
    {"name": "Tokyo", "country": "JP", "lat": 35.6762, "lon": 139.6503, "tz": "Asia/Tokyo"},
    {"name": "Osaka", "country": "JP", "lat": 34.6937, "lon": 135.5023, "tz": "Asia/Tokyo"},
    {"name": "Yokohama", "country": "JP", "lat": 35.4437, "lon": 139.6380, "tz": "Asia/Tokyo"},
    {"name": "Seoul", "country": "KR", "lat": 37.5665, "lon": 126.9780, "tz": "Asia/Seoul"},
    {"name": "Busan", "country": "KR", "lat": 35.1796, "lon": 129.0756, "tz": "Asia/Seoul"},
    {"name": "Beijing", "country": "CN", "lat": 39.9042, "lon": 116.4074, "tz": "Asia/Shanghai"},
    {"name": "Shanghai", "country": "CN", "lat": 31.2304, "lon": 121.4737, "tz": "Asia/Shanghai"},
    {"name": "Guangzhou", "country": "CN", "lat": 23.1291, "lon": 113.2644, "tz": "Asia/Shanghai"},
    {"name": "Shenzhen", "country": "CN", "lat": 22.5431, "lon": 114.0579, "tz": "Asia/Shanghai"},
    {"name": "Chengdu", "country": "CN", "lat": 30.5728, "lon": 104.0668, "tz": "Asia/Shanghai"},
    {"name": "Hong Kong", "country": "HK", "lat": 22.3193, "lon": 114.1694, "tz": "Asia/Hong_Kong"},
    {"name": "Taipei", "country": "TW", "lat": 25.0330, "lon": 121.5654, "tz": "Asia/Taipei"},
    {"name": "Bangkok", "country": "TH", "lat": 13.7563, "lon": 100.5018, "tz": "Asia/Bangkok"},
    {"name": "Singapore", "country": "SG", "lat": 1.3521, "lon": 103.8198, "tz": "Asia/Singapore"},
    {"name": "Kuala Lumpur", "country": "MY", "lat": 3.1390, "lon": 101.6869, "tz": "Asia/Kuala_Lumpur"},
    {"name": "Jakarta", "country": "ID", "lat": -6.2088, "lon": 106.8456, "tz": "Asia/Jakarta"},
    {"name": "Surabaya", "country": "ID", "lat": -7.2575, "lon": 112.7521, "tz": "Asia/Jakarta"},
    {"name": "Manila", "country": "PH", "lat": 14.5995, "lon": 120.9842, "tz": "Asia/Manila"},
    {"name": "Ho Chi Minh City", "country": "VN", "lat": 10.8231, "lon": 106.6297, "tz": "Asia/Ho_Chi_Minh"},
    {"name": "Hanoi", "country": "VN", "lat": 21.0278, "lon": 105.8342, "tz": "Asia/Ho_Chi_Minh"},
    {"name": "Mumbai", "country": "IN", "lat": 19.0760, "lon": 72.8777, "tz": "Asia/Kolkata"},
    {"name": "Delhi", "country": "IN", "lat": 28.7041, "lon": 77.1025, "tz": "Asia/Kolkata"},
    {"name": "Bangalore", "country": "IN", "lat": 12.9716, "lon": 77.5946, "tz": "Asia/Kolkata"},
    {"name": "Hyderabad", "country": "IN", "lat": 17.3850, "lon": 78.4867, "tz": "Asia/Kolkata"},
    {"name": "Chennai", "country": "IN", "lat": 13.0827, "lon": 80.2707, "tz": "Asia/Kolkata"},
    {"name": "Kolkata", "country": "IN", "lat": 22.5726, "lon": 88.3639, "tz": "Asia/Kolkata"},
    {"name": "Karachi", "country": "PK", "lat": 24.8607, "lon": 67.0011, "tz": "Asia/Karachi"},
    {"name": "Lahore", "country": "PK", "lat": 31.5204, "lon": 74.3587, "tz": "Asia/Karachi"},
    {"name": "Islamabad", "country": "PK", "lat": 33.6844, "lon": 73.0479, "tz": "Asia/Karachi"},
    {"name": "Dhaka", "country": "BD", "lat": 23.8103, "lon": 90.4125, "tz": "Asia/Dhaka"},
    {"name": "Colombo", "country": "LK", "lat": 6.9271, "lon": 79.8612, "tz": "Asia/Colombo"},
    {"name": "Kathmandu", "country": "NP", "lat": 27.7172, "lon": 85.3240, "tz": "Asia/Kathmandu"},
    {"name": "Almaty", "country": "KZ", "lat": 43.2220, "lon": 76.8512, "tz": "Asia/Almaty"},
    {"name": "Tashkent", "country": "UZ", "lat": 41.2995, "lon": 69.2401, "tz": "Asia/Tashkent"},
    # Oceania
    {"name": "Sydney", "country": "AU", "lat": -33.8688, "lon": 151.2093, "tz": "Australia/Sydney"},
    {"name": "Melbourne", "country": "AU", "lat": -37.8136, "lon": 144.9631, "tz": "Australia/Melbourne"},
    {"name": "Brisbane", "country": "AU", "lat": -27.4698, "lon": 153.0251, "tz": "Australia/Brisbane"},
    {"name": "Perth", "country": "AU", "lat": -31.9505, "lon": 115.8605, "tz": "Australia/Perth"},
    {"name": "Adelaide", "country": "AU", "lat": -34.9285, "lon": 138.6007, "tz": "Australia/Adelaide"},
    {"name": "Auckland", "country": "NZ", "lat": -36.8485, "lon": 174.7633, "tz": "Pacific/Auckland"},
    {"name": "Wellington", "country": "NZ", "lat": -41.2865, "lon": 174.7762, "tz": "Pacific/Auckland"},
]


def _label(city: dict) -> str:
    return f"{city['name']}, {city['country']}"


def search(q: str, limit: int = 8) -> List[dict]:
    """Case-insensitive search: prefix matches first, then substring matches.

    Each returned dict includes a ``label`` ("City, CC") for display.
    """
    q = (q or "").strip().lower()
    if not q:
        return []
    prefix, substring = [], []
    for city in CITIES:
        name = city["name"].lower()
        if name.startswith(q):
            prefix.append(city)
        elif q in name:
            substring.append(city)
    results = (prefix + substring)[:limit]
    return [{**c, "label": _label(c)} for c in results]


def get(name: str, country: Optional[str] = None) -> Optional[dict]:
    """Exact lookup by city name (and optional country code)."""
    name = (name or "").strip().lower()
    for city in CITIES:
        if city["name"].lower() == name and (country is None or city["country"] == country):
            return {**city, "label": _label(city)}
    return None
