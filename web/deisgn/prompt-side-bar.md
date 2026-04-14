Aplica el siguiente sistema de diseño a la web app "Deep Researcher". Es un panel de investigación AI con sidebar + área de contenido principal.

## IDENTIDAD VISUAL
- Tema: Dark Terminal Green — oscuro, técnico, minimalista
- Inspiración: terminales de código, dashboards de DevOps, interfaces hacker elegantes

## PALETA DE COLORES

### Superficies
- Background principal: #0A0A0A (casi negro puro)
- Card activa / inputs: #141414 (gris muy oscuro, elevación sutil)
- Card inactiva / hover: #0F0F0F (apenas perceptible sobre el fondo)
- Dividers / bordes sutiles: #1E1E1E
- Bordes de inputs: #1A1A1A (stroke inside, 1px)

### Texto
- Texto principal (títulos, headings): #FFFFFF
- Texto primario (items de lista): #CCCCCC
- Texto secundario (nombres usuario): #DDDDDD
- Texto muted (previews, placeholders): #555555 a #666666
- Texto terciario (timestamps, emails): #444444

### Accent (verde terminal)
- Accent primario: #00FF00 (verde brillante — botones, badges activos, iconos clave)
- Accent sobre fondo oscuro (tint): #00FF0015 (para backgrounds de tabs y badges activos)
- Accent para badges completed: #00FF0018
- Accent para bordes/glow: #00FF0025 a #00FF0040
- Accent gradient (icon brand): linear de #00FF0030 a #00FF0008

### Status Colors
- Running: #FFB800 (ámbar) — badge bg: #FFB80018, dot: #FFB800
- Clarify / Needs Attention: #FF6B00 (naranja) — badge bg: #FF6B0018, dot: #FF6B00
- Completed: #00FF00 (verde) — badge bg: #00FF0018

## TIPOGRAFÍA

### Font Families
- Headings y body: "Geist" (sans-serif moderna, clean)
- Captions, badges, timestamps, código: "Geist Mono" (monospace técnica)

### Escala tipográfica
- Brand name: 15px, weight 600, Geist
- Botón principal: 14px, weight 600, Geist
- Search placeholder: 13px, weight normal, Geist
- Títulos de conversación: 13px, weight 500, Geist, lineHeight 1.3
- Nombre usuario: 13px, weight 500, Geist
- Filter tabs: 12px, weight 500 (activo) / normal (inactivo), Geist Mono
- Preview text: 11px, weight normal, Geist, lineHeight 1.2
- Email usuario: 11px, weight normal, Geist Mono
- Badge status: 10px, weight 500, Geist Mono
- Timestamps: 10px, weight normal, Geist Mono

## BORDES Y RADIOS
- Contenedor sidebar: cornerRadius 12px
- Botones, inputs, cards: cornerRadius 8px
- Badges de status: cornerRadius 10px (pill shape)
- Filter tabs: cornerRadius 12px (pill shape)
- Avatar circular: cornerRadius 16px (en 32x32 = círculo)
- Icon brand container: cornerRadius 8px

## ICONOGRAFÍA
- Familia: Lucide icons
- Brand icon: "brain-circuit" (16x16) dentro de contenedor 28x28 con gradient y borde verde
- Acciones: "plus" (16x16, negro sobre verde), "search" (14x14, #666666)
- Footer: "settings" (18x18, #555555)
- Los status dots son círculos de 6x6 del color del status

## LAYOUT Y SPACING

### Sidebar
- Ancho: 320px, height 100vh
- Layout: vertical, sin gap entre secciones principales
- Clip: true (overflow hidden)

### Top section
- Padding: [24, 16, 16, 16] (más arriba que a los lados)
- Gap entre elementos: 16px
- Gap entre filter tabs: 8px

### Conversation list
- Padding: 8px alrededor
- Gap entre items: 4px
- Cada item: padding 12px, gap interno 4px (vertical)
- Row superior (título + badge): horizontal, gap 8px, space_between
- Row inferior (preview + time): horizontal, gap 6px, space_between

### Footer
- Padding: [12, 16]
- Gap: 12px entre avatar, texto y settings icon
- Separado por línea divisoria (#1E1E1E, 1px)

## ESTADOS DE ITEMS

### Item activo (seleccionado)
- Background: #141414
- Borde izquierdo verde: stroke inside, left 3px, color #00FF0040
- Título: #FFFFFF (blanco puro)

### Item inactivo
- Background: #0F0F0F
- Sin borde especial
- Título: #CCCCCC (gris claro)

### Badges de status
- Contenedor: pill con padding [3, 8], cornerRadius 10
- Contienen un dot (ellipse 6x6) + texto
- Colores según status (ver Status Colors arriba)

## COMPONENTES CLAVE

### Botón "New Research"
- Full width, height 40px, cornerRadius 8px
- Fill: #00FF00 (accent sólido)
- Texto e icono: #000000 (negro sobre verde)
- Icon "plus" a la izquierda, gap 8px
- Centered content (justifyContent center)

### Search bar
- Full width, height 36px, cornerRadius 8px
- Background: #141414
- Border: #1A1A1A, 1px, inside
- Icon search + placeholder text en #666666
- Padding horizontal: 12px, gap 8px

### Avatar usuario
- Círculo 32x32, cornerRadius 16
- Background: #00FF0015 (tint verde)
- Inicial: 14px, Geist, weight 600, #00FF00

## PRINCIPIOS DE DISEÑO
1. Densidad media-alta — información compacta pero legible
2. Jerarquía por color, no por tamaño — el verde guía la atención
3. Mínima decoración — sin sombras, sin gradientes llamativos (excepto el icon brand)
4. Monospace para datos técnicos — timestamps, badges, emails, filtros
5. Sans-serif para contenido — títulos, previews, labels
6. Status colors semánticos con opacidad baja para backgrounds (~10%) y color puro para texto
7. Bordes sutiles, nunca protagonistas
8. El accent verde #00FF00 se usa con moderación: solo en CTA principal, estado activo, y avatar
