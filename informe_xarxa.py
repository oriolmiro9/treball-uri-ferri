from fpdf import FPDF
from fpdf.svg import SVGObject
from fpdf.enums import XPos, YPos
import os
import pandas as pd
from graph_tool.all import load_graph
from graf_seguidors import build_followers_subgraph
from graf_interaccio_threads import _get_client_threads, build_interaction_graph
from comunitats import main as comunitats_main
from pagerank import main as pagerank_main

def get_input(prompt):
    try:
        return input(prompt)
    except EOFError:
        return ''

def ascii_only(text):
    # Elimina accents, diacritics i caracters no ascii
    import unicodedata
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    # Substitueix cometes tipografiques i altres simbols
    text = text.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"')
    text = text.replace('·', '-').replace('–', '-').replace('—', '-')
    return text

def main():
    print(ascii_only("=== Generador informes PDF analisi de xarxa Bluesky ==="))
    handle = ascii_only(get_input(ascii_only("Introdueix el handle de l'usuari (ex: user.bsky.social): ")).strip())
    handle = handle.replace('\u200e', '').replace('\u200f', '').replace('\u202a', '').replace('\u202c', '').replace('\u202d', '').replace('\u202e', '')
    print(ascii_only("Tipus d'analisi disponibles: seguidors, threads, comunitats, pagerank, propagacio, valuosos, completa"))
    analisi = ascii_only(get_input(ascii_only("Quina analisi vols incloure a l'informe? (separa amb comes o escriu 'completa'): ")).strip().lower())
    if analisi == 'completa':
        analisis = ['seguidors', 'threads', 'comunitats', 'pagerank', 'propagacio', 'valuosos']
    else:
        analisis = [ascii_only(a.strip()) for a in analisi.split(',') if a.strip()]

    carpeta = os.path.join("resultats", handle)
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()
    pdf.set_font("helvetica", 'B', 18)
    pdf.cell(0, 12, ascii_only(f"Informe d'analisi de xarxa: {handle}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(8)
    pdf.set_font("helvetica", '', 12)
    pdf.cell(0, 10, ascii_only(f"Analisi inclosa: {', '.join(analisis)}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(5)


    # SEGUIDORS
    if 'seguidors' in analisis:
        # --- Genera el graf de seguidors si no existeix ---
        svg_path = os.path.join(carpeta, f"seguidors_{handle}_scour.svg")
        gt_path = os.path.join(carpeta, f"{handle}_followers.gt")
        if not os.path.isfile(gt_path):
            build_followers_subgraph(handle)
        g = load_graph(gt_path)
        num_vertex = g.num_vertices()
        num_arestes = g.num_edges()
        # Comptem seguidors directes (tots els nodes del graf)
        num_seguidors = num_vertex
        # --- Inserim SVG ---
        pdf.set_font("helvetica", 'B', 14)
        pdf.cell(0, 10, ascii_only("Graf de seguidors"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        if os.path.isfile(svg_path):
            try:
                svg = SVGObject.from_file(svg_path)
                pdf.add_page()
                pdf.cell(0, 10, ascii_only(f"Graf de seguidors de {handle}:"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.ln(2)
                pdf.svg(svg, x=10, y=25, w=180)
            except Exception as e:
                pdf.cell(0, 10, ascii_only(f"No s'ha pogut inserir l'SVG: {e}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.cell(0, 10, ascii_only("Si l'SVG es corrupte, prova a netejar-lo amb: scour entrada.svg > sortida.svg"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.ln(2)
                
        else:
            pdf.cell(0, 10, ascii_only("No s'ha trobat el graf SVG de seguidors."), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(5)
        # --- Redacció automàtica ---
        pdf.set_font("helvetica", '', 10)
        pdf.multi_cell(0, 8, ascii_only(f"El graf dirigit anterior representa les connexions entre els seguidors de l'usuari {handle}. En total, te {num_vertex} vertex (dels quals {num_seguidors} son seguidors directes de {handle}). Te {num_arestes} arestes, cosa que ens porta a deduir el seguent."))
        proporcio = num_arestes / num_vertex if num_vertex > 0 else 0
        if proporcio > 1.5:
            pdf.multi_cell(0, 8, ascii_only(f"Com podem veure, hi ha moltes mes arestes que nodes, cosa que indica que gran part dels seguidors de {handle} tambe tenen relacio entre ells. Ens podria indicar tambe altres propietats i caracteristiques que estudiarem proximament."))
        else:
            pdf.multi_cell(0, 8, ascii_only(f"En aquest cas, el nombre de les arestes no supera gaire el nombre de nodes, cosa que suggereix que la majoria de seguidors de {handle} no tenen una relacio directa entre ells. Aixo pot indicar una xarxa de seguidors mes dispersa o menys cohesionada."))
        pdf.ln(5)

    # THREADS
    if 'threads' in analisis:
        pdf.set_font("helvetica", 'B', 14)
        pdf.cell(0, 10, ascii_only("Graf d'interaccio de threads"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        svg_path = os.path.join(carpeta, f"threads_{handle}.svg")
        if os.path.isfile(svg_path):
            try:
                svg = SVGObject.from_file(svg_path)
                pdf.add_page()
                pdf.cell(0, 10, ascii_only("Graf d'interaccio de threads:"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.ln(2)
                pdf.svg(svg, x=10, y=25, w=180)
            except Exception as e:
                pdf.cell(0, 10, ascii_only(f"No s'ha pogut inserir l'SVG: {e}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.cell(0, 10, ascii_only("Si l'SVG es corrupte, prova a netejar-lo amb: scour entrada.svg > sortida.svg"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.ln(2)
        else:
            pdf.cell(0, 10, ascii_only("No s'ha trobat el graf SVG de threads."), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(5)

    # COMUNITATS
    if 'comunitats' in analisis:
        pdf.set_font("helvetica", 'B', 14)
        pdf.cell(0, 10, ascii_only("Comunitats detectades (SBM)"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        svg_path = os.path.join(carpeta, f"comunitats_{handle}.svg")
        if os.path.isfile(svg_path):
            try:
                svg = SVGObject.from_file(svg_path)
                pdf.add_page()
                pdf.cell(0, 10, ascii_only("Comunitats detectades:"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.ln(2)
                pdf.svg(svg, x=10, y=25, w=180)
            except Exception as e:
                pdf.cell(0, 10, ascii_only(f"No s'ha pogut inserir l'SVG: {e}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.cell(0, 10, ascii_only("Si l'SVG es corrupte, prova a netejar-lo amb: scour entrada.svg > sortida.svg"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.ln(2)
        else:
            pdf.cell(0, 10, ascii_only("No s'ha trobat el graf SVG de comunitats."), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(5)


    # PAGERANK
    if 'pagerank' in analisis:
        pdf.set_font("helvetica", 'B', 14)
        pdf.cell(0, 10, ascii_only("Centralitats (PageRank, Betweenness, Closeness)"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        csv_path = os.path.join(carpeta, "centralitats_seguidors.csv")
        if os.path.isfile(csv_path):
            try:
                df = pd.read_csv(csv_path)
                # Si existeix la columna 'handle', la fem servir per mostrar noms
                handle_col = 'handle' if 'handle' in df.columns else 'id'
                pdf.set_font("helvetica", '', 10)
                pdf.ln(2)
                pdf.multi_cell(0, 8, ascii_only(f"El PageRank es un algoritme que ens permet classificar els usuaris del graf de seguidors de {handle} en ordre ascendent segons la seva valoracio. Aquells amb puntuacio mes alta son els que tenen mes influencia dins la xarxa, mentre que els que tenen una puntuacio mes baixa tendeixen a seguir a usuaris mes influents o tenen poca presencia."))
                # Top 5 més influents
                top = df.sort_values(by="PageRank", ascending=False).head(5)
                top_list = ", ".join([ascii_only(f"{row[handle_col]} ({row['PageRank']:.4f})") for _, row in top.iterrows()])
                pdf.multi_cell(0, 8, ascii_only(f"En el nostre cas, els usuaris amb PageRank maxim son: {top_list}. Aquests usuaris son els que considerem com a mes influents dins la xarxa. Això no nomes vol dir que tenen molts seguidors, sino que els seus seguidors tambe son usuaris influents. Es a dir, reben connexions dels usuaris que tambe tenen un alt PageRank, la qual cosa amplifica la seva importancia."))
                # Bottom 5 menys influents
                bottom = df.sort_values(by="PageRank", ascending=True).head(5)
                bottom_list = ", ".join([ascii_only(f"{row[handle_col]} ({row['PageRank']:.4f})") for _, row in bottom.iterrows()])
                pdf.multi_cell(0, 8, ascii_only(f"Per altra banda, els usuaris que tenen el PageRank mes baix son: {bottom_list}. Aquests tenen un valor mes baix a causa dels pocs seguidors que tenen o la poca influencia dels seus seguidors. Tambe pot passar que segueixin molts altres usuaris, pero no tinguin gaire presencia o reconeixement dins la xarxa."))
                pdf.ln(2)
                pdf.set_font("helvetica", '', 9)
                pdf.cell(0, 8, ascii_only("Top 10 per PageRank:"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                for _, row in df.sort_values(by="PageRank", ascending=False).head(10).iterrows():
                    pdf.cell(0, 8, ascii_only(f"{row[handle_col]}  PR: {row['PageRank']:.4f}  Betw: {row['Betweenness']:.4f}  Close: {row['Closeness']:.4f}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            except Exception as e:
                pdf.set_font("helvetica", '', 10)
                pdf.cell(0, 10, ascii_only(f"No s'ha pogut llegir el CSV: {e}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        else:
            pdf.set_font("helvetica", '', 10)
            pdf.cell(0, 10, ascii_only("No s'ha trobat el CSV de centralitats."), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        # Gràfics
        for img in ["pagerank_vs_betweenness.png", "pagerank_vs_closeness.png"]:
            img_path = os.path.join(carpeta, img)
            if os.path.isfile(img_path):
                pdf.add_page()
                pdf.cell(0, 10, ascii_only(f"{img}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.image(img_path, x=10, w=180)
        pdf.ln(5)

    # PROPAGACIO
    if 'propagacio' in analisis:
        pdf.set_font("helvetica", 'B', 14)
        pdf.cell(0, 10, ascii_only("Propagacio de threads"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        svg_path = os.path.join(carpeta, f"propagacio_{handle}.svg")
        if os.path.isfile(svg_path):
            try:
                svg = SVGObject.from_file(svg_path)
                pdf.add_page()
                pdf.cell(0, 10, ascii_only("Histograma de distancies de propagacio:"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.ln(2)
                pdf.svg(svg, x=10, y=25, w=180)
            except Exception as e:
                pdf.cell(0, 10, ascii_only(f"No s'ha pogut inserir l'SVG: {e}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.cell(0, 10, ascii_only("Si l'SVG es corrupte, prova a netejar-lo amb: scour entrada.svg > sortida.svg"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.ln(2)
        else:
            pdf.cell(0, 10, ascii_only("No s'ha trobat el SVG de propagacio."), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(5)

    # VALUOSOS
    if 'valuosos' in analisis:
        pdf.set_font("helvetica", 'B', 14)
        pdf.cell(0, 10, ascii_only("Seguidors valuosos (expansio fora del cercle)"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        csv_path = os.path.join(carpeta, f"seguidors_valuosos_{handle}.csv")
        if os.path.isfile(csv_path):
            try:
                df = pd.read_csv(csv_path)
                pdf.set_font("helvetica", '', 10)
                pdf.ln(2)
                pdf.cell(0, 8, ascii_only("Top 10 seguidors valuosos:"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                for _, row in df.sort_values(by="proporcio_expansio", ascending=False).head(10).iterrows():
                    percent = f"{row['proporcio_expansio']*100:.1f}%"
                    pdf.cell(0, 8, ascii_only(f"{row['handle']:<20}  Expansio: {percent:>6}  Respostes: {int(row['respostes_totals'])}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            except Exception as e:
                pdf.set_font("helvetica", '', 10)
                pdf.cell(0, 10, ascii_only(f"No s'ha pogut llegir el CSV: {e}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        else:
            pdf.set_font("helvetica", '', 10)
            pdf.cell(0, 10, ascii_only("No s'ha trobat el CSV de seguidors valuosos."), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(5)

    # Guarda el PDF
    out_pdf = os.path.join(carpeta, f"informe_{handle}.pdf")
    pdf.output(out_pdf)
    print(ascii_only(f"\nInforme PDF generat a: {out_pdf}"))
    print(ascii_only("Si algun SVG no es veu correctament, pots provar a netejar-lo amb: scour entrada.svg > sortida.svg"))

if __name__ == "__main__":
    main()
