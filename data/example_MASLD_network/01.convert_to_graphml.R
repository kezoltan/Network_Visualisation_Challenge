
# November 2026
# Code to read RData network files and convert to GraphML format 

library(igraph)

load("MASLD_unified_undirected_network_with_semantics.RData")

write_graph(
  MASLD_unified_undirected_network,
  file = file.path(root_dir, "MASLD_undirected_network.graphml"),
  format = "graphml")

load("MASLD_unified_directed_network_with_semantics.RData")

write_graph(
  MASLD_unified_directed_network,
  file = file.path(root_dir, "MASLD_directed_network.graphml"),
  format = "graphml")