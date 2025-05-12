from graph_tool.all import *
import matplotlib.pyplot as plt
from collections import defaultdict

# ---------------------------
# 1. Càrrega del graf
# ---------------------------
g = load_graph("seguidors_customer.bsky.social.gt")

# ---------------------------
# 2. Detecció de comunitats (SBM)
# ---------------------------
state = minimize_blockmodel_dl(g) 
blocks = state.get_blocks()

# ---------------------------
# 3. Visualització amb colors per comunitat
# ---------------------------
block_colors = g.new_vertex_property("vector<float>")
palette = plt.get_cmap("tab20")

for v in g.vertices():
    c = blocks[v]
    color = palette(c % 20)
    block_colors[v] = color[:3]

graph_draw(g,
           vertex_fill_color=block_colors,
           output_size=(800, 800),
           output="comunitats_sbm.pdf")

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
        print(f"Comunitat {cid}: {n} nodes, {e} arestes internes, densitat = {densitat:.3f}")

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
            filt[v] = (blocks[v] == cid)
        g.set_vertex_filter(filt)
        subgraph = Graph(g, vorder=g.vertex_index, directed=False)

        num_nodes = subgraph.num_vertices()
        num_edges = subgraph.num_edges()

        print(f"Comunitat {cid}: {num_nodes} nodes, {num_edges} arestes internes", end="")

        if num_nodes > 0 and num_edges > 0:
            pr = pagerank(subgraph)
            densitat = 2 * num_edges / (num_nodes * (num_nodes - 1))
            print(f", densitat = {densitat:.3f}")
            # Si vols mostrar els PageRanks:
            for v in subgraph.vertices():
                print(f" - node {int(v)}: PR = {pr[v]:.4f}")
        else:
            print(", comunitat buida o sense connexions — s'omet càlcul de PageRank.")

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
with open("comunitats.csv", "w") as f:
    f.write("node_id,comunitat\n")
    for v in g.vertices():
        f.write(f"{int(v)},{int(blocks[v])}\n")