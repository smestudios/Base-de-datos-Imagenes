import os
import json
import shutil

ESTADO_FILENAME = "estado.json"
EXTENSION = ".webp"

def cargar_estado():
    if os.path.exists(ESTADO_FILENAME):
        with open(ESTADO_FILENAME, 'r') as f:
            return json.load(f)
    return {}

def guardar_estado(estado):
    with open(ESTADO_FILENAME, 'w') as f:
        json.dump(estado, f, indent=4)

def obtener_info_actual(carpeta, prefijo):
    archivos = [f for f in os.listdir(carpeta) if f.endswith(EXTENSION) and os.path.isfile(os.path.join(carpeta, f))]
    numerados = [f for f in archivos if f.startswith(prefijo + '_') and f[len(prefijo)+1:-len(EXTENSION)].isdigit()]
    return {
        'total': len(archivos),
        'numerados': len(numerados),
        'archivos': archivos,
        'numerados_lista': numerados
    }

def procesar_carpeta(ruta_subcarpeta, subcarpeta, estado_anterior):
    print(f"\n🔍 Revisando carpeta: {subcarpeta}")
    info = obtener_info_actual(ruta_subcarpeta, subcarpeta)
    total_actual = info['total']
    numerados_actual = info['numerados']
    archivos = info['archivos']

    estado_prev = estado_anterior.get(subcarpeta, {})
    if estado_prev.get('total') == total_actual and estado_prev.get('numerados') == numerados_actual:
        print("✅ Sin cambios detectados.")
        return estado_anterior

    numeros_usados = set()
    for nombre in info['numerados_lista']:
        try:
            numero = int(nombre.replace(subcarpeta + '_', '').replace(EXTENSION, ''))
            numeros_usados.add(numero)
        except ValueError:
            pass

    if numeros_usados:
        max_existente = max(numeros_usados)
        min_existente = min(numeros_usados)
    else:
        max_existente = 0
        min_existente = 1

    # Detectar huecos
    huecos = sorted(set(range(min_existente, max_existente + 1)) - numeros_usados)
    if huecos:
        print(f"⚠️  Huecos detectados en '{subcarpeta}': {huecos}")
        for hueco in huecos:
            while True:
                ruta_archivo = input(f"🧩 Proporciona la ruta del archivo para llenar '{subcarpeta}_{hueco}{EXTENSION}':\n> ").strip('"')
                if os.path.exists(ruta_archivo) and ruta_archivo.lower().endswith(EXTENSION):
                    destino = os.path.join(ruta_subcarpeta, f"{subcarpeta}_{hueco}{EXTENSION}")
                    shutil.copy2(ruta_archivo, destino)
                    print(f"✅ Copiado como '{subcarpeta}_{hueco}{EXTENSION}'")
                    break
                else:
                    print("🚫 Ruta inválida o no es .webp. Intenta de nuevo.\n")

    # Renombrar archivos nuevos
    nuevos = [f for f in archivos if not f.startswith(subcarpeta + '_') or not f[len(subcarpeta)+1:-len(EXTENSION)].isdigit()]
    contador = max(numeros_usados) + 1 if numeros_usados else 1

    for archivo in nuevos:
        extension = os.path.splitext(archivo)[1]
        nuevo_nombre = f"{subcarpeta}_{contador}{EXTENSION}"
        ruta_vieja = os.path.join(ruta_subcarpeta, archivo)
        ruta_nueva = os.path.join(ruta_subcarpeta, nuevo_nombre)
        os.rename(ruta_vieja, ruta_nueva)
        print(f"📁 Renombrado: {archivo} → {nuevo_nombre}")
        contador += 1

    # Guardar nuevo estado
    estado_anterior[subcarpeta] = {
        "total": len([f for f in os.listdir(ruta_subcarpeta) if f.endswith(EXTENSION)]),
        "numerados": contador - 1
    }
    print(f"✅ Carpeta '{subcarpeta}' organizada correctamente.")
    return estado_anterior

def renombrar_stickers(ruta_base):
    estado = cargar_estado()
    subcarpetas = [d for d in os.listdir(ruta_base) if os.path.isdir(os.path.join(ruta_base, d))]

    for subcarpeta in subcarpetas:
        ruta_subcarpeta = os.path.join(ruta_base, subcarpeta)
        estado = procesar_carpeta(ruta_subcarpeta, subcarpeta, estado)

    guardar_estado(estado)
    print("\n✅ Proceso completo. Estado actualizado.")

# USO
renombrar_stickers(r'C:\Users\estudianteap2\Downloads\Base-de-datos-Imagenes\RECURSOS')
