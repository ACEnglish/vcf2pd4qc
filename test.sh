rm -rf dist/
bash dist_cmds.sh
pip install dist/*tar.gz

vpq -h 
vpq vcf2pd -h
vpq stats -h 
vpq stats type_counter ~/mucnv_ccdg/dataframes/CCDG.chr7q11.*.jl -t 4
vpq stats size_type_counter ~/mucnv_ccdg/dataframes/CCDG.chr7q11.*.jl -t 4
