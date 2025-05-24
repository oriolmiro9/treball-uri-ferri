import click
import os
from graph_tool.all import load_graph
from graf_seguidors import build_followers_subgraph
from graf_interaccio_threads import _get_client_threads, _build_interaction_graph
from comunitats import main as comunitats_main
from pagerank import main as pagerank_main
from propagacio_threads import main as propagacio_main
from vertex_sortida import identifica_seguidors_valuosos

def neteja_handle(handle: str) -> str:
    # Elimina caràcters invisibles i espais
    return handle.strip().replace('\u200e', '').replace('\u200f', '').replace('\u202a', '').replace('\u202c', '').replace('\u202d', '').replace('\u202e', '')

@click.command()
@click.option('--handle', prompt="Introdueix el handle de l'usuari (sense @)", help='Handle de Bluesky (sense @)')
@click.option('--analisi', prompt="Quina anàlisi vols fer? (seguidors/threads/comunitats/pagerank/propagacio/valuosos/completa)",
              type=click.Choice(['seguidors', 'threads', 'comunitats', 'pagerank', 'propagacio', 'valuosos', 'completa']),
              default='completa',
              help="Tipus d'anàlisi a fer")


def analitza(handle: str, analisi: str):
    handle = neteja_handle(handle)
    carpeta = os.path.join("resultats", handle)
    os.makedirs(carpeta, exist_ok=True)
    fitxer_seguidors = os.path.join(carpeta, f"{handle}_followers.gt")
    fitxer_threads = os.path.join(carpeta, f"{handle}_threads.gt")

    # SEGUIDORS
    if analisi in ["seguidors", "completa", "comunitats", "pagerank"]:
        if not os.path.isfile(fitxer_seguidors):
            print("Creant graf de seguidors...")
            build_followers_subgraph(handle)
        else:
            print("Graf de seguidors ja existeix.")
        if os.path.isfile(fitxer_seguidors):
            g = load_graph(fitxer_seguidors)
            if g.num_vertices() == 0:
                print("Advertència: el graf de seguidors està buit. Comprova el handle i que l'usuari tingui seguidors.")

    # THREADS
    if analisi in ["threads", "completa", "propagacio"]:
        if not os.path.isfile(fitxer_threads):
            print("Creant graf de threads...")
            threads = _get_client_threads(handle)
            g = _build_interaction_graph(threads)
            g.save(fitxer_threads)
        else:
            print("Graf de threads ja existeix.")
        if os.path.isfile(fitxer_threads):
            g = load_graph(fitxer_threads)
            if g.num_vertices() == 0:
                print("Advertència: el graf de threads està buit. Comprova el handle i que l'usuari tingui activitat.")

    # COMUNITATS
    if analisi in ["comunitats", "completa"]:
        print("Analitzant comunitats...")
        comunitats_main(handle)

    # PAGERANK , BETWEENNESS, CLOSENESS
    if analisi in ["pagerank", "completa"]:
        print("Calculant centralitats (PageRank, Betweenness, Closeness)...")
        pagerank_main(handle)

    # PROPAGACIÓ
    if analisi in ["propagacio", "completa"]:
        print("Calculant propagació de threads...")
        propagacio_main(handle)

    # VALUOSOS
    if analisi in ["valuosos", "completa"]:
        print("Identificant seguidors valuosos...")
        identifica_seguidors_valuosos(handle)

    print("Anàlisi finalitzada!")

if __name__ == '__main__':
    analitza()
