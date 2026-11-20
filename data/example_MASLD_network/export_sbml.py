
## Eport the directed MASLD GraphML network to SBML format with annotations for edges.
## Each graph node becomes an SBML species. 
## Edges are stored as custom annotations so their endpoints, labels and weights are retained

from pathlib import Path
import xml.etree.ElementTree as ET

## Install libSBML in the environment (python -m pip install python-libsbml)
import libsbml

## re-uses the graphml loader from load_network.py to read the MASLD network and then export it to SBML format with annotations for edges.
from load_network import load_network


## This will create an SBML level 3 version 2 document with a single compartment and one species per node in the graph.
def export_sbml(graph, output_path):
    # Create a new SBML document
    document = libsbml.SBMLDocument(3, 2)
    model = document.createModel()
    model.setId("MASLD_network")

## Create a compartment to group the exported speicies. This is a single compartment for the entire network.
## "Network" is a label for this export and has no other meaning. 
    compartment = model.createCompartment()
    compartment.setId("Network")
    compartment.setConstant(True)

## Records the mapping from each GraphMl node ID to its generated SBML ID.
## The edge export uses this mapping to refer to the correct species. 
    species_ids = {}
    for index, (node_id, attributes) in enumerate(graph.nodes(data=True), start=1):
        species_id = f"gene_{index}"
        species_ids[node_id] = species_id

## create one species per node and use its gene symbol as the name displayed. 
        species = model.createSpecies()
        species.setId(species_id)
        species.setName(attributes["name"])
        species.setCompartment("Network")

## Flags for a structural export with fixed species. 
## The graph provides no initial amounts or concentreations. This will lead to ERRORS but these are not important
        species.setHasOnlySubstanceUnits(False)
        species.setBoundaryCondition(True)
        species.setConstant(True)

## Creates a custom XML annotation to hold the edges of the network. The namesapce will identify these elments as project specific 
## network data
    annotation = ET.Element("annotation")
    network = ET.SubElement(annotation, "network", xmlns="urn:masld-project:network")

## This will keep the stored order of the endpoints and copy each edge field as text. The database labels provide the evidence
## for interpreting the realtiionship between the two genes. The weight is a numeric value that can be used to filter edges for downstream analysis.
    for source_id, target_id, attributes in graph.edges(data=True):
        edge = ET.SubElement(network, "edge", source=species_ids[source_id], target=species_ids[target_id],)
        for field, value in attributes.items():
            ET.SubElement(edge, "attribute", name=field).text = str(value)

## Convert the annotations to XML text and attach to the model. 
    annotation_xml = ET.tostring(annotation, encoding="unicode")
    if model.setAnnotation(annotation_xml) != libsbml.LIBSBML_OPERATION_SUCCESS:
        raise ValueError("Failed to set annotation for the model.")

## Write the document to the requested path and report any write failures. 
    if not libsbml.writeSBMLToFile(document, str(output_path)):
        raise OSError(f"Failed to write SBML to file: {output_path}")


## This will run the full export when this script is exectued directly. 
## other scripts can import export_sbml() and supply their own graph and output path. 
if __name__ == "__main__":
    folder = Path(__file__).resolve().parent
    graph = load_network("MASLD_directed_network.graphml")
    output_path = folder / "MASLD_network.sbml"

    export_sbml(graph, output_path)

    # read it back and check the contents
    saved = libsbml.readSBMLFromFile(str(output_path))
    saved_model = saved.getModel()
    if saved.getNumErrors() or saved_model is None:
        raise ValueError(saved.getErrorLog().toString())

## find the edge elements inside the custom network annotation. 
    annotation = ET.fromstring(saved_model.getAnnotationString())
    edges = annotation.findall(".//{urn:masld-project:network}edge")


## for the current full MASLD export, the expected values are 7,234 species and 75,625 edges. 
    print("Saved:", output_path)
    print("Species read ack:", saved_model.getNumSpecies())
    print("Annotated edges read back:", len(edges))


