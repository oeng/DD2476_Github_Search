package dd2476.project;

import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.scene.control.*;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLConnection;
import java.sql.SQLOutput;
import java.util.ArrayList;
import java.util.List;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

public class Controller {
    final static String INDEX_NAME = "test";
    final static String ES_URL = "http://localhost:9200/";

    @FXML
    ListView<PostingsEntry> resultsListView;
    @FXML
    TextField queryField;
    @FXML
    Label infoLabel;
    @FXML
    ToggleGroup toggleGroup;
    @FXML
    RadioMenuItem functionSearchRadio;
    @FXML
    RadioMenuItem classSearchRadio;
    @FXML
    RadioMenuItem packageSearchRadio;

    @FXML
    public void initialize() {
        infoLabel.setText("Press enter to search");
    }

    private void openResultEntry(PostingsEntry entry) {
        // TODO: Display the method/function/class/file when user clicks an entry in the result list.
        // Should it open in a new window?
        // For method/function display only the method/function?
        // For class, display entire class?
        // For package, display entire file?
    }

    private void updateListView(PostingsList plist) {
        resultsListView.getItems().clear();
        resultsListView.getItems().addAll(plist.postings);
    }

    private PostingsList search(Query query) {
        PostingsList searchResults = new PostingsList(query.type);
        URL queryURL;
        String key = "";
        if (query.type == QueryType.FUNCTIONS || query.type == QueryType.CLASSES) {
            key = "?q="+query.type.name().toLowerCase()+".name:"+query.term;
        } else if (query.type == QueryType.PACKAGE) {
            key = "?q="+query.type.name().toLowerCase()+":"+query.term;
        }
        try {
            queryURL = new URL(ES_URL + INDEX_NAME + "/_search/" + key);
            URLConnection conn = queryURL.openConnection();
            BufferedReader in = new BufferedReader(new InputStreamReader(conn.getInputStream(), "UTF8"));
            StringBuilder response = new StringBuilder();
            String inputLine;

            while ((inputLine = in.readLine()) != null) {
                response.append(inputLine);
            }
            in.close();

            JSONObject jsonObject = new JSONObject(response.toString());
            JSONObject hitsObject = jsonObject.getJSONObject("hits");
            int nrofHits = hitsObject.getInt("total");

            if (nrofHits > 0) {
                JSONArray hitsArray = hitsObject.getJSONArray("hits");
                for (int i = 0; i < hitsArray.length(); ++i) {
                    JSONObject hitObject = hitsArray.getJSONObject(i);
                    JSONObject _sourceObject = hitObject.getJSONObject("_source");
                    String filename = _sourceObject.getString("filename");
                    String filepath = _sourceObject.getString("filepath");
                    String pkg = _sourceObject.getString("package");
                    JSONArray functions = _sourceObject.getJSONArray("functions");
                    JSONArray classes = _sourceObject.getJSONArray("classes");

                    if (query.type == QueryType.FUNCTIONS) {
                        for (int j = 0; j < functions.length(); ++j) {
                            PostingsEntry foundEntry = new PostingsEntry();
                            JSONObject function = functions.getJSONObject(j);
                            foundEntry.filename = filename;
                            foundEntry.filepath = filepath;
                            foundEntry.pkg = pkg;
                            foundEntry.name = function.getString("name");
                            foundEntry.startRow = function.getInt("row");
                            searchResults.addPostingsEntry(foundEntry);
                        }

                    } else if (query.type == QueryType.CLASSES) {
                        for (int j = 0; j < classes.length(); ++j) {
                            PostingsEntry foundEntry = new PostingsEntry();
                            JSONObject klass = functions.getJSONObject(j);
                            foundEntry.filename = filename;
                            foundEntry.filepath = filepath;
                            foundEntry.pkg = pkg;
                            foundEntry.name = klass.getString("name");
                            foundEntry.startRow = klass.getInt("row");
                            searchResults.addPostingsEntry(foundEntry);
                        }

                    } else if (query.type == QueryType.PACKAGE) {
                        // TODO: Implement package search
                            PostingsEntry foundEntry = new PostingsEntry();
                            foundEntry.filename = filename;
                            foundEntry.filepath = filepath;
                            foundEntry.pkg = pkg;
                            foundEntry.name = pkg;
                            foundEntry.startRow = 0;
                            searchResults.addPostingsEntry(foundEntry);

                        } else {
                        System.err.println("error: unknown query type");
                        return searchResults;
                    }
                }
            } else {
                System.out.println("Search returned 0 hits");
            }
        } catch (MalformedURLException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        } catch (JSONException e) {
            e.printStackTrace();
        }
        return searchResults;
    }


    // ----- EVENT HANDLERS -----

    public void onEnter(ActionEvent e) {
        String queryFieldText = queryField.getText().trim();
        if (queryFieldText != null) {
            Query query;
            if (functionSearchRadio.isSelected()) {
                query = new Query(queryFieldText, QueryType.FUNCTIONS);
                PostingsList plist = search(query);
                infoLabel.setText("Number of hits: " + plist.postings.size());
                updateListView(plist);
            } else if (classSearchRadio.isSelected()) {
                query = new Query(queryFieldText, QueryType.CLASSES);
                PostingsList plist = search(query);
                infoLabel.setText("Number of hits: " + plist.postings.size());
                updateListView(plist);
            } else if (packageSearchRadio.isSelected()) {
                query = new Query(queryFieldText, QueryType.PACKAGE);
                PostingsList plist = search(query);
                infoLabel.setText("Number of hits: " + plist.postings.size());
                updateListView(plist);
            }
        } else {
            System.out.println("error: empty query received");
        }
    }
}
