import os
import numpy as np
import matplotlib
matplotlib.use("Agg") 
from matplotlib import pyplot as plt

from services.ProductionStatisticsService import ProductionStatisticsService


class ProductionGraphicsService:
    """
    Genera los gráficos del EDA y los guarda como PNG en /charts.
    Consume únicamente lo que expone ProductionStatisticsService.
    """

    CHARTS_DIR = "charts"

    VARIEDAD_COLORS = {
        "Castillo": "#4C72B0",  
        "Caturra":  "#DD8452",   
        "Colombia": "#55A868",   
    }
    VARIEDAD_MARKERS = {
        "Castillo": "o",   
        "Caturra":  "s",  
        "Colombia": "^",   
    }

    def __init__(self, statistics_service: ProductionStatisticsService = None):
        self.service = statistics_service or ProductionStatisticsService()
        os.makedirs(self.CHARTS_DIR, exist_ok=True)

   

    def _save(self, fig, filename):
        path = os.path.join(self.CHARTS_DIR, filename)
        fig.tight_layout()                      
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)                          
        print(f"    Gráfico guardado: {path}")


    def generateAmountDistributionGraph(self, filename="01_distribucion_produccion.png"):
        """
        Histograma comparativo de produccion_kg:
          Panel A → datos crudos (con el valor atípico de 51.000 kg)
          Panel B → datos limpios (sin el atípico)
        Demuestra visualmente por qué el outlier debe tratarse.
        """
        raw = self.service.getProductionAmounts()
        raw = raw[~np.isnan(raw)]                      
        clean = self.service.getCleanProductionAmounts()

        raw_stats = self.service.getStatistics(raw)
        clean_stats = self.service.getStatistics(clean)

        fig, axes = plt.subplots(1, 2, figsize=(15, 6))

        ax = axes[0]
        ax.hist(raw, bins=8, color="#C44E52", edgecolor="black", alpha=0.85)
        ax.axvline(raw_stats.average, color="black", linestyle="--", linewidth=2,
                   label=f"Media: {raw_stats.average:,.0f} kg")
        ax.axvline(raw_stats.median, color="navy", linestyle="-.", linewidth=2,
                   label=f"Mediana: {raw_stats.median:,.0f} kg")
        ax.set_title("A) Datos crudos — distorsionados por el valor atípico",
                     fontsize=11, fontweight="bold")
        ax.set_xlabel("Producción (kg)")
        ax.set_ylabel("Cantidad de fincas")
        ax.legend(fontsize=9)
        ax.grid(axis="y", alpha=0.3)
        ax = axes[1]
        ax.hist(clean, bins=6, color="#4C72B0", edgecolor="black", alpha=0.85)
        ax.axvline(clean_stats.average, color="black", linestyle="--", linewidth=2,
                   label=f"Media: {clean_stats.average:,.0f} kg")
        ax.axvline(clean_stats.median, color="crimson", linestyle="-.", linewidth=2,
                   label=f"Mediana: {clean_stats.median:,.0f} kg")
        ax.set_title("B) Datos limpios — distribución real del sector",
                     fontsize=11, fontweight="bold")
        ax.set_xlabel("Producción (kg)")
        ax.set_ylabel("Cantidad de fincas")
        ax.legend(fontsize=9)
        ax.grid(axis="y", alpha=0.3)

        fig.suptitle("Distribución de la producción de café — Fincas de Cartago, Valle del Cauca",
                     fontsize=14, fontweight="bold", y=1.02)
        self._save(fig, filename)
        return raw_stats, clean_stats


    def generateRelationGraph(self, filename="02_relacion_altitud_produccion.png"):
        """
        Dispersión: altitud (msnm) vs producción (kg).
        Color y marcador codifican la variedad. Incluye línea de tendencia
        y el coeficiente de correlación de Pearson en el título.
        """
        records = self.service.getCleanProductions()
        x = np.array([p.altitud_msnm for p in records])
        y = np.array([p.produccion_kg for p in records])
        variedades = [p.variedad for p in records]

        fig, ax = plt.subplots(figsize=(12, 7))

        for variedad in self.service.getUniqueVariedades():
            mask = np.array([v == variedad for v in variedades])
            ax.scatter(
                x[mask], y[mask],
                c=self.VARIEDAD_COLORS.get(variedad, "#888888"),
                marker=self.VARIEDAD_MARKERS.get(variedad, "o"),
                s=150, alpha=0.85, edgecolors="black", linewidths=0.8,
                label=f"{variedad} (n={int(mask.sum())})"
            )
        slope, intercept = np.polyfit(x, y, 1)
        line_x = np.linspace(x.min(), x.max(), 100)
        ax.plot(line_x, slope * line_x + intercept, color="gray", linestyle="--",
                linewidth=1.8, label=f"Tendencia: y = {slope:,.1f}x + {intercept:,.0f}")

        corr = self.service.getCorrelationAltitudProduction()

        for p in records:
            ax.annotate(p.finca, (p.altitud_msnm, p.produccion_kg),
                        textcoords="offset points", xytext=(9, 6),
                        fontsize=8, alpha=0.75)

        ax.set_xlabel("Altitud (m s. n. m.)", fontsize=12)
        ax.set_ylabel("Producción (kg)", fontsize=12)
        ax.set_title(f"Relación entre altitud y producción de café\n"
                     f"Correlación de Pearson r = {corr:.3f} "
                     f"({'negativa fuerte' if corr < -0.7 else 'débil'})",
                     fontsize=13, fontweight="bold")
        ax.legend(title="Variedad", fontsize=9, title_fontsize=10, loc="upper right")
        ax.grid(alpha=0.3)

        self._save(fig, filename)
        return corr, slope


    def generateHectaresRelationGraph(self, filename="03_relacion_hectareas_produccion.png"):
        """
        Dispersión: hectáreas vs producción.
        Revela que el área cultivada explica casi toda la variación en producción.
        """
        records = self.service.getCleanProductions()
        x = np.array([p.hectareas for p in records])
        y = np.array([p.produccion_kg for p in records])
        variedades = [p.variedad for p in records]

        fig, ax = plt.subplots(figsize=(12, 7))

        for variedad in self.service.getUniqueVariedades():
            mask = np.array([v == variedad for v in variedades])
            ax.scatter(x[mask], y[mask],
                       c=self.VARIEDAD_COLORS.get(variedad, "#888888"),
                       marker=self.VARIEDAD_MARKERS.get(variedad, "o"),
                       s=150, alpha=0.85, edgecolors="black", linewidths=0.8,
                       label=f"{variedad} (n={int(mask.sum())})")

        slope, intercept = np.polyfit(x, y, 1)
        line_x = np.linspace(x.min(), x.max(), 100)
        ax.plot(line_x, slope * line_x + intercept, color="black", linestyle="--",
                linewidth=1.8, label=f"Tendencia: y = {slope:,.0f}x + {intercept:,.0f}")

        corr = self.service.getCorrelationHectaresProduction()

        for p in records:
            ax.annotate(p.finca, (p.hectareas, p.produccion_kg),
                        textcoords="offset points", xytext=(9, 6),
                        fontsize=8, alpha=0.75)

        ax.set_xlabel("Área cultivada (hectáreas)", fontsize=12)
        ax.set_ylabel("Producción (kg)", fontsize=12)
        ax.set_title(f"Relación entre área cultivada y producción\n"
                     f"Correlación de Pearson r = {corr:.3f} (lineal casi perfecta)",
                     fontsize=13, fontweight="bold")
        ax.legend(title="Variedad", fontsize=9, title_fontsize=10, loc="upper left")
        ax.grid(alpha=0.3)

        self._save(fig, filename)
        return corr, slope


    def generateYieldGraph(self, filename="04_rendimiento_por_hectarea.png"):
        """
        Barras horizontales con kg/hectárea por finca.
        Normaliza el tamaño del terreno: aquí se ve la eficiencia real.
        """
        records = self.service.getCleanProductions()
        yields = np.array([p.getProductionPerformanceByHectares() for p in records])
        order = np.argsort(yields)                 # de menor a mayor
        records = [records[i] for i in order]
        yields = yields[order]

        colors = [self.VARIEDAD_COLORS.get(p.variedad, "#888888") for p in records]
        labels = [f"{p.finca} ({p.variedad[:3]})" for p in records]

        fig, ax = plt.subplots(figsize=(12, 7))
        bars = ax.barh(labels, yields, color=colors, edgecolor="black", alpha=0.85)

        mean_yield = np.mean(yields)
        ax.axvline(mean_yield, color="black", linestyle="--", linewidth=2,
                   label=f"Rendimiento promedio: {mean_yield:,.0f} kg/ha")

        for bar, value in zip(bars, yields):
            ax.text(value + 5, bar.get_y() + bar.get_height() / 2,
                    f"{value:,.0f}", va="center", fontsize=9)

        ax.set_xlabel("Rendimiento (kg por hectárea)", fontsize=12)
        ax.set_title("Eficiencia productiva por finca — Rendimiento normalizado por área",
                     fontsize=13, fontweight="bold")
        ax.legend(fontsize=10)
        ax.grid(axis="x", alpha=0.3)

        self._save(fig, filename)
        return mean_yield


    def generateBoxplotByVariedad(self, filename="05_boxplot_por_variedad.png"):
        """
        Boxplot de producción agrupado por variedad de café.
        """
        variedades = self.service.getUniqueVariedades()
        data = [self.service.getCleanProductionAmountsByVariedad(v) for v in variedades]

        fig, ax = plt.subplots(figsize=(10, 6))
       
        bp = ax.boxplot(data, patch_artist=True, widths=0.5)

        
        ax.set_xticklabels(variedades)

        for patch, variedad in zip(bp["boxes"], variedades):
            patch.set_facecolor(self.VARIEDAD_COLORS.get(variedad, "#888888"))
            patch.set_alpha(0.75)

        for i, valores in enumerate(data, start=1):
            x_jitter = np.random.normal(i, 0.04, size=len(valores))
            ax.scatter(x_jitter, valores, color="black", s=45, zorder=3, alpha=0.8)
            ax.text(i, ax.get_ylim()[1] * 0.98, f"n={len(valores)}",
                    ha="center", va="top", fontsize=9, fontweight="bold")

        ax.set_ylabel("Producción (kg)", fontsize=12)
        ax.set_xlabel("Variedad de café", fontsize=12)
        ax.set_title("Distribución de la producción según la variedad de café",
                    fontsize=13, fontweight="bold")
        ax.grid(axis="y", alpha=0.3)

        self._save(fig, filename)

    def generateAll(self):
        print("\n Generando gráficos del EDA...\n")
        self.generateAmountDistributionGraph()
        self.generateRelationGraph()
        self.generateHectaresRelationGraph()
        self.generateYieldGraph()
        self.generateBoxplotByVariedad()
        print(f"\n Todos los gráficos están en /{self.CHARTS_DIR}\n")