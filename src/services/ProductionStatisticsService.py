import numpy as np
from gateways.Gateway import Gateway
from app_collections.ProductionCollection import ProductionCollection
from enums.ProductionEnum import ProductionEnum
from entities.Production import Production
from dto.ProductionStatisticsDTO import ProductionStatisticsDTO
from dto.ProductionPerformanceDTO import ProductionPerformanceDTO


class ProductionStatisticsService:
    OUTLIER_THRESHOLD = 10000
    Z_THRESHOLD = 3.0

    def __init__(self):
        self.productions: ProductionCollection = Gateway.open()

    def getProductionAmounts(self) -> np.ndarray:
        """Producción cruda. Los faltantes quedan como NaN."""
        return np.array([
            p.produccion_kg if p.produccion_kg is not None else np.nan
            for p in self.productions.getItems()
        ], dtype=np.float64)   

    def getCleanProductionAmounts(self) -> np.ndarray:
        return np.array([p.produccion_kg for p in self.getCleanProductions()], dtype=np.float64)

    def getHectares(self) -> np.ndarray:
        return np.array([p.hectareas for p in self.getCleanProductions()], dtype=np.float64)

    def getAltitudes(self) -> np.ndarray:
        return np.array([p.altitud_msnm for p in self.getCleanProductions()], dtype=np.float64)

    def getYieldPerHectare(self) -> np.ndarray:
        return np.array([p.getProductionPerformanceByHectares() for p in self.getCleanProductions()], dtype=np.float64)

    def getVariedades(self) -> list[str]:
        return [p.variedad for p in self.getCleanProductions()]

    def getUniqueVariedades(self) -> list[str]:
        return sorted(set(self.getVariedades()))

    def getCleanProductionAmountsByVariedad(self, variedad: str) -> np.ndarray:
        return np.array([
            p.produccion_kg for p in self.productions.getCleanByKey(ProductionEnum.VARIEDAD, variedad, self.OUTLIER_THRESHOLD)
        ], dtype=np.float64)

    def getProductionAmountsByVariedad(self, value: str) -> np.ndarray:
        """Producción por variedad (datos crudos, incluye faltantes como NaN)."""
        return np.array([
            p.produccion_kg if p.produccion_kg is not None else np.nan
            for p in self.productions.getByKey(ProductionEnum.VARIEDAD, value)
        ], dtype=np.float64)

    def getStatistics(self, data: np.ndarray) -> ProductionStatisticsDTO:
        if len(data) == 0:
            return ProductionStatisticsDTO(0, 0, 0, 0, 0, 0, 0)
        return ProductionStatisticsDTO(
            np.mean(data),
            np.median(data),
            np.std(data),
            np.min(data),
            np.max(data),
            len(data),
            np.sum(data)
        )

    def getStatisticsForAllItems(self) -> ProductionStatisticsDTO:
        data = self.getProductionAmounts()
        data = data[~np.isnan(data)] 
        return self.getStatistics(data)

    def getStatisticsForCleanItems(self) -> ProductionStatisticsDTO:
        return self.getStatistics(self.getCleanProductionAmounts())

    def getStatisticsByVariedad(self, value: str) -> ProductionStatisticsDTO:
        data = self.getProductionAmountsByVariedad(value)
        data = data[~np.isnan(data)]
        return self.getStatistics(data)


    def getProductionPerformanceByHectares(self) -> list[ProductionPerformanceDTO]:
        return [
            ProductionPerformanceDTO(production.finca, production.getProductionPerformanceByHectares())
            for production in self.productions.getItems()
            if production.getProductionPerformanceByHectares() is not None
        ]


    def getOutliers(self) -> list[tuple]:
        """Retorna (finca, produccion, z_score) de los valores atípicos."""
        data = self.getProductionAmounts()
        data = data[~np.isnan(data)]
        mean, std = np.mean(data), np.std(data)
        if std == 0:
            return []
        return [
            (p.finca, p.produccion_kg, (p.produccion_kg - mean) / std)
            for p in self.productions.getValidProductions()
            if abs((p.produccion_kg - mean) / std) > self.Z_THRESHOLD
        ]

   

    def getCorrelation(self, a: np.ndarray, b: np.ndarray) -> float:
        if len(a) < 2:
            return 0.0
        return float(np.corrcoef(a, b)[0, 1])

    def getCorrelationAltitudProduction(self) -> float:
        return self.getCorrelation(self.getAltitudes(), self.getCleanProductionAmounts())

    def getCorrelationHectaresProduction(self) -> float:
        return self.getCorrelation(self.getHectares(), self.getCleanProductionAmounts())

    def getCorrelationAltitudePerformance(self) -> float:
        return self.getCorrelation(self.getAltitudes(), self.getYieldPerHectare())



    def getCleanProductions(self) -> list[Production]:
        return self.productions.getCleanProductions(self.OUTLIER_THRESHOLD)