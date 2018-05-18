package dd2476.project;

/**
 * Class to represent an index entry that is retrieved from elasticsearch API.
 */
class PostingsEntry {
    // Path to the root directory which all downloaded code repositories are located within.
    private static final String REPO_PATH = "download_repo/";
    String filename;
    String filepath;
    String pkg;
    String name;
    // startPos holds the starting line of the code snippet in the source file
    int startPos;
    // endPos holds the ending line of the code snippet in the source file
    int endPos;
    int packageId = -1;
    int docsInPackage = -1;

    public String toString() {
        return (pkg + " " + filename + " " + name);
    }

    /**
     * Strips away everything except the repository path from the source code file's full path.
     *
     * @return path to the repository where the source code file of this code snippet is located.
     */
    public String getRepo() {
        // Remove download_repo\
        return filepath.substring(14);
    }

    /**
     * Generates the full path to the source code file.
     *
     * @return path to the source code file of this code snippet.
     */
    public String getFilepath() {
        return REPO_PATH + getRepo();
    }
}
