package dd2476.project;

class PostingsEntry {
    private static final String REPO_PATH = "../../download_repo/";
    String filename;
    String filepath;
    String pkg;
    String name;
    int startPos;
    int endPos;
    public String toString() {
        return (pkg + " " + filename + " " + name);
    }
    public String getRepo() {
        // Remove download_repo\
        return filepath.substring(14);
    }
    public String getFilepath() {
        return REPO_PATH + getRepo();
    }
}
