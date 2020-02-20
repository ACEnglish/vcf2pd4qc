BASEPATH=/users/u233287/scratch/ccdg_analysis
VCFBASEPATH=/users/u233287/mucnv_ccdg/cleaned
OUTBASEPATH=/users/u233287/mucnv_ccdg/dataframes
CYTOBANDS=/users/u233287/scratch/ccdg_analysis/ref_annotations/hg38.ideo_cytoBand.txt
cat $CYTOBANDS | while read chrom start end name extra
do
    vcf_fn="${VCFBASEPATH}/CCDG.${chrom}.clean.vcf.gz"
    region="${chrom}:${start}-${end}"
    name="CCDG.${chrom}${name}.jl"
    out=${OUTBASEPATH}/${name}
    if test -f "$vcf_fn"
    then
        echo python ${BASEPATH}/VCFtoDATAFRAME.py $vcf_fn --region $region --out $out > jobs/${name}.sh
        qsub -N ${name} -o ${BASEPATH}/logs/${name}.o -e ${BASEPATH}/logs/${name}.e -A proj-dm0020 \
            -l nodes=1:ppn=1,mem=8g jobs/${name}.sh
    fi
done
