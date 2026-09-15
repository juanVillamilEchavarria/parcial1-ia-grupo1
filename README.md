Estadísticas de la variable principal (produccion_kg)
Métrica
Datos crudos (n=12)
Datos limpios (n=11)
Suma total
84.500 kg
33.500 kg
Media
7.041,67 kg
3.045,45 kg
Mediana
2.950,00 kg
2.800,00 kg
Desv. estándar
13.305,60 kg
1.223,53 kg
Mínimo
1.200 kg
1.200 kg
Máximo
51.000 kg
5.800 kg
¿El promedio es representativo? ❌ No. En los datos crudos la media (7.041 kg) es 2,4 veces mayor que la mediana (2.950 kg) y ninguna de las 12 fincas tiene una producción cercana al promedio. La desviación estándar (13.305 kg) es casi el doble de la media, lo cual es matemáticamente imposible en una distribución normal. Un único registro (La Montaña, 51.000 kg) está secuestrando la estadística. Tras limpiarlo, la media (3.045 kg) y la mediana (2.800 kg) quedan a solo 8% de distancia y la desviación baja a 1.223 kg → ahora sí es representativa.
Correlaciones
Par de variables
Pearson r
Lectura
Altitud ↔ Producción
−0,959
Negativa muy fuerte (¡engañoso!)
Hectáreas ↔ Producción
+0,997
Lineal casi perfecta
Altitud ↔ Rendimiento (kg/ha)
+0,039
Nula
El hallazgo más importante 🎯
A simple vista parece que a mayor altitud, menor producción (r = −0,96). Pero esto no es causalidad: las fincas de mayor altitud en Cartago son simplemente más pequeñas (La Ceiba: 1.750 m y 2 ha; El Bosque: 1.520 m y 9 ha). Al normalizar por área, la correlación altitud↔rendimiento colapsa a 0,039, es decir, desaparece.
La variable que realmente explica la producción es el área cultivada (r = 0,997). El rendimiento por hectárea es notablemente uniforme: entre 600 y 700 kg/ha en las 11 fincas, con un promedio de 644 kg/ha.
Conclusión: en Cartago la producción de café está limitada por tierra disponible, no por condiciones agroecológicas ni por variedad.
Rendimiento por variedad
Variedad
n
Rendimiento medio (kg/ha)
Colombia
4
669
Caturra
3
651
Castillo
4
639
La variedad Colombia lidera con ~5% más rendimiento que Castillo, pero con n=3-4 por grupo esa diferencia no es estadísticamente significativa.
Recomendación al gobierno local (Tarea 7)
Justificada con 3 números del dataset:
El rendimiento promedio es de 644 kg/ha y el rango completo va apenas de 600 a 700 kg/ha. Ninguna finca destaca por eficiencia: todas están en el mismo techo productivo. Un programa de asistencia técnica que suba el promedio de 644 a 800 kg/ha (+24%) incrementaría la producción regional mucho más que ampliar la frontera agrícola.
La correlación hectáreas↔producción es de 0,997, lo que prueba que el sector crece por extensión y no por productividad. Esto es riesgoso ambientalmente (presión sobre suelo y agua en zona de ladera entre 1.520 y 1.750 msnm).
El registro de La Montaña (51.000 kg) tiene un Puntaje Z de +3,30, muy por encima del umbral de 3. Antes de diseñar cualquier política pública, la alcaldía debe auditar sus sistemas de registro: un solo dato erróneo multiplicó por 2,4 el promedio regional y habría llevado a conclusiones totalmente equivocadas.
Limitaciones (Tarea 8)
Muestra de n=13 fincas (11 utilizables). Insuficiente para generalizar a todo Cartago.
3-4 observaciones por variedad: no permite prueba de hipótesis entre variedades.
Corte transversal: no hay serie temporal, imposible detectar estacionalidad o tendencias.
Datos adicionales necesarios: precio de venta por kg, costos de insumos, antigüedad del cafetal, densidad de siembra (árboles/ha), precipitación y temperatura por finca, número de trabajadores, y certificaciones (orgánico, comercio justo).


ejecutar docker compose up -d --build y luego dentro del contenedor (docker compose exec app bash) ejecutar en src python analisis.py