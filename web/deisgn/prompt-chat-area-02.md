Rediseña la interfaz web de "Deep Researcher", una aplicación de investigación AI
multi-agente. Layout: sidebar izquierdo (320px) + chat central (~850px) con reporte final.

═══════════════════════════════════════════════════════════════
                    1. SISTEMA DE DISEÑO
═══════════════════════════════════════════════════════════════

## IDENTIDAD VISUAL
- Tema: "Terminal Green" — oscuro, técnico, minimalista
- Inspirado en terminales de código y dashboards DevOps
- Sin decoraciones innecesarias, jerarquía visual por color
- Accent verde como guía de atención, usado con moderación

## PALETA DE COLORES

### Superficies
| Token                | Hex       | Uso                                        |
|----------------------|-----------|--------------------------------------------|
| surface.base         | #0A0A0A   | Background principal (sidebar, chat)       |
| surface.header       | #0D0D0D   | Headers y barras superiores                |
| surface.card-active  | #141414   | Cards activas, inputs, search bar          |
| surface.card-idle    | #0F0F0F   | Cards inactivas en sidebar                 |
| surface.code         | #080808   | Bloques de código JSON / tool output       |
| surface.report-card  | #111111   | Card del Final Report                      |

### Bordes y divisores
| Token                | Hex       | Uso                                        |
|----------------------|-----------|--------------------------------------------|
| border.subtle        | #1A1A1A   | Bordes de inputs, header bottom, badges    |
| border.divider       | #1E1E1E   | Líneas divisorias, bordes de report card   |

### Texto
| Token                | Hex       | Uso                                        |
|----------------------|-----------|--------------------------------------------|
| text.primary         | #FFFFFF   | Títulos principales, headings del report   |
| text.secondary       | #CCCCCC   | Títulos de items, contenido bloques normales |
| text.tertiary        | #DDDDDD   | Nombre usuario, section labels del report  |
| text.muted           | #AAAAAA   | Contenido bloques SYSTEM/CLARIFY, body report |
| text.subtle          | #888888   | Código en tool blocks                      |
| text.placeholder     | #666666   | Placeholders, tabs inactivos               |
| text.dim             | #555555   | Previews, emails, settings icon            |
| text.ghost           | #444444   | Timestamps, botones COPY, chevrons         |

### Accent primario (verde terminal)
| Token                | Hex         | Uso                                      |
|----------------------|-------------|------------------------------------------|
| accent.solid         | #00FF00     | CTA fill, texto activo, dots             |
| accent.tint-15       | #00FF0015   | Bg tab activo, avatar circle             |
| accent.tint-18       | #00FF0018   | Bg badge COMPLETED                       |
| accent.tint-10       | #00FF0010   | Bg botón Collapse all (activo)           |
| accent.border-40     | #00FF0040   | Left border bloques PRO/ASSISTANT, item activo |
| accent.border-30     | #00FF0030   | Left border collapsed PRO/ASSISTANT      |
| accent.border-25     | #00FF0025   | Stroke icon brand, stroke Collapse btn   |
| accent.gradient-top  | #00FF0030   | Gradient top del icon brand              |
| accent.gradient-bot  | #00FF0008   | Gradient bottom del icon brand           |

### Colores de bloques del chat (TODOS ÚNICOS, sin repetir)
| Bloque               | Color principal | Left border (expanded) | Left border (collapsed) | Card bg (expanded) | Card bg (collapsed) |
|----------------------|----------------|----------------------|------------------------|-------------------|-------------------|
| MESSAGE              | #6B8AFF (azul) | #6B8AFF40            | #6B8AFF20              | #0A0D15           | #0A0D15           |
| PRO (user message)   | #00FF00 (verde)| #00FF0040            | #00FF0030              | #0A150A           | #0A150A           |
| CLARIFY WITH USER    | #FF6B6B (rojo) | #FF6B6B40            | #FF6B6B30              | #150A0A           | #150A0A           |
| SYSTEM               | #FFB800 (ámbar)| #FFB80040            | #FFB80030              | #15120A           | #15120A           |
| ASSISTANT            | #00FF00 (verde)| #00FF0040            | #00FF0030              | #0A150A           | #0A150A           |
| RESEARCH BRIEF       | #C084FC (violeta)| #C084FC40          | #C084FC30              | #100A15           | #100A15           |
| TOOL CALL            | #06B6D4 (cyan) | #06B6D440            | #06B6D420              | #0A1215           | #0A1215           |
| TOOL OUTPUT          | #F472B6 (rosa) | #F472B640            | #F472B620              | #150A10           | #150A10           |

### Colores de status del sidebar
| Status     | Dot/Texto  | Badge bg    |
|------------|------------|-------------|
| Completed  | #00FF00    | #00FF0018   |
| Running    | #FFB800    | #FFB80018   |
| Clarify    | #FF6B00    | #FF6B0018   |

## TIPOGRAFÍA

### Font Families
- Body/UI: "Geist" (sans-serif moderna, limpia)
- Técnico/datos: "Geist Mono" (monospace — badges, timestamps, código, block labels)

### Escala tipográfica completa
| Elemento                     | Font        | Size | Weight | Color    | lineHeight |
|------------------------------|-------------|------|--------|----------|------------|
| Report main title            | Geist       | 20px | 700    | #FFFFFF  | 1.3        |
| Report section labels        | Geist       | 15px | 600    | #DDDDDD  | —          |
| Chat header title            | Geist       | 15-16px | 500  | #FFFFFF  | 1.3        |
| Final Report label           | Geist       | 16px | 600    | #FFFFFF  | —          |
| Brand name "Deep Researcher" | Geist       | 15px | 600    | #FFFFFF  | —          |
| CTA "New Research"           | Geist       | 14px | 600    | #000000  | —          |
| Conversation item title      | Geist       | 13px | 500    | #FFFFFF/#CCCCCC | 1.3  |
| Block content text           | Geist       | 13px | normal | #CCCCCC/#AAAAAA | 1.4  |
| Report body text             | Geist       | 13px | normal | #AAAAAA  | 1.5        |
| Bullet list items            | Geist       | 13px | normal | #CCCCCC  | —          |
| Search placeholder           | Geist       | 13px | normal | #666666  | —          |
| User name                    | Geist       | 13px | 500    | #DDDDDD  | —          |
| Collapse/Expand buttons      | Geist       | 12px | normal | #00FF00/#555555 | —   |
| Download .md button          | Geist       | 12px | 600    | #000000  | —          |
| Code in tool blocks          | Geist Mono  | 12px | normal | #888888  | 1.5        |
| Filter tabs                  | Geist Mono  | 12px | 500/normal | #00FF00/#666666 | — |
| Block type labels (UPPERCASE)| Geist Mono  | 11px | 600    | (color del bloque) | — |
| COPY buttons                 | Geist Mono  | 10-11px | normal | #444444 | —         |
| Status badges                | Geist Mono  | 10-11px | 500-600 | (color del status) | — |
| Preview text                 | Geist       | 11px | normal | #555555  | 1.2        |
| User email                   | Geist Mono  | 11px | normal | #555555  | —          |
| Source count                  | Geist Mono  | 11px | normal | #666666  | —          |
| Timestamps                   | Geist Mono  | 10px | normal | #444444  | —          |
| Pill badges (REFERENCES etc) | Geist Mono  | 9px  | 500    | (color del bloque) | — |

## BORDES Y RADIOS
| Elemento                    | cornerRadius |
|-----------------------------|-------------|
| Sidebar / Chat container    | 12px        |
| Report card                 | 10px        |
| Buttons, inputs, msg cards  | 8px         |
| Brand icon container        | 8px         |
| Pill badges (status)        | 10px        |
| Filter tabs                 | 12px (pill) |
| Collapse/Expand buttons     | 6px         |
| Code blocks                 | 6px         |
| Avatar (32x32)              | 16px (circle)|

## ICONOGRAFÍA (Lucide)
| Icono              | Tamaño | Color   | Ubicación                     |
|--------------------|--------|---------|-------------------------------|
| brain-circuit      | 16x16  | #00FF00 | Brand icon (28x28 container con gradient) |
| plus               | 16x16  | #000000 | Botón New Research            |
| search             | 14x14  | #666666 | Search bar                    |
| chevrons-down-up   | 14x14  | #00FF00/#666666 | Collapse all           |
| chevrons-up-down   | 14x14  | #00FF00/#555555 | Expand all             |
| chevron-down       | 14x14  | #444444 | Bloques colapsados            |
| file-text          | 18x18  | #FFFFFF | Final Report header           |
| download           | 14x14  | #000000 | Botón Download .md            |
| link               | 12x12  | #666666 | Source count badge             |
| settings           | 18x18  | #555555 | Footer sidebar                |

═══════════════════════════════════════════════════════════════
                    2. SIDEBAR (320px)
═══════════════════════════════════════════════════════════════

### Contenedor: vertical, bg #0A0A0A, cornerRadius 12, clip true, height 100vh

#### Top Section (padding [24,16,16,16], gap 16)
1. **Brand row** — horizontal, gap 10, alignItems center
   - Icon container: 28x28, cornerRadius 8, gradient (#00FF0030→#00FF0008 linear 180°),
     stroke #00FF0025 1px inside. Dentro: "brain-circuit" 16x16 #00FF00
   - "Deep Researcher" Geist 15px 600 #FFFFFF

2. **New Research** — full width, height 40, cornerRadius 8, fill #00FF00
   - Centered: "plus" 16x16 #000000 + text Geist 14px 600 #000000, gap 8

3. **Search bar** — full width, height 36, cornerRadius 8, fill #141414,
   stroke #1A1A1A 1px inside, padding [0,12], gap 8
   - "search" 14x14 #666666 + "Search conversations..." Geist 13px #666666

4. **Filter tabs** — horizontal, gap 8
   - Activo ("All"): padding [4,10], cornerRadius 12, fill #00FF0015,
     text Geist Mono 12px 500 #00FF00
   - Inactivo: sin fill, Geist Mono 12px normal #666666

#### Conversation List (padding 8, gap 4, clip true, fill_container height)
- **Item activo**: fill #141414, stroke inside left 3px #00FF0040, título #FFFFFF
- **Item inactivo**: fill #0F0F0F, sin stroke, título #CCCCCC
- Cada item: cornerRadius 8, padding 12, gap 4 (vertical)
  - Top row: título (Geist 13px 500, lineHeight 1.3) + badge pill
  - Bottom row: preview (Geist 11px #555555) + timestamp (Geist Mono 10px #444444)
- **Badges**: padding [3,8], cornerRadius 10
  - Running: dot 6x6 #FFB800 + "Running" Geist Mono 10px 500 #FFB800, bg #FFB80018
  - Clarify: dot 6x6 #FF6B00 + "Clarify" Geist Mono 10px 500 #FF6B00, bg #FF6B0018
  - Completed: "Completed" Geist Mono 10px 500 #00FF00, bg #00FF0018

#### Divider — line #1E1E1E 1px

#### Footer (padding [12,16], gap 12, horizontal)
- Avatar: 32x32, cornerRadius 16, fill #00FF0015, "M" Geist 14px 600 #00FF00
- Column: "Maximo" Geist 13px 500 #DDDDDD + email Geist Mono 11px #555555
- "settings" 18x18 #555555

═══════════════════════════════════════════════════════════════
              3. CHAT — VISTA EXPANDIDA
═══════════════════════════════════════════════════════════════

### Header (fill #0D0D0D, padding [16,24], horizontal, space_between)
- Left: título Geist 16px 500 #FFFFFF + "COMPLETED" pill (cornerRadius 10,
  fill #00FF0018, Geist Mono 11px #00FF00, padding [4,10])
- Right: ghost buttons gap 8, cornerRadius 6, padding [6,10]
  - Activo: fill #00FF0010, stroke #00FF0025 1px, icon+text #00FF00
  - Inactivo: sin fill, icon+text #666666 o #555555
  - Collapse: "chevrons-down-up" | Expand: "chevrons-up-down"
- Debajo: rectángulo 1px #1A1A1A

### Message blocks (padding [16,24], gap 2, vertical)
Cada bloque: cornerRadius 8, padding [14,16], gap 10

**Header de bloque** (horizontal, gap 8):
- Dot (ellipse 8x8, color principal del bloque)
- Label (Geist Mono 11px 600, color principal, UPPERCASE)
- Spacer (frame fill_container, height 1)
- [Opcional] Pill "REFERENCES"/"SUBBLOCKS" (cornerRadius 8, fill #1A1A1A,
  Geist Mono 10px, color del bloque, padding [3,8])
- "COPY" (Geist Mono 11px #444444)

**Contenido**:
- Texto: Geist 13px normal, lineHeight 1.4, textGrowth fixed-width
- Código (tool calls): frame cornerRadius 6, fill #080808, padding 12,
  Geist Mono 12px #888888 lineHeight 1.5

**Left border**: stroke inside, thickness {left:3}, opacidad ~40

**Colores por tipo de bloque** (TODOS distintos):
| Bloque               | Color      | Card bg  | Left border |
|----------------------|------------|----------|-------------|
| MESSAGE              | #6B8AFF    | #0A0D15  | #6B8AFF40   |
| PRO                  | #00FF00    | #0A150A  | #00FF0040   |
| CLARIFY WITH USER    | #FF6B6B    | #150A0A  | #FF6B6B40   |
| SYSTEM               | #FFB800    | #15120A  | #FFB80040   |
| ASSISTANT            | #00FF00    | #0A150A  | #00FF0040   |
| RESEARCH BRIEF       | #C084FC    | #100A15  | #C084FC40   |
| TOOL CALL            | #06B6D4    | #0A1215  | #06B6D440   |
| TOOL OUTPUT          | #F472B6    | #150A10  | #F472B640   |

═══════════════════════════════════════════════════════════════
              4. CHAT — VISTA COLAPSADA
═══════════════════════════════════════════════════════════════

### Header idéntico al expandido, con "Collapse all" activo (verde)

### Bloques colapsados (padding [12,24], gap 2)
Cada bloque: cornerRadius 8, padding [10,14], horizontal, gap 10, alignItems center
- Dot 8x8 (color del bloque)
- Label Geist Mono 11px 600 (color del bloque, UPPERCASE)
- Spacer (fill_container)
- [Opcional] "COPY" Geist Mono 10px #444444
- [Opcional] Pill badge (cornerRadius 8, fill #1A1A1A, Geist Mono 9px 500, color del bloque)
- Chevron: "chevron-down" 14x14 #444444

Left border: stroke inside {left:3}, opacidad ~20-30

**Mismos colores que la tabla expandida** pero con bg y border de opacidad reducida:
- Card bg: mismos hex que expandido
- Left border: opacidad 20 en vez de 40

═══════════════════════════════════════════════════════════════
              5. FINAL REPORT
═══════════════════════════════════════════════════════════════

### Divider — line #1E1E1E 1px

### Report Header (horizontal, space_between, padding [16,0,12,0])
- Left: "file-text" 18x18 #FFFFFF + "Final Report" Geist 16px 600 #FFFFFF, gap 10
- Right: gap 8
  - Source badge: cornerRadius 8, stroke #1E1E1E 1px, padding [6,12],
    "link" 12x12 #666666 + "6 sources" Geist Mono 11px #666666
  - Download: cornerRadius 8, fill #00FF00, padding [8,14], gap 6,
    "download" 14x14 #000000 + "Download .md" Geist 12px 600 #000000

### Report Card (cornerRadius 10, fill #111111, stroke #1E1E1E 1px,
               padding [24,28,28,28], gap 16)
- Título: Geist 20px 700 #FFFFFF, lineHeight 1.3
- Sección: Geist 15px 600 #DDDDDD
- Body: Geist 13px normal #AAAAAA, lineHeight 1.5
- Bullets: padding-left 16, gap 6, dot 5x5 #00FF00 + Geist 13px #CCCCCC

═══════════════════════════════════════════════════════════════
              6. PRINCIPIOS DE DISEÑO
═══════════════════════════════════════════════════════════════

1. Densidad media-alta — compacto pero legible
2. Jerarquía por color, no por tamaño
3. Mínima decoración — sin sombras, sin gradientes (excepto icon brand)
4. Geist Mono para datos técnicos, Geist para contenido
5. CADA TIPO DE BLOQUE tiene un color ÚNICO — nunca repetir colores entre bloques
6. Status colors semánticos: bg ~10% opacidad, texto/dots al 100%
7. Bordes sutiles #1A1A1A o #1E1E1E, nunca protagonistas
8. Left border 3px como identificador visual de cada bloque
9. Accent verde solo en: CTA, tab activo, badge completado, avatar, brand
10. Collapsed = dot + label + spacer + [badges] + chevron (una sola línea)
11. Expanded = header + content con tipografía readable
