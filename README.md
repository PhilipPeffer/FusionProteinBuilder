# FusionProteinBuilder

### [Report](https://philippeffer.github.io/FusionProteinBuilder/)

## Summary

The goal of the `RTKfusion.py` script is to generate the amino acid sequence of a fusion protein specified by the user. The user enters the names of the protein Ig domains in the order in which they should be constructed, and the program retrieves their sequences from the UniProtKB database and concatenates them along with the Fc domain of IgG1 to create a fusion protein similar to VEGF-Trap.

## Dependencies

The script requires two Python packages:

1. `requests` - for making HTTP requests to the UniProt database
2. `argparse` - for parsing command-line arguments

These packages can be installed using:
```sh
pip install requests argparse
```

## Execution

Run the script using the following command:
```sh
python3 RTKfusion.py [-p] -g GENE1 IgX -g GENE2 IgY ...etc. [-o OUTFILE]
```
### Important Notes:
- The `-g` flag must precede **each** gene name. At least one gene name is required.
- An Ig domain must be specified for each gene name, separated by a space.
- The order of the genes determines the order of concatenation (N-terminus to C-terminus).
- The gene for the IgG1 Fc domain (IGHG1) is automatically added at the C-terminus.
- The signal peptide of the first argument's protein is automatically added at the N-terminus.

### Example:
```sh
python3 RTKfusion.py -g FLT1 Ig2 -g KDR Ig3
```
This generates the amino acid sequence for the fusion of VEGFR1 signal peptide (FLT1), VEGFR1 Ig-domain 2, VEGFR2 Ig-domain 3 (KDR), and IgG1 Fc domain.

### Optional Arguments:
- `-h, --help` : Show help message and exit.
- `-p, --uniprot` : Use UniProt accession IDs instead of gene names to reduce runtime.
  ```sh
  python3 RTKfusion.py -p -g P17948 Ig2 -g P35968 Ig3
  ```
  This generates the same output as the previous example.
- `-o, --outfile` : Specify the output filename/path. Without this option, the output filename follows the format: `GENE1_IgX_GENE2_IgY_fusion.fasta`.

## Outputs

1. **Fusion Protein Sequence FASTA File**
   - Default filename format: `GENE1_IgX_GENE2_IgY_fusion.fasta`.
   - The header follows the format: `>GENE1_IgX+GENE2_IgY+IgG1_Fc`.
   - The sequence consists of the signal peptide, Ig domain sequences, and IgG1 Fc domain.

2. **Terminal Summary Output**
   ```sh
   Execution Successful
   {Gene1} Signal AA (Start, End), fusion AA Start-End: AA_Sequence
   {Gene1} {Ig domain} AA (Start, End), fusion AA Start-End: AA_Sequence
   {Gene2} {Ig domain} AA (Start, End), fusion AA Start-End: AA_Sequence
   IgG1 Fc domain AA (Start, End), fusion AA Start-End: AA_Sequence
   ```
   - The first `(Start, End)` represents the original sequence position.
   - The second `Start-End` represents the fusion protein position.

### Example Output:
```
Execution Successful
VGFR1_HUMAN Signal AA (1, 26), fusion AA 1-26: MVSYWDTGVLLCALLSCLLLTGSSSG
VGFR1_HUMAN Ig2 AA (151, 214), fusion AA 27-90: GRELVIPCRVTSPNITVTLKKFPLDTLIPDGKRIIWDSRKGFIISNATYKEIGLLTCEATVNGH
VGFR2_HUMAN Ig3 AA (224, 320), fusion AA 91-187: YDVVLSPSHGIELSVGEKLVLNCTARTELNVGIDFNWEYPSSKHQHKKLVNRDLKTQSGSEMKKFLSTLTIDGVTRSDQGLYTCAASSGLMTKKNST
IgG1 Fc domain AA (104, 330), fusion AA 189-414: DKTHTCPPCPAPELLGGPSVFLFPPKPKDTLMISRTPEVTCVVVDVSHEDPEVKFNWYVDGVEVHNAKTKPREEQYNSTYRVVSVLTVLHQDWLNGKEYKCKVSNKALPAPIEKTISKAKGQPREPQVYTLPPSRDELTKNQVSLTCLVKGFYPSDIAVEWESNGQPENNYKTTPPVLDSDGSFFLYSKLTVDKSRWQQGNVFSCSVMHEALHNHYTQKSLSLSPGK
```
