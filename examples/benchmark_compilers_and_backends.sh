#!/bin/bash -u

# TODO: Very experimental status
#       Translate to python and make
#       more flexible.


model=${1}
if [[ "${model}" == *xml* ]]
then
    echo "Run benchmark just on prefix (without XML)"
    exit

fi
BENCHMARK_FILE="$(readlink -f benchmark_${model}.txt)"
for compiler in intelem gfortran
do
    for backend in local_smart lat_int
    do
        export F2PY_FCOMPILER=${compiler}
        rm -rf ${model}
        echo -e "BENCHMARK ${model} ${backend} ${compiler}" >> ${BENCHMARK_FILE}
        echo "    COMPILE TIME" >> ${BENCHMARK_FILE}
        /usr/bin/time -o ${BENCHMARK_FILE} -a kmos export -b ${backend} ${model}.xml
        #cp kmc_settings.py ${model}
        #cp setup_model.py ${model}
        cd ${model}
        echo "    RUN TIME" >> ${BENCHMARK_FILE}
        for i in $(seq 3)
        do
            kmos benchmark >> ${BENCHMARK_FILE}
        done
        cd ..
        echo -e "\n\n\n" >> ${BENCHMARK_FILE}
    done
done
