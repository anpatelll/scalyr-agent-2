# Copyright 2014 Scalyr Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------
#
# A ScalyrMonitor which retrieves a specified URL and records the response status and body.

import re
import urllib2
import cookielib

from scalyr_agent import ScalyrMonitor, define_config_option

__monitor__ = __name__

define_config_option(__monitor__, 'module',
                     'Always ``scalyr_agent.builtin_monitors.url_monitor``',
                     required_option=True, convert_to=str)
define_config_option(__monitor__, 'id',
                     'Included in each log message generated by this monitor, as a field named ``instance``. Allows '
                     'you to distinguish between values recorded by different monitors.')
define_config_option(__monitor__, 'url',
                     'The URL to fetch. Must be an http or https URL.', required_option=True)
define_config_option(__monitor__, 'timeout',
                     'Optional (defaults to 10): the maximum amount of time, in seconds, to wait for the URL to load.',
                     default=10, convert_to=float, min_value=0, max_value=30)
define_config_option(__monitor__, 'extract',
                     'Optional: a regular expression to apply to the command output. If defined, this expression must '
                     'contain a matching group (i.e. a subexpression enclosed in parentheses). The monitor will record '
                     'only the content of that matching group. This allows you to discard unnecessary portions of the '
                     'command output and extract the information you need.', default="")
define_config_option(__monitor__, 'log_all_lines',
                     'Optional (defaults to false). If true, the monitor will record the entire command output; '
                     'otherwise, it only records the first line.', default=False)
define_config_option(__monitor__, 'max_characters',
                     'Optional (defaults to 200). At most this many characters of output are recorded. You may specify '
                     'a value up to 10000, but the Scalyr server currently truncates all fields to 3500 characters.',
                     default=200, convert_to=int, min_value=0, max_value=10000)

# Pattern that matches the first line of a string
first_line_pattern = re.compile('[^\r\n]+')


# Redirect handler that doesn't follow any redirects
class NoRedirection(urllib2.HTTPErrorProcessor):
    def __init__(self):
        pass

    def http_response(self, request, response):
        return response

    https_response = http_response


# UrlMonitor implementation
class UrlMonitor(ScalyrMonitor):
    """A Scalyr agent monitor which retrieves a specified URL, and records the response status and body.
    """

    def _initialize(self):
        # Fetch and validate our configuration options.
        #
        # Note that we do NOT currently validate the URL. It would be reasonable to check
        # for valid syntax here, but we should not check that the domain name exists, as an
        # external change (e.g. misconfigured DNS server) could then prevent the agent from
        # starting up.
        self.url = self._config.get("url")
        self.timeout = self._config.get("timeout")
        self.max_characters = self._config.get("max_characters")
        self.log_all_lines = self._config.get("log_all_lines")

        extract_expression = self._config.get("extract")
        if extract_expression:
            self.extractor = re.compile(extract_expression)
            
            # Verify that the extract expression contains a matching group, i.e. a parenthesized clause.
            # We perform a quick-and-dirty test here, which will work for most regular expressions.
            # If we miss a bad expression, it will result in a stack trace being logged when the monitor
            # executes.
            if extract_expression.find("(") < 0:
                raise Exception("extract expression [%s] must contain a matching group" % extract_expression)
        else:
            self.extractor = None

    def gather_sample(self):
        # Query the URL
        try:
            opener = urllib2.build_opener(NoRedirection, urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
            response = opener.open(self.url, None, self.timeout)
        except urllib2.HTTPError, e:
            self._logger.error("HTTPError retrieving %s: %s" % (self.url, e))
            return
        except urllib2.URLError, e:
            self._logger.error("URLError retrieving %s: %s" % (self.url, e))
            return

        # Read the response, and apply any extraction pattern
        response_body = response.read()
        response.close()
        if self.extractor is not None:
            match = self.extractor.search(response_body)
            if match is not None:
                response_body = match.group(1)

        # Apply log_all_lines and max_characters, and record the result.
        if self.log_all_lines:
            s = response_body
        else:
            first_line = first_line_pattern.search(response_body)
            s = ''
            if first_line is not None:
                s = first_line.group().strip()

        if len(s) > self.max_characters:
            s = s[:self.max_characters] + "..."
        self._logger.emit_value('response', s, extra_fields={'url': self.url, 'status': response.getcode(),
                                                             'length': len(response_body)})
