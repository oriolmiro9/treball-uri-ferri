from bsky import get_feed, get_thread, Thread, Post
from graph_tool.all import Graph, graph_draw
from typing import Optional, List, Union
import os


def _count_replies(thread: Thread) -> int:
    """
    Calcula el nombre total de respostes dins d'un thread, incloent-hi totes les respostes recursives a qualsevol nivell.
    Rep un objecte Thread i retorna un enter amb el recompte de respostes totals.
    """
    return sum(1 + _count_replies(r) for r in thread.replies)


def _get_client_threads(client_handle: str, limit: int = 500) -> List[Thread]:
    """
    Recupera tots els threads originals publicats per un usuari concret a Bluesky, sense incloure reposts.
    El paràmetre 'limit' permet controlar quants posts es consulten com a màxim.
    Retorna una llista de threads trobats. Si hi ha errors en obtenir algun thread, es mostren per pantalla però el procés continua.
    """
    threads: List[Thread] = []
    posts = get_feed(client_handle, limit=limit)
    for item in posts:
        if isinstance(item, Post) and item.author.handle == client_handle:
            post_uri = item.uri
            try:
                thread = get_thread(post_uri)
                threads.append(thread)
            except Exception as e:
                print(f"Error amb {post_uri}: {e}")
    return threads


def build_interaction_graph(threads: List[Thread], client_handle: str) -> Graph:
    """
    Genera un graf d'interacció a partir de tots els threads originals d'un usuari, fusionant-los en una sola estructura.
    Cada node representa un usuari i cada aresta indica una resposta entre usuaris dins dels threads. El pes de l'aresta reflecteix el nombre d'interaccions.
    El graf es desa automàticament en format .gt i SVG a la carpeta de resultats de l'usuari. Retorna el graf creat.
    """
    graph = Graph(directed=True)
    user_prop = graph.new_vertex_property("string")
    weight_prop = graph.new_edge_property("int")
    user_to_vertex = {}

    def _get_vertex(handle: str):
        if handle not in user_to_vertex:
            v = graph.add_vertex()
            user_prop[v] = handle
            user_to_vertex[handle] = v
        return user_to_vertex[handle]

    def _explore_thread_and_add_edges(t: Thread) -> None:
        post_author_v = _get_vertex(t.post.author.handle)
        for reply in t.replies:
            reply_author_v = _get_vertex(reply.post.author.handle)
            if post_author_v == reply_author_v:
                _explore_thread_and_add_edges(reply)
                continue
            edge = graph.edge(post_author_v, reply_author_v)
            if edge is None:
                edge = graph.add_edge(post_author_v, reply_author_v)
                weight_prop[edge] = 1
            else:
                weight_prop[edge] += 1
            _explore_thread_and_add_edges(reply)

    for thread in threads:
        _explore_thread_and_add_edges(thread)

    graph.vertex_properties["user"] = user_prop
    graph.edge_properties["weight"] = weight_prop
    print(f"Nodes: {graph.num_vertices()}, Arestes: {graph.num_edges()}")

    carpeta = os.path.join("resultats", client_handle)
    os.makedirs(carpeta, exist_ok=True)
    output_gt = os.path.join(carpeta, f"{client_handle}_threads.gt")
    graph.save(output_gt)
    print(f"Graf d'interacció de threads guardat a: {output_gt}")
    try:
        output_svg = os.path.join(carpeta, f"threads_{client_handle}.svg")
        graph_draw(
            graph,
            vertex_shape="circle",
            vertex_size=8,
            edge_pen_width=1.2,
            output_size=(1200, 1200),
            bg_color="white",
            output=output_svg,
        )
        print(f"Imatge SVG del graf desada a: {output_svg}")
    except Exception as e:
        print(f"No s'ha pogut generar l'SVG: {e}")
    return graph


def main():
    """
    Permet executar el mòdul des de la línia de comandes per generar el graf d'interacció de threads d'un usuari.
    Demana el handle per entrada o com a argument, i desa els resultats a la carpeta corresponent.
    """
    import sys
    if len(sys.argv) > 1:
        client_handle = sys.argv[1].strip()
    else:
        client_handle = input(
            "Introdueix el handle de l'usuari (ex: user.bsky.social): "
        ).strip()
    threads = _get_client_threads(client_handle)
    build_interaction_graph(threads, client_handle)


if __name__ == "__main__":
    main()
