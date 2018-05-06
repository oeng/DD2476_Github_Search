package dd2476.project;

import java.util.ArrayList;

public class PostingsList {
    ArrayList<PostingsEntry> postings;
    QueryType queryType;

    public PostingsList(QueryType queryType){
        this.queryType = queryType;
        postings = new ArrayList<>();
    }
    public PostingsList(){
        postings = new ArrayList<>();
    }
    public void addPostingsEntry(PostingsEntry newEntry) {
        postings.add(newEntry);
    }
    public boolean isEmpty() {
        return postings.isEmpty();
    }
}