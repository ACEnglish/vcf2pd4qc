rm -rf dist/
bash dist_cmds.sh
pip install dist/*tar.gz

vpq -h 
vpq vcf2pd -h
vpq stats -h 
vpq vcf2pd -p skeleton -o test.chr -r test.band.bed merge.vcf.gz
vpq vcf2pd -p generic -o test.chr -r test.band.bed merge.vcf.gz
vpq stats type_cnt test.chr1p21.1.jl blank.jl
vpq stats size_type_cnt test.chr1p21.1.jl 
vpq stats sample_gt_cnt test.chr1p21.1.jl
vpq stats qualbin_cnt test.chr1p21.1.jl
