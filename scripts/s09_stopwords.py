import sys

from tm2p.refine.concept.stop import StopWord  # type: ignore

for word in sorted(
    [
        "infrare",
    ]
):

    sys.stderr.write(f"\nProcessing stop word: {word}\n")
    sys.stderr.flush()
    StopWord().having_word(word).where_root_directory("./scopus/").run()
    sys.stderr.write("\n")
    sys.stderr.flush()
