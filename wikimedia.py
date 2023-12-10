import mwxml
import mwparserfromhell
import time


def process_dump(dump, path):
    for page in dump:
        yield next(page, None)


def process_wikidump(paths):

    for revision in mwxml.map(process_dump, paths):
        plaintxt = mwparserfromhell.parse(revision.text).strip_code()
        yield str(plaintxt), revision.page.id, revision.page.title


def write_output(filename, title, answer, lasttime, currenttime):
    runtime = currenttime - lasttime
    with open(filename, "w") as f:
        f.write(title)
        f.write("\n\n")
        f.write(answer)
        f.write("\n\n")
        f.write("Time: {}".format(runtime))
    lasttime = currenttime
    return runtime
