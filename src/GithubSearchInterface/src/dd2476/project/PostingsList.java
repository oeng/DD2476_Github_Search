package dd2476.project;

import java.util.ArrayList;

/**
 * Represents a list of postings for a specific query type. Used to store the results retrieved
 * from the elasticsearch API after the user issues a query.
 */
class PostingsList {
    ArrayList<PostingsEntry> postings;
    private QueryType queryType;

    /**
     * PostingsList constructor.
     * Creates an empty PostingsList with the specified query type.
     *
     * @param queryType the type of query this postings list is associated with
     */
    public PostingsList(QueryType queryType){
        this.queryType = queryType;
        postings = new ArrayList<>();
    }

    /**
     * Adds a new postings entry to this postings list.
     *
     * @param newEntry The new postings entry to be added.
     */
    public void addPostingsEntry(PostingsEntry newEntry) {
        postings.add(newEntry);
    }
}
