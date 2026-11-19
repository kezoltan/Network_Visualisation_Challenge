
# November 2026
# Step 3: Convert NetworkX to SBML
# MASLD Network Visualisation Challenge

from pathlib import Path

import networkx as nx
import libsbml


# --------------------------------------------------
# 1. Load NetworkX network
# --------------------------------------------------

def load_network():
    """Load the directed MASLD network."""

    folder = Path(__file__).resolve().parent

    graphml_file = folder / "MASLD_directed_network.graphml"

    G = nx.read_graphml(graphml_file)

    print("Network loaded successfully!")
    print("Number of nodes:", G.number_of_nodes())
    print("Number of edges:", G.number_of_edges())

    return G


# --------------------------------------------------
# 2. Select interactions
# --------------------------------------------------

def select_interactions(G, limit=100):
    """Select OmniPath directed stimulation interactions."""

    selected = []

    for source, target, attributes in G.edges(data=True):

        interaction = str(
            attributes.get("OmniPath", "NA")
        )

        labels = [
            label.strip()
            for label in interaction.split("&")
        ]

        if "directed_stimulation" in labels:
            selected.append((source, target))

        if len(selected) >= limit:
            break

    print("Selected interactions:", len(selected))

    return selected


# --------------------------------------------------
# 3. Create SBML qualitative model
# --------------------------------------------------

def create_sbml_qual(G, interactions):
    """Create an SBML Level 3 qualitative model."""

    # Create SBML namespaces
    namespaces = libsbml.SBMLNamespaces(3, 1)
    namespaces.addPackageNamespace("qual", 1)

    document = libsbml.SBMLDocument(namespaces)

    document.setPackageRequired("qual", True)

    # Create model
    model = document.createModel()
    model.setId("MASLD_qual_model")

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

    # ----------------------------------------------
    # Create qualitative species
    # ----------------------------------------------

    nodes = set()

    for source, target in interactions:
        nodes.add(source)
        nodes.add(target)

    for node in sorted(nodes):

        species = qual.createQualitativeSpecies()

        species.setId(str(node))
        species.setName(
            str(G.nodes[node].get("name", node))
        )
        species.setCompartment("cell")
        species.setConstant(False)
        species.setMaxLevel(1)

    print("Qualitative species created:", len(nodes))

    # ----------------------------------------------
    # Create qualitative transitions
    # ----------------------------------------------

    for index, (source, target) in enumerate(interactions):

        transition = qual.createTransition()
        transition.setId(f"transition_{index}")

        # Input species
        input_node = transition.createInput()
        input_node.setId(f"input_{index}")
        input_node.setQualitativeSpecies(str(source))

        input_node.setTransitionEffect(
            libsbml.INPUT_TRANSITION_EFFECT_NONE
        )

        input_node.setSign(
            libsbml.INPUT_SIGN_POSITIVE
        )

        input_node.setThresholdLevel(1)

        # Output species
        output_node = transition.createOutput()
        output_node.setId(f"output_{index}")
        output_node.setQualitativeSpecies(str(target))

        output_node.setTransitionEffect(
            libsbml.OUTPUT_TRANSITION_EFFECT_ASSIGNMENT_LEVEL
        )

        # Default term: target inactive
        default_term = transition.createDefaultTerm()
        default_term.setResultLevel(0)

        # Function term: target active
        function_term = transition.createFunctionTerm()
        function_term.setResultLevel(1)

        math = libsbml.parseL3Formula(
            f"geq({source}, 1)"
        )

        if math is None:
            raise ValueError(
                f"Could not create math for {source}"
            )

        function_term.setMath(math)

    print("Transitions created:", len(interactions))

    return document


# --------------------------------------------------
# 4. Validate and save SBML
# --------------------------------------------------

def save_sbml(document):
    """Validate and save the SBML document."""

    # Find the main project directory
    project_folder = Path(__file__).resolve().parents[2]

    # Create results directory
    output_folder = project_folder / "results"
    output_folder.mkdir(parents=True, exist_ok=True)

    output_file = output_folder / "MASLD_qual.xml"

    print("\nValidating SBML...")

    # Check SBML consistency
    document.checkConsistency()

    error_count = document.getNumErrors(
        libsbml.LIBSBML_SEV_ERROR
    )

    if error_count > 0:
        document.printErrors()
        raise ValueError(
            f"SBML validation failed with {error_count} errors"
        )

    print("SBML validation passed!")

    # Save SBML
    print("\nSaving SBML...")
    print("Output path:", output_file)

    result = libsbml.writeSBMLToFile(
        document,
        str(output_file)
    )

    # writeSBMLToFile returns True on success
    if not result:
        raise IOError(
            f"Failed to save SBML file: {output_file}"
        )

    print("\nSBML conversion successful!")
    print("Saved to:", output_file)

    return output_file


# --------------------------------------------------
# 5. Main pipeline
# --------------------------------------------------

def main():

    # Step 1: Load NetworkX graph
    G = load_network()

    # Step 2: Select interactions
    interactions = select_interactions(
        G,
        limit=100
    )

    if not interactions:
        raise ValueError(
            "No suitable interactions found"
        )

    # Step 3: Convert to SBML
    document = create_sbml_qual(
        G,
        interactions
    )

    # Step 4: Validate and save
    save_sbml(document)


if __name__ == "__main__":
    main()
