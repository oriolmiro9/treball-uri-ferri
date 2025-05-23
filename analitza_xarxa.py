import click
import os
from build_followers_subgraph import build_followers_subgraph
from build_threads_graph import build_threads_graph
from analisi_seguidors import analisi_seguidors
from analisi_comunitats import analisi_comunitats

@click.command()
@click.option('--handle', prompt='🔠 Introdueix el handle de l\'usuari (sense @)', help='Handle de Bluesky (sense @)')
@click.option('--analisi', type=click.Choice(['seguidors', 'threads', 'comunitats', 'completa']), default='completa', help='Tipus d\'anàlisi a fer')
def analitza(handle: str, analisi: str):
    """
    Analitza la xarxa de seguidors i converses d'un usuari de Bluesky,
    i produeix visualitzacions i dades analítiques.
    """
    print(f"\n🔍 Analitzant usuari: @{handle}")
    fitxer_seguidors = f"seguidors_{handle}.gt"
    fitxer_threads = f"threads_{handle}.gt"

    df_centralitats = None

    if analisi in ["seguidors", "completa"]:
        if not os.path.exists(fitxer_seguidors):
            print("📡 Creant graf de seguidors...")
            build_followers_subgraph(handle, fitxer_seguidors)
        else:
            print("✅ Graf de seguidors ja existeix.")

        print("📈 Analitzant centralitats de seguidors...")
        df_centralitats = analisi_seguidors(fitxer_seguidors)

    if analisi in ["comunitats", "completa"]:
        if not os.path.exists(fitxer_seguidors):
            print("⚠️ Graf de seguidors no trobat. Executa primer l'anàlisi de seguidors.")
        else:
            print("🧩 Analitzant comunitats...")
            analisi_comunitats(fitxer_seguidors, output_prefix=f"comunitats_{handle}")

    if analisi in ["threads", "completa"]:
        if not os.path.exists(fitxer_threads):
            print("💬 Creant graf de threads...")
            build_threads_graph(handle, fitxer_threads)
        else:
            print("✅ Graf de threads ja existeix.")

    print("\n🏁 Anàlisi finalitzada!")

if __name__ == '__main__':
    analitza()
