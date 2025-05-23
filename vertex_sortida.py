from typing import Optional, Set
from bsky import get_follower_handles
from graph_tool.all import Graph, Vertex, load_graph
from graf_fusio_threads import build_threads_graph
import matplotlib
import pandas as pd
from typing import List, Dict, Optional, Tuple
matplotlib.use("Agg")


def identifica_seguidors_valuosos(client_handle: str) -> None:
    """
    Combina el graf de threads per identificar
    quins seguidors del client ajuden a expandir la seva veu
    fora del cercle de seguidors directes.
    Ara s'obtenen els seguidors directes amb get_follower_handles.
    """
    # --- Carreguem graf de threads ---
    g_threads: Graph = build_threads_graph(client_handle, f"threads_{client_handle}.gt", max_posts=100)
    if g_threads is None:
        print(f"❌ Error: No s'ha pogut construir el graf de threads per '{client_handle}'.")
        return

    # --- Extraiem seguidors directes del client ---
    seguidors_directes: Set[str] = set(get_follower_handles(client_handle))

    # --- Analitzem comportament dels seguidors al graf de threads ---
    dades: List[dict[str, str | int]] = [] 

    for v in g_threads.vertices(): 
        autor: str = g_threads.vp["handle"][v]
        if autor not in seguidors_directes:
            continue

        expansions: int = 0
        total_respostes: int = 0

        for e in v.in_edges():  # qui ha respost a aquest seguidor
            origen = e.source()
            repon: str = g_threads.vp["handle"][origen] 
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
        print("⚠️ No s'ha trobat cap seguidor directe amb activitat al graf de threads.")
        return
    df = df.sort_values(by="proporcio_expansio", ascending=False)
    df.to_csv(f"seguidors_valuosos_{client_handle}.csv", index=False)

    # Mostra només els 10 primers, o tots els amb proporció > 0 si n'hi ha menys de 10
    df_positius = df[df["proporcio_expansio"] > 0]
    if len(df_positius) < 10 and not df_positius.empty:
        print("📋 Seguidors amb proporció d'expansió > 0:")
        print(df_positius.to_string(index=False))
    else:
        print("📋 Top seguidors amb més capacitat d'expansió:")
        print(df.head(10).to_string(index=False))
    print(f"✅ Resultats desats a 'seguidors_valuosos_{client_handle}.csv'")


def main() -> None:
    handle: str = input("Introdueix el handle del client: ")
    identifica_seguidors_valuosos(handle)


if __name__ == "__main__":
    main()
