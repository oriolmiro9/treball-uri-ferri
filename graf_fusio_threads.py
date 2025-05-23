from bsky import get_feed, get_thread, Post, Thread
from graph_tool.all import Graph, graph_draw, Vertex


def build_threads_graph(client_handle: str, output_path: str, max_posts: int = 100) -> Graph:
    """
    Donat un client_handle i un camí de sortida,
    crea un graf gt agregant tots els threads del feed,
    on cada aresta (a→b) representa “qui respon → a qui es respon”
    i té un pes equal al nombre de respostes repetides.
    """
    
    posts_feed = get_feed(client_handle, limit=max_posts)
    posts = [p for p in posts_feed if isinstance(p, Post)]  # només agafem els posts originals (funció isinstance usada a bsky.py)

    g = Graph(directed=True)
    vp_did    = g.new_vertex_property("string")
    vp_handle = g.new_vertex_property("string") 
    ep_weight = g.new_edge_property("int") 
    g.vertex_properties["did"]    = vp_did
    g.vertex_properties["handle"] = vp_handle
    g.edge_properties["weight"]   = ep_weight

    did_a_vertex = {} # diccionari DID -> Vertex

    def get_vertex(did: str, handle: str)-> Vertex:
        """
        Retorna el vertex associat al did i handle donats.
        Si no existeix, el crea i l'afegeix al graf.
        """
        if did not in did_a_vertex:
            v = g.add_vertex()
            vp_did[v]    = did
            vp_handle[v] = handle
            did_a_vertex[did]   = v
        return did_a_vertex[did]

    
    for idx, post in enumerate(posts, 1):
        print(f"[{idx}/{len(posts)}] Obtenint thread de: {post.uri}")
        thread: Thread = get_thread(post.uri)
        if thread is None:
            continue

        # recorrem el thread i afegim els posts al graf
        stack = [thread]
        while stack:
            node = stack.pop()
            for reply in node.replies:
                # v_orig = qui respon, v_dst = a qui es respon
                v_orig = get_vertex(reply.post.author.did,
                                   reply.post.author.handle)
                v_dst = get_vertex(node.post.author.did,
                                   node.post.author.handle)

                e = g.edge(v_orig, v_dst)
                if e is None: # si no existeix l'aresta, la creem
                    e = g.add_edge(v_orig, v_dst)
                    ep_weight[e] = 1
                else:
                    ep_weight[e] += 1

                stack.append(reply)

    g.save(output_path)
    print(f"S'ha guardat el graf de threads a '{output_path}'")

    
    img_path = output_path.replace(".gt", ".svg")
    graph_draw(
        g, 
        bg_color=(1, 1, 1, 1),
        vertex_font_size=5,
        vertex_fill_color=(0.5, 0.5, 0.5, 0.5),
        vertex_color=(0.5, 0.5, 0.5, 0.5),
        vertex_shape="circle", 
        vertex_size=10,
        edge_color="blue",
        edge_pen_width=3,
        output_size=(1200,1200),
        output=img_path
    )
    print(f"S'ha guardat la imatge del graf a '{img_path}'")

    return g
def main() -> None:
    usuari_handle = input("Introdueix el handle de l'usuari: ") 
    fitxer_sortida = f"threads_{usuari_handle}.gt"
    build_threads_graph(usuari_handle, fitxer_sortida)

if __name__ == "__main__":
    main()