from typing import Set, List
from bsky import get_follower_handles
from graph_tool.all import Graph, load_graph
from graf_interaccio_threads import _get_client_threads, build_interaction_graph
import matplotlib
import pandas as pd
import os

matplotlib.use("Agg")


def identifica_seguidors_valuosos(client_handle: str) -> None:
    """
    Analitza el graf d'interacció de threads d'un usuari per identificar quins seguidors directes ajuden a expandir la seva veu més enllà del seu cercle immediat.
    Calcula, per a cada seguidor, la proporció de respostes que provenen de fora del cercle de seguidors directes, i exporta els resultats a CSV i per pantalla.
    """
    carpeta = os.path.join("resultats", client_handle)
    os.makedirs(carpeta, exist_ok=True)
    threads_path = os.path.join(carpeta, f"{client_handle}_threads.gt")
    # --- Carreguem graf de threads ---
    if not os.path.isfile(threads_path):
        threads = _get_client_threads(client_handle, limit=100)
        g_threads = build_interaction_graph(threads, client_handle)
    else:
        g_threads = load_graph(threads_path)
    if g_threads is None:
        print(
            f"Error: No s'ha pogut construir el graf de threads per '{client_handle}'."
        )
        return

    # --- Extraiem seguidors directes del client ---
    seguidors_directes: Set[str] = set(get_follower_handles(client_handle))

    # --- Analitzem comportament dels seguidors al graf de threads ---
    dades: List[dict[str, str | int | float]] = []

    for v in g_threads.vertices():
        autor: str = (
            g_threads.vp["user"][v]
            if "user" in g_threads.vp
            else g_threads.vp["handle"][v]
        )
        if autor not in seguidors_directes:
            continue
        expansions: int = 0
        total_respostes: int = 0
        for e in v.in_edges():  # qui ha respost a aquest seguidor
            origen = e.source()
            repon: str = (
                g_threads.vp["user"][origen]
                if "user" in g_threads.vp
                else g_threads.vp["handle"][origen]
            )
            if repon != client_handle and repon not in seguidors_directes:
                expansions += 1
            total_respostes += 1
        if total_respostes > 0:
            proporcio_expansio: float = expansions / total_respostes
        else:
            proporcio_expansio = 0.0
        dades.append(
            {
                "handle": autor,
                "respostes_totals": total_respostes,
                "respostes_expansio": expansions,
                "proporcio_expansio": proporcio_expansio,
            }
        )
    # --- Guardem resultats ---
    df = pd.DataFrame(dades)
    if df.empty:
        print("No s'ha trobat cap seguidor directe amb activitat al graf de threads.")
        return
    df = df.sort_values(by="proporcio_expansio", ascending=False)
    out_csv = os.path.join(carpeta, f"seguidors_valuosos_{client_handle}.csv")
    df.to_csv(out_csv, index=False)

    # Mostra taula bonica per pantalla
    print("\nSeguidors valuosos (expansió fora del cercle directe):")
    print(
        "{:<30} {:>10} {:>18} {:>18}".format(
            "Handle", "Respostes", "Expansió", "% Expansió"
        )
    )
    print("-" * 80)
    for _, row in df.iterrows():
        percent = f"{row['proporcio_expansio']*100:.1f}%"
        print(
            f"{row['handle']:<30} {int(row['respostes_totals']):>10} {int(row['respostes_expansio']):>18} {percent:>18}"
        )
    print(f"\nResultats desats a '{out_csv}'")
    print(
        "\n% Expansió: percentatge de respostes d'aquest seguidor que han ajudat a expandir la veu fora del cercle directe."
    )


def main():
    """
    Permet executar el mòdul per identificar seguidors valuosos d'un usuari a partir del seu handle.
    """
    handle: str = input("Introdueix el handle del client: ")
    identifica_seguidors_valuosos(handle)


if __name__ == "__main__":
    main()
