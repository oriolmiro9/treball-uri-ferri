from graf_interaccio_threads import _get_client_threads, _build_interaction_graph
from graph_tool.all import Graph
import os

def build_threads_graph(client_handle: str, output_path: str = "", max_posts: int = 100) -> Graph:
    """
    Construeix el graf d'interacció de threads d'un usuari i el desa si cal.
    Retorna el graf.
    """
    threads = _get_client_threads(client_handle, limit=max_posts)
    g = _build_interaction_graph(threads)
    if not output_path:
        carpeta = os.path.join("resultats", client_handle)
        os.makedirs(carpeta, exist_ok=True)
        output_path = os.path.join(carpeta, f"{client_handle}_threads.gt")
    g.save(output_path)
    return g
