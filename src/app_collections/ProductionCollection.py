from entities.Production import Production
from enums.ProductionEnum import ProductionEnum
class ProductionCollection:
    def __init__(self, productions : list[Production]):
        self.productions: list[Production] = productions

    @staticmethod
    def from_dict( productions : list[dict]):
        return ProductionCollection(list(map(Production.from_dict, productions)))
    def getValidProductions(self) -> list[Production]:
            """Registros con producción registrada."""
            return [p for p in self.productions if p.produccion_kg is not None]
    
    def getCleanProductions(self, outlier: float) -> list[Production]:
            """Registros aptos para el análisis: producción válida y sin atípicos."""
            return [p for p in self.getValidProductions()
                    if p.produccion_kg <= outlier]

    def getByKey(self, key: ProductionEnum, value )-> list[Production]:
        return list(filter(lambda production: getattr(production, key) == value, self.getValidProductions()))
    def getCleanByKey(self, key: ProductionEnum, value, outlier: float ):
        return list(filter(lambda production: getattr(production, key) == value, self.getCleanProductions( outlier)))
    def count(self):
        return len(self.productions)

    def getFiveFirstRows(self):
        return self.productions[:5]
    def getItems(self):
        return self.productions