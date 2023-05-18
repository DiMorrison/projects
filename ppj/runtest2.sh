#!/bin/bash
red=`tput setaf 1`
green=`tput setaf 2`
blue=`tput setaf 4`
reset=`tput sgr0`

tests_folder="../tests/lab2"
single_test_folder=""
single_after_test_folder="_*"
pre_input="test.san"
pre_run_file="GSA.py"
test_in_file="test.in"
test_out_file="test.out"
res_out_file="your.out"
run_file="analizator/SA.py"

for i in `seq 1 2 45`
do
    # generiraj ime direktorija s vodecom nulom
    dir=$(printf "%0*d\n" 2 $i)
    # pokreni program i provjeri izlaz
    folder_name=`ls $tests_folder | grep $single_test_folder$dir$single_after_test_folder`
    if [ "$pre_input" != "" ]
    then
      start=`date +%s`
      python3 $pre_run_file < $tests_folder/$folder_name/$pre_input
      end=`date +%s`
      runtime=$((end-start))
      if [ $runtime -gt 5 ]
      then
        echo "${red}Preprocessing took too long!${reset} - $runtime s"
      fi
    fi
    start=`date +%s`
    res=`python3 $run_file < $tests_folder/$folder_name/$test_in_file | diff $tests_folder/$folder_name/$test_out_file -`
    end=`date +%s`
    runtime=$((end-start))
    if [ $runtime -gt 5 ]
    then
      echo "${red}Runtime took too long!${reset} - $runtime s"
    fi
    if [ "$res" != "" ]
    then
        # izlazi ne odgovaraju
        echo "Test $dir ${red}FAIL${reset}"
        echo "${blue}> means your output, < means expected output${reset}"
        echo $res
        python3 $run_file < $tests_folder/$folder_name/$test_in_file > $tests_folder/$folder_name/$res_out_file
    else
        # OK!
        echo "Test $dir ${green}PASS${reset}"
    fi
done