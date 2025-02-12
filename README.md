# steam-depot-finder
Gathers appid, app name and depot size information for all depots on steam using reverese appinfo lookup and saves the data as a json file.

# Requirements
`pip install -U "steam[client]"`

# How it works
On the first run the program gathers all appids and requests their info in 1000 batches (for more speed) and saves the data into `depot_data.json` file. On future runs only changed apps are requested and their depots are added. last change number is saved to `.get_depot_last_run`.
