import os


QUERY_FILES = 'query_files'

UNIQUE_SEARCH_DIR = lambda x: os.path.join(QUERY_FILES, str(x))

prod_res_path = lambda lib_id: "/projects/caeg/data/production/*/*/*/" + lib_id + "/*"
fastq_path = lambda flowcell_id, fastq_id: (
                            "/datasets/caeg_fastq/*/*" 
                            + flowcell_id 
                            + "*/*/" 
                            + fastq_id
                            + "*.fastq.gz"
    )

