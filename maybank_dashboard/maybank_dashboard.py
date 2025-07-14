import streamlit as st
import pandas as pd
import networkx as nx
import plotly.express as px
from pyvis.network import Network
import streamlit.components.v1 as components
import os
import tempfile

# Konfigurasi halaman dengan tema yang lebih profesional
st.set_page_config(
    page_title="Transaction Network Analysis", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS untuk styling dashboard seperti Power BI/Tableau
st.markdown("""
<style>
    /* Warna tema dan font */
    :root {
        --main-color: #FFC700;       /* Maybank Yellow */
        --secondary-color: #000000;  /* Black */
        --background-color: #FFFBE6; /* Soft yellow background */
        --text-color: #000000;       /* Black */
        --accent-color: #FFC700;     /* Yellow accent */
    }
    
    /* Header styling */
    .main-header {
        background-color: var(--main-color);
        color: white;
        padding: 20px;
        border-radius: 5px;
        margin-bottom: 20px;
        text-align: center;
    }
    
    /* Card styling seperti di Power BI */
    .metric-card {
        background-color: white;
        border-radius: 5px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 15px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card h4 {
        color: #000000;  /* Changed to blue */
        margin-bottom: 10px;
    }
    
    .metric-card p, .metric-card ul {
        color: #333333;  /* Darker gray for better readability */
    }
    
    .metric-card strong {
        color: #0078D4;  /* Blue for emphasis */
    }
    
    .metric-card li {
        color: #333333;  /* Darker gray for list items */
        margin-bottom: 5px;
    }
    
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        color: #0078D4;  /* Blue for values */
    }
    
    .metric-label {
        font-size: 14px;
        color: #333333;  /* Darker gray for labels */
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
    }
    
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        color: var(--main-color);
    }
    
    .metric-label {
        font-size: 14px;
        color: gray;
    }
    
    /* Styling untuk sidebar */
    .css-1d391kg, .css-12oz5g7 {
        background-color: white;
    }
    
    /* Styling untuk tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f0f0;
        border-radius: 4px 4px 0 0;
        padding: 10px 20px;
        border: none;
        transition: background-color 0.3s ease;
        color: #000000;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--main-color);
        color: black;
    }
    
    /* Styling untuk tabel */
    .dataframe {
        border: none !important;
    }
    
    .dataframe th {
        background-color: var(--main-color);
        color: white;
        font-weight: normal;
        border: none !important;
        text-align: left;
        padding: 12px 15px !important;
    }
    
    .dataframe td {
        text-align: left;
        border-bottom: 1px solid #f0f0f0 !important;
        border-left: none !important;
        border-right: none !important;
        padding: 10px 15px !important;
    }
    
    .dataframe tr:hover {
        background-color: #f5f9ff;
    }
    
    /* Styling untuk visualisasi */
    .plot-container {
        background-color: white;
        border-radius: 5px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease;
    }
    
    .plot-container:hover {
        box-shadow: 0 6px 10px rgba(0, 0, 0, 0.15);
    }
    
    /* Filter pills styling */
    .filter-pill {
        display: inline-block;
        background-color: #e6f2ff;
        border: 1px solid #0078D4;
        border-radius: 20px;
        padding: 5px 15px;
        margin-right: 10px;
        margin-bottom: 10px;
        font-size: 12px;
        color: #0078D4;
    }
    
    /* Tooltip styling */
    .tooltip {
        position: relative;
        display: inline-block;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: #555;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    
    /* Animation for loading */
    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
    
    .loading-pulse {
        animation: pulse 1.5s infinite ease-in-out;
    }
</style>
""", unsafe_allow_html=True)

# Header dengan logo dan judul (seperti di Power BI/Tableau)
st.markdown("""
<div class="main-header">
    <h1>Transaction Network Analysis Dashboard</h1>
    <p>Analisis Jaringan Transaksi untuk Akuisisi dan Retensi Nasabah</p>
</div>
""", unsafe_allow_html=True)

# Tabs untuk navigasi seperti di Power BI/Tableau
tabs = st.tabs(["📊 Dashboard", "🔍 Network Analysis",])

# Load Data
@st.cache_data
def load_data():
    df = pd.read_excel("UNAIR - GRAPH NEW.xlsx").drop_duplicates()
    def get_transaction_direction(row):
        if row['type'].upper() == 'INCOMING':
            return pd.Series({
                'source': f"{row['sender_recipient_name']} ({row['sender_recipient_bank']})",
                'target': f"{row['debitor_name']} ({row['debitor_bank']})"
            })
        elif row['type'].upper() == 'OUTGOING':
            return pd.Series({
                'source': f"{row['debitor_name']} ({row['debitor_bank']})",
                'target': f"{row['sender_recipient_name']} ({row['sender_recipient_bank']})"
            })
        return pd.Series({'source': None, 'target': None})

    df[['source', 'target']] = df.apply(get_transaction_direction, axis=1)
    graph_df = df[['source', 'target', 'amount_tx_idr', 'trx', 'type']]
    try:
        nodes_df = pd.read_csv("nodes.csv")
        edges_df = pd.read_csv("edges.csv")
    except:
        nodes_df, edges_df = None, None
    return df, graph_df, nodes_df, edges_df

df, graph_df, nodes_df, edges_df = load_data()

# Tab Dashboard
with tabs[0]:
    st.markdown("<h3 style='color: #FFFFFF;'>📊 Network Overview</h3>", unsafe_allow_html=True)
    
        # --- Metrik Ringkasan Maybank ---
    if edges_df is not None and nodes_df is not None:
        total_maybank_nodes = nodes_df[nodes_df['entity'].str.contains(r'\(B1\)', na=False)].shape[0]
        total_external_entities = nodes_df[~nodes_df['entity'].str.contains(r'\(B1\)', na=False)].shape[0]
        total_connections = edges_df.shape[0]

        incoming_amount = edges_df[
            (edges_df['type'] == 'INCOMING') &
            (edges_df['target'].str.contains(r'\(B1\)', na=False))
        ]['amount_tx_idr'].sum()

        outgoing_amount = edges_df[
            (edges_df['type'] == 'OUTGOING') &
            (edges_df['source'].str.contains(r'\(B1\)', na=False))
        ]['amount_tx_idr'].sum()
        
        total_volume = incoming_amount + outgoing_amount

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
                <div class="metric-card">
                    <h4>🧑‍💼 Nasabah Maybank Aktif</h4>
                    <div class="metric-value">{total_maybank_nodes:,}</div>
                    <div class="metric-label">Entity dengan kode (B1)</div>
                </div>
            """, unsafe_allow_html=True)
            
            
            st.markdown(f"""
                <div class="metric-card">
                    <h4>⬅️ Uang Masuk ke Maybank</h4>
                    <div class="metric-value">Rp {incoming_amount / 1_000_000_000_000:.2f} T</div>
                    <div class="metric-label">Tipe INCOMING ke (B1)</div>
                </div>
            """, unsafe_allow_html=True)


        with col2:
            st.markdown(f"""
                <div class="metric-card">
                    <h4>🌍 Entitas Eksternal</h4>
                    <div class="metric-value">{total_external_entities:,}</div>
                    <div class="metric-label">Entity non-Maybank</div>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class="metric-card">
                    <h4>➡️ Uang Keluar dari Maybank</h4>
                    <div class="metric-value">Rp {outgoing_amount / 1_000_000_000_000:.2f} T</div>
                    <div class="metric-label">Tipe OUTGOING dari (B1)</div>
                </div>
            """, unsafe_allow_html=True)


        with col3:

            st.markdown(f"""
                <div class="metric-card">
                    <h4>🔗 Total Koneksi Transaksi</h4>
                    <div class="metric-value">{total_connections:,}</div>
                    <div class="metric-label">Edge pada network</div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
                <div class="metric-card">
                    <h4>💰 Total Volume Transaksi</h4>
                    <div class="metric-value">Rp {total_volume / 1_000_000_000_000:.2f} T</div>
                    <div class="metric-label">Masuk + Keluar (Maybank)</div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("Data belum tersedia. Pastikan file 'nodes.csv' dan 'edges.csv' ada.")

    # Total uang masuk dan keluar
    incoming_amount = edges_df[edges_df['type'] == 'INCOMING']['amount_tx_idr'].sum()
    outgoing_amount = edges_df[edges_df['type'] == 'OUTGOING']['amount_tx_idr'].sum()
    
    # Identifikasi top bank partners
    bank_partners = edges_df['source'].str.extract(r'\((B\d+)\)')[0].value_counts().reset_index()
    bank_partners.columns = ['Bank', 'Count']
    bank_partners = bank_partners[bank_partners['Bank'] != 'B1']  # Exclude Maybank
    


    # --- Visualisasi: Bar & Pie & Top Bank Partners ---
    st.markdown("<h3 style='color: #FFFFFF; margin-top: 30px;'>🔍 Transaction Insights</h3>", unsafe_allow_html=True)
    col5, col6, col7 = st.columns(3)

    with col5:
        st.markdown("#### Top 5 Transaksi Tertinggi")
        top5_df = df.sort_values(by="amount_tx_idr", ascending=False).head(5)
        top5_df["label"] = top5_df.apply(lambda row: f"{row['debitor_name']} → {row['sender_recipient_name']}", axis=1)

        fig = px.bar(
            top5_df,
            x="amount_tx_idr",
            y="label",
            orientation='h',
            labels={"amount_tx_idr": "Amount (IDR)", "label": "Transaksi"},
            color_discrete_sequence=['#FFC700']
        )
        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(color="black"),
            margin=dict(l=10, r=10, t=40, b=10),
            xaxis=dict(
                title="Amount (IDR)",
                color="black",
                showgrid=True,
                gridcolor="#DADADA",
                tickfont=dict(color="black"),
                titlefont=dict(color="black")
            ),
            yaxis=dict(
                title="Debitor → Penerima",
                color="black",
                showgrid=True,
                gridcolor="#DADADA",
                tickfont=dict(color="black"),
                titlefont=dict(color="black")
            ),
            hoverlabel=dict(
                bgcolor="white",
                font=dict(color="black")
            )
        )
        fig.update_traces(
            marker=dict(
                color='#FFC700',
                line=dict(width=1.5, color='black')
            ),
            hovertemplate='<b>%{y}</b><br>Amount: %{x:,.0f} IDR'
        )
        st.plotly_chart(fig, use_container_width=True)


    # --- Distribusi Tipe Transaksi ---
    with col6:
        st.markdown("#### Distribusi Tipe Transaksi")
        type_summary = df.groupby('type').agg(
            Count=('type', 'count'),
            Total_Amount=('amount_tx_idr', 'sum')
        ).reset_index().rename(columns={'type': 'Type'})

        fig = px.pie(
            type_summary,
            values='Count',
            names='Type',
            color_discrete_sequence=['#FFC700', '#000000', '#FFDD00', '#333333']
        )
        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(l=10, r=10, t=40, b=10),
            font=dict(color="#000000"), 
            xaxis=dict(
                showgrid=True,
                gridcolor="#E5E5E5",
                color="#000000" 
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor="#E5E5E5",
                color="#000000" 
            ),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5, font=dict(color="#000000")),
            hoverlabel=dict(bgcolor="white", font_size=12, font_family="Segoe UI", font=dict(color="#000000"))
        )
        fig.update_traces(
            hovertemplate="<b>%{label}</b><br>Jumlah Transaksi: %{value}<br>Total Nominal: Rp %{customdata[0]:,.0f}<br>Persentase: %{percent}",
            customdata=type_summary[['Total_Amount']].values
        )
        st.plotly_chart(fig, use_container_width=True)

    with col7:
        st.markdown("#### Top Bank Partners")

        partner_stats = edges_df.copy()
        partner_stats['Bank'] = partner_stats['source'].str.extract(r'\((B\d+)\)')[0]

        bank_partners = (
            partner_stats.groupby('Bank')
            .agg(
                Count=('Bank', 'size'),
                Total_Amount=('amount_tx_idr', 'sum')
            )
            .reset_index()
        )
        bank_partners = bank_partners[bank_partners['Bank'] != 'B1']
        top_banks = bank_partners.sort_values('Count', ascending=False).head(10)

        fig = px.bar(
            top_banks,
            x='Bank',
            y='Count',
            labels={'Bank': 'Bank Code', 'Count': 'Number of Transactions'},
            color_discrete_sequence=['#FFC700'],
            custom_data=['Total_Amount']
        )
        fig.update_traces(
            marker=dict(line=dict(width=1.5, color='black')),
            hovertemplate="<b>Bank: %{x}</b><br>Jumlah Transaksi: %{y}<br>Total Nominal: Rp %{customdata[0]:,.0f}"
        )
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color="black"),
            margin=dict(t=40, l=10, r=10, b=10),
            xaxis=dict(
                title="Bank Code",
                color="black",
                showgrid=True,
                gridcolor="#DADADA",
                tickfont=dict(color="black"),
                titlefont=dict(color="black")
            ),
            yaxis=dict(
                title="Jumlah Transaksi",
                color="black",
                showgrid=True,
                gridcolor="#DADADA",
                tickfont=dict(color="black"),
                titlefont=dict(color="black")
            ),
            hoverlabel=dict(bgcolor="white", font=dict(color="black"))
        )
        st.plotly_chart(fig, use_container_width=True)


    # --- Visualisasi network graph (HTML-based) ---
    st.markdown("<h3 style='color: #FFFFFF; margin-top: 30px;'>🌐 Network Graph</h3>", unsafe_allow_html=True)
    vis_option = st.radio("Pilih Jenis Visualisasi:", ["Berdasarkan Nominal", "Berdasarkan Frekuensi", "Tanpa Pembobotan"], horizontal=True)

    vis_file = {
        "Berdasarkan Nominal": "nominal.html",
        "Berdasarkan Frekuensi": "frekuensi.html",
        "Tanpa Pembobotan": "struktur_unweighted.html"
    }.get(vis_option, "")

    try:
        with open(vis_file, "r", encoding="utf-8") as f:
            html_content = f.read()
        components.html(html_content, height=650, scrolling=True)
    except Exception as e:
        st.error(f"Visualisasi tidak ditemukan. Pastikan file `{vis_file}` ada di direktori.")

    # Tabel setelah network graph
    st.markdown(f"<h3 style='color: #FFFFFF; margin-top: 30px;'>📄 Top Retensi & Akuisisi {vis_option}</h3>", unsafe_allow_html=True)

    # Mapping visualisasi ke file dan sheet
    excel_data = {
        "Berdasarkan Nominal": "berdasarkan_nominal.xlsx",
        "Berdasarkan Frekuensi": "berdasarkan_frekuensi.xlsx",
        "Tanpa Pembobotan": "tanpa_pembobotan.xlsx"
    }

    selected_excel = excel_data.get(vis_option, "")
    if selected_excel:
        try:
            xl = pd.ExcelFile(selected_excel)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 🏆 Top Retensi")
                top_retensi = xl.parse(xl.sheet_names[0]).head(10)
                top_retensi.columns = ['Entity', 'Score']
                st.dataframe(top_retensi, use_container_width=True)

            with col2:
                st.markdown("#### 📈 Top Akuisisi")
                top_akuisisi = xl.parse(xl.sheet_names[1]).head(10)
                top_akuisisi.columns = ['Entity', 'Score']
                st.dataframe(top_akuisisi, use_container_width=True)

        except Exception as e:
            st.error(f"Gagal memuat data dari file: {e}")
    
    # Penjelasan & Insight Berdasarkan Pilihan
    if vis_option == "Berdasarkan Nominal":
        ret_mets = ['amt_in_deg', 'amt_betweenness', 'amt_pagerank']
        aqs_mets = ['amt_out_deg', 'amt_closeness']
        st.markdown("### ℹ️ Deskripsi: Berdasarkan Nominal")
        st.markdown("""
        - **Retensi Metrics**: Mengukur *seberapa besar nilai uang (amount)* yang masuk ke node Maybank melalui:
            - `In-Degree`: seberapa banyak uang yang diterima
            - `Betweenness`: posisi strategis dalam alur uang
            - `PageRank`: popularitas node dari aliran uang
        - **Akuisisi Metrics**: Mengukur *kemampuan node Maybank* mendorong nilai uang keluar ke jaringan lain melalui:
            - `Out-Degree`: berapa banyak uang yang ditransfer keluar
            - `Closeness`: kecepatan menjangkau node lain dalam hal nilai transaksi
        """)
        st.markdown("#### 💡 Business Insight")
        st.markdown("""
        - Nasabah dengan nilai **inflow uang besar** dan memiliki **posisi penting** berpotensi untuk dipertahankan (*retensi*).
        - Nasabah dengan nilai **outflow tinggi** dan **akses cepat** ke jaringan bisa menjadi sasaran ekspansi (*akuisisi*).
        """)

    elif vis_option == "Berdasarkan Frekuensi":
        ret_mets = ['trx_in_deg', 'trx_betweenness', 'trx_pagerank']
        aqs_mets = ['trx_out_deg','trx_closeness']
        st.markdown("### ℹ️ Deskripsi: Berdasarkan Frekuensi Transaksi")
        st.markdown("""
        - **Retensi Metrics**: Mengukur *seberapa sering transaksi masuk* ke Maybank:
            - `In-Degree`: banyaknya transaksi masuk
            - `Betweenness`: node sebagai penghubung dalam alur transaksi
            - `PageRank`: frekuensi jadi pusat transaksi
        - **Akuisisi Metrics**: Seberapa sering node menginisiasi transaksi keluar:
            - `Out-Degree`: seberapa sering mentransfer
            - `Closeness`: seberapa efisien menjangkau pihak lain secara frekuensi
        """)
        st.markdown("#### 💡 Business Insight")
        st.markdown("""
        - Nasabah dengan **frekuensi interaksi tinggi** cenderung aktif dan layak dipertahankan.
        - Nasabah dengan **banyak transaksi keluar** berpotensi menjadi agen pertumbuhan dan ekspansi.
        """)

    elif vis_option == "Tanpa Pembobotan":
        ret_mets = ['unw_in_deg', 'unw_betweenness', 'unw_pagerank']
        aqs_mets = ['unw_out_deg','unw_closeness']
        st.markdown("### ℹ️ Deskripsi: Tanpa Pembobotan (Struktur Jaringan Saja)")
        st.markdown("""
        - **Retensi Metrics**: Mengukur *struktur posisi node* tanpa memperhitungkan nilai atau frekuensi:
            - `In-Degree`: jumlah koneksi masuk
            - `Betweenness`: peran penghubung antar node
            - `PageRank`: posisi sentral dalam jaringan
        - **Akuisisi Metrics**: Fokus pada pola keluar:
            - `Out-Degree`: jumlah koneksi keluar
            - `Closeness`: kedekatan struktural dengan entitas lain
        """)
        st.markdown("#### 💡 Business Insight")
        st.markdown("""
        - Cocok untuk mengenali node penting secara **struktur**, walau nominalnya kecil.
        - Baik untuk mengidentifikasi **entitas tersembunyi** yang berperan strategis.
        """)


# Tab 2 - Network & Filters
with tabs[1]:
    st.markdown("### 🔍 Network Analysis")

    with st.expander("🎛️ Filter & Visualization Settings", expanded=True):
        # Jumlah maksimum top node disesuaikan dengan jumlah unik node
        all_nodes = pd.unique(df[['debitor_name', 'sender_recipient_name']].values.ravel('K'))
        top_n = st.slider("Jumlah Node Teratas", 5, len(all_nodes), 200)

        min_amount = float(df['amount_tx_idr'].min())
        max_amount = float(df['amount_tx_idr'].max())
        amount_range = st.slider("Rentang Nilai Transaksi", min_amount, max_amount, (min_amount, max_amount), format="%.0f")

        transaction_types = df['type'].unique().tolist()
        selected_types = st.multiselect("Tipe Transaksi", transaction_types, default=transaction_types)

    # Apply filters
    filtered_df = df[
        (df['amount_tx_idr'] >= amount_range[0]) &
        (df['amount_tx_idr'] <= amount_range[1]) &
        (df['type'].isin(selected_types))
    ]

    # Source-target column logic
    if not filtered_df.empty:
        filtered_df[['source', 'target']] = filtered_df.apply(
            lambda row: pd.Series({
                'source': f"{row['sender_recipient_name']} ({row['sender_recipient_bank']})",
                'target': f"{row['debitor_name']} ({row['debitor_bank']})"
            }) if row['type'].upper() == 'INCOMING' else pd.Series({
                'source': f"{row['debitor_name']} ({row['debitor_bank']})",
                'target': f"{row['sender_recipient_name']} ({row['sender_recipient_bank']})"
            }),
            axis=1
        )
    else:
        st.warning("⚠️ Tidak ada data yang sesuai dengan filter yang dipilih.")
        st.stop()

    filtered_graph_df = filtered_df[['source', 'target', 'amount_tx_idr', 'trx', 'type']]
    G = nx.from_pandas_edgelist(filtered_graph_df, 'source', 'target',
                                edge_attr=['amount_tx_idr', 'trx', 'type'],
                                create_using=nx.DiGraph())

    # Hitung nilai transaksi per node
    node_tx_values = {
        node: sum(d['amount_tx_idr'] for _, _, d in G.in_edges(node, data=True)) +
              sum(d['amount_tx_idr'] for _, _, d in G.out_edges(node, data=True))
        for node in G.nodes()
    }

    # Ambil top-N node
    top_nodes = sorted(node_tx_values.items(), key=lambda x: x[1], reverse=True)[:top_n]
    top_node_names = [n for n, _ in top_nodes]
    top_subgraph = G.subgraph(top_node_names)

    # Visualisasi Network
    net = Network(height="600px", width="100%", directed=True, notebook=False, bgcolor="#ffffff", font_color="#252525")

    max_tx_value = max([v for _, v in top_nodes]) if top_nodes else 1

    # Hitung degree (jumlah hubungan) per node
    node_degrees = dict(G.degree())
    max_degree = max(node_degrees.values()) if node_degrees else 1

    for node in top_node_names:
        degree = node_degrees.get(node, 0)
        size = 15 + (degree / max_degree * 100)  # skala proporsional berdasarkan degree
        color = "#FFC700" if "(B1)" in node else "#547792"
        net.add_node(node, label=node, size=size, title=node, color=color, borderWidth=2)
        
    for source, target, attr in top_subgraph.edges(data=True):
        width = 2  # Tetap
        title = f"Amount: {attr.get('amount_tx_idr', 0):,.2f} IDR\nType: {attr.get('type', 'N/A')}"
        net.add_edge(source, target, width=width, title=title, color="#0078D4", arrows={"to": {"enabled": True, "scaleFactor": 1.5}})

    net.toggle_physics(True)
    path = os.path.join(tempfile.gettempdir(), "network_graph.html")
    net.save_graph(path)
    with open(path, "r", encoding="utf-8") as f:
        components.html(f.read(), height=600)
