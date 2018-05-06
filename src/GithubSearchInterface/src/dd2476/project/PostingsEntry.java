package dd2476.project;

public class PostingsEntry {
    static final String REPO_PATH = "../../download_repo/";
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
        String repo = filepath.substring(14);
        return repo;
    }
    public String getFilepath() {
        String result = REPO_PATH + getRepo();
        return result;
    }
}
