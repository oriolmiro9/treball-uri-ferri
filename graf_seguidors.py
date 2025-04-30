#!/usr/bin/env python3
import sys
from bsky import get_followers, get_relationships, get_profiles
from graph_tool.all import Graph

def build_followers_subgraph(client_handle: str, output_path: str) -> None:
    "Donat un client_handle i el nom del fitxer de sortida, crea un graf en "
    followers = get_followers(client_handle)  # retorna llistat de Profile
    dids = [p.did for p in followers]
    print(f"[i] Trobats {len(dids)} seguidors.")

    # 2) Crear el graf dirigit i una propietat per guardar el DID (i opcionalment el handle)
    g = Graph(directed=True)
    vprop_did    = g.new_vertex_property("string")
    vprop_handle = g.new_vertex_property("string")
    g.vertex_properties["did"]    = vprop_did
    g.vertex_properties["handle"] = vprop_handle

    # 3) Afegir un vèrtex per a cada seguidor i omplir el dict did → vertex
    did2v = {}
    for prof in followers:
        v = g.add_vertex()
        vprop_did[v]    = prof.did
        vprop_handle[v] = prof.handle
        did2v[prof.did] = v

    # 4) Per a cada seguidor, obtenir les relacions dins el grup de dids
    print("[i] Construint arestes entre seguidors…")
    for idx, did in enumerate(dids, 1):
        rel = get_relationships(did, dids)
        src = did2v[did]
        # rel.following són els dids que 'did' segueix
        for dst_did in rel.following:
            if dst_did in did2v:
                g.add_edge(src, did2v[dst_did])
        # (Opcional) si vols també les relacions "followedBy",
        # iteraries rel.followedBy i faries g.add_edge(did2v[dst], src)

        if idx % 50 == 0 or idx == len(dids):
            print(f"    • Processats {idx}/{len(dids)} usuaris")

    # 5) Guardar el graf a disc
    print(f"[i] Guardant graf a '{output_path}'…")
    g.save(output_path)
    print("[✓] Fet!")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Ús: {sys.argv[0]} <client_handle> <fitxer_de_sortida.gt>")
        sys.exit(1)
    client_handle = sys.argv[1]
    output_path   = sys.argv[2]
    build_followers_subgraph(client_handle, output_path)
