from bsky import get_followers, get_relationships, Profile, Relationships
from graph_tool.all import Graph, graph_draw
import os


def build_followers_subgraph(client_handle: str) -> None:
    """
    Crea un subgraf dels seguidors d'un usuari, on cada node és un seguidor i les arestes representen relacions de seguiment entre ells.
    Desa el graf en format .gt i SVG a la carpeta de resultats de l'usuari. Mostra informació bàsica per pantalla.
    """
    followers = get_followers(client_handle)
    dids = [p.did for p in followers]
    g = Graph(directed=True)
    vprop_did = g.new_vertex_property("string")
    vprop_handle = g.new_vertex_property("string")
    g.vertex_properties["did"] = vprop_did
    g.vertex_properties["handle"] = vprop_handle
    did_a_vertex = {}
    for prof in followers:
        v = g.add_vertex()
        vprop_did[v] = prof.did
        vprop_handle[v] = prof.handle
        did_a_vertex[prof.did] = v
    for did in dids:
        rel = get_relationships(did, dids)
        v_origen = did_a_vertex[did]
        for dst_did in rel.following:
            if dst_did in did_a_vertex and did != dst_did:
                g.add_edge(v_origen, did_a_vertex[dst_did])
    print(f"Nodes: {g.num_vertices()}, Arestes: {g.num_edges()}")
    carpeta = os.path.join("resultats", client_handle)
    os.makedirs(carpeta, exist_ok=True)
    output_gt = os.path.join(carpeta, f"{client_handle}_followers.gt")
    g.save(output_gt)
    print(f"Graf guardat a: {output_gt}")
    try:
        output_svg = os.path.join(carpeta, f"seguidors_{client_handle}.svg")
        graph_draw(
            g,
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


def main() -> None:
    """
    Permet executar el mòdul des de la línia de comandes per generar el graf de seguidors d'un usuari.
    Demana el handle per entrada o com a argument, i desa els resultats a la carpeta corresponent.
    """
    import sys
    if len(sys.argv) > 1:
        client_handle = sys.argv[1].strip()
    else:
        client_handle = input(
            "Introdueix el handle de l'usuari (ex: user.bsky.social): "
        ).strip()
    build_followers_subgraph(client_handle)


if __name__ == "__main__":
    main()
