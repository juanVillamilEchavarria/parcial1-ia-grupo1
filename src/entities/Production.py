class Production:
    def __init__(self, finca, hectareas, produccion_kg, altitud_msnm, variedad):
        self.finca = finca.strip()
        self.hectareas = float(hectareas) if hectareas else None
        self.produccion_kg = float(produccion_kg) if str(produccion_kg).strip() else None
        self.altitud_msnm = float(altitud_msnm) if altitud_msnm else None
        self.variedad = variedad.strip()


    @staticmethod
    def from_dict(d : dict):
        return Production(d["finca"], d["hectareas"], d["produccion_kg"], d["altitud_msnm"], d["variedad"])
    def getProductionPerformanceByHectares(self):
        if self.hectareas is None or self.produccion_kg is None:
            return 0
        return self.produccion_kg / self.hectareas