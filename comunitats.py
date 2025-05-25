from graph_tool.all import *
import matplotlib.pyplot as plt
from collections import defaultdict
from graph_tool.topology import label_components, label_largest_component
import os
import sys
import matplotlib.cm as cm


def main(handle=None):
    """
    Analitza la comunitat de seguidors d'un usuari: carrega el graf, detecta components, calcula comunitats amb SBM, visualitza-les, calcula densitats i centralitats, i exporta resultats.
    Si el graf no existeix, l'intenta generar automàticament. Desa SVG, PDF i CSV a la carpeta de resultats.
    """
    # ---------------------------
    # 1. Càrrega del graf
    # ---------------------------
    if handle is None:
        handle = input(
            "Introdueix el handle de l'usuari (ex: user.bsky.social): "
        ).strip()
    # Neteja de caràcters invisibles
    handle = (
        handle.replace("\u200e", "")
        .replace("\u200f", "")
        .replace("\u202a", "")
        .replace("\u202c", "")
        .replace("\u202d", "")
        .replace("\u202e", "")
    )

    # --- Carpeta de resultats ---
    carpeta = os.path.join("resultats", handle)
    os.makedirs(carpeta, exist_ok=True)
    graf_path = os.path.join(carpeta, f"{handle}_followers.gt")
    if not os.path.isfile(graf_path):
        print(
            f"No s'ha trobat el graf de seguidors per a {handle}. Es genera automàticament..."
        )
        import subprocess

        subprocess.run(["python3", "graf_seguidors.py", handle], check=True)
        if not os.path.isfile(graf_path):
            print(f"Error: no s'ha pogut generar el graf de seguidors per a {handle}.")
            sys.exit(1)
    g = load_graph(graf_path)

    # Diagnòstic de components i densitat
    n_nodes = g.num_vertices()
    n_edges = g.num_edges()
    densitat = n_edges / (n_nodes * (n_nodes - 1)) if n_nodes > 1 else 0
    print(f"Nodes: {n_nodes}, Arestes: {n_edges}, Densitat global: {densitat:.3f}")

    # Components forts
    comp_result = label_components(g, directed=True)
    if len(comp_result) == 2:
        comp, hist = comp_result
    else:
        comp, hist, _ = comp_result
    n_comp = len(hist)
    print(f"Nombre de components forts: {n_comp}")
    if n_comp > 1:
        print(f"Nodes per component: {hist}")
    else:
        print("El graf és fortament connex.")

    # ---------------------------
    # 2. Detecció de comunitats (SBM)
    # ---------------------------
    state = minimize_blockmodel_dl(g)
    blocks = state.get_blocks()
    print(f"Nombre de comunitats trobades per SBM: {len(set(blocks.a))}")

    # ---------------------------
    # 3. Visualització amb colors per comunitat
    # ---------------------------
    block_colors = g.new_vertex_property("vector<float>")
    edge_colors = g.new_edge_property("vector<float>")
    palette = cm.get_cmap("tab20")

    for v in g.vertices():
        c = blocks[v]
        color = palette(c % 20)
        block_colors[v] = color[:3]

    for e in g.edges():
        src = int(blocks[e.source()])
        tgt = int(blocks[e.target()])
        # Si l'aresta connecta nodes de la mateixa comunitat, pinta-la del color de la comunitat
        if src == tgt:
            edge_colors[e] = palette(src % 20)[:3]
        else:
            edge_colors[e] = (0.7, 0.7, 0.7)  # gris per arestes entre comunitats

    # Ajusta la mida dels nodes segons el nombre de nodes
    n_nodes = g.num_vertices()
    if n_nodes < 50:
        vsize = 20
    elif n_nodes < 200:
        vsize = 12
    else:
        vsize = 6

    # Desa com svg i PDF només a la carpeta de resultats
    output_svg = os.path.join(carpeta, f"comunitats_{handle}.svg")
    graph_draw(
        g,
        vertex_fill_color=block_colors,
        edge_color=edge_colors,
        vertex_shape="circle",
        vertex_size=vsize,
        edge_pen_width=1.2,
        output_size=(1800, 1800),
        bg_color="white",
        output=output_svg,
    )
    print(f"Imatge svg de comunitats desada a: {output_svg}")

    # ---------------------------
    # 4. Càlcul de densitat per comunitat
    # ---------------------------
    def calcular_densitat_comunitats(g, blocs):
        comunitats = defaultdict(set)
        arestes = defaultdict(int)

        for v in g.vertices():
            comunitats[int(blocs[v])].add(v)

        for e in g.edges():
            src = int(blocs[e.source()])
            tgt = int(blocs[e.target()])
            if src == tgt:
                arestes[src] += 1

        for cid, nodes in comunitats.items():
            n = len(nodes)
            e = arestes[cid]
            densitat = (2 * e) / (n * (n - 1)) if n > 1 else 0
            print(
                f"Comunitat {cid}: {n} nodes, {e} arestes internes, densitat = {densitat:.3f}"
            )

    calcular_densitat_comunitats(g, blocks)

    # ---------------------------
    # 5. Centralitat (PageRank) dins d'una comunitat
    # ---------------------------
    def pagerank_per_comunitat(g, blocks, comunitat_id=None):
        from graph_tool.centrality import pagerank

        if comunitat_id is not None:
            comunitats = [comunitat_id]
        else:
            comunitats = set(blocks.a)

        for cid in comunitats:
            filt = g.new_vertex_property("bool")
            for v in g.vertices():
                filt[v] = blocks[v] == cid
            g.set_vertex_filter(filt)
            subgraph = Graph(g, vorder=g.vertex_index, directed=False)

            num_nodes = subgraph.num_vertices()
            num_edges = subgraph.num_edges()

            print(
                f"Comunitat {cid}: {num_nodes} nodes, {num_edges} arestes internes",
                end="",
            )

            if num_nodes > 0 and num_edges > 0:
                pr = pagerank(subgraph)
                densitat = 2 * num_edges / (num_nodes * (num_nodes - 1))
                print(f", densitat = {densitat:.3f}")
                # Si vols mostrar els PageRanks:
                for v in subgraph.vertices():
                    print(f" - node {int(v)}: PR = {pr[v]:.4f}")
            else:
                print(
                    ", comunitat buida o sense connexions — s'omet càlcul de PageRank."
                )

            g.clear_filters()

    # Exemple amb comunitat 0
    pagerank_per_comunitat(g, blocks, comunitat_id=0)

    # ---------------------------
    # 6. Detecció jeràrquica de comunitats (Nested SBM)
    # ---------------------------
    nested_state = minimize_nested_blockmodel_dl(g)
    draw_hierarchy(nested_state, output="jerarquia_comunitats.pdf")

    # ---------------------------
    # 7. Exportació de les comunitats a CSV
    # ---------------------------
    with open(os.path.join(carpeta, "comunitats.csv"), "w") as f:
        f.write("node_id,comunitat\n")
        for v in g.vertices():
            f.write(f"{int(v)},{int(blocks[v])}\n")


if __name__ == "__main__":
    main()
