from tm2p.ingest.datasrc import Scopus, WoS  # type: ignore

# WoS().where_root_directory("./wos/").run()
Scopus().where_root_directory("./scopus/").run()
