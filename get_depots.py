import json, os
from steam.client import SteamClient
from steam.webapi import WebAPI

def get_depot_data(depots, last_change_number):

    print("logging in")
    client = SteamClient()
    client.anonymous_login()

    print("getting changes")
    changes = client.get_changes_since(last_change_number, app_changes=True, package_changes=False)
    current_change_number = changes.current_change_number
    change_difference = current_change_number - last_change_number
    print(f"last run change number was {last_change_number}")
    print(f"current change number is {current_change_number} ({change_difference} changes)")
    if change_difference == 0:
        print("no changes")
        return depots, current_change_number

    appids = []
    if last_change_number == 0:
        print("gathering all appids")
        api = WebAPI("YOUR_STEAM_API_KEY")
        apps_data = api.call("ISteamApps.GetAppList")["applist"]["apps"]
        for app in apps_data:
            appids.append(int(app["appid"]))
    else:
        print("gathering changed appids")
        if len(changes.app_changes) < 1:
            print("no changes")
            return depots, current_change_number

        for app_change in changes.app_changes:
            print(app_change.appid)
            appids.append(app_change.appid)

    appids_count = len(appids)
    print(f"total appids: {appids_count}")

    chunk_size = min(500, appids_count)
    appids_chunks = [appids[i:i + chunk_size] for i in range(0, appids_count, chunk_size)]
    chunks_count = len(appids_chunks)

    for chunk_index, chunk in enumerate(appids_chunks):
        done_percent = int(chunk_index / chunks_count * 100)
        print(f"getting appinfo - {chunk_index * chunk_size} to {(chunk_index + 1) * chunk_size} ({done_percent}%)")
        appinfo_chunk = client.get_product_info(apps=chunk)["apps"]
        chunk_count = len(appinfo_chunk)
        print(f"got info of {chunk_count} apps")
        for appid, appinfo in appinfo_chunk.items():
            app_depots = appinfo.get("depots")
            if not app_depots:
                continue
            appid = int(appinfo["appid"])
            appname = appinfo["common"]["name"]
            for depot_id, depot_data in app_depots.items():
                if not depot_id.isnumeric():
                    continue
                if depot_id not in depots:
                    depot_size = ""
                    try:
                        manifests = depot_data.get("manifests")
                    except:
                        print(depot_data)
                    if manifests:
                        if "public" in manifests:
                            if "download" in manifests["public"]:
                                depot_size = int(manifests["public"]["download"])
                    depots[depot_id] = {"appid": appid, "appname": appname, "size": depot_size}
    return depots, current_change_number

last_change_number = 0
if os.path.exists(".get_depot_last_run"):
    with open(".get_depot_last_run", "r") as file:
        last_change_number = int(file.read().strip())

depots = {}
if os.path.exists("depot_data.json"):
    with open("depot_data.json", "r") as file:
        depots = json.load(file)

last_depots_count = len(depots)
depots, current_change_number = get_depot_data(depots, last_change_number)
added_depots_count = len(depots) - last_depots_count

if added_depots_count > 0:
    with open("depot_data.json", "w") as file:
        json.dump(depots, file)
    print(f"added {added_depots_count} depots to {last_depots_count}")
else:
    print("no new depots to add")

with open(".get_depot_last_run", "w") as file:
    file.write(str(current_change_number))
