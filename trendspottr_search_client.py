import sublime, sublime_plugin
import urllib, urllib2, json, threading

class TrendspottrSearchPanelCommand(sublime_plugin.WindowCommand):

    def run(self):
        self.window.show_input_panel("Search Query:", "Web Technology", self.on_done, None, None)

    def on_done(self, keyword):
        try:
            self.window.new_file()
            self.call_trendspottr_search(keyword)
        except BaseException as ex:
            sublime.error_message(str(ex))
            pass

    def call_trendspottr_search(self, query):
        self.window.active_view().run_command('trendspottr_search', {'query': query})

class TrendspottrSearchCommand(sublime_plugin.TextCommand):

    def run(self, edit, query):
        # set view name
        self.view.set_name("TrendSpottr - " + query)
        # set syntax 
        self.view.set_syntax_file('Packages/JavaScript/JSON.tmLanguage')
        # clear region
        region = sublime.Region(0, self.view.size())

        url = self.url_builder(query)
        # start thread
        thread = threading.Thread(target=self.http_request_call, args=(edit, region, url))
        thread.start()

        # show status message
        sublime.status_message("Connect to TrendSpottr service.")

    def url_builder(self, keyword):
        # load settings
        prop = sublime.load_settings("TrendspottrPreferences.sublime-settings")

        params = [('key', prop.get('apikey', '')),
                  ('q', keyword), 
                  ('w', prop.get('source', 'all')),
                  ('n', prop.get('limit', 5)),
                  ('lang', prop.get('lang', 'en')),
                  ('expand', prop.get('expand', 'true'))] 

        query_string = urllib.urlencode(params)

        return prop.get('url', '') + '?' + query_string

    def http_request_call(self, edit, region, url):
        response = None 
        try:
            # http response
            response = urllib2.urlopen(url)
            # parse response to JSON object
            json_obj = json.loads(response.read())
            # pretty formatted JSON string
            pretty_json = json.dumps(json_obj, indent=4, separators=(',', ':'))
            # update sublime view
            self.view.replace(edit, region, pretty_json);
        except Exception as ex:
            self.view.replace(edit, region, str(ex));
            pass
        finally:
            if response is not None:
                response.close()
            pass