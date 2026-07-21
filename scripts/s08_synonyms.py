import sys

from tm2p.refine.concept.merge import Manual  # type: ignore

for preferred, variant in [
    ("food image recognition", "food recognition"),
    ("food image recognition", "image recognition"),
    ("food image classification", "food classification"),
    ("convolutional neural network", "convolutional neural network architecture"),
    ("deep learning", "deep learning techniques"),
    ("food recommendation system", "recommender systems"),
    ("food recommendation", "recommendation"),
    ("user profile", "user profiling"),
    ("mobile phone", "smartphone"),
    ("food supply chain", "food supply chain management"),
]:

    sys.stderr.write(f"\nProcessing {preferred} ---> {variant}\n")
    sys.stderr.flush()
    Manual().having_text_matching(
        (preferred, variant),
    ).where_root_directory("./scopus/").run()
    sys.stderr.write("\n")
    sys.stderr.flush()
