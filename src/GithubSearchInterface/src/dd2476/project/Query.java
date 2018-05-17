package dd2476.project;

/**
 * Class used to store information about a query entered by the user.
 */
class Query {
    public String term;
    public QueryType type;

    /**
     * Query constructor
     * @param term the complete query string entered by the user
     * @param type the type of query, either PACKAGE, CLASSES, or FUNCTIONS
     */
    public Query(String term, QueryType type) {
        this.term = term;
        this.type = type;
    }
}
