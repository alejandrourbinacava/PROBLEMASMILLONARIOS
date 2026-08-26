"""Descarga clips de casino al cache. Solo Pexels/Pixabay: no gasta creditos."""
import sys
sys.path.insert(0, ".")
from pipeline.providers.stock import StockLibrary

QUERIES = [
    "casino roulette wheel spinning", "poker chips stack close up",
    "casino slot machine lights", "playing cards dealer table",
    "las vegas casino night neon", "dice rolling table",
    "croupier hands casino table", "casino interior gambling",
    "security camera ceiling dome", "luxury hotel lobby chandelier",
    "man walking suit silhouette", "city skyline sunset silhouette",
]

lib = StockLibrary()
for query in QUERIES:
    names = []
    for _ in range(3):
        clip = lib.acquire(query, min_duration=3.0, fallback_query="")
        if clip is None:
            break
        names.append(f"{clip.path.name} <- {clip.hint[:50]}")
    print(f"{query}:")
    for name in names:
        print(f"    {name}")
