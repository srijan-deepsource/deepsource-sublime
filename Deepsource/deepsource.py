import json
import subprocess
import sys
import threading

import sublime
import sublime_plugin

# The version of Python that SublimeText is using
PYTHON_VERSION = sys.version_info[0]
# Issues raised by DeepSource
DEEPSOURCE_ISSUES = {}
# The last line selected (i.e. the one we need to display status info for)
LAST_SELECTED_LINE = -1
# Indicates if we're displaying info in the status line
STATUS_ACTIVE = False


class AnalyzerCommand(sublime_plugin.TextCommand):
    """The command to run on the shortcuts."""
    def run(self, edit, **kwargs):
        """Main action point of the plugin."""
        action = kwargs.get('action', None)

        # See if skipcq needs to be added.
        if action == 'ignore':
            self.add_skipcq(edit)
        # Action to list all issues raised.
        elif action == 'list':
            self.popup_issues_list()
        else:
            # Run analysis
            print("Running DeepSource Analysis: ")
            # Run the cli command here to get the results.
            thread = AnalyzerThread(self.view)
            thread.start()
            self.progress_tracker(thread)

    def progress_tracker(self, thread, i=0):
        """ Display spinner while DeepSource is running """
        icons = [u"◐", u"◓", u"◑", u"◒"]
        sublime.status_message("Running analysis on DeepSource %s" % icons[i])
        if thread.is_alive():
            i = (i + 1) % 4
            sublime.set_timeout(lambda: self.progress_tracker(thread, i), 100)
        else:
            sublime.status_message("")

    @classmethod
    def show_errors(cls, view):
        """ Display the errors for the given view """
        region_flag = sublime.DRAW_OUTLINED
        # TODO: Get outlines for different issue categories.
        outlines = {"PYL": [], "PTC": [], "FLK": [], "BAN": []}
        # This would be changed later. Right now: Display same icon for every issue.
        icons = {
            "PYL": "Packages/Deepsource/icons/logo-white.png",
            "PTC": "Packages/Deepsource/icons/logo-white.png",
            "FLK": "Packages/Deepsource/icons/logo-white.png",
            "BAN": "Packages/Deepsource/icons/logo-white.png",
        }

        for line_num, issue in DEEPSOURCE_ISSUES[view.id()].items():
            if type(issue) is not str:
                continue
            # Get the line element for the line number.
            line = view.line(view.text_point(line_num, 0))
            outlines[issue[:3]].append(line)

        for key, regions in outlines.items():
            view.add_regions(
                "analyzer." + key, regions, "analyzer." + key, icons[key], region_flag
            )

    def add_skipcq(self, edit):
        """ Make DeepSource ignore the line that the carret is on by adding a skipcq. """
        global DEEPSOURCE_ISSUES

        view_id = self.view.id()
        point = self.view.sel()[0].end()
        position = self.view.rowcol(point)
        current_line = position[0]

        skipcq = "".join(("# ", "skipcq: ",))

        # If an error is registered for that line
        if current_line in DEEPSOURCE_ISSUES[view_id]:
            # print position
            line_region = self.view.line(point)
            line_txt = self.view.substr(line_region)

            err_code = DEEPSOURCE_ISSUES[view_id][current_line]
            err_code = err_code[:err_code.find(':')]

            if skipcq not in line_txt:
                line_txt += "  " + skipcq + err_code
            else:
                line_txt += "," + err_code

            self.view.replace(edit, line_region, line_txt)
            self.view.end_edit(edit)

    def popup_issues_list(self):
        """ Display a popup list of the issues found """
        view_id = self.view.id()

        if view_id not in DEEPSOURCE_ISSUES:
            return

        # No Issues were found
        if len(DEEPSOURCE_ISSUES[view_id]) == 1:
            sublime.message_dialog("No DeepSource issues found")
            return

        issues = [(key + 1, value)
                  for key, value in DEEPSOURCE_ISSUES[view_id].items()
                  if key != 'visible']
        line_nums, panel_items = zip(*sorted(issues,
                                             key=lambda issue: issue[1]))

        def on_done(selected_item):
            """ Jump to the line of the item that was selected from the list """
            if selected_item == -1:
                return
            self.view.run_command("goto_line",
                                  {"line": line_nums[selected_item]})

        self.view.window().show_quick_panel(list(panel_items), on_done)


class AnalyzerThread(threading.Thread):
    """ This class creates a seperate thread to run DeepSource Analysis"""

    def __init__(self, view):
        self.view = view
        # Grab the file name here, since view cannot be accessed
        # from anywhere but the main application thread
        self.file_name = view.file_name()
        # print(self.file_name)

        threading.Thread.__init__(self)

    def run(self):
        """ Run the analysis command """
        # To remove these.
        import time
        time.sleep(5)

        # TODO: Sourya to integrate CLI command here.
        command = [
            "python",
            "/Users/sauravsrijan/Library/Application Support/Sublime Text 3/Packages/Deepsource/tester.py",
        ]

        p = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        output, eoutput = p.communicate()

        sublime.set_timeout(lambda: self.process_issues(output, eoutput), 100)

    def process_issues(self, output, eoutput):
        """ Process the issues detected """
        view_id = self.view.id()
        DEEPSOURCE_ISSUES[view_id] = {"visible": True}

        try:
            issues = json.loads(output)
        except TypeError:
            issues = json.loads(output.decode())

        for issue in issues:
            if issue["position"]["filepath"] != self.file_name:
                continue
            mid = issue["issue_code"]
            line = issue["position"]["begin"]["line"] - 1
            issue_text = issue["issue_text"]

            DEEPSOURCE_ISSUES[view_id][line] = "%s: %s " % (mid, issue_text.strip())

        if len(DEEPSOURCE_ISSUES[view_id]) <= 1:
            print("No errors found")
        else:
            print("found issues")

        AnalyzerCommand.show_errors(self.view)


class BackgroundAnalyzerr(sublime_plugin.EventListener):
    """ Process Sublime Text events """

    def _last_selected_lineno(self, view):
        return view.rowcol(view.sel()[0].end())[0]

    # def on_post_save(self, view):
    #     """ Run DeepSource on file save """
    #     if view.file_name().endswith(".py"):
    #         view.run_command("analyzer")

    def on_selection_modified(self, view):
        """ Show errors in the status line when the carret/selection moves """
        global LAST_SELECTED_LINE, STATUS_ACTIVE
        view_id = view.id()
        if view_id in DEEPSOURCE_ISSUES:
            new_selected_line = self._last_selected_lineno(view)
            if new_selected_line != LAST_SELECTED_LINE:
                LAST_SELECTED_LINE = new_selected_line
                if LAST_SELECTED_LINE in DEEPSOURCE_ISSUES[view_id]:
                    err_str = DEEPSOURCE_ISSUES[view_id][LAST_SELECTED_LINE]
                    # if PylSet.get_or("message_stay", False):
                    view.set_status('Analyzer', err_str)
                    STATUS_ACTIVE = True
                    # else:
                    #     sublime.status_message(err_str)
                elif STATUS_ACTIVE:
                    view.erase_status("Analyzer")
                    STATUS_ACTIVE = False
