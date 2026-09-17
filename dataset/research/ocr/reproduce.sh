#!/bin/sh
# Rebuild/run from retained source. Requires Python 3, CMake, a C++ compiler,
# pkg-config and Leptonica development libraries. Outputs to a NEW directory.
set -eu
if [ "$#" -ne 2 ]; then
  echo 'Usage: sh reproduce.sh SOURCE_DIR NEW_OUTPUT_DIR' >&2
  exit 2
fi
ocr_source_dir=$(cd "$1" && pwd)
ocr_output_dir=$2
ocr_script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
mkdir "$ocr_output_dir"
ocr_output_dir=$(cd "$ocr_output_dir" && pwd)
tar -xzf "$ocr_source_dir/tesseract-5.5.1.tar.gz" -C "$ocr_output_dir"
python3 "$ocr_script_dir/instrument.py" "$ocr_output_dir/tesseract-5.5.1"
cmake -S "$ocr_output_dir/tesseract-5.5.1" -B "$ocr_output_dir/build" \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTS=OFF -DBUILD_TRAINING_TOOLS=OFF \
  -DDISABLE_ARCHIVE=ON -DDISABLE_CURL=ON -DFAST_FLOAT=ON \
  -DGRAPHICS_DISABLED=ON -DOPENMP_BUILD=OFF > "$ocr_output_dir/configure.log" 2>&1
cmake --build "$ocr_output_dir/build" -j 4 > "$ocr_output_dir/build.log" 2>&1
"$ocr_output_dir/build/bin/tesseract" "$ocr_source_dir/phototest.tif" \
  "$ocr_output_dir/complete-audit" --tessdata-dir "$ocr_source_dir" \
  -l eng --oem 1 --psm 3 -c tessedit_create_txt=1 -c tessedit_create_tsv=1 \
  2> "$ocr_output_dir/complete-audit.log"
python3 "$ocr_script_dir/calculate.py" "$ocr_source_dir" \
  "$ocr_output_dir/complete-audit.log" "$ocr_output_dir/complete-audit.txt" \
  "$ocr_output_dir/calculations.json"
python3 "$ocr_script_dir/review_human.py" "$ocr_source_dir" \
  "$ocr_output_dir/human-calculations.json"
