package dd2476.project;

public class PostingsEntry {
    String filename;
    String filepath;
    String pkg;
    String name;
    int startRow;
    int endRow;
    public String toString() {
        return (pkg + " " + filename + " " + name);
    }
}
