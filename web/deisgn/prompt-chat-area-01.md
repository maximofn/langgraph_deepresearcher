Rediseña la interfaz web de "Deep Researcher", una aplicación de investigación AI con
multi-agente. La interfaz tiene tres zonas: sidebar izquierdo, chat central y reporte final.

═══════════════════════════════════════════════════════════════
                    1. SISTEMA DE DISEÑO
═══════════════════════════════════════════════════════════════

## IDENTIDAD VISUAL
- Tema: "Terminal Green" — oscuro, técnico, minimalista, inspirado en terminales
  y dashboards de DevOps
- Sin decoraciones innecesarias, jerarquía visual por color (no por tamaño)
- Accent verde como guía de atención, usado con moderación

## PALETA DE COLORES

### Superficies
| Token                | Hex       | Uso                                        |
|----------------------|-----------|--------------------------------------------|
| surface.base         | #0A0A0A   | Background principal (sidebar, chat)       |
| surface.header       | #0D0D0D   | Headers y barras superiores                |
| surface.card-active  | #141414   | Cards activas, inputs, search bar          |
| surface.card-idle    | #0F0F0F   | Cards inactivas, bloques MESSAGE           |
| surface.code         | #080808   | Bloques de código JSON/tool output         |
| surface.report-card  | #111111   | Card del Final Report                      |

### Bordes y divisores
| Token                | Hex       | Uso                                        |
|----------------------|-----------|--------------------------------------------|
| border.subtle        | #1A1A1A   | Bordes de inputs, header bottom border     |
| border.divider       | #1E1E1E   | Líneas divisorias, bordes de report card   |
| border.badge-bg      | #1A1A1A   | Background de pills (REFERENCES, SUBBLOCKS)|

### Texto
| Token                | Hex       | Uso                                        |
|----------------------|-----------|--------------------------------------------|
| text.primary         | #FFFFFF   | Títulos principales, headings del report   |
| text.secondary       | #CCCCCC   | Títulos de items, contenido de bloques     |
| text.tertiary        | #DDDDDD   | Nombre usuario, section labels del report  |
| text.muted           | #AAAAAA   | Contenido bloques SYSTEM/CLARIFY, report body |
| text.subtle          | #888888   | Código en tool blocks                      |
| text.placeholder     | #666666   | Placeholders, tabs inactivos, fuentes muted|
| text.dim             | #555555   | Preview text, emails, settings icon        |
| text.ghost           | #444444   | Timestamps, botones COPY, chevrons         |

### Accent primario (verde terminal)
| Token                | Hex         | Uso                                      |
|----------------------|-------------|------------------------------------------|
| accent.solid         | #00FF00     | CTA button fill, texto activo, dots      |
| accent.tint-15       | #00FF0015   | Bg tab activo, avatar circle             |
| accent.tint-18       | #00FF0018   | Bg badge COMPLETED                       |
| accent.tint-10       | #00FF0010   | Bg botón Collapse all (activo)           |
| accent.border-40     | #00FF0040   | Left border item activo sidebar          |
| accent.border-30     | #00FF0030   | Left border bloques PRO/ASSISTANT        |
| accent.border-25     | #00FF0025   | Stroke icon brand, stroke Collapse btn   |
| accent.gradient-top  | #00FF0030   | Gradient top del icon brand              |
| accent.gradient-bot  | #00FF0008   | Gradient bottom del icon brand           |

### Colores de status
| Status     | Dot/Texto  | Background tint | Left border  | Card bg  |
|------------|------------|-----------------|--------------|----------|
| Completed  | #00FF00    | #00FF0018       | #00FF0040    | #0A150A  |
| Running    | #FFB800    | #FFB80018       | #FFB80040    | #15120A  |
| Clarify    | #FF6B6B    | #FF6B6B30       | #FF6B6B40    | #150A0A  |
| (sidebar)  | #FF6B00    | #FF6B0018       | —            | —        |

### Colores de bloques del chat
| Bloque               | Dot/Label  | Left border  | Card bg  |
|----------------------|------------|--------------|----------|
| MESSAGE              | #888888    | #88888840    | #0F0F0F  |
| PRO (user)           | #00FF00    | #00FF0040    | #0A150A  |
| CLARIFY WITH USER    | #FF6B6B    | #FF6B6B40    | #150A0A  |
| SYSTEM               | #FFB800    | #FFB80040    | #15120A  |
| ASSISTANT            | #00FF00    | #00FF0040    | #0A150A  |
| RESEARCH BRIEF       | #C084FC    | #C084FC40    | #100A15  |
| TOOL CALL            | #666666    | #66666640    | #0C0C0C  |
| TOOL OUTPUT          | #FFB800    | #66666620    | #0C0C0C  |
| CONDUCT_RESEARCH     | #C084FC    | #66666620    | #0C0C0C  |

## TIPOGRAFÍA

### Font Families
- Body/UI: "Geist" (sans-serif moderna, limpia)
- Técnico/datos: "Geist Mono" (monospace para badges, timestamps, código, labels)

### Escala tipográfica completa
| Elemento                     | Font        | Size | Weight | Color    | lineHeight |
|------------------------------|-------------|------|--------|----------|------------|
| Report main title            | Geist       | 20px | 700    | #FFFFFF  | 1.3        |
| Report section labels        | Geist       | 15px | 600    | #DDDDDD  | —          |
| Chat header title            | Geist       | 15-16px | 500  | #FFFFFF  | 1.3        |
| Final Report label           | Geist       | 16px | 600    | #FFFFFF  | —          |
| Brand name "Deep Researcher" | Geist       | 15px | 600    | #FFFFFF  | —          |
| CTA button "New Research"    | Geist       | 14px | 600    | #000000  | —          |
| Conversation item title      | Geist       | 13px | 500    | #FFFFFF/#CCCCCC | 1.3 |
| Block content text           | Geist       | 13px | normal | #CCCCCC/#AAAAAA | 1.4 |
| Report body text             | Geist       | 13px | normal | #AAAAAA  | 1.5        |
| Bullet list items            | Geist       | 13px | normal | #CCCCCC  | —          |
| Search placeholder           | Geist       | 13px | normal | #666666  | —          |
| User name                    | Geist       | 13px | 500    | #DDDDDD  | —          |
| Collapse/Expand buttons      | Geist       | 12px | normal | #00FF00/#555555 | — |
| Download .md button          | Geist       | 12px | 600    | #000000  | —          |
| Code in tool blocks          | Geist Mono  | 12px | normal | #888888  | 1.5        |
| Filter tabs                  | Geist Mono  | 12px | 500/normal | #00FF00/#666666 | — |
| Block type labels            | Geist Mono  | 11px | 600    | (color del bloque) | — |
| COPY button text             | Geist Mono  | 10-11px | normal | #444444  | —        |
| Status badges (COMPLETED)    | Geist Mono  | 10-11px | 500-600 | #00FF00 | —        |
| Preview text                 | Geist       | 11px | normal | #555555  | 1.2        |
| User email                   | Geist Mono  | 11px | normal | #555555  | —          |
| Source count "6 sources"     | Geist Mono  | 11px | normal | #666666  | —          |
| Timestamps "2h ago"          | Geist Mono  | 10px | normal | #444444  | —          |
| Pill badges (REFERENCES)     | Geist Mono  | 9px  | 500    | #555555  | —          |

## BORDES Y RADIOS
| Elemento                    | cornerRadius |
|-----------------------------|-------------|
| Sidebar container           | 12px        |
| Chat container              | 12px        |
| Report card                 | 10px        |
| Buttons, inputs, msg cards  | 8px         |
| Brand icon container        | 8px         |
| Pill badges (status)        | 10px        |
| Filter tabs                 | 12px (pill) |
| Collapse/Expand buttons     | 6px         |
| Code blocks                 | 6px         |
| Avatar (32x32)              | 16px (circle)|
| Bullet dots                 | circle (5x5)|
| Status dots                 | circle (8x8)|

## ICONOGRAFÍA (Lucide)
| Icono              | Tamaño | Color   | Ubicación                     |
|--------------------|--------|---------|-------------------------------|
| brain-circuit      | 16x16  | #00FF00 | Brand icon (dentro de 28x28 container con gradient) |
| plus               | 16x16  | #000000 | Botón New Research            |
| search             | 14x14  | #666666 | Search bar                    |
| chevrons-down-up   | 14x14  | #00FF00 | Collapse all (activo)         |
| chevrons-up-down   | 14x14  | #555555 | Expand all (inactivo)         |
| chevron-down       | 14x14  | #444444 | Bloques colapsados            |
| file-text          | 18x18  | #FFFFFF | Final Report header           |
| download           | 14x14  | #000000 | Botón Download .md            |
| link               | 12x12  | #666666 | Source count badge             |
| settings           | 18x18  | #555555 | Footer sidebar                |

═══════════════════════════════════════════════════════════════
                    2. SIDEBAR (320px ancho)
═══════════════════════════════════════════════════════════════

### Estructura: vertical, sin gap entre secciones, bg #0A0A0A, cornerRadius 12, clip true

#### Top Section (padding [24,16,16,16], gap 16)
1. **Brand row** — horizontal, gap 10, alignItems center
   - Icon container: frame 28x28, cornerRadius 8, gradient fill (#00FF0030→#00FF0008 linear 180°),
     stroke #00FF0025 1px inside, centered "brain-circuit" icon 16x16 #00FF00
   - Text: "Deep Researcher", Geist 15px weight 600 #FFFFFF

2. **New Research button** — frame full width, height 40, cornerRadius 8, fill #00FF00
   - Centered: icon "plus" 16x16 #000000 + "New Research" Geist 14px 600 #000000, gap 8

3. **Search bar** — frame full width, height 36, cornerRadius 8, fill #141414,
   stroke #1A1A1A 1px inside, padding [0,12], gap 8
   - Icon "search" 14x14 #666666 + "Search conversations..." Geist 13px #666666

4. **Filter tabs** — horizontal, gap 8
   - Cada tab: frame padding [4,10], cornerRadius 12
   - Activo ("All"): fill #00FF0015, text Geist Mono 12px 500 #00FF00
   - Inactivo: sin fill, text Geist Mono 12px normal #666666
   - Tabs: All, Running, Clarify, Completed

#### Conversation List (padding 8, gap 4, clip true, fill_container height)
Cada item: frame full width, cornerRadius 8, padding 12, gap 4 (vertical)

- **Item activo**: fill #141414, stroke inside left 3px #00FF0040
  - Top row: título #FFFFFF + badge (ver abajo)
  - Bottom row: preview #555555 Geist 11px + timestamp #444444 Geist Mono 10px

- **Item inactivo**: fill #0F0F0F, sin stroke especial
  - Top row: título #CCCCCC + badge
  - Bottom row: preview + timestamp

- **Badges**: frame padding [3,8], cornerRadius 10
  - Running: dot 6x6 #FFB800 + text "Running" Geist Mono 10px 500 #FFB800, bg #FFB80018
  - Clarify: dot 6x6 #FF6B00 + text "Clarify" Geist Mono 10px 500 #FF6B00, bg #FF6B0018
  - Completed: text "Completed" Geist Mono 10px 500 #00FF00, bg #00FF0018

#### Divider — line full width, stroke #1E1E1E 1px

#### Footer (padding [12,16], gap 12, horizontal, alignItems center)
- Avatar: frame 32x32, cornerRadius 16, fill #00FF0015, centered "M" Geist 14px 600 #00FF00
- Text column: gap 2, "Maximo" Geist 13px 500 #DDDDDD + email Geist Mono 11px #555555
- Icon "settings" 18x18 #555555

═══════════════════════════════════════════════════════════════
              3. CHAT AREA — VISTA EXPANDIDA (850px)
═══════════════════════════════════════════════════════════════

### Header (fill #0D0D0D, padding [16,24], horizontal, space_between)
- Left: título Geist 16px 500 #FFFFFF + pill "COMPLETED" (cornerRadius 10, fill #00FF0018,
  text Geist Mono 11px #00FF00, padding [4,10])
- Right: dos ghost buttons gap 8
  - "Collapse all": icon chevrons-down-up 14x14 + text Geist 12px, color #666666 (inactivo)
  - "Expand all": icon chevrons-up-down 14x14 + text Geist 12px, color #00FF00 (activo)
  - Botón activo: fill #00FF0010, stroke #00FF0025 1px inside, cornerRadius 6

### Header border — rectangle full width, height 1, fill #1A1A1A

### Message area (padding [16,24], gap 2, vertical)
Cada bloque: frame full width, cornerRadius 8, padding [14,16], gap 10

**Header de cada bloque** (horizontal, gap 8, full width):
- Dot (ellipse 8x8, color del bloque)
- Label (Geist Mono 11px 600, color del bloque, UPPERCASE)
- Spacer (frame fill_container, height 1)
- [Opcional] Pill badge "REFERENCES"/"SUBBLOCKS" (cornerRadius 8, fill #1A1A1A,
  text Geist Mono 10px #666666, padding [3,8])
- "COPY" (Geist Mono 11px #444444)

**Contenido de cada bloque**:
- Texto regular: Geist 13px normal, lineHeight 1.4, textGrowth fixed-width, fill_container
- Código (tool calls): frame cornerRadius 6, fill #080808, padding 12,
  text Geist Mono 12px #888888 lineHeight 1.5

**Left border en cada bloque**: stroke inside, thickness {left:3}, color según tabla de colores

═══════════════════════════════════════════════════════════════
              4. CHAT AREA — VISTA COLAPSADA (850px)
═══════════════════════════════════════════════════════════════

### Header — idéntico al expandido pero con "Collapse all" activo (verde)

### Bloques colapsados (padding [12,24], gap 2)
Cada bloque: frame full width, cornerRadius 8, padding [10,14], horizontal, gap 10,
alignItems center
- Dot 8x8 (color del bloque)
- Label Geist Mono 11px 600 (color del bloque)
- Spacer frame fill_container height 1
- [Opcional] Pill "COPY" text Geist Mono 10px #444444
- [Opcional] Pill badge "REFERENCES"/"SUBBLOCKS"/"ARGUMENTS"
  (cornerRadius 8, fill #1A1A1A, text Geist Mono 9px 500 #555555, padding [2,8])
- Chevron: icon chevron-down 14x14 #444444

Left border: stroke inside {left:3}, color según tabla (con opacidad 20-30)

═══════════════════════════════════════════════════════════════
              5. FINAL REPORT (dentro del chat)
═══════════════════════════════════════════════════════════════

### Section container (padding [8,24,24,24])

### Divider — line full width, stroke #1E1E1E 1px

### Report Header (horizontal, space_between, padding [16,0,12,0])
- Left: icon "file-text" 18x18 #FFFFFF + "Final Report" Geist 16px 600 #FFFFFF, gap 10
- Right: gap 8
  - Source badge: frame cornerRadius 8, stroke #1E1E1E 1px inside, padding [6,12],
    icon "link" 12x12 #666666 + "6 sources" Geist Mono 11px #666666
  - Download button: frame cornerRadius 8, fill #00FF00, padding [8,14], gap 6,
    icon "download" 14x14 #000000 + "Download .md" Geist 12px 600 #000000

### Report Card (cornerRadius 10, fill #111111, stroke #1E1E1E 1px inside,
               padding [24,28,28,28], gap 16)
- Main title: Geist 20px 700 #FFFFFF, lineHeight 1.3
- Section labels: Geist 15px 600 #DDDDDD
- Body text: Geist 13px normal #AAAAAA, lineHeight 1.5
- Bullet list: padding-left 16, gap 6, cada bullet = dot 5x5 #00FF00 + text Geist 13px #CCCCCC
- Fade text (truncated): Geist 13px #666666

═══════════════════════════════════════════════════════════════
              6. PRINCIPIOS DE DISEÑO
═══════════════════════════════════════════════════════════════

1. Densidad media-alta — información compacta pero legible
2. Jerarquía por color, no por tamaño — el verde #00FF00 guía la atención
3. Mínima decoración — sin sombras visibles, gradientes solo en el icon brand
4. Geist Mono para datos técnicos (timestamps, badges, labels, código, filtros)
5. Geist para contenido (títulos, previews, body text, buttons)
6. Status colors semánticos: bg con ~10% opacidad, texto/dots al 100%
7. Bordes sutiles, nunca protagonistas — siempre #1A1A1A o #1E1E1E
8. Left border de 3px como identificador visual de cada tipo de bloque
9. Accent verde solo en: CTA principal, tab activo, badge completado, avatar, brand icon
10. Collapsed = una sola línea por bloque (dot + label + spacer + badge + chevron)
11. Expanded = header + content con tipografía readable y lineHeight generoso
