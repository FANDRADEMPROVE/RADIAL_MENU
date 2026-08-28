# Radial Menu — Menú de anillo para tu mouse

Esto te arma un `.exe` de Windows que abre un menú circular (con submenús,
iconos PNG/SVG, y acciones: programas, scripts, atajos de teclado o macros
de texto), activado por una combinación de teclas (por defecto
`Ctrl+Shift+Alt+Espacio`, que puedes asignar a un botón de tu mouse
Attack Shark). No requiere permisos de administrador para ejecutarse.

No necesitas saber programar ni instalar Python: la compilación se hace
en la nube con GitHub Actions, gratis. Solo sigue estos pasos.

---

## Paso 1 — Crear cuenta de GitHub (si no tienes)

1. Ve a https://github.com/signup
2. Crea una cuenta gratuita con tu correo.

## Paso 2 — Crear un repositorio nuevo

1. Ya con sesión iniciada, ve a https://github.com/new
2. En "Repository name" pon: `radial-menu`
3. Déjalo en **Public** (o Private, cualquiera funciona igual)
4. NO marques ninguna casilla de "Add a README" etc.
5. Da clic en **Create repository**

## Paso 3 — Subir estos archivos

En la página que se abre, verás un botón que dice **"uploading an existing
file"** (o "Add file" → "Upload files" arriba a la derecha).

1. Da clic ahí
2. Arrastra **TODA** la carpeta `radial_menu_app` que te compartí
   (o selecciona todos sus archivos y subcarpetas — incluye la carpeta
   oculta `.github`, es importante)
3. Abajo, en "Commit changes", da clic en **Commit changes** (déjalo con
   los valores por defecto)

> **Importante:** la carpeta `.github/workflows/build.yml` tiene que
> quedar exactamente en esa ruta dentro del repositorio. Si tu navegador
> no te deja arrastrar carpetas completas, usa GitHub Desktop (más abajo,
> Alternativa) o pídeme ayuda y lo revisamos juntos.

## Paso 4 — Esperar a que compile solo

1. Ve a la pestaña **Actions** de tu repositorio (arriba)
2. Verás un proceso corriendo llamado "Compilar Radial Menu (Windows .exe)"
   con un círculo amarillo girando
3. Espera 2-4 minutos hasta que se ponga una palomita verde ✅

## Paso 5 — Descargar tu programa ya compilado

1. Dentro de esa misma pestaña Actions, da clic en el proceso que terminó
   (el de la palomita verde)
2. Abajo de todo, en la sección **Artifacts**, verás
   **"RadialMenu_Portable"** — da clic para descargarlo
3. Se descarga un `.zip`. Descomprímelo donde quieras (Escritorio, USB,
   la compu del trabajo — no necesita instalarse, es portable)

Dentro encontrarás:
- `RadialMenu.exe` — el programa que corre en segundo plano y muestra el
  menú anillo
- `Editor.exe` — la ventana gráfica para armar/editar tus opciones
- `config.json` — donde se guarda tu configuración
- `icons/` — carpeta con los iconos (unos de ejemplo ya incluidos)

---

## Cómo usarlo

1. Abre **Editor.exe** primero para armar tu menú:
   - Arriba, define la combinación que abre el menú (por defecto
     `ctrl+shift+alt+space`)
   - "Agregar opción" para cada botón del anillo: ponle nombre, icono
     (PNG o SVG), tipo de acción (programa / script / atajo / macro /
     submenú) y su valor
   - Si eliges tipo **"Abrir submenú"**, guarda esa opción y luego usa el
     botón **"Editar submenú"** para llenar lo que aparece dentro
   - Da clic en **"Guardar configuración"** al terminar

2. Abre **RadialMenu.exe** — se queda corriendo en segundo plano (verás
   una ventana de consola negra, no la cierres, solo minimízala)

3. Presiona la tecla configurada (`F13` por defecto) y el anillo aparecerá
   en la posición de tu cursor

4. Configura tu mouse Attack Shark (desde su software, en casa) para que
   el botón que quieras mande esa misma tecla `F13`

---

## Nota sobre el icono de la consola negra

`RadialMenu.exe` deja abierta una ventanita de consola porque así puedes
ver si algo falla (mensajes de error). Si más adelante quieres que corra
totalmente oculto, dime y te paso la variante sin consola — la dejé así
al inicio para que sea más fácil detectar y corregir cualquier problema.

## Alternativa si no puedes arrastrar carpetas en GitHub Web

Instala **GitHub Desktop** (gratis, sin permisos de admin en muchos casos):
https://desktop.github.com — te deja arrastrar la carpeta completa del
proyecto a tu repositorio con un clic de "Publish". Si prefieres esta
ruta, avísame y te doy el paso a paso específico.

---

## Si algo no compila

Pégame el texto de error que aparece en la pestaña Actions (la parte en
rojo) y lo resolvemos — es normal que a la primera compilación le falte
ajustar algo pequeño.
