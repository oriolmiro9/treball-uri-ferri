from bsky import get_feed, get_thread, Thread, Post, Repost
from graph_tool.all import Graph, graph_draw, Vertex
from typing import Dict, Union, Optional, List
import re
import os

def _count_replies(thread: Thread) -> int:
    """
    Compta totes les respostes recursivament d’un thread, incloses les respostes a respostes, i així successivament.
    S'utilitza en ocasions on volem explorar tant sols els posts amb més respostes.
    """
    return sum(1 + _count_replies(r) for r in thread.replies)


def _get_post_uri(item: Union[Post, Repost]) -> Optional[str]:
    """
    Donat un item del Feed de l'usuari, extreu l'uri del post original tenint en compte que pot ser un Post o un Repost.
    """
    if isinstance(item, Repost):
        return item.post.uri
    elif isinstance(item, Post):
        return item.uri
    else:  # cas que no hauria de passar
        return None


def _get_client_threads(client_handle: str, limit: int = 500) -> List[Thread]:
    """
    A partir del handle d'un usuari de Bluesky obté cada thread del fil d'un Usuari.
    Retorna una llista d'aquests Threads.
    """
    threads: List[Thread] = []
    posts = get_feed(client_handle, limit=limit)

    for item in posts:
        post_uri = _get_post_uri(item)
        if not post_uri:  # cas que no hauria de passar
            continue
        try:
            thread = get_thread(post_uri)
            threads.append(thread)
        except Exception as e:
            print(f"Error amb {post_uri}: {e}")
    return threads


def build_interaction_graph(threads: List[Thread], client_handle: str) -> Graph:
    """
    Construeix i desa el graf d'interacció de threads (GT i SVG) a la carpeta de resultats.
    Retorna el graf creat.
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
            # Evita arestes d'autoresposta
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

    # Desa el graf GT i SVG
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
            output=output_svg
        )
        print(f"Imatge SVG del graf desada a: {output_svg}")
    except Exception as e:
        print(f"No s'ha pogut generar l'SVG: {e}")
    return graph


def main():
    import sys
    if len(sys.argv) > 1:
        client_handle = sys.argv[1].strip()
    else:
        client_handle = input("Introdueix el handle de l'usuari (ex: user.bsky.social): ").strip()
    threads = _get_client_threads(client_handle)
    build_interaction_graph(threads, client_handle)

if __name__ == "__main__":
    main()
