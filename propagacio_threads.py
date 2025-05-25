import matplotlib
matplotlib.use("Agg")
from graf_interaccio_threads import build_interaction_graph, _get_client_threads
from graph_tool.all import load_graph, Graph, shortest_distance
import matplotlib.pyplot as plt
from collections import Counter
import os
import numpy as np

def calcula_distancia_propagacio(g: Graph, handle_arrel: str) -> None:
    """
    Calcula la distància de propagació de les respostes a partir d'un usuari arrel dins d'un graf de threads.
    Mostra un histograma de distàncies i desa el gràfic a la carpeta de resultats.
    Si l'arrel no existeix o no hi ha vèrtexs accessibles, mostra un avís.
    """
    # Ara la propietat es diu 'user' en comptes de 'handle'
    vp_handle = g.vertex_properties["user"]

    # Troba el vèrtex associat a l'usuari arrel
    v_arrel = None
    for v in g.vertices():
        if vp_handle[v] == handle_arrel:
            v_arrel = v
            break

    if v_arrel is None:
        print(
            f"No s'ha trobat cap vèrtex amb handle '{handle_arrel}'. Potser l'usuari no té posts originals o el handle no coincideix exactament."
        )
        return

    # Calcular distàncies
    dist_map = shortest_distance(g, source=v_arrel)

    # graph-tool pot retornar un VertexPropertyMap o un array de numpy directament
    # Si és VertexPropertyMap, convertim a array amb list()
    try:
        dist_array = np.array(list(dist_map))
    except Exception:
        dist_array = np.array(dist_map)
    INFINIT = 2147483647
    distancies = [int(d) for d in dist_array if 0 < int(d) < INFINIT]
    inaccessibles = sum(1 for d in dist_array if int(d) == INFINIT)

    if not distancies:
        print("No s'han trobat vèrtexs accessibles des de l'arrel (o només l'arrel).")
        return

    dist_max = max(distancies)
    histograma = Counter(distancies)

    print(f"\n📏 Distància màxima de propagació: {dist_max}")
    print("📊 Histograma de distàncies:")
    for d in sorted(histograma):
        print(f"  Distància {d}: {histograma[d]} vèrtexs")
    if inaccessibles > 0:
        print(f"  (Hi ha {inaccessibles} vèrtexs inaccessibles des de l'arrel)")

    # Mostrar gràfic
    plt.bar(list(histograma.keys()), list(histograma.values()), color="skyblue")
    plt.xlabel("Distància")
    plt.ylabel("Nombre de vèrtexs")
    plt.title(f"Histograma de distàncies des de '{handle_arrel}'")
    plt.grid(True)
    plt.tight_layout()
    # Desa el gràfic en comptes de mostrar-lo
    carpeta = os.path.join("resultats", handle_arrel)
    os.makedirs(carpeta, exist_ok=True)
    img_path = os.path.join(carpeta, f"propagacio_{handle_arrel}.svg")
    plt.savefig(img_path)
    plt.close()
    print(f"📈 Gràfic desat a: {img_path}")


def carregar_graf_threads(handle: str):
    """
    Carrega el graf de threads d'un usuari des de la carpeta de resultats.
    Si el graf no existeix, l'intenta generar automàticament. Retorna el graf carregat o None si falla.
    """
    carpeta = os.path.join("resultats", handle)
    os.makedirs(carpeta, exist_ok=True)
    graf_path = os.path.join(carpeta, f"{handle}_threads.gt")
    if not os.path.isfile(graf_path):
        print(
            f"No s'ha trobat el graf de threads per a {handle}. Es genera automàticament..."
        )
        threads = _get_client_threads(handle)
        build_interaction_graph(threads, handle)
        if not os.path.isfile(graf_path):
            print(f"Error: no s'ha pogut generar el graf de threads per a {handle}.")
            return None
    return load_graph(graf_path)


def main(handle=None):
    """
    Permet executar el mòdul des de la línia de comandes per analitzar la propagació de threads d'un usuari.
    Demana el handle per entrada o com a argument, i desa els resultats a la carpeta corresponent.
    """
    import sys

    if handle is None:
        if len(sys.argv) > 1:
            handle = sys.argv[1].strip()
        else:
            handle = input(
                "Introdueix el handle de l'usuari (ex: user.bsky.social): "
            ).strip()
    # Neteja de caràcters invisibles
    handle = (
        handle.replace("\u200e", "")
        .replace("\u200f", "")
        .replace("\u202a", "")
        .replace("\u202c", "")
        .replace("\u202d", "")
        .replace("\u202e", "")
    )
    g = carregar_graf_threads(handle)
    if g is not None:
        calcula_distancia_propagacio(g, handle)


if __name__ == "__main__":
    main()
