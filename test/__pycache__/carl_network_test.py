import networkx as nx

G = nx.Graph()

G.add_node("v_upstream_Fribrosis")
G.add_node"v_upstream_Fibrosis"
G.add_node"v_upstream_NAS"
G.add_node"v_upstream_Steatosis"
G.add_node"v_upstream_Ballooning"
G.add_node"v_upstream_diff_exp"
G.add_node"v_upstream"
G.add_node"v_downstream_Fibrosis"
G.add_node"v_downstream_NAS"
G.add_node"v_downstream_Steatosis"
G.add_node"v_downstream_Ballooning"
G.add_node"v_downstream_diff_exp"
G.add_node"v_downstream"
G.add_node"v_name"
G.add_edge("v_upstream_Fribrosis", "v_downstream_Fibrosis")
G.add_edge("v_upstream_NAS", "v_downstream_NAS")
G.add_edge("v_upstream_Steatosis", "v_downstream_Steatosis")
G.add_edge("v_upstream_Ballooning", "v_downstream_Ballooning")
G.add_edge("v_upstream_diff_exp", "v_downstream_diff_exp")