process PLASMIDFINDER {
    tag "$meta.id"
    label 'process_low'

    // WARN: Version information not provided by tool on CLI. Please update version string below when bumping container versions.
    conda "${projectDir}/conda_environments/plasmidfinder.yml"
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/plasmidfinder:2.1.6--py310hdfd78af_1':
        'biocontainers/plasmidfinder:2.1.6--py310hdfd78af_1' }"

    input:
    tuple val(meta), path(seqs)

    output:
    tuple val(meta), path("*.json")                 , emit: json
    tuple val(meta), path("*.txt")                  , emit: txt
    path("*.tsv")                                   , emit: tsv
    tuple val(meta), path("*-hit_in_genome_seq.fsa"), emit: genome_seq
    tuple val(meta), path("*-plasmid_seqs.fsa")     , emit: plasmid_seq
    path "versions.yml"                             , emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    def args = task.ext.args ?: ''
    def prefix = task.ext.prefix ?: "${meta.id}"
    def VERSION = '2.1.6' // WARN: Version information not provided by tool on CLI. Please update this string when bumping container versions.
    """
    plasmidfinder.py \\
        $args \\
        -i $seqs \\
        -o ./ \\
        -x

    # Rename hard-coded outputs with prefix to avoid name collisions
    mv data.json ${prefix}.json
    mv results.txt ${prefix}.txt
    mv results_tab.tsv ${prefix}.tsv
    mv Hit_in_genome_seq.fsa ${prefix}-hit_in_genome_seq.fsa
    mv Plasmid_seqs.fsa ${prefix}-plasmid_seqs.fsa

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        plasmidfinder: $VERSION
    END_VERSIONS
    """
}

process COMBINE_PLASMIDFINDER {
    tag "combine plasmidfinder output"


    input:
    path(plasmidfinder_tsvs)
    


    output:
    path("combined_plasmidfinder_out.tsv"), emit: plasmidfinder


    script:
    """
    PLASMIDFINDER_FILES=(${plasmidfinder_tsvs})

    for index in \${!PLASMIDFINDER_FILES[@]}; do
    PLASMIDFINDER_FILE=\${PLASMIDFINDER_FILES[\$index]}
    
    # add header line if first file
    if [[ \$index -eq 0 ]]; then
      echo "sample\t\$(head -1 \${PLASMIDFINDER_FILE})" >> combined_plasmidfinder_out.tsv
    fi
    awk -v OFS='\\t' 'FNR>=2 { print FILENAME, \$0 }' \${PLASMIDFINDER_FILE} |  sed 's/\\.tsv//g' >> combined_plasmidfinder_out.tsv
    done

    """
}


process CUSTOM_DUMPSOFTWAREVERSIONS {

    publishDir "${params.outdir}", mode:'copy'

    input:
    path versions

    output:
    path "software_versions.yml"    , emit: yml_ch
    path "software_versions_mqc.yml", emit: mqc_yml_ch
    path "versions.yml"             , emit: versions_ch

    when:
    task.ext.when == null || task.ext.when

    script:
    def args = task.ext.args ?: ''
    template 'dumpsoftwareversions.py'
}
