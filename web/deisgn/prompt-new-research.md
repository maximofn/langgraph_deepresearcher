Modal "New Research" — Especificación de Diseño
Tema General
Tema Terminal Green oscuro, coherente con el resto de la aplicación Deep Researcher.

Backdrop (Overlay)
type: frame
layout: none (modal posicionado absolutamente dentro)
fill: #000000CC (negro 80% opacidad)
Cubre toda la pantalla
Modal Card (Contenedor)
type: frame
layout: vertical
width: 520px
height: fit_content
fill: #111111
stroke: inside, 1px, #1A1A1A
cornerRadius: 16
padding: [28, 32] (28px vertical, 32px horizontal)
gap: 24
Centrado en el backdrop
Sección 1: Header
layout: horizontal
width: fill_container
justifyContent: space_between
alignItems: center
Contenido:
Título "New Research": Geist, 20px, weight 600, fill #FFFFFF
Botón cerrar (X): icono lucide "x", 18x18, fill #666666
Sección 2: Campo de Query
Frame vertical, fill_container, gap 8:

Label "QUERY": Geist Mono, 11px, weight 500, fill #888888, letterSpacing 1
Input row (frame horizontal):
width: fill_container
height: 48
fill: #0A0A0A
stroke: inside, 1px, #222222
cornerRadius: 10
padding: [0, 16]
alignItems: center
gap: 12
Contenido:
Placeholder text: "What do you want to research?", Geist, 14px, weight 400, fill #555555, width fill_container
Botón enviar: frame 32x32, cornerRadius 8, fill #00FF00, centrado, contiene icono lucide "arrow-up" 16x16 fill #0A0A0A
Sección 3: Sliders
Frame vertical, fill_container, gap 20. Cada slider tiene:

Slider "Max iterations"
Header row (horizontal, fill_container, space_between, center):
Label: "Max iterations", Geist, 13px, weight 500, fill #CCCCCC
Valor: "6", Geist Mono, 13px, weight 600, fill #00FF00
Track (frame, layout none, fill_container, height 6, fill #1A1A1A, cornerRadius 3):
Fill bar: rectangle, width 274px (≈60% del track), height 6, fill #00FF00, cornerRadius 3
Thumb: ellipse, 16x16, fill #FFFFFF, posicionado al final del fill bar (x: 266, y: -5), shadow blur 4 color #00000066
Slider "Max concurrent researchers"
Header row (idéntico al anterior):
Label: "Max concurrent researchers", Geist, 13px, weight 500, fill #CCCCCC
Valor: "3", Geist Mono, 13px, weight 600, fill #00FF00
Track (idéntico, pero fill bar width 137px ≈30% del track, thumb en x: 129)
Sección 4: Botones de Acción
Divider: rectangle, fill_container, height 1, fill #1A1A1A
Button row (horizontal, fill_container, justifyContent end, gap 12):
Cancel: frame, fit_content, padding [10, 20], cornerRadius 10, sin fill, stroke inside 1px #333333, texto "Cancel" Geist 14px weight 500 fill #AAAAAA
Start Research: frame, fit_content, padding [10, 24], cornerRadius 10, fill #00FF00, gap 8, contenido:
Icono lucide "sparkles" 16x16 fill #0A0A0A
Texto "Start Research" Geist 14px weight 600 fill #0A0A0A
Paleta de Colores Resumen
Uso	Color
Backdrop overlay	#000000CC
Modal fondo	#111111
Modal borde	#1A1A1A
Input fondo	#0A0A0A
Input borde	#222222
Accent (botones, sliders, valores)	#00FF00
Texto sobre accent	#0A0A0A
Título	#FFFFFF
Labels	#CCCCCC
Labels técnicos	#888888
Placeholder	#555555
Ícono cerrar	#666666
Borde Cancel	#333333
Texto Cancel	#AAAAAA
Divider/Track	#1A1A1A
Thumb slider	#FFFFFF
Tipografía
Elemento	Font	Size	Weight
Título modal	Geist	20px	600
Input placeholder	Geist	14px	400
Labels slider	Geist	13px	500
Botones texto	Geist	14px	500-600
Label "QUERY"	Geist Mono	11px	500
Valores slider	Geist Mono	13px	600