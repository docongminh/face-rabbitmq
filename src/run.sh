while getopts d: flag
do
    case "${flag}" in
        d) dir=${OPTARG};;
    esac
done
#
image_path=()
for entry in "$dir"/*/*
do
  image_path+=($entry)
done

len=${#image_path[@]}
token=1
for((i=0; i<14; i++))
do
  if (($i>7))
  then
    j=$(( $i - 2 ))
  else
    j=$(( $i + 3 ))
  fi
  path1=${image_path[$i]}
  path2=${image_path[$j]}
  ../build/similarity $path1 $path2 /source/evaluate/result $i
done
