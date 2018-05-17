# Github search

## Run using run script
Assumes no instance of elasticsearch is running.

### Install dependencies:
1. Make sure Oracle JDK (version >= 8) is installed.
2. Install python dependencies:

    `pip install -r requirements.txt`
3. Run the script and specify number of minutes to crawl (1 is enough for testing). The script will download `elasticsearch-6.2.4` if not present in the current directory, run the crawler if the directory `download_repo` is not present, start elasticsearch, run the indexer and finally launch the interface.
```bash
./run_all 1
```

## Run individual components
The crawler and indexer use Python 3. Source files are located in `src/`

Install python dependencies with:

`pip install -r requirements.txt`

The interface uses Java with JavaFX. Source files are located in `src/GithubSearchInterface/`

### Crawler
`python -m src.Crawler`

### Indexer
`python -m src.Indexer`

### To evaluate
First run RelevanceScoring.py to manually rank documents with:

`python -m src.RelevanceScoring`

Enter the search phrase, eg "quick sort" to be evaluated and then manually rank the documents based upon percieved relevance. 

The results will be saved in the folder `evaluation_results/relevance_scoring_results/`, in the format:`DOC_ID,RANK`. 

To use elasticsearch to use the relevance scores for evaluation run:

`python -m src.Evaluater`

This will read the file content of `./evaluation_results/relevance_scoring_results/` and save the json response to `evaluation_results/`

### Interface
Source files in src/GithubSearchInterface/

Java 8 with JavaFX is used.

### Dependencies:
The dependencies are included in this repository but they were downloaded from the following places.

- [richtextfx-0.9.0.jar](https://github.com/TomasMikula/RichTextFX/releases/download/v0.9.0/richtextfx-0.9.0.jar)
- [org.json.jar](http://www.java2s.com/Code/JarDownload/org.json/org.json.jar.zip) (zipped)

### Runing the interface
#### Compiling and running on Windows
```bat
cd src\GithubSearchInterface\
if not exist classes mkdir classes
javac -cp "imports/*" -d ./classes ./src/dd2476/project/*.java
java -cp "classes;imports/*;src" dd2476.project.Main
```
#### Running Jar-file on Linux
```bash
java -jar ./src/GithubSearchInterface/out/artifacts/GithubSearchInterface/GithubSearchInterface.jar
```

#### OS X
*work in progress*

### Elasticsearch
To download and extract:
```bash
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-6.2.4.tar.gz
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-6.2.4.tar.gz.sha512
shasum -a 512 -c elasticsearch-6.2.4.tar.gz.sha512 
tar -xzf elasticsearch-6.2.4.tar.gz
```
To start:
```bash
cd elasticsearch-6.2.4/bin
./elasticsearch
```
To delete the index (in case you want to re-index):
```bash
rm -rf elasticsearch-6.2.4/data/nodes/0
```

## Project Specification

- [x] Crawl (a part of) the publicly available GitHub code.
- [x] Filter out one programming language that you feel comfortable with. (Java)
- [x] Process the files and separate class names, method names, modifiers (for example public, private, static, final etc.), variable names – things that you may want to search and filter!
- [x] Index it into elasticsearch (https://github.com/elastic/elasticsearch), or another search engine of your choice.
- [x] Create an interface where you can search and filter methods or classes based on the metadata you have created.
- [x] A sample query could be methodName:quicksort AND returnType:List<Number> i i.e. search for quicksort, and filter by methods with returnType List. What would you want to search for?


## Additional criteria, 2 needed for C, 3 needed for B etc

- [ ] The solution to the problem is novel in some respect (i.e., it has not been published before in a book, report, article or paper). A novel combination of known techniques is fine.
- [ ] The results are evaluated, preferably on realistic data, preferably using methods from the literature.
- [ ] The poster presentation is clear and understandable to another student who has not read the report or references in it.
- [ ] The report is clear, complete, technically correct, and written in grammatically correct English.
