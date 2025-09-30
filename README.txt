Dolorímetro 2.0

Resumen
-------
Aplicación de registro y medición de umbral de dolor con algómetro (interfaz Tk + OpenCV). 
Todas las imágenes y recursos (por ejemplo im.png, Fondo.png, icono.ico) deben residir en la carpeta Aplicacion: \SOFT_TIF\Aplicacion.
El ejecutable Dolorimetro.exe debe estar en la carpeta Aplicacion: \SOFT_TIF\Aplicacion.

Requisitos
----------
- Python 3.8+
- Dependencias: numpy, opencv-python, pillow, pandas, openpyxl, pywin32 (winsound/ctypes en Windows)
- Archivo ejecutable / script: [c:\SOFT_TIF\Aplicacion\Aplicacion.py](c:\SOFT_TIF\Aplicacion\Aplicacion.py)


Calibración (resumen técnico)
-----------------------------
- Si no existe calibracion.txt se usa un valor por defecto calculado en el código:
  $$k_{def} = \frac{(73.1\times10^{9})(1.81\times10^{-3})}{8(8.94^{3})\cdot 13 \left(1+\frac{0.5}{8.94^{2}}\right)}$$
  (cálculo implementado en [`Aplicacion.cargar_k`](c:\SOFT_TIF\Aplicacion\Aplicacion.py)).

- Procedimiento de calibración dentro de la GUI:
  1. Colocar el algómetro sobre una balanza.
  2. Aplicar presión hasta que la balanza marque 2 kgf.
  3. Al llegar a 2 kgf, hacer click izquierdo para registrar la medición.
  4. Repetir varias veces y presionar ESC para finalizar.
  (Implementado en [`Aplicacion.abrir_calibracion`](c:\SOFT_TIF\Aplicacion\Aplicacion.py)).

- Cálculo de la constante del resorte tras calibrar:
  - Se toman varias mediciones de desplazamiento (en cm en la GUI), se convierten a metros y se promedia:
    $$\bar{x} = \text{promedio de desplazamientos (m)}$$
  - La fuerza usada es 2 kgf ≈ 2 * 9.81 N.
  - Nueva constante:
    $$k = \frac{F}{\bar{x}}$$
  - El nuevo k se escribe en calibracion.txt (función [`Aplicacion.guardar_k`](c:\SOFT_TIF\Aplicacion\Aplicacion.py)).

PARA REINICIAR LA CALIBRACION BORRAR calibracion.txt EN ESE CASO SE UTILIZARA LA K PROPIA DEL PROGRAMA Y SE DEBERA RECALIBRAR.

Mediciones y formatos de salida
-------------------------------
- Durante la medición se registran lecturas en pantalla (función de evento: [`Aplicacion.process_mouse_event`](c:\SOFT_TIF\Aplicacion\Aplicacion.py)).
- Las mediciones se guardan en:
  - Un .txt por voluntario en C:\SOFT_TIF\Medidas
  - Un Excel consolidado C:\SOFT_TIF\Medidas\mediciones_voluntarios.xlsx (pandas + openpyxl)

Notas operativas y buenas prácticas
----------------------------------
- Asegurar que los archivos de imagen (im.png, Fondo.png, icono.ico) están en C:\SOFT_TIF\Aplicacion antes de ejecutar.
- Si mueves la carpeta SOFT_TIF, no hace falta cambiar rutas internas: el script usa la carpeta del ejecutable (`BASE_DIR`) para localizar recursos.
- Si la calibración falla o no hay mediciones, se conserva el valor previo en calibracion.txt.


