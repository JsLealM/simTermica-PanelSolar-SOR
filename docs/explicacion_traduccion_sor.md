# Explicacion del flujo: imagen -> temperatura -> SOR -> mapa de calor

Este documento explica que hace el programa desde que se carga una imagen hasta
que se muestra el mapa de calor en matplotlib.

## 1. Idea general

El programa no conoce fisicamente el panel solar. Lo que recibe es una imagen.
Para poder hacer calculos numericos, la imagen se convierte en una matriz de
numeros.

El flujo completo es:

```text
Imagen PNG/JPG/BMP
    ↓
Escala de grises
    ↓
Matriz de pixeles 0-255
    ↓
Matriz normalizada 0.0-1.0
    ↓
Matriz de temperaturas en grados Celsius
    ↓
Metodo SOR
    ↓
Mapa de calor con matplotlib
```

## 2. Conversion a escala de grises

Una imagen a color tiene varios canales, normalmente rojo, verde y azul. Para
este proyecto se usa solo escala de grises, porque asi cada pixel queda
representado por un unico numero:

```text
0   = negro
255 = blanco
```

Valores intermedios representan tonos de gris.

La interpretacion usada por el proyecto es:

```text
Pixel oscuro -> menor temperatura
Pixel claro  -> mayor temperatura
```

## 3. Normalizacion del pixel

Antes de convertir a temperatura, cada pixel se divide entre 255:

```text
pixel_normalizado = pixel / 255
```

Asi:

```text
0   / 255 = 0.00
128 / 255 = 0.50 aprox.
255 / 255 = 1.00
```

## 4. Conversion de pixel a temperatura

La formula usada es:

```text
T = T_min + pixel_normalizado * (T_max - T_min)
```

Donde:

```text
T        = temperatura asignada al pixel
T_min    = temperatura minima definida por el usuario
T_max    = temperatura maxima definida por el usuario
```

Ejemplo con:

```text
T_min = 20 °C
T_max = 100 °C
```

Entonces:

```text
pixel = 0   -> T = 20 + 0.00 * 80 = 20 °C
pixel = 128 -> T = 20 + 0.50 * 80 = 60 °C aprox.
pixel = 255 -> T = 20 + 1.00 * 80 = 100 °C
```

En este punto, la imagen ya fue traducida a una matriz de temperaturas.

## 5. Filtro laplaciano discreto

La parte de "arriba, abajo, izquierda y derecha" viene del filtro laplaciano
discreto en 2D. Tambien se conoce como stencil de 5 puntos.

Para un punto interior `(i,j)` se toman estos valores:

```text
              T_arriba

T_izquierda   T_ij       T_derecha

              T_abajo
```

El laplaciano discreto clasico se escribe como:

```text
T_arriba + T_abajo + T_izquierda + T_derecha - 4T_ij
```

Ese operador mide como cambia un punto respecto a sus vecinos. En terminos
termicos, sirve para modelar la difusion o distribucion del calor entre celdas
cercanas.

En este proyecto se usa una forma con parametro `λ`:

```text
(1 + 4λ)T_ij - λ(T_arriba + T_abajo + T_izquierda + T_derecha) = T_pixel
```

Donde:

```text
T_ij      = temperatura final que se quiere calcular en la posicion (i,j)
T_pixel   = temperatura original obtenida desde el pixel de la imagen
λ         = parametro del filtro laplaciano
```

Esta ecuacion es el sistema lineal que se resuelve con SOR. Es decir:

```text
Filtro laplaciano discreto
    ↓
Sistema lineal Ax = b
    ↓
Metodo SOR para resolverlo
```

## 6. Para que se aplica SOR

Si solo se hiciera la conversion anterior, el resultado seria una traduccion
directa:

```text
gris claro -> temperatura alta
gris oscuro -> temperatura baja
```

Eso sirve para visualizar, pero no simula la conduccion de calor. En un panel
real, una zona caliente afecta a sus zonas cercanas. El calor se distribuye.

Por eso se usa SOR: para resolver el sistema generado por el filtro laplaciano
discreto y ajustar la temperatura de cada punto usando sus vecinos.

Cada punto interior mira:

```text
arriba
abajo
izquierda
derecha
valor original del pixel
```

La ecuacion del filtro laplaciano usada en el programa es:

```text
(1 + 4λ)T_ij - λ(T_arriba + T_abajo + T_izquierda + T_derecha) = T_pixel
```

Para poder actualizar el valor de `T_ij`, primero se despeja la ecuacion:

```text
T_ij = (T_pixel + λ(T_arriba + T_abajo + T_izquierda + T_derecha)) / (1 + 4λ)
```

Ese valor despejado se llama aqui `T_gs`, porque es el valor tipo
Gauss-Seidel:

```text
T_gs = (T_pixel + λ(T_arriba + T_abajo + T_izquierda + T_derecha)) / (1 + 4λ)
```

Luego se aplica la relajacion SOR:

```text
T_nueva = (1 - ω)T_anterior + ωT_gs
```

Donde:

```text
λ = parametro del filtro laplaciano
ω = factor de relajacion SOR
```

Casos de ω:

```text
0 < ω < 1  -> subrelajacion, avance mas lento
ω = 1      -> Gauss-Seidel normal
1 < ω < 2  -> sobrerrelajacion, normalmente converge mas rapido
```

Entonces:

```text
El laplaciano define la relacion entre vecinos.
SOR es el metodo iterativo que resuelve esa relacion.
```

## 7. Prueba de escritorio sencilla

Supongamos una imagen muy pequena de 4x4 pixeles.

> Nota: en el programa real se pide N >= 5, pero 4x4 sirve para entender el
> proceso a mano.

Imagen original en escala de grises:

```text
[  0,  64, 128, 255 ]
[ 32, 128, 200, 240 ]
[ 16, 100, 180, 220 ]
[  0,  50, 150, 255 ]
```

Usamos:

```text
T_min = 20 °C
T_max = 100 °C
λ = 1
ω = 1.5
```

### Paso 1: normalizar pixeles

Cada valor se divide entre 255:

```text
[ 0.00, 0.25, 0.50, 1.00 ]
[ 0.13, 0.50, 0.78, 0.94 ]
[ 0.06, 0.39, 0.71, 0.86 ]
[ 0.00, 0.20, 0.59, 1.00 ]
```

### Paso 2: convertir a temperatura

Formula:

```text
T = 20 + pixel_normalizado * (100 - 20)
T = 20 + pixel_normalizado * 80
```

Matriz de temperaturas iniciales:

```text
[ 20.00, 40.08, 60.16, 100.00 ]
[ 30.04, 60.16, 82.75,  95.29 ]
[ 25.02, 51.37, 76.47,  89.02 ]
[ 20.00, 35.69, 67.06, 100.00 ]
```

### Paso 3: aplicar filtro laplaciano y SOR

Los bordes se dejan fijos. En esta matriz 4x4, los nodos interiores son:

```text
(1,1), (1,2), (2,1), (2,2)
```

Tomemos el nodo `(1,1)`:

```text
T_anterior = 60.16
Tpixel = 60.16

Vecinos:
arriba    = 40.08
abajo     = 51.37
izquierda = 30.04
derecha   = 82.75
```

La ecuacion laplaciana para este nodo es:

```text
(1 + 4λ)T_ij - λ(T_arriba + T_abajo + T_izquierda + T_derecha) = T_pixel
```

Como `λ = 1`, el despeje queda:

```text
T_gs = (Tpixel + vecinos) / 5
T_gs = (60.16 + 40.08 + 51.37 + 30.04 + 82.75) / 5
T_gs = 52.88
```

Ese `T_gs` es el valor que saldria de Gauss-Seidel. Ahora se aplica SOR con
`ω = 1.5`:

```text
T_nueva = (1 - 1.5) * 60.16 + 1.5 * 52.88
T_nueva = -0.5 * 60.16 + 79.32
T_nueva = 49.24 °C
```

Entonces el nodo `(1,1)` pasa aproximadamente de:

```text
60.16 °C -> 49.24 °C
```

Esto no significa que SOR siempre baje la temperatura. En este caso bajo porque
los vecinos eran, en promedio, mas frios que ese punto.

Si un punto frio estuviera rodeado de puntos calientes, SOR podria subir su
temperatura.

### Paso 4: error de la iteracion

El error se calcula como el mayor cambio entre la temperatura anterior y la nueva:

```text
error = max(|T_nueva - T_anterior|)
```

Por ejemplo, si los cambios fueran:

```text
(1,1): 10.92
(1,2): 14.95
(2,1):  7.32
(2,2): 10.77
```

Entonces:

```text
error = 14.95
```

Si:

```text
error < tolerancia
```

el metodo se detiene. Si no, SOR repite otra iteracion.

## 8. Que muestra matplotlib

Matplotlib no calcula la temperatura. Solo dibuja la matriz final.

La matriz final de temperaturas se manda a:

```python
imshow(malla_resultado, cmap="hot", vmin=T_min, vmax=T_max)
```

Eso significa:

```text
temperatura baja  -> color oscuro
temperatura media -> color intermedio
temperatura alta  -> color claro/caliente
```

La barra de color indica la correspondencia entre color y temperatura.

Por eso es correcto mostrar toda la imagen en el mapa de calor: cada posicion
del mapa representa la temperatura calculada para esa zona del panel.

## 9. Resumen corto

```text
1. La imagen se vuelve una matriz de pixeles.
2. Cada pixel se normaliza de 0-255 a 0-1.
3. Cada pixel se convierte a temperatura con T_min y T_max.
4. SOR ajusta esas temperaturas usando los vecinos.
5. Matplotlib pinta la matriz final como mapa de calor.
```

La parte importante es:

```text
La temperatura no sale directamente de matplotlib.
La temperatura sale de la matriz numerica.
Matplotlib solo la visualiza con colores.
```
