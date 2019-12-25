#!/bin/bash
### In sphinx directory and terminal, run this file:
#  ./autodoc.sh

echo "QMCPy autodoc process starts..."

echo "$(date)"

## Use pandoc to generate HTML files from REAME.md that has LaTeX expressions

cd ../..  # to go to directory QMCSoftware
pwd
DIR=python_prototype/sphinx/markdown_to_rst/
if [ ! -d $DIR ]; then
  mkdir $DIR
fi
rm DIR/*
python python_prototype/qmcpy/_util/render_readme_as_rst.py
# pandoc -s --mathjax ./README.md -o python_prototype/sphinx/markdown_to_rst/QMCSoftware.html

## Generate rst (ReStructured Text) files from notebooks
cd python_prototype

export PYTHONPATH=$PYTHONPATH:"$(pwd; cd ..)"
echo $PYTHONPATH

# run notebooks
# jupyter notebook demos/plotDemos.ipynb
cd demos
FILES=*.ipynb
DIR=../sphinx/rst_from_demos
if [ ! -d $DIR ]; then
  mkdir $DIR
fi
rm -f $DIR/*
DIRSUFFIX="_files"
for f in $FILES
do
  echo "Processing $f file..."
  jupyter-nbconvert --execute --ExecutePreprocessor.kernel_name=$CONDA_DEFAULT_ENV --ExecutePreprocessor.timeout=0 $f --to rst
  file=${f%.ipynb}
  echo $file
  cp -r "$file$DIRSUFFIX" $DIR/
done
mv *.rst $DIR

cd .. # to python_prototype

## Use sphinx to generate HTML documentation with inputs from above and
## docstrings from Python code

cd sphinx   # to return to sphinx directory

make clean;

make html

rm -fr ../../docs;  mkdir ../../docs;
cp -a _build/html/. ../../docs;

## Use sphinx to generate PDF documentation

make latex

cp -a _build/latex/qmcpy.pdf ../../docs/qmcpy.pdf

cp ../requirements.txt ../../docs

echo "QMCPy autodoc process ends..."