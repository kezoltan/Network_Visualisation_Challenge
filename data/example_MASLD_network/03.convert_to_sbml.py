
# November 2026
# Step 3: Convert NetworkX to SBML
# MASLD Network Visualisation Challenge
#
# Full-network export with original attributes
# preserved as XML annotations.
#
# IMPORTANT:
# This is a network exchange representation,
# not a biologically validated simulation model.

from pathlib import Path
import json
import html

import networkx as nx
import libsbml


# --------------------------------------------------
# 1. Load the NetworkX network
# --------------------------------------------------

def load_network():
    """Load the directed MASLD network."""

    folder = Path(__file__).resolve().parent

    graphml_file = (
        folder / "MASLD_directed_network.graphml"
    )

    G = nx.read_graphml(graphml_file)

    print("Network loaded successfully!")
    print("Number of nodes:", G.number_of_nodes())
    print("Number of edges:", G.number_of_edges())

    return G


# --------------------------------------------------
# 2. Preserve original attributes
# --------------------------------------------------

def add_metadata(element, metadata):
    """Store original graph data as an XML annotation."""

    payload = json.dumps(
        metadata,
        ensure_ascii=True,
        default=str
    )

    annotation = (
        '<masld:metadata '
        'xmlns:masld="https://example.org/masld/metadata">'
        + html.escape(payload, quote=False)
        + '</masld:metadata>'
    )

    result = element.appendAnnotation(annotation)

    if result != libsbml.LIBSBML_OPERATION_SUCCESS:
        raise RuntimeError(
            "Failed to add metadata annotation"
        )


# --------------------------------------------------
# 3. Convert NetworkX into SBML qual
# --------------------------------------------------

def convert_to_sbml(G):
    """Convert all nodes and edges into SBML qual."""

    # Create SBML Level 3 namespaces
    namespaces = libsbml.SBMLNamespaces(3, 1)
    namespaces.addPackageNamespace("qual", 1)

    document = libsbml.SBMLDocument(namespaces)
    document.setPackageRequired("qual", True)

    # Create model
    model = document.createModel()
    model.setId("MASLD_full_network")

    # Create compartment
    compartment = model.createCompartment()
    compartment.setId("cell")
    compartment.setConstant(True)
    compartment.setSize(1.0)
    compartment.setSpatialDimensions(3)

    # Access qualitative model plugin
    qual = model.getPlugin("qual")

    if qual is None:
        raise RuntimeError(
            "SBML qual package is unavailable"
        )

    node_ids = {}

    # ----------------------------------------------
    # Create species for every node
    # ----------------------------------------------

    for index, (node, attributes) in enumerate(
        G.nodes(data=True)
    ):

        sbml_id = f"species_{index}"
        node_ids[node] = sbml_id

        species = qual.createQualitativeSpecies()

        species.setId(sbml_id)
        species.setName(
            str(attributes.get("name", node))
        )
        species.setCompartment("cell")
        species.setConstant(False)
        species.setMaxLevel(1)

        # Preserve node ID and attributes
        add_metadata(
            species,
            {
                "original_node_id": str(node),
                "attributes": attributes
            }
        )

    print("SBML species created:", len(node_ids))

    # ----------------------------------------------
    # Create transitions for every edge
    # ----------------------------------------------

    for index, (source, target, attributes) in enumerate(
        G.edges(data=True)
    ):

        transition = qual.createTransition()
        transition.setId(f"interaction_{index}")

        # Input species
        input_node = transition.createInput()
        input_node.setId(f"input_{index}")
        input_node.setQualitativeSpecies(
            node_ids[source]
        )

        input_node.setTransitionEffect(
            libsbml.INPUT_TRANSITION_EFFECT_NONE
        )

        # Unknown sign avoids assuming activation
        input_node.setSign(
            libsbml.INPUT_SIGN_UNKNOWN
        )

        # Output species
        output_node = transition.createOutput()
        output_node.setId(f"output_{index}")
        output_node.setQualitativeSpecies(
            node_ids[target]
        )

        output_node.setTransitionEffect(
            libsbml.OUTPUT_TRANSITION_EFFECT_ASSIGNMENT_LEVEL
        )

        # ------------------------------------------
        # Required SBML qualitative function terms
        # ------------------------------------------

        # A default term is required by SBML qual.
        # This assigns level 0 to the target.
        #
        # It is a technical modelling assumption,
        # NOT a verified biological mechanism.

        default_term = transition.createDefaultTerm()
        default_term.setResultLevel(0)

        # ------------------------------------------
        # Preserve original edge information
        # ------------------------------------------

        add_metadata(
            transition,
            {
                "source": str(source),
                "target": str(target),
                "attributes": attributes
            }
        )

        # Progress updates
        if (index + 1) % 10000 == 0:
            print(
                f"Processed {index + 1} edges..."
            )

    print(
        "SBML transitions created:",
        qual.getNumTransitions()
    )

    return document


# --------------------------------------------------
# 4. Display validation errors
# --------------------------------------------------

def show_validation_errors(document, maximum=5):
    """Show only the first few validation errors."""

    print(
        "\nTotal validation diagnostics:",
        document.getNumErrors()
    )

    shown = 0

    for index in range(document.getNumErrors()):

        error = document.getError(index)

        if error.getSeverity() < libsbml.LIBSBML_SEV_ERROR:
            continue

        shown += 1

        print(f"\nError {shown}")
        print("Error code:", error.getErrorId())
        print("Message:", error.getMessage())

        if shown >= maximum:
            break


# --------------------------------------------------
# 5. Validate and save SBML
# --------------------------------------------------

def save_sbml(document):
    """Validate and export the SBML document."""

    project_folder = (
        Path(__file__).resolve().parents[2]
    )

    output_folder = project_folder / "results"

    output_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        output_folder / "MASLD_full_network.xml"
    )

    print("\nValidating SBML...")

    document.checkConsistency()

    error_count = document.getNumErrors(
        libsbml.LIBSBML_SEV_ERROR
    )

    if error_count > 0:

        show_validation_errors(
            document,
            maximum=5
        )

        raise ValueError(
            f"SBML validation failed: "
            f"{error_count} errors"
        )

    print("SBML validation passed!")

    # ----------------------------------------------
    # Write SBML file
    # ----------------------------------------------

    print("\nSaving SBML...")
    print("Output path:", output_file)

    success = libsbml.writeSBMLToFile(
        document,
        str(output_file)
    )

    if not success:
        raise IOError(
            f"Failed to save SBML file: {output_file}"
        )

    print("SBML saved successfully!")

    return output_file


# --------------------------------------------------
# 6. Verify exported SBML
# --------------------------------------------------

def verify_sbml(output_file, expected_nodes, expected_edges):
    """Read the SBML file and verify counts."""

    print("\nVerifying exported SBML...")

    document = libsbml.readSBMLFromFile(
        str(output_file)
    )

    model = document.getModel()

    if model is None:
        raise ValueError(
            "Could not read the exported SBML model"
        )

    qual = model.getPlugin("qual")

    if qual is None:
        raise ValueError(
            "Exported model has no qual package"
        )

    species_count = qual.getNumQualitativeSpecies()
    transition_count = qual.getNumTransitions()

    print("Exported species:", species_count)
    print("Exported transitions:", transition_count)

    if species_count != expected_nodes:
        raise ValueError(
            "Species count does not match original network"
        )

    if transition_count != expected_edges:
        raise ValueError(
            "Transition count does not match original network"
        )

    print("Node and edge counts verified!")


# --------------------------------------------------
# 7. Main pipeline
# --------------------------------------------------

def main():

    # Load original GraphML
    G = load_network()

    # Convert the full network
    document = convert_to_sbml(G)

    # Validate and save
    output_file = save_sbml(document)

    # Verify exported counts
    verify_sbml(
        output_file,
        expected_nodes=G.number_of_nodes(),
        expected_edges=G.number_of_edges()
    )

    print("\nFull-network export completed!")


if __name__ == "__main__":
    main()
