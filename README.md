# Análisis Exploratorio de Datos (EDA) — Producción de Café en Cartago

**Primer Parcial — Inteligencia Artificial**
**Asignatura:** Inteligencia Artificial
**Fecha:** 14 de septiembre de 2026
**Modalidad:** Individual / en parejas

---

## Contexto

Cartago, Valle del Cauca, enfrenta múltiples desafíos en sectores como agricultura, salud, movilidad, educación, medio ambiente, comercio y gobierno. En este proyecto actuamos como **consultores de IA** para analizar datos reales de la problemática agrícola (producción de café) y generar recomendaciones basadas en evidencia.

El dataset asignado es `grupo_01.csv` y contiene información de **13 fincas cafeteras** de la región.

---

## 1. Configuración del entorno

### Tecnologías utilizadas

- **Python 3.12**
- **Docker** + **Docker Compose** (sobre **WSL** en Windows)
- **NumPy** — análisis estadístico
- **Pandas** — lectura de datos
- **Matplotlib** — visualización
- **Scikit-learn / Jupyter** — utilidades de apoyo

### Requisitos previos

- Docker instalado y funcionando (con WSL 2 habilitado si usas Windows).
- Git para clonar el repositorio.

### Cómo reproducir el entorno

```bash
# 1. Clonar el repositorio
git clone https://github.com/<usuario>/parcial1-ia-grupo01.git
cd parcial1-ia-grupo01

# 2. Construir y levantar el contenedor
docker compose up -d --build

# 3. Entrar al contenedor
docker compose exec app bash

# 4. Ejecutar el análisis (desde el directorio src/)
cd src
python analisis.py
```

> Nota: `docker-compose.yml` monta el directorio local en `/app`, por lo que los cambios hechos en el código se reflejan en caliente sin reconstruir la imagen.

### Estructura del repositorio

```
parcial1-ia-grupo01/
├── Dockerfile                 # Imagen Python 3.12 + dependencias
├── docker-compose.yml         # Orquestación del contenedor
├── requirements.txt           # Dependencias de Python
├── README.md                  # Esta documentación
└── src/
    ├── analisis.py            # Script principal del EDA
    ├── data/
    │   └── grupo_01.csv       # Dataset asignado
    ├── charts/                # Gráficos PNG generados
    │   ├── 01_distribucion_produccion.png
    │   ├── 02_relacion_altitud_produccion.png
    │   ├── 03_relacion_hectareas_produccion.png
    │   ├── 04_rendimiento_por_hectarea.png
    │   └── 05_boxplot_por_variedad.png
    ├── entities/              # Modelo de dominio Production
    ├── app_collections/       # Colección de registros
    ├── enums/                 # Constantes de columnas
    ├── dto/                   # Objetos de transferencia de datos
    ├── gateways/              # Lectura del CSV (Gateway)
    └── services/              # Lógica de estadística y gráficos
```

---

## 2. Carga de datos

El script `analisis.py` carga el archivo `grupo_01.csv` mediante la clase `Gateway`, que usa `csv.DictReader` y construye objetos `Production`.

**Primeras 5 filas:**

| # | Finca | Hectáreas | Producción (kg) | Altitud (msnm) | Variedad |
|---|-------|-----------|-----------------|----------------|----------|
| 1 | La Esperanza | 5 | 3,200 | 1650 | Castillo |
| 2 | El Paraíso | 3 | 2,100 | 1720 | Caturra |
| 3 | La Montaña | 8 | 51,000 | 1580 | Castillo |
| 4 | Buenos Aires | 4 | 2,800 | 1690 | Colombia |
| 5 | El Roble | 6 | *(faltante)* | 1610 | Caturra |

**Total de registros leídos: 13**

---

## 3. Calidad de datos

Se identificaron **4 problemas de calidad**. Para cada uno se indica cómo se detectó, qué decisión se tomó y por qué.

### 3.1 Dato faltante — "El Roble"

- **Cómo se detectó:** Al cargar el CSV, la celda de `produccion_kg` de la finca *El Roble* está vacía. El script lo representa como `None`/`NaN` y lo lista en la sección de calidad.
- **Decisión:** Se excluye del análisis estadístico (queda como `NaN`, y NumPy lo ignora al calcular).
- **Por qué:** No podemos inventar una producción; imputar un valor fabricado distorsionaría la distribución. Es mejor analizar con los 12 registros válidos y documentar la ausencia.

### 3.2 Valor atípico (outlier) — "La Montaña" (51,000 kg)

- **Cómo se detectó:** Mediante **Puntaje Z**. El valor de 51,000 kg tiene un `z = +3.30`, muy por encima del umbral de `|z| > 3`. Además, su rendimiento de 6,375 kg/ha es más de 10 veces el promedio del resto (600–700 kg/ha).
- **Decisión:** Se marca como atípico y se separa. El análisis se hace sobre los datos limpios (sin este registro), pero se conserva para mostrar el impacto.
- **Por qué:** Un único valor extremo secuestra la media. Si no se corrige, la media pasa de 3,045 kg a 7,041 kg (más del doble), llevando a conclusiones erróneas sobre el sector.

### 3.3 Finca duplicada — "La Esperanza"

- **Cómo se detectó:** La finca *La Esperanza* aparece **dos veces** (con 5 ha / 3,200 kg y con 4 ha / 2,500 kg). El script detecta nombres de finca repetidos.
- **Decisión:** Se documenta como duplicado y se **conserva** en el análisis, tratándolo como dos registros distintos.
- **Por qué:** No hay forma segura de saber cuál registro es el correcto ni si son dos fincas homónimas o un error de digitación. Eliminar uno arbitrariamente podría descartar datos válidos. Se mantiene y se anota la limitación.

### 3.4 Pregunta clave — valor sospechoso

**Sí.** El valor más sospechoso es la producción de **51,000 kg de *La Montaña*** en solo 8 ha (6,375 kg/ha), cuando todas las demás fincas rinden entre 600 y 700 kg/ha. Esto es fisiológicamente improbable y muy probablemente es un error de registro (un dígito extra, o confusión de unidades). **Si no se corrige**, multiplica por 2.4 el promedio regional y haría creer que la producción cafetera de Cartago es mucho mayor de lo real, distorsionando cualquier política pública.

---

## 4. Análisis estadístico (NumPy)

Variable numérica principal: **`produccion_kg`** (producción anual en kilogramos).

| Métrica | Datos crudos (n=12) | Datos limpios (n=11) |
|---------|---------------------|----------------------|
| Suma total | 84,500 kg | 33,500 kg |
| Media | 7,041.67 kg | 3,045.45 kg |
| Mediana | 2,950 kg | 2,800 kg |
| Desv. estándar | 13,305.60 kg | 1,223.53 kg |
| Mínimo | 1,200 kg | 1,200 kg |
| Máximo | 51,000 kg | 5,800 kg |

### Pregunta clave: ¿El promedio es representativo?

**En los datos crudos, NO.** La media (7,041 kg) es **2.4 veces** mayor que la mediana (2,950 kg), y ninguna de las 12 fincas produce cerca del promedio. La desviación estándar (13,305 kg) supera a la propia media, lo cual es imposible en una distribución normal: evidencia clara de que un solo registro (La Montaña, 51,000 kg) distorsiona todo.

**En los datos limpios, SÍ.** La media (3,045 kg) y la mediana (2,800 kg) quedan a solo **8%** de distancia, y la desviación baja a 1,223 kg. Esto indica una distribución razonablemente simétrica y centrada, por lo que el promedio de ~3,045 kg sí describe al sector típico.

---

## 5. Visualización

Se generaron **5 gráficos PNG** en `src/charts/`. Los dos principales se describen a continuación.

### Gráfico 1 — Distribución de la variable principal
`01_distribucion_produccion.png`

Histograma de la producción en dos paneles:
- **Panel A (crudos):** el valor atípico de 51,000 kg estira el eje y separa la media (7,041 kg) de la mediana (2,950 kg).
- **Panel B (limpios):** la distribución real, concentrada entre 1,200 y 5,800 kg, con media y mediana casi coincidentes (~3,000 kg).

**Conclusión:** demuestra visualmente por qué el outlier debe tratarse antes de interpretar cualquier métrica.

### Gráfico 2 — Relación entre dos variables
`02_relacion_altitud_produccion.png`

Dispersión de **altitud vs. producción**, con puntos coloreados por variedad y línea de tendencia. Muestra una correlación de Pearson `r = -0.959` (negativa muy fuerte).

**Conclusión:** a simple vista parece que a mayor altitud hay menor producción. Sin embargo, como se verá en la interpretación profunda, **esto es un artefacto del tamaño de la finca**, no de la altitud en sí.

*(Gráficos adicionales: `03_relacion_hectareas_produccion.png`, `04_rendimiento_por_hectarea.png`, `05_boxplot_por_variedad.png`.)*

---

## 6. Interpretación profunda

### Relaciones y correlación

| Par de variables | Pearson r | Lectura |
|------------------|-----------|---------|
| Altitud ↔ Producción | −0.959 | Negativa muy fuerte (¡engañoso!) |
| Hectáreas ↔ Producción | +0.997 | Lineal casi perfecta |
| Altitud ↔ Rendimiento (kg/ha) | +0.039 | Nula |

### El hallazgo más importante

Parece que a mayor altitud, menor producción (`r = -0.96`). **Pero esto NO es causalidad:** las fincas de mayor altitud en Cartago simplemente son más pequeñas (La Ceiba: 1,750 m y 2 ha; El Bosque: 1,520 m y 9 ha). Al normalizar por área, la correlación altitud ↔ rendimiento colapsa a **0.039**, es decir, desaparece.

La variable que **realmente** explica la producción es el **área cultivada** (`r = 0.997`). El rendimiento por hectárea es notablemente uniforme: entre 600 y 700 kg/ha en las 11 fincas, con un promedio de **~644 kg/ha**.

**Conclusión:** en Cartago la producción de café está limitada por la **tierra disponible**, no por condiciones agroecológicas ni por la variedad.

### Rendimiento por variedad

| Variedad | n | Rendimiento medio (kg/ha) |
|----------|---|---------------------------|
| Colombia | 4 | ~669 |
| Caturra | 3 | ~651 |
| Castillo | 4 | ~639 |

La variedad Colombia lidera con ~5% más rendimiento que Castillo, pero con n=3-4 por grupo esa diferencia **no es estadísticamente significativa**.

---

## 7. Recomendación al gobierno local

Recomendamos priorizar **programas de asistencia técnica y mejora de la productividad por hectárea**, en lugar de ampliar la frontera agrícola. Justificación con 3 números del dataset:

1. El rendimiento promedio es de **644 kg/ha** y el rango completo va apenas de **600 a 700 kg/ha**. Ninguna finca destaca por eficiencia: todas están en el mismo techo productivo. Un programa que suba el promedio de 644 a 800 kg/ha (**+24%**) incrementaría la producción regional mucho más que sembrar nuevas áreas.
2. La correlación hectáreas ↔ producción es de **0.997**, lo que prueba que el sector crece por **extensión** y no por productividad. Esto es riesgoso ambientalmente (presión sobre suelo y agua en zona de ladera entre 1,520 y 1,750 msnm).
3. El registro de La Montaña (51,000 kg) tiene un **Puntaje Z de +3.30**. Antes de diseñar cualquier política pública, la alcaldía debe **auditar sus sistemas de registro**: un solo dato erróneo multiplicó por **2.4** el promedio regional y habría llevado a conclusiones totalmente equivocadas.

---

## 8. Limitaciones

- **Muestra pequeña:** n=13 fincas (11 utilizables). Insuficiente para generalizar a todo Cartago.
- **Pocas observaciones por variedad:** 3-4 por grupo, no permite prueba de hipótesis robusta entre variedades.
- **Corte transversal:** no hay serie temporal, imposible detectar estacionalidad o tendencias.
- **Duplicado sin resolver:** la finca "La Esperanza" aparece dos veces y no se pudo determinar cuál registro es el correcto.

### Datos adicionales necesarios

- Precio de venta por kg.
- Costos de insumos (fertilizantes, mano de obra).
- Antigüedad del cafetal y densidad de siembra (árboles/ha).
- Precipitación y temperatura por finca.
- Número de trabajadores.
- Certificaciones (orgánico, comercio justo).

---

## Entrega

Repositorio público en GitHub: `parcial1-ia-grupo01`

Contenido entregable:
- [x] `Dockerfile`
- [x] `docker-compose.yml`
- [x] `requirements.txt`
- [x] `analisis.py`
- [x] `grupo_01.csv`
- [x] Gráficos PNG (5)
- [x] `README.md` (esta documentación)