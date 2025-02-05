import requests
import argparse


# Constant Fc portion (AA 104-330) of Immunoglobulin heavy constant gamma 1 (IGHG1; UniProt P01857). Used as the C-terminus of the fusion protein.
IgG_Fc = "DKTHTCPPCPAPELLGGPSVFLFPPKPKDTLMISRTPEVTCVVVDVSHEDPEVKFNWYVDGVEVHNAKTKPREEQYNSTYRVVSVLTVLHQDWLNGKEYKCKVSNKALPAPIEKTISKAKGQPREPQVYTLPPSRDELTKNQVSLTCLVKGFYPSDIAVEWESNGQPENNYKTTPPVLDSDGSFFLYSKLTVDKSRWQQGNVFSCSVMHEALHNHYTQKSLSLSPGK"


# Retrieves the UniProt accession ID for the given gene name from the UniProt database using the API
def get_ID(gene):
    server = "https://rest.uniprot.org"
    endpoint = f"/uniprotkb/search?query=gene:{gene}+AND+organism_id:9606+AND+reviewed:true"
    parameters = {'format':'json'}

    response = requests.get(server+endpoint, params = parameters)
    assert response.status_code == 200, f"Database query ERROR: {response.status_code}"
    response = response.json()
    assert len(response['results']) != 0, "ERROR: no hits in UniProt database"
    ID = response['results'][0]['primaryAccession']
    return ID


# Retrieves the protein sequence and feature annotation data for the given UniProt accession ID from the UniProtKB database using the REST API, and returns it as a dictionary
def get_features(accession):
    server = "https://www.ebi.ac.uk/proteins/api"
    endpoint = f"/features/{accession}"
    r_headers = {'Content-Type':'application/json'}

    response = requests.get(server+endpoint, headers=r_headers)
    assert response.status_code == 200, f"ERROR: {response.status_code}"
    response = response.json()

    return response


# Given a dictionary of feature annotations from a UniProtKB entry, finds and return the AA coordinates (begin, end) of every Ig or Ig-like domain 
# that overlaps with the protein's ectodomain / extracellular domain
def IgDomains(protein_data):
    features = protein_data['features']

    ectoFound = False
    IgDomainIndex = []
    for feature in features:
        if feature['category'] == 'TOPOLOGY' and feature['description'] == "Extracellular" and not ectoFound:
            ectoStart = int(feature['begin'])
            ectoEnd = int(feature['end'])
            ectoFound = True
            continue
        if ectoFound:
            if feature['type'] == 'DOMAIN' and feature['description'].startswith("Ig"):
                start = int(feature['begin'])
                end = int(feature['end'])
                if start >= ectoStart and end <= ectoEnd:
                    IgIndex = (start,end)
                    IgDomainIndex.append(IgIndex)
    assert ectoFound, f"{protein_data[0]['entryName']} extracellular domain not found"
    assert len(IgDomainIndex) > 0, f"{protein_data[0]['entryName']} extracellular Ig domain not found"

    return IgDomainIndex


# Given a dictionary of feature annotations from a UniProtKB entry, finds and return the AA coordinates (begin, end) of every Ig or Ig-like domain 
# that overlaps with the protein's ectodomain / extracellular domain
def signalSeq(protein_data):
    features = protein_data['features']

    for feature in features:
        if feature['type'] == 'SIGNAL':
            signalStart = int(feature['begin'])
            signalEnd = int(feature['end'])
            signal_coords = (signalStart, signalEnd)
            break
    
    signal_seq = protein_data['sequence'][signalStart-1:signalEnd]
    
    return signal_coords, signal_seq




if __name__ == "__main__":
    '''
    Parse the command line arguments
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--uniprot", action='store_true', help="use this option when using UniProt IDs instead of gene names")
    parser.add_argument('-g', '--gene', nargs='+', action='append', required=True, help="specify this flag in front of each gene name (or Uniprot ID if -p used). Each gene name/ID should be followed by a space and then the Ig domain to be fused. E.g., -g GENE1 Ig2 -g GENE2 Ig1")
    parser.add_argument('-o', '--outfile', help="specify the filename/path for the output fusion protein FASTA sequence")
    args = parser.parse_args()

    # Parse the gene name from the Ig domain number and separate each into a list
    gene_list = []
    IgDom_list = []
    for gene_arg in args.gene:
        assert len(gene_arg) == 2, f"Invalid argument syntax: {gene_arg}. -g/--gene must proceed each gene"
        gene_list.append(gene_arg[0])
        Ig = gene_arg[1]
        assert Ig.startswith("Ig"), f"Invalid argument syntax, Ig Domain: {Ig}"
        IgNum = int(Ig[2:])
        assert IgNum > 0, f"Invalid domain number: {Ig}. Must be greater than zero."
        IgDom_list.append(IgNum)
    assert len(gene_list) == len(IgDom_list), f"Something went wrong. Gene list: {gene_list} size does not match Ig Domain list size: {IgDom_list}"


    
    '''
    If gene names were passed in as arguments, retrieve the UniProt accession number / ID for each gene from the UniProt database
    '''
    ID_list = []
    if not args.uniprot:
        i = 0
        while i < len(gene_list):
            # if the same gene name is used in multiple arguments, only retrieve the ID from the database once
            first_i = gene_list.index(gene_list[i])
            if first_i == i:
                ID_list.append(get_ID(gene_list[i]))
            else:
                ID_list.append(ID_list[first_i])
            i += 1
    else:
        ID_list = gene_list


    '''
    For each UniProt ID, retrieve the full list of features for the protein from the UniProt database
    '''
    protein_DB_entries = []
    i = 0
    while i < len(ID_list):
        # if the same gene name / UniProt ID is used in multiple arguments, only retrieve the features from the database once
        first_i = ID_list.index(ID_list[i])
        if first_i == i:
            protein_DB_entries.append(get_features(ID_list[i]))
        else:
            protein_DB_entries.append(protein_DB_entries[first_i])
        i += 1
 

    '''
    Extract the signal peptide sequence of the first gene/ID argument
    '''
    signal_seq = signalSeq(protein_DB_entries[0])


    '''
    For each UniProt ID, extract the full protein sequence and the AA begin/end locations of every extracellular Ig domain from the list of features for the protein
    '''
    protein_seq = []
    Ig_coords = []
    for protein in protein_DB_entries:
        protein_seq.append(protein['sequence'])
        Ig_coords.append(IgDomains(protein))
    

    '''
    For each UniProt ID, get the AA sequence of the user-specified Ig domain
    '''
    fusion_seq_list = []
    gene_num = 0
    for DomNum in IgDom_list:
        assert DomNum <= len(Ig_coords[gene_num]), f"Ig domain number entered (Ig{DomNum}) greater than number of Ig domains found ({len(Ig_coords[gene_num])}) for {gene_list[gene_num]}"
        index = Ig_coords[gene_num][DomNum-1]
        seq = protein_seq[gene_num][index[0]-1:index[1]]
        fusion_seq_list.append(seq)
        gene_num += 1


    '''
    Construct the final fusion protein
    '''
    fusion_protein = signal_seq[1]+''.join(fusion_seq_list)+IgG_Fc


    '''
    OUTPUT
    '''
    header = ">"
    outfile = ""
    i = 0
    while i < len(gene_list):   # construct the FASTA header and output filename
        header += f"{protein_DB_entries[i]['entryName']}_Ig{IgDom_list[i]}+"
        outfile += f"{protein_DB_entries[i]['entryName']}_Ig{IgDom_list[i]}_"
        i += 1
    header += "IgG1_Fc\n"

    if args.outfile:
        outfile = args.outfile
    else:
        outfile += 'fusion.fasta'

    # output fusion protein sequence to file in FASTA format  
    with open(outfile, 'w') as file:
        file.write(header)
        file.write(fusion_protein)

    # print summary to the terminal
    print("Execution Successful")
    print(f"{protein_DB_entries[0]['entryName']} Signal AA {signal_seq[0]}, fusion AA 1-{1+signal_seq[0][1]-signal_seq[0][0]}: {signal_seq[1]}")
    
    endPos = signal_seq[0][1]+1
    i = 0
    while i < len(gene_list):
        seq_len = Ig_coords[i][IgDom_list[i]-1][1] - Ig_coords[i][IgDom_list[i]-1][0]
        print(f"{protein_DB_entries[i]['entryName']} Ig{IgDom_list[i]} AA {Ig_coords[i][IgDom_list[i]-1]}, fusion AA {endPos}-{endPos+seq_len}: {fusion_seq_list[i]}")
        endPos = endPos+seq_len+1
        i += 1
    print(f"IgG1 Fc domain AA (104, 330), fusion AA {endPos+1}-{endPos+330-104}: {IgG_Fc}")