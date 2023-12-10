#!/usr/bin/env python3

import glob
import time
import os
import langchain

from chains import WikipediaShrinker
from wikimedia import process_wikidump, write_output


#https://wikimedia.bringyour.com/enwiki/20231201/enwiki-20231201-pages-articles.xml.bz2


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--llm", default="mistral", help="which llm to use")
    parser.add_argument("--max_token", default=8192, type=int)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--xmlpath", default="./xml/", help="path to wikipedia dump xml files")
    args = parser.parse_args()

    paths = glob.glob(args.xmlpath + "*.xml")

    langchain.debug=args.debug
    langchain.verbose=args.verbose

    shrinker = WikipediaShrinker(args.llm, args.max_token, args.verbose)

    # for track timing for iterations
    starttime = time.time()
    lasttime = starttime

    # create hardcoded output directory if it doesn't exist
    if not os.path.exists("output"):
        os.makedirs("output")

    article_count = 0
    processed_count = 0

    for text, id, title in process_wikidump(paths):
        # TODO: fix this to be a json file and fix prompts to output json.
        # Maybe use a codellama chain at the end?
        output_file = "output/{}.txt".format(id)

        # If we have an output file assume we're starting over.
        if os.path.exists(output_file):
            print("Skipping {} - exists".format(id))
            continue

        # Total articles from the xml dump
        article_count += 1

        # Skip articles that are too short
        # We're assuming these are redirects to a real article
        # TODO: detect REDIRECT?  Add alternate questions to list
        if len(text.split()) < 20:
            if args.verbose:
                print("Skipping {} - too short probably a redirect".format(id))
            continue

        # Real articles that we're processing
        processed_count += 1

        # Actually process article
        answer = shrinker.shrink_article(text)

        # Write out the answer to a file and track timing
        currenttime = time.time()
        processed_time = write_output(output_file, title, answer, lasttime, currenttime)
        lasttime = currenttime # when last article was processed
        runtime = currenttime - starttime # total time this has been running
        print("Processed '{}' id={} in {} seconds.  Total Articles {} - {:.2f}s/per, Real Articles {} - {:.2f}s/per.  Runtime {:.2f}s".format(title, id, int(processed_time), article_count, runtime/article_count, processed_count, runtime/processed_count, runtime))
