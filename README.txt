#RBIF109 Final Assignment
#Author: Philip Peffer


Summary:
    The goal of the RTKfusion.py script is to generate the amino acid sequence of a fusion protein specified by the user. The user enters the names of the protein Ig domains in
    the order in which they should be constructed, and the program retrieves their sequences from the UniProtKB database and concatenates them along with the Fc domain of IgG1
    to create a fusion protein similar to VEGF-Trap.


Dependencies:
    The script requires two Python packages:
        1. requests - for making HTTP requests to the UniProt database
        2. argparse - for parsing command line arguments
    The packages can be easily installed from the command line using the command 'pip install [package]'


Execution:
    To run the script, execute the following from the command line within the directory containing the RTKfusion.py file:

        python3 RTKfusion.py [-p] -g GENE1 IgX -g GENE2 IgY ...etc. [-o OUTFILE]

        Important notes:
            -The '-g' flag must proceed EACH gene name. A minimum of one gene name must be specified. There is no maximum.
            -An Ig domain must be specified for each gene name with a space inbetween.
            -The order of the genes is important. The amino acid sequences will be concatenated in the order that the arguments appear, from N-terminus to C-terminus.
            -The gene for the IgG1 Fc domain (IGHG1) should not be added as an argument. Its sequence will automatically be added as the C-terminus to the fusion protein.
            -Additionally, the signal peptide of the first argument's protein will automatically be added proceeding the first Ig domain sequence at the N-terminus.

        Example: 'python3 RTKfusion.py -g FLT1 Ig2 -g KDR Ig3'
                    generates the amino acid sequence for the fusion of VEGFR1 signal peptide (encoded by gene FLT1), VEGFR1 Ig-domain 2, 
                    VEGFR2 (encoded by gene KDR) Ig-domain 3, and IgG1 Fc domain, from N-terminus to C-terminus (i.e. the VEGF-Trap sequence)
        
        optional arguments:
            -h, --help          show help message in terminal and exit
            -p, --uniprot       when the argument is specified, use UniProt accession IDs in place of gene names. This reduces overall runtime by decreasing the number of
                                HTTP requests made to the UniProt database (without this option, the UniProt ID must be retrieved from the database using the gene name)
                                Example usage: 'python3 RTKfusion.py -p -g P17948 Ig2 -g P35968 Ig3'
                                                    generates the same output as the example above
            -o, --outfile       specify the output filename/path for the generated fusion protein FASTA sequence. Without this option, the output filename generated is a
                                concatenation of each UniProt database entry name with the Ig# followed by "_fusion.fasta". The file is output to the current working directory.
                                For example, the output file for the example commands above would be 'VGFR1_HUMAN_Ig2_VGFR2_HUMAN_Ig3_fusion.fasta'


Outputs:
    1. Fusion protein sequence FASTA file
        -This will be output to the file specified, if the -o/--outfile argument is used. Otherwise, the output filename generated is a concatenation of each UniProt database
            entry name with the Ig# followed by "_fusion.fasta". The file is output to the current working directory. For example, the output file for the example commands
            above would be 'VGFR1_HUMAN_Ig2_VGFR2_HUMAN_Ig3_fusion.fasta'
        -The header is generated similarly to the filename, except with '+' instead of '_' between elements, and 'IgG1_Fc' in place of '_fusion.fasta'.
            For instance, the header for the example above would be '>VGFR1_HUMAN_Ig2+VGFR2_HUMAN_Ig3+IgG1_Fc'
        -The sequence itself is an amino acid sequence, created by concatenating the signal peptide sequence of the first argument's protein, the sequence of each Ig domain
            specified as an argument, followed by the sequence of the IgG1 Fc domain.

    2. Summary printed to the terminal, consisting of the following:
            "Execution Successful"
            "{UniProtKB entry name of first argument} Signal AA (BeginPos, EndPos), fusion AA BeginPos-EndPos: AA_Sequence"
            "{UniProtKB entry name of first argument} {Ig domain number} AA (BeginPos, EndPos), fusion AA BeginPos-EndPos: AA_Sequence"
            If applicable, "{UniProtKB entry name of second argument} {Ig domain number} AA (BeginPos, EndPos), fusion AA BeginPos-EndPos: AA_Sequence"
             .
             .
             .
            "IgG1 Fc domain AA (BeginPos, EndPos), fusion AA BeginPos-EndPos: AA_Sequence"
        -The first pair of start and end positions in parantheses (BeginPos, EndPos) is the position of the sequence in the original protein.
        -The second pair of start and end positions BeginPos-EndPos is the position of the sequence in the new fusion protein.
        -Example from the example commands above:
            Execution Successful
            VGFR1_HUMAN Signal AA (1, 26), fusion AA 1-26: MVSYWDTGVLLCALLSCLLLTGSSSG
            VGFR1_HUMAN Ig2 AA (151, 214), fusion AA 27-90: GRELVIPCRVTSPNITVTLKKFPLDTLIPDGKRIIWDSRKGFIISNATYKEIGLLTCEATVNGH
            VGFR2_HUMAN Ig3 AA (224, 320), fusion AA 91-187: YDVVLSPSHGIELSVGEKLVLNCTARTELNVGIDFNWEYPSSKHQHKKLVNRDLKTQSGSEMKKFLSTLTIDGVTRSDQGLYTCAASSGLMTKKNST
            IgG1 Fc domain AA (104, 330), fusion AA 189-414: DKTHTCPPCPAPELLGGPSVFLFPPKPKDTLMISRTPEVTCVVVDVSHEDPEVKFNWYVDGVEVHNAKTKPREEQYNSTYRVVSVLTVLHQDWLNGKEYKCKVSNKALPAPIEKTISKAKGQPREPQVYTLPPSRDELTKNQVSLTCLVKGFYPSDIAVEWESNGQPENNYKTTPPVLDSDGSFFLYSKLTVDKSRWQQGNVFSCSVMHEALHNHYTQKSLSLSPGK
