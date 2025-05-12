from graph_tool.all import load_graph, pagerank, betweenness, closeness
import pandas as pd
import matplotlib.pyplot as plt

# Carrega el graf
g = load_graph("grafic_seguidors.gt")

# Càlcul de les centralitats
pr = pagerank(g)
bc, _ = betweenness(g)
cc = closeness(g)

# Recollida de dades
dades = []
for v in g.vertices():
    dades.append({
        "nom": g.vp["nom"][v],  # Assegura't que tens aquest property!
        "PageRank": float(pr[v]),
        "Betweenness": float(bc[v]),
        "Closeness": float(cc[v])
    })

# Convertim a DataFrame
df = pd.DataFrame(dades)

# Desa com CSV
df.to_csv("centralitats_seguidors.csv", index=False)

# Mostra els 10 primers per PageRank
print("\n📋 Top 10 seguidors per PageRank:")
print(df.sort_values(by="PageRank", ascending=False).head(10))

# ----------- GRÀFICS DE DISPERSIÓ -------------

# PageRank vs Betweenness
plt.figure(figsize=(8,6))
plt.scatter(df["PageRank"], df["Betweenness"], alpha=0.6)
plt.xlabel("PageRank")
plt.ylabel("Betweenness")
plt.title("Reputació vs. Rol de Connector")
plt.grid(True)
plt.savefig("pagerank_vs_betweenness.png")
plt.close()

# PageRank vs Closeness
plt.figure(figsize=(8,6))
plt.scatter(df["PageRank"], df["Closeness"], alpha=0.6, color="orange")
plt.xlabel("PageRank")
plt.ylabel("Closeness")
plt.title("Reputació vs. Centralitat de Posició")
plt.grid(True)
plt.savefig("pagerank_vs_closeness.png")
plt.close()

print("\n✅ Imatges generades: pagerank_vs_betweenness.png i pagerank_vs_closeness.png")