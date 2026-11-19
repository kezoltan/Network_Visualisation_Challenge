
# Date: November 2026
# Author: Katie Zoltan

# Code to convert .RData files into Python Networkx objects 

import networkx as nx

#Undirected network

G = nx.read_graphml("MASLD_undirected_network.graphml")
print(G.number_of_nodes())
print(G.number_of_edges())

#Directed network

G = nx.read_graphml("MASLD_directed_network.graphml")
print(G.number_of_nodes())
print(G.number_of_edges())