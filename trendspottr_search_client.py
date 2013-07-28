# -*- coding: utf8 -*-
#
# The MIT License (MIT)
#
# Copyright (c) 2013 Lee <lee.github@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import sublime
import sublime_plugin
import urllib
import urllib2
import json
import threading

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
        # Set view name
        self.view.set_name("TrendSpottr - " + query)
        # Set syntax 
        self.view.set_syntax_file('Packages/JavaScript/JSON.tmLanguage')
        # Clear region
        region = sublime.Region(0, self.view.size())
        # Build url query
        url = self.url_builder(query)

        # Trendspottr service call
        service = TrendSpottrServiceThread(self, edit, region, url)
        service.start()

        # Show status message
        sublime.status_message("Connect to TrendSpottr service.")

    def url_builder(self, keyword):
        # Load settings
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
            # Http response
            resp = urllib2.urlopen(self.url)
            # Parse response to JSON object
            json_obj = json.loads(resp.read())
            # Pretty formatted JSON string
            pretty_json = json.dumps(json_obj, indent=4, separators=(',', ':'))
            # Update sublime view text buffer
            self.response = pretty_json
            # Fixed: RuntimeError: Must call on main thread
            sublime.set_timeout(self.callback, 1)
        except Exception as ex:
            # Update sublime view text buffer
            self.response = str(ex)
            # Fixed: RuntimeError: Must call on main thread
            sublime.set_timeout(self.callback, 1)
            pass
        finally:
            if resp is not None:
                resp.close()
            pass

    # Fixed: RuntimeError: Must call on main thread
    def callback(self):
        self.cmd.view.replace(self.edit, self.region, self.response)