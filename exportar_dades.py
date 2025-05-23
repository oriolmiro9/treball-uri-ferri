import os
import shutil

def exportar_dades(handle: str):
    """
    Organitza i copia tots els fitxers generats per l'anàlisi
    a la carpeta resultats/<handle>/
    """
    print(f"\n📁 Organitzant resultats per a @{handle}...")
    carpeta_desti = os.path.join("resultats", handle)
    os.makedirs(carpeta_desti, exist_ok=True)

    # Llistat de fitxers esperats a moure (nom fix o prefixats)
    fitxers_a_moure = [
        f"seguidors_{handle}.gt",
        f"threads_{handle}.gt",
        f"analisi_seguidors_{handle}.csv",
        "pagerank_vs_betweenness.png",
        "pagerank_vs_closeness.png",
        "distribucions_centralitats.png",
        f"comunitats_{handle}_visualitzacio.pdf",
        f"comunitats_{handle}_jerarquia.pdf",
        f"comunitats_{handle}_densitats.csv",
        f"comunitats_{handle}_assignacio.csv",
        f"comunitats_{handle}_pagerank_comunitats.csv"
    ]

    fitxers_moguts = 0

    for fitxer in fitxers_a_moure:
        if os.path.exists(fitxer):
            shutil.move(fitxer, os.path.join(carpeta_desti, os.path.basename(fitxer)))
            fitxers_moguts += 1
        else:
            print(f"⚠️ Fitxer no trobat: {fitxer}")

    print(f"\n✅ {fitxers_moguts} fitxers moguts a 'resultats/{handle}/'")
