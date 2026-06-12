# Guia de parametros para estimar Watts en el panel solar

Este documento explica que valores se deben usar para que la estimacion de
potencia en Watts tenga sentido dentro del simulador.

## 1. Formula usada

El sistema usa una version simple del modelo PVWatts DC:

```text
P_dc = (G / 1000) * Pdc0 * (1 + gamma_pdc * (T_cell - 25))
```

Donde:

```text
P_dc      = potencia DC estimada en Watts
G         = irradiancia solar en W/m²
Pdc0      = potencia nominal del panel en Watts
gamma_pdc = coeficiente termico de potencia
T_cell    = temperatura del panel o del pixel
25        = temperatura de referencia STC en °C
```

Importante:

```text
La imagen no dice por si sola cuantos Watts tiene el panel.
El dato clave lo debe dar el usuario con Pdc0.
```

## 2. Pdc0 - Potencia nominal del panel

`Pdc0` es la potencia maxima nominal del panel bajo condiciones estandar STC.
Normalmente aparece en la etiqueta o ficha tecnica como:

```text
Pmax
Maximum Power
Rated Power
Nominal Power
```

Ejemplos:

```text
Pmax = 100 W
Pmax = 450 W
Maximum Power = 550 W
```

Rangos comunes:

| Tipo de panel real | Rango aproximado de Pdc0 |
|---|---:|
| Panel pequeno portatil | 10 - 100 W |
| Panel residencial antiguo | 150 - 330 W |
| Panel residencial moderno | 400 - 600 W |
| Panel grande/comercial | 550 - 700 W |

Regla practica:

```text
Si comparas un panel pequeno con uno grande, NO uses el mismo Pdc0.
```

Ejemplo:

```text
Panel pequeno real  -> Pdc0 = 50 W
Panel grande real   -> Pdc0 = 550 W
```

Si ambos se dejan con:

```text
Pdc0 = 450 W
```

el programa interpreta que ambos paneles son de 450 W, aunque en la imagen uno
se vea mas pequeno.

## 3. G - Irradiancia solar

`G` representa cuanta energia solar llega al panel por metro cuadrado.

Unidad:

```text
W/m²
```

Rangos tipicos:

| Condicion | Irradiancia aproximada |
|---|---:|
| Noche o sombra fuerte | 0 - 100 W/m² |
| Dia nublado | 100 - 400 W/m² |
| Sol moderado | 400 - 800 W/m² |
| Sol fuerte / STC | 800 - 1000 W/m² |
| Valor puntual muy alto | 1000 - 1200 W/m² |

Valor recomendado si no se tiene una medicion real:

```text
G = 1000 W/m²
```

Ese es el valor de referencia usado en condiciones STC.

## 4. gamma_pdc - Coeficiente termico de potencia

`gamma_pdc` indica cuanto cambia la potencia cuando cambia la temperatura del
panel.

En paneles solares normalmente es negativo, porque al subir la temperatura baja
la potencia.

Ejemplo de ficha tecnica:

```text
Temperature Coefficient of Pmax = -0.35 %/°C
```

Para usarlo en la formula se convierte a decimal:

```text
-0.35 %/°C = -0.0035 1/°C
```

Rangos tipicos:

| Tipo de panel | gamma_pdc aproximado |
|---|---:|
| Monocristalino | -0.0030 a -0.0040 1/°C |
| Policristalino | -0.0035 a -0.0045 1/°C |
| Pelicula delgada | -0.0015 a -0.0030 1/°C |

Presets usados en el programa:

```text
Monocristalino   -> gamma_pdc = -0.0035
Policristalino   -> gamma_pdc = -0.0040
Pelicula delgada -> gamma_pdc = -0.0025
```

## 5. Temperatura del panel

La temperatura usada en la formula no es necesariamente la temperatura ambiente.
Es la temperatura estimada del panel o de cada pixel del panel.

Rangos comunes:

| Estado aproximado | Temperatura |
|---|---:|
| Ambiente fresco / panel frio | 20 - 35 °C |
| Panel trabajando normal | 35 - 60 °C |
| Panel caliente | 60 - 75 °C |
| Panel muy caliente | 75 - 90 °C |

Efecto sobre la potencia:

```text
Si T_cell > 25 °C, la potencia baja.
Si T_cell = 25 °C, la potencia queda cerca de Pdc0.
Si T_cell < 25 °C, la potencia puede subir ligeramente.
```

Ejemplo con:

```text
Pdc0 = 450 W
G = 1000 W/m²
gamma_pdc = -0.0035
```

Panel a 65 °C:

```text
P_dc = 450 * (1 + (-0.0035) * (65 - 25))
P_dc = 450 * 0.86
P_dc = 387 W aprox.
```

Panel a 35 °C:

```text
P_dc = 450 * (1 + (-0.0035) * (35 - 25))
P_dc = 450 * 0.965
P_dc = 434 W aprox.
```

Por eso un panel mas pequeno en la imagen puede mostrar mas Watts si:

```text
1. Tiene el mismo Pdc0 configurado.
2. Su temperatura media es menor.
```

## 6. T_min y T_max del mapeo termico

`T_min` y `T_max` son los valores usados para convertir pixeles grises a
temperaturas.

Formula:

```text
T = T_min + pixel_normalizado * (T_max - T_min)
```

Valores recomendados:

| Caso | T_min | T_max |
|---|---:|---:|
| Simulacion realista normal | 25 °C | 75 °C |
| Simulacion amplia | 20 °C | 100 °C |
| Panel muy caliente | 25 °C | 90 °C |

Recomendacion general:

```text
T_min = 25 °C
T_max = 75 °C
```

Si la imagen representa condiciones extremas:

```text
T_min = 20 °C
T_max = 100 °C
```

## 7. Como comparar dos imagenes correctamente

Para comparar un panel grande y uno pequeno:

```text
1. Recortar la imagen para que solo salga el panel.
2. Usar el Pdc0 real de cada panel.
3. Usar la misma irradiancia G si las condiciones de sol son iguales.
4. Usar el tipo de panel correcto.
5. Revisar T_media antes de interpretar P_total.
```

Ejemplo justo:

```text
Panel pequeno:
Pdc0 = 50 W
G = 1000 W/m²
Tipo = Monocristalino
T_min = 25 °C
T_max = 75 °C

Panel grande:
Pdc0 = 550 W
G = 1000 W/m²
Tipo = Monocristalino
T_min = 25 °C
T_max = 75 °C
```

Ejemplo no justo:

```text
Panel pequeno:
Pdc0 = 450 W

Panel grande:
Pdc0 = 450 W
```

En ese caso el programa asume que ambos tienen la misma potencia nominal.

## 8. Valores recomendados si no se conoce la ficha tecnica

Para una prueba general:

```text
Tipo de panel = Monocristalino
Pdc0 = 450 W
G = 1000 W/m²
T_min = 25 °C
T_max = 75 °C
```

Para panel pequeno:

```text
Tipo de panel = Monocristalino
Pdc0 = 50 W
G = 1000 W/m²
T_min = 25 °C
T_max = 75 °C
```

Para panel residencial moderno:

```text
Tipo de panel = Monocristalino
Pdc0 = 450 W
G = 1000 W/m²
T_min = 25 °C
T_max = 75 °C
```

Para panel grande:

```text
Tipo de panel = Monocristalino
Pdc0 = 600 W
G = 1000 W/m²
T_min = 25 °C
T_max = 75 °C
```

## 9. Advertencias importantes

La estimacion de Watts es aproximada.

No reemplaza mediciones reales con:

```text
multimetro
sensor de irradiancia
termografia calibrada
ficha tecnica completa
```

La imagen se usa como aproximacion visual de temperatura. Si la foto incluye
fondo, cielo, piso, marco o sombras externas, esos pixeles pueden afectar el
resultado.

Reglas finales:

```text
Mas grande en la foto no significa automaticamente mas Watts.
Mas Pdc0 real si significa mas capacidad de generar Watts.
Mas temperatura normalmente significa menos Watts.
Mas irradiancia normalmente significa mas Watts.
```
