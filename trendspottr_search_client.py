import sublime, sublime_plugin
import urllib, urllib2, json, threading

class TrendspottrSearchPanelCommand(sublime_plugin.WindowCommand):

    def run(self):
        self.window.show_input_panel("TrendSpottr Search:", "Web Technology", self.on_done, None, None)

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
        # build url query
        url = self.url_builder(query)

        # trendspottr service call
        service = TrendSpottrServiceThread(self, edit, region, url)
        service.start()

        # show status message
        sublime.status_message("Connect to TrendSpottr service.")

    def url_builder(self, keyword):
        # load settings
        prop = sublime.load_settings("TrendSpottrPreferences.sublime-settings")

        params = [('key', prop.get('apikey', '')),
                  ('q', keyword), 
                  ('w', prop.get('source', 'all')),
                  ('n', prop.get('limit', 5)),
                  ('lang', prop.get('lang', 'en')),
                  ('expand', prop.get('expand', 'true'))] 

        query_string = urllib.urlencode(params)

        return prop.get('url', '') + '?' + query_string

class TrendSpottrServiceThread(threading.Thread):

    def __init__(self, cmd, edit, region, url):
        threading.Thread.__init__(self)
        self.cmd = cmd
        self.edit = edit
        self.region = region
        self.url = url

    def run(self):
        resp = None 
        try:
            # http response
            resp = urllib2.urlopen(self.url)
            # parse response to JSON object
            json_obj = json.loads(resp.read())
            # pretty formatted JSON string
            pretty_json = json.dumps(json_obj, indent=4, separators=(',', ':'))
            # update sublime view
            self.response = pretty_json
            # fixed: RuntimeError: Must call on main thread
            sublime.set_timeout(self.callback, 1)
        except Exception as ex:
            # update sublime view
            self.response = str(ex)
            # fixed: RuntimeError: Must call on main thread
            sublime.set_timeout(self.callback, 1)
            pass
        finally:
            if resp is not None:
                resp.close()
            pass

    # fixed: RuntimeError: Must call on main thread
    def callback(self):
        self.cmd.view.replace(self.edit, self.region, self.response)