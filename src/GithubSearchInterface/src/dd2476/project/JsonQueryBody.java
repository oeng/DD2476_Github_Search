package dd2476.project;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

/**
 * Creates json bodies for elasticsearch POST requests.
 */
public class JsonQueryBody {
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
        JSONArray jsonMustOptions = new JSONArray();
        JSONArray jsonFilterOptions = new JSONArray();
        JSONObject jsonMatch = new JSONObject();
        JSONObject jsonInnerQuery = new JSONObject();
        try {
            jsonQuery.put("query", jsonBool);
            jsonQuery.put("from", 0);
            jsonQuery.put("size", numResults);
            jsonBool.put("bool", jsonOptions);
            jsonOptions.put("must", jsonMustOptions);
            jsonMustOptions.put(jsonMust);
            jsonOptions.put("filter", jsonFilterOptions);
            jsonFilterOptions.put(jsonFilter);
            jsonMust.put("match", jsonMatch);
            jsonMatch.put(field, jsonInnerQuery);
            jsonInnerQuery.put("query", searchParameter);
            jsonFilter.put("term", jsonTerm);
            jsonTerm.put("category", filter);

        } catch (JSONException e) {
            e.printStackTrace();
        }
        System.out.println(jsonQuery);
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
