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
            // jsonField.put("functions.name", "test");
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
     * @return
     */
    public JSONObject getMatchQuery(String searchParameter, String field){
        JSONObject jsonQuery = new JSONObject();
        JSONObject jsonMatch = new JSONObject();
        JSONObject jsonField = new JSONObject();
        try {
            jsonQuery.put("query", jsonMatch);
            jsonMatch.put("match", jsonField);
            jsonField.put(field, searchParameter);
        } catch (JSONException e) {
            e.printStackTrace();
        }
        return jsonQuery;

    }
}
