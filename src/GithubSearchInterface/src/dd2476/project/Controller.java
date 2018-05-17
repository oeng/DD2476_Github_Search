package dd2476.project;

import javafx.application.Platform;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.layout.StackPane;
import javafx.stage.Stage;
import org.fxmisc.richtext.InlineCssTextArea;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.*;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;

public class Controller {
    // Name of the elasticsearch index
    private final static String INDEX_NAME = "test";
    // URL to the elasticsearch API
    private final static String ES_URL = "http://localhost:9200/";
    private int page = 0;

    // List view for displaying search results
    @FXML
    ListView<PostingsEntry> resultsListView;

    // Text field where the user enters a query string
    @FXML
    TextField queryField;

    // Label that can be used to display information such as number of hits
    @FXML
    Label infoLabel;

    // Toggle group used to group the radio buttons for selecting search method
    @FXML
    ToggleGroup toggleGroup;

    // Radio buttons used to select search method
    @FXML
    RadioMenuItem functionSearchRadio;
    @FXML
    RadioMenuItem classSearchRadio;
    @FXML
    RadioMenuItem packageSearchRadio;

    // Combo box used for selecting the number of results to display in the list view
    @FXML
    ComboBox<Integer> numResultsComboBox;

    // Check box used to select whether the results should be filtered by return type
    @FXML
    CheckBox returnTypeCheckbox;

    // Text field to get the return type specified by the user if return type filtering is enabled
    @FXML
    TextField returnTypeField;

    @FXML
    Button prevButton;

    @FXML
    Button nextButton;

    /**
     * This method is called right after the FXML objects are injected.
     * Used to initialize the number of results combo box and adds an
     * event listener to the list view.
     */
    @FXML
    public void initialize() {
        infoLabel.setText("Press enter to search");

        // Populate options for the combo box for the number of results to display in the list view
        numResultsComboBox.getItems().addAll(10, 20, 30, 40, 50, 75, 100, 150, 200);
        numResultsComboBox.getSelectionModel().selectFirst();

        // Setup an event handler on the list view for what happens when the user clicks a result in the list view
        resultsListView.setOnMouseClicked((event) -> {
            // Find out which result item was clicked
            PostingsEntry clickedEntry = resultsListView.getSelectionModel().getSelectedItem();
            if (clickedEntry != null) {
                // Show detailed information to user
                if(clickedEntry.packageId < 0)
                    openResultEntry(clickedEntry);
            }
        });
    }

    /**
     * Opens a new window with the marked source code snippet for a postings entry.
     *
     * @param entry The postings entry that should have its details shown in a new window.
     */
    private void openResultEntry(PostingsEntry entry) {
        int width = 600;
        int height = 800;
        int lineHeight = height / 50;
        int linesBeforeHighlight = 4;

        // text area to show the contents of the source code
        InlineCssTextArea codeArea = new InlineCssTextArea();

        // Settings for the new window that we will open
        StackPane detailsLayout = new StackPane();
        detailsLayout.getChildren().add(codeArea);
        Scene detailsScene = new Scene(detailsLayout, width, height);
        Stage detailsWindow = new Stage();
        detailsWindow.setScene(detailsScene);
        detailsWindow.setTitle("Showing result found in: " + entry.getRepo());

        // Get the symbol used for new line on the system the interface is running on
        String newLineSymbol = System.getProperty("line.separator");

        // Open the source code file the postings entry and read it line by line
        int lineNumber = 0;
        try (BufferedReader br = new BufferedReader(new FileReader(entry.getFilepath()))) {
            String line;
            while ((line = br.readLine()) != null) {
                // Quickfix for displaying package result
                codeArea.appendText(String.format("%4d", lineNumber) + "   " + line + newLineSymbol);
                // Mark the relevant code snippet in this source file, so it is easily visible to the user
                if (lineNumber >= entry.startPos - 1 && lineNumber <= entry.endPos - 1) {
                    codeArea.setParagraphStyle(lineNumber, "-fx-background-color: #c8ccd0;");
                }
                ++lineNumber;
            }
            // Scroll the view to the location of the code snippet
            codeArea.scrollToPixel(entry.startPos, 0);
        } catch (FileNotFoundException e) {
            System.err.println("Warning: could not find " + entry.getFilepath());
            e.printStackTrace();
        } catch (IOException e) {
            System.err.println("Error: could not read " + entry.getFilepath());
            e.printStackTrace();
        }
        // Show the window containing the source code we just built
        detailsWindow.show();
        // After the window is opened, scroll the code view
        Platform.runLater(() -> codeArea.scrollYBy((entry.startPos - linesBeforeHighlight) * lineHeight));
    }

    /**
     * Resets the list view and adds a new postings list to it.
     *
     * @param plist New postings list to be added to the list view
     */
    private void updateListView(PostingsList plist) {
        resultsListView.getItems().clear();
        resultsListView.getItems().addAll(plist.postings);
    }

    private Integer getFrom() {
        return page * numResultsComboBox.getValue();
    }

    /**
     * The main method used for performing a complete search operation with the
     * user-specified query string.
     *
     * @param query The query object to search with.
     *
     * @return The resulting postings list containing all retrieved postings
     */
    private PostingsList search(Query query) {
        /* Create an empty postings list with the current query type for storing the
         * retrieved postings entries. */
        PostingsList searchResults = new PostingsList(query.type);
        // URL object to store the complete request URL to be sent to the elasticsearch API
        URL queryURL;
        // The json object we will populate and send to the elasticsearch API
        JSONObject jsonBody = new JSONObject();
        // Get the number of results we should show in the list view
        Integer numResults = numResultsComboBox.getValue();
        try {
            // construct function search request
            if (query.type == QueryType.FUNCTIONS) {
                jsonBody = new JsonQueryBody().getMatchQueryFilter(query.term, "name", "function", numResults, getFrom());
                if (returnTypeCheckbox.isSelected() && !returnTypeField.getText().isEmpty()) {
                    String returnType = returnTypeField.getText();
                    JSONObject jsonTermReturn = new JSONObject();
                    JSONObject jsonFilterReturn = new JSONObject();
                    jsonFilterReturn.put("match", jsonTermReturn);
                    jsonTermReturn.put("return_type", returnType);
                    jsonBody.getJSONObject("query").getJSONObject("bool").getJSONArray("filter").put(jsonFilterReturn);
                }
            }

            // construct class search request
            else if (query.type == QueryType.CLASSES) {
                jsonBody = new JsonQueryBody().getMatchQueryFilter(query.term, "name", "class", numResults, getFrom());
            }

            // construct package search request
            else if (query.type == QueryType.PACKAGE) {
                jsonBody = new JsonQueryBody().getPackageQuery(query.term, "package", numResults, getFrom());
            }

            // Open a connection to elasticsearch and send the request, receive response.
            queryURL = new URL(ES_URL + INDEX_NAME + "/_search/");
            JSONObject jsonObject = getResponse(queryURL, jsonBody);

            // Parse the received JSON data
            JSONObject hitsObject = jsonObject.getJSONObject("hits");
            int nrofHits = hitsObject.getInt("total");

            // Parse response for function or class search
            if (query.type == QueryType.FUNCTIONS || query.type == QueryType.CLASSES) {
                if (nrofHits > 0) {
                    JSONArray hitsArray = hitsObject.getJSONArray("hits");
                    for (int i = 0; i < hitsArray.length(); ++i) {
                        PostingsEntry foundEntry = new PostingsEntry();
                        JSONObject object = hitsArray.getJSONObject(i).getJSONObject("_source");
                        foundEntry.filename = object.getString("filename");
                        foundEntry.filepath = object.getString("filepath");
                        foundEntry.pkg = object.getString("package");
                        foundEntry.name = object.getString("name");
                        foundEntry.startPos = object.getInt("start_row");
                        foundEntry.endPos = object.getInt("end_row");
                        searchResults.addPostingsEntry(foundEntry);
                    }
                } else {
                    System.out.println("Search returned 0 hits");
                }
            }
            // Parse response for package search
            else if (query.type == QueryType.PACKAGE) {
                JSONArray bucketObject = jsonObject.getJSONObject("aggregations").getJSONObject("package_id").getJSONArray("buckets");
                for (int i = 0; i < bucketObject.length(); i++) {
                    PostingsEntry foundEntry = new PostingsEntry();
                    JSONObject object = bucketObject.getJSONObject(i);
                    // This array should always have a single element
                    JSONArray innerBucket = object.getJSONObject("package").getJSONArray("buckets");
                    if(innerBucket.length() != 1) {
                        System.err.println("error: inner bucket > 1");
                        return searchResults;
                    }
                    foundEntry.filename = "";
                    foundEntry.filepath = "";
                    foundEntry.docsInPackage = innerBucket.getJSONObject(0).getInt("doc_count");

                    foundEntry.name = "#docs" + Integer.toString(foundEntry.docsInPackage);
                    foundEntry.packageId = object.getInt("key");
                    foundEntry.pkg = innerBucket.getJSONObject(0).getString("key");
                    searchResults.addPostingsEntry(foundEntry);
                }
            }
            else {
                System.err.println("ERROR: Unknown query type");
            }
        } catch (MalformedURLException e) {
            System.err.println("ERROR: Malformed URL");
            e.printStackTrace();
        } catch (IOException e) {
            System.err.println("ERROR: Could not communicate with elasticsearch API");
            e.printStackTrace();
        } catch (JSONException e) {
            System.err.println("ERROR: Malformed JSON");
            e.printStackTrace();
        }
        return searchResults;
    }

    /**
     * @param queryURL the URL to send a query to.
     * @param jbody the JSONBody to pass in the request
     * @return response JSONObject
     * @throws IOException
     */
    public JSONObject getResponse(URL queryURL, JSONObject jbody) throws IOException, JSONException {
        HttpURLConnection conn = (HttpURLConnection) queryURL.openConnection();
        conn.setRequestMethod("POST");
        conn.setDoOutput(true);
        conn.setRequestProperty("Content-Type", "application/json");
        OutputStreamWriter out = new OutputStreamWriter(conn.getOutputStream());
        out.write(jbody.toString());
        out.flush();
        out.close();
        InputStream is = conn.getInputStream();
        BufferedReader in = new BufferedReader(new InputStreamReader(is));
        StringBuilder response = new StringBuilder();
        String inputLine;
        while ((inputLine = in.readLine()) != null) {
            response.append(inputLine);
        }
        in.close();
        JSONObject jsonResponse = new JSONObject(response.toString());
        return jsonResponse;
    }


    // ----- EVENT HANDLERS -----

    /**
     * Enable/disable return type text field depending on whether the
     * return type checkbox is selected or unselected.
     */
    public void onReturnTypeCheckbox(ActionEvent e) {
        returnTypeField.setDisable(!returnTypeCheckbox.isSelected());
    }

    /**
     * Enable/disable return type checkbox depending on search method.
     */
    public void onSelectFunctionSearch(ActionEvent e) {
        returnTypeCheckbox.setDisable(false);
        nextButton.setDisable(false);
        prevButton.setDisable(false);
    }

    /**
     * Enable/disable return type checkbox depending on search method.
     */
    public void onSelectClassSearch(ActionEvent e) {
        returnTypeCheckbox.setDisable(true);
        returnTypeField.setDisable(true);
        returnTypeCheckbox.setSelected(false);
        nextButton.setDisable(false);
        prevButton.setDisable(false);
    }

    /**
     * Enable/disable return type checkbox depending on search method.
     */
    public void onSelectPackageSearch(ActionEvent e) {
        returnTypeCheckbox.setDisable(true);
        returnTypeField.setDisable(true);
        returnTypeCheckbox.setSelected(false);
        nextButton.setDisable(true);
        prevButton.setDisable(true);
    }

    /**
     * Handle prev button press
     */
    public void onPrevPress(ActionEvent e) {
        if (page > 0) {
            page--;
        }
        searchAction();
    }

    /**
     * Handle next button press
     */
    public void onNextPress(ActionEvent e) {
        page++;
        searchAction();
    }

    /**
     * Handle enter button presses.
     *
     * If a query string is present in the query text field, issue a search
     * of the selected search type.
     */
    public void onEnter(ActionEvent e) {
        page = 0;
        searchAction();
    }

    /**
     * Perform a search and update the result box
     */
    private void searchAction() {
        String queryFieldText = queryField.getText().trim();

        if (!queryFieldText.equals("")) {
            Query query;

            if (functionSearchRadio.isSelected()) {
                query = new Query(queryFieldText, QueryType.FUNCTIONS);
                PostingsList plist = search(query);
                infoLabel.setText("Number of hits: " + plist.postings.size());
                updateListView(plist);
            }

            else if (classSearchRadio.isSelected()) {
                query = new Query(queryFieldText, QueryType.CLASSES);
                PostingsList plist = search(query);
                infoLabel.setText("Number of hits: " + plist.postings.size());
                updateListView(plist);
            }

            else if (packageSearchRadio.isSelected()) {
                query = new Query(queryFieldText, QueryType.PACKAGE);
                PostingsList plist = search(query);
                infoLabel.setText("Number of hits: " + plist.postings.size());
                updateListView(plist);
            }

        } else {
            System.out.println("Empty query received");
        }
    }
}
