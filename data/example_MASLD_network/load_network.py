## This will hopefully open the directed MASLD network from the
## graphml file. The scrpit can be run to inspect the network or 
## import its functions to another script to use the network in a more programmatic way.

# Step 1 - Check files are in right place
# data - example_MASLD_network - check that the following files are in the folder
# 1 load_network.py
# 2 MASLD_directed_network.graphml

from collections import Counter
from pathlib import Path

# ensure networkx is installed in your environment (python -m pip install networkx)
import networkx as nx

## Load the GraphML file and return the network as a NetworkX graph object
def load_network(filename):
    ## read graphml file from the same folder as this script
    folder = Path(__file__).resolve().parent
    return nx.read_graphml(folder / filename)

## Find the internal node IDs for an exact gene symbol
def find_gene_nodes(graph, gene_name):
    matching_ids = []
    for node_id, attributes in graph.nodes(data=True):
        ## the "name" attrubute holds the gene symbol. while node_id hold an ID e.g. n1
        if attributes.get("name") == gene_name:
            matching_ids.append(node_id)
    ## this will return all matches or an empty list if symbol is absent
    return matching_ids


## run the below checks when the script is run directly. 
## other scripts can imprt the functions above
if __name__ == "__main__":
    graph = load_network("MASLD_directed_network.graphml")
## basic over view (descriptive) of the network including directionality
    print("Nodes:", graph.number_of_nodes())
    print("Edges:", graph.number_of_edges())
    print("Directed:", graph.is_directed())


## look up two known genes in the network to check that the search uses the correct attribute.
    gene_name = "IL20RA"
    il20ra_ids = find_gene_nodes(graph, "IL20RA")
    il20rb_ids = find_gene_nodes(graph, "IL20RB")


## for this specific export the expected result is that there is n1 for IL20RA and n0 for IL20RB
    print("Matching node IDs for IL20RA:", il20ra_ids)
    print("Matching node IDs for IL20RB:", il20rb_ids)

## this will check that each gene has one match before taking the first ID from each list
    if len(il20ra_ids) == 1 and len(il20rb_ids) == 1:
        source_id = il20ra_ids[0]
        target_id = il20rb_ids[0]
## Looks yp the edge in the stored source to target direction. For this par the path label "complex" is indicative that
## shared complex membership. 
        print("IL20RA node attributes:", graph.nodes[source_id])

        edge_attributes = graph.get_edge_data(source_id, target_id)
        print("Edge attributes from IL20RA to IL20RB:", edge_attributes)
    else:
        print("Expected exactly one node for each gene.")

## Count how often each exac OmniPath label appears in the graph. 
    omnipath_counts = Counter()
    for source_id, target_id, edge_attributes in graph.edges(data=True):
        label = edge_attributes.get("OmniPath", "NA")
        omnipath_counts[label] += 1

## print labels from most to least common. Combined labels are counted as a written in the file. 
    print("\nOmniPath label counts in this graph:")
    for label, count in omnipath_counts.most_common():
        print(f"{label}: {count}")

## find one example edge for each of the two labels below 
    for wanted_label in ("directed_stimulation", "directed"):
        for source_id, target_id, edge_attributes in graph.edges(data=True):
            if edge_attributes.get("OmniPath") == wanted_label:
                source_gene = graph.nodes[source_id]["name"]
                target_gene = graph.nodes[target_id]["name"]

                print(f"\nExample of {wanted_label}")
                print(f"{source_gene} ({source_id}) -> {target_gene} ({target_id})")
                print(edge_attributes)
                ## stop searching after the first match then move to the next label. 
                break