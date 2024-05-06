//
// Check input samplesheet and get read channels
//

params.options = [:]

include { SAMPLESHEET_CHECK } from '../modules/local/samplesheet_check.nf' addParams( options: params.options )

workflow INPUT_CHECK {
    take:
    samplesheet // file: /path/to/samplesheet.csv

    main:
    SAMPLESHEET_CHECK ( samplesheet )

    SAMPLESHEET_CHECK
        .out
        .splitCsv ( header:true, sep:',' )
        .map { create_fasta_channels(it) }
        .set { sample_info }

    emit:
    sample_info // channel: [ val(meta), [ reads ] ]
}

// Function to get list of [ meta, [ fasta ] ]
def create_fasta_channels(LinkedHashMap row) {
    def meta = [:]
    meta.id         = row.sample
  //  meta.single_end = row.single_end.toBoolean()

    def array = []
    if (!file(row.fasta).exists()) {
        exit 1, "ERROR: Please check input samplesheet -> Fasta file does not exist!\n${row.fasta}"
    } else {
       array = [ meta, [ file(row.fasta) ] ]
    }
    
    return array
}
