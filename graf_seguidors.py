#!/usr/bin/env python3
import sys
from bsky import get_followers, get_relationships, get_profiles
from graph_tool.all import *

def build_followers_subgraph(client_handle: str, output_path: str) -> None:
    "Donat un client_handle i el nom del fitxer de sortida, crea un graf en "
    "gt que mostra els seguidors d'un usuari i les relacions entre ells. "

    followers = get_followers(client_handle)  # retorna llistat de Profile
    dids = [p.did for p in followers]

    g = Graph(directed=True)
    vprop_did = g.new_vertex_property("string") # propietat per guardar el did
    vprop_handle = g.new_vertex_property("string") # propietat per guardar el handle
    g.vertex_properties["did"]    = vprop_did
    g.vertex_properties["handle"] = vprop_handle

    did_a_vertex: dict[str, Vertex] = {} # diccionari de tipus {did: vertex}
    for prof in followers: # afegim els perfils al graf
        v = g.add_vertex() 
        vprop_did[v] = prof.did 
        vprop_handle[v] = prof.handle
        did_a_vertex[prof.did] = v

    # construim les arestes entre els seguidors
    for idx, did in enumerate(dids, 1): 
        rel = get_relationships(did, dids)
        v_origen = did_a_vertex[did]  
        # rel.following són els dids que 'did' segueix
        for dst_did in rel.following: 
            if dst_did in did_a_vertex:
                g.add_edge(v_origen, did_a_vertex[dst_did]) # aresta de 'did' a 'dst_did'
        # (Opcional) si vols també les relacions "followedBy",
        # iteraries rel.followedBy i faries g.add_edge(did_a_vertex[dst], v_origen)


    g.save(output_path)
    print(f"[i] Graf guardat a '{output_path}'.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Ús: {sys.argv[0]} <client_handle> <fitxer_de_sortida.gt>")
        sys.exit(1)
    client_handle = sys.argv[1]
    output_path   = sys.argv[2]
    build_followers_subgraph(client_handle, output_path)
