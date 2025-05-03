import sys
from bsky import get_followers, get_relationships, Profile, Relationships
from graph_tool.all import Graph, graph_draw

def build_followers_subgraph(client_handle: str) -> None:
    "Donat un client_handle i el nom del fitxer de sortida, crea un graf en "
    "gt que mostra els seguidors d'un usuari i les relacions entre ells. "

    followers: list[Profile] = get_followers(client_handle)  # retorna llistat de Profile
    dids = [p.did for p in followers]

    g = Graph(directed=True)
    vprop_did = g.new_vertex_property("string") # propietat per guardar el did
    vprop_handle = g.new_vertex_property("string") # propietat per guardar el handle
    g.vertex_properties["did"]    = vprop_did
    g.vertex_properties["handle"] = vprop_handle

    did_a_vertex = {} # diccionari de tipus {did: vertex}
    for prof in followers: # afegim els perfils al graf
        v = g.add_vertex() 
        vprop_did[v] = prof.did 
        vprop_handle[v] = prof.handle
        did_a_vertex[prof.did] = v

    # construim les arestes entre els seguidors
    for did in dids: 
        rel: Relationships = get_relationships(did, dids)
        v_origen = did_a_vertex[did]  
        # rel.following són els dids que 'did' segueix
        for dst_did in rel.following: 
            if dst_did in did_a_vertex:
                g.add_edge(v_origen, did_a_vertex[dst_did]) # aresta de 'did' a 'dst_did'
    
    
    graph_draw(
        g, 
        bg_color=(1, 1, 1, 1),
        vertex_font_size=20,
        vertex_fill_color=(0.5, 0.5, 0.5, 0.5),
        vertex_color=(0.5, 0.5, 0.5, 0.5),
        vertex_shape="square", 
        vertex_size=20,
        edge_color="blue",
        edge_pen_width=7,
        output_size=(1200,1200),
        output='bluesky.png',
    )

    #g.save(output_path)

def main()-> None:
    client_handle = "customer.bsky.social" 
    build_followers_subgraph(client_handle)

if __name__ == "__main__":
    main()
