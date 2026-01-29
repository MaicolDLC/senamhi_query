import requests
import re

def get_station(criterio_busqueda):
    """
    Consulta estaciones SENAMHI por nombre o por código.
    El tipo de búsqueda se detecta automáticamente.
    """

    CATEGORIAS_SENAMHI = {
        "CP": "Climatológica Principal",
        "CO": "Climatológica Ordinaria",
        "MAP": "Meteorológica Agrícola Principal",
        "PLU": "Pluviométrica",
        "HLM": "Hidrológica Limnimétrica",
        "HLG": "Hidrológica Limnigráfica",
        "EMA": "Meteorológica Automática",
        "EAMA": "Agrometeorológica Automática",
        "EHA": "Hidrológica Automática",
        "EHMA": "Hidrometeorológica Automática",
        "EAA": "Ambiental Automática",
        "SIN": "Sinóptica",
        "O": "Oceanográfica Automática",
        "PE": "Propósito Específico"
    }

    url = "https://www.senamhi.gob.pe/mapas/mapa-estaciones-2/"
    html = requests.get(url).text

    buscar_por_codigo = str(criterio_busqueda).isdigit()
    criterio = str(criterio_busqueda).upper()

    bloques = html.split('"nom":')

    resultados = []

    for bloque in bloques[1:]:
        nombre = bloque.split('"')[1]
        partes = bloque.split(',')

        est = {"estacion": nombre}

        for p in partes:
            if '"cod":' in p:
                est["codigo"] = re.sub(r'\D', '', p)
            elif '"cate":' in p:
                est["categoria"] = p.replace('"cate":', '').strip().strip('"')
            elif '"estado":' in p:
                est["estado_raw"] = re.sub(r'[^A-Z]', '', p.upper())
            elif '"lat":' in p:
                est["lat"] = p.replace('"lat":', '').strip()
            elif '"lon":' in p:
                est["lon"] = p.replace('"lon":', '').strip()

        coincide = False

        if buscar_por_codigo and est.get("codigo") == criterio:
            coincide = True
        elif not buscar_por_codigo and criterio in nombre.upper():
            coincide = True

        if not coincide:
            continue

        sigla_cat = est.get("categoria", "ND")
        cat_larga = CATEGORIAS_SENAMHI.get(sigla_cat, "No definida por SENAMHI")

        estado_raw = est.get("estado_raw", "")

        if "AUTO" in estado_raw:
            estado_final = "AUTOMATICA"
        elif "REAL" in estado_raw:
            estado_final = "REAL (CONV)"
        elif "DIF" in estado_raw:
            estado_final = "DIFERIDO (CONV)"
        else:
            estado_final = "NO DEFINIDO"

        est_final = {
            "estacion": est.get("estacion"),
            "codigo": est.get("codigo"),
            "categoria_sigla": sigla_cat,
            "categoria": cat_larga,
            "estado": estado_final,
            "lat": est.get("lat"),
            "lon": est.get("lon"),
        }

        resultados.append(est_final)

        # Mantener prints como tú pediste
        print("─" * 75)
        print(f"Estación   : {est['estacion']}")
        print(f"Código     : {est.get('codigo')}")
        print(f"Categoría  : {sigla_cat} → {cat_larga}")
        print(f"Estado     : {estado_final}")
        print(f"Lat / Lon  : {est.get('lat')} , {est.get('lon')}")

    print("─" * 75)

    return resultados
