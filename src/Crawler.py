import base64
import glob
import tarfile
import tempfile
import os
import pickle
import requests
import time
import sys
import shutil


class Crawler:
    """
    Uses Github API to search, download, and filter out Java files in Github repos.

    Does everything sequentially to postpone rate limit problems.

    Safe to cancel with ctrl-c, assuming a file is not being written at that time

    https://developer.github.com/v3/

    """
    def __init__(self):
        self.language = "java"
        self.file_storage = "download_repo"  # If you change this, also change the entry in .gitignore
        self.page = os.path.join(self.file_storage, "page.pickle")

        # Max repo size
        # Note: this does not work, possible due to chunking
        # For example 1048576 is 10MB
        self.max_tarball_size = 1048576  # In bytes

    def download_repo(self, repo_url):
        """
        Downloads repo as an archive and then extracts it, only keeping Java files

        Overwrites any existing files already saved on disk

        https://developer.github.com/v3/repos/contents/#get-archive-link

        :param repo_url: API url to the repo
        :return:
        """
        repo_url = repo_url + "/tarball"

        # Download the repo as tarball
        repo_raw = self.GET(repo_url, is_tarball=True)
        if not repo_raw:
            # If the tarball was too big, ignore it
            return

        # Save it to disk in a temporary directory
        temp_dir = tempfile.TemporaryDirectory()
        # Append path using os path join instead of backslash for Windows/Linux cross compatibility
        tarball_name = os.path.join(temp_dir.name, "tarball.tar.gz")
        extracted_repo_name = os.path.join(temp_dir.name, "extracted")
        with open(tarball_name, "wb") as f:
            repo_raw.decode_content = True
            shutil.copyfileobj(repo_raw, f)

        # Extract the tarball
        tar = tarfile.open(tarball_name, "r:gz")
        tar.extractall(path=extracted_repo_name)
        tar.close()

        # Move Java files to storage
        # Keep the package structure
        s = os.path.sep
        for filepath in glob.iglob(extracted_repo_name + s + "**" + s + "*." + self.language, recursive=True):
            filename = os.path.basename(filepath)
            # Create package structure
            # Cut away the extracted repo path (and path separator)
            new_location = filepath[len(extracted_repo_name):]
            new_location = new_location[len(os.path.sep):]
            # Get the repo name (first folder in the extracted tarball)
            repo_name = new_location.split(os.path.sep)[0]
            # Remove the repo name from the path
            new_location = new_location[len(repo_name):]
            new_location = new_location[len(os.path.sep):]
            # Add repo name
            new_location = os.path.join(repo_name, new_location)
            # Add absolute path
            new_location = os.path.join(self.file_storage, new_location)
            if not os.path.exists(new_location[:-len(filename)]):
                os.makedirs(new_location[:-len(filename)])
            shutil.move(filepath, new_location)

        # Delete the temporary directory
        temp_dir.cleanup()

        print("Saved repo to disk: ", repo_url)

    def retrieve_code_from_repo(self, repo_trees_url):
        """
        Download all Java files from a repo

        RATE LIMIT IS A PROBLEM FOR THIS FUNCTION, DO NOT USE

        :param repo_trees_url: "trees_url" from Github"s API,
        example: https://api.github.com/repos/iluwatar/java-design-patterns/git/trees{/sha}"
        :return:
        """
        # Browse master branch
        # not always called master, will not work
        repo_trees_url = repo_trees_url.replace("{/sha}", "/master")
        # Browse files recursively
        repo_trees_url = repo_trees_url + "?recursive=1"

        r = self.GET(repo_trees_url)
        # Ignore if the result is truncated for our scope

        # Filter all java/python/etc file blobs
        acceptable_file_ending = "." + self.language
        acceptable_file_ending_length = len(acceptable_file_ending)
        tree = [
            x for x in r["tree"]
            if x["type"] == "blob" and len(x["path"]) > acceptable_file_ending_length and
            # Filter out .java
            x["path"][-acceptable_file_ending_length:] == acceptable_file_ending
        ]
        # Now tree is a list of links to Java-file blobs

        # Get the file content, also keep the file names
        files = []
        for t in tree[5:]:
            file_name = t["path"].split("/")[-1]
            print(file_name)
            blob = self.GET(t["url"])
            if blob:
                content = blob["content"]
                content = base64.b64decode(content)
                print(content)
                files.append((file_name, content))
        # Now files is a list of tuples (file_name, file_content)

    def search_repos_generator(self, max_count, page=None):
        """
        Generator for search_repos, list Github repos

        :param page: optional page to search from
        :type max_count: terminate the search after finding this many repos
        :return: list of items (items field in Github"s response) and next page
        """

        retrieved_count = 0

        while retrieved_count < max_count:
            if page:
                res = self.search_repos(page=page)
                page += 1
            else:
                res = self.search_repos()
                page = 2
            # Update total count
            retrieved_count += len(res["items"])

            # Yield the found repos
            yield res["items"], page

    def search_repos(self, page=None):
        """
        List Github Java repos, sorted by stars
        https://developer.github.com/v3/search/#search-repositories

        :param page: id to search from
        :return: Github JSON response https://developer.github.com/v3/search/#search-repositories
        """
        url = "https://api.github.com/search/repositories?q=language:%s&sort=stars&order=desc&per_page=10" % self.language
        if page:
            url = url + "&page=%i" % page
            pass

        r = self.GET(url)

        return r

    def GET(self, url, is_tarball=False, wait_time=10):
        """
        Sends HTTP GET request to Github"s API and handles rate limiting

        :param wait_time: waiting time between failed requests
        :param is_tarball: download file or not
        :param url: full url
        :return: None or response JSON
        """
        r = requests.get(url, stream=is_tarball)

        if r.status_code == 403:
            # Rate limit
            print("Rate limit reached for URL ", str(url), " waiting ", wait_time, "seconds", file=sys.stderr)

            # If rate limit reached, simply wait one minut for the rate limit to dissapear
            time.sleep(wait_time)
            return self.GET(url, wait_time=wait_time*2)
        if r.status_code != 200:
            print("HTTP GET failed with code ", str(r.status_code), " for URL ", str(url), file=sys.stderr)
            return None

        # Limit file size, if tarball
        if is_tarball and "content_length" in r.headers:
            if type(r.headers["content-length"]) is not int or int(r.headers["content-length"]) > self.max_tarball_size:
                print("Skipping repository since too big ", r.headers["content-length"], "url: ", url, file=sys.stderr)
                return None

        if is_tarball:
            return r.raw
        else:
            return r.json()

    def start(self):
        # Try to load id from last search, if not new start
        try:
            with open(self.page, "rb") as f:
                page = pickle.load(f)
            print("Found pickled page ", page)
        except (FileNotFoundError, EOFError, pickle.PickleError):
            # Fresh start
            page = None
            print("Found no pickled page", file=sys.stderr)
        for items, p in self.search_repos_generator(10000, page=page):
            for item in items:
                repo_url = item["url"]
                self.download_repo(repo_url)
            # Pickle page if the search is aborted
            if not os.path.exists(self.file_storage):
                os.makedirs(self.file_storage)
            with open(self.page, "wb") as f:
                pickle.dump(p, f)

if __name__ == "__main__":
    Crawler().start()
