import os
import shutil


def exportar_dades(handle: str):
    """
    Mou i organitza tots els fitxers generats per l'anàlisi d'un usuari a la carpeta de resultats corresponent.
    Si algun fitxer esperat no es troba, mostra un avís però continua amb la resta.
    """
    print(f"Organitzant resultats per a @{handle}...")
    carpeta_desti = os.path.join("resultats", handle)
    os.makedirs(carpeta_desti, exist_ok=True)
    fitxers_a_moure = [
        f"{handle}_followers.gt",
        f"{handle}_threads.gt",
        f"comunitats_{handle}.png",
        f"comunitats_{handle}.pdf",
        "comunitats.csv",
        "centralitats_seguidors.csv",
        "pagerank_vs_betweenness.png",
        "pagerank_vs_closeness.png",
    ]
    fitxers_moguts = 0
    for fitxer in fitxers_a_moure:
        if os.path.exists(fitxer):
            shutil.move(fitxer, os.path.join(carpeta_desti, os.path.basename(fitxer)))
            fitxers_moguts += 1
        else:
            print(f"Fitxer no trobat: {fitxer}")
    print(f"{fitxers_moguts} fitxers moguts a 'resultats/{handle}/'")

if __name__ == "__main__":
    handle = input("Introdueix el handle de l'usuari (ex: user.bsky.social): ").strip()
    exportar_dades(handle)
