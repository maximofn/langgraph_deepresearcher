## BOTÓN COPY — Estilo interactivo (outlined ghost button)

El botón "Copy" debe verse claramente como un elemento INTERACTIVO/clickable,
diferenciándose visualmente de las etiquetas informativas.

### Estructura
- Contenedor: frame, layout horizontal, gap 4, alignItems center
- Padding: [4, 10, 4, 10] (vertical 4px, horizontal 10px)
- Corner radius: 6px
- Background: TRANSPARENTE (sin fill, o fill con alpha 0)
- Border: stroke 1px, color #444444, align inside

### Contenido
- Icono: lucide "copy", 11x11px, fill #888888
- Texto: "Copy" (capitalizado, NO todo mayúsculas), Geist Mono 10px, normal weight, fill #888888

### Diferenciadores clave vs etiquetas info
1. ✅ Tiene BORDE visible (#444444) → señal universal de botón
2. ✅ SIN fondo → estilo "ghost/outlined button"
3. ✅ Tiene ICONO (copy) → refuerza que es una acción
4. ✅ Texto más BRILLANTE (#888888) → destaca sobre el fondo oscuro
5. ✅ Padding horizontal mayor (10px) → da más espacio de click target

### Estados (para implementación)
- Default: border #444444, text/icon #888888
- Hover: border #666666, text/icon #AAAAAA, bg #1A1A1A (sutil highlight)
- Active/Click: border #00FF00, text/icon #00FF00 (feedback de acción)
- Copied (temporal, 2s): icono cambia a "check", texto "Copied!", color #00FF00

---

## ETIQUETA DE AGENTE — Estilo informativo (filled tag)

La etiqueta de agente (Scope, Supervisor, User) debe verse como METADATA estática,
NO interactiva.

### Estructura
- Contenedor: frame, layout horizontal, alignItems center
- Padding: [2, 8, 2, 8] (vertical 2px, horizontal 8px — más compacto que el botón)
- Corner radius: 8px
- Background: fill #1A1A1A (sólido, sutil)
- Border: NINGUNO (sin stroke)

### Contenido
- Solo texto, SIN icono
- Texto: nombre del agente ("Scope", "Supervisor", "User")
- Font: Geist Mono 9px, weight 500, fill #555555

### Diferenciadores clave vs Copy button
1. ✅ Tiene FONDO sólido (#1A1A1A) → parece una etiqueta/badge
2. ✅ SIN borde → no parece clickable
3. ✅ SIN icono → no sugiere acción
4. ✅ Texto más TENUE (#555555 vs #888888) → se lee como metadata
5. ✅ Font más pequeño (9px vs 10px) → jerarquía visual inferior
6. ✅ Padding más compacto → no invita al click

---

## RESUMEN VISUAL COMPARATIVO

| Propiedad        | Agent Tag (info)         | Copy Button (acción)       |
|------------------|--------------------------|----------------------------|
| Background       | #1A1A1A (filled)         | Transparente               |
| Border           | Ninguno                  | #444444, 1px               |
| Icono            | No                       | Sí (lucide "copy" 11x11)  |
| Texto            | "Scope"/"Supervisor"     | "Copy"                     |
| Font             | Geist Mono 9px, 500     | Geist Mono 10px, normal    |
| Color texto      | #555555                  | #888888                    |
| Padding          | [2, 8]                   | [4, 10]                    |
| Corner radius    | 8px                      | 6px                        |
| Señal visual     | Tag/badge estático       | Ghost button interactivo   |

## PRINCIPIO DE DISEÑO
La diferencia se basa en el patrón "filled vs outlined":
- **Filled** (fondo sólido, sin borde) = información pasiva, etiqueta, badge
- **Outlined** (sin fondo, con borde + icono) = acción interactiva, botón

Este es el mismo patrón que usan Figma, Linear, Notion y otros productos
para distinguir tags de acciones en interfaces densas.