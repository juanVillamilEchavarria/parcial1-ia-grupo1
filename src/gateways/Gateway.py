from app_collections.ProductionCollection import ProductionCollection
import csv

class Gateway:
    @staticmethod
    def open(path: str = "data/grupo_01.csv") -> ProductionCollection:
        with open(path, newline='', encoding='utf-8') as file:  
            return ProductionCollection.from_dict(list(csv.DictReader(file)))