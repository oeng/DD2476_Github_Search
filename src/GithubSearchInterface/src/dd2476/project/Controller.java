package dd2476.project;

import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.scene.Scene;
import javafx.scene.control.*;


import java.io.*;
import java.util.Collections;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLConnection;

import javafx.scene.input.Clipboard;
import javafx.scene.input.ClipboardContent;
import javafx.scene.layout.StackPane;
import javafx.scene.paint.Color;
import javafx.scene.text.Text;
import javafx.scene.text.TextFlow;
import javafx.stage.Stage;
import org.fxmisc.richtext.InlineCssTextArea;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import org.fxmisc.richtext.CodeArea;

public class Controller {
    private final static String INDEX_NAME = "test";
    private final static String ES_URL = "http://localhost:9200/";

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

        // Handle what happens when user clicks a result on the list
        resultsListView.setOnMouseClicked((event) -> {
            // Find out which result item was clicked
            PostingsEntry clickedEntry = resultsListView.getSelectionModel().getSelectedItem();
            if (clickedEntry != null) {
                // Show detailed information to user
                openResultEntry(clickedEntry);
            }
        });
    }

    private void openResultEntry(PostingsEntry entry) {
        InlineCssTextArea codeArea = new InlineCssTextArea();
        // Settings for the new window that we will open
        StackPane detailsLayout = new StackPane();
        detailsLayout.getChildren().add(codeArea);
        Scene detailsScene = new Scene(detailsLayout, 600, 800);
        Stage detailsWindow = new Stage();
        detailsWindow.setScene(detailsScene);
        detailsWindow.setTitle("Showing result found in: " + entry.getRepo());

        // TODO: Använd radnummer istället för absolutpositioner
        String newLineSymbol = System.getProperty("line.separator");
        int lineNumber= 0;
        int startPos = 0;
        int endPos = 0;
        try (BufferedReader br = new BufferedReader(new FileReader(entry.getFilepath()))) {
            String line;
            while ((line = br.readLine()) != null) {
                //if (lineNumber == entry.startPos - 1) {
                //    /**
                //     * Increment the startPos as long as we have not reached the
                //     * method/functions/class start line.
                //     */
                //    startPos += line.getBytes().length;
                //}
                //if (lineNumber < entry.startPos) {
                //    endPos += line.getBytes().length;
                //}
                codeArea.appendText(line + newLineSymbol);
                if (lineNumber >= entry.startPos-1 && lineNumber <= entry.endPos-1) {
                    codeArea.setParagraphStyle(lineNumber, "-fx-background-color: #c8ccd0;");
                }
                ++lineNumber;
            }
            codeArea.moveTo(entry.startPos - 1, 0);
            codeArea.scrollToPixel(entry.startPos, 0);
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }
        detailsWindow.show();
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
            // Open a connection to elasticsearch and send the request, receive response.
            queryURL = new URL(ES_URL + INDEX_NAME + "/_search/" + key);
            URLConnection conn = queryURL.openConnection();
            BufferedReader in = new BufferedReader(new InputStreamReader(conn.getInputStream(), "UTF8"));
            StringBuilder response = new StringBuilder();
            String inputLine;

            while ((inputLine = in.readLine()) != null) {
                response.append(inputLine);
            }
            in.close();

            // Parse the received JSON data
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
                            foundEntry.startPos = function.getInt("start_row");
                            foundEntry.endPos = function.getInt("end_row");
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
                            foundEntry.startPos = klass.getInt("start_row");
                            foundEntry.endPos = klass.getInt("end_row");
                            searchResults.addPostingsEntry(foundEntry);
                        }

                    } else if (query.type == QueryType.PACKAGE) {
                            PostingsEntry foundEntry = new PostingsEntry();
                            foundEntry.filename = filename;
                            foundEntry.filepath = filepath;
                            foundEntry.pkg = pkg;
                            foundEntry.name = pkg;
                            foundEntry.startPos = 0;
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
        if (!queryFieldText.equals("")) {
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
            // TODO: Implement search with combinations of function, class, package etc.
        } else {
            System.out.println("empty query received");
        }
    }
}
