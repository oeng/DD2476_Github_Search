package dd2476.project;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

/**
 * Creates json bodies for elasticsearch POST requests.
 */
public class JsonQueryBody {

    /**
     * Creates a nested query
     * @param searchParameter the parameter to search for.
     * @param nestedType the type of nested eg, class or function.
     * @param nestedField the field to search for eg.
     * @return
     */
    public JSONObject getNestedQuery(String searchParameter, String nestedType, String nestedField) {
        JSONObject jsonQuery = new JSONObject();
        JSONObject jsonNested = new JSONObject();
        JSONObject jsonNestedQuery = new JSONObject();
        JSONObject jsonBool = new JSONObject();
        JSONArray matchConditions = new JSONArray();
        JSONObject jsonMatch = new JSONObject();
        JSONObject jsonField = new JSONObject();
        JSONObject jsonPath = new JSONObject();
        JSONObject jsonInnerHits = new JSONObject();
        JSONObject jsonIncluded = new JSONObject();
        JSONArray includedFields = new JSONArray();
        try {
            includedFields.put("filename");
            includedFields.put("filepath");
            includedFields.put("package");
            jsonIncluded.put("includes", includedFields);
            jsonQuery.put("_source", jsonIncluded);
            jsonQuery.put("query", jsonNested);
            jsonNested.put("nested", jsonPath);
            jsonPath.put("path", nestedType);
            jsonPath.put("inner_hits", jsonInnerHits);
            jsonPath.put("query", jsonNestedQuery);
            jsonNestedQuery.put("bool", jsonBool);
            jsonBool.put("must", matchConditions);
            jsonMatch.put("match", jsonField);
            jsonField.put(nestedType + "." + nestedField, searchParameter);
            matchConditions.put(jsonMatch);
        } catch (JSONException e) {
            e.printStackTrace();
        }
        return jsonQuery;
    }

    /**
     * Creates a simple query
     * @param searchParameter the parameter to search for.
     * @param field the field to search for
     * @param numResults
     * @return
     */
    public JSONObject getMatchQuery(String searchParameter, String field, Integer numResults){
        JSONObject jsonQuery = new JSONObject();
        JSONObject jsonMatch = new JSONObject();
        JSONObject jsonField = new JSONObject();
        try {
            jsonQuery.put("query", jsonMatch);
            jsonQuery.put("from", 0);
            jsonQuery.put("size", numResults);
            jsonMatch.put("match", jsonField);
            jsonField.put(field, searchParameter);
        } catch (JSONException e) {
            e.printStackTrace();
        }

        return jsonQuery;

    }

    /**
     * @param searchParameter search term, will be matched
     * @param field the field to search on eg name or start_row
     * @param filter the categories to filter
     * @param numResults
     * @return
     */
    public JSONObject getMatchQueryFilter(String searchParameter, String field, String filter, Integer numResults){
        JSONObject jsonQuery = new JSONObject();
        JSONObject jsonBool = new JSONObject();
        JSONObject jsonOptions = new JSONObject();
        JSONObject jsonMust = new JSONObject();
        JSONObject jsonFilter = new JSONObject();
        JSONObject jsonTerm = new JSONObject();
        JSONObject jsonMatch = new JSONObject();
        JSONObject jsonInnerQuery = new JSONObject();
        try {
            jsonQuery.put("query", jsonBool);
            jsonQuery.put("from", 0);
            jsonQuery.put("size", numResults);
            jsonBool.put("bool", jsonOptions);
            jsonOptions.put("must", jsonMust);
            jsonOptions.put("filter", jsonFilter);
            jsonMust.put("match", jsonMatch);
            jsonMatch.put(field, jsonInnerQuery);
            jsonInnerQuery.put("query", searchParameter);
            jsonFilter.put("term", jsonTerm);
            jsonTerm.put("category", filter);

        } catch (JSONException e) {
            e.printStackTrace();
        }
        return jsonQuery;
    }

    /**
     * @param searchParameter search term, will be matched
     * @param field the field to search on eg name or start_row
     * @param numResults
     * @return
     */
    public JSONObject getPackageQuery(String searchParameter, String field, Integer numResults) {
        JSONObject jsonQuery = new JSONObject();
        JSONObject jsonMatch = new JSONObject();
        JSONObject jsonField = new JSONObject();
        JSONObject jsonAggs1 = new JSONObject();
        JSONObject jsonPackageId = new JSONObject();
        JSONObject jsonPackageIdTerms = new JSONObject();
        JSONObject jsonPackageIdField = new JSONObject();
        JSONObject jsonAggs2 = new JSONObject();
        JSONObject jsonPackage = new JSONObject();
        JSONObject jsonPackageTerms = new JSONObject();
        JSONObject jsonPackageField = new JSONObject();
        try {
            jsonQuery.put("query", jsonMatch);
            jsonQuery.put("size", 0);
            jsonMatch.put("match", jsonField);
            jsonField.put(field, searchParameter);
            jsonQuery.put("from", 0);
            jsonQuery.put("aggs", jsonAggs1);
            jsonAggs1.put("package_id", jsonPackageId);
            jsonPackageId.put("terms", jsonPackageIdField);
            jsonPackageIdField.put("field", "package_id");
            jsonPackageIdField.put("size", numResults);
            jsonPackageId.put("aggs", jsonAggs2);
            jsonAggs2.put("package", jsonPackageTerms);
            jsonPackageTerms.put("terms", jsonPackageField);
            jsonPackageField.put("field", "package.raw");

        } catch (JSONException e) {
            e.printStackTrace();
        }
        return jsonQuery;
    }
}
