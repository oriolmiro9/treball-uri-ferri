from graph_tool.all import load_graph, pagerank, betweenness, closeness
import pandas as pd
import matplotlib.pyplot as plt
import os
import sys
matplotlib.use("Agg")

def main(handle=None):
    if handle is None:
        if len(sys.argv) > 1:
            handle = sys.argv[1].strip()
        else:
            handle = input("Introdueix el handle de l'usuari (ex: user.bsky.social): ").strip()
    # Neteja de caràcters invisibles
    handle = handle.replace('\u200e', '').replace('\u200f', '').replace('\u202a', '').replace('\u202c', '').replace('\u202d', '').replace('\u202e', '')
    carpeta = os.path.join("resultats", handle)
    os.makedirs(carpeta, exist_ok=True)
    graf_path = os.path.join(carpeta, f"{handle}_followers.gt")
    if not os.path.isfile(graf_path):
        print(f"No s'ha trobat el graf de seguidors per a {handle}. Es genera automàticament...")
        from graf_seguidors import build_followers_subgraph
        build_followers_subgraph(handle)
        if not os.path.isfile(graf_path):
            print(f"Error: no s'ha pogut generar el graf de seguidors per a {handle}.")
            return
    g = load_graph(graf_path)
    if g.num_vertices() == 0:
        print("Error: el graf de seguidors està buit. Comprova que el handle sigui correcte i que l'usuari tingui seguidors.")
        return

    pr = pagerank(g)
    bc, _ = betweenness(g)
    cc = closeness(g)

    dades = []
    for v in g.vertices():
        dades.append({
            "id": int(v),
            "PageRank": float(pr[v]),
            "Betweenness": float(bc[v]),
            "Closeness": float(cc[v])
        })
    df = pd.DataFrame(dades)
    csv_path = os.path.join(carpeta, "centralitats_seguidors.csv")
    df.to_csv(csv_path, index=False)
    print(f"Centralitats exportades a: {csv_path}")

    print("Top 10 seguidors per PageRank:")
    print(df.sort_values(by="PageRank", ascending=False).head(10))

    # Gràfics
    plt.figure(figsize=(8,6))
    plt.scatter(df["PageRank"], df["Betweenness"], alpha=0.6)
    plt.xlabel("PageRank")
    plt.ylabel("Betweenness")
    plt.title("Reputació vs. Rol de Connector")
    plt.grid(True)
    img1 = os.path.join(carpeta, "pagerank_vs_betweenness.png")
    plt.savefig(img1)
    plt.close()

    plt.figure(figsize=(8,6))
    plt.scatter(df["PageRank"], df["Closeness"], alpha=0.6, color="orange")
    plt.xlabel("PageRank")
    plt.ylabel("Closeness")
    plt.title("Reputació vs. Centralitat de Posició")
    plt.grid(True)
    img2 = os.path.join(carpeta, "pagerank_vs_closeness.png")
    plt.savefig(img2)
    plt.close()
    print(f"Imatges generades: {img1} i {img2}")

if __name__ == "__main__":
    main()
