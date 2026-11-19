
A user would upload their network data in a **networkx** file format under ["data/user_input"](./user_input/).

These files should be read using the conversion files in [src/read_and_convert_data](Network_Visualisation_Challenge/src/read_and_convert_data) and then deleted once they have been read (to ensure the program can be rerun without duplicating inputs).

We include a sample dataset in [data/example_MASLD_network](./example_MASLD_network/) which can be loaded into the user input location. Ensure that the data is duplicated into the user folder to avoid deletion -- copying of files rather than moving them should be prioritised.