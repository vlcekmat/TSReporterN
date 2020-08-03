from collections import deque
import io

from config import read_config
from bugs import read_bug_lines, read_bugs_file, archive_bug
from information_compile import get_image


class BugHandler:
    _all_bugs = deque()  # Queue of bugs read from the bugs file, each bug is a stack of lines, the bug head on top
    current = deque()  # The current bug popped from the above queue

    # The current bug has its images stored here
    # The dictionary is "line": "image path", accessed by try_get_image()
    image_locations = {}

    game_path = None
    # Message is used to catch output from console-based methods to be able to show them
    message = None

    def __init__(self, game):
        if game == "A":
            self.game_path = read_config("documents location") + "/American Truck Simulator"
        else:
            self.game_path = read_config("documents location") + "/Euro Truck Simulator 2"
        out_string = io.StringIO()
        bug_lines = read_bugs_file(self.game_path, out_string)
        if out_string.getvalue() == "":
            self._all_bugs = read_bug_lines(bug_lines)
            self.read_next()

        else:
            self._all_bugs = None
            self.current = None
            self.message = out_string.getvalue()

    def archive(self):
        archive_bug(self.current, self.game_path)
        self.read_next()

    def read_next(self):
        if len(self._all_bugs) > 0:
            self.image_locations.clear()
            self.current = self._all_bugs.popleft()
            while self.current[0][0] in ['!', ';']:
                self.archive()
                self.current = self._all_bugs.popleft()
            for line in self.current:
                self.image_locations[line] = get_image(line)
        else:
            self.current = None

    def try_images_again(self):
        for line in self.current:
            if not self.image_locations[line]:
                self.image_locations[line] = get_image(line)

    def get_current(self):
        return self.current

    def try_get_image(self, line):
        return self.image_locations[line]

    def images_good(self):
        # Checks if all images have a path, if so, returns True
        for location in self.image_locations.values():
            if location == "":
                return False
        return True

    def set_image(self, line, path):
        self.image_locations[line] = path
