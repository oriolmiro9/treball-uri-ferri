#!/usr/bin/env python3
import sys
from bsky import get_posts, get_thread
from graph_tool.all import *

def build_threads_graph(client_handle: str, output_path: str, max_posts: int = 100) -> None:
    "Donat un client_handle i un nom de fitxer de sortida, crea un graf gt amb les interaccions per resposta entre usuaris."

    posts = get_posts(client_handle, max_posts=max_posts)  # retorna llistat de Post

    g = Graph(directed=True)
    vprop_did = g.new_vertex_property("string")  # propietat per guardar el DID
    vprop_handle = g.new_vertex_property("string")  # propietat per guardar el handle
    g.vertex_properties["did"] = vprop_did
    g.vertex_properties["handle"] = vprop_handle

    did_a_vertex: dict[str, Vertex] = {}  # diccionari {did: vertex}

    def get_vertex(did: str, handle: str) -> Vertex:
        "Afegeix un nou vèrtex al graf si no existeix, i retorna el vèrtex corresponent al DID."
        if did not in did_a_vertex:
            v = g.add_vertex()
            vprop_did[v] = did
            vprop_handle[v] = handle
            did_a_vertex[did] = v
        return did_a_vertex[did]

    for idx, post in enumerate(posts, 1):
        print(f"[{idx}/{len(posts)}] Analitzant post: {post.uri}")
        thread = get_thread(post.uri)
        if thread is None:
            continue

        items = thread.flatten()  # llista de Post ordenats
        for post in items:
            aut = post.author  # autor del post
            if not post.reply_to:
                continue  # només ens interessen respostes

            replied_to_post = post.reply_to
            replied_to_author = replied_to_post.author

            v_aut = get_vertex(aut.did, aut.handle)
            v_replied = get_vertex(replied_to_author.did, replied_to_author.handle)

            g.add_edge(v_aut, v_replied)  # aresta de qui respon → a qui es respon

    g.save(output_path)
    print(f"[i] Graf de respostes guardat a '{output_path}'.")

if _name_ == "_main_":
    if len(sys.argv) != 3:
        print(f"Ús: {sys.argv[0]} <client_handle> <fitxer_de_sortida.gt>")
        sys.exit(1)

    client_handle = sys.argv[1]
    output_path = sys.argv[2]

    build_threads_graph(client_handle, output_path)