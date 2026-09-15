import numpy as np
from services.ProductionStatisticsService import ProductionStatisticsService
from services.ProductionGraphicsService import ProductionGraphicsService


def sep(title=""):
    print("\n" + "=" * 68)
    if title:
        print(f"  {title}")
        print("=" * 68)


def print_stats(label, s):
    print(f"\n   {label}")
    print(f"     Registros   : {s.count}")
    print(f"     Suma total  : {s.sum:>12,.2f} kg")
    print(f"     Media       : {s.average:>12,.2f} kg")
    print(f"     Mediana     : {s.median:>12,.2f} kg")
    print(f"     Desv. Std   : {s.std:>12,.2f} kg")
    print(f"     Mínimo      : {s.min:>12,.2f} kg")
    print(f"     Máximo      : {s.max:>12,.2f} kg")


def main():
    service = ProductionStatisticsService()
    graphics = ProductionGraphicsService(service)
    sep("1. CARGA DE DATOS — grupo_01.csv")
    print("\n  Primeras 5 filas:")
    for i, p in enumerate(service.productions.getFiveFirstRows(), start=1):
        prod = f"{p.produccion_kg:,.0f} kg" if p.produccion_kg is not None else "FALTANTE"
        print(f"   {i}. {p.finca:<15} | {p.hectareas:>4.0f} ha | "
              f"{prod:>12} | {p.altitud_msnm:>6.0f} msnm | {p.variedad}")
    print(f"\n  Total de registros leídos: {service.productions.count()}")

    sep("2. CALIDAD DE DATOS")
    faltantes = [p.finca for p in service.productions.getItems() if p.produccion_kg is None]
    print(f"\n   Registros con dato faltante ({len(faltantes)}): {', '.join(faltantes) or 'ninguno'}")

    nombres = [p.finca for p in service.productions.getItems()]
    duplicados = {n for n in nombres if nombres.count(n) > 1}
    print(f"   Nombres de finca duplicados: {', '.join(duplicados) or 'ninguno'}")

    print("\n   Valores atípicos detectados con Puntaje Z (|z| > 3):")
    for finca, monto, z in service.getOutliers():
        print(f"     → {finca}: {monto:,.0f} kg  (z = {z:+.2f})")

    print("\n   Verificación con rendimiento por hectárea:")
    for p in service.productions.getItems():
        if p.getProductionPerformanceByHectares:
            flag = " ATÍPICO" if p.getProductionPerformanceByHectares() > 2000 else ""
            print(f"     → {p.finca:<15}: {p.getProductionPerformanceByHectares():>9,.2f} kg/ha{flag}")

    sep("3. ANÁLISIS ESTADÍSTICO (NumPy)")
    print_stats("PRODUCCIÓN — DATOS CRUDOS (incluye atípico)",
                service.getStatisticsForAllItems())
    print_stats("PRODUCCIÓN — DATOS LIMPIOS (sin atípico ni faltante)",
                service.getStatisticsForCleanItems())

    sep("4. ESTADÍSTICAS POR VARIEDAD")
    for variedad in service.getUniqueVariedades():
        print_stats(f"Variedad: {variedad}", service.getStatisticsByVariedad(variedad))

    sep("5. CORRELACIONES (Pearson)")
    print(f"\n  Altitud  ↔ Producción         r = {service.getCorrelationAltitudProduction():+.3f}")
    print(f"  Hectáreas ↔ Producción        r = {service.getCorrelationHectaresProduction():+.3f}")
    print(f"  Altitud  ↔ Rendimiento (kg/ha) r = {service.getCorrelationAltitudePerformance():+.3f}")
    print("\n   La altitud parece determinante, pero al normalizar por área la")
    print("     correlación desaparece: el efecto real es del TAMAÑO de la finca.")

    graphics.generateAll()

    sep("EDA COMPLETADO")
    print("   Gráficos: /charts/*.png")


if __name__ == "__main__":
    main()