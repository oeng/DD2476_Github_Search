import base64

import requests
import time

import sys


class Crawler:
    """
    Uses Github API

    https://developer.github.com/v3/

    """
    def __init__(self):
        self.language = 'java'

    def retrieve_code_from_repo(self, repo_trees_url):
        """
        Download all Java files from a repo

        TODO the rate limit is a problem
        Maybe download as an archive and then extract?
        https://developer.github.com/v3/repos/contents/#get-archive-link

        :param repo_trees_url: 'trees_url' from Github's API,
        example: https://api.github.com/repos/iluwatar/java-design-patterns/git/trees{/sha}'
        :return:
        """
        # Browse master branch
        repo_trees_url = repo_trees_url.replace('{/sha}', '/master')
        # Browse files recursively
        repo_trees_url = repo_trees_url + '?recursive=1'

        r = self.GET(repo_trees_url)
        # Ignore if the result is truncated for our scope

        # Filter all java/python/etc file blobs
        acceptable_file_ending = '.' + self.language
        acceptable_file_ending_length = len(acceptable_file_ending)
        tree = [
            x for x in r['tree']
            if x['type'] == 'blob' and len(x['path']) > acceptable_file_ending_length and
            # Filter out .java
            x['path'][-acceptable_file_ending_length:] == acceptable_file_ending
        ]
        # Now tree is a list of links to Java-file blobs

        # Get the file content, also keep the file names
        files = []
        for t in tree[5:]:
            file_name = t['path'].split('/')[-1]
            blob = self.GET(t['url'])
            if blob:
                content = blob['content']
                content = base64.b64decode(content)
                files.append((file_name, content))
        # Now files is a list of tuples (file_name, file_content)
        print(files)

    def search_repos_generator(self, max_count):
        """
        Generator for search_repos, list Github repos

        :type max_count: terminate the search after finding this many repos
        :return: list of items (items field in Github's response)
        """
        retrieved_count = 0

        res = self.search_repos()

        # Get the id of the last search result
        since = res['items'][-1]['id']
        # Update total count
        retrieved_count += len(res['items'])

        # Yield the found repos
        yield res['items']

        while retrieved_count < max_count:
            res = self.search_repos(since=since)
            # Get the id of the last search result
            since = res['items'][-1]['id']
            # Update total count
            retrieved_count += len(res['items'])

            # Yield the found repos
            yield res['items']

    def search_repos(self, since=None):
        """
        List Github Java repos, sorted by stars
        https://developer.github.com/v3/search/#search-repositories

        :param since: id to search from
        :return: Github JSON response https://developer.github.com/v3/search/#search-repositories
        """
        url = 'https://api.github.com/search/repositories?q=language:%s&sort=stars&order=desc' % self.language
        if since:
            url = url + '&since=%i' % since
            pass

        r = self.GET(url)

        return r

    def GET(self, url):
        """
        Sends HTTP GET request to Github's API and handles rate limiting

        :param url: full url
        :return: None or response JSON
        """
        r = requests.get(url)

        if r.status_code == 403:
            # Rate limit
            print('Rate limit reached for URL ', str(url), file=sys.stderr)

            # If rate limit reached, simply wait one minut for the rate limit to dissapear
            time.sleep(60)
            return self.GET(url)
        if r.status_code != 200:
            print('HTTP GET failed with code ', str(r.status_code), ' for URL ', str(url), file=sys.stderr)
            return None

        return r.json()



def test():
    crawler = Crawler()
    #for items in crawler.search_repos_generator(150):
    #    print(items)
    url = 'https://api.github.com/repos/iluwatar/java-design-patterns/git/trees{/sha}'
    crawler.retrieve_code_from_repo(url)


if __name__ == '__main__':
    test()
