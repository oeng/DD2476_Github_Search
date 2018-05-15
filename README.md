## Crawler and Indexer
Python 3 is used. Source files in src/

### Install python dependencies:
`pip install -r requirements.txt`

### To crawl and index, run:
`python -m src.Crawler`
`python -m src.Indexer`

### To evaluate
First run RelevanceScoring.py to manually rank documents with:

`python -m src.RelevanceScoring`

Enter the search term to be evaluated and then manually rank the documents based upon percieved relevance. 

The results will be saved in the folder where the filename is the search phrase entered `evaluation_results/relevance_scoring_results/`, in the format:`DOC_ID,RANK`. 

To use elasticsearch to use the relevance scores for evaluation run:

`python -m src.Evaluater`

This will read the file content of `./evaluation_results/relevance_scoring_results/` and save the json response to `evaluation_results/`

## Interface
Source files in src/GithubSearchInterface/

Java 8 with JavaFX is used.

### Dependencies:
- [richtextfx-0.9.0.jar](https://github.com/TomasMikula/RichTextFX/releases/download/v0.9.0/richtextfx-0.9.0.jar)
- [org.json.jar](http://www.java2s.com/Code/JarDownload/org.json/org.json.jar.zip) (zipped)

### Runing the interface
#### Windows
```bat
cd src\GithubSearchInterface\
if not exist classes mkdir classes
javac -cp "imports/*" -d ./classes ./src/dd2476/project/*.java
java -cp "classes;imports/*;src" dd2476.project.Main
```

#### OS X
*work in progress*

#### Linux
*work in progress*

## Project Specification

- [x] Crawl (a part of) the publicly available GitHub code.
- [x] Filter out one programming language that you feel comfortable with. (Java)
- [ ] Process the files and separate class names, method names, modifiers (for example public, private, static, final etc.), variable names – things that you may want to search and filter!
- [ ] Index it into elasticsearch (https://github.com/elastic/elasticsearch), or another search engine of your choice.
- [ ] Create an interface where you can search and filter methods or classes based on the metadata you have created.
- [ ] A sample query could be methodName:quicksort AND returnType:List<Number> i i.e. search for quicksort, and filter by methods with returnType List. What would you want to search for?


## Additional criteria, 2 needed for C, 3 needed for B etc

- [ ] The solution to the problem is novel in some respect (i.e., it has not been published before in a book, report, article or paper). A novel combination of known techniques is fine.
- [ ] The results are evaluated, preferably on realistic data, preferably using methods from the literature.
- [ ] The poster presentation is clear and understandable to another student who has not read the report or references in it.
- [ ] The report is clear, complete, technically correct, and written in grammatically correct English.
