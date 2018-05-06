package dd2476.project;

public class Query {
    public String term;
    public QueryType type;

    public Query(String term, QueryType type) {
        this.term = term;
        this.type = type;
    }
}
